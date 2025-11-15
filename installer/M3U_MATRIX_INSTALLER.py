"""
M3U MATRIX ALL-IN-ONE - Windows Installer
Professional installer with portable and full installation modes
"""

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import shutil
import json
import sys
import subprocess
from pathlib import Path
import hashlib
import requests
from datetime import datetime

VERSION = "5.3.0"
APP_NAME = "M3U Matrix ALL-IN-ONE"
GITHUB_REPO = "YOUR_GITHUB_USERNAME/m3u-matrix"  # Update with your repo
UPDATE_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

class M3UMatrixInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} - Installer v{VERSION}")
        self.root.geometry("700x600")
        self.root.configure(bg="#1a1a2a")
        self.root.resizable(False, False)
        
        self.install_mode = tk.StringVar(value="portable")
        self.install_path = tk.StringVar()
        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.create_start_menu = tk.BooleanVar(value=True)
        
        # Get source directory (where installer files are)
        if getattr(sys, 'frozen', False):
            self.source_dir = Path(sys._MEIPASS)
        else:
            self.source_dir = Path(__file__).parent.parent
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create installer UI"""
        # Header
        header = tk.Frame(self.root, bg="#6b46c1", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text=f"🎬 {APP_NAME}", 
                font=("Arial", 24, "bold"), bg="#6b46c1", fg="#fff").pack(pady=20)
        
        # Main content
        content = tk.Frame(self.root, bg="#1a1a2a")
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Version info
        tk.Label(content, text=f"Version {VERSION}", 
                font=("Arial", 10), bg="#1a1a2a", fg="#aaa").pack(anchor=tk.W)
        
        tk.Label(content, text="Complete IPTV Management & Streaming Platform", 
                font=("Arial", 11), bg="#1a1a2a", fg="#00f3ff").pack(anchor=tk.W, pady=(0, 20))
        
        # Installation mode selection
        mode_frame = tk.LabelFrame(content, text="Installation Mode", 
                                   font=("Arial", 12, "bold"),
                                   bg="#2e2e4e", fg="#fff", bd=2)
        mode_frame.pack(fill=tk.X, pady=10)
        
        modes = [
            ("portable", "🔹 Portable (USB Stick) - Run from anywhere, no installation required"),
            ("full", "🔹 Full Installation - Install to Program Files with shortcuts")
        ]
        
        for value, text in modes:
            rb = tk.Radiobutton(mode_frame, text=text, variable=self.install_mode,
                               value=value, font=("Arial", 10), bg="#2e2e4e", fg="#fff",
                               selectcolor="#6b46c1", activebackground="#2e2e4e",
                               activeforeground="#fff", command=self.mode_changed)
            rb.pack(anchor=tk.W, padx=20, pady=5)
        
        # Installation path
        path_frame = tk.LabelFrame(content, text="Installation Location", 
                                   font=("Arial", 12, "bold"),
                                   bg="#2e2e4e", fg="#fff", bd=2)
        path_frame.pack(fill=tk.X, pady=10)
        
        path_inner = tk.Frame(path_frame, bg="#2e2e4e")
        path_inner.pack(fill=tk.X, padx=20, pady=10)
        
        self.path_entry = tk.Entry(path_inner, textvariable=self.install_path,
                                   font=("Arial", 10), width=50)
        self.path_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(path_inner, text="Browse", command=self.browse_path,
                 bg="#6b46c1", fg="#fff", font=("Arial", 10)).pack(side=tk.LEFT)
        
        # Options
        options_frame = tk.LabelFrame(content, text="Additional Options", 
                                      font=("Arial", 12, "bold"),
                                      bg="#2e2e4e", fg="#fff", bd=2)
        options_frame.pack(fill=tk.X, pady=10)
        
        self.desktop_cb = tk.Checkbutton(options_frame, 
                                        text="Create Desktop Shortcut",
                                        variable=self.create_desktop_shortcut,
                                        font=("Arial", 10), bg="#2e2e4e", fg="#fff",
                                        selectcolor="#6b46c1", activebackground="#2e2e4e",
                                        activeforeground="#fff")
        self.desktop_cb.pack(anchor=tk.W, padx=20, pady=5)
        
        self.startmenu_cb = tk.Checkbutton(options_frame, 
                                          text="Create Start Menu Entry",
                                          variable=self.create_start_menu,
                                          font=("Arial", 10), bg="#2e2e4e", fg="#fff",
                                          selectcolor="#6b46c1", activebackground="#2e2e4e",
                                          activeforeground="#fff")
        self.startmenu_cb.pack(anchor=tk.W, padx=20, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(content, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=20)
        
        # Status label
        self.status_label = tk.Label(content, text="Ready to install", 
                                     font=("Arial", 10), bg="#1a1a2a", fg="#00f3ff")
        self.status_label.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(content, bg="#1a1a2a")
        button_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(button_frame, text="Install", command=self.install,
                 bg="#2ecc71", fg="#fff", font=("Arial", 12, "bold"),
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Check for Updates", command=self.check_updates,
                 bg="#3498db", fg="#fff", font=("Arial", 12, "bold"),
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Exit", command=self.root.quit,
                 bg="#e74c3c", fg="#fff", font=("Arial", 12, "bold"),
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        # Set default path
        self.mode_changed()
        
    def mode_changed(self):
        """Handle installation mode change"""
        if self.install_mode.get() == "portable":
            # Default to current directory for portable
            self.install_path.set(str(Path.cwd()))
            self.desktop_cb.config(state=tk.DISABLED)
            self.startmenu_cb.config(state=tk.DISABLED)
        else:
            # Default to Program Files for full install
            program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
            self.install_path.set(os.path.join(program_files, "M3U Matrix"))
            self.desktop_cb.config(state=tk.NORMAL)
            self.startmenu_cb.config(state=tk.NORMAL)
    
    def browse_path(self):
        """Browse for installation directory"""
        path = filedialog.askdirectory(initialdir=self.install_path.get())
        if path:
            self.install_path.set(path)
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        self.root.update()
    
    def install(self):
        """Perform installation"""
        install_dir = Path(self.install_path.get())
        
        if not install_dir.parent.exists():
            messagebox.showerror("Error", "Invalid installation path!")
            return
        
        # Confirm installation
        mode_text = "Portable Installation" if self.install_mode.get() == "portable" else "Full Installation"
        confirm = messagebox.askyesno(
            "Confirm Installation",
            f"{mode_text}\n\nInstall to: {install_dir}\n\nProceed?"
        )
        
        if not confirm:
            return
        
        try:
            self.progress.start()
            
            # Create installation directory
            self.update_status("Creating installation directory...")
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy files
            self.update_status("Copying application files...")
            self.copy_files(install_dir)
            
            # Create configuration
            self.update_status("Creating configuration...")
            self.create_config(install_dir)
            
            # Create shortcuts if full install
            if self.install_mode.get() == "full":
                if self.create_desktop_shortcut.get():
                    self.update_status("Creating desktop shortcut...")
                    self.create_shortcut("desktop", install_dir)
                
                if self.create_start_menu.get():
                    self.update_status("Creating start menu entry...")
                    self.create_shortcut("startmenu", install_dir)
            
            # Create portable marker if portable mode
            if self.install_mode.get() == "portable":
                (install_dir / "PORTABLE_MODE.txt").write_text(
                    "This is a portable installation. You can move this folder anywhere."
                )
            
            self.progress.stop()
            self.update_status("Installation complete!")
            
            messagebox.showinfo(
                "Success",
                f"{APP_NAME} has been installed successfully!\n\n"
                f"Location: {install_dir}\n\n"
                f"Run: {install_dir / 'M3U_MATRIX_PRO.py'}"
            )
            
        except Exception as e:
            self.progress.stop()
            self.update_status("Installation failed!")
            messagebox.showerror("Installation Error", f"Failed to install:\n{e}")
    
    def copy_files(self, dest_dir):
        """Copy application files to destination"""
        # List of files/folders to copy
        items_to_copy = [
            "src",
            "templates",
            "Sample Playlists",
            "M3U_MATRIX_README.md",
            "QUICK_START_GUIDE.txt",
            "THUMBNAIL_CACHING_GUIDE.md",
            "HYBRID_MODE_GUIDE.md",
            "START_WEB_SERVER.py",
            "START_WEB_SERVER.bat",
            "requirements.txt"
        ]
        
        for item in items_to_copy:
            source = self.source_dir / item
            if source.exists():
                dest = dest_dir / item
                if source.is_file():
                    shutil.copy2(source, dest)
                else:
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(source, dest)
        
        # Create necessary directories
        for dirname in ["logs", "exports", "backups", "thumbnails", 
                       "epg_data", "temp", "generated_pages"]:
            (dest_dir / dirname).mkdir(exist_ok=True)
    
    def create_config(self, install_dir):
        """Create installation configuration"""
        config = {
            "version": VERSION,
            "install_date": datetime.now().isoformat(),
            "install_mode": self.install_mode.get(),
            "install_path": str(install_dir),
            "auto_update": True
        }
        
        config_file = install_dir / "install_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def create_shortcut(self, location, install_dir):
        """Create Windows shortcut"""
        try:
            import win32com.client
            
            shell = win32com.client.Dispatch("WScript.Shell")
            
            if location == "desktop":
                shortcut_path = Path(shell.SpecialFolders("Desktop")) / f"{APP_NAME}.lnk"
            else:  # start menu
                programs = Path(shell.SpecialFolders("Programs"))
                app_folder = programs / APP_NAME
                app_folder.mkdir(exist_ok=True)
                shortcut_path = app_folder / f"{APP_NAME}.lnk"
            
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.TargetPath = sys.executable if getattr(sys, 'frozen', False) else "python.exe"
            shortcut.Arguments = str(install_dir / "src" / "M3U_MATRIX_PRO.py")
            shortcut.WorkingDirectory = str(install_dir)
            shortcut.IconLocation = str(install_dir / "src" / "M3U_MATRIX_PRO.py")
            shortcut.Description = APP_NAME
            shortcut.save()
            
        except ImportError:
            # Fallback: create batch file
            if location == "desktop":
                batch_path = Path.home() / "Desktop" / f"{APP_NAME}.bat"
            else:
                batch_path = install_dir / f"{APP_NAME}.bat"
            
            batch_content = f"""@echo off
cd /d "{install_dir}"
python src\\M3U_MATRIX_PRO.py
pause
"""
            batch_path.write_text(batch_content)
    
    def check_updates(self):
        """Check for updates from GitHub"""
        try:
            self.update_status("Checking for updates...")
            
            # For now, show a message
            # In production, this would check GitHub releases
            messagebox.showinfo(
                "Updates",
                f"Current version: {VERSION}\n\n"
                "To enable auto-updates:\n"
                "1. Upload project to GitHub\n"
                "2. Update GITHUB_REPO in installer\n"
                "3. Create releases with version tags"
            )
            
            self.update_status("Ready to install")
            
        except Exception as e:
            messagebox.showerror("Update Check Failed", str(e))
    
    def run(self):
        """Run installer"""
        self.root.mainloop()


if __name__ == "__main__":
    installer = M3UMatrixInstaller()
    installer.run()
