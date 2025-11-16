#!/usr/bin/env python3
"""
Video Player Workbench - Advanced video playback and management interface
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json
import subprocess
from datetime import datetime, timedelta
import os
import sys
import shutil
import re
import urllib.parse
from PIL import Image, ImageTk
import threading

class VideoPlayerWorkbench(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Video Player Workbench")
        self.geometry("1400x900")
        self.configure(bg='#0f0f1e')
        
        self.playlist = []
        self.current_index = -1
        self.clipboard_videos = []
        self.schedule_data = []
        self.is_playing = False
        self.current_process = None
        
        self.screenshots_dir = Path(__file__).parent / "screenshots"
        self.data_dir = Path(__file__).parent / "data"
        self.screenshots_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        self.create_menu()
        self.create_layout()
        self.load_playlist_from_disk()
        
    def create_menu(self):
        menubar = tk.Menu(self, bg='#1a1a2e', fg='white')
        self.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0, bg='#1a1a2e', fg='white')
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Video(s)", command=self.open_videos, accelerator="Ctrl+O")
        file_menu.add_command(label="Open Folder", command=self.open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Save Playlist", command=self.save_playlist)
        file_menu.add_command(label="Load Playlist", command=self.load_playlist)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        edit_menu = tk.Menu(menubar, tearoff=0, bg='#1a1a2e', fg='white')
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy Selected", command=self.copy_selected, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_videos, accelerator="Ctrl+V")
        edit_menu.add_command(label="Delete Selected", command=self.delete_selected, accelerator="Delete")
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear All", command=self.clear_all)
        
        schedule_menu = tk.Menu(menubar, tearoff=0, bg='#1a1a2e', fg='white')
        menubar.add_cascade(label="Schedule", menu=schedule_menu)
        schedule_menu.add_command(label="Generate Schedule", command=self.generate_schedule)
        schedule_menu.add_command(label="Export Schedule", command=self.export_schedule)
        schedule_menu.add_command(label="View Schedule", command=self.view_schedule)
        
        self.bind_all("<Control-o>", lambda e: self.open_videos())
        self.bind_all("<Control-c>", lambda e: self.copy_selected())
        self.bind_all("<Control-v>", lambda e: self.paste_videos())
        self.bind_all("<Delete>", lambda e: self.delete_selected())
    
    def create_layout(self):
        main_container = tk.Frame(self, bg='#0f0f1e')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_panel = tk.Frame(main_container, bg='#1a1a2e', width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        right_panel = tk.Frame(main_container, bg='#1a1a2e')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.create_playlist_panel(left_panel)
        self.create_player_panel(right_panel)
    
    def create_playlist_panel(self, parent):
        header = tk.Label(
            parent,
            text="PLAYLIST",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='#00ff88'
        )
        header.pack(pady=10)
        
        tree_frame = tk.Frame(parent, bg='#1a1a2e')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.playlist_tree = ttk.Treeview(
            tree_frame,
            columns=('title', 'duration', 'type'),
            show='tree headings',
            yscrollcommand=scrollbar.set,
            selectmode='extended'
        )
        self.playlist_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.playlist_tree.yview)
        
        self.playlist_tree.heading('#0', text='#')
        self.playlist_tree.heading('title', text='Title')
        self.playlist_tree.heading('duration', text='Duration')
        self.playlist_tree.heading('type', text='Type')
        
        self.playlist_tree.column('#0', width=40, minwidth=40)
        self.playlist_tree.column('title', width=180)
        self.playlist_tree.column('duration', width=80)
        self.playlist_tree.column('type', width=60)
        
        self.playlist_tree.bind('<Double-Button-1>', self.on_playlist_double_click)
        
        btn_frame = tk.Frame(parent, bg='#1a1a2e')
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="📂 Load",
            command=self.import_files,
            bg='#4444ff',
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=15,
            pady=5,
            cursor='hand2'
        ).grid(row=0, column=0, padx=5)
        
        tk.Button(
            btn_frame,
            text="Add Videos",
            command=self.open_videos,
            bg='#00ff88',
            fg='#1a1a2e',
            font=('Arial', 9, 'bold'),
            padx=10,
            pady=5
        ).grid(row=0, column=1, padx=5)
        
        tk.Button(
            btn_frame,
            text="Remove",
            command=self.delete_selected,
            bg='#ff4444',
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=10,
            pady=5
        ).grid(row=0, column=2, padx=5)
        
        tk.Button(
            btn_frame,
            text="Clear All",
            command=self.clear_all,
            bg='#666666',
            fg='white',
            font=('Arial', 9, 'bold'),
            padx=10,
            pady=5
        ).grid(row=0, column=3, padx=5)
    
    def create_player_panel(self, parent):
        header = tk.Label(
            parent,
            text="VIDEO PLAYER",
            font=('Arial', 14, 'bold'),
            bg='#1a1a2e',
            fg='#00ff88'
        )
        header.pack(pady=10)
        
        video_frame = tk.Frame(parent, bg='#000000', height=500)
        video_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        self.video_placeholder = tk.Label(
            video_frame,
            text="No Video Loaded\n\nDouble-click a video in the playlist to play",
            font=('Arial', 14),
            fg='#666666',
            bg='#000000'
        )
        self.video_placeholder.pack(expand=True)
        
        info_frame = tk.Frame(parent, bg='#1a1a2e')
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.info_label = tk.Label(
            info_frame,
            text="Ready",
            font=('Arial', 10),
            fg='#cccccc',
            bg='#1a1a2e',
            anchor='w'
        )
        self.info_label.pack(fill=tk.X)
        
        controls_frame = tk.Frame(parent, bg='#1a1a2e')
        controls_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(
            controls_frame,
            text="◄◄ Previous",
            command=self.previous_video,
            bg='#333333',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        self.play_btn = tk.Button(
            controls_frame,
            text="▶ Play",
            command=self.toggle_play,
            bg='#00ff88',
            fg='#1a1a2e',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        )
        self.play_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            controls_frame,
            text="Next ►►",
            command=self.next_video,
            bg='#333333',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            controls_frame,
            text="📸 Screenshot",
            command=self.capture_screenshot,
            bg='#4444ff',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            controls_frame,
            text="ℹ Info",
            command=self.show_video_info,
            bg='#ff8800',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
    
    def open_videos(self):
        files = filedialog.askopenfilenames(
            title="Select Video Files",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v"),
                ("All files", "*.*")
            ]
        )
        
        if files:
            threading.Thread(target=self.add_videos_to_playlist, args=(files,), daemon=True).start()
    
    def open_folder(self):
        folder = filedialog.askdirectory(title="Select Folder with Videos")
        if folder:
            video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
            files = []
            for root, dirs, filenames in os.walk(folder):
                for filename in filenames:
                    if Path(filename).suffix.lower() in video_extensions:
                        files.append(os.path.join(root, filename))
            
            if files:
                threading.Thread(target=self.add_videos_to_playlist, args=(files,), daemon=True).start()
            else:
                messagebox.showinfo("No Videos", "No video files found in the selected folder.")
    
    def add_videos_to_playlist(self, files):
        for filepath in files:
            metadata = self.extract_video_metadata(filepath)
            if metadata:
                self.playlist.append(metadata)
                self.after(0, self.update_playlist_ui)
        
        self.after(0, self.save_playlist_to_disk)
    
    def extract_video_metadata(self, filepath):
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                filepath
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            data = json.loads(result.stdout)
            
            duration = float(data.get('format', {}).get('duration', 0))
            
            video_stream = next((s for s in data.get('streams', []) if s['codec_type'] == 'video'), {})
            width = video_stream.get('width', 0)
            height = video_stream.get('height', 0)
            codec = video_stream.get('codec_name', 'unknown')
            
            title = Path(filepath).stem
            
            return {
                'filepath': filepath,
                'title': title,
                'duration': duration,
                'duration_str': self.format_duration(duration),
                'resolution': f"{width}x{height}" if width and height else "Unknown",
                'type': Path(filepath).suffix.upper()[1:],
                'codec': codec,
                'filesize': os.path.getsize(filepath)
            }
        except Exception as e:
            print(f"Error extracting metadata from {filepath}: {e}")
            return None
    
    def format_duration(self, seconds):
        if seconds <= 0:
            return "00:00:00"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def update_playlist_ui(self):
        self.playlist_tree.delete(*self.playlist_tree.get_children())
        
        for idx, video in enumerate(self.playlist, 1):
            self.playlist_tree.insert(
                '',
                'end',
                text=str(idx),
                values=(video['title'], video['duration_str'], video['type'])
            )
    
    def on_playlist_double_click(self, event):
        selection = self.playlist_tree.selection()
        if selection:
            item = selection[0]
            index = self.playlist_tree.index(item)
            self.play_video(index)
    
    def play_video(self, index):
        if 0 <= index < len(self.playlist):
            self.current_index = index
            video = self.playlist[index]
            
            self.info_label.config(text=f"Playing: {video['title']} ({video['duration_str']})")
            self.video_placeholder.config(text=f"Now Playing:\n{video['title']}\n\nExternal player launched")
            
            try:
                if os.name == 'nt':
                    os.startfile(video['filepath'])
                elif os.name == 'posix':
                    if sys.platform == 'darwin':
                        subprocess.Popen(['open', video['filepath']])
                    else:
                        subprocess.Popen(['xdg-open', video['filepath']])
                
                self.is_playing = True
                self.play_btn.config(text="⏸ Pause")
            except Exception as e:
                messagebox.showerror("Playback Error", f"Failed to play video:\n{str(e)}")
    
    def toggle_play(self):
        if self.current_index >= 0:
            if self.is_playing:
                self.is_playing = False
                self.play_btn.config(text="▶ Play")
            else:
                self.play_video(self.current_index)
        else:
            messagebox.showinfo("No Video", "Please select a video from the playlist first.")
    
    def previous_video(self):
        if self.current_index > 0:
            self.play_video(self.current_index - 1)
    
    def next_video(self):
        if self.current_index < len(self.playlist) - 1:
            self.play_video(self.current_index + 1)
    
    def capture_screenshot(self):
        if self.current_index < 0:
            messagebox.showinfo("No Video", "Please play a video first.")
            return
        
        video = self.playlist[self.current_index]
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_filename = f"screenshot_{timestamp}.jpg"
            screenshot_path = self.screenshots_dir / screenshot_filename
            
            cmd = [
                'ffmpeg',
                '-ss', '00:00:05',
                '-i', video['filepath'],
                '-vframes', '1',
                '-q:v', '2',
                str(screenshot_path)
            ]
            
            subprocess.run(cmd, capture_output=True, timeout=10)
            
            metadata = {
                'video': video['title'],
                'filepath': video['filepath'],
                'timestamp': timestamp,
                'screenshot': screenshot_filename,
                'resolution': video['resolution'],
                'duration': video['duration_str'],
                'capture_time': datetime.now().isoformat()
            }
            
            metadata_path = self.screenshots_dir / f"screenshot_{timestamp}.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            thumbnail_path = self.screenshots_dir / f"thumb_{timestamp}.jpg"
            img = Image.open(screenshot_path)
            img.thumbnail((320, 180))
            img.save(thumbnail_path, "JPEG", quality=85)
            
            messagebox.showinfo(
                "Screenshot Captured",
                f"Screenshot saved:\n{screenshot_filename}\n\nMetadata and thumbnail created."
            )
        except Exception as e:
            messagebox.showerror("Screenshot Error", f"Failed to capture screenshot:\n{str(e)}")
    
    def show_video_info(self):
        if self.current_index < 0:
            messagebox.showinfo("No Video", "Please select a video first.")
            return
        
        video = self.playlist[self.current_index]
        
        info_window = tk.Toplevel(self)
        info_window.title("Video Information")
        info_window.geometry("500x400")
        info_window.configure(bg='#1a1a2e')
        
        tk.Label(
            info_window,
            text="VIDEO INFORMATION",
            font=('Arial', 14, 'bold'),
            fg='#00ff88',
            bg='#1a1a2e'
        ).pack(pady=10)
        
        info_text = tk.Text(
            info_window,
            font=('Courier', 10),
            bg='#0f0f1e',
            fg='#cccccc',
            padx=20,
            pady=20,
            wrap=tk.WORD
        )
        info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_content = f"""Title: {video['title']}

