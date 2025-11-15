import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from typing import Dict, Set, List, Tuple
import json
from pathlib import Path
import logging

# Try to import our modules with error handling
try:
    from config import config
    from episode_parser import EpisodeParser
    from media_processor import MediaProcessor
except ImportError as e:
    print(f"Import error: {e}")
    # Create dummy classes for testing
    class DummyConfig:
        def __init__(self):
            self.metadata = {}
            self.paths = type('Paths', (), {})()
            self.paths.output = Path("output")
            self.paths.m3u_dir = Path("output/m3u")
            self.paths.json_dir = Path("output/json")
            self.paths.hls_dir = Path("output/hls")
            self.paths.user_root = Path("user_data")
        def save_metadata(self): pass
        def push_undo_state(self, *args): pass
        def undo(self): return None
        def redo(self): return None
    
    config = DummyConfig()
    
    class EpisodeParser:
        def parse_m3u_file(self, path):
            return [], []
    
    class MediaProcessor:
        def __init__(self): pass
        def add_progress_callback(self, callback): pass
        def batch_process_episodes(self, episodes, operations): return episodes

class ProgressDialog:
    def __init__(self, parent, title="Processing"):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("400x120")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the dialog
        self.window.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.window.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.window.winfo_height()) // 2
        self.window.geometry(f"+{x}+{y}")
        
        self.label = tk.Label(self.window, text="Starting...")
        self.label.pack(pady=10)
        
        self.progress = ttk.Progressbar(self.window, mode='determinate')
        self.progress.pack(fill=tk.X, padx=20, pady=5)
        
        self.percent_label = tk.Label(self.window, text="0%")
        self.percent_label.pack()
        
        self.cancel_button = tk.Button(self.window, text="Cancel", command=self.cancel)
        self.cancel_button.pack(pady=10)
        
        self.cancelled = False
    
    def update(self, current: int, total: int, message: str = ""):
        if self.cancelled:
            return False
            
        percent = (current / total) * 100 if total > 0 else 0
        self.progress['value'] = percent
        self.percent_label.config(text=f"{percent:.1f}%")
        self.label.config(text=message or f"Processing {current} of {total}")
        self.window.update()
        return True
    
    def cancel(self):
        self.cancelled = True
        self.label.config(text="Cancelling...")
        self.cancel_button.config(state=tk.DISABLED)

