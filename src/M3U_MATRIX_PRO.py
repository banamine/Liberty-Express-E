
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, font, simpledialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import re, os, threading, tempfile, webbrowser, urllib.request, socket, json, csv, subprocess
from datetime import datetime, timedelta
from collections import defaultdict
from urllib.parse import urlparse
import requests
import sys
import logging
from pathlib import Path
import uuid

# Add script directory to sys.path for local imports
script_dir = str(Path(__file__).parent.resolve())
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Optional imports - only needed for advanced features
try:
    from page_generator import NexusTVPageGenerator, WebIPTVGenerator
    PAGE_GENERATOR_AVAILABLE = True
except ImportError as e:
    PAGE_GENERATOR_AVAILABLE = False
    logging.warning(f"Page generator not available: {e}")

try:
    from utils import (sanitize_filename, validate_url, validate_file_path, 
                       sanitize_input, SimpleCache, is_valid_m3u, 
                       download_and_cache_thumbnail, get_cached_thumbnail_stats)
    UTILS_AVAILABLE = True
except ImportError as e:
    UTILS_AVAILABLE = False
    logging.warning(f"Utils module not available: {e}")
    download_and_cache_thumbnail = None
    get_cached_thumbnail_stats = None
    # Minimal fallback functions
    def sanitize_filename(filename, max_length=255):
        """Remove dangerous characters from filename"""
        clean = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return clean[:max_length] if len(clean) > max_length else clean
    
    def validate_url(url):
        """Basic URL validation"""
        return url.startswith(('http://', 'https://', 'rtmp://', 'rtsp://'))
    
    def validate_file_path(file_path, base_dir=None):
        """Basic path validation"""
        try:
            path = Path(file_path)
            if base_dir and not path.is_relative_to(base_dir):
                return False
            return True
        except:
            return False
    
    def sanitize_input(text, max_length=None):
        """Sanitize user input to prevent injection attacks"""
        if not text:
            return ""
        # Remove control characters
        sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        # Remove potential script tags
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        # Remove HTML tags
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        # Limit length if specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        return sanitized
    
    def is_valid_m3u(content):
        """Check if content is valid M3U format"""
        return '#EXTM3U' in content or '#EXTINF' in content
    
    class SimpleCache:
        """Simple LRU cache implementation"""
        def __init__(self, max_size=200):
            self.cache = {}
            self.max_size = max_size
            self.access_order = []
        
        def get(self, key):
            if key in self.cache:
                self.access_order.remove(key)
                self.access_order.append(key)
                return self.cache[key]
            return None
        
        def set(self, key, value):
            if key in self.cache:
                self.access_order.remove(key)
            elif len(self.cache) >= self.max_size:
                oldest = self.access_order.pop(0)
                del self.cache[oldest]
            self.cache[key] = value
            self.access_order.append(key)

# Setup logging
log_path = Path(__file__).parent / "logs" / "m3u_matrix.log"
log_path.parent.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_path),
              logging.StreamHandler()])

socket.setdefaulttimeout(7)


