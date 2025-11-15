"""
M3U MATRIX - Auto Updater
Checks for updates and downloads new versions
"""

import tkinter as tk
from tkinter import messagebox, ttk
import json
import requests
import shutil
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime
import subprocess
import sys

VERSION_FILE = "install_config.json"
GITHUB_API = "https://api.github.com/repos/YOUR_USERNAME/m3u-matrix/releases/latest"
VERIFICATION_KEY_FILE = "update_key.txt"

class AutoUpdater:
    def __init__(self, app_dir=None):
        self.app_dir = Path(app_dir) if app_dir else Path(__file__).parent.parent
        self.config_file = self.app_dir / VERSION_FILE
        
        self.current_version = self.get_current_version()
        
        self.root = tk.Tk()
        self.root.title("M3U Matrix - Auto Updater")
        self.root.geometry("600x400")
        self.root.configure(bg="#1a1a2a")
        
        self.setup_ui()
        
    def get_current_version(self):
        """Get current installed version"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return config.get('version', '1.0.0')
        except:
            return "1.0.0"
    
    def setup_ui(self):
        """Create updater UI"""
        # Header
        header = tk.Frame(self.root, bg="#6b46c1", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🔄 Auto Updater", 
                font=("Arial", 18, "bold"), bg="#6b46c1", fg="#fff").pack(pady=15)
        
        # Content
        content = tk.Frame(self.root, bg="#1a1a2a")
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Version info
        info_frame = tk.LabelFrame(content, text="Version Information",
                                   font=("Arial", 11, "bold"),
                                   bg="#2e2e4e", fg="#fff")
        info_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(info_frame, text=f"Current Version: {self.current_version}",
                font=("Arial", 10), bg="#2e2e4e", fg="#00f3ff").pack(anchor=tk.W, padx=20, pady=5)
        
        self.latest_label = tk.Label(info_frame, text="Latest Version: Checking...",
                                     font=("Arial", 10), bg="#2e2e4e", fg="#00f3ff")
        self.latest_label.pack(anchor=tk.W, padx=20, pady=5)
        
        # Status
        self.status_label = tk.Label(content, text="Ready to check for updates",
                                     font=("Arial", 10), bg="#1a1a2a", fg="#aaa")
        self.status_label.pack(pady=10)
        
        # Progress
        self.progress = ttk.Progressbar(content, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=10)
        
        # Changelog area
        changelog_frame = tk.LabelFrame(content, text="What's New",
                                       font=("Arial", 11, "bold"),
                                       bg="#2e2e4e", fg="#fff")
        changelog_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.changelog_text = tk.Text(changelog_frame, height=8, bg="#1a1a2a",
                                     fg="#fff", font=("Arial", 9), wrap=tk.WORD)
        self.changelog_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons
        button_frame = tk.Frame(content, bg="#1a1a2a")
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(button_frame, text="Check for Updates", command=self.check_updates,
                 bg="#3498db", fg="#fff", font=("Arial", 11, "bold"),
                 width=18).pack(side=tk.LEFT, padx=5)
        
        self.update_btn = tk.Button(button_frame, text="Download & Install", 
                                    command=self.download_update,
                                    bg="#2ecc71", fg="#fff", font=("Arial", 11, "bold"),
                                    width=18, state=tk.DISABLED)
        self.update_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Close", command=self.root.quit,
                 bg="#e74c3c", fg="#fff", font=("Arial", 11, "bold"),
                 width=18).pack(side=tk.LEFT, padx=5)
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        self.root.update()
    
    def verify_user(self):
        """Verify user has permission to update"""
        # Check for update key file
        key_file = self.app_dir / VERIFICATION_KEY_FILE
        
        if key_file.exists():
            try:
                with open(key_file, 'r') as f:
                    stored_key = f.read().strip()
            except:
                stored_key = None
        else:
            stored_key = None
        
        # Prompt for verification key
        from tkinter import simpledialog
        
        entered_key = simpledialog.askstring(
            "User Verification",
            "Enter update authorization key:\n\n"
            "(First time: set your own key)\n"
            "(Subsequent: enter your key)",
            show='*'
        )
        
        if not entered_key:
            return False
        
        # First time: set the key
        if not stored_key:
            confirm_key = simpledialog.askstring(
                "Confirm Key",
                "Confirm your authorization key:",
                show='*'
            )
            
            if entered_key == confirm_key:
                with open(key_file, 'w') as f:
                    f.write(hashlib.sha256(entered_key.encode()).hexdigest())
                messagebox.showinfo("Key Set", "Authorization key has been set successfully!")
                return True
            else:
                messagebox.showerror("Error", "Keys do not match!")
                return False
        
        # Verify against stored key
        entered_hash = hashlib.sha256(entered_key.encode()).hexdigest()
        if entered_hash == stored_key:
            return True
        else:
            messagebox.showerror("Access Denied", "Invalid authorization key!")
            return False
    
    def check_updates(self):
        """Check for available updates"""
        self.progress.start()
        self.update_status("Checking for updates...")
        
        try:
            # Try to get real GitHub releases
            try:
                response = requests.get(GITHUB_API, timeout=10)
                if response.status_code == 200:
                    release_data = response.json()
                    latest_version = release_data.get('tag_name', '').lstrip('v')
                    changelog = release_data.get('body', 'No changelog available')
                    self.download_url = release_data.get('zipball_url', '')
                else:
                    raise Exception("GitHub API not configured")
            except:
                # Fallback to demo data
                latest_version = "5.3.1"
                changelog = """Version 5.3.1 - Latest Release

