#!/usr/bin/env python3
"""
Video Player Application - Main Launcher
A standalone GUI application for advanced video playback, scheduling, and management
"""

import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

class MainLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Video Player Pro")
        self.geometry("500x350")
        self.resizable(False, False)
        self.configure(bg='#1a1a2e')
        
        self.center_window()
        self.create_widgets()
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        title_frame = tk.Frame(self, bg='#1a1a2e')
        title_frame.pack(pady=40)
        
        title_label = tk.Label(
            title_frame,
            text="VIDEO PLAYER PRO",
            font=('Arial Black', 28, 'bold'),
            fg='#00ff88',
            bg='#1a1a2e'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Advanced Video Playback & Scheduling System",
            font=('Arial', 11),
            fg='#cccccc',
            bg='#1a1a2e'
        )
        subtitle_label.pack(pady=5)
        
        button_frame = tk.Frame(self, bg='#1a1a2e')
        button_frame.pack(pady=30)
        
        launch_btn = tk.Button(
            button_frame,
            text="LAUNCH PLAYER",
            font=('Arial', 14, 'bold'),
            bg='#00ff88',
            fg='#1a1a2e',
            activebackground='#00cc6a',
            activeforeground='#1a1a2e',
            relief=tk.FLAT,
            cursor='hand2',
            padx=40,
            pady=15,
            command=self.launch_player
        )
        launch_btn.pack()
        
        info_frame = tk.Frame(self, bg='#1a1a2e')
        info_frame.pack(side=tk.BOTTOM, pady=20)
        
        features = [
            "✓ Advanced Video Playback",
            "✓ Smart Scheduling System",
            "✓ Screenshot & Metadata Capture",
            "✓ Playlist Management"
        ]
        
        for feature in features:
            feature_label = tk.Label(
                info_frame,
                text=feature,
                font=('Arial', 9),
                fg='#888888',
                bg='#1a1a2e'
            )
            feature_label.pack(anchor='w')
    
    def launch_player(self):
        self.withdraw()
        
        try:
            from video_player_workbench import VideoPlayerWorkbench
            player = VideoPlayerWorkbench(self)
            player.protocol("WM_DELETE_WINDOW", lambda: self.on_player_close(player))
            player.mainloop()
        except Exception as e:
            self.show_error(f"Failed to launch player: {str(e)}")
            self.deiconify()
    
    def on_player_close(self, player):
        player.destroy()
        self.deiconify()
    
    def show_error(self, message):
        error_window = tk.Toplevel(self)
        error_window.title("Error")
        error_window.geometry("400x150")
        error_window.configure(bg='#1a1a2e')
        error_window.resizable(False, False)
        
        msg_label = tk.Label(
            error_window,
            text=message,
            font=('Arial', 10),
            fg='#ff4444',
            bg='#1a1a2e',
            wraplength=350
        )
        msg_label.pack(pady=30)
        
        ok_btn = tk.Button(
            error_window,
            text="OK",
            font=('Arial', 10),
            bg='#00ff88',
            fg='#1a1a2e',
            command=error_window.destroy,
            padx=20,
            pady=5
        )
        ok_btn.pack()

def main():
    app = MainLauncher()
    app.mainloop()

if __name__ == "__main__":
    main()