Duration: {video['duration_str']}

Resolution: {video['resolution']}

File Type: {video['type']}

Codec: {video['codec']}

File Size: {video['filesize'] / 1024 / 1024:.2f} MB

File Path: {video['filepath']}
"""
        
        info_text.insert('1.0', info_content)
        info_text.config(state=tk.DISABLED)
        
        tk.Button(
            info_window,
            text="Close",
            command=info_window.destroy,
            bg='#00ff88',
            fg='#1a1a2e',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5
        ).pack(pady=10)
    
    def copy_selected(self):
        selection = self.playlist_tree.selection()
        if selection:
            self.clipboard_videos = []
            for item in selection:
                index = self.playlist_tree.index(item)
                self.clipboard_videos.append(self.playlist[index].copy())
            messagebox.showinfo("Copied", f"{len(self.clipboard_videos)} video(s) copied to clipboard.")
    
    def paste_videos(self):
        if self.clipboard_videos:
            for video in self.clipboard_videos:
                self.playlist.append(video)
            self.update_playlist_ui()
            self.save_playlist_to_disk()
            messagebox.showinfo("Pasted", f"{len(self.clipboard_videos)} video(s) pasted.")
    
    def delete_selected(self):
        selection = self.playlist_tree.selection()
        if selection:
            if messagebox.askyesno("Confirm Delete", f"Delete {len(selection)} video(s) from playlist?"):
                indices = [self.playlist_tree.index(item) for item in selection]
                for index in sorted(indices, reverse=True):
                    del self.playlist[index]
                self.update_playlist_ui()
                self.save_playlist_to_disk()
    
    def clear_all(self):
        if self.playlist:
            if messagebox.askyesno("Confirm Clear", "Clear entire playlist?"):
                self.playlist.clear()
                self.current_index = -1
                self.update_playlist_ui()
                self.save_playlist_to_disk()
    
    def generate_schedule(self):
        if not self.playlist:
            messagebox.showinfo("Empty Playlist", "Please add videos to the playlist first.")
            return
        
        schedule_window = tk.Toplevel(self)
        schedule_window.title("Generate Schedule")
        schedule_window.geometry("400x300")
        schedule_window.configure(bg='#1a1a2e')
        
        tk.Label(
            schedule_window,
            text="SCHEDULE GENERATOR",
            font=('Arial', 14, 'bold'),
            fg='#00ff88',
            bg='#1a1a2e'
        ).pack(pady=20)
        
        tk.Label(
            schedule_window,
            text="Start Time (HH:MM):",
            font=('Arial', 10),
            fg='white',
            bg='#1a1a2e'
        ).pack()
        
        start_time_var = tk.StringVar(value="08:00")
        tk.Entry(
            schedule_window,
            textvariable=start_time_var,
            font=('Arial', 12),
            justify='center',
            width=10
        ).pack(pady=5)
        
        tk.Label(
            schedule_window,
            text="Show Duration (minutes):",
            font=('Arial', 10),
            fg='white',
            bg='#1a1a2e'
        ).pack(pady=(20, 0))
        
        duration_var = tk.StringVar(value="30")
        tk.Entry(
            schedule_window,
            textvariable=duration_var,
            font=('Arial', 12),
            justify='center',
            width=10
        ).pack(pady=5)
        
        def create_schedule():
            try:
                hour, minute = map(int, start_time_var.get().split(':'))
                start = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
                show_duration = int(duration_var.get())
                
                self.schedule_data = []
                current_time = start
                
                for video in self.playlist:
                    video_duration_mins = int(video['duration'] / 60)
                    
                    self.schedule_data.append({
                        'time': current_time.strftime("%H:%M"),
                        'title': video['title'],
                        'duration': video['duration_str'],
                        'next_show': (current_time + timedelta(minutes=show_duration)).strftime("%H:%M")
                    })
                    
                    current_time += timedelta(minutes=show_duration)
                
                schedule_window.destroy()
                self.view_schedule()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input:\n{str(e)}")
        
        tk.Button(
            schedule_window,
            text="Generate",
            command=create_schedule,
            bg='#00ff88',
            fg='#1a1a2e',
            font=('Arial', 11, 'bold'),
            padx=30,
            pady=10
        ).pack(pady=30)
    
    def view_schedule(self):
        if not self.schedule_data:
            messagebox.showinfo("No Schedule", "Generate a schedule first.")
            return
        
        schedule_window = tk.Toplevel(self)
        schedule_window.title("Schedule View")
        schedule_window.geometry("700x600")
        schedule_window.configure(bg='#1a1a2e')
        
        tk.Label(
            schedule_window,
            text="VIDEO SCHEDULE",
            font=('Arial', 14, 'bold'),
            fg='#00ff88',
            bg='#1a1a2e'
        ).pack(pady=10)
        
        tree_frame = tk.Frame(schedule_window, bg='#1a1a2e')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        schedule_tree = ttk.Treeview(
            tree_frame,
            columns=('time', 'title', 'duration', 'next'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        schedule_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=schedule_tree.yview)
        
        schedule_tree.heading('time', text='Start Time')
        schedule_tree.heading('title', text='Title')
        schedule_tree.heading('duration', text='Duration')
        schedule_tree.heading('next', text='Next Show')
        
        schedule_tree.column('time', width=100)
        schedule_tree.column('title', width=300)
        schedule_tree.column('duration', width=100)
        schedule_tree.column('next', width=100)
        
        for item in self.schedule_data:
            schedule_tree.insert('', 'end', values=(
                item['time'],
                item['title'],
                item['duration'],
                item['next_show']
            ))
    
    def export_schedule(self):
        if not self.schedule_data:
            messagebox.showinfo("No Schedule", "Generate a schedule first.")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(self.schedule_data, f, indent=2)
            messagebox.showinfo("Exported", f"Schedule exported to:\n{filepath}")
    
    def save_playlist(self):
        if not self.playlist:
            messagebox.showinfo("Empty Playlist", "No playlist to save.")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(self.playlist, f, indent=2)
            messagebox.showinfo("Saved", f"Playlist saved to:\n{filepath}")
    
    def load_playlist(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    self.playlist = json.load(f)
                self.update_playlist_ui()
                messagebox.showinfo("Loaded", f"Playlist loaded from:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load playlist:\n{str(e)}")
    
    def save_playlist_to_disk(self):
        playlist_file = self.data_dir / "playlist.json"
        with open(playlist_file, 'w') as f:
            json.dump(self.playlist, f, indent=2)
    
    def load_playlist_from_disk(self):
        playlist_file = self.data_dir / "playlist.json"
        if playlist_file.exists():
            try:
                with open(playlist_file, 'r') as f:
                    self.playlist = json.load(f)
                self.update_playlist_ui()
            except:
                pass
    
    def import_files(self):
        """Import ANY file type - extracts URLs from any file"""
        choice = messagebox.askquestion(
            "Select Import Type",
            "Do you want to load individual files?\n\nYes = Select Files\nNo = Select Folder (scans subfolders)\nCancel = Abort",
            icon='question'
        )
        
        if choice == 'yes':
            files = filedialog.askopenfilenames(
                title="Select ANY Files to Import - URLs will be extracted",
                filetypes=[
                    ("All Files", "*.*")
                ]
            )
            
            if files:
                threading.Thread(target=self.process_import_files, args=(list(files),), daemon=True).start()
        elif choice == 'no':
            folder = filedialog.askdirectory(title="Select Folder to Import")
            if folder:
                threading.Thread(target=self.process_import_folder, args=(folder,), daemon=True).start()
    
    def process_import_files(self, files):
        """Process ANY file type - extracts URLs from all files"""
        all_videos = []
        
        for file_path in files:
            try:
                ext = os.path.splitext(file_path)[1].lower()
                
                # Try M3U parsing first
                if ext in {'.m3u', '.m3u8'}:
                    videos = self.parse_m3u_file(file_path)
                    all_videos.extend(videos)
                # Try media file detection
                elif self.is_media_file(file_path):
                    metadata = self.extract_video_metadata(file_path)
                    if metadata:
                        all_videos.append(metadata)
                # For ANY other file, try to extract URLs from it
                else:
                    videos = self.extract_urls_from_any_file(file_path)
                    all_videos.extend(videos)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        
        if not all_videos:
            self.after(0, lambda: messagebox.showwarning(
                "No Content Found",
                f"No channels or media files were found in the selected files/folders.\n\n"
                f"Supported file types:\n"
                f"• M3U Playlists (.m3u, .m3u8)\n"
                f"• Text Files with URLs (.txt)\n"
                f"• Video Files (.mp4, .mkv, .avi, .mov, .wmv, etc.)\n"
                f"• Audio Files (.mp3, .aac, .wav, .flac, .ogg, etc.)\n"
                f"• Folders (scans all subfolders for media and playlists)\n\n"
                f"Text files should contain URLs (one per line) or M3U format.\n\n"
                f"Files scanned: {len(files)}\n"
                f"The file(s) were accepted but no valid URLs or media were extracted."
            ))
            return
        
        self.playlist.extend(all_videos)
        self.after(0, self.update_playlist_ui)
        self.after(0, self.save_playlist_to_disk)
        self.after(0, lambda: messagebox.showinfo(
            "Import Complete",
            f"Loaded {len(all_videos)} item(s) from {len(files)} file(s)"
        ))
    
    def process_import_folder(self, folder):
        """Process folder import"""
        all_videos = self.scan_folder_for_media(folder)
        
        if not all_videos:
            self.after(0, lambda: messagebox.showwarning(
                "No Content Found",
                "No media files or playlists found in the selected folder.\n\n"
                "The folder will be scanned recursively for:\n"
                "• M3U Playlists (.m3u, .m3u8)\n"
                "• Text Files with URLs (.txt)\n"
                "• Video Files (.mp4, .mkv, .avi, .mov, .wmv, etc.)\n"
                "• Audio Files (.mp3, .aac, .wav, .flac, .ogg, etc.)"
            ))
            return
        
        self.playlist.extend(all_videos)
        self.after(0, self.update_playlist_ui)
        self.after(0, self.save_playlist_to_disk)
        self.after(0, lambda: messagebox.showinfo(
            "Import Complete",
            f"Loaded {len(all_videos)} videos from folder scan"
        ))
    
    def is_media_file(self, file_path):
        """Check if file is a video/audio file"""
        media_extensions = {
            '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v',
            '.mpg', '.mpeg', '.3gp', '.ts', '.m2ts', '.vob', '.ogv',
            '.mp3', '.aac', '.wav', '.flac', '.ogg', '.m4a', '.wma', '.opus',
            '.ape', '.alac', '.aiff'
        }
        ext = os.path.splitext(file_path)[1].lower()
        return ext in media_extensions
    
    def parse_m3u_file(self, file_path):
        """Parse M3U playlist file - supports standard #EXTINF and non-standard #EXTM variants"""
        videos = []
        current_video = None
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    lines = f.readlines()
            except Exception as e:
                print(f"Cannot read M3U file {file_path}: {e}")
                return []
        
        for line in lines:
            line = line.strip()
            
            if not line or line == "#EXTM3U" or line == "#EXTMM3U":
                continue
            
            # Accept both standard #EXTINF: and non-standard #EXTM:/#EXTMM: tags
            if line.startswith("#EXTINF:") or line.startswith("#EXTM:") or line.startswith("#EXTMM:"):
                name_part = line.split(',')[-1].strip()
                current_video = {
                    'title': name_part or "Unknown",
                    'filepath': '',
                    'duration': 0,
                    'duration_str': "00:00:00",
                    'type': 'STREAM',
                    'resolution': 'Unknown',
                    'codec': 'unknown',
                    'filesize': 0
                }
            elif not line.startswith("#"):
                if current_video:
                    current_video['filepath'] = line
                    current_video['url'] = line
                    
                    # Try to extract metadata if it's a local file
                    if os.path.exists(line):
                        metadata = self.extract_video_metadata(line)
                        if metadata:
                            current_video.update(metadata)
                    
                    videos.append(current_video)
                    current_video = None
        
        return videos
    
    def extract_urls_from_any_file(self, file_path):
        """Extract URLs from ANY file type - accepts everything"""
        videos = []
        
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            try:
                # Fallback to latin-1
                with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
                    content = f.read()
            except:
                try:
                    # Last resort: binary read and decode
                    with open(file_path, 'rb') as f:
                        content = f.read().decode('utf-8', errors='ignore')
                except Exception as e:
                    print(f"Cannot read file {file_path}: {e}")
                    return []
        
        # Extract ALL possible URLs (HTTP, HTTPS, RTMP, RTSP, file://, local paths)
        url_pattern = r'https?://[^\s<>"\'()]+|rtmp[st]?://[^\s<>"\'()]+|file://[^\s<>"\'()]+|[A-Za-z]:[/\\][^\s<>"\'()]+\.[a-zA-Z0-9]+'
        urls = re.findall(url_pattern, content)
        
        # Also try line-by-line for simple URLs
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and ('://' in line or line.endswith(('.mp4', '.mkv', '.avi', '.mov', '.m3u8', '.m3u', '.mp3', '.flac'))):
                if line not in urls:
                    urls.append(line)
        
        for idx, url in enumerate(urls, 1):
            url = url.strip()
            if not url:
                continue
            
            # Extract name from URL
            name = url.split('/')[-1]
            if '?' in name:
                name = name.split('?')[0]
            name = urllib.parse.unquote(name)
            
            video = {
                'title': name or f"Link {idx}",
                'filepath': url,
                'url': url,
                'duration': 0,
                'duration_str': "00:00:00",
                'resolution': "Unknown",
                'type': 'URL',
                'codec': 'unknown',
                'filesize': 0
            }
            videos.append(video)
        
        return videos
    
    def parse_txt_file(self, file_path):
        """Parse TXT file - wrapper for extract_urls_from_any_file"""
        return self.extract_urls_from_any_file(file_path)
    
    def scan_folder_for_media(self, folder_path):
        """Recursively scan folder for ANY files with URLs or media"""
        all_videos = []
        
        try:
            for root, dirs, files in os.walk(folder_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    ext = os.path.splitext(filename)[1].lower()
                    
                    try:
                        # M3U playlists
                        if ext in {'.m3u', '.m3u8'}:
                            videos = self.parse_m3u_file(file_path)
                            all_videos.extend(videos)
                        # Media files
                        elif self.is_media_file(file_path):
                            metadata = self.extract_video_metadata(file_path)
                            if metadata:
                                all_videos.append(metadata)
                        # Any other text-based file - try to extract URLs
                        elif ext in {'.txt', '.html', '.xml', '.json', '.log', '.ini', '.cfg', '.conf'}:
                            videos = self.extract_urls_from_any_file(file_path)
                            all_videos.extend(videos)
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")
                        continue
        except Exception as e:
            print(f"Error scanning folder {folder_path}: {e}")
        
        return all_videos