class M3UMatrix:

    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title(
            "M3U MATRIX PRO • DRAG & DROP M3U FILES • DOUBLE-CLICK TO OPEN")
        self.root.geometry("1600x950")
        self.root.minsize(1300, 800)
        self.root.configure(bg="#121212")

        # Set working directory to application folder
        os.chdir(Path(__file__).parent)

        self.files = []
        self.channels = []
        self.m3u = ""
        self.clipboard = None
        self.drag_data = {"iid": None, "y": 0}
        self.schedule = {}
        self.custom_tags = {}
        self.epg_data = {}
        self.settings = {}
        self.logger = logging.getLogger(__name__)
        self.thumbnail_cache = SimpleCache(max_size=200)  # Cache for thumbnails
        self.filter_cache = {}  # Cache for filter results
        self.autosave_counter = 0  # Track changes for autosave
        self.last_save_time = datetime.now()
        
        # Undo/Redo system
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_history = 50
        
        # Performance & UX improvements
        self.uuid_to_iid_map = {}  # O(1) lookup for treeview updates
        self.dirty = False  # Track unsaved changes
        self.search_debounce_id = None  # For debounced search

        self.setup_error_handling()
        self.load_settings()
        self.build_ui()
        self.load_tv_guide()
        self.start_autosave()
        self.logger.info("M3U Matrix started successfully")
        self.root.mainloop()

    def setup_error_handling(self):
        """Setup comprehensive error handling"""

        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            self.logger.error("Uncaught exception",
                              exc_info=(exc_type, exc_value, exc_traceback))
            self.show_error_dialog(
                "Unexpected Error",
                f"An unexpected error occurred: {exc_value}")

        sys.excepthook = handle_exception

    def show_error_dialog(self, title, message, exception=None):
        """Show user-friendly error dialog with helpful suggestions"""
        # Log the full error
        if exception:
            self.logger.error(f"{title}: {message} - {str(exception)}")
        else:
            self.logger.error(f"{title}: {message}")
        
        # Create user-friendly dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"⚠️ {title}")
        dialog.geometry("600x400")
        dialog.configure(bg="#1e1e1e")
        dialog.resizable(True, True)
        
        # Title
        tk.Label(dialog, text=f"⚠️ {title}", font=("Arial", 16, "bold"),
                fg="#ff6b6b", bg="#1e1e1e").pack(pady=15)
        
        # Message frame
        frame = tk.Frame(dialog, bg="#2e2e2e", relief=tk.RAISED, bd=2)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Main message
        tk.Label(frame, text=message, font=("Arial", 11), 
                fg="#fff", bg="#2e2e2e", wraplength=550, justify=tk.LEFT).pack(pady=10, padx=10)
        
        # Technical details (if available)
        if exception:
            tk.Label(frame, text="Technical Details:", font=("Arial", 10, "bold"),
                    fg="#ffd93d", bg="#2e2e2e").pack(anchor=tk.W, padx=10, pady=(10,5))
            
            details_text = tk.Text(frame, bg="#1a1a1a", fg="#aaa", 
                                  font=("Courier", 9), height=6, wrap=tk.WORD)
            details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            details_text.insert("1.0", str(exception))
            details_text.config(state=tk.DISABLED)
        
        # Helpful suggestions based on error type
        suggestions = []
        error_str = str(exception).lower() if exception else message.lower()
        
        if "network" in error_str or "connection" in error_str or "timeout" in error_str:
            suggestions.append("• Check your internet connection")
            suggestions.append("• The server might be temporarily down")
            suggestions.append("• Try again in a few moments")
        elif "file" in error_str or "not found" in error_str:
            suggestions.append("• Verify the file path is correct")
            suggestions.append("• Check if the file exists")
            suggestions.append("• Ensure you have permission to access it")
        elif "permission" in error_str:
            suggestions.append("• Run the application as administrator")
            suggestions.append("• Check file/folder permissions")
        elif "invalid" in error_str or "malformed" in error_str:
            suggestions.append("• The M3U file may be corrupted")
            suggestions.append("• Try opening it in a text editor first")
            suggestions.append("• Verify the file format is correct")
        
        if suggestions:
            tk.Label(frame, text="💡 Suggestions:", font=("Arial", 10, "bold"),
                    fg="#00ff41", bg="#2e2e2e").pack(anchor=tk.W, padx=10, pady=(10,5))
            
            for suggestion in suggestions:
                tk.Label(frame, text=suggestion, font=("Arial", 9),
                        fg="#ddd", bg="#2e2e2e").pack(anchor=tk.W, padx=25, pady=2)
        
        # Close button
        tk.Button(dialog, text="Close", command=dialog.destroy,
                 bg="#e74c3c", fg="#fff", font=("Arial", 11),
                 width=15, height=2).pack(pady=15)

    def load_settings(self):
        """Load user settings"""
        settings_file = "m3u_matrix_settings.json"
        default_settings = {
            "window_geometry": "1600x950",
            "theme": "dark",
            "auto_check_channels": False,
            "default_epg_url": "",
            "recent_files": [],
            "cache_thumbnails": True,
            "use_ffmpeg_extraction": False
        }

        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    self.settings = {**default_settings, **json.load(f)}
            else:
                self.settings = default_settings
        except Exception as e:
            self.settings = default_settings
            self.logger.warning(f"Failed to load settings: {e}")

    def save_settings(self):
        """Save user settings"""
        try:
            with open("m3u_matrix_settings.json", 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
    
    def export_settings(self):
        """Export settings to backup file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=f"m3u_matrix_settings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(self.settings, f, indent=2)
                messagebox.showinfo("Settings Exported", 
                                  f"Settings exported successfully to:\n{os.path.basename(filename)}")
                self.stat.config(text="Settings exported")
        except Exception as e:
            self.show_error_dialog("Export Failed", "Could not export settings", e)
    
    def import_settings(self):
        """Import settings from backup file"""
        try:
            filename = filedialog.askopenfilename(
                title="Import Settings",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    imported_settings = json.load(f)
                
                # Validate it's actually settings
                if isinstance(imported_settings, dict):
                    self.settings = imported_settings
                    self.save_settings()
                    messagebox.showinfo("Settings Imported", 
                                      "Settings imported successfully!\nRestart app to apply all changes.")
                    self.stat.config(text="Settings imported")
                else:
                    messagebox.showerror("Invalid File", 
                                        "The selected file doesn't contain valid settings.")
        except Exception as e:
            self.show_error_dialog("Import Failed", "Could not import settings", e)

    def build_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=8, font=("Arial", 10, "bold"))
        style.configure("Treeview",
                        background="#1e1e1e",
                        foreground="#ffffff",
                        fieldbackground="#1e1e1e",
                        rowheight=28)
        style.configure("Treeview.Heading",
                        background="#333",
                        foreground="gold",
                        font=("Arial", 11, "bold"))

        # === HEADER ===
        header = tk.Frame(self.root, bg="#8e44ad", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header,
                 text="M3U MATRIX PRO",
                 font=("Impact", 28),
                 fg="gold",
                 bg="#8e44ad").pack(side=tk.LEFT, padx=20)
        tk.Label(
            header,
            text=
            "DRAG to reorder • DOUBLE-CLICK to edit • RIGHT-CLICK for magic",
            fg="#fff",
            bg="#8e44ad").pack(side=tk.RIGHT, padx=20)

        # === TOOLBAR (3 ROWS) ===
        toolbar_container = tk.Frame(self.root, bg="#1e1e1e")
        toolbar_container.pack(fill=tk.X, pady=5)
        
        # ROW 1: File Operations
        tb1 = tk.Frame(toolbar_container, bg="#1e1e1e")
        tb1.pack(fill=tk.X, pady=2)
        row1 = [("LOAD", "#2980b9", self.load),
                ("SAVE", "#c0392b", self.save),
                ("M3U OUTPUT", "#16a085", self.export_m3u_output),
                ("EXPORT JSON", "#16a085", self.export_json),
                ("NEW", "#34495e", self.new_project)]
        for txt, col, cmd in row1:
            tk.Button(tb1, text=txt, bg=col, fg="white", width=14,
                      command=cmd).pack(side=tk.LEFT, padx=4)
        
        # ROW 2: Processing & Generation
        tb2 = tk.Frame(toolbar_container, bg="#1e1e1e")
        tb2.pack(fill=tk.X, pady=2)
        row2 = [("ORGANIZE", "#27ae60", self.organize_channels),
                ("CHECK", "#e67e22", self.start_check),
                ("GENERATE PAGES", "#e91e63", self.generate_pages),
                ("SMART SCHEDULE", "#9b59b6", self.smart_scheduler),
                ("JSON GUIDE", "#95e1d3", self.export_tv_guide_json)]
        for txt, col, cmd in row2:
            tk.Button(tb2, text=txt, bg=col, fg="white", width=14,
                      command=cmd).pack(side=tk.LEFT, padx=4)
        
        # ROW 3: Import & Advanced
        tb3 = tk.Frame(toolbar_container, bg="#1e1e1e")
        tb3.pack(fill=tk.X, pady=2)
        row3 = [("URL IMPORT", "#4ecdc4", self.url_import_workbench),
                ("IMPORT URL", "#8e44ad", self.import_url),
                ("TIMESTAMP GEN", "#ff6b6b", self.timestamp_generator),
                ("FETCH EPG", "#d35400", self.fetch_epg),
                ("TV GUIDE", "#9b59b6", self.open_guide),
                ("LAUNCH REDIS", "#FF5733", self.launch_redis_services)]
        for txt, col, cmd in row3:
            tk.Button(tb3, text=txt, bg=col, fg="white", width=14,
                      command=cmd).pack(side=tk.LEFT, padx=4)

        # === SEARCH + TOOLS + SETTINGS ===
        tools = tk.Frame(self.root, bg="#1e1e1e")
        tools.pack(fill=tk.X, pady=5, padx=10)
        tk.Label(tools, text="Search:", fg="#fff",
                 bg="#1e1e1e").pack(side=tk.LEFT)
        self.search = tk.StringVar()
        self.search.trace("w", lambda *_: self.filter_debounced())
        tk.Entry(tools,
                 textvariable=self.search,
                 width=30,
                 bg="#333",
                 fg="#fff",
                 insertbackground="#fff").pack(side=tk.LEFT, padx=8)
        
        # Settings menu
        tk.Button(tools, text="⚙️ Export Settings", command=self.export_settings,
                 bg="#34495e", fg="#fff", font=("Arial", 9)).pack(side=tk.RIGHT, padx=5)
        tk.Button(tools, text="⚙️ Import Settings", command=self.import_settings,
                 bg="#34495e", fg="#fff", font=("Arial", 9)).pack(side=tk.RIGHT, padx=5)
        for txt, col, cmd in [("CUT", "#e74c3c", self.cut),
                              ("COPY", "#3498db", self.copy),
                              ("PASTE", "#2ecc71", self.paste),
                              ("UNDO", "#f39c12", self.undo),
                              ("REDO", "#9b59b6", self.redo)]:
            tk.Button(tools,
                      text=txt,
                      bg=col,
                      fg="white",
                      width=10,
                      command=cmd).pack(side=tk.LEFT, padx=4)

        # === MAIN PANEL ===
        main = tk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # LEFT: Files + Guide
        left = tk.Frame(main, bg="#1e1e1e", width=300)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left.pack_propagate(False)

        tk.Label(left,
                 text="Loaded Files (DRAG M3U HERE!)",
                 fg="gold",
                 bg="#1e1e1e",
                 font=("Arial", 12, "bold")).pack(pady=5)
        self.file_list = tk.Listbox(left,
                                    bg="#333",
                                    fg="#fff",
                                    selectbackground="#8e44ad")
        self.file_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.file_list.bind("<Button-3>", self.file_menu)
        self.file_list.bind("<Double-1>", self.open_file_from_list)

        # Enable drag and drop on file list
        self.file_list.drop_target_register(DND_FILES)
        self.file_list.dnd_bind('<<Drop>>', self.drop_files)

        tk.Label(left,
                 text="TV Guide Preview",
                 fg="gold",
                 bg="#1e1e1e",
                 font=("Arial", 12, "bold")).pack(pady=(15, 5))
        self.guide_prev = tk.Text(left,
                                  height=12,
                                  bg="#111",
                                  fg="#0f0",
                                  font=("Courier", 9),
                                  wrap=tk.WORD)
        self.guide_prev.pack(fill=tk.X, padx=5, pady=5)

        # RIGHT: Channel Matrix
        right = tk.Frame(main)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tf = tk.LabelFrame(
            right,
            text="CHANNEL MATRIX – DRAG to sort • DOUBLE-CLICK to edit",
            fg="gold",
            bg="#1e1e1e")
        tf.pack(fill=tk.BOTH, expand=True)

        cols = ("#", "Now Playing", "Next", "Group", "Name", "URL", "Backs",
                "Tags", "Del")
        self.tv = ttk.Treeview(tf, columns=cols, show="headings")
        
        # Responsive column configuration with relative sizing
        # Format: (width, minwidth, stretch)
        column_config = {
            "#": (50, 40, False),
            "Now Playing": (180, 120, True),
            "Next": (180, 100, True),
            "Group": (120, 80, True),
            "Name": (200, 150, True),
            "URL": (380, 200, True),
            "Backs": (70, 50, False),
            "Tags": (80, 60, False),
            "Del": (50, 40, False)
        }
        
        for c in cols:
            width, minwidth, stretch = column_config[c]
            self.tv.heading(c, text=c, command=lambda col=c: self.sort_by(col))
            self.tv.column(c,
                           width=width,
                           minwidth=minwidth,
                           stretch=stretch,
                           anchor="center" if c in ("#", "Backs", "Tags",
                                                    "Del") else "w")
        self.tv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(tf, command=self.tv.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tv.configure(yscrollcommand=vsb.set)

        # DRAG DROP & EDIT
        self.tv.bind("<ButtonPress-1>", self.drag_start)
        self.tv.bind("<B1-Motion>", self.drag_motion)
        self.tv.bind("<ButtonRelease-1>", self.drag_stop)
        self.tv.bind("<Double-1>", self.on_double)
        self.tv.bind("<Button-3>", self.row_menu)

        # STATUS
        self.stat = tk.Label(self.root,
                             text="MATRIX ONLINE - Ready to work!",
                             fg="#0f0",
                             bg="#000",
                             font=("Courier", 11),
                             anchor="w")
        self.stat.pack(fill=tk.X, side=tk.BOTTOM, pady=5)

        self.editor = None

    # ========== COMPLETE CLIPBOARD IMPLEMENTATION ==========
    def cut(self):
        """Cut selected channels to clipboard"""
        selection = self.tv.selection()
        if not selection:
            messagebox.showwarning("No Selection",
                                   "Select channels to cut first!")
            return
        
        self.save_state(f"Cut {len(selection)} channels")

        self.clipboard = {
            "operation": "cut",
            "channels": [],
            "indices": [self.tv.index(iid) for iid in selection]
        }

        for iid in selection:
            num = int(self.tv.item(iid, "values")[0])
            channel = next(c for c in self.channels if c["num"] == num)
            self.clipboard["channels"].append(channel.copy())

        self.stat.config(text=f"CUT: {len(selection)} channels to clipboard")

    def copy(self):
        """Copy selected channels to clipboard"""
        selection = self.tv.selection()
        if not selection:
            messagebox.showwarning("No Selection",
                                   "Select channels to copy first!")
            return

        self.clipboard = {
            "operation": "copy",
            "channels": [],
            "indices": [self.tv.index(iid) for iid in selection]
        }

        for iid in selection:
            num = int(self.tv.item(iid, "values")[0])
            channel = next(c for c in self.channels if c["num"] == num)
            self.clipboard["channels"].append(channel.copy())

        self.stat.config(
            text=f"COPIED: {len(selection)} channels to clipboard")

    def save_state(self, operation_name):
        """Save current state for undo"""
        state = {
            'operation': operation_name,
            'channels': [ch.copy() for ch in self.channels],
            'timestamp': datetime.now()
        }
        
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_undo_history:
            self.undo_stack.pop(0)
        
        # Clear redo stack when new action is performed
        self.redo_stack.clear()
    
    def undo(self):
        """Undo last operation"""
        if not self.undo_stack:
            self.stat.config(text="Nothing to undo")
            return
        
        # Save current state to redo stack
        current_state = {
            'operation': 'redo_point',
            'channels': [ch.copy() for ch in self.channels],
            'timestamp': datetime.now()
        }
        self.redo_stack.append(current_state)
        
        # Restore previous state
        previous_state = self.undo_stack.pop()
        self.channels = previous_state['channels']
        
        self.fill()
        self.build_m3u()
        self.stat.config(text=f"UNDO: {previous_state['operation']}")
    
    def redo(self):
        """Redo last undone operation"""
        if not self.redo_stack:
            self.stat.config(text="Nothing to redo")
            return
        
        # Save current state to undo stack
        current_state = {
            'operation': 'undo_point',
            'channels': [ch.copy() for ch in self.channels],
            'timestamp': datetime.now()
        }
        self.undo_stack.append(current_state)
        
        # Restore redo state
        redo_state = self.redo_stack.pop()
        self.channels = redo_state['channels']
        
        self.fill()
        self.build_m3u()
        self.stat.config(text="REDO")

    def paste(self):
        """Paste clipboard channels"""
        if not self.clipboard:
            messagebox.showwarning("Empty Clipboard",
                                   "Cut or copy channels first!")
            return
        
        self.save_state(f"Paste {len(self.clipboard['channels'])} channels")
        self.mark_changed()

        if self.clipboard["operation"] == "cut":
            # Remove original channels when pasting a cut
            for channel in self.clipboard["channels"]:
                self.channels = [
                    c for c in self.channels if c["num"] != channel["num"]
                ]

        # Add clipboard channels to current list
        for channel in self.clipboard["channels"]:
            new_channel = channel.copy()
            if self.clipboard["operation"] == "copy":
                new_channel["num"] = max([c["num"] for c in self.channels],
                                         default=0) + 1
            self.channels.append(new_channel)

        self.auto_increment_channels()
        self.fill()
        self.build_m3u()

        action = "MOVED" if self.clipboard["operation"] == "cut" else "COPIED"
        self.stat.config(
            text=f"{action}: {len(self.clipboard['channels'])} channels")
        self.clipboard = None

    # ========== COMPLETE CHANNEL CHECKER ==========
    def start_check(self):
        """Comprehensive channel validation and audit"""
        if not self.channels:
            messagebox.showwarning("No Channels", "Load channels first!")
            return

        # Create progress dialog with cancel
        progress_dialog, progress_var, status_label, cancel_flag = self.create_progress_dialog(
            "🔍 Checking Channels", len(self.channels))

        def check_thread():
            results = {
                "working": 0,
                "broken": 0,
                "timeout": 0,
                "total": len(self.channels)
            }

            for i, channel in enumerate(self.channels):
                # Check if cancelled
                if cancel_flag["cancelled"]:
                    self.root.after(0, lambda: progress_dialog.destroy())
                    self.root.after(0, lambda: self.stat.config(
                        text=f"CHECK CANCELLED - Checked {i}/{len(self.channels)} channels"))
                    return
                
                status = self.validate_channel(channel)
                results[status] += 1

                # Update progress bar and status
                self.root.after(0, lambda p=i+1, ch=channel.get('name', 'Unknown'): (
                    progress_var.set(p),
                    status_label.config(text=f"Checking {p}/{len(self.channels)}: {ch[:40]}...")
                ))

                # Update channel status in treeview (using UUID for safety)
                channel_uuid = channel.get('uuid', '')
                self.root.after(0,
                                lambda uuid=channel_uuid, stat=status: self.
                                update_channel_status(uuid, stat, results))

                # Small delay to avoid overwhelming servers
                threading.Event().wait(0.1)

            # Close progress dialog and show results
            self.root.after(0, lambda: progress_dialog.destroy())
            self.root.after(0, lambda: self.show_audit_results(results))

        threading.Thread(target=check_thread, daemon=True).start()

    def validate_channel(self, channel):
        """Validate a single channel's URL and metadata"""
        url = channel.get("url", "")

        if not url or not url.startswith(('http', 'rtmp', 'rtsp')):
            return "broken"

        try:
            if url.startswith('http'):
                # HTTP-based streams - Try GET with range first (more reliable than HEAD)
                try:
                    response = requests.get(url, timeout=5, allow_redirects=True,
                                          headers={'Range': 'bytes=0-1024'},
                                          stream=True)
                    # Accept 200 (OK), 206 (Partial Content), or 403 (stream exists but needs auth)
                    if response.status_code in (200, 206, 403):
                        return "working"
                    else:
                        return "broken"
                except requests.exceptions.RequestException:
                    # Fallback to HEAD request if GET fails
                    try:
                        response = requests.head(url, timeout=5, allow_redirects=True)
                        if response.status_code in (200, 403):
                            return "working"
                        else:
                            return "broken"
                    except:
                        return "broken"
            else:
                # RTMP/RTSP - enhanced connection test with handshake
                return self.validate_stream_protocol(url)

        except requests.exceptions.Timeout:
            return "timeout"
        except Exception:
            return "broken"
    
    def validate_stream_protocol(self, url):
        """Enhanced validation for RTMP/RTSP streams with socket handshake"""
        try:
            parsed = urlparse(url)
            protocol = parsed.scheme.lower()
            hostname = parsed.hostname
            
            if not hostname:
                return "broken"
            
            # Determine default port based on protocol
            if protocol == 'rtmp' or protocol == 'rtmps':
                default_port = 1935
            elif protocol == 'rtsp':
                default_port = 554
            else:
                default_port = 1935  # Fallback
            
            port = parsed.port or default_port
            
            # Create socket with timeout
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            try:
                # Attempt connection
                sock.connect((hostname, port))
                
                # For RTSP, send OPTIONS request to verify server response
                if protocol == 'rtsp':
                    options_request = f"OPTIONS {url} RTSP/1.0\r\nCSeq: 1\r\n\r\n"
                    sock.sendall(options_request.encode('utf-8'))
                    
                    # Try to receive response (with small timeout)
                    sock.settimeout(2)
                    try:
                        response = sock.recv(1024).decode('utf-8', errors='ignore')
                        # Check if we got a valid RTSP response
                        if 'RTSP/1.0' in response or 'RTSP/2.0' in response:
                            sock.close()
                            return "working"
                    except socket.timeout:
                        # No response, but connection worked - likely valid
                        sock.close()
                        return "working"
                else:
                    # For RTMP, just connection test (full handshake is complex)
                    sock.close()
                    return "working"
                    
            except socket.timeout:
                return "timeout"
            except (socket.error, OSError):
                return "broken"
            finally:
                try:
                    sock.close()
                except:
                    pass
                    
        except Exception as e:
            self.logger.debug(f"Stream protocol validation failed for {url}: {e}")
            return "broken"

    def update_channel_status(self, channel_uuid, status, results):
        """Update UI with channel validation status using UUID with O(1) lookup"""
        # O(1) lookup using UUID-to-IID mapping
        iid = self.uuid_to_iid_map.get(channel_uuid)
        
        if not iid or not self.tv.exists(iid):
            return  # Channel not found (may have been deleted or not in view)

        # Update treeview with status - O(1) operation
        values = list(self.tv.item(iid, "values"))
        status_icons = {"working": "✓", "broken": "✗", "timeout": "⌛"}
        # Remove any previous status icon before adding new one
        current_value = str(values[1])
        for icon in status_icons.values():
            current_value = current_value.replace(f"{icon} ", "")
        values[1] = f"{status_icons.get(status, '?')} {current_value}"
        self.tv.item(iid, values=values)

        # Update status bar
        self.stat.config(
            text=
            f"AUDIT: {results['working']}✓ {results['broken']}✗ {results['timeout']}⌛"
        )

    def show_audit_results(self, results):
        """Show comprehensive audit results"""
        report = f"""
Channel Audit Complete:
✅ Working: {results['working']} channels
❌ Broken: {results['broken']} channels  
⏰ Timeout: {results['timeout']} channels
📊 Total: {results['total']} channels

Success Rate: {results['working']/results['total']*100:.1f}%
"""
        messagebox.showinfo("Audit Results", report)
        self.stat.config(
            text=
            f"AUDIT COMPLETE: {results['working']}/{results['total']} channels working"
        )

    # ========== DIRTY FLAG FOR UNSAVED CHANGES ==========
    def mark_dirty(self):
        """Mark that there are unsaved changes and update window title"""
        if not self.dirty:
            self.dirty = True
            self.update_window_title()
    
    def mark_clean(self):
        """Mark that all changes are saved and update window title"""
        if self.dirty:
            self.dirty = False
            self.update_window_title()
    
    def update_window_title(self):
        """Update window title to reflect unsaved changes"""
        base_title = "M3U MATRIX PRO • DRAG & DROP M3U FILES • DOUBLE-CLICK TO OPEN"
        if self.dirty:
            self.root.title(f"* (Unsaved Changes) - {base_title}")
        else:
            self.root.title(base_title)

    # ========== MEDIA FILE DETECTION ==========
    def is_media_file(self, file_path):
        """Detect if file is a video/audio file instead of M3U playlist"""
        media_extensions = {
            # Video formats
            '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v',
            '.mpg', '.mpeg', '.3gp', '.ts', '.m2ts', '.vob', '.ogv',
            # Audio formats
            '.mp3', '.aac', '.wav', '.flac', '.ogg', '.m4a', '.wma', '.opus',
            '.ape', '.alac', '.aiff'
        }
        
        ext = os.path.splitext(file_path)[1].lower()
        return ext in media_extensions
    
    def create_channel_from_media_file(self, file_path):
        """Create a channel entry from a video/audio file"""
        filename = os.path.basename(file_path)
        name_without_ext = os.path.splitext(filename)[0]
        ext = os.path.splitext(file_path)[1].lower()
        
        # Determine group based on file type
        video_exts = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v',
                      '.mpg', '.mpeg', '.3gp', '.ts', '.m2ts', '.vob', '.ogv'}
        audio_exts = {'.mp3', '.aac', '.wav', '.flac', '.ogg', '.m4a', '.wma', '.opus',
                      '.ape', '.alac', '.aiff'}
        
        if ext in video_exts:
            group = "Videos"
        elif ext in audio_exts:
            group = "Audio"
        else:
            group = "Media Files"
        
        # Create channel structure
        channel = {
            "name": name_without_ext,
            "group": group,
            "logo": "",
            "tvg_id": "",
            "num": 0,
            "url": file_path,  # Use local file path as URL
            "backups": [],
            "custom_tags": {
                "FILE-TYPE": ext[1:].upper(),  # e.g., "MP4", "MKV"
                "FILE-SIZE": self.get_file_size(file_path),
                "SOURCE": "LOCAL-FILE"
            }
        }
        
        return channel
    
    def get_file_size(self, file_path):
        """Get human-readable file size"""
        try:
            size_bytes = os.path.getsize(file_path)
            
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
        except:
            return "Unknown"

    # ========== ENHANCED M3U PARSING ==========
    def parse_m3u_file(self, file_path):
        """Robust M3U parser with support for EXTGRP, custom tags, and duplicates handling"""
        channels = []
        current_channel = None
        custom_tags = {}

        try:
            try:
                with open(file_path, 'r', encoding='utf-8',
                          errors='ignore') as f:
                    lines = f.readlines()
            except Exception:
                with open(file_path, 'r', encoding='latin-1') as f:
                    lines = f.readlines()
        except Exception as e:
            self.root.after(
                0, lambda: messagebox.showerror(
                    "File Read Error",
                    f"Cannot read file {os.path.basename(file_path)}: {e}"))
            return []

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if not line or line == "#EXTM3U":
                i += 1
                continue

            if line.startswith("#EXTINF"):
                current_channel = self.parse_extinf_line(line)
                if i + 1 < len(lines) and lines[i + 1].startswith("#EXTGRP"):
                    current_channel["group"] = lines[i +
                                                     1].split(":")[1].strip()
                    i += 1
                i += 1
                continue

            if line.startswith(
                    "#") and ":" in line and not line.startswith("#EXTINF"):
                tag_parts = line[1:].split(":", 1)
                if len(tag_parts) == 2:
                    tag_name, tag_value = tag_parts
                    custom_tags[tag_name.strip()] = tag_value.strip()
                i += 1
                continue

            if current_channel and (line.startswith("http")
                                    or line.startswith("rtmp")
                                    or line.startswith("rtsp")):
                current_channel["url"] = line.strip()
                current_channel["custom_tags"] = custom_tags.copy()
                
                # Download and cache thumbnail if enabled
                if self.settings.get("cache_thumbnails", True) and current_channel.get("logo") and download_and_cache_thumbnail:
                    cached_path, status = download_and_cache_thumbnail(
                        current_channel["logo"],
                        current_channel["name"],
                        self.thumbnails_dir,
                        timeout=5
                    )
                    if cached_path:
                        current_channel["logo"] = cached_path
                        current_channel["logo_cached"] = True
                
                channels.append(current_channel)
                current_channel = None
                custom_tags = {}

            i += 1

        return channels

    def parse_extinf_line(self, line):
        """Parse EXTINF line with support for various attributes"""
        channel = {
            "name": "Unknown",
            "group": "Other",
            "logo": "",
            "tvg_id": "",
            "num": 0,
            "url": "",
            "backups": []
        }

        attr_pattern = r'([a-zA-Z-]+)="([^"]*)"'
        attributes = dict(re.findall(attr_pattern, line))

        name_part = line.split(',')[-1].strip()
        if name_part:
            channel["name"] = name_part

        if "tvg-name" in attributes:
            channel["name"] = attributes["tvg-name"]
        if "group-title" in attributes:
            channel["group"] = attributes["group-title"]
        if "tvg-logo" in attributes:
            channel["logo"] = attributes["tvg-logo"]
        if "tvg-id" in attributes:
            channel["tvg_id"] = attributes["tvg-id"]

        return channel

    # ========== ADVANCED ORGANIZE ROUTINE ==========
    def organize_channels(self):
        """Normalize groups, remove duplicates, and auto-increment channel numbers"""
        if not self.channels:
            messagebox.showwarning("No Channels", "Load M3U files first!")
            return

        self.save_state("Organize channels")
        self.mark_changed()
        
        group_mapping = self.normalize_groups()
        self.remove_duplicates()
        self.auto_increment_channels()
        self.channels.sort(
            key=lambda x: (x.get("group", "Other"), x.get("name", "")))

        self.root.after(0, self.fill)
        self.root.after(0, self.build_m3u)
        self.root.after(
            0, lambda: self.stat.config(
                text=
                f"ORGANIZED: {len(self.channels)} channels, {len(group_mapping)} groups"
            ))

    def normalize_groups(self):
        """Normalize group names and return mapping"""
        group_mapping = {}
        normalized_groups = set()

        for channel in self.channels:
            original_group = channel.get("group", "Other")
            normalized = self.clean_group_name(original_group)

            if original_group not in group_mapping:
                group_mapping[original_group] = normalized
                normalized_groups.add(normalized)

            channel["group"] = normalized

        return group_mapping

    def clean_group_name(self, group_name):
        """Clean and standardize group names"""
        if not group_name or group_name.strip() == "":
            return "Other"

        cleaned = group_name.strip()

        replacements = {
            "ENTERTAINMENT": "Entertainment",
            "MOVIES": "Movies",
            "SPORTS": "Sports",
            "NEWS": "News",
            "KIDS": "Kids",
            "MUSIC": "Music",
            "DOCUMENTARIES": "Documentaries",
            "REGIONAL": "Regional",
            "INTERNATIONAL": "International"
        }

        for key, value in replacements.items():
            if key in cleaned.upper():
                return value

        return ' '.join(word.capitalize() for word in cleaned.split())

    def remove_duplicates(self):
        """Remove duplicate channels based on URL and name"""
        unique_channels = []
        seen = set()

        for channel in self.channels:
            identifier = (channel.get("url",
                                      "").lower(), channel.get("name",
                                                               "").lower())

            if identifier not in seen:
                seen.add(identifier)
                unique_channels.append(channel)

        removed_count = len(self.channels) - len(unique_channels)
        self.channels = unique_channels

        if removed_count > 0:
            self.stat.config(text=f"Removed {removed_count} duplicates")

    def auto_increment_channels(self):
        """Auto-increment channel numbers starting from 1"""
        for i, channel in enumerate(self.channels, 1):
            channel["num"] = i

    # ========== EXPORT FEATURES ==========
    def export_json(self):
        """Export channels as JSON with full metadata"""
        if not self.channels:
            messagebox.showwarning("No Channels", "Load channels first!")
            return
        
        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=str(exports_dir),
            initialfile=f"playlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            try:
                # Build comprehensive JSON export
                export_data = {
                    "metadata": {
                        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "total_channels": len(self.channels),
                        "app_version": "M3U Matrix Pro v4.0",
                        "format": "M3U Matrix JSON Export"
                    },
                    "channels": []
                }
                
                # Group channels by category
                groups = defaultdict(list)
                for ch in self.channels:
                    group = ch.get('group', 'Other')
                    channel_data = {
                        "uuid": ch.get('uuid', ''),
                        "number": ch.get('num', 0),
                        "name": ch.get('name', ''),
                        "url": ch.get('url', ''),
                        "logo": ch.get('logo', ''),
                        "group": group,
                        "tvg_id": ch.get('tvg_id', ''),
                        "custom_tags": ch.get('custom_tags', {})
                    }
                    groups[group].append(channel_data)
                    export_data["channels"].append(channel_data)
                
                # Add group summary
                export_data["groups"] = {
                    group: len(channels) for group, channels in groups.items()
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", 
                                  f"JSON export complete!\n\n"
                                  f"Channels: {len(self.channels)}\n"
                                  f"Groups: {len(groups)}\n"
                                  f"File: {os.path.basename(filename)}")
                self.stat.config(text=f"Exported {len(self.channels)} channels to JSON")
            except Exception as e:
                self.show_error_dialog("Export Failed", "Could not export to JSON", e)
    
    def export_csv(self):
        """Export channel list to CSV file"""
        if not self.channels:
            messagebox.showwarning("No Data", "No channels to export!")
            return

        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)
        
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[
                                                    ("CSV files", "*.csv"),
                                                    ("All files", "*.*")
                                                ],
                                                initialdir=str(exports_dir),
                                                initialfile=f"channels_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                                title="Export channels to CSV")

        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'Number', 'Name', 'Group', 'URL', 'Logo', 'TVG-ID',
                    'Backup_URLs'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()

                for channel in self.channels:
                    writer.writerow({
                        'Number':
                        channel.get('num', ''),
                        'Name':
                        channel.get('name', ''),
                        'Group':
                        channel.get('group', ''),
                        'URL':
                        channel.get('url', ''),
                        'Logo':
                        channel.get('logo', ''),
                        'TVG-ID':
                        channel.get('tvg_id', ''),
                        'Backup_URLs':
                        '|'.join(channel.get('backups', []))
                    })

            messagebox.showinfo("Export Successful",
                                f"Channels exported to {filename}")
            self.stat.config(
                text=f"EXPORTED: {len(self.channels)} channels to CSV")

        except Exception as e:
            messagebox.showerror("Export Error",
                                 f"Failed to export CSV: {str(e)}")

    # ========== IMPORT FROM REMOTE M3U URL ==========
    def import_url(self):
        """Import M3U playlist from remote URL with security validation"""
        url = simpledialog.askstring("Import M3U URL",
                                     "Enter M3U playlist URL:")
        if not url:
            return
        
        # SECURITY: Sanitize and validate URL
        url = sanitize_input(url).strip()
        
        if not validate_url(url):
            messagebox.showerror("Invalid URL", 
                               "The URL is invalid or not allowed.\n"
                               "Only HTTP/HTTPS URLs are supported.")
            return

        def download_thread():
            try:
                self.root.after(
                    0, lambda: self.stat.config(text=
                                                "Downloading M3U from URL..."))

                response = requests.get(url, timeout=15, 
                                       headers={'User-Agent': 'M3UMatrix/2.0'})
                response.raise_for_status()
                
                # SECURITY: Validate M3U format
                if not is_valid_m3u(response.text):
                    self.root.after(
                        0, lambda: messagebox.showerror(
                            "Invalid Format", 
                            "The downloaded file doesn't appear to be a valid M3U playlist."))
                    return

                temp_file = tempfile.NamedTemporaryFile(mode='w',
                                                        suffix='.m3u',
                                                        delete=False,
                                                        encoding='utf-8')
                temp_file.write(response.text)
                temp_file.close()

                self.root.after(
                    0,
                    lambda: self.process_downloaded_m3u(temp_file.name, url))

            except Exception as e:
                self.root.after(
                    0, lambda: messagebox.showerror(
                        "Download Error", f"Failed to download M3U: {str(e)}"))
                self.root.after(
                    0, lambda: self.stat.config(text="Download failed"))

        threading.Thread(target=download_thread, daemon=True).start()

    def process_downloaded_m3u(self, temp_path, url):
        """Process the downloaded M3U file"""
        try:
            channels = self.parse_m3u_file(temp_path)

            for channel in channels:
                channel['source'] = f"URL: {url}"
                channel.setdefault("num", 0)
                channel.setdefault("backups", [])

            self.channels.extend(channels)
            self.files.append(f"[URL] {url}")
            self.file_list.insert(tk.END, f"[URL] {os.path.basename(url)}")

            self.fill()
            self.organize_channels()
            self.build_m3u()
            self.stat.config(
                text=f"IMPORTED: {len(channels)} channels from URL")

            os.unlink(temp_path)

        except Exception as e:
            messagebox.showerror("Parse Error",
                                 f"Failed to parse downloaded M3U: {str(e)}")

    # ========== ENHANCED EPG FETCHER ==========
    def fetch_epg(self):
        """Fetch EPG data from online sources with XML parsing"""
        epg_url = simpledialog.askstring(
            "Fetch EPG", "Enter EPG XML URL (leave empty for default):")

        if epg_url is None:
            return

        if not epg_url:
            epg_url = "http://example.com/epg.xml"
            messagebox.showinfo(
                "EPG Source",
                f"Using placeholder EPG source. Replace with actual EPG URL.\n\n{epg_url}"
            )
            return

        def fetch_thread():
            try:
                self.root.after(
                    0, lambda: self.stat.config(text="Fetching EPG data..."))

                response = requests.get(epg_url, timeout=15)
                response.raise_for_status()

                self.root.after(
                    0, lambda: self.process_epg_data_enhanced(
                        response.text, epg_url))

            except Exception as e:
                self.root.after(
                    0, lambda: messagebox.showerror(
                        "EPG Error", f"Failed to fetch EPG: {str(e)}"))
                self.root.after(
                    0, lambda: self.stat.config(text="EPG fetch failed"))

        threading.Thread(target=fetch_thread, daemon=True).start()

    def process_epg_data_enhanced(self, epg_xml, source_url):
        """Enhanced EPG parsing with proper XML handling"""
        try:
            import xml.etree.ElementTree as ET

            # Clean XML
            epg_xml = self.clean_epg_xml(epg_xml)
            root = ET.fromstring(epg_xml)

            shows = []
            channel_mapping = {}

            # Map channel IDs to names
            for channel in root.findall('.//channel'):
                channel_id = channel.get('id')
                if channel_id:
                    display_name = channel.find('display-name')
                    if display_name is not None and display_name.text:
                        channel_mapping[channel_id] = display_name.text

            # Parse programmes
            for programme in root.findall('.//programme'):
                try:
                    channel_id = programme.get('channel')
                    start = programme.get('start')
                    title_elem = programme.find('title')

                    if channel_id and title_elem is not None and title_elem.text:
                        start_time = self.parse_epg_time(start)

                        stop = programme.get('stop')
                        end_time = self.parse_epg_time(stop) if stop else None

                        desc_elem = programme.find('desc')
                        description = desc_elem.text if desc_elem is not None else ""

                        shows.append({
                            'channel_id':
                            channel_id,
                            'channel_name':
                            channel_mapping.get(channel_id, channel_id),
                            'title':
                            title_elem.text,
                            'description':
                            description,
                            'start':
                            start_time,
                            'end':
                            end_time
                        })
                except Exception:
                    continue

            # Update schedule
            self.update_schedule_from_epg(shows)
            self.update_guide_preview()

            self.epg_data = {
                'source': source_url,
                'fetch_time': datetime.now().isoformat(),
                'shows': shows,
                'total_programs': len(shows)
            }

            messagebox.showinfo(
                "EPG Success", f"Loaded EPG data with:\n"
                f"• {len(shows)} program entries\n"
                f"• Source: {source_url}")

            self.stat.config(text=f"EPG: {len(shows)} shows loaded")

        except Exception as e:
            messagebox.showerror(
                "EPG Parse Error", f"Failed to parse EPG data:\n{str(e)}\n\n"
                f"Ensure the URL points to a valid XMLTV format file.")

    def clean_epg_xml(self, xml_content):
        """Clean common XML issues in EPG files with proper escaping"""
        # Remove invalid XML characters (keep valid Unicode ranges)
        xml_content = re.sub(
            r'[^\x09\x0A\x0D\x20-\x7E\x85\xA0-\uD7FF\uE000-\uFFFD]', '',
            xml_content)
        
        # Fix ampersands properly - protect existing entities first
        entities = ['&amp;', '&lt;', '&gt;', '&quot;', '&apos;', '&#']
        placeholders = {}
        
        # Protect XML entities and numeric character references
        for i, entity in enumerate(entities):
            placeholder = f'__PROTECT_{i}__'
            placeholders[placeholder] = entity
            xml_content = xml_content.replace(entity, placeholder)
        
        # Now escape bare ampersands
        xml_content = xml_content.replace('&', '&amp;')
        
        # Restore protected entities
        for placeholder, entity in placeholders.items():
            xml_content = xml_content.replace(placeholder, entity)
        
        return xml_content

    def parse_epg_time(self, time_str):
        """Parse EPG time format (YYYYMMDDHHMMSS +0000)"""
        try:
            if len(time_str) >= 14:
                dt_str = time_str[:14]
                return datetime.strptime(dt_str, '%Y%m%d%H%M%S')
        except:
            pass
        return datetime.now()

    def update_schedule_from_epg(self, shows):
        """Update channel schedule from EPG data"""
        for channel_num in list(self.schedule.keys()):
            self.schedule[channel_num] = [
                s for s in self.schedule[channel_num]
                if s.get('source') != 'EPG'
            ]

        for show in shows:
            matching_channels = []
            for channel in self.channels:
                if (show['channel_id'] == channel.get('tvg_id')
                        or show['channel_name'].lower() in channel.get(
                            'name', '').lower()):
                    matching_channels.append(channel)

            for channel in matching_channels:
                channel_num = str(channel['num'])
                if channel_num not in self.schedule:
                    self.schedule[channel_num] = []

                self.schedule[channel_num].append({
                    'time':
                    show['start'].strftime('%H:%M'),
                    'show':
                    show['title'],
                    'description':
                    show['description'],
                    'source':
                    'EPG',
                    'end':
                    show['end'].strftime('%H:%M') if show['end'] else None
                })

    # ========== ENHANCED UI FEATURES ==========
    def filter_debounced(self):
        """Debounced search - delays filter execution by 300ms"""
        # Cancel previous debounce timer if it exists
        if self.search_debounce_id:
            self.root.after_cancel(self.search_debounce_id)
        
        # Set new timer - filter will run 300ms after last keystroke
        self.search_debounce_id = self.root.after(300, self.filter)
    
    def filter(self):
        """Advanced filtering with regex support and caching"""
        search_term = self.search.get().lower()

        if not search_term:
            self.fill()
            self.filter_cache.clear()  # Clear cache when showing all
            return
        
        # PERFORMANCE: Check cache first
        cache_key = search_term
        if cache_key in self.filter_cache:
            matching_channels = self.filter_cache[cache_key]
        else:
            # SECURITY: Sanitize search input
            search_term = sanitize_input(search_term, max_length=200).lower()

            use_regex = False
            if search_term.startswith('/') and search_term.endswith('/'):
                use_regex = True
                pattern = search_term[1:-1]
                try:
                    re.compile(pattern)
                except re.error:
                    use_regex = False
                    messagebox.showwarning("Invalid Regex", 
                                         "Invalid regular expression. Using plain text search.")

            # Filter channels
            matching_channels = []
            for ch in self.channels:
                name = ch.get("name", "").lower()
                group = ch.get("group", "").lower()
                url = ch.get("url", "").lower()

                match = False
                if use_regex:
                    try:
                        match = (re.search(pattern, name, re.IGNORECASE)
                                or re.search(pattern, group, re.IGNORECASE)
                                or re.search(pattern, url, re.IGNORECASE))
                    except re.error:
                        match = False
                else:
                    match = (search_term in name or search_term in group
                            or search_term in url)

                if match:
                    matching_channels.append(ch)
            
            # Cache results (limit cache size)
            if len(self.filter_cache) < 50:
                self.filter_cache[cache_key] = matching_channels

        # Update UI only with matching channels
        self.tv.delete(*self.tv.get_children())
        self.uuid_to_iid_map.clear()  # Clear and rebuild mapping for filtered view
        
        for ch in matching_channels:
            now = "LIVE"
            shows = sorted(self.schedule.get(str(ch["num"]), []),
                           key=lambda x: x["time"],
                           reverse=True)
            for s in shows:
                if s["time"] <= datetime.now().strftime("%H:%M"):
                    now = s["show"]
                    break

            tags_count = len(ch.get('custom_tags', {}))

            iid = self.tv.insert(
                "",
                "end",
                values=(ch["num"], now, "—", ch.get("group", "Other"),
                        ch.get("name",
                               ""), ch.get("url", "")[:80] + "..." if
                        len(ch.get("url", "")) > 80 else ch.get("url", ""),
                        len(ch.get("backups",
                                   [])), f"{tags_count} tags", ""))
            
            # Map UUID to IID for O(1) lookups during audits
            if "uuid" in ch:
                self.uuid_to_iid_map[ch["uuid"]] = iid

    def sort_by(self, col):
        """Enhanced multi-column sorting"""
        if not hasattr(self, '_sort_state'):
            self._sort_state = {}

        reverse = self._sort_state.get(col, False)
        self._sort_state[col] = not reverse

        sort_keys = {
            "#": lambda x: x["num"],
            "Group": lambda x: x.get("group", "").lower(),
            "Name": lambda x: x.get("name", "").lower(),
            "URL": lambda x: x.get("url", "").lower(),
            "Backs": lambda x: len(x.get("backups", [])),
            "Tags": lambda x: len(x.get("custom_tags", {}))
        }

        if col in sort_keys:
            self.channels.sort(key=sort_keys[col], reverse=reverse)

        self.fill()
        self.stat.config(text=f"Sorted by {col} {'↓' if reverse else '↑'}")

    # ========== EXISTING CORE METHODS ==========
    def fill(self):
        """Update the treeview with current channels and build UUID->IID mapping"""
        self.tv.delete(*self.tv.get_children())
        self.uuid_to_iid_map.clear()  # Clear old mapping
        
        for ch in self.channels:
            now_playing = "LIVE"
            shows = sorted(self.schedule.get(str(ch["num"]), []),
                           key=lambda x: x["time"],
                           reverse=True)
            for s in shows:
                if s["time"] <= datetime.now().strftime("%H:%M"):
                    now_playing = s["show"]
                    break

            next_show = "—"
            tags_count = len(ch.get('custom_tags', {}))

            iid = self.tv.insert(
                "",
                "end",
                values=(ch["num"], now_playing, next_show,
                        ch.get("group", "Other"), ch.get("name", "Unknown"),
                        ch.get("url", "")[:80] + "..." if len(ch.get(
                            "url", "")) > 80 else ch.get("url", ""),
                        len(ch.get("backups", [])), f"{tags_count} tags", ""))
            
            # Map UUID to IID for O(1) lookups during audits
            if "uuid" in ch:
                self.uuid_to_iid_map[ch["uuid"]] = iid

    def build_m3u(self):
        """Build M3U content with enhanced tags"""
        self.m3u = "#EXTM3U\n"
        for ch in self.channels:
            extinf = f'#EXTINF:-1 tvg-id="{ch.get("tvg_id", "")}" tvg-name="{ch.get("name", "")}" '
            extinf += f'tvg-logo="{ch.get("logo", "")}" group-title="{ch.get("group", "Other")}",{ch.get("name", "")}\n'

            if ch.get("group"):
                extinf += f'#EXTGRP:{ch.get("group", "Other")}\n'

            for tag_name, tag_value in ch.get('custom_tags', {}).items():
                extinf += f'#{tag_name}:{tag_value}\n'

            self.m3u += extinf + ch.get("url", "") + "\n"

            for backup in ch.get("backups", []):
                self.m3u += backup + "\n"

    def drag_start(self, e):
        iid = self.tv.identify_row(e.y)
        if iid and self.tv.identify_column(e.x) != "#9":
            self.drag_data["iid"] = iid
            self.drag_data["y"] = e.y

    def drag_motion(self, e):
        if not self.drag_data["iid"]: return
        iid = self.tv.identify_row(e.y)
        if iid and iid != self.drag_data["iid"]:
            self.tv.move(self.drag_data["iid"], "", self.tv.index(iid))

    def drag_stop(self, e):
        if not self.drag_data["iid"]: return
        self.reorder_channels()
        self.drag_data = {"iid": None, "y": 0}
        self.stat.config(text="DRAG SORT APPLIED")

    def reorder_channels(self):
        new_order = []
        for iid in self.tv.get_children():
            num = int(self.tv.item(iid, "values")[0])
            ch = next(c for c in self.channels if c["num"] == num)
            new_order.append(ch)
        for i, ch in enumerate(new_order, 1):
            ch["num"] = i
        self.channels = new_order
        self.fill()
        self.build_m3u()

    def load(self):
        f = filedialog.askopenfilenames(
            filetypes=[
                ("M3U Files", "*.m3u *.m3u8"),
                ("All Files", "*.*")
            ]
        )
        if not f:
            return
        
        # Update file list immediately
        self.files.extend(f)
        self.file_list.delete(0, tk.END)
        for ff in self.files:
            self.file_list.insert(tk.END, os.path.basename(ff))
        
        # Create progress window
        progress_win = tk.Toplevel(self.root)
        progress_win.title("Loading Files")
        progress_win.geometry("500x200")
        progress_win.configure(bg="#1a1a2e")
        progress_win.transient(self.root)
        progress_win.grab_set()
        
        tk.Label(
            progress_win,
            text="📂 Loading Playlist Files",
            font=("Arial", 16, "bold"),
            fg="#00ff88",
            bg="#1a1a2e"
        ).pack(pady=20)
        
        status_label = tk.Label(
            progress_win,
            text="Reading files...",
            font=("Arial", 12),
            fg="#ffffff",
            bg="#1a1a2e"
        )
        status_label.pack(pady=10)
        
        progress = ttk.Progressbar(
            progress_win,
            length=400,
            mode='determinate'
        )
        progress.pack(pady=20)
        
        # Force window to show
        progress_win.update()
        
        # Parse files with progress updates
        all_channels = []
        total_files = len(f)
        
        for idx, file_path in enumerate(f, 1):
            status_label.config(text=f"Reading file {idx}/{total_files}: {os.path.basename(file_path)}")
            progress['value'] = (idx / total_files) * 50  # First 50% for parsing
            progress_win.update()
            
            try:
                # Check if this is a media file or M3U playlist
                if self.is_media_file(file_path):
                    # Create channel directly from media file
                    channel = self.create_channel_from_media_file(file_path)
                    channel.setdefault("num", 0)
                    channel.setdefault("backups", [])
                    channel["uuid"] = str(uuid.uuid4())
                    all_channels.append(channel)
                    self.logger.info(f"Created channel from media file: {os.path.basename(file_path)}")
                else:
                    # Parse as M3U playlist
                    channels = self.parse_m3u_file(file_path)
                    for ch in channels:
                        ch.setdefault("num", 0)
                        ch.setdefault("backups", [])
                        # Add unique UUID if not present
                        if "uuid" not in ch:
                            ch["uuid"] = str(uuid.uuid4())
                    all_channels.extend(channels)
                    self.logger.info(f"Parsed {len(channels)} channels from M3U: {os.path.basename(file_path)}")
            except Exception as e:
                self.logger.error(f"Failed to process {file_path}: {e}")
                status_label.config(text=f"Error reading {os.path.basename(file_path)}")
                progress_win.update()
                continue
        
        # Check if we got any channels
        if not all_channels:
            progress_win.destroy()
            messagebox.showwarning(
                "No Content Found",
                "No channels or media files were found in the selected files.\n\n"
                "Supported file types:\n"
                "• M3U Playlists (.m3u, .m3u8)\n"
                "• Video Files (.mp4, .mkv, .avi, .mov, .wmv, etc.)\n"
                "• Audio Files (.mp3, .aac, .wav, .flac, .ogg, etc.)\n\n"
                "If you selected a text file, make sure it contains valid M3U format."
            )
            return
        
        # Validate large imports
        if len(all_channels) > 1000:
            progress_win.destroy()
            response = messagebox.askyesno(
                "Large Import Detected",
                f"You're importing {len(all_channels)} channels.\n\n"
                f"This may slow down the interface.\n"
                f"Continue?")
            if not response:
                return
            
            # Recreate progress window
            progress_win = tk.Toplevel(self.root)
            progress_win.title("Loading Channels")
            progress_win.geometry("500x200")
            progress_win.configure(bg="#1a1a2e")
            progress_win.transient(self.root)
            progress_win.grab_set()
            
            tk.Label(
                progress_win,
                text="📺 Loading Channels",
                font=("Arial", 16, "bold"),
                fg="#00ff88",
                bg="#1a1a2e"
            ).pack(pady=20)
            
            status_label = tk.Label(
                progress_win,
                text=f"Processing {len(all_channels)} channels...",
                font=("Arial", 12),
                fg="#ffffff",
                bg="#1a1a2e"
            )
            status_label.pack(pady=10)
            
            progress = ttk.Progressbar(
                progress_win,
                length=400,
                mode='determinate'
            )
            progress.pack(pady=20)
            progress_win.update()
        
        # Update status
        status_label.config(text="Processing channels...")
        progress['value'] = 60
        progress_win.update()
        
        # Set channels
        self.channels = all_channels
        
        # Auto-increment
        status_label.config(text="Numbering channels...")
        progress['value'] = 70
        progress_win.update()
        self.auto_increment_channels()
        
        # Fill treeview with batching for large lists
        status_label.config(text="Updating display...")
        progress['value'] = 80
        progress_win.update()
        
        self.tv.delete(*self.tv.get_children())
        self.uuid_to_iid_map.clear()  # Clear and rebuild mapping for loaded channels
        
        # Batch insert for better performance
        batch_size = 100
        total_channels = len(self.channels)
        
        for i in range(0, total_channels, batch_size):
            batch = self.channels[i:i + batch_size]
            
            for ch in batch:
                now_playing = "LIVE"
                shows = sorted(self.schedule.get(str(ch["num"]), []),
                              key=lambda x: x["time"],
                              reverse=True)
                for s in shows:
                    if s["time"] <= datetime.now().strftime("%H:%M"):
                        now_playing = s["show"]
                        break
                
                next_show = "—"
                tags_count = len(ch.get('custom_tags', {}))
                
                iid = self.tv.insert(
                    "",
                    "end",
                    values=(ch["num"], now_playing, next_show,
                           ch.get("group", "Other"), ch.get("name", "Unknown"),
                           ch.get("url", "")[:80] + "..." if len(ch.get(
                               "url", "")) > 80 else ch.get("url", ""),
                           len(ch.get("backups", [])), f"{tags_count} tags", ""))
                
                # Map UUID to IID for O(1) lookups during audits
                if "uuid" in ch:
                    self.uuid_to_iid_map[ch["uuid"]] = iid
            
            # Update progress
            progress_val = 80 + ((i + batch_size) / total_channels) * 15
            progress['value'] = min(progress_val, 95)
            status_label.config(text=f"Loading... {min(i + batch_size, total_channels)}/{total_channels} channels")
            progress_win.update_idletasks()
        
        # Build M3U
        status_label.config(text="Building M3U output...")
        progress['value'] = 97
        progress_win.update()
        self.build_m3u()
        
        # Mark changed
        self.mark_changed()
        
        # Final update
        progress['value'] = 100
        status_label.config(text="✅ Complete!")
        progress_win.update()
        
        # Close progress window
        progress_win.after(500, progress_win.destroy)
        
        # Update status bar
        self.stat.config(
            text=f"✅ LOADED {len(self.channels)} channels from {len(f)} files"
        )

    def save(self):
        folder = filedialog.askdirectory()

        if folder:
            path = os.path.join(
                folder,
                f"MATRIX_{datetime.now().strftime('%Y%m%d')}_{len(self.channels)}.m3u"
            )
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.m3u)
            self.mark_clean()  # Clear unsaved changes flag
            messagebox.showinfo(
                "Saved", f"Playlist saved with {len(self.channels)} channels")
            self.stat.config(text=f"SAVED: {path}")

    def overlay(self):
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>M3U Matrix Player</title>
    <style>
        body { margin: 0; padding: 0; background: #000; color: white; font-family: Arial; }
        #player { width: 100vw; height: 100vh; background: #111; }
    </style>
</head>
<body>
    <div id="player">
        <h1>M3U Matrix Golden Player</h1>
        <p>Advanced IPTV player loaded successfully!</p>
    </div>
</body>
</html>
"""
        temp_path = os.path.join(tempfile.gettempdir(),
                                 "M3U_MATRIX_PLAYER.html")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create player: {str(e)}")
            return

        webbrowser.open(temp_path)

    def new_project(self):
        if messagebox.askyesno("REBOOT", "Wipe the Matrix?"):
            self.files = []
            self.channels = []
            self.m3u = ""
            self.file_list.delete(0, tk.END)
            self.tv.delete(*self.tv.get_children())
            self.stat.config(text="MATRIX RESET")

    def on_double(self, e):
        col = self.tv.identify_column(e.x)
        iid = self.tv.identify_row(e.y)
        if not iid: return

        if col == "#6":
            url = self.tv.item(iid, "values")[5]
            if url and not url.endswith("..."):
                self.vlc(url)
        elif col in ("#1", "#2", "#3", "#4", "#5"):
            self.inline_edit(iid, int(col[1:]) - 1)

    def inline_edit(self, iid, col_idx):
        if self.editor: self.editor.destroy()
        x, y, w, h = self.tv.bbox(iid, f"#{col_idx+1}")
        self.editor = tk.Entry(self.tv,
                               bg="#333",
                               fg="#fff",
                               font=("Arial", 10),
                               relief=tk.FLAT,
                               highlightthickness=2,
                               highlightcolor="#8e44ad")
        self.editor.insert(0, self.tv.item(iid, "values")[col_idx])
        self.editor.select_range(0, tk.END)
        self.editor.focus()
        self.editor.place(x=x, y=y + 2, width=w - 4, height=h - 4)
        self.editor.bind("<Return>", lambda e: self.save_inline(iid, col_idx))
        self.editor.bind("<FocusOut>", lambda e: self.editor.destroy())

    def save_inline(self, iid, col_idx):
        val = self.editor.get().strip()
        values = list(self.tv.item(iid, "values"))
        values[col_idx] = val
        self.tv.item(iid, values=values)
        num = int(values[0])
        ch = next(c for c in self.channels if c["num"] == num)

        mapping = {1: "now", 2: "next", 3: "group", 4: "name"}
        if col_idx in mapping:
            key = mapping[col_idx]
            if key in ("now", "next"):
                time = datetime.now().strftime("%H:%M")
                show = val
                num_str = str(num)
                if num_str not in self.schedule:
                    self.schedule[num_str] = []
                self.schedule[num_str].append({"time": time, "show": show})
            elif key == "group":
                ch["group"] = val
            elif key == "name":
                ch["name"] = val

        self.editor.destroy()
        self.editor = None
        self.build_m3u()
        self.update_guide_preview()

    def vlc(self, url):
        if os.name == 'nt':
            try:
                os.startfile(url)
            except Exception:
                messagebox.showwarning(
                    "VLC Error",
                    "Could not open stream. Ensure VLC is installed.")
        else:
            webbrowser.open(url)
    
    def launch_redis_services(self):
        """Launch Redis server, API, and Dashboard with output window"""
        redis_dir = Path("redis")
        
        if not redis_dir.exists():
            messagebox.showwarning(
                "Redis Not Found",
                "Redis folder not found!\n\n"
                "Make sure the 'redis' folder exists with:\n"
                "• START_ALL_SERVICES.bat\n"
                "• api_server.py\n"
                "• dashboard.py"
            )
            return
        
        bat_file = redis_dir / "START_ALL_SERVICES.bat"
        
        if not bat_file.exists():
            messagebox.showwarning(
                "Startup Script Not Found",
                "START_ALL_SERVICES.bat not found in redis folder!\n\n"
                "Please ensure the Redis integration is properly installed."
            )
            return
        
        # Create output window
        output_win = tk.Toplevel(self.root)
        output_win.title("Redis Services Output")
        output_win.geometry("900x600")
        output_win.configure(bg="#1a1a2e")
        
        # Header
        header = tk.Frame(output_win, bg="#667eea", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🚀 Redis Services Launcher",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#667eea"
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        # Back to Index button
        tk.Button(
            header,
            text="← Back to Index",
            command=lambda: self.show_redis_index(output_win),
            bg="#764ba2",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8
        ).pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Status
        status_frame = tk.Frame(output_win, bg="#1a1a2e")
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        status_label = tk.Label(
            status_frame,
            text="✅ Redis services are starting...",
            font=("Arial", 12),
            fg="#00ff88",
            bg="#1a1a2e"
        )
        status_label.pack(pady=5)
        
        # Output text area
        text_frame = tk.Frame(output_win, bg="#1a1a2e")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        output_text = tk.Text(
            text_frame,
            bg="#2e2e2e",
            fg="#00ff88",
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame, command=output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        output_text.config(yscrollcommand=scrollbar.set)
        
        # Quick links
        links_frame = tk.Frame(output_win, bg="#1a1a2e")
        links_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            links_frame,
            text="🔗 Quick Access:",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#1a1a2e"
        ).pack(side=tk.LEFT, padx=10)
        
        def open_url(url):
            webbrowser.open(url)
        
        tk.Button(
            links_frame,
            text="📊 Dashboard (port 8080)",
            command=lambda: open_url("http://localhost:8080"),
            bg="#3498db",
            fg="white",
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            links_frame,
            text="📡 API Docs (port 3000)",
            command=lambda: open_url("http://localhost:3000/docs"),
            bg="#2ecc71",
            fg="white",
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=5)
        
        # Launch services
        try:
            output_text.insert(tk.END, "="*80 + "\n")
            output_text.insert(tk.END, "🚀 LAUNCHING REDIS SERVICES\n")
            output_text.insert(tk.END, "="*80 + "\n\n")
            output_text.insert(tk.END, f"📂 Working directory: {redis_dir.absolute()}\n")
            output_text.insert(tk.END, f"📜 Running: {bat_file.name}\n\n")
            output_text.insert(tk.END, "Starting services:\n")
            output_text.insert(tk.END, "  • Redis Server (port 6379)\n")
            output_text.insert(tk.END, "  • FastAPI Backend (port 3000)\n")
            output_text.insert(tk.END, "  • Web Dashboard (port 8080)\n\n")
            output_text.insert(tk.END, "-"*80 + "\n\n")
            
            if os.name == 'nt':
                # Windows: Launch in new command window
                subprocess.Popen(
                    ['cmd', '/c', 'start', 'cmd', '/k', str(bat_file)],
                    cwd=str(redis_dir)
                )
                output_text.insert(tk.END, "✅ Services launched in new window!\n\n")
                output_text.insert(tk.END, "📝 Check the command window for live output\n\n")
            else:
                # Linux/Mac: Launch in background
                process = subprocess.Popen(
                    [str(bat_file)],
                    cwd=str(redis_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                output_text.insert(tk.END, "✅ Services launched in background!\n\n")
            
            output_text.insert(tk.END, "-"*80 + "\n\n")
            output_text.insert(tk.END, "🎉 Services should now be running!\n\n")
            output_text.insert(tk.END, "Access points:\n")
            output_text.insert(tk.END, "  📊 Dashboard: http://localhost:8080\n")
            output_text.insert(tk.END, "  📡 API: http://localhost:3000\n")
            output_text.insert(tk.END, "  📚 API Docs: http://localhost:3000/docs\n\n")
            output_text.insert(tk.END, "💡 Use 'EXPORT REDIS' button to send channels to cache\n")
            
            status_label.config(text="✅ Redis services launched successfully!")
            
        except Exception as e:
            output_text.insert(tk.END, f"\n❌ ERROR: {str(e)}\n")
            status_label.config(text="❌ Failed to launch services", fg="#ff4444")
            self.logger.error(f"Failed to launch Redis services: {e}")
    
    def show_redis_index(self, current_window):
        """Show Redis integration index page"""
        current_window.destroy()
        
        # Create index window
        index_win = tk.Toplevel(self.root)
        index_win.title("Redis Integration - Index")
        index_win.geometry("800x700")
        index_win.configure(bg="#1a1a2e")
        
        # Header
        header = tk.Frame(index_win, bg="#667eea", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📡 M3U Matrix - Redis Integration",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="#667eea"
        ).pack(pady=20)
        
        # Content
        content = tk.Frame(index_win, bg="#1a1a2e")
        content.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Welcome message
        tk.Label(
            content,
            text="Welcome to Redis Integration",
            font=("Arial", 18, "bold"),
            fg="#00ff88",
            bg="#1a1a2e"
        ).pack(pady=(0, 20))
        
        # Info text
        info_text = """
Redis provides fast caching for your M3U channels, making
NEXUS TV and other applications load instantly!

Services included:
  • Redis Server - In-memory cache (port 6379)
  • FastAPI Backend - REST API (port 3000)
  • Web Dashboard - Browse channels (port 8080)
"""
        
        tk.Label(
            content,
            text=info_text,
            font=("Arial", 11),
            fg="white",
            bg="#1a1a2e",
            justify=tk.LEFT
        ).pack(pady=(0, 30))
        
        # Buttons
        btn_frame = tk.Frame(content, bg="#1a1a2e")
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="🚀 Launch Redis Services",
            command=lambda: [index_win.destroy(), self.launch_redis_services()],
            bg="#2ecc71",
            fg="white",
            font=("Arial", 14, "bold"),
            width=25,
            height=2
        ).pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="📊 Open Dashboard",
            command=lambda: webbrowser.open("http://localhost:8080"),
            bg="#3498db",
            fg="white",
            font=("Arial", 12),
            width=25,
            height=2
        ).pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="📚 View API Documentation",
            command=lambda: webbrowser.open("http://localhost:3000/docs"),
            bg="#9b59b6",
            fg="white",
            font=("Arial", 12),
            width=25,
            height=2
        ).pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="❌ Close",
            command=index_win.destroy,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11),
            width=25
        ).pack(pady=20)

    def row_menu(self, e):
        iid = self.tv.identify_row(e.y)
        if not iid: return
        self.tv.selection_set(iid)
        menu = tk.Menu(self.root, tearoff=0, bg="#333", fg="#fff")
        menu.add_command(
            label="Play in VLC",
            command=lambda: self.vlc(self.tv.item(iid, "values")[5]))
        menu.add_command(label="Copy URL",
                         command=lambda: self.root.clipboard_append(
                             self.tv.item(iid, "values")[5]))
        menu.add_command(label="Schedule Show",
                         command=lambda: self.schedule_show(iid))
        menu.add_separator()
        menu.add_command(label="Delete",
                         command=lambda: self.delete_channel(iid))
        menu.post(e.x_root, e.y_root)

    def delete_channel(self, iid):
        values = self.tv.item(iid, "values")
        num = int(values[0])
        
        self.save_state(f"Delete channel #{num}")
        self.mark_changed()
        
        self.channels = [ch for ch in self.channels if ch["num"] != num]
        self.auto_increment_channels()
        self.fill()
        self.build_m3u()
        self.stat.config(text=f"Deleted channel {num}")

    def schedule_show(self, iid):
        num = self.tv.item(iid, "values")[0]
        win = tk.Toplevel(self.root)
        win.title("Schedule Show")
        tk.Label(win, text="Time (HH:MM):").pack()
        t = tk.Entry(win)
        t.pack()
        t.insert(0, datetime.now().strftime("%H:%M"))
        tk.Label(win, text="Show Name:").pack()
        s = tk.Entry(win)
        s.pack()

        def ok():
            num_str = str(num)
            if num_str not in self.schedule: self.schedule[num_str] = []
            self.schedule[num_str].append({"time": t.get(), "show": s.get()})
            self.update_guide_preview()
            self.fill()
            win.destroy()

        tk.Button(win, text="Schedule", command=ok).pack(pady=10)

    def drop_files(self, event):
        """Handle drag and drop of M3U files"""
        files = self.root.tk.splitlist(event.data)
        m3u_files = [
            f.strip('{}') for f in files
            if f.lower().endswith(('.m3u', '.m3u8'))
        ]

        if not m3u_files:
            messagebox.showwarning("Invalid Files",
                                   "Please drop M3U or M3U8 files only!")
            return

        # Add to file list (avoid duplicates)
        for file_path in m3u_files:
            if file_path not in self.files:
                self.files.append(file_path)

        # Refresh file list display
        self.file_list.delete(0, tk.END)
        for ff in self.files:
            self.file_list.insert(tk.END, os.path.basename(ff))

        # Auto-load the dropped files in a thread
        def load_dropped():
            all_channels = []
            for file_path in m3u_files:
                channels = self.parse_m3u_file(file_path)
                for ch in channels:
                    ch.setdefault("num", 0)
                    ch.setdefault("backups", [])
                all_channels.extend(channels)

            self.channels.extend(all_channels)
            self.auto_increment_channels()
            self.root.after(0, self.fill)
            self.root.after(0, self.build_m3u)
            self.root.after(
                0, lambda: self.stat.config(
                    text=
                    f"Loaded {len(m3u_files)} file(s), {len(all_channels)} channels!"
                ))

        threading.Thread(target=load_dropped, daemon=True).start()
        self.stat.config(text=f"Loading {len(m3u_files)} M3U file(s)...")

    def open_file_from_list(self, event=None):
        """Open selected file by double-clicking"""
        selection = self.file_list.curselection()
        if not selection:
            return

        index = selection[0]
        file_path = self.files[index]

        # Clear current channels and reload just this file
        def load_single():
            self.channels = []
            channels = self.parse_m3u_file(file_path)
            for ch in channels:
                ch.setdefault("num", 0)
                ch.setdefault("backups", [])
            self.channels = channels
            self.auto_increment_channels()
            self.root.after(0, self.fill)
            self.root.after(0, self.build_m3u)
            self.root.after(
                0, lambda: self.stat.config(
                    text=
                    f"Opened: {os.path.basename(file_path)} - {len(channels)} channels"
                ))

        threading.Thread(target=load_single, daemon=True).start()
        self.stat.config(text=f"Opening {os.path.basename(file_path)}...")

    def file_menu(self, e):
        selection = self.file_list.curselection()
        menu = tk.Menu(self.root, tearoff=0, bg="#333", fg="#fff")
        menu.add_command(label="✅ Open File (Double-Click)",
                         command=self.open_file_from_list)
        menu.add_separator()
        menu.add_command(label="📋 Copy File Path", command=self.copy_file_path)
        menu.add_command(label="📁 Open in Explorer",
                         command=self.open_file_location)
        menu.add_separator()
        menu.add_command(label="❌ Remove File", command=self.remove_file)
        menu.post(e.x_root, e.y_root)

    def copy_file_path(self):
        """Copy selected file path to clipboard"""
        selection = self.file_list.curselection()
        if selection:
            file_path = self.files[selection[0]]
            self.root.clipboard_clear()
            self.root.clipboard_append(file_path)
            self.stat.config(text=f"Copied: {file_path}")

    def open_file_location(self):
        """Open file location in file explorer"""
        selection = self.file_list.curselection()
        if selection:
            file_path = self.files[selection[0]]
            folder = os.path.dirname(os.path.abspath(file_path))
            try:
                if sys.platform == 'win32':
                    os.startfile(folder)
                elif sys.platform == 'darwin':
                    os.system(f'open "{folder}"')
                else:
                    os.system(f'xdg-open "{folder}"')
                self.stat.config(text=f"Opened folder: {folder}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder: {e}")

    def remove_file(self):
        selection = self.file_list.curselection()
        if selection:
            index = selection[0]
            self.files.pop(index)
            self.file_list.delete(index)
            self.stat.config(text="File removed")

    def load_tv_guide(self):
        try:
            with open("tv_guide.json", "r", encoding="utf-8") as f:
                self.schedule = json.load(f)
            self.stat.config(text="Custom schedule loaded.")
        except FileNotFoundError:
            self.schedule = {}
        except json.JSONDecodeError:
            messagebox.showwarning(
                "File Error",
                "tv_guide.json is malformed. Resetting schedule.")
            self.schedule = {}
        except Exception as e:
            self.stat.config(text=f"Error loading schedule: {e}")
        self.update_guide_preview()

    def update_guide_preview(self):
        now = datetime.now().strftime("%H:%M")
        preview = ""
        for ch in self.channels[:5]:
            num = ch["num"]
            shows = self.schedule.get(str(num), [])
            shows.sort(key=lambda s: s["time"])

            current = "No show"
            for s in shows:
                if s["time"] <= now:
                    current = s["show"]

            preview += f"{num:3} │ {current[:25]:25} │ {ch.get('name', 'Unknown')[:20]}\n"

        self.guide_prev.config(state=tk.NORMAL)
        self.guide_prev.delete(1.0, tk.END)
        self.guide_prev.insert(tk.END, preview or "No schedule loaded")
        self.guide_prev.config(state=tk.DISABLED)

    def open_guide(self):
        win = tk.Toplevel(self.root)
        win.title("TV GUIDE SCHEDULER")
        win.geometry("800x600")
        win.configure(bg="#1e1e1e")

        tk.Label(win,
                 text="Edit Schedule (JSON)",
                 fg="gold",
                 bg="#1e1e1e",
                 font=("Arial", 14)).pack(pady=10)
        text = tk.Text(win, bg="#111", fg="#0f0", font=("Courier", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, json.dumps(self.schedule, indent=2))

        def save():
            try:
                tv_guide_dir = Path("tv_guide")
                tv_guide_dir.mkdir(exist_ok=True)
                
                self.schedule = json.loads(text.get(1.0, tk.END))
                guide_file = tv_guide_dir / f"tv_guide_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(guide_file, "w") as f:
                    json.dump(self.schedule, f, indent=2)
                self.update_guide_preview()
                self.fill()
                messagebox.showinfo("Saved", f"TV Guide saved to:\n{guide_file}")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win,
                  text="SAVE GUIDE",
                  bg="#27ae60",
                  fg="white",
                  command=save).pack(pady=10)

    def generate_pages(self):
        """Generate NEXUS TV pages from current channels"""
        if not PAGE_GENERATOR_AVAILABLE:
            messagebox.showwarning("Feature Unavailable", 
                "Page generator not available.\n\n"
                "Download the full project from GitHub to use this feature.")
            return
            
        if not self.channels:
            messagebox.showwarning("No Channels", "Load channels first!")
            return

        # Template selection dialog
        template_dialog = tk.Toplevel(self.root)
        template_dialog.title("Choose Template")
        template_dialog.geometry("500x300")
        template_dialog.configure(bg="#1e1e1e")
        template_dialog.resizable(False, False)
        template_dialog.transient(self.root)
        template_dialog.grab_set()
        
        selected_template = tk.StringVar(value="nexus")
        
        tk.Label(
            template_dialog,
            text="Select Player Template",
            font=("Segoe UI", 16, "bold"),
            bg="#1e1e1e",
            fg="#00ff88"
        ).pack(pady=20)
        
        # NEXUS TV option
        nexus_frame = tk.Frame(template_dialog, bg="#2a2a2a", relief=tk.RAISED, bd=2)
        nexus_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Radiobutton(
            nexus_frame,
            text="NEXUS TV (24-Hour Scheduled Player)",
            variable=selected_template,
            value="nexus",
            font=("Segoe UI", 11),
            bg="#2a2a2a",
            fg="white",
            selectcolor="#0066cc",
            activebackground="#2a2a2a",
            activeforeground="white"
        ).pack(anchor=tk.W, padx=10, pady=10)
        
        tk.Label(
            nexus_frame,
            text="Cyberpunk-themed player with time-based scheduling",
            font=("Segoe UI", 9),
            bg="#2a2a2a",
            fg="#aaa"
        ).pack(anchor=tk.W, padx=30, pady=(0, 10))
        
        # Web IPTV option
        iptv_frame = tk.Frame(template_dialog, bg="#2a2a2a", relief=tk.RAISED, bd=2)
        iptv_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Radiobutton(
            iptv_frame,
            text="Web IPTV (Sequential Channel Player)",
            variable=selected_template,
            value="webiptv",
            font=("Segoe UI", 11),
            bg="#2a2a2a",
            fg="white",
            selectcolor="#0066cc",
            activebackground="#2a2a2a",
            activeforeground="white"
        ).pack(anchor=tk.W, padx=10, pady=10)
        
        tk.Label(
            iptv_frame,
            text="Modern IPTV player with channel list, favorites, and analysis",
            font=("Segoe UI", 9),
            bg="#2a2a2a",
            fg="#aaa"
        ).pack(anchor=tk.W, padx=30, pady=(0, 10))
        
        def on_template_selected():
            template_dialog.destroy()
            self._continue_generation(selected_template.get())
        
        tk.Button(
            template_dialog,
            text="CONTINUE",
            bg="#00ff88",
            fg="#000",
            font=("Segoe UI", 11, "bold"),
            command=on_template_selected,
            cursor="hand2"
        ).pack(pady=20)

    def _continue_generation(self, template_type):
        """Continue page generation with selected template"""
        # Ask how to generate pages
        choice = messagebox.askquestion(
            "Generate Pages",
            "Generate pages BY GROUP (Yes) or ALL IN ONE (No)?",
            icon='question')

        def generation_thread():
            try:
                template_name = "NEXUS TV" if template_type == "nexus" else "Web IPTV"
                self.root.after(
                    0, lambda: self.stat.config(
                        text=f"Generating {template_name} pages..."))
                
                # Initialize the correct generator
                if template_type == "nexus":
                    # Check for NEXUS TV template file
                    template_path = Path("../templates/nexus_tv_template.html")
                    if not template_path.exists():
                        template_path = Path("templates/nexus_tv_template.html")
                    if not template_path.exists():
                        self.root.after(0, lambda: messagebox.showerror(
                            "Template Not Found",
                            "NEXUS TV template file missing!\n\n"
                            "Download the full project from GitHub:\n"
                            "- templates/nexus_tv_template.html\n"
                            "- src/page_generator.py\n"
                            "- src/utils.py\n\n"
                            "Or use the SAVE button to export M3U files."))
                        self.root.after(0, lambda: self.stat.config(text="Template missing"))
                        return
                    generator = NexusTVPageGenerator(template_path=str(template_path))
                else:  # webiptv
                    # Check for Web IPTV template
                    template_path = Path("../templates/web-iptv-extension")
                    if not template_path.exists():
                        template_path = Path("templates/web-iptv-extension")
                    if not template_path.exists() or not (template_path / "player.html").exists():
                        self.root.after(0, lambda: messagebox.showerror(
                            "Template Not Found",
                            "Web IPTV template files missing!\n\n"
                            "Download the full project from GitHub:\n"
                            "- templates/web-iptv-extension/\n"
                            "- src/page_generator.py\n\n"
                            "Or use the SAVE button to export M3U files."))
                        self.root.after(0, lambda: self.stat.config(text="Template missing"))
                        return
                    generator = WebIPTVGenerator(template_path=str(template_path))
                
                generated = []

                if choice == 'yes':
                    # Group by category
                    groups = {}
                    for ch in self.channels:
                        group = ch.get('group', 'Other')
                        if group not in groups:
                            groups[group] = []
                        groups[group].append(ch)

                    # Generate page for each group
                    for group_name, group_channels in groups.items():
                        m3u_content = self.build_group_m3u(group_channels)
                        output_path = generator.generate_page(
                            m3u_content, group_name)
                        generated.append({
                            'name': group_name,
                            'file': output_path.name,
                            'programs': len(group_channels)
                        })
                        self.root.after(0,
                                        lambda g=group_name: self.stat.config(
                                            text=f"Generated: {g}"))
                else:
                    # All channels in one page
                    m3u_content = self.m3u
                    output_path = generator.generate_page(
                        m3u_content, "All Channels")
                    generated.append({
                        'name': 'All Channels',
                        'file': output_path.name,
                        'programs': len(self.channels)
                    })

                # Generate channel selector
                if template_type == "nexus":
                    selector_path = generator.generate_channel_selector(generated)
                else:  # webiptv
                    selector_path = generator.generate_selector_page(generated)

                # Show success message
                abs_selector = selector_path.absolute()
                abs_dir = Path('generated_pages').absolute()
                
                self.root.after(
                    0, lambda: messagebox.showinfo(
                        "✅ Pages Generated Successfully!",
                        f"Generated {len(generated)} channel pages\n\n"
                        f"📁 Location:\n{abs_dir}\n\n"
                        f"🌐 HOW TO VIEW (IMPORTANT):\n\n"
                        f"✅ OPTION 1 - Web Server (RECOMMENDED):\n"
                        f"   Open: http://localhost:5000/generated_pages/\n"
                        f"   (Web server must be running on port 5000)\n\n"
                        f"⚠️ OPTION 2 - Direct File:\n"
                        f"   Open: {abs_selector}\n"
                        f"   Note: Videos may not play due to browser\n"
                        f"   security. Use Option 1 for best results.\n\n"
                        f"💡 TIP: Keep your web server running!"))
                self.root.after(
                    0, lambda: self.stat.config(
                        text=f"✅ GENERATED: {len(generated)} pages"))

            except Exception as e:
                self.root.after(
                    0,
                    lambda: messagebox.showerror("Generation Error", str(e)))
                self.root.after(
                    0, lambda: self.stat.config(text="Generation failed"))

        threading.Thread(target=generation_thread, daemon=True).start()

    def build_group_m3u(self, channels):
        """Build M3U content for a group of channels"""
        m3u = "#EXTM3U\n"
        for ch in channels:
            extinf = f'#EXTINF:-1 tvg-id="{ch.get("tvg_id", "")}" tvg-name="{ch.get("name", "")}" '
            extinf += f'tvg-logo="{ch.get("logo", "")}" group-title="{ch.get("group", "Other")}",{ch.get("name", "")}\n'
            m3u += extinf + ch.get("url", "") + "\n"
        return m3u

    def start_autosave(self):
        """Start autosave timer - saves every 5 minutes if changes detected"""
        def autosave_check():
            if self.autosave_counter > 0 and self.channels:
                minutes_since_save = (datetime.now() - self.last_save_time).total_seconds() / 60
                if minutes_since_save >= 5:
                    self.autosave()
            # Schedule next check
            self.root.after(60000, autosave_check)  # Check every minute
        
        # Start the autosave checker
        self.root.after(60000, autosave_check)
    
    def autosave(self):
        """Perform automatic save to backups folder"""
        try:
            backups_dir = Path("backups")
            backups_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backups_dir / f"autosave_{timestamp}.m3u"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(self.m3u)
            
            self.last_save_time = datetime.now()
            self.autosave_counter = 0
            self.stat.config(text=f"💾 Autosaved: {backup_file.name}")
            self.logger.info(f"Autosaved to {backup_file}")
            
            # Keep only last 10 autosaves
            autosaves = sorted(backups_dir.glob("autosave_*.m3u"))
            if len(autosaves) > 10:
                for old_file in autosaves[:-10]:
                    old_file.unlink()
        except Exception as e:
            self.logger.error(f"Autosave failed: {e}")
    
    def mark_changed(self):
        """Mark that channels have been modified"""
        self.autosave_counter += 1
        self.mark_dirty()  # Update window title to show unsaved changes
    
    def create_progress_dialog(self, title, total):
        """Create a progress bar dialog with cancel button for long operations"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x180")
        dialog.configure(bg="#1e1e1e")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Cancel flag
        cancel_flag = {"cancelled": False}
        
        tk.Label(dialog, text=title, font=("Arial", 14, "bold"),
                fg="#00ff41", bg="#1e1e1e").pack(pady=15)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(dialog, variable=progress_var,
                                      maximum=total, length=450, mode='determinate')
        progress_bar.pack(pady=10)
        
        status_label = tk.Label(dialog, text="Starting...", font=("Arial", 10),
                               fg="#fff", bg="#1e1e1e")
        status_label.pack(pady=5)
        
        def cancel_operation():
            cancel_flag["cancelled"] = True
            status_label.config(text="Cancelling...", fg="#ff6b6b")
        
        tk.Button(dialog, text="Cancel", command=cancel_operation,
                 bg="#e74c3c", fg="#fff", font=("Arial", 10),
                 width=12).pack(pady=10)
        
        return dialog, progress_var, status_label, cancel_flag
    
    def safe_exit(self):
        """Safe exit procedure"""
        # Final autosave if there are unsaved changes
        if self.autosave_counter > 0 and self.channels:
            response = messagebox.askyesno(
                "Unsaved Changes", 
                "You have unsaved changes. Save before exit?")
            if response:
                self.save()
        
        self.save_settings()
        self.root.quit()

    def export_m3u_output(self):
        """Export M3U playlist to organized exports folder"""
        if not self.channels:
            messagebox.showwarning("No Channels", "Load channels first!")
            return
        
        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".m3u",
            filetypes=[("M3U files", "*.m3u"), ("M3U8 files", "*.m3u8"), ("All files", "*.*")],
            initialdir=str(exports_dir),
            initialfile=f"playlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.m3u"
        )
        
        if filename:
            try:
                m3u_content = "#EXTM3U\n"
                for ch in self.channels:
                    extinf = f'#EXTINF:-1 tvg-id="{ch.get("tvg_id", "")}" tvg-name="{ch.get("name", "")}" '
                    extinf += f'tvg-logo="{ch.get("logo", "")}" group-title="{ch.get("group", "Other")}",{ch.get("name", "")}\n'
                    
                    if ch.get('subtitle'):
                        extinf = extinf.replace('\n', f' tvg-subtitle="{ch.get("subtitle")}"\n')
                    
                    m3u_content += extinf + ch.get("url", "") + "\n"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(m3u_content)
                
                messagebox.showinfo("Success", 
                                  f"M3U playlist exported!\n"
                                  f"Channels: {len(self.channels)}\n"
                                  f"File: {filename}")
                self.stat.config(text=f"✅ Exported M3U: {len(self.channels)} channels")
                
            except Exception as e:
                self.show_error_dialog("Export Failed", "Could not export M3U", e)

    def generate_thumbnails(self):
        """Generate thumbnails (Pillow placeholders or FFmpeg from video files)"""
        if not self.channels:
            messagebox.showwarning("No Channels", "Load channels first!")
            return
        
        choice = messagebox.askquestion(
            "Thumbnail Generation",
            "Generate PLACEHOLDER thumbnails (Yes) or use FFmpeg on video files (No)?",
            icon='question'
        )
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            thumb_dir = Path("thumbnails")
            thumb_dir.mkdir(exist_ok=True)
            
            if choice == 'yes':
                # Generate placeholder thumbnails with PIL
                generated = 0
                for ch in self.channels:
                    try:
                        # Create 480x270 thumbnail with channel name
                        img = Image.new('RGB', (480, 270), color=(30, 30, 30))
                        draw = ImageDraw.Draw(img)
                        
                        # Draw channel name
                        name = ch.get('name', 'Unknown')[:40]
                        group = ch.get('group', 'Other')
                        
                        # Try to use a font, fallback to default
                        try:
                            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
                        except:
                            font_title = ImageFont.load_default()
                            font_sub = ImageFont.load_default()
                        
                        # Draw text centered
                        draw.text((240, 100), name, fill=(255, 215, 0), font=font_title, anchor="mm")
                        draw.text((240, 150), f"Group: {group}", fill=(150, 150, 150), font=font_sub, anchor="mm")
                        draw.text((240, 180), f"Channel #{ch.get('num', '?')}", fill=(100, 100, 100), font=font_sub, anchor="mm")
                        
                        # Save
                        safe_name = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in name)
                        thumb_file = thumb_dir / f"{safe_name}_thumb.jpg"
                        img.save(thumb_file, 'JPEG', quality=85)
                        
                        generated += 1
                        self.stat.config(text=f"Generated: {generated}/{len(self.channels)}")
                        self.root.update()
                        
                    except Exception as e:
                        self.logger.warning(f"Thumb gen failed for {ch.get('name')}: {e}")
                        continue
                
                messagebox.showinfo("Success", 
                                  f"Generated {generated} placeholder thumbnails!\n"
                                  f"Location: {thumb_dir.absolute()}")
                self.stat.config(text=f"✅ Generated {generated} thumbnails")
            
            else:
                # FFmpeg mode - for actual video files
                import subprocess
                
                video_dir = filedialog.askdirectory(title="Select folder with video files")
                if not video_dir:
                    return
                
                video_files = list(Path(video_dir).glob('*.mp4')) + list(Path(video_dir).glob('*.mkv'))
                
                if not video_files:
                    messagebox.showwarning("No Videos", "No MP4 or MKV files found!")
                    return
                
                generated = 0
                for video_file in video_files[:20]:  # Limit to 20 files
                    try:
                        thumb_file = thumb_dir / f"{video_file.stem}_thumb.jpg"
                        
                        cmd = [
                            'ffmpeg', '-i', str(video_file), '-ss', '00:00:05',
                            '-vframes', '1', '-vf', 'scale=480:270',
                            str(thumb_file), '-y'
                        ]
                        
                        subprocess.run(cmd, capture_output=True, timeout=30)
                        generated += 1
                        self.stat.config(text=f"Generated: {generated}/{len(video_files)}")
                        self.root.update()
                        
                    except Exception as e:
                        self.logger.warning(f"FFmpeg failed for {video_file.name}: {e}")
                        continue
                
                messagebox.showinfo("Success", 
                                  f"Generated {generated} FFmpeg thumbnails!\n"
                                  f"Location: {thumb_dir.absolute()}")
                self.stat.config(text=f"✅ Generated {generated} FFmpeg thumbs")
                
        except Exception as e:
            self.show_error_dialog("Thumbnail Generation Failed", 
                                 "Could not generate thumbnails", e)
    
    def url_import_workbench(self):
        """Import URLs from text file or clipboard - Enhanced Notepad Mode"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Import Workbench - Notepad Mode")
        dialog.geometry("900x700")
        dialog.configure(bg="#1e1e1e")
        
        tk.Label(dialog, text="📝 IMPORT WORKBENCH - NOTEPAD MODE", 
                font=("Arial", 18, "bold"), 
                fg="gold", bg="#1e1e1e").pack(pady=10)
        
        tk.Label(dialog, text="Paste URLs or M3U content below:", 
                fg="#fff", bg="#1e1e1e").pack()
        
        text_frame = tk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        text = tk.Text(text_frame, bg="#333", fg="#fff", 
                      insertbackground="#fff", font=("Consolas", 10),
                      wrap=tk.NONE)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll_y = tk.Scrollbar(text_frame, command=text.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scroll_y.set)
        
        scroll_x = tk.Scrollbar(dialog, orient=tk.HORIZONTAL, command=text.xview)
        scroll_x.pack(fill=tk.X, padx=20)
        text.config(xscrollcommand=scroll_x.set)
        
        def load_from_file():
            """Open a file and load content"""
            file = filedialog.askopenfilename(
                title="Open File",
                filetypes=[("All files", "*.*"), ("M3U files", "*.m3u"), 
                          ("Text files", "*.txt"), ("M3U8 files", "*.m3u8")]
            )
            if file:
                try:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        text.delete("1.0", tk.END)
                        text.insert("1.0", content)
                        self.stat.config(text=f"Loaded: {os.path.basename(file)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open file:\n{e}")
        
        def save_to_file():
            """Save text content to file"""
            content = text.get("1.0", tk.END).strip()
            if not content:
                messagebox.showwarning("Empty", "Nothing to save!")
                return
            
            file = filedialog.asksaveasfilename(
                title="Save As",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("M3U files", "*.m3u"), 
                          ("M3U8 files", "*.m3u8"), ("All files", "*.*")]
            )
            if file:
                try:
                    with open(file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    messagebox.showinfo("Saved", f"File saved:\n{os.path.basename(file)}")
                    self.stat.config(text=f"Saved: {os.path.basename(file)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save file:\n{e}")
        
        def copy_to_clipboard():
            """Copy text to clipboard"""
            content = text.get("1.0", tk.END).strip()
            if not content:
                messagebox.showwarning("Empty", "Nothing to copy!")
                return
            
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.root.update()
            messagebox.showinfo("Copied", "Content copied to clipboard!")
            self.stat.config(text="Copied to clipboard")
        
        def clear_text():
            """Clear all text"""
            if text.get("1.0", tk.END).strip():
                if messagebox.askyesno("Clear All", "Delete all text?"):
                    text.delete("1.0", tk.END)
                    self.stat.config(text="Text cleared")
        
        def generate_m3u():
            """Parse M3U content and add to playlist"""
            content = text.get("1.0", tk.END).strip()
            if not content:
                messagebox.showwarning("Empty", "Enter M3U content first!")
                return
            
            try:
                # Save to temporary file for parsing
                temp_file = Path(tempfile.gettempdir()) / "workbench_temp.m3u"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Parse M3U
                channels = self.parse_m3u_file(str(temp_file))
                
                if not channels:
                    messagebox.showwarning("No Channels", "No valid channels found in M3U content!")
                    temp_file.unlink()
                    return
                
                # Add to playlist with proper numbering and required fields
                start_num = len(self.channels) + 1
                for idx, channel in enumerate(channels):
                    # Ensure all required fields exist
                    channel['num'] = start_num + idx
                    channel.setdefault('uuid', str(uuid.uuid4()))
                    channel.setdefault('name', 'Unknown')
                    channel.setdefault('group', 'Other')
                    channel.setdefault('logo', '')
                    channel.setdefault('tvg_id', '')
                    channel.setdefault('url', '')
                    channel.setdefault('backups', [])
                    channel.setdefault('custom_tags', {})
                    
                    self.channels.append(channel)
                
                # Clean up temp file
                temp_file.unlink()
                
                # Refresh UI
                self.fill()
                self.build_m3u()
                
                messagebox.showinfo("Success", 
                                  f"✅ Generated M3U!\n\n"
                                  f"Added {len(channels)} channels to playlist\n"
                                  f"Total channels: {len(self.channels)}")
                self.stat.config(text=f"Added {len(channels)} channels from M3U")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Parse Error", 
                                   f"Could not parse M3U content:\n{str(e)}")
        
        def import_urls():
            """Import plain URLs (legacy function)"""
            urls = text.get("1.0", tk.END).strip().split('\n')
            urls = [u.strip() for u in urls if u.strip()]
            
            if not urls:
                messagebox.showwarning("No URLs", "Enter URLs first!")
                return
            
            added = 0
            for url in urls:
                if url.startswith('http'):
                    filename = url.split('/')[-1] or f"url_{added}"
                    self.channels.append({
                        'name': filename,
                        'group': 'Imported',
                        'url': url,
                        'logo': '',
                        'num': len(self.channels) + 1,
                        'uuid': str(uuid.uuid4()),
                        'custom_tags': {}
                    })
                    added += 1
            
            self.fill()
            self.build_m3u()
            messagebox.showinfo("Success", f"Imported {added} URLs!")
            self.stat.config(text=f"Imported {added} URLs")
            dialog.destroy()
        
        # Button row 1: File operations
        btn_frame1 = tk.Frame(dialog, bg="#1e1e1e")
        btn_frame1.pack(pady=5)
        
        tk.Button(btn_frame1, text="📁 Open", bg="#3498db", 
                 fg="white", width=12, command=load_from_file).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_frame1, text="💾 Save", bg="#2ecc71", 
                 fg="white", width=12, command=save_to_file).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_frame1, text="📋 Copy", bg="#9b59b6", 
                 fg="white", width=12, command=copy_to_clipboard).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_frame1, text="🗑️ Clear", bg="#e67e22", 
                 fg="white", width=12, command=clear_text).pack(side=tk.LEFT, padx=3)
        
        # Button row 2: Import operations
        btn_frame2 = tk.Frame(dialog, bg="#1e1e1e")
        btn_frame2.pack(pady=5)
        
        tk.Button(btn_frame2, text="🎬 Generate M3U", bg="#27ae60", 
                 fg="white", width=20, height=2, font=("Arial", 11, "bold"),
                 command=generate_m3u).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame2, text="Import URLs Only", bg="#16a085", 
                 fg="white", width=20, height=2, command=import_urls).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame2, text="❌ Close", bg="#e74c3c", 
                 fg="white", width=15, height=2, command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def export_tv_guide_json(self):
        """Export 7-day TV Guide in JSON format with timestamps"""
        if not self.channels:
            messagebox.showwarning("No Channels", "Load channels first!")
            return
        
        # Ask for duration and days
        duration = simpledialog.askinteger(
            "Show Duration",
            "Enter show duration in minutes:",
            initialvalue=30,
            minvalue=5,
            maxvalue=180
        )
        
        if not duration:
            return
        
        days = simpledialog.askinteger(
            "Number of Days",
            "Generate TV guide for how many days?",
            initialvalue=7,
            minvalue=1,
            maxvalue=30
        )
        
        if not days:
            return
        
        try:
            json_dir = Path("json")
            json_dir.mkdir(exist_ok=True)
            cache_dir = Path("cache")
            cache_dir.mkdir(exist_ok=True)
            
            # Generate 7-day schedule
            tv_guide = {
                "config": {
                    "channel_name": "M3U Matrix Channel",
                    "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_days": days,
                    "show_duration_minutes": duration,
                    "total_shows": 0,
                    "buffer_enabled": True,
                    "cache_enabled": True
                },
                "days": []
            }
            
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            channel_index = 0
            total_shows = 0
            
            for day in range(days):
                current_day = start_date + timedelta(days=day)
                day_schedule = {
                    "date": current_day.strftime("%Y-%m-%d"),
                    "day_name": current_day.strftime("%A"),
                    "shows": []
                }
                
                current_time = current_day
                
                # Fill 24 hours
                while current_time.date() == current_day.date():
                    # Rotate through channels
                    if channel_index >= len(self.channels):
                        channel_index = 0
                    
                    ch = self.channels[channel_index]
                    
                    show_entry = {
                        "show_number": total_shows + 1,
                        "show_title": ch.get('name', 'Unknown'),
                        "start_time": current_time.strftime("%H:%M:%S"),
                        "duration_minutes": duration,
                        "url": ch.get('url', ''),
                        "logo": ch.get('logo', ''),
                        "group": ch.get('group', 'Unknown'),
                        "channel_number": ch.get('num', 0),
                        "cache_file": f"cache/show_{total_shows + 1}.dat",
                        "buffer_file": f"buffer/buffer_{(total_shows + 1) % 10}.dat"
                    }
                    
                    end_time = current_time + timedelta(minutes=duration)
                    show_entry["end_time"] = end_time.strftime("%H:%M:%S")
                    
                    day_schedule["shows"].append(show_entry)
                    current_time = end_time
                    channel_index += 1
                    total_shows += 1
                
                tv_guide["days"].append(day_schedule)
            
            tv_guide["config"]["total_shows"] = total_shows
            
            # Save main guide
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialdir=str(json_dir),
                initialfile=f"tv_guide_{days}day_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(tv_guide, f, indent=2, ensure_ascii=False)
                
                # Also save a quick-access cache index
                cache_index = {
                    "guide_file": filename,
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_shows": total_shows,
                    "days": days
                }
                
                with open(cache_dir / "guide_index.json", 'w') as f:
                    json.dump(cache_index, f, indent=2)
                
                messagebox.showinfo("Success", 
                                  f"📺 {days}-Day TV Guide Generated!\n\n"
                                  f"Total Shows: {total_shows}\n"
                                  f"Duration: {duration} min/show\n"
                                  f"Days: {days}\n\n"
                                  f"Main file: {Path(filename).name}\n"
                                  f"Cache index: cache/guide_index.json")
                self.stat.config(text=f"✅ Generated {days}-day guide ({total_shows} shows)")
                
        except Exception as e:
            self.show_error_dialog("Export Failed", "Could not export TV Guide JSON", e)
    
    def smart_scheduler(self):
        """Intelligent playlist scheduler with rotation algorithms and random modes"""
        if not self.channels:
            messagebox.showwarning("No Channels", "Load channels first!")
            return
        
        # Create scheduler dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("📺 SMART SCHEDULER - Intelligent Playlist Generator")
        dialog.geometry("700x750")
        dialog.configure(bg="#1a1a2e")
        
        # Title
        tk.Label(dialog, text="SMART SCHEDULER", 
                font=("Arial", 18, "bold"), fg="#00ff41", bg="#1a1a2e").pack(pady=15)
        
        # Configuration Frame
        config_frame = tk.Frame(dialog, bg="#16213e", relief=tk.RAISED, bd=2)
        config_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)
        
        # Schedule Mode Selection
        tk.Label(config_frame, text="SCHEDULING MODE:", 
                font=("Arial", 12, "bold"), fg="#f0f0f0", bg="#16213e").pack(pady=(15,5))
        
        mode_var = tk.StringVar(value="balanced")
        
        modes = [
            ("balanced", "🎯 Balanced Rotation", "Equal time for all shows, prevents dominance"),
            ("random", "🎲 Random Shuffle", "Unpredictable viewing with smart distribution"),
            ("weighted", "📊 Weighted Mix", "Popular shows get more slots"),
            ("sequential", "📜 Sequential", "Classic order with group awareness")
        ]
        
        for val, label, desc in modes:
            frame = tk.Frame(config_frame, bg="#16213e")
            frame.pack(fill=tk.X, padx=15, pady=3)
            tk.Radiobutton(frame, text=label, variable=mode_var, value=val,
                          font=("Arial", 10, "bold"), fg="#fff", bg="#16213e",
                          selectcolor="#444", activebackground="#16213e").pack(anchor=tk.W)
            tk.Label(frame, text=f"   └─ {desc}", 
                    font=("Arial", 8), fg="#aaa", bg="#16213e").pack(anchor=tk.W, padx=30)
        
        # Parameters Frame
        params_frame = tk.Frame(config_frame, bg="#0f3460")
        params_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Duration
        tk.Label(params_frame, text="Show Duration (minutes):", 
                fg="#fff", bg="#0f3460", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        duration_var = tk.IntVar(value=30)
        duration_spin = tk.Spinbox(params_frame, from_=5, to=180, textvariable=duration_var,
                                  width=10, font=("Arial", 10))
        duration_spin.grid(row=0, column=1, padx=10, pady=5)
        
        # Days
        tk.Label(params_frame, text="Number of Days:", 
                fg="#fff", bg="#0f3460", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        days_var = tk.IntVar(value=7)
        days_spin = tk.Spinbox(params_frame, from_=1, to=30, textvariable=days_var,
                              width=10, font=("Arial", 10))
        days_spin.grid(row=1, column=1, padx=10, pady=5)
        
        # Max consecutive shows
        tk.Label(params_frame, text="Max Consecutive Shows:", 
                fg="#fff", bg="#0f3460", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        max_consec_var = tk.IntVar(value=3)
        max_consec_spin = tk.Spinbox(params_frame, from_=1, to=10, textvariable=max_consec_var,
                                    width=10, font=("Arial", 10))
        max_consec_spin.grid(row=2, column=1, padx=10, pady=5)
        
        # Advanced Options
        tk.Label(config_frame, text="ADVANCED OPTIONS:", 
                font=("Arial", 11, "bold"), fg="#f0f0f0", bg="#16213e").pack(pady=(10,5))
        
        options_frame = tk.Frame(config_frame, bg="#16213e")
        options_frame.pack(fill=tk.X, padx=15, pady=5)
        
        group_aware_var = tk.BooleanVar(value=True)
        thumbnails_var = tk.BooleanVar(value=True)
        buffer_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(options_frame, text="📁 Group-Aware Scheduling (respect categories)",
                      variable=group_aware_var, fg="#fff", bg="#16213e",
                      selectcolor="#444", activebackground="#16213e").pack(anchor=tk.W, pady=2)
        tk.Checkbutton(options_frame, text="🖼️  Generate Thumbnails",
                      variable=thumbnails_var, fg="#fff", bg="#16213e",
                      selectcolor="#444", activebackground="#16213e").pack(anchor=tk.W, pady=2)
        tk.Checkbutton(options_frame, text="💾 Enable Buffer/Cache Files",
                      variable=buffer_var, fg="#fff", bg="#16213e",
                      selectcolor="#444", activebackground="#16213e").pack(anchor=tk.W, pady=2)
        
        # Preview Stats
        stats_frame = tk.Frame(config_frame, bg="#1a1a2e", relief=tk.SUNKEN, bd=2)
        stats_frame.pack(fill=tk.X, padx=15, pady=10)
        
        stats_label = tk.Label(stats_frame, text="", font=("Courier", 9), 
                              fg="#00ff41", bg="#1a1a2e", justify=tk.LEFT)
        stats_label.pack(padx=10, pady=10)
        
        def update_stats():
            duration = duration_var.get()
            days = days_var.get()
            slots_per_day = (24 * 60) // duration
            total_slots = slots_per_day * days
            total_channels = len(self.channels)
            
            stats_text = f"""