✨ New Features:
- Improved thumbnail caching performance
- Enhanced error handling for remote URLs
- New batch processing capabilities

🐛 Bug Fixes:
- Fixed compact mode reset issue
- Improved FFmpeg integration stability
- Better memory management for large playlists

📝 Other Changes:
- Updated documentation
- Performance optimizations
- UI improvements

⚠️ Note: GitHub API not configured. Using demo data.
Set GITHUB_API in AUTO_UPDATER.py for real updates.
"""
                self.download_url = None
            
            self.latest_label.config(text=f"Latest Version: {latest_version}")
            self.changelog_text.delete(1.0, tk.END)
            self.changelog_text.insert(1.0, changelog)
            
            # Compare versions
            if self.compare_versions(latest_version, self.current_version) > 0:
                self.update_status("✅ New version available!")
                self.update_btn.config(state=tk.NORMAL)
                
                messagebox.showinfo(
                    "Update Available",
                    f"A new version is available!\n\n"
                    f"Current: {self.current_version}\n"
                    f"Latest: {latest_version}\n\n"
                    f"Click 'Download & Install' to update."
                )
            else:
                self.update_status("✅ You have the latest version")
                messagebox.showinfo("No Updates", "You are running the latest version!")
            
            self.progress.stop()
            
        except Exception as e:
            self.progress.stop()
            self.update_status(f"❌ Error checking for updates: {str(e)}")
            messagebox.showerror("Update Check Failed", str(e))
    
    def compare_versions(self, v1, v2):
        """Compare version strings (returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal)"""
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            p1 = v1_parts[i] if i < len(v1_parts) else 0
            p2 = v2_parts[i] if i < len(v2_parts) else 0
            
            if p1 > p2:
                return 1
            elif p1 < p2:
                return -1
        
        return 0
    
    def download_update(self):
        """Download and install update"""
        # Verify user first
        if not self.verify_user():
            return
        
        confirm = messagebox.askyesno(
            "Confirm Update",
            "This will download and install the update.\n\n"
            "A backup will be created automatically.\n"
            "The application will close and restart.\n\n"
            "Continue?"
        )
        
        if not confirm:
            return
        
        try:
            self.progress.start()
            
            # Create backup
            self.update_status("Creating backup...")
            backup_dir = self.app_dir.parent / f"M3U_Matrix_Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copytree(self.app_dir, backup_dir)
            
            if hasattr(self, 'download_url') and self.download_url:
                # Real download from GitHub
                self.update_status("Downloading update...")
                response = requests.get(self.download_url, stream=True, timeout=60)
                response.raise_for_status()
                
                # Save to temp file
                import tempfile
                temp_zip = Path(tempfile.gettempdir()) / "m3u_matrix_update.zip"
                
                with open(temp_zip, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Extract update
                self.update_status("Installing update...")
                with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                    zip_ref.extractall(self.app_dir.parent / "temp_update")
                
                # Move files
                temp_update = self.app_dir.parent / "temp_update"
                for item in temp_update.rglob('*'):
                    if item.is_file():
                        rel_path = item.relative_to(temp_update)
                        dest = self.app_dir / rel_path
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest)
                
                # Cleanup
                shutil.rmtree(temp_update)
                temp_zip.unlink()
                
                # Update config
                with open(self.config_file, 'r+') as f:
                    config = json.load(f)
                    config['last_update'] = datetime.now().isoformat()
                    f.seek(0)
                    json.dump(config, f, indent=2)
                    f.truncate()
                
                self.progress.stop()
                
                messagebox.showinfo(
                    "Update Complete",
                    f"Update installed successfully!\n\n"
                    f"Backup saved to:\n{backup_dir}\n\n"
                    f"Please restart the application."
                )
                
                self.root.quit()
                
            else:
                # Fallback: manual update instructions
                self.progress.stop()
                messagebox.showinfo(
                    "Manual Update Required",
                    "GitHub API not configured for automatic updates.\n\n"
                    "To enable automatic updates:\n"
                    "1. Upload project to GitHub\n"
                    "2. Create releases with version tags\n"
                    "3. Update GITHUB_API in AUTO_UPDATER.py\n\n"
                    "For now, manually update from:\n"
                    "- Network share\n"
                    "- USB stick\n"
                    "- Project repository\n\n"
                    f"Backup created: {backup_dir}"
                )
            
            self.update_status("Ready")
            
        except Exception as e:
            self.progress.stop()
            self.update_status(f"❌ Update failed: {str(e)}")
            messagebox.showerror("Update Failed", f"Failed to update:\n{str(e)}\n\nBackup available at:\n{backup_dir}")
    
    def run(self):
        """Run updater"""
        self.root.mainloop()


if __name__ == "__main__":
    updater = AutoUpdater()
    updater.run()