class OddCoupleManager:
    def __init__(self, root):
        self.root = root
        self.root.title("The Odd Couple Manager v2.0")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2d2d2d")
        
        print("Initializing OddCoupleManager...")
        
        self.config = config
        self.parser = EpisodeParser()
        self.processor = MediaProcessor()
        self.processor.add_progress_callback(self._on_progress_update)
        
        self.user = "@banamine"
        self.user_dir = Path("user_data") / self.user
        self.user_dir.mkdir(exist_ok=True)
        
        self.episodes = []
        self.selected_keys: Set[str] = set()
        self.current_progress_dialog = None
        
        print("Building UI...")
        self.build_ui()
        self.refresh_list()
        print("UI built successfully")
        
    def build_ui(self):
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=6, font=('Arial', 10))
        
        # Top bar with buttons
        top_frame = tk.Frame(self.root, bg="#1a1a1a")
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Buttons
        tk.Button(top_frame, text="Import M3U", command=self.import_m3u, 
                 bg="#0078d7", fg="white", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Export JSON", command=self.export_json, 
                 bg="#28a745", fg="white", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Create M3U", command=self.create_m3u, 
                 bg="#ffc107", fg="black", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Delete Selected", command=self.delete_selected, 
                 bg="#dc3545", fg="white", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        # Stats label
        self.stats_label = tk.Label(top_frame, text="Total: 0 | Valid: 0", 
                                   bg="#1a1a1a", fg="#00ff00", font=('Arial', 10))
        self.stats_label.pack(side=tk.RIGHT, padx=10)
        
        # Main content
        main_frame = tk.Frame(self.root, bg="#2d2d2d")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for episodes
        columns = ("sel", "key", "season", "episode", "title", "duration", "valid")
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col.title())
            width = 40 if col == "sel" else 80 if col in ["key", "season", "episode", "duration", "valid"] else 300
            self.tree.column(col, width=width, anchor='w')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             bg="#0078d7", fg="white", anchor=tk.W, font=('Arial', 9))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def set_status(self, message: str):
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def _on_progress_update(self, current: int, total: int, message: str):
        if self.current_progress_dialog:
            if not self.current_progress_dialog.update(current, total, message):
                if hasattr(self.processor, 'stop_processing'):
                    self.processor.stop_processing()
    
    def refresh_list(self):
        """Refresh the episode list from metadata"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.episodes = []
        
        for key, data in self.config.metadata.items():
            self.episodes.append(data)
            valid = "✓" if data.get("valid") else "✗"
            dur = f"{int(data.get('duration', 0)//60):02d}:{int(data.get('duration', 0)%60):02d}"
            
            iid = self.tree.insert("", "end", values=(
                "☐", data['key'], data['season'], data['episode'], 
                data['title'], dur, valid
            ))
        
        self.update_stats()
    
    def update_stats(self):
        total = len(self.episodes)
        valid = sum(1 for e in self.episodes if e.get("valid"))
        self.stats_label.config(text=f"Total: {total} | Valid: {valid}")
    
    def on_tree_select(self, event):
        selected = self.tree.selection()
        self.selected_keys.clear()
        
        for iid in self.tree.get_children():
            key = self.tree.item(iid, "values")[1]  # key is in second column
            check = "☑" if iid in selected else "☐"
            self.tree.set(iid, "sel", check)
            
            if iid in selected:
                self.selected_keys.add(key)
    
    def import_m3u(self):
        path = filedialog.askopenfilename(
            title="Select M3U File",
            filetypes=[("M3U Files", "*.m3u *.m3u8"), ("All Files", "*.*")]
        )
        if path:
            self.process_m3u_file(path)
    
    def process_m3u_file(self, path: str):
        self.set_status(f"Importing {Path(path).name}...")
        
        def do_import():
            try:
                episodes, errors = self.parser.parse_m3u_file(path)
                
                if errors:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Import Warnings", 
                        f"Found {len(errors)} errors during import"
                    ))
                
                if episodes:
                    # Add to metadata
                    for ep in episodes:
                        self.config.metadata[ep['key']] = ep
                    
                    self.config.save_metadata()
                    self.root.after(0, self.refresh_list)
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Import Complete", 
                        f"Successfully imported {len(episodes)} episodes"
                    ))
                else:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Import", "No episodes found in file"
                    ))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Import Error", 
                    f"Error importing file: {e}"
                ))
            finally:
                self.root.after(0, lambda: self.set_status("Ready"))
        
        threading.Thread(target=do_import, daemon=True).start()
    
    def delete_selected(self):
        if not self.selected_keys:
            messagebox.showinfo("Info", "No episodes selected")
            return
            
        if messagebox.askyesno("Confirm Delete", f"Delete {len(self.selected_keys)} episodes?"):
            for key in self.selected_keys:
                if key in self.config.metadata:
                    del self.config.metadata[key]
            
            self.config.save_metadata()
            self.refresh_list()
            self.set_status(f"Deleted {len(self.selected_keys)} episodes")
    
    def export_json(self):
        try:
            data = {
                "user": self.user,
                "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "episodes": [v for k, v in self.config.metadata.items() if v.get("valid")]
            }
            path = self.config.paths.json_dir / "odd_couple_complete.json"
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Exported", f"JSON saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting JSON: {e}")
    
    def create_m3u(self):
        try:
            lines = ["#EXTM3U"]
            for key, ep in sorted(self.config.metadata.items(), 
                                key=lambda x: (x[1]['season'], x[1]['episode'])):
                if ep.get("valid"):
                    dur = int(ep.get("duration", 0))
                    title = f"The Odd Couple {key} - {ep['title']}"
                    lines.append(f"#EXTINF:{dur},{title}")
                    lines.append(ep["url"])
            
            path = self.config.paths.m3u_dir / "the_odd_couple_master.m3u"
            with open(path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
            messagebox.showinfo("M3U", f"Master playlist saved:\n{path}")
        except Exception as e:
            messagebox.showerror("M3U Error", f"Error creating M3U: {e}")

def main():
    """Main function to start the application"""
    try:
        root = tk.Tk()
        app = OddCoupleManager(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")