📊 SCHEDULE STATISTICS:
─────────────────────────
Channels Available: {total_channels}
Total Time Slots: {total_slots}
Slots per Day: {slots_per_day}
Duration per Show: {duration} min
Rotations: {total_slots // total_channels if total_channels > 0 else 0}x through library
Coverage: {(total_slots / total_channels):.1f}x per show
"""
            stats_label.config(text=stats_text)
        
        update_stats()
        duration_spin.config(command=update_stats)
        days_spin.config(command=update_stats)
        
        # Generate Button
        def generate():
            import random
            from collections import defaultdict
            
            try:
                mode = mode_var.get()
                duration = duration_var.get()
                days = days_var.get()
                max_consecutive = max_consec_var.get()
                group_aware = group_aware_var.get()
                
                # Initialize schedule
                tv_guide = {
                    "config": {
                        "channel_name": "M3U Matrix Smart Channel",
                        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "total_days": days,
                        "show_duration_minutes": duration,
                        "scheduling_mode": mode,
                        "max_consecutive": max_consecutive,
                        "group_aware": group_aware,
                        "total_shows": 0
                    },
                    "days": []
                }
                
                # Group channels if group-aware mode
                if group_aware:
                    groups = defaultdict(list)
                    for ch in self.channels:
                        group = ch.get('group', 'Other')
                        groups[group].append(ch)
                    group_list = list(groups.keys())
                else:
                    groups = {"All": self.channels}
                    group_list = ["All"]
                
                # Generate schedule based on mode
                playlist = []
                total_slots = (24 * 60 * days) // duration
                
                if mode == "balanced":
                    # Equal distribution - round-robin through all channels
                    for slot in range(total_slots):
                        ch = self.channels[slot % len(self.channels)]
                        playlist.append(ch)
                
                elif mode == "random":
                    # Smart random - tracks usage to ensure balanced distribution
                    usage_count = defaultdict(int)
                    available = self.channels.copy()
                    
                    for slot in range(total_slots):
                        # Reset if all shows used equally
                        if all(usage_count[ch.get('url', id(ch))] >= (slot // len(self.channels)) + 1 
                              for ch in self.channels):
                            usage_count.clear()
                        
                        # Filter out recently used
                        if len(playlist) > 0:
                            recent = [playlist[-i].get('url', '') for i in range(1, min(max_consecutive, len(playlist)) + 1)]
                            available = [ch for ch in self.channels if ch.get('url', '') not in recent]
                        
                        if not available:
                            available = self.channels.copy()
                        
                        ch = random.choice(available)
                        playlist.append(ch)
                        usage_count[ch.get('url', id(ch))] += 1
                
                elif mode == "weighted":
                    # Weighted by group size
                    weights = []
                    for ch in self.channels:
                        group = ch.get('group', 'Other')
                        weight = len(groups[group])
                        weights.append(weight)
                    
                    for slot in range(total_slots):
                        ch = random.choices(self.channels, weights=weights, k=1)[0]
                        playlist.append(ch)
                
                elif mode == "sequential":
                    # Sequential with group rotation
                    if group_aware:
                        group_idx = 0
                        channel_idx_per_group = {g: 0 for g in groups}
                        
                        for slot in range(total_slots):
                            current_group = group_list[group_idx % len(group_list)]
                            group_channels = groups[current_group]
                            
                            ch_idx = channel_idx_per_group[current_group]
                            ch = group_channels[ch_idx % len(group_channels)]
                            playlist.append(ch)
                            
                            channel_idx_per_group[current_group] += 1
                            if channel_idx_per_group[current_group] >= len(group_channels):
                                group_idx += 1
                    else:
                        for slot in range(total_slots):
                            playlist.append(self.channels[slot % len(self.channels)])
                
                # Build day schedules
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                slot_idx = 0
                
                for day in range(days):
                    current_day = start_date + timedelta(days=day)
                    day_schedule = {
                        "date": current_day.strftime("%Y-%m-%d"),
                        "day_name": current_day.strftime("%A"),
                        "shows": []
                    }
                    
                    current_time = current_day
                    
                    while current_time.date() == current_day.date() and slot_idx < len(playlist):
                        ch = playlist[slot_idx]
                        
                        show_entry = {
                            "show_number": slot_idx + 1,
                            "show_title": ch.get('name', 'Unknown'),
                            "start_time": current_time.strftime("%H:%M:%S"),
                            "duration_minutes": duration,
                            "url": ch.get('url', ''),
                            "logo": ch.get('logo', ''),
                            "group": ch.get('group', 'Unknown'),
                            "channel_number": ch.get('num', 0)
                        }
                        
                        if buffer_var.get():
                            show_entry["cache_file"] = f"cache/show_{slot_idx + 1}.dat"
                            show_entry["buffer_file"] = f"buffer/buffer_{(slot_idx + 1) % 10}.dat"
                        
                        end_time = current_time + timedelta(minutes=duration)
                        show_entry["end_time"] = end_time.strftime("%H:%M:%S")
                        
                        day_schedule["shows"].append(show_entry)
                        current_time = end_time
                        slot_idx += 1
                    
                    tv_guide["days"].append(day_schedule)
                
                tv_guide["config"]["total_shows"] = len(playlist)
                
                # Show preview window with SAVE button
                preview_win = tk.Toplevel(dialog)
                preview_win.title("Smart Schedule Preview")
                preview_win.geometry("800x600")
                preview_win.configure(bg="#1a1a2e")
                
                # Header
                header = tk.Label(preview_win, 
                                text=f"✅ SCHEDULE GENERATED - {mode.upper()} MODE\n"
                                     f"Total Shows: {len(playlist)} | Duration: {duration} min/show | Days: {days}",
                                bg="#00ff41", fg="#000", font=("Arial", 12, "bold"),
                                pady=10)
                header.pack(fill=tk.X)
                
                # Preview Text
                preview_frame = tk.Frame(preview_win, bg="#1a1a2e")
                preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                preview_text = tk.Text(preview_frame, bg="#2a2a3e", fg="#00ff41",
                                     font=("Courier", 9), wrap=tk.WORD)
                preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                
                scrollbar = tk.Scrollbar(preview_frame, command=preview_text.yview)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                preview_text.config(yscrollcommand=scrollbar.set)
                
                # Insert schedule preview
                preview_text.insert(tk.END, json.dumps(tv_guide, indent=2, ensure_ascii=False))
                preview_text.config(state=tk.DISABLED)
                
                # Button frame
                btn_frame = tk.Frame(preview_win, bg="#1a1a2e")
                btn_frame.pack(fill=tk.X, pady=10)
                
                def save_schedule():
                    json_dir = Path("json")
                    json_dir.mkdir(exist_ok=True)
                    
                    filename = filedialog.asksaveasfilename(
                        defaultextension=".json",
                        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                        initialdir=str(json_dir),
                        initialfile=f"smart_schedule_{mode}_{days}day_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    )
                    
                    if filename:
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(tv_guide, f, indent=2, ensure_ascii=False)
                        
                        messagebox.showinfo("💾 Saved!", 
                                          f"Smart Schedule saved successfully!\n\n"
                                          f"File: {Path(filename).name}\n"
                                          f"Location: {Path(filename).parent}")
                        preview_win.destroy()
                        dialog.destroy()
                        self.stat.config(text=f"✅ Smart schedule saved: {mode} mode")
                
                def save_and_generate_page():
                    json_dir = Path("json")
                    json_dir.mkdir(exist_ok=True)
                    
                    filename = filedialog.asksaveasfilename(
                        defaultextension=".json",
                        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                        initialdir=str(json_dir),
                        initialfile=f"smart_schedule_{mode}_{days}day_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    )
                    
                    if filename:
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(tv_guide, f, indent=2, ensure_ascii=False)
                        
                        messagebox.showinfo("💾 Saved!", 
                                          f"Smart Schedule saved!\n\n"
                                          f"File: {Path(filename).name}\n\n"
                                          f"Now use GENERATE PAGES to create NEXUS TV page.")
                        preview_win.destroy()
                        dialog.destroy()
                        self.stat.config(text=f"✅ Smart schedule saved")
                
                # Buttons
                tk.Button(btn_frame, text="💾 SAVE SCHEDULE", command=save_schedule,
                         bg="#00ff41", fg="#000", font=("Arial", 11, "bold"),
                         width=20, height=2).pack(side=tk.LEFT, padx=10)
                
                tk.Button(btn_frame, text="📋 COPY TO CLIPBOARD", 
                         command=lambda: self.root.clipboard_append(json.dumps(tv_guide, indent=2)),
                         bg="#3498db", fg="#fff", font=("Arial", 10),
                         width=20, height=2).pack(side=tk.LEFT, padx=10)
                
                tk.Button(btn_frame, text="❌ CLOSE", command=preview_win.destroy,
                         bg="#e74c3c", fg="#fff", font=("Arial", 10),
                         width=15, height=2).pack(side=tk.LEFT, padx=10)
            
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate schedule:\n{e}")
        
        # Button Frame
        btn_frame = tk.Frame(dialog, bg="#1a1a2e")
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="✨ GENERATE SCHEDULE", command=generate,
                 bg="#00ff41", fg="#000", font=("Arial", 12, "bold"),
                 width=25, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                 bg="#e74c3c", fg="#fff", font=("Arial", 10),
                 width=12, height=2).pack(side=tk.LEFT, padx=5)
    
    # ========== TIMESTAMP GENERATOR ==========
    def timestamp_generator(self):
        """Generate M3U playlists with timestamps from media files"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Timestamp Generator - Media Scanner")
        dialog.geometry("700x600")
        dialog.configure(bg="#1e1e1e")
        
        # Instructions
        instructions = tk.Label(dialog, 
                               text="📹 Timestamp Generator\n\n"
                                    "Scans video/audio files and creates M3U playlists with timestamps.\n"
                                    "Supports: MP4, MKV, AVI, MP3, OGG, WEBM, FLV, MOV",
                               bg="#1e1e1e", fg="#fff", font=("Arial", 11), justify=tk.LEFT)
        instructions.pack(pady=15, padx=15)
        
        # Directory selection
        dir_frame = tk.Frame(dialog, bg="#1e1e1e")
        dir_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(dir_frame, text="Scan Directory:", bg="#1e1e1e", fg="#fff").pack(side=tk.LEFT)
        dir_var = tk.StringVar(value=str(Path.cwd()))
        tk.Entry(dir_frame, textvariable=dir_var, width=40, bg="#333", fg="#fff").pack(side=tk.LEFT, padx=10)
        tk.Button(dir_frame, text="Browse", command=lambda: self.browse_directory(dir_var),
                 bg="#2980b9", fg="#fff").pack(side=tk.LEFT)
        
        # Options
        options_frame = tk.Frame(dialog, bg="#1e1e1e")
        options_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(options_frame, text="Timestamp Interval (seconds):", 
                bg="#1e1e1e", fg="#fff").pack(side=tk.LEFT)
        interval_var = tk.IntVar(value=60)
        tk.Spinbox(options_frame, from_=10, to=3600, textvariable=interval_var,
                  width=10, bg="#333", fg="#fff").pack(side=tk.LEFT, padx=10)
        
        recursive_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Include subdirectories",
                      variable=recursive_var, bg="#1e1e1e", fg="#fff",
                      selectcolor="#333").pack(side=tk.LEFT, padx=20)
        
        # Results
        result_frame = tk.Frame(dialog, bg="#1e1e1e")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        tk.Label(result_frame, text="Found Media Files:", bg="#1e1e1e", fg="#fff").pack(anchor=tk.W)
        
        result_text = tk.Text(result_frame, height=15, bg="#333", fg="#0f0",
                             font=("Courier", 9), wrap=tk.WORD)
        result_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(result_frame, command=result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        result_text.config(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg="#1e1e1e")
        button_frame.pack(fill=tk.X, padx=15, pady=15)
        
        def scan_files():
            """Scan directory for media files"""
            directory = Path(dir_var.get())
            if not directory.exists():
                messagebox.showerror("Error", f"Directory not found: {directory}")
                return
            
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"Scanning {directory}...\n\n")
            dialog.update()
            
            # Supported formats
            video_formats = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm', '.m4v'}
            audio_formats = {'.mp3', '.ogg', '.m4a', '.aac', '.flac', '.wav', '.wma'}
            all_formats = video_formats | audio_formats
            
            # Scan files
            found_files = []
            if recursive_var.get():
                for ext in all_formats:
                    found_files.extend(directory.rglob(f"*{ext}"))
            else:
                for ext in all_formats:
                    found_files.extend(directory.glob(f"*{ext}"))
            
            found_files.sort()
            
            result_text.insert(tk.END, f"✅ Found {len(found_files)} media files\n\n")
            
            for file in found_files:
                size_mb = file.stat().st_size / (1024 * 1024)
                result_text.insert(tk.END, f"📹 {file.name} ({size_mb:.1f} MB)\n")
            
            result_text.insert(tk.END, f"\n{'='*60}\n")
            result_text.insert(tk.END, "Click 'Generate M3U' to create playlist with timestamps\n")
            
            # Store for generation
            dialog.found_files = found_files
        
        def generate_m3u():
            """Generate M3U with timestamps"""
            if not hasattr(dialog, 'found_files') or not dialog.found_files:
                messagebox.showwarning("No Files", "Scan for media files first!")
                return
            
            # Ask for output location
            output_file = filedialog.asksaveasfilename(
                defaultextension=".m3u",
                filetypes=[("M3U Playlist", "*.m3u"), ("M3U8 Playlist", "*.m3u8")],
                initialfile=f"timestamps_{datetime.now().strftime('%Y%m%d_%H%M%S')}.m3u"
            )
            
            if not output_file:
                return
            
            interval = interval_var.get()
            
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("#EXTM3U\n\n")
                    
                    for idx, file_path in enumerate(dialog.found_files, 1):
                        # Try to get duration using ffprobe (if available)
                        duration = self.get_media_duration(file_path)
                        
                        if duration:
                            # Generate timestamp entries
                            timestamps = list(range(0, int(duration), interval))
                            if not timestamps or timestamps[-1] < duration - interval/2:
                                timestamps.append(int(duration))
                            
                            for ts_idx, timestamp in enumerate(timestamps):
                                time_str = self.format_timestamp(timestamp)
                                
                                f.write(f"#EXTINF:-1 ")
                                f.write(f'tvg-id="{file_path.stem}_{ts_idx}" ')
                                f.write(f'tvg-name="{file_path.stem} - {time_str}" ')
                                f.write(f'group-title="Timestamps",')
                                f.write(f'{file_path.stem} - {time_str}\n')
                                f.write(f"{file_path}#t={timestamp}\n\n")
                        else:
                            # No duration available, single entry
                            f.write(f"#EXTINF:-1 ")
                            f.write(f'tvg-id="{file_path.stem}" ')
                            f.write(f'tvg-name="{file_path.name}" ')
                            f.write(f'group-title="Media",')
                            f.write(f'{file_path.name}\n')
                            f.write(f"{file_path}\n\n")
                
                result_text.insert(tk.END, f"\n✅ SUCCESS!\n")
                result_text.insert(tk.END, f"Generated: {output_file}\n")
                result_text.insert(tk.END, f"Interval: {interval}s\n")
                
                messagebox.showinfo("Success", 
                                  f"Timestamp M3U created!\n\n"
                                  f"Files: {len(dialog.found_files)}\n"
                                  f"Interval: {interval}s\n"
                                  f"Output: {Path(output_file).name}")
                
            except Exception as e:
                self.show_error_dialog("Generation Failed", "Could not create M3U", e)
        
        tk.Button(button_frame, text="🔍 Scan Files", command=scan_files,
                 bg="#27ae60", fg="#fff", width=15, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="📝 Generate M3U", command=generate_m3u,
                 bg="#e91e63", fg="#fff", width=15, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=dialog.destroy,
                 bg="#7f8c8d", fg="#fff", width=15).pack(side=tk.RIGHT, padx=5)
    
    def browse_directory(self, dir_var):
        """Browse for directory"""
        directory = filedialog.askdirectory(initialdir=dir_var.get())
        if directory:
            dir_var.set(directory)
    
    def get_media_duration(self, file_path):
        """Get media duration using ffprobe if available, else estimate"""
        try:
            # Try ffprobe first
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 
                 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
                 str(file_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Fallback: estimate based on file size (rough approximation)
        # For videos: ~1MB per minute at medium quality
        # For audio: ~1MB per 8 minutes
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            ext = file_path.suffix.lower()
            
            if ext in {'.mp3', '.ogg', '.m4a', '.aac', '.flac'}:
                # Audio estimate
                return size_mb * 8 * 60  # Rough estimate
            else:
                # Video estimate
                return size_mb * 60  # Rough estimate
        except:
            return None
    
    def format_timestamp(self, seconds):
        """Format seconds as HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def manage_subtitles(self):
        """Subtitle file management and integration"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Subtitle Management")
        dialog.geometry("700x500")
        dialog.configure(bg="#1e1e1e")
        
        tk.Label(dialog, text="SUBTITLE MANAGER", 
                font=("Arial", 18, "bold"), 
                fg="gold", bg="#1e1e1e").pack(pady=10)
        
        info_text = (
            "Add subtitle files (SRT) to selected channels\n"
            "Subtitles will be included in M3U export with tvg-subtitle tag"
        )
        tk.Label(dialog, text=info_text, fg="#fff", bg="#1e1e1e").pack(pady=5)
        
        frame = tk.Frame(dialog, bg="#1e1e1e")
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        listbox = tk.Listbox(frame, bg="#333", fg="#fff", font=("Arial", 10))
        listbox.pack(fill=tk.BOTH, expand=True)
        
        for ch in self.channels:
            subtitle = ch.get('subtitle', '')
            display = f"{ch['name']} → {subtitle if subtitle else '(no subtitle)'}"
            listbox.insert(tk.END, display)
        
        def add_subtitle():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("No Selection", "Select a channel first!")
                return
            
            idx = sel[0]
            srt_file = filedialog.askopenfilename(
                title="Select Subtitle File",
                filetypes=[("Subtitle files", "*.srt"), ("All files", "*.*")]
            )
            
            if srt_file:
                self.channels[idx]['subtitle'] = srt_file
                listbox.delete(idx)
                listbox.insert(idx, f"{self.channels[idx]['name']} → {srt_file}")
                messagebox.showinfo("Success", "Subtitle added!")
        
        def remove_subtitle():
            sel = listbox.curselection()
            if not sel:
                return
            
            idx = sel[0]
            if 'subtitle' in self.channels[idx]:
                del self.channels[idx]['subtitle']
                listbox.delete(idx)
                listbox.insert(idx, f"{self.channels[idx]['name']} → (no subtitle)")
        
        btn_frame = tk.Frame(dialog, bg="#1e1e1e")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Add Subtitle", bg="#27ae60", 
                 fg="white", width=15, command=add_subtitle).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove", bg="#e74c3c", 
                 fg="white", width=15, command=remove_subtitle).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", bg="#95a5a6", 
                 fg="white", width=15, command=dialog.destroy).pack(side=tk.LEFT, padx=5)


if __name__ == "__main__":
    try:
        app = M3UMatrix()
        app.root.protocol("WM_DELETE_WINDOW", app.safe_exit)
    except Exception as e:
        logging.error(f"Failed to start M3U Matrix: {e}")
        messagebox.showerror("Startup Error",
                             f"Failed to start application: {e}")

