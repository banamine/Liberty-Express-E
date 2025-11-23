
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
import argparse

# Calculate project root and add to sys.path
# M3U_MATRIX_PRO.py is in src/videos/, so go up 2 levels to project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

# Add src directory to sys.path for imports
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Define resource paths
TEMPLATES_DIR = PROJECT_ROOT / "templates"
DATA_DIR = SRC_DIR / "data"

# Optional imports - only needed for advanced features
try:
    # Try to fix paths for packaged executable FIRST
    if getattr(sys, 'frozen', False):
        # Running as packaged executable - use fixed paths
        from page_generator_fix import fix_page_generator_paths, get_output_directory
        fixed_module = fix_page_generator_paths()
        if fixed_module:
            NexusTVPageGenerator = fixed_module.NexusTVPageGenerator
            WebIPTVGenerator = fixed_module.WebIPTVGenerator
            SimplePlayerGenerator = fixed_module.SimplePlayerGenerator
            RumbleChannelGenerator = fixed_module.RumbleChannelGenerator
            MultiChannelGenerator = fixed_module.MultiChannelGenerator
            BufferTVGenerator = fixed_module.BufferTVGenerator
            PAGE_GENERATOR_AVAILABLE = True
            print("Page generators loaded with executable path fixes")
        else:
            raise ImportError("Could not apply path fixes")
    else:
        # Running as Python script - normal import
        from page_generator import NexusTVPageGenerator, WebIPTVGenerator, SimplePlayerGenerator, RumbleChannelGenerator, MultiChannelGenerator, BufferTVGenerator
        PAGE_GENERATOR_AVAILABLE = True
        print("Page generators loaded (development mode)")
        
        # Create helper function for development using OutputManager
        def get_output_directory(subfolder=""):
            try:
                from output_manager import get_output_manager
                manager = get_output_manager()
                if subfolder:
                    return manager.get_page_output_dir(subfolder)
                else:
                    return manager.pages_dir
            except ImportError:
                # Fallback if OutputManager not available
                output_dir = Path("M3U_Matrix_Output") / "generated_pages"
                if subfolder:
                    output_dir = output_dir / subfolder
                output_dir.mkdir(exist_ok=True, parents=True)
                return output_dir
            
except ImportError as e:
    PAGE_GENERATOR_AVAILABLE = False
    logging.warning(f"Page generator not available: {e}")
    
    # Fallback helper using OutputManager
    def get_output_directory(subfolder=""):
        try:
            from output_manager import get_output_manager
            manager = get_output_manager()
            if subfolder:
                return manager.get_page_output_dir(subfolder)
            else:
                return manager.pages_dir
        except ImportError:
            # Fallback if OutputManager not available
            output_dir = Path("M3U_Matrix_Output") / "generated_pages"
            if subfolder:
                output_dir = output_dir / subfolder
            output_dir.mkdir(exist_ok=True, parents=True)
            return output_dir

try:
    from utils import (sanitize_filename, validate_url, validate_file_path, 
                       sanitize_input, SimpleCache, is_valid_m3u, 
                       download_and_cache_thumbnail, get_cached_thumbnail_stats)
    UTILS_AVAILABLE = True
except ImportError as e:
    UTILS_AVAILABLE = False
    logging.warning(f"Utils module not available: {e}")

# NDI Output import
try:
    from ndi_output import get_ndi_manager
    NDI_AVAILABLE = True
except ImportError as e:
    NDI_AVAILABLE = False
    logging.info(f"NDI output module not available: {e}")
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

    def __init__(self, headless=False):
        self.headless = headless
        self.root = None  # Will be initialized only in GUI mode
        
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
        self.open_windows = []  # Track all open Toplevel windows for smooth cleanup

        self.setup_error_handling()
        self.load_settings()
        
        # Initialize GUI only in non-headless mode
        if not self.headless:
            self.root = TkinterDnD.Tk()
            self.root.title(
                "M3U MATRIX PRO • DRAG & DROP M3U FILES • DOUBLE-CLICK TO OPEN")
            self.root.geometry("1600x950")
            self.root.minsize(1300, 800)
            self.root.configure(bg="#121212")
            
            self.build_ui()
            self.load_tv_guide()
            self.start_autosave()
            self.logger.info("M3U Matrix started successfully (GUI mode)")
            self.root.mainloop()
        else:
            # Headless mode: initialize only core systems
            self.load_tv_guide()
            self.start_autosave()
            self.logger.info("M3U Matrix started successfully (Headless mode)")

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
    
    # ========== SMART BUTTON COLOR SYSTEM ==========
    
    @staticmethod
    def get_contrasting_text_color(bg_color):
        """Calculate if text should be dark or light based on background brightness
        
        Args:
            bg_color: Hex color string (e.g., '#F2E1C1')
            
        Returns:
            '#000000' for dark text or '#FFFFFF' for light text
        """
        # Handle common color names
        color_map = {
            'red': '#FF0000',
            'green': '#00FF00',
            'blue': '#0000FF',
            'yellow': '#FFFF00',
            'purple': '#800080',
            'orange': '#FFA500',
            'pink': '#FFC0CB',
            'brown': '#A52A2A',
            'gray': '#808080',
            'black': '#000000',
            'white': '#FFFFFF'
        }
        
        if bg_color.lower() in color_map:
            bg_color = color_map[bg_color.lower()]
        
        # Convert hex to RGB
        if bg_color.startswith('#'):
            try:
                r = int(bg_color[1:3], 16)
                g = int(bg_color[3:5], 16)
                b = int(bg_color[5:7], 16)
            except (ValueError, IndexError):
                return "#000000"  # Default to black on error
        else:
            return "#000000"  # Default to black for invalid input
        
        # Calculate luminance (perceived brightness)
        # Using ITU-R BT.709 coefficients for better accuracy
        luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
        
        # Return dark text for bright backgrounds, light text for dark backgrounds
        return "#000000" if luminance > 0.5 else "#FFFFFF"
    
    def create_styled_button(self, parent, text, command, bg_color="#F2E1C1", width=15, 
                            font_size=10, font_weight="bold"):
        """Create a button with smart text color and consistent styling
        
        Args:
            parent: Parent widget
            text: Button text
            command: Button command/callback
            bg_color: Background color (hex or name)
            width: Button width
            font_size: Font size
            font_weight: Font weight (normal/bold)
            
        Returns:
            tk.Button with smart styling
        """
        fg_color = self.get_contrasting_text_color(bg_color)
        
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=fg_color,
            font=("Arial", font_size, font_weight),
            width=width,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
            activebackground=bg_color,
            activeforeground=fg_color
        )
        
        # Add hover effect (slightly darker on hover)
        def on_enter(e):
            button.configure(relief=tk.RAISED, bd=3)
        
        def on_leave(e):
            button.configure(relief=tk.RAISED, bd=2)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button

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
    
    def configure_output_folder(self):
        """Configure the base output folder for all exports"""
        try:
            from output_manager import get_output_manager
            manager = get_output_manager()
            
            # Create dialog window
            dialog = tk.Toplevel(self.root)
            dialog.title("Configure Output Folder")
            dialog.geometry("600x300")
            dialog.configure(bg="#1e1e1e")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            # Title label
            tk.Label(dialog, text="Configure Output Directory", 
                    font=("Arial", 14, "bold"),
                    bg="#1e1e1e", fg="gold").pack(pady=10)
            
            # Current location label
            current_label = tk.Label(dialog, 
                                   text=f"Current Location: {manager.base_path}",
                                   font=("Arial", 10),
                                   bg="#1e1e1e", fg="white", wraplength=550)
            current_label.pack(pady=10)
            
            # Folder structure info
            info_frame = tk.Frame(dialog, bg="#2e2e2e")
            info_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
            
            info_text = tk.Text(info_frame, height=8, width=70,
                              bg="#2e2e2e", fg="#aaa",
                              font=("Consolas", 9))
            info_text.pack(padx=10, pady=10)
            
            # Show folder structure
            folder_info = """📁 M3U_Matrix_Output/
  ├── 📁 generated_pages/    # HTML player pages
  ├── 📁 playlists/          # M3U playlist files
  ├── 📁 json_data/          # JSON exports & metadata
  ├── 📁 thumbnails/         # Channel & video thumbnails
  ├── 📁 screenshots/        # Video screenshots
  ├── 📁 saves/              # Application save states
  └── 📁 backups/            # Automatic backups"""
            
            info_text.insert("1.0", folder_info)
            info_text.config(state=tk.DISABLED)
            
            # Button frame
            btn_frame = tk.Frame(dialog, bg="#1e1e1e")
            btn_frame.pack(pady=10)
            
            def change_location():
                new_dir = filedialog.askdirectory(
                    title="Select Base Output Directory",
                    initialdir=str(Path.home())
                )
                if new_dir:
                    # Update settings
                    self.settings['output_base_dir'] = new_dir
                    self.save_settings()
                    
                    # Update OutputManager
                    manager.base_path = Path(new_dir)
                    manager._create_directories()
                    
                    current_label.config(text=f"Current Location: {new_dir}")
                    messagebox.showinfo("Success", 
                                      f"Output folder changed to:\n{new_dir}\n\n" +
                                      "New files will be saved to this location.")
            
            def reset_default():
                # Reset to default
                if 'output_base_dir' in self.settings:
                    del self.settings['output_base_dir']
                    self.save_settings()
                
                # Reset OutputManager to default
                manager.base_path = Path("M3U_Matrix_Output")
                manager._create_directories()
                
                current_label.config(text=f"Current Location: {manager.base_path}")
                messagebox.showinfo("Reset", 
                                  "Output folder reset to default:\nM3U_Matrix_Output")
            
            tk.Button(btn_frame, text="📂 Change Location",
                     command=change_location,
                     bg="#2980b9", fg="white",
                     font=("Arial", 10, "bold"),
                     width=20).pack(side=tk.LEFT, padx=5)
            
            tk.Button(btn_frame, text="↺ Reset to Default",
                     command=reset_default,
                     bg="#e67e22", fg="white",
                     font=("Arial", 10, "bold"),
                     width=20).pack(side=tk.LEFT, padx=5)
            
            tk.Button(btn_frame, text="✓ Close",
                     command=dialog.destroy,
                     bg="#27ae60", fg="white",
                     font=("Arial", 10, "bold"),
                     width=15).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            self.show_error_dialog("Configuration Error", 
                                 "Could not configure output folder", e)

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
                ("NEW", "#34495e", self.new_project),
                ("THUMBS", "#ff9500", self.open_thumbnails_folder),
                ("VIDEO", "#00d4ff", self.launch_video_player),
                ("NAV HUB", "#FFD700", self.open_navigation_hub)]
        for txt, col, cmd in row1:
            self.create_styled_button(tb1, txt, cmd, bg_color=col, width=10, font_size=9).pack(side=tk.LEFT, padx=2)
        
        # ROW 2: Processing & Generation
        tb2 = tk.Frame(toolbar_container, bg="#1e1e1e")
        tb2.pack(fill=tk.X, pady=2)
        row2 = [("ORGANIZE", "#27ae60", self.organize_channels),
                ("CHECK", "#e67e22", self.start_check),
                ("GENERATE PAGES", "#e91e63", self.generate_pages),
                ("MULTI-CHANNEL", "#1e90ff", self.generate_multi_channel),
                ("RUMBLE BROWSER", "#FF6347", self.open_rumble_browser),
                ("RUMBLE CHANNEL", "#FF4500", self.generate_rumble_channel),
                ("BUFFER TV", "#DC143C", self.generate_buffer_tv),
                ("STREAM HUB", "#00d4ff", self.generate_stream_hub),
                ("STANDALONE", "#9400D3", self.generate_standalone_secure),
                ("SMART SCHEDULE", "#9b59b6", self.smart_scheduler),
                ("JSON GUIDE", "#95e1d3", self.export_tv_guide_json),
                ("🔴 NDI", "#FF0000", self.open_ndi_control)]
        for txt, col, cmd in row2:
            self.create_styled_button(tb2, txt, cmd, bg_color=col, width=10, font_size=9).pack(side=tk.LEFT, padx=2)
        
        # ROW 3: Import & Advanced
        tb3 = tk.Frame(toolbar_container, bg="#1e1e1e")
        tb3.pack(fill=tk.X, pady=2)
        row3 = [("URL IMPORT", "#4ecdc4", self.url_import_workbench),
                ("IMPORT URL", "#8e44ad", self.import_url),
                ("BULK EDITOR", "#2ecc71", self.open_bulk_editor),
                ("VERSION CTRL", "#3498db", self.open_version_control),
                ("TIMESTAMP GEN", "#ff6b6b", self.timestamp_generator),
                ("FETCH EPG", "#d35400", self.fetch_epg),
                ("TV GUIDE", "#9b59b6", self.open_guide),
                ("MEDIA STRIPPER", "#ff00ff", self.open_media_stripper),
                ("LAUNCH REDIS", "#FF5733", self.launch_redis_services)]
        for txt, col, cmd in row3:
            self.create_styled_button(tb3, txt, cmd, bg_color=col, width=10, font_size=9).pack(side=tk.LEFT, padx=2)

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
        
        # Settings menu with smart colors
        self.create_styled_button(tools, "📋 Documentation", self.open_documentation,
                                  bg_color="#27ae60", width=12, font_size=8).pack(side=tk.RIGHT, padx=2)
        self.create_styled_button(tools, "📁 Output Folder", self.configure_output_folder,
                                  bg_color="#8b4789", width=12, font_size=8).pack(side=tk.RIGHT, padx=2)
        self.create_styled_button(tools, "⚙️ Export Settings", self.export_settings,
                                  bg_color="#34495e", width=12, font_size=8).pack(side=tk.RIGHT, padx=2)
        self.create_styled_button(tools, "⚙️ Import Settings", self.import_settings,
                                  bg_color="#34495e", width=12, font_size=8).pack(side=tk.RIGHT, padx=2)
        
        # Edit buttons with smart colors
        for txt, col, cmd in [("CUT", "#e74c3c", self.cut),
                              ("COPY", "#3498db", self.copy),
                              ("PASTE", "#2ecc71", self.paste),
                              ("UNDO", "#f39c12", self.undo),
                              ("REDO", "#9b59b6", self.redo)]:
            self.create_styled_button(tools, txt, cmd, bg_color=col, width=8, font_size=8).pack(side=tk.LEFT, padx=2)

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
        
        # KEYBOARD SHORTCUTS for Copy/Paste
        self.tv.bind("<Control-c>", lambda e: self.copy())
        self.tv.bind("<Control-v>", lambda e: self.paste())
        self.tv.bind("<Control-x>", lambda e: self.cut())

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
        """Paste clipboard channels at current selection"""
        if not self.clipboard:
            messagebox.showwarning("Empty Clipboard",
                                   "Cut or copy channels first!")
            return
        
        self.save_state(f"Paste {len(self.clipboard['channels'])} channels")
        self.mark_changed()

        # Determine insertion index from current selection
        selection = self.tv.selection()
        if selection:
            # Insert after the last selected item
            last_selected_index = max(self.tv.index(iid) for iid in selection)
            insert_index = last_selected_index + 1
        else:
            # No selection, append to end
            insert_index = len(self.channels)

        if self.clipboard["operation"] == "cut":
            # Remove original channels when pasting a cut
            for channel in self.clipboard["channels"]:
                self.channels = [
                    c for c in self.channels if c["num"] != channel["num"]
                ]
            # Adjust insert index if we removed items before it
            if selection:
                insert_index = min(insert_index, len(self.channels))

        # Insert clipboard channels at the determined position
        for i, channel in enumerate(self.clipboard["channels"]):
            new_channel = channel.copy()
            if self.clipboard["operation"] == "copy":
                new_channel["num"] = max([c["num"] for c in self.channels],
                                         default=0) + i + 1
            self.channels.insert(insert_index + i, new_channel)

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

    # ========== RUMBLE URL DETECTION & OEMBED ==========
    def detect_rumble_url(self, url):
        """Detect if URL is a Rumble video and extract video ID + publisher code"""
        if not url or 'rumble.com' not in url.lower():
            return None
        
        # Pattern 1: Embed URL: https://rumble.com/embed/v6zldbc/?pub=15son
        embed_match = re.search(r'rumble\.com/embed/(v[a-zA-Z0-9]+)/?\?pub=([a-zA-Z0-9]+)', url)
        if embed_match:
            return {
                'video_id': embed_match.group(1),
                'pub_code': embed_match.group(2),
                'embed_url': url  # Preserve full URL with query params
            }
        
        # Pattern 2: Watch URL: https://rumble.com/v6zldbc-title.html or https://rumble.com/watch/v6zldbc
        watch_match = re.search(r'rumble\.com/(?:watch/)?(v[a-zA-Z0-9]+)', url)
        if watch_match:
            video_id = watch_match.group(1)
            # Try to fetch pub code from oEmbed
            return {
                'video_id': video_id,
                'pub_code': None,  # Will be fetched from oEmbed
                'embed_url': None  # Will be constructed or fetched
            }
        
        return None
    
    def fetch_rumble_metadata(self, url):
        """Fetch Rumble video metadata using oEmbed API"""
        try:
            oembed_url = f"https://rumble.com/api/Media/oembed.json?url={urllib.parse.quote(url)}"
            response = requests.get(oembed_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract embed URL from HTML
                html = data.get('html', '')
                embed_match = re.search(r'src=["\']([^"\']+)["\']', html)
                embed_url = embed_match.group(1) if embed_match else None
                
                # Extract video ID and pub code from embed URL
                video_info = self.detect_rumble_url(embed_url) if embed_url else {}
                
                return {
                    'title': data.get('title', 'Rumble Video'),
                    'thumbnail': data.get('thumbnail_url', ''),
                    'width': data.get('width', 640),
                    'height': data.get('height', 360),
                    'embed_url': embed_url,
                    'video_id': video_info.get('video_id') if video_info else None,
                    'pub_code': video_info.get('pub_code') if video_info else None,
                    'provider': 'Rumble'
                }
        except Exception as e:
            logging.warning(f"Failed to fetch Rumble oEmbed for {url}: {e}")
        
        # Fallback: try to extract from URL directly
        video_info = self.detect_rumble_url(url)
        if video_info:
            return {
                'title': f"Rumble Video {video_info['video_id']}",
                'thumbnail': '',
                'width': 640,
                'height': 360,
                'embed_url': video_info.get('embed_url'),
                'video_id': video_info['video_id'],
                'pub_code': video_info.get('pub_code'),
                'provider': 'Rumble'
            }
        
        return None

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

            if not line or line == "#EXTM3U" or line == "#EXTMM3U":
                i += 1
                continue

            if line.startswith("#EXTINF") or line.startswith("#EXTM:") or line.startswith("#EXTMM:"):
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

            # Accept any non-comment line after #EXTINF as a URL/path
            if current_channel and not line.startswith("#"):
                current_channel["url"] = line.strip()
                current_channel["custom_tags"] = custom_tags.copy()
                
                # Detect and enrich Rumble URLs
                rumble_info = self.detect_rumble_url(current_channel["url"])
                if rumble_info:
                    # Mark as Rumble channel
                    current_channel["custom_tags"]["PROVIDER"] = "RUMBLE"
                    current_channel["custom_tags"]["VIDEO_ID"] = rumble_info.get('video_id', '')
                    current_channel["custom_tags"]["PUB_CODE"] = rumble_info.get('pub_code', '')
                    
                    # Fetch metadata from oEmbed API
                    rumble_meta = self.fetch_rumble_metadata(current_channel["url"])
                    if rumble_meta:
                        # Update channel with Rumble metadata
                        if not current_channel.get("name") or current_channel["name"] == "Unknown":
                            current_channel["name"] = rumble_meta['title']
                        if not current_channel.get("logo"):
                            current_channel["logo"] = rumble_meta.get('thumbnail', '')
                        current_channel["custom_tags"]["EMBED_URL"] = rumble_meta.get('embed_url', '')
                        current_channel["custom_tags"]["WIDTH"] = str(rumble_meta.get('width', 640))
                        current_channel["custom_tags"]["HEIGHT"] = str(rumble_meta.get('height', 360))
                
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
        """Parse EXTINF/EXTM line with support for various attributes"""
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

        # Extract name - works for both #EXTINF: and #EXTM: formats
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

    def parse_txt_file(self, file_path):
        """Parse TXT file containing URLs (one per line) or extract links from any text"""
        channels = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception as e:
                self.logger.error(f"Cannot read TXT file {file_path}: {e}")
                return []
        
        # Extract all URLs from the content
        url_pattern = r'https?://[^\s<>"\']+|rtmp://[^\s<>"\']+|rtsp://[^\s<>"\']+|file://[^\s<>"\']+|/[^\s<>"\']+\.[a-zA-Z0-9]+'
        urls = re.findall(url_pattern, content)
        
        # Create channels from found URLs
        for idx, url in enumerate(urls, 1):
            url = url.strip()
            if not url:
                continue
            
            # Try to extract a meaningful name from the URL
            name = url.split('/')[-1]
            if '?' in name:
                name = name.split('?')[0]
            name = urllib.parse.unquote(name) if hasattr(urllib.parse, 'unquote') else name
            
            channel = {
                "name": name or f"Link {idx}",
                "group": "Imported Links",
                "logo": "",
                "tvg_id": "",
                "num": 0,
                "url": url,
                "backups": []
            }
            channels.append(channel)
        
        self.logger.info(f"Extracted {len(channels)} links from {os.path.basename(file_path)}")
        return channels
    
    def scan_folder_for_media(self, folder_path):
        """Recursively scan folder for media files and playlists"""
        all_channels = []
        supported_playlist_exts = {'.m3u', '.m3u8', '.txt'}
        
        try:
            for root, dirs, files in os.walk(folder_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    ext = os.path.splitext(filename)[1].lower()
                    
                    try:
                        # Check if it's a playlist file
                        if ext in supported_playlist_exts:
                            if ext == '.txt':
                                channels = self.parse_txt_file(file_path)
                            else:
                                channels = self.parse_m3u_file(file_path)
                            all_channels.extend(channels)
                            self.logger.info(f"Found {len(channels)} channels in {filename}")
                        
                        # Check if it's a media file
                        elif self.is_media_file(file_path):
                            channel = self.create_channel_from_media_file(file_path)
                            channel.setdefault("num", 0)
                            channel.setdefault("backups", [])
                            all_channels.append(channel)
                            self.logger.info(f"Found media file: {filename}")
                    
                    except Exception as e:
                        self.logger.error(f"Error processing {filename}: {e}")
                        continue
        
        except Exception as e:
            self.logger.error(f"Error scanning folder {folder_path}: {e}")
        
        return all_channels

    # ========== SMART SCHEDULER FOR TV PROGRAMMING ==========
    def create_smart_schedule(self, channels, show_duration=30, num_days=7, max_consecutive=3):
        """
        Create a 7-day, 24-hour TV schedule with global randomization
        
        Args:
            channels: List of channel dictionaries
            show_duration: Default duration in minutes for shows without duration metadata
            num_days: Number of days to schedule (default 7)
            max_consecutive: Maximum consecutive episodes from same show
        
        Returns:
            List of scheduled items with start times
        """
        import random
        from datetime import datetime, timedelta
        
        # Make a copy and globally randomize
        shuffled_channels = channels.copy()
        random.shuffle(shuffled_channels)
        
        schedule = []
        current_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = current_time + timedelta(days=num_days)
        
        # Track what played each day to prevent daily repeats
        daily_played = {day: set() for day in range(num_days)}
        
        channel_index = 0
        consecutive_count = 0
        last_show_name = None
        
        while current_time < end_time:
            # Get current day
            day_num = (current_time - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).days
            
            # Try to find next channel that hasn't played today
            attempts = 0
            selected_channel = None
            
            while attempts < len(shuffled_channels):
                candidate = shuffled_channels[channel_index % len(shuffled_channels)]
                channel_id = candidate.get('uuid', candidate.get('url', ''))
                
                # Check if this channel played today
                if channel_id not in daily_played[day_num]:
                    # Check consecutive limit
                    current_show_name = self.extract_show_name(candidate.get('name', ''))
                    if current_show_name != last_show_name:
                        consecutive_count = 0
                    
                    if consecutive_count < max_consecutive:
                        selected_channel = candidate
                        break
                
                channel_index += 1
                attempts += 1
            
            # If we couldn't find one (all played today), just pick next in rotation
            if not selected_channel:
                selected_channel = shuffled_channels[channel_index % len(shuffled_channels)]
                channel_index += 1
            
            # Get duration (use metadata or default)
            duration_minutes = show_duration
            if 'duration' in selected_channel:
                try:
                    duration_minutes = int(selected_channel['duration'])
                except:
                    pass
            
            # Add to schedule
            schedule_item = {
                **selected_channel,
                'scheduled_start': current_time.isoformat(),
                'scheduled_duration': duration_minutes
            }
            schedule.append(schedule_item)
            
            # Mark as played today
            channel_id = selected_channel.get('uuid', selected_channel.get('url', ''))
            daily_played[day_num].add(channel_id)
            
            # Update tracking
            current_show_name = self.extract_show_name(selected_channel.get('name', ''))
            if current_show_name == last_show_name:
                consecutive_count += 1
            else:
                consecutive_count = 1
                last_show_name = current_show_name
            
            # Move to next time slot
            current_time += timedelta(minutes=duration_minutes)
            channel_index += 1
        
        return schedule
    
    def extract_show_name(self, channel_name):
        """Extract show name from channel name (removes episode info)"""
        import re
        # Remove common episode patterns
        patterns = [
            r'[Ss]\d+[Ee]\d+',  # S01E01
            r'Season\s+\d+',     # Season 1
            r'Episode\s+\d+',    # Episode 1
            r'\d+x\d+',          # 1x01
            r'\(\d{4}\)',        # (2020)
        ]
        
        name = channel_name
        for pattern in patterns:
            name = re.sub(pattern, '', name)
        
        # Clean up extra spaces and special chars
        name = re.sub(r'\s+', ' ', name).strip()
        name = re.sub(r'[_\-\.]+$', '', name).strip()
        
        return name
    
    def show_scheduler_dialog(self, callback):
        """Show scheduler configuration dialog before NEXUS TV generation"""
        scheduler_dialog = tk.Toplevel(self.root)
        scheduler_dialog.title("Smart TV Scheduler")
        scheduler_dialog.geometry("500x500")
        scheduler_dialog.configure(bg="#1a1a2e")
        scheduler_dialog.transient(self.root)
        scheduler_dialog.grab_set()
        
        # Title
        tk.Label(
            scheduler_dialog,
            text="📺 Smart TV Scheduler",
            font=("Segoe UI", 18, "bold"),
            bg="#1a1a2e",
            fg="#00ff88"
        ).pack(pady=20)
        
        tk.Label(
            scheduler_dialog,
            text="Create a 7-day TV schedule with randomized programming",
            font=("Segoe UI", 10),
            bg="#1a1a2e",
            fg="#aaaaaa"
        ).pack(pady=(0, 30))
        
        # Settings frame
        settings_frame = tk.Frame(scheduler_dialog, bg="#1a1a2e")
        settings_frame.pack(pady=20, padx=40, fill=tk.X)
        
        # Show Duration
        duration_frame = tk.Frame(settings_frame, bg="#1a1a2e")
        duration_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            duration_frame,
            text="Show Duration (minutes):",
            font=("Segoe UI", 11),
            bg="#1a1a2e",
            fg="#ffffff"
        ).pack(side=tk.LEFT)
        
        duration_var = tk.IntVar(value=30)
        duration_spin = tk.Spinbox(
            duration_frame,
            from_=5,
            to=180,
            textvariable=duration_var,
            width=10,
            font=("Segoe UI", 11),
            bg="#2a2a2a",
            fg="#ffffff",
            buttonbackground="#00ff88"
        )
        duration_spin.pack(side=tk.RIGHT)
        
        # Number of Days
        days_frame = tk.Frame(settings_frame, bg="#1a1a2e")
        days_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            days_frame,
            text="Number of Days:",
            font=("Segoe UI", 11),
            bg="#1a1a2e",
            fg="#ffffff"
        ).pack(side=tk.LEFT)
        
        days_var = tk.IntVar(value=7)
        days_spin = tk.Spinbox(
            days_frame,
            from_=1,
            to=30,
            textvariable=days_var,
            width=10,
            font=("Segoe UI", 11),
            bg="#2a2a2a",
            fg="#ffffff",
            buttonbackground="#00ff88"
        )
        days_spin.pack(side=tk.RIGHT)
        
        # Max Consecutive Shows
        consecutive_frame = tk.Frame(settings_frame, bg="#1a1a2e")
        consecutive_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            consecutive_frame,
            text="Max Consecutive Shows:",
            font=("Segoe UI", 11),
            bg="#1a1a2e",
            fg="#ffffff"
        ).pack(side=tk.LEFT)
        
        consecutive_var = tk.IntVar(value=3)
        consecutive_spin = tk.Spinbox(
            consecutive_frame,
            from_=1,
            to=10,
            textvariable=consecutive_var,
            width=10,
            font=("Segoe UI", 11),
            bg="#2a2a2a",
            fg="#ffffff",
            buttonbackground="#00ff88"
        )
        consecutive_spin.pack(side=tk.RIGHT)
        
        # Info text
        info_text = (
            "This will create a randomized TV schedule with:\n"
            "• Global shuffling of all content\n"
            "• No repeats within the same day\n"
            "• Sequential playback with set durations\n"
            "• Limit on consecutive episodes"
        )
        
        tk.Label(
            scheduler_dialog,
            text=info_text,
            font=("Segoe UI", 9),
            bg="#1a1a2e",
            fg="#888888",
            justify=tk.LEFT
        ).pack(pady=20, padx=40)
        
        # Buttons frame
        buttons_frame = tk.Frame(scheduler_dialog, bg="#1a1a2e")
        buttons_frame.pack(pady=20)
        
        def on_create_schedule():
            params = {
                'show_duration': duration_var.get(),
                'num_days': days_var.get(),
                'max_consecutive': consecutive_var.get()
            }
            scheduler_dialog.destroy()
            callback(params)
        
        def on_skip():
            scheduler_dialog.destroy()
            callback(None)  # None means skip scheduling
        
        tk.Button(
            buttons_frame,
            text="CREATE SCHEDULE",
            bg="#00ff88",
            fg="#000000",
            font=("Segoe UI", 11, "bold"),
            command=on_create_schedule,
            cursor="hand2",
            width=18
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="SKIP",
            bg="#555555",
            fg="#ffffff",
            font=("Segoe UI", 11),
            command=on_skip,
            cursor="hand2",
            width=10
        ).pack(side=tk.LEFT, padx=5)

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
        
        # Use OutputManager for organized exports
        try:
            from output_manager import get_output_manager
            manager = get_output_manager()
            exports_dir = manager.json_data_dir
        except:
            exports_dir = Path("M3U_Matrix_Output") / "json_data"
            exports_dir.mkdir(exist_ok=True, parents=True)
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialdir=str(exports_dir),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
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
        # Ask user if they want to load files or a folder
        response = messagebox.askyesnocancel(
            "Select Import Type",
            "Do you want to load individual files?\n\n"
            "Yes = Select Files\n"
            "No = Select Folder (scans subfolders)\n"
            "Cancel = Abort"
        )
        
        if response is None:  # Cancel
            return
        
        if response:  # Yes - load files
            f = filedialog.askopenfilenames(
                filetypes=[
                    ("All Playlists", "*.m3u *.m3u8 *.txt"),
                    ("M3U Files", "*.m3u *.m3u8"),
                    ("Text Files", "*.txt"),
                    ("All Files", "*.*")
                ]
            )
            if not f:
                return
            files_to_process = f
            is_folder = False
        else:  # No - load folder
            folder = filedialog.askdirectory(title="Select Folder to Scan")
            if not folder:
                return
            files_to_process = [folder]
            is_folder = True
        
        # Return early if no selection
        if not files_to_process:
            return
        
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
        
        if is_folder:
            # Scan folder for all media and playlist files
            status_label.config(text=f"Scanning folder: {os.path.basename(files_to_process[0])}")
            progress['value'] = 10
            progress_win.update()
            
            all_channels = self.scan_folder_for_media(files_to_process[0])
            
            progress['value'] = 50
            progress_win.update()
            
            # Update file list to show folder
            self.files.append(files_to_process[0])
            self.file_list.delete(0, tk.END)
            for ff in self.files:
                self.file_list.insert(tk.END, os.path.basename(ff) if os.path.isfile(ff) else f"[Folder] {os.path.basename(ff)}")
        else:
            # Process individual files
            total_files = len(files_to_process)
            
            for idx, file_path in enumerate(files_to_process, 1):
                status_label.config(text=f"Reading file {idx}/{total_files}: {os.path.basename(file_path)}")
                progress['value'] = (idx / total_files) * 50  # First 50% for parsing
                progress_win.update()
                
                try:
                    ext = os.path.splitext(file_path)[1].lower()
                    
                    # Check if this is a TXT file
                    if ext == '.txt':
                        channels = self.parse_txt_file(file_path)
                        all_channels.extend(channels)
                        self.logger.info(f"Extracted {len(channels)} links from TXT: {os.path.basename(file_path)}")
                    # Check if this is a media file
                    elif self.is_media_file(file_path):
                        channel = self.create_channel_from_media_file(file_path)
                        channel.setdefault("num", 0)
                        channel.setdefault("backups", [])
                        channel["uuid"] = str(uuid.uuid4())
                        all_channels.append(channel)
                        self.logger.info(f"Created channel from media file: {os.path.basename(file_path)}")
                    # Parse as M3U playlist
                    else:
                        channels = self.parse_m3u_file(file_path)
                        for ch in channels:
                            ch.setdefault("num", 0)
                            ch.setdefault("backups", [])
                            if "uuid" not in ch:
                                ch["uuid"] = str(uuid.uuid4())
                        all_channels.extend(channels)
                        self.logger.info(f"Parsed {len(channels)} channels from M3U: {os.path.basename(file_path)}")
                except Exception as e:
                    self.logger.error(f"Failed to process {file_path}: {e}")
                    status_label.config(text=f"Error reading {os.path.basename(file_path)}")
                    progress_win.update()
                    continue
            
            # Update file list
            self.files.extend(files_to_process)
            self.file_list.delete(0, tk.END)
            for ff in self.files:
                self.file_list.insert(tk.END, os.path.basename(ff))
        
        # Check if we got any channels
        if not all_channels:
            progress_win.destroy()
            messagebox.showwarning(
                "No Content Found",
                "No channels or media files were found in the selected files/folder.\n\n"
                "Supported file types:\n"
                "• M3U Playlists (.m3u, .m3u8)\n"
                "• Text Files with URLs (.txt)\n"
                "• Video Files (.mp4, .mkv, .avi, .mov, .wmv, etc.)\n"
                "• Audio Files (.mp3, .aac, .wav, .flac, .ogg, etc.)\n"
                "• Folders (scans all subfolders for media and playlists)\n\n"
                "Text files should contain URLs (one per line) or M3U format."
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
        # Use OutputManager for organized saves
        try:
            from output_manager import get_output_manager
            manager = get_output_manager()
            default_dir = manager.playlists_dir
        except:
            default_dir = Path("M3U_Matrix_Output") / "playlists"
            default_dir.mkdir(exist_ok=True, parents=True)
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".m3u",
            initialdir=str(default_dir),
            filetypes=[("M3U files", "*.m3u"), ("M3U8 files", "*.m3u8"), ("All files", "*.*")],
            initialfile=f"MATRIX_{datetime.now().strftime('%Y%m%d')}_{len(self.channels)}.m3u"
        )

        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.m3u)
            self.mark_clean()  # Clear unsaved changes flag
            messagebox.showinfo(
                "Saved", f"Playlist saved with {len(self.channels)} channels")
            self.stat.config(text=f"SAVED: {os.path.basename(filename)}")

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
    
    def open_thumbnails_folder(self):
        """Open the thumbnails folder in file explorer"""
        thumb_folder = os.path.join(os.getcwd(), "generated_pages")
        
        if not os.path.exists(thumb_folder):
            messagebox.showinfo(
                "No Thumbnails Yet",
                "No generated pages found.\n\n"
                "Thumbnails are created when you:\n"
                "• Generate NEXUS TV pages\n"
                "• Generate Web IPTV pages\n"
                "• Generate Simple Player pages\n\n"
                "Use 'GENERATE PAGES' to create pages with thumbnails."
            )
            return
        
        try:
            if sys.platform == 'win32':
                os.startfile(thumb_folder)
            elif sys.platform == 'darwin':
                subprocess.run(['open', thumb_folder])
            else:
                subprocess.run(['xdg-open', thumb_folder])
            self.stat.config(text=f"Opened: {thumb_folder}")
        except Exception as e:
            self.show_error_dialog("Cannot Open Folder", f"Failed to open thumbnails folder:\n{thumb_folder}", e)
    
    def launch_video_player(self):
        """Launch Video Player Pro application - works from any location"""
        try:
            # Get the directory containing this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Try multiple possible locations for video_player_app
            possible_paths = [
                # Same directory as script (for deployment)
                os.path.join(script_dir, "video_player_app", "run_player.py"),
                # Parent directory (if in src/videos/)
                os.path.join(script_dir, "..", "video_player_app", "run_player.py"),
                # Root of project (if in nested structure)
                os.path.join(script_dir, "..", "..", "video_player_app", "run_player.py"),
                # Sibling to script (alt deployment)
                os.path.join(os.path.dirname(script_dir), "video_player_app", "run_player.py")
            ]
            
            video_player_path = None
            for path in possible_paths:
                normalized_path = os.path.normpath(path)
                if os.path.exists(normalized_path):
                    video_player_path = normalized_path
                    break
            
            if not video_player_path:
                messagebox.showerror(
                    "Video Player Not Found",
                    "Video Player Pro not found!\n\n"
                    f"Searched in:\n{script_dir}\n\n"
                    "Please ensure video_player_app folder is in the same directory as M3U_MATRIX_PRO.py"
                )
                return
            
            # Launch Video Player Pro
            subprocess.Popen([sys.executable, video_player_path])
            self.stat.config(text=f"Launched Video Player Pro from {os.path.dirname(video_player_path)}")
        except Exception as e:
            self.show_error_dialog("Launch Failed", "Could not launch Video Player Pro", e)
    
    def open_navigation_hub(self):
        """Open the Navigation Hub page in default browser"""
        try:
            # Use OutputManager to get the correct hub path
            try:
                from output_manager import get_output_manager
                manager = get_output_manager()
                hub_path = manager.pages_dir / "index.html"
            except ImportError:
                # Fallback to M3U_Matrix_Output structure
                hub_path = Path.cwd() / "M3U_Matrix_Output" / "generated_pages" / "index.html"
            
            # Check if hub exists
            if not hub_path.exists():
                messagebox.showwarning(
                    "Navigation Hub Not Found",
                    "Navigation Hub not found!\n\n"
                    "The hub page will be created automatically when you generate your first player page.\n\n"
                    f"Expected location:\n{hub_path}"
                )
                return
            
            # Open in default browser using absolute path
            abs_path = hub_path.absolute()
            webbrowser.open(f"file:///{abs_path}")
            self.stat.config(text="Navigation Hub opened in browser")
        except Exception as e:
            self.show_error_dialog("Failed to Open Hub", "Could not open Navigation Hub", e)
    
    def open_documentation(self):
        """Open the File Browser Documentation page"""
        try:
            # Use OutputManager to get the correct documentation path
            try:
                from output_manager import get_output_manager
                manager = get_output_manager()
                doc_path = manager.pages_dir / "FILE_BROWSER_README.html"
            except ImportError:
                # Fallback to M3U_Matrix_Output structure
                doc_path = Path.cwd() / "M3U_Matrix_Output" / "generated_pages" / "FILE_BROWSER_README.html"
            
            # Check if documentation exists
            if not doc_path.exists():
                messagebox.showwarning(
                    "Documentation Not Found",
                    "FILE_BROWSER_README.html not found!\n\n"
                    "The documentation will be created when you generate your first page.\n\n"
                    f"Expected location:\n{doc_path}"
                )
                return
            
            # Open in default browser
            abs_path = doc_path.absolute()
            webbrowser.open(f"file:///{abs_path}")
            self.stat.config(text="Documentation opened in browser")
        except Exception as e:
            self.show_error_dialog("Failed to Open Documentation", "Could not open File Browser", e)

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
        redis_dir = PROJECT_ROOT / "redis"
        
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
        """Generate ALL 3 player pages automatically"""
        if not PAGE_GENERATOR_AVAILABLE:
            messagebox.showwarning("Feature Unavailable", 
                "Page generator not available.\n\n"
                "Download the full project from GitHub to use this feature.")
            return
            
        if not self.channels:
            messagebox.showwarning("No Channels", "Load channels first!")
            return

        # Show scheduler dialog - works for all pages now
        def on_scheduler_callback(scheduler_params):
            self._generate_all_three_pages(scheduler_params)
        
        self.show_scheduler_dialog(on_scheduler_callback)

    def open_rumble_browser(self):
        """Open the Rumble Category Browser for discovering and importing channels"""
        try:
            # Import RumbleCategory Browser
            import sys
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
            from ui.rumble_category_browser import RumbleCategoryBrowser
            
            # Create browser with import callback
            def on_import(channel):
                self._import_rumble_channel_from_browser(channel)
            
            browser = RumbleCategoryBrowser(self.root, on_channel_import=on_import)
            
        except Exception as e:
            messagebox.showerror(
                "Error Opening Rumble Browser",
                f"Failed to open Rumble Browser:\n{str(e)}\n\n"
                "Please check that the browser component is installed correctly."
            )
            self.logger.error(f"Error opening Rumble Browser: {e}", exc_info=True)
    
    def open_media_stripper(self):
        """Open Private Media Stripper to extract links from any website"""
        try:
            from stripper import strip_site
            
            # Create input dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("🎬 Private Media Stripper")
            dialog.geometry("600x400")
            dialog.configure(bg="#1a1a2e")
            dialog.transient(self.root)
            
            # Center window
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - 300
            y = (dialog.winfo_screenheight() // 2) - 200
            dialog.geometry(f"+{x}+{y}")
            
            # Header
            tk.Label(dialog, text="🎬 PRIVATE MEDIA STRIPPER", 
                    font=("Arial", 16, "bold"), bg="#1a1a2e", 
                    fg="#ff00ff").pack(pady=15)
            
            tk.Label(dialog, text="Extract videos/audio/streams from any website\n100% Private • No Logging • Offline Ready",
                    font=("Arial", 10), bg="#1a1a2e", fg="#fff").pack(pady=10)
            
            # URL Input
            tk.Label(dialog, text="Website URL:", bg="#1a1a2e", fg="#fff").pack(anchor=tk.W, padx=20)
            url_entry = tk.Entry(dialog, bg="#333", fg="#fff", width=50, insertbackground="#fff")
            url_entry.pack(padx=20, pady=5, fill=tk.X)
            
            # Progress area
            tk.Label(dialog, text="Progress:", bg="#1a1a2e", fg="#fff").pack(anchor=tk.W, padx=20, pady=(20, 5))
            progress_text = tk.Text(dialog, bg="#111", fg="#0f0", height=8, font=("Courier", 9))
            progress_text.pack(padx=20, fill=tk.BOTH, expand=True, pady=5)
            
            def on_strip_click():
                url = url_entry.get().strip()
                if not url:
                    messagebox.showwarning("No URL", "Please enter a website URL")
                    return
                
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                # Disable button and lock entry
                strip_btn.config(state=tk.DISABLED)
                url_entry.config(state=tk.DISABLED)
                progress_text.config(state=tk.NORMAL)
                progress_text.delete("1.0", tk.END)
                
                def progress_callback(msg):
                    progress_text.insert(tk.END, msg + "\n")
                    progress_text.see(tk.END)
                    dialog.update_idletasks()
                
                def strip_thread():
                    try:
                        result = strip_site(url, progress_callback=progress_callback)
                        
                        if result.get('master_path'):
                            progress_text.insert(tk.END, f"\n✓ SUCCESS!\n")
                            progress_text.insert(tk.END, f"Found: {result['found']} media links\n")
                            progress_text.insert(tk.END, f"Subtitles: {result['subtitles']}\n")
                            progress_text.insert(tk.END, f"Saved to: {result['master_path']}\n")
                            
                            # Show completion with open folder option
                            self.root.after(0, lambda: self._show_stripper_success(result, dialog))
                        else:
                            progress_text.insert(tk.END, f"\n✗ FAILED!\n{result.get('error', 'Unknown error')}\n")
                    except Exception as e:
                        progress_text.insert(tk.END, f"\n✗ ERROR: {str(e)}\n")
                        self.logger.error(f"Media Stripper error: {e}", exc_info=True)
                    finally:
                        self.root.after(0, lambda: (
                            strip_btn.config(state=tk.NORMAL),
                            url_entry.config(state=tk.NORMAL)
                        ))
                        progress_text.config(state=tk.DISABLED)
                
                threading.Thread(target=strip_thread, daemon=True).start()
            
            # Buttons
            btn_frame = tk.Frame(dialog, bg="#1a1a2e")
            btn_frame.pack(pady=10, fill=tk.X, padx=20)
            
            strip_btn = tk.Button(btn_frame, text="🚀 STRIP MEDIA", bg="#ff00ff", fg="#fff",
                                 command=on_strip_click, font=("Arial", 11, "bold"))
            strip_btn.pack(side=tk.LEFT, padx=5)
            
            tk.Button(btn_frame, text="✕ Close", bg="#666", fg="#fff",
                     command=dialog.destroy, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
            
            url_entry.focus()
            
        except ImportError:
            messagebox.showerror(
                "Media Stripper Not Available",
                "Media Stripper module (stripper.py) not found.\n\n"
                "Please ensure stripper.py is in src/videos/ directory."
            )
            self.logger.error("stripper module not available")
        except Exception as e:
            messagebox.showerror("Media Stripper Error", f"Failed to open Media Stripper:\n{str(e)}")
            self.logger.error(f"Media Stripper error: {e}", exc_info=True)
    
    def _show_stripper_success(self, result, dialog):
        """Show success dialog for media stripper"""
        success_msg = (
            f"✓ Media Stripper Complete!\n\n"
            f"Found: {result['found']} media links\n"
            f"Subtitles saved: {result['subtitles']}\n\n"
            f"Output folder: {os.path.dirname(result['master_path'])}\n\n"
            f"Your playlist is ready to use in VLC, MPC-HC, or any player!"
        )
        
        result_dialog = messagebox.showinfo(
            "Media Stripper Success",
            success_msg
        )
        
        # Option to open folder
        if messagebox.askyesno("Open Folder", "Open output folder?"):
            try:
                import subprocess, platform
                folder = os.path.dirname(result['master_path'])
                if platform.system() == 'Darwin':  # macOS
                    subprocess.Popen(['open', folder])
                elif platform.system() == 'Windows':
                    os.startfile(folder)
                else:  # Linux
                    subprocess.Popen(['xdg-open', folder])
            except Exception as e:
                self.logger.warning(f"Could not open folder: {e}")
    
    def open_ndi_control(self):
        """Open NDI Control Center for managing NDI outputs"""
        if not NDI_AVAILABLE:
            messagebox.showinfo(
                "NDI Not Available",
                "NDI output module is not available.\n\n"
                "Please ensure NDI Tools are installed and\n"
                "the NDI output module is properly configured."
            )
            return
        
        try:
            ndi_manager = get_ndi_manager()
            
            # Create NDI Control Window
            ndi_window = tk.Toplevel(self.root)
            ndi_window.title("NDI Output Control Center")
            ndi_window.geometry("800x600")
            ndi_window.configure(bg="#1a1a2e")
            ndi_window.transient(self.root)
            
            # Center the window
            ndi_window.update_idletasks()
            x = (ndi_window.winfo_screenwidth() // 2) - 400
            y = (ndi_window.winfo_screenheight() // 2) - 300
            ndi_window.geometry(f"+{x}+{y}")
            
            # Header
            header = tk.Label(
                ndi_window,
                text="🔴 NDI OUTPUT CONTROL CENTER",
                font=("Arial", 18, "bold"),
                bg="#1a1a2e",
                fg="#ff0000"
            )
            header.pack(pady=20)
            
            # Info label
            info_label = tk.Label(
                ndi_window,
                text="Network Device Interface - Professional Broadcast Output",
                font=("Arial", 11),
                bg="#1a1a2e",
                fg="#cccccc"
            )
            info_label.pack(pady=(0, 20))
            
            # Control Frame
            control_frame = tk.Frame(ndi_window, bg="#2a2a3e")
            control_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
            
            # Channel List Frame
            list_frame = tk.Frame(control_frame, bg="#2a2a3e")
            list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            tk.Label(
                list_frame,
                text="Active Channels:",
                font=("Arial", 12, "bold"),
                bg="#2a2a3e",
                fg="#00ff88"
            ).pack(anchor="w", pady=(0, 10))
            
            # Channel Listbox
            channel_listbox = tk.Listbox(
                list_frame,
                bg="#1a1a2e",
                fg="#ffffff",
                font=("Courier", 10),
                selectmode=tk.SINGLE,
                height=10
            )
            channel_listbox.pack(fill=tk.BOTH, expand=True)
            
            # Populate with current channels
            for i, channel in enumerate(self.channels[:20], 1):  # Show first 20 channels
                channel_name = channel.get('name', f'Channel {i}')
                channel_listbox.insert(tk.END, f"{i:3d}. {channel_name}")
            
            # NDI Control Buttons
            button_frame = tk.Frame(control_frame, bg="#2a2a3e")
            button_frame.pack(fill=tk.X, padx=10, pady=10)
            
            def start_ndi_for_channel():
                selection = channel_listbox.curselection()
                if not selection:
                    messagebox.showwarning("No Selection", "Please select a channel first")
                    return
                
                idx = selection[0]
                if idx < len(self.channels):
                    channel = self.channels[idx]
                    url = channel.get('url', '')
                    name = channel.get('name', f'Channel_{idx+1}')
                    
                    # Start NDI stream
                    success = ndi_manager.create_stream(
                        channel_name=name,
                        source_url=url,
                        resolution=(1920, 1080),
                        framerate=30
                    )
                    
                    if success:
                        messagebox.showinfo("NDI Started", f"NDI output started for:\n{name}")
                        update_status()
                    else:
                        messagebox.showerror("NDI Error", f"Failed to start NDI for:\n{name}")
            
            def stop_all_ndi():
                ndi_manager.stop_all_streams()
                messagebox.showinfo("NDI Stopped", "All NDI streams stopped")
                update_status()
            
            tk.Button(
                button_frame,
                text="▶ Start NDI Output",
                command=start_ndi_for_channel,
                bg="#00ff88",
                fg="#1a1a2e",
                font=("Arial", 10, "bold"),
                width=20,
                pady=5
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                button_frame,
                text="⏹ Stop All NDI",
                command=stop_all_ndi,
                bg="#ff3333",
                fg="#ffffff",
                font=("Arial", 10, "bold"),
                width=20,
                pady=5
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                button_frame,
                text="📹 Open Video Player",
                command=self.launch_video_player,
                bg="#00d4ff",
                fg="#1a1a2e",
                font=("Arial", 10, "bold"),
                width=20,
                pady=5
            ).pack(side=tk.LEFT, padx=5)
            
            # Status Display
            status_frame = tk.Frame(ndi_window, bg="#2a2a3e")
            status_frame.pack(fill=tk.BOTH, padx=20, pady=(0, 20))
            
            tk.Label(
                status_frame,
                text="NDI Status:",
                font=("Arial", 12, "bold"),
                bg="#2a2a3e",
                fg="#00ff88"
            ).pack(anchor="w", pady=(10, 5))
            
            status_text = tk.Text(
                status_frame,
                height=6,
                bg="#1a1a2e",
                fg="#cccccc",
                font=("Courier", 9),
                wrap=tk.WORD
            )
            status_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            def update_status():
                status_text.delete('1.0', tk.END)
                status_list = ndi_manager.get_all_status()
                
                if status_list:
                    for status in status_list:
                        status_info = (
                            f"📡 {status['source_name']}\n"
                            f"   Status: {'🟢 Active' if status['is_active'] else '🔴 Inactive'}\n"
                            f"   Resolution: {status['resolution']} @ {status['framerate']}fps\n"
                            f"   Bandwidth: {status['bandwidth_mbps']} Mbps\n\n"
                        )
                        status_text.insert(tk.END, status_info)
                else:
                    status_text.insert('1.0', "No active NDI streams\n\n"
                                             "Select a channel and click 'Start NDI Output'\n"
                                             "to begin broadcasting via NDI.")
            
            # Initial status update
            update_status()
            
            # Auto-refresh status
            def auto_refresh():
                if ndi_window.winfo_exists():
                    update_status()
                    ndi_window.after(2000, auto_refresh)
            
            auto_refresh()
            
            # Close button
            tk.Button(
                ndi_window,
                text="✖ Close",
                command=ndi_window.destroy,
                bg="#333333",
                fg="#ffffff",
                font=("Arial", 10, "bold"),
                width=15,
                pady=5
            ).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror(
                "NDI Control Error",
                f"Failed to open NDI Control Center:\n{str(e)}"
            )
            self.logger.error(f"Error opening NDI Control: {e}", exc_info=True)
    
    def _import_rumble_channel_from_browser(self, channel):
        """
        Import a Rumble channel reference from the browser into the playlist
        
        NOTE: This imports CHANNEL pages (e.g., rumble.com/c/RedPill78), not individual videos.
        These are reference links to browse the channel's content on Rumble.
        For individual video imports, use the regular M3U import with video URLs.
        
        Args:
            channel: Channel dict from rumble_channels.json
            
        Returns:
            bool: True if import successful, False otherwise
        """
        try:
            # Build channel URL from database
            handle = channel.get('handle', '')
            channel_url = channel.get('channel_url', f"https://rumble.com/c/{handle}")
            
            # Store channel metadata from database
            # Note: These are channel page URLs, not playable video URLs
            # RumbleHelper enrichment doesn't apply to channel references
            enriched_data = {
                'PROVIDER': 'RUMBLE',
                'TYPE': 'CHANNEL_REF',  # Channel reference for browsing, not playable video
                'HANDLE': handle,
                'PUB_CODE': channel.get('pub_code', ''),
                'CHANNEL_ID': channel.get('channel_id', ''),
                'DESCRIPTION': channel.get('description', ''),
                'CATEGORY': channel.get('category', '')
            }
            
            # Create channel entry for playlist
            new_channel = {
                'num': len(self.channels) + 1,
                'name': channel.get('name', 'Unknown Channel'),
                'group': channel.get('category', 'Rumble'),
                'url': channel_url,
                'logo': '',
                'backups': [],
                'uuid': str(uuid.uuid4()),
                'custom_tags': enriched_data
            }
            
            # Add to channels list
            self.channels.append(new_channel)
            
            # Mark as dirty for autosave
            self.dirty = True
            self.autosave_counter += 1
            
            # Rebuild M3U and refresh UI
            self.build_m3u()
            self.fill()
            
            # Update status
            self.stat.config(
                text=f"✓ Imported Rumble channel: {new_channel['name']}"
            )
            
            self.logger.info(f"Imported Rumble channel from browser: {new_channel['name']}")
            
            return True
            
        except Exception as e:
            messagebox.showerror(
                "Import Error",
                f"Failed to import channel:\n{str(e)}"
            )
            self.logger.error(f"Error importing Rumble channel: {e}", exc_info=True)
            return False

    def generate_rumble_channel(self):
        """Generate Rumble Channel player page (for Rumble videos only)"""
        if not PAGE_GENERATOR_AVAILABLE:
            messagebox.showwarning("Feature Unavailable", 
                "Page generator not available.\n\n"
                "Download the full project from GitHub to use this feature.")
            return
            
        if not self.channels:
            messagebox.showwarning("No Channels", "Load channels first!")
            return
        
        # Check for Rumble channels
        rumble_channels = []
        for ch in self.channels:
            custom_tags = ch.get('custom_tags', {})
            if custom_tags.get('PROVIDER') == 'RUMBLE':
                rumble_channels.append(ch)
        
        if not rumble_channels:
            messagebox.showinfo(
                "No Rumble Videos",
                "No Rumble videos found in your playlist!\n\n"
                "To use Rumble Channel:\n"
                "1. Import an M3U with Rumble URLs\n"
                "2. Rumble URLs are auto-detected during import\n\n"
                "Supported formats:\n"
                "• https://rumble.com/embed/v123/?pub=abc\n"
                "• https://rumble.com/watch/v123\n"
                "• https://rumble.com/v123-title.html"
            )
            return
        
        # Ask for page name
        page_name = tk.simpledialog.askstring(
            "Rumble Channel Name",
            f"Found {len(rumble_channels)} Rumble video(s)!\n\n"
            "Enter a name for your Rumble Channel:",
            initialvalue="My Rumble Channel"
        )
        
        if not page_name:
            return
        
        # Sanitize page name for filename
        safe_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in page_name)
        safe_name = safe_name.replace(' ', '_').lower()
        
        def generation_thread():
            try:
                self.root.after(0, lambda: self.stat.config(text="Generating Rumble Channel..."))
                
                # Check for template using absolute path
                template_path = TEMPLATES_DIR / "rumble_channel_template.html"
                if not template_path.exists():
                    self.root.after(0, lambda: messagebox.showerror(
                        "Template Not Found",
                        "Rumble Channel template file missing!\n\n"
                        "Ensure this file exists:\n"
                        "- templates/rumble_channel_template.html"
                    ))
                    self.root.after(0, lambda: self.stat.config(text="Template missing"))
                    return
                
                # Generate page
                generator = RumbleChannelGenerator(template_path=str(template_path))
                output_path = generator.generate_page(rumble_channels, safe_name)
                
                # Show success message
                abs_path = output_path.absolute()
                # Use the fixed path for executables
                if getattr(sys, 'frozen', False):
                    from page_generator_fix import get_output_directory
                    abs_dir = get_output_directory().absolute()
                else:
                    abs_dir = Path('generated_pages').absolute()
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success!",
                    f"✅ Rumble Channel Generated!\n\n"
                    f"Page: {page_name}\n"
                    f"Videos: {len(rumble_channels)}\n\n"
                    f"📂 Open this file:\n{abs_path}\n\n"
                    f"💡 All files saved to:\n{abs_dir / safe_name}"
                ))
                
                self.root.after(0, lambda: self.stat.config(
                    text=f"✅ Rumble Channel: {len(rumble_channels)} videos"))
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                self.root.after(0, lambda: messagebox.showerror(
                    "Generation Error",
                    f"Failed to generate Rumble Channel:\n\n{str(e)}\n\n{error_details}"
                ))
                self.root.after(0, lambda: self.stat.config(text="Generation failed"))
        
        threading.Thread(target=generation_thread, daemon=True).start()

    def generate_multi_channel(self):
        """Generate Multi-Channel Viewer page (1-6 simultaneous channels)"""
        if not PAGE_GENERATOR_AVAILABLE:
            messagebox.showwarning("Feature Unavailable", 
                "Page generator not available.\n\n"
                "Download the full project from GitHub to use this feature.")
            return
            
        if not self.channels:
            messagebox.showwarning("No Channels", "Load channels first!")
            return
        
        # Show configuration dialog
        config_dialog = tk.Toplevel(self.root)
        config_dialog.title("Multi-Channel Viewer Configuration")
        config_dialog.geometry("500x400")
        config_dialog.configure(bg="#1a1a2e")
        config_dialog.transient(self.root)
        config_dialog.grab_set()
        
        # Title
        tk.Label(
            config_dialog,
            text="📺 Multi-Channel Viewer",
            font=("Segoe UI", 18, "bold"),
            bg="#1a1a2e",
            fg="#4a90e2"
        ).pack(pady=20)
        
        # Description
        tk.Label(
            config_dialog,
            text=f"Found {len(self.channels)} channels in your playlist.\n\n"
                 "Create a viewer that displays 1 to 6 channels simultaneously\n"
                 "with smart audio management and time-based rotation.",
            font=("Segoe UI", 10),
            bg="#1a1a2e",
            fg="#fff",
            justify=tk.CENTER
        ).pack(pady=10)
        
        # Page name
        name_frame = tk.Frame(config_dialog, bg="#1a1a2e")
        name_frame.pack(pady=15, padx=30, fill=tk.X)
        
        tk.Label(name_frame, text="Page Name:", bg="#1a1a2e", fg="#fff",
                font=("Arial", 10, "bold")).pack(anchor=tk.W)
        page_name_var = tk.StringVar(value="Multi Channel Viewer")
        tk.Entry(name_frame, textvariable=page_name_var, width=40,
                bg="#2c3e50", fg="#fff", font=("Arial", 10)).pack(fill=tk.X, pady=5)
        
        # Channel count
        count_frame = tk.Frame(config_dialog, bg="#1a1a2e")
        count_frame.pack(pady=15, padx=30, fill=tk.X)
        
        tk.Label(count_frame, text="Default Number of Channels to Display:", 
                bg="#1a1a2e", fg="#fff", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        channel_count_var = tk.IntVar(value=1)
        
        count_options = tk.Frame(count_frame, bg="#1a1a2e")
        count_options.pack(pady=5)
        
        for count in [1, 2, 3, 4, 6]:
            tk.Radiobutton(
                count_options,
                text=f"{count} Channel{'s' if count > 1 else ''}",
                variable=channel_count_var,
                value=count,
                bg="#1a1a2e",
                fg="#fff",
                selectcolor="#2c3e50",
                font=("Arial", 9)
            ).pack(side=tk.LEFT, padx=10)
        
        # Info text
        info_text = tk.Label(
            config_dialog,
            text="💡 Users can change the channel count when viewing.\n"
                 "This just sets the initial default layout.",
            font=("Arial", 8),
            bg="#1a1a2e",
            fg="#aaa",
            justify=tk.CENTER
        )
        info_text.pack(pady=10)
        
        # Buttons
        btn_frame = tk.Frame(config_dialog, bg="#1a1a2e")
        btn_frame.pack(pady=20)
        
        def generate():
            page_name = page_name_var.get().strip()
            if not page_name:
                messagebox.showwarning("Invalid Name", "Please enter a page name.")
                return
            
            channel_count = channel_count_var.get()
            config_dialog.destroy()
            self._generate_multi_channel_page(page_name, channel_count)
        
        tk.Button(btn_frame, text="✨ GENERATE", command=generate,
                 bg="#4a90e2", fg="#fff", font=("Arial", 12, "bold"),
                 width=15, height=2).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Cancel", command=config_dialog.destroy,
                 bg="#e74c3c", fg="#fff", font=("Arial", 10),
                 width=12, height=2).pack(side=tk.LEFT, padx=10)
    
    def _generate_multi_channel_page(self, page_name, channel_count):
        """Internal method to generate multi-channel page"""
        safe_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in page_name)
        safe_name = safe_name.replace(' ', '_').lower()
        
        def generation_thread():
            try:
                self.root.after(0, lambda: self.stat.config(text="Generating Multi-Channel Viewer..."))
                
                # Check for template using absolute path
                template_path = TEMPLATES_DIR / "multi_channel_template.html"
                if not template_path.exists():
                    self.root.after(0, lambda: messagebox.showerror(
                        "Template Not Found",
                        "Multi-Channel template file missing!\n\n"
                        "Ensure this file exists:\n"
                        "- templates/multi_channel_template.html"
                    ))
                    self.root.after(0, lambda: self.stat.config(text="Template missing"))
                    return
                
                # Generate page
                generator = MultiChannelGenerator(template_path=str(template_path))
                output_path = generator.generate_page(
                    self.channels, 
                    safe_name,
                    default_channel_count=channel_count
                )
                
                # Show success message
                abs_path = output_path.absolute()
                # Use the fixed path for executables
                if getattr(sys, 'frozen', False):
                    from page_generator_fix import get_output_directory
                    abs_dir = get_output_directory().absolute()
                else:
                    abs_dir = Path('generated_pages').absolute()
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success!",
                    f"✅ Multi-Channel Viewer Generated!\n\n"
                    f"Page: {page_name}\n"
                    f"Channels: {len(self.channels)}\n"
                    f"Default Layout: {channel_count} channel(s)\n\n"
                    f"📂 Open this file:\n{abs_path}\n\n"
                    f"💡 Features:\n"
                    f"• Display 1-6 channels simultaneously\n"
                    f"• Smart audio (only one plays at a time)\n"
                    f"• Time-based rotation\n"
                    f"• Focus mode for fullscreen\n"
                    f"• Keyboard shortcuts (1-6, SPACE, ESC)"
                ))
                
                self.root.after(0, lambda: self.stat.config(
                    text=f"✅ Multi-Channel Viewer: {len(self.channels)} channels"))
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                self.root.after(0, lambda: messagebox.showerror(
                    "Generation Error",
                    f"Failed to generate Multi-Channel Viewer:\n\n{str(e)}\n\n{error_details}"
                ))
                self.root.after(0, lambda: self.stat.config(text="Generation failed"))
        
        threading.Thread(target=generation_thread, daemon=True).start()

    def _generate_all_three_pages(self, scheduler_params):
        """Generate all 3 player pages (NEXUS TV, Web IPTV, Simple Player)"""
        def generation_thread():
            try:
                # Get the first channel name for page naming
                first_channel_name = self.channels[0].get('name', 'Playlist') if self.channels else 'Playlist'
                
                self.root.after(0, lambda: self.stat.config(text="Generating 3 player pages..."))
                
                # Build M3U content (with or without scheduling)
                if scheduler_params:
                    # Create smart schedule
                    scheduled_channels = self.create_smart_schedule(
                        self.channels,
                        show_duration=scheduler_params['show_duration'],
                        num_days=scheduler_params['num_days'],
                        max_consecutive=scheduler_params['max_consecutive']
                    )
                    
                    # Build M3U with schedule metadata
                    m3u_content = "#EXTM3U\n"
                    for item in scheduled_channels:
                        extinf = f'#EXTINF:{item["scheduled_duration"]} tvg-id="{item.get("tvg_id", "")}" '
                        extinf += f'tvg-name="{item.get("name", "")}" tvg-logo="{item.get("logo", "")}" '
                        extinf += f'group-title="{item.get("group", "Other")}" '
                        extinf += f'scheduled-start="{item["scheduled_start"]}",{item.get("name", "")}\n'
                        m3u_content += extinf + item.get("url", "") + "\n"
                else:
                    # Use regular playlist
                    m3u_content = self.m3u
                
                generated = []
                
                # Generate NEXUS TV
                self.root.after(0, lambda: self.stat.config(text="Generating NEXUS TV..."))
                nexus_path = TEMPLATES_DIR / "nexus_tv_template.html"
                if nexus_path.exists():
                    from page_generator import NexusTVPageGenerator
                    nexus_gen = NexusTVPageGenerator(template_path=str(nexus_path))
                    nexus_output = nexus_gen.generate_page(m3u_content, first_channel_name)
                    generated.append({
                        'name': f"{first_channel_name} - NEXUS TV",
                        'file': nexus_output.name,
                        'type': 'nexus'
                    })
                
                # Generate Web IPTV
                self.root.after(0, lambda: self.stat.config(text="Generating Web IPTV..."))
                webiptv_path = TEMPLATES_DIR / "web-iptv-extension"
                if webiptv_path.exists():
                    from page_generator import WebIPTVGenerator
                    webiptv_gen = WebIPTVGenerator(template_path=str(webiptv_path))
                    webiptv_output = webiptv_gen.generate_page(m3u_content, first_channel_name)
                    generated.append({
                        'name': f"{first_channel_name} - Web IPTV",
                        'file': webiptv_output.name,
                        'type': 'webiptv'
                    })
                
                # Generate Simple Player
                self.root.after(0, lambda: self.stat.config(text="Generating Simple Player..."))
                simple_path = TEMPLATES_DIR / "simple-player"
                if simple_path.exists():
                    from page_generator import SimplePlayerGenerator
                    simple_gen = SimplePlayerGenerator(template_path=str(simple_path))
                    simple_output = simple_gen.generate_page(m3u_content, first_channel_name)
                    generated.append({
                        'name': f"{first_channel_name} - Simple Player",
                        'file': simple_output.name,
                        'type': 'simple'
                    })
                
                # Show success message
                abs_dir = Path('generated_pages').absolute()
                
                mode_text = f"with {scheduler_params['num_days']}-day schedule" if scheduler_params else "sequential mode"
                
                self.root.after(
                    0, lambda: messagebox.showinfo(
                        "✅ 3 Pages Generated!",
                        f"Created 3 player pages {mode_text}\n\n"
                        f"📁 Location:\n{abs_dir}\n\n"
                        f"🌐 Open: http://localhost:5000/generated_pages/\n\n"
                        f"📺 Pages Created:\n"
                        f"• {first_channel_name} - NEXUS TV\n"
                        f"• {first_channel_name} - Web IPTV\n"
                        f"• {first_channel_name} - Simple Player\n\n"
                        f"💡 Each page has a SCHEDULER TOGGLE in the menu!"))
                
                self.root.after(0, lambda: self.stat.config(
                    text=f"✅ GENERATED: 3 pages with {len(self.channels)} channels"))
                
            except Exception as e:
                import traceback
                error_msg = f"{str(e)}\n\n{traceback.format_exc()}"
                self.root.after(0, lambda: messagebox.showerror("Generation Error", error_msg))
                self.root.after(0, lambda: self.stat.config(text="Generation failed"))
        
        threading.Thread(target=generation_thread, daemon=True).start()
    
    def _continue_generation(self, template_type):
        """Continue page generation with selected template"""
        
        # For NEXUS TV, show scheduler dialog first
        if template_type == "nexus":
            def on_scheduler_callback(scheduler_params):
                if scheduler_params:
                    # User wants to create a schedule
                    self._generate_with_scheduler(template_type, scheduler_params)
                else:
                    # User skipped scheduling, proceed normally
                    self._generate_normally(template_type)
            
            self.show_scheduler_dialog(on_scheduler_callback)
        else:
            # For other templates, generate normally
            self._generate_normally(template_type)
    
    def _generate_normally(self, template_type):
        """Generate pages without scheduling"""
        # Ask how to generate pages
        choice = messagebox.askquestion(
            "Generate Pages",
            "Generate pages BY GROUP (Yes) or ALL IN ONE (No)?",
            icon='question')

        def generation_thread():
            try:
                template_names = {
                    "nexus": "NEXUS TV",
                    "webiptv": "Web IPTV",
                    "simple": "Simple Player"
                }
                template_name = template_names.get(template_type, "Player")
                self.root.after(
                    0, lambda: self.stat.config(
                        text=f"Generating {template_name} pages..."))
                
                # Initialize the correct generator
                if template_type == "nexus":
                    # Check for NEXUS TV template file
                    template_path = TEMPLATES_DIR / "nexus_tv_template.html"
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
                elif template_type == "webiptv":
                    # Check for Web IPTV template
                    template_path = TEMPLATES_DIR / "web-iptv-extension"
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
                else:  # simple
                    # Check for Simple Player template
                    template_path = TEMPLATES_DIR / "simple-player"
                    if not template_path.exists() or not (template_path / "player.html").exists():
                        self.root.after(0, lambda: messagebox.showerror(
                            "Template Not Found",
                            "Simple Player template files missing!\n\n"
                            "Ensure these files exist:\n"
                            "- templates/simple-player/player.html\n"
                            "- templates/simple-player/css/styles.css\n"
                            "- templates/simple-player/js/app.js\n\n"
                            "Or use the SAVE button to export M3U files."))
                        self.root.after(0, lambda: self.stat.config(text="Template missing"))
                        return
                    generator = SimplePlayerGenerator(template_path=str(template_path))
                
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
                else:  # webiptv or simple
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
    
    def _generate_with_scheduler(self, template_type, scheduler_params):
        """Generate NEXUS TV page with smart scheduling"""
        def generation_thread():
            try:
                self.root.after(0, lambda: self.stat.config(text="Creating smart schedule..."))
                
                # Create the smart schedule
                scheduled_channels = self.create_smart_schedule(
                    self.channels,
                    show_duration=scheduler_params['show_duration'],
                    num_days=scheduler_params['num_days'],
                    max_consecutive=scheduler_params['max_consecutive']
                )
                
                self.root.after(0, lambda: self.stat.config(
                    text=f"Scheduled {len(scheduled_channels)} time slots over {scheduler_params['num_days']} days..."))
                
                # Build M3U content from scheduled channels
                m3u_content = "#EXTM3U\n"
                for item in scheduled_channels:
                    extinf = f'#EXTINF:{item["scheduled_duration"]} tvg-id="{item.get("tvg_id", "")}" '
                    extinf += f'tvg-name="{item.get("name", "")}" tvg-logo="{item.get("logo", "")}" '
                    extinf += f'group-title="{item.get("group", "Other")}" '
                    extinf += f'scheduled-start="{item["scheduled_start"]}",{item.get("name", "")}\n'
                    m3u_content += extinf + item.get("url", "") + "\n"
                
                # Check for NEXUS TV template file
                template_path = Path("../templates/nexus_tv_template.html")
                if not template_path.exists():
                    template_path = Path("templates/nexus_tv_template.html")
                if not template_path.exists():
                    self.root.after(0, lambda: messagebox.showerror(
                        "Template Not Found",
                        "NEXUS TV template file missing!"))
                    return
                
                generator = NexusTVPageGenerator(template_path=str(template_path))
                
                # Generate the page
                self.root.after(0, lambda: self.stat.config(text="Generating NEXUS TV page..."))
                output_path = generator.generate_page(m3u_content, "Smart Schedule")
                
                generated = [{
                    'name': f"Smart Schedule ({scheduler_params['num_days']} days)",
                    'file': output_path.name,
                    'programs': len(scheduled_channels)
                }]
                
                # Generate channel selector
                selector_path = generator.generate_channel_selector(generated)
                
                # Show success message
                abs_selector = selector_path.absolute()
                abs_dir = Path('generated_pages').absolute()
                
                self.root.after(
                    0, lambda: messagebox.showinfo(
                        "✅ Smart Schedule Created!",
                        f"Created {scheduler_params['num_days']}-day TV schedule\n"
                        f"Total time slots: {len(scheduled_channels)}\n\n"
                        f"📁 Location:\n{abs_dir}\n\n"
                        f"🌐 Open: http://localhost:5000/generated_pages/\n\n"
                        f"✨ Features:\n"
                        f"• Globally randomized content\n"
                        f"• No daily repeats\n"
                        f"• Max {scheduler_params['max_consecutive']} consecutive episodes\n"
                        f"• {scheduler_params['show_duration']} minute default duration"))
                
                self.root.after(0, lambda: self.stat.config(
                    text=f"✅ SCHEDULED: {len(scheduled_channels)} time slots"))
                
            except Exception as e:
                import traceback
                error_msg = f"{str(e)}\n\n{traceback.format_exc()}"
                self.root.after(0, lambda: messagebox.showerror("Scheduling Error", error_msg))
                self.root.after(0, lambda: self.stat.config(text="Scheduling failed"))
        
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
        """Safe exit procedure - closes all windows smoothly without errors"""
        try:
            # Final autosave if there are unsaved changes
            if self.autosave_counter > 0 and self.channels:
                response = messagebox.askyesno(
                    "Unsaved Changes", 
                    "You have unsaved changes. Save before exit?")
                if response:
                    self.save()
            
            self.save_settings()
            
            # Close all Toplevel windows gracefully before destroying root
            try:
                # Get all Toplevel windows currently open
                for widget in self.root.winfo_children():
                    try:
                        if isinstance(widget, tk.Toplevel):
                            widget.destroy()
                    except:
                        pass  # Silently skip any errors
                
                # Also try to close any other Toplevel windows
                for toplevel in self.root.winfo_toplevel().__class__.__bases__:
                    try:
                        if hasattr(toplevel, 'destroy'):
                            toplevel.destroy()
                    except:
                        pass
            except:
                pass  # Continue even if window cleanup has issues
            
            # Suppress all errors during final cleanup and quit
            self.root.withdraw()  # Hide window out of view
            self.root.update()
            self.root.quit()
            
        except Exception as e:
            # Silent exit - no error dialogs
            try:
                self.root.quit()
            except:
                import sys
                sys.exit(0)

    def export_m3u_output(self):
        """Export M3U playlist to organized exports folder"""
        if not self.channels:
            messagebox.showwarning("No Channels", "Load channels first!")
            return
        
        # Use OutputManager for organized exports
        try:
            from output_manager import get_output_manager
            manager = get_output_manager()
            exports_dir = manager.playlists_dir
        except:
            exports_dir = Path("M3U_Matrix_Output") / "playlists"
            exports_dir.mkdir(exist_ok=True, parents=True)
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".m3u",
            initialdir=str(exports_dir),
            filetypes=[("M3U files", "*.m3u"), ("M3U8 files", "*.m3u8"), ("All files", "*.*")],
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
                      wrap=tk.NONE, selectbackground="#0066cc",
                      selectforeground="#fff", cursor="xterm")
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll_y = tk.Scrollbar(text_frame, command=text.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scroll_y.set)
        
        scroll_x = tk.Scrollbar(dialog, orient=tk.HORIZONTAL, command=text.xview)
        scroll_x.pack(fill=tk.X, padx=20)
        text.config(xscrollcommand=scroll_x.set)
        
        # Right-click context menu for text operations
        def show_text_context_menu(event):
            context_menu = tk.Menu(text, tearoff=0, bg="#2a2a2a", fg="#fff")
            
            context_menu.add_command(
                label="✂ Cut",
                command=lambda: text.event_generate("<<Cut>>"),
                accelerator="Ctrl+X"
            )
            context_menu.add_command(
                label="📋 Copy",
                command=lambda: text.event_generate("<<Copy>>"),
                accelerator="Ctrl+C"
            )
            context_menu.add_command(
                label="📄 Paste",
                command=lambda: text.event_generate("<<Paste>>"),
                accelerator="Ctrl+V"
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="🔄 Select All",
                command=lambda: text.tag_add(tk.SEL, "1.0", tk.END),
                accelerator="Ctrl+A"
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="↶ Undo",
                command=lambda: text.event_generate("<<Undo>>"),
                accelerator="Ctrl+Z"
            )
            context_menu.add_command(
                label="↷ Redo",
                command=lambda: text.event_generate("<<Redo>>"),
                accelerator="Ctrl+Y"
            )
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        text.bind("<Button-3>", show_text_context_menu)
        
        # Enable drag-and-drop for files
        def handle_file_drop(event):
            """Handle files dropped onto the workbench"""
            files = dialog.tk.splitlist(event.data)
            if files:
                file_path = files[0]
                
                # Check if there's existing content
                existing_content = text.get("1.0", tk.END).strip()
                if existing_content:
                    response = messagebox.askyesno(
                        "Replace Content?",
                        f"Replace current text with content from:\n{os.path.basename(file_path)}?",
                        icon='warning'
                    )
                    if not response:
                        return
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Create undo separator to preserve history
                        text.edit_separator()
                        text.delete("1.0", tk.END)
                        text.insert("1.0", content)
                        # Create another separator so the whole operation can be undone
                        text.edit_separator()
                        self.stat.config(text=f"Loaded: {os.path.basename(file_path)} (Undo available)")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open file:\n{e}")
        
        # Register drag-and-drop
        text.drop_target_register(DND_FILES)
        text.dnd_bind('<<Drop>>', handle_file_drop)
        
        # Enable standard text editing shortcuts
        def select_all(e):
            text.tag_add(tk.SEL, "1.0", tk.END)
            return "break"  # Prevent default behavior
        
        text.bind('<Control-a>', select_all)
        text.bind('<Control-A>', select_all)
        
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
    
    def generate_buffer_tv(self):
        """Generate Buffer TV player page with buffering controls and numeric keypad"""
        if not PAGE_GENERATOR_AVAILABLE:
            messagebox.showwarning("Feature Unavailable", 
                "Page generator not available.\n\n"
                "Download the full project from GitHub to use this feature.")
            return
            
        if not self.channels:
            messagebox.showwarning("No Channels", "Load channels first!")
            return
        
        # Show configuration dialog
        config_dialog = tk.Toplevel(self.root)
        config_dialog.title("Buffer TV Configuration")
        config_dialog.geometry("500x300")
        config_dialog.configure(bg="#1a1a2e")
        config_dialog.transient(self.root)
        config_dialog.grab_set()
        
        # Title
        tk.Label(
            config_dialog,
            text="📺 Buffer TV Player",
            font=("Segoe UI", 18, "bold"),
            bg="#1a1a2e",
            fg="#DC143C"
        ).pack(pady=20)
        
        # Description
        tk.Label(
            config_dialog,
            text=f"Found {len(self.channels)} channels in your playlist.\n\n"
                 "Create a TV player with buffering controls,\n"
                 "numeric keypad, and advanced stream management.",
            font=("Segoe UI", 10),
            bg="#1a1a2e",
            fg="#fff",
            justify=tk.CENTER
        ).pack(pady=10)
        
        # Page name
        name_frame = tk.Frame(config_dialog, bg="#1a1a2e")
        name_frame.pack(pady=15, padx=30, fill=tk.X)
        
        tk.Label(name_frame, text="Page Name:", bg="#1a1a2e", fg="#fff",
                font=("Arial", 10, "bold")).pack(anchor=tk.W)
        page_name_var = tk.StringVar(value="Buffer TV")
        tk.Entry(name_frame, textvariable=page_name_var, width=40,
                bg="#2c3e50", fg="#fff", font=("Arial", 10)).pack(fill=tk.X, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(config_dialog, bg="#1a1a2e")
        btn_frame.pack(pady=20)
        
        def generate():
            page_name = page_name_var.get().strip()
            if not page_name:
                messagebox.showwarning("Invalid Name", "Please enter a page name.")
                return
            
            config_dialog.destroy()
            self._generate_buffer_tv_page(page_name)
        
        self.create_styled_button(btn_frame, "✨ GENERATE", generate,
                                  bg_color="#DC143C", width=15, font_size=12).pack(side=tk.LEFT, padx=10)
        self.create_styled_button(btn_frame, "Cancel", config_dialog.destroy,
                                  bg_color="#e74c3c", width=12, font_size=10).pack(side=tk.LEFT, padx=10)
    
    def _generate_buffer_tv_page(self, page_name):
        """Internal method to generate Buffer TV page"""
        safe_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in page_name)
        safe_name = safe_name.replace(' ', '_').lower()
        
        def generation_thread():
            try:
                self.root.after(0, lambda: self.stat.config(text="Generating Buffer TV..."))
                
                # Generate M3U content from current channels
                m3u_content = "#EXTM3U\n"
                for ch in self.channels:
                    m3u_content += f"#EXTINF:-1 "
                    if ch.get('tvg_name'):
                        m3u_content += f'tvg-name="{ch["tvg_name"]}" '
                    if ch.get('tvg_logo'):
                        m3u_content += f'tvg-logo="{ch["tvg_logo"]}" '
                    if ch.get('group'):
                        m3u_content += f'group-title="{ch["group"]}" '
                    m3u_content += f',{ch.get("name", "Unknown")}\n'
                    m3u_content += f'{ch.get("url", "")}\n'
                
                # Generate page
                generator = BufferTVGenerator()
                output_path = generator.generate_page(m3u_content, safe_name)
                
                abs_path = output_path.absolute()
                abs_dir = Path('generated_pages').absolute()
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success!",
                    f"✅ Buffer TV Generated!\n\n"
                    f"Page: {page_name}\n"
                    f"Channels: {len(self.channels)}\n\n"
                    f"📂 Open this file:\n{abs_path}\n\n"
                    f"💡 Features:\n"
                    f"• Numeric keypad for channel selection\n"
                    f"• Buffering controls (timeout, retry delay)\n"
                    f"• TV Guide overlay\n"
                    f"• Quick category buttons\n\n"
                    f"All files saved to:\n{abs_dir / safe_name}"
                ))
                
                self.root.after(0, lambda: self.stat.config(
                    text=f"✅ Buffer TV: {len(self.channels)} channels"))
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                self.root.after(0, lambda: messagebox.showerror(
                    "Generation Error",
                    f"Failed to generate Buffer TV:\n\n{str(e)}\n\n{error_details}"
                ))
                self.root.after(0, lambda: self.stat.config(text="Generation failed"))
        
        threading.Thread(target=generation_thread, daemon=True).start()
    
    def generate_stream_hub(self):
        """Generate Stream Hub live TV player with glass-morphism design"""
        if not PAGE_GENERATOR_AVAILABLE:
            messagebox.showwarning("Feature Unavailable", 
                "Page generator not available.\n\n"
                "Download the full project from GitHub to use this feature.")
            return
            
        if not self.channels:
            messagebox.showwarning("No Channels", "Load channels first!")
            return
        
        # Show configuration dialog
        config_dialog = tk.Toplevel(self.root)
        config_dialog.title("Stream Hub Configuration")
        config_dialog.geometry("500x450")  # Increased height to show buttons
        config_dialog.configure(bg="#1a1a2e")
        config_dialog.transient(self.root)
        config_dialog.grab_set()
        
        # Title with animated gradient effect
        tk.Label(
            config_dialog,
            text="⚡ STREAM HUB",
            font=("Segoe UI", 20, "bold"),
            bg="#1a1a2e",
            fg="#00d4ff"
        ).pack(pady=20)
        
        # Description
        tk.Label(
            config_dialog,
            text=f"Found {len(self.channels)} live channels in your playlist.\n\n"
                 "Create a stunning broadcast-quality IPTV player with:\n"
                 "• Glass-morphism UI with animated gradients\n"
                 "• Smart HLS/MP4/Audio fallback system\n"
                 "• Live channel grid with status indicators\n"
                 "• Multi-timezone clock and program info",
            font=("Segoe UI", 10),
            bg="#1a1a2e",
            fg="#fff",
            justify=tk.CENTER
        ).pack(pady=10)
        
        # Page name
        name_frame = tk.Frame(config_dialog, bg="#1a1a2e")
        name_frame.pack(pady=15, padx=30, fill=tk.X)
        
        tk.Label(name_frame, text="Page Name:", bg="#1a1a2e", fg="#fff",
                font=("Arial", 10, "bold")).pack(anchor=tk.W)
        page_name_var = tk.StringVar(value="Stream Hub Live")
        tk.Entry(name_frame, textvariable=page_name_var, width=40,
                bg="#2c3e50", fg="#fff", font=("Arial", 10)).pack(fill=tk.X, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(config_dialog, bg="#1a1a2e")
        btn_frame.pack(pady=20)
        
        def generate():
            page_name = page_name_var.get().strip()
            if not page_name:
                messagebox.showwarning("Invalid Name", "Please enter a page name!")
                return
            
            config_dialog.destroy()
            self._generate_stream_hub_page(page_name)
        
        tk.Button(btn_frame, text="✨ GENERATE", command=generate,
                 bg="#00d4ff", fg="#000", font=("Arial", 12, "bold"),
                 width=15, height=2).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Cancel", command=config_dialog.destroy,
                 bg="#e74c3c", fg="#fff", font=("Arial", 10),
                 width=12, height=2).pack(side=tk.LEFT, padx=10)
    
    def _generate_stream_hub_page(self, page_name):
        """Generate the Stream Hub page with the template"""
        def generation_thread():
            try:
                self.root.after(0, lambda: self.stat.config(text="Generating Stream Hub..."))
                
                # Check for template
                from page_generator import StreamHubGenerator
                
                # Clean page name for filesystem
                safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in page_name).strip()
                safe_name = safe_name.replace(" ", "_")
                
                # Prepare M3U content
                m3u_content = "#EXTM3U\n"
                for ch in self.channels:
                    m3u_content += f"#EXTINF:-1 "
                    if ch.get('tvg_name'):
                        m3u_content += f'tvg-name="{ch["tvg_name"]}" '
                    if ch.get('tvg_logo'):
                        m3u_content += f'tvg-logo="{ch["tvg_logo"]}" '
                    if ch.get('group'):
                        m3u_content += f'group-title="{ch["group"]}" '
                    m3u_content += f',{ch.get("name", "Unknown")}\n'
                    m3u_content += f'{ch.get("url", "")}\n'
                
                # Generate page
                generator = StreamHubGenerator()
                output_path = generator.generate_page(m3u_content, safe_name)
                
                abs_path = output_path.absolute()
                abs_dir = Path('generated_pages').absolute()
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success!",
                    f"⚡ Stream Hub Generated!\n\n"
                    f"Page: {page_name}\n"
                    f"Channels: {len(self.channels)}\n\n"
                    f"📂 Open this file:\n{abs_path}\n\n"
                    f"✨ Features:\n"
                    f"• Glass-morphism design with animated gradients\n"
                    f"• Intelligent HLS/MP4/Audio fallback\n"
                    f"• Live channel grid with categories\n"
                    f"• Numeric keypad & search\n"
                    f"• Multi-timezone clock\n\n"
                    f"All files saved to:\n{abs_dir / safe_name}"
                ))
                
                self.root.after(0, lambda: self.stat.config(
                    text=f"⚡ Stream Hub: {len(self.channels)} channels"))
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                self.root.after(0, lambda: messagebox.showerror(
                    "Generation Error",
                    f"Failed to generate Stream Hub:\n\n{str(e)}\n\n{error_details}"
                ))
                self.root.after(0, lambda: self.stat.config(text="Generation failed"))
        
        threading.Thread(target=generation_thread, daemon=True).start()
    
    def generate_standalone_secure(self):
        """Generate standalone secure player page with hidden URLs and chunked loading"""
        if not PAGE_GENERATOR_AVAILABLE:
            messagebox.showwarning("Feature Unavailable", 
                "Page generator not available.\n\n"
                "Download the full project from GitHub to use this feature.")
            return
            
        if not self.channels:
            messagebox.showwarning("No Channels", "Load channels first!")
            return
        
        # Show configuration dialog
        config_dialog = tk.Toplevel(self.root)
        config_dialog.title("Standalone Secure Player Configuration")
        config_dialog.geometry("550x500")
        config_dialog.configure(bg="#1a1a2e")
        config_dialog.transient(self.root)
        config_dialog.grab_set()
        
        # Title with purple gradient
        tk.Label(
            config_dialog,
            text="🔒 STANDALONE SECURE PLAYER",
            font=("Segoe UI", 20, "bold"),
            bg="#1a1a2e",
            fg="#9400D3"
        ).pack(pady=20)
        
        # Description
        tk.Label(
            config_dialog,
            text=f"Found {len(self.channels)} channels in your playlist.\n\n"
                 "Create a completely self-contained HTML player with:\n"
                 "• Everything embedded inline (no external files)\n"
                 "• URLs hidden from user view (security)\n"
                 "• Smart loading - 20% chunks for large playlists\n"
                 "• Perfect for GitHub Pages hosting\n"
                 "• Works offline once loaded",
            font=("Segoe UI", 10),
            bg="#1a1a2e",
            fg="#fff",
            justify=tk.CENTER
        ).pack(pady=10)
        
        # Page name
        name_frame = tk.Frame(config_dialog, bg="#1a1a2e")
        name_frame.pack(pady=15, padx=30, fill=tk.X)
        
        tk.Label(name_frame, text="Page Name:", bg="#1a1a2e", fg="#fff",
                font=("Arial", 10, "bold")).pack(anchor=tk.W)
        page_name_var = tk.StringVar(value="Secure Player")
        tk.Entry(name_frame, textvariable=page_name_var, width=40,
                bg="#2c3e50", fg="#fff", font=("Arial", 10)).pack(fill=tk.X, pady=5)
        
        # GitHub Pages info
        github_frame = tk.Frame(config_dialog, bg="#1a1a2e")
        github_frame.pack(pady=10, padx=30, fill=tk.X)
        
        tk.Label(
            github_frame,
            text="📦 GitHub Pages Ready:\n"
                 "Generated file can be uploaded directly to GitHub\n"
                 "and hosted at: username.github.io/repository/",
            font=("Segoe UI", 9),
            bg="#1a1a2e",
            fg="#00d4ff",
            justify=tk.LEFT
        ).pack(anchor=tk.W)
        
        # Buttons
        btn_frame = tk.Frame(config_dialog, bg="#1a1a2e")
        btn_frame.pack(pady=20)
        
        def generate():
            page_name = page_name_var.get().strip()
            if not page_name:
                messagebox.showwarning("Invalid Name", "Please enter a page name!")
                return
            
            config_dialog.destroy()
            self._generate_standalone_page(page_name)
        
        tk.Button(btn_frame, text="🚀 GENERATE", command=generate,
                 bg="#9400D3", fg="#fff", font=("Arial", 12, "bold"),
                 width=15, height=2).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Cancel", command=config_dialog.destroy,
                 bg="#e74c3c", fg="#fff", font=("Arial", 10),
                 width=12, height=2).pack(side=tk.LEFT, padx=10)
    
    def _generate_standalone_page(self, page_name):
        """Generate the standalone secure page with template"""
        def generation_thread():
            try:
                self.root.after(0, lambda: self.stat.config(text="Generating Standalone Secure Player..."))
                
                # Import generator
                from page_generator import StandaloneSecurePageGenerator
                
                # Prepare M3U content
                m3u_content = "#EXTM3U\n"
                for ch in self.channels:
                    m3u_content += f"#EXTINF:-1 "
                    if ch.get('tvg_name'):
                        m3u_content += f'tvg-name="{ch["tvg_name"]}" '
                    if ch.get('tvg_logo'):
                        m3u_content += f'tvg-logo="{ch["tvg_logo"]}" '
                    if ch.get('group'):
                        m3u_content += f'group-title="{ch["group"]}" '
                    m3u_content += f',{ch.get("name", "Unknown")}\n'
                    m3u_content += f'{ch.get("url", "")}\n'
                
                # Generate page
                generator = StandaloneSecurePageGenerator()
                output_path = generator.generate_page(m3u_content, page_name)
                
                if output_path:
                    self.root.after(0, lambda: self.stat.config(
                        text=f"✅ Standalone page generated: {output_path.name}"))
                    
                    # Show success message with GitHub Pages instructions
                    abs_path = output_path.absolute()
                    self.root.after(100, lambda: messagebox.showinfo(
                        "🔒 Standalone Secure Player Generated!", 
                        f"Your standalone player has been generated!\n\n"
                        f"📁 File: {output_path.name}\n"
                        f"📂 Location: {abs_path}\n\n"
                        f"✨ Features:\n"
                        f"• Completely self-contained (no external files)\n"
                        f"• URLs hidden from display\n"
                        f"• 20% chunked loading for performance\n"
                        f"• {len(self.channels)} channels embedded\n\n"
                        f"📦 GitHub Pages Hosting:\n"
                        f"1. Upload to GitHub repository\n"
                        f"2. Enable Pages in Settings → Pages\n"
                        f"3. Access at: username.github.io/repo/\n\n"
                        f"Check README_GITHUB_PAGES.md for full instructions."))
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Generation Failed", "Failed to generate standalone page"))
                
            except ImportError as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Import Error", f"Could not load Standalone generator: {e}"))
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                self.root.after(0, lambda: messagebox.showerror(
                    "Generation Error", f"Failed to generate page: {e}\n\n{error_details}"))
        
        # Run in thread
        threading.Thread(target=generation_thread, daemon=True).start()
    
    def open_bulk_editor(self):
        """Open the Bulk Editor - spreadsheet-like interface for batch operations"""
        if not self.channels:
            messagebox.showwarning("No Channels", "Load channels first to use the bulk editor!")
            return
        
        # Create bulk editor window
        editor = tk.Toplevel(self.root)
        editor.title("📊 Bulk Channel Editor - Spreadsheet Mode")
        editor.geometry("1200x700")
        editor.configure(bg="#1a1a2e")
        
        # Header
        header_frame = tk.Frame(editor, bg="#2c3e50", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📊 BULK CHANNEL EDITOR", 
                font=("Arial", 18, "bold"), fg="#2ecc71", bg="#2c3e50").pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(header_frame, text=f"{len(self.channels)} channels loaded | Use checkboxes to select",
                font=("Arial", 10), fg="#ecf0f1", bg="#2c3e50").pack(side=tk.LEFT, padx=20)
        
        # Toolbar for bulk operations
        toolbar = tk.Frame(editor, bg="#34495e", height=50)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        # Selection controls
        select_frame = tk.Frame(toolbar, bg="#34495e")
        select_frame.pack(side=tk.LEFT, padx=10, pady=8)
        
        tk.Button(select_frame, text="✓ All", command=lambda: self._select_all_bulk(editor),
                 bg="#3498db", fg="#fff", width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(select_frame, text="✗ None", command=lambda: self._select_none_bulk(editor),
                 bg="#95a5a6", fg="#fff", width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(select_frame, text="⇄ Invert", command=lambda: self._invert_selection_bulk(editor),
                 bg="#9b59b6", fg="#fff", width=8).pack(side=tk.LEFT, padx=2)
        
        # Bulk operations
        ops_frame = tk.Frame(toolbar, bg="#34495e")
        ops_frame.pack(side=tk.LEFT, padx=20, pady=8)
        
        tk.Button(ops_frame, text="🔍 Find & Replace", command=lambda: self._find_replace_bulk(editor),
                 bg="#e67e22", fg="#fff", width=15).pack(side=tk.LEFT, padx=2)
        tk.Button(ops_frame, text="📁 Change Group", command=lambda: self._change_group_bulk(editor),
                 bg="#16a085", fg="#fff", width=15).pack(side=tk.LEFT, padx=2)
        tk.Button(ops_frame, text="🏷️ Add Tag", command=lambda: self._add_tag_bulk(editor),
                 bg="#f39c12", fg="#fff", width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(ops_frame, text="🔗 Update URLs", command=lambda: self._update_urls_bulk(editor),
                 bg="#e74c3c", fg="#fff", width=12).pack(side=tk.LEFT, padx=2)
        
        # Status filter
        filter_frame = tk.Frame(toolbar, bg="#34495e")
        filter_frame.pack(side=tk.RIGHT, padx=10, pady=8)
        
        tk.Label(filter_frame, text="Filter:", fg="#ecf0f1", bg="#34495e").pack(side=tk.LEFT, padx=5)
        filter_var = tk.StringVar(value="all")
        for text, value in [("All", "all"), ("✅ Working", "working"), ("❌ Dead", "dead"), ("⚠️ Slow", "slow")]:
            tk.Radiobutton(filter_frame, text=text, variable=filter_var, value=value,
                          bg="#34495e", fg="#ecf0f1", selectcolor="#2c3e50",
                          command=lambda: self._apply_filter_bulk(editor, filter_var.get())).pack(side=tk.LEFT)
        
        # Main content - Spreadsheet view
        content = tk.Frame(editor, bg="#1a1a2e")
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Treeview with checkboxes
        columns = ("✓", "#", "Status", "Name", "Group", "URL", "Tags")
        tree = ttk.Treeview(content, columns=columns, show="headings", selectmode="extended")
        
        # Configure columns
        tree.heading("✓", text="✓")
        tree.column("✓", width=30, stretch=False)
        tree.heading("#", text="#")
        tree.column("#", width=40, stretch=False)
        tree.heading("Status", text="Status")
        tree.column("Status", width=60, stretch=False)
        tree.heading("Name", text="Channel Name")
        tree.column("Name", width=250, stretch=True)
        tree.heading("Group", text="Group")
        tree.column("Group", width=150, stretch=True)
        tree.heading("URL", text="URL")
        tree.column("URL", width=400, stretch=True)
        tree.heading("Tags", text="Tags")
        tree.column("Tags", width=150, stretch=True)
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", 
                       background="#2c3e50",
                       foreground="#ecf0f1",
                       fieldbackground="#2c3e50",
                       rowheight=25)
        style.configure("Treeview.Heading",
                       background="#34495e",
                       foreground="#2ecc71",
                       font=("Arial", 10, "bold"))
        
        # Scrollbars
        vsb = ttk.Scrollbar(content, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(content, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack elements
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)
        
        # Store references
        editor.tree = tree
        editor.channels_data = self.channels.copy()
        editor.selected_items = set()
        
        # Populate tree
        self._populate_bulk_editor(tree, self.channels)
        
        # Enable inline editing
        tree.bind("<Double-1>", lambda e: self._edit_cell_bulk(e, tree))
        tree.bind("<Button-1>", lambda e: self._toggle_checkbox_bulk(e, tree, editor))
        
        # Bottom status bar
        status_bar = tk.Frame(editor, bg="#2c3e50", height=40)
        status_bar.pack(fill=tk.X)
        status_bar.pack_propagate(False)
        
        status_label = tk.Label(status_bar, text="Ready. Double-click cells to edit inline.", 
                               fg="#ecf0f1", bg="#2c3e50")
        status_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Apply changes button
        apply_frame = tk.Frame(status_bar, bg="#2c3e50")
        apply_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        tk.Button(apply_frame, text="💾 Apply Changes", command=lambda: self._apply_bulk_changes(editor),
                 bg="#27ae60", fg="#fff", font=("Arial", 11, "bold"),
                 width=15, height=1).pack(side=tk.LEFT, padx=5)
        tk.Button(apply_frame, text="Export CSV", command=lambda: self._export_csv_bulk(editor),
                 bg="#3498db", fg="#fff", width=12, height=1).pack(side=tk.LEFT, padx=5)
        tk.Button(apply_frame, text="Close", command=editor.destroy,
                 bg="#e74c3c", fg="#fff", width=10, height=1).pack(side=tk.LEFT, padx=5)
        
        editor.status_label = status_label
    
    def _populate_bulk_editor(self, tree, channels):
        """Populate the bulk editor tree with channel data"""
        for i, channel in enumerate(channels, 1):
            # Determine status (simulated for now)
            status = "✅"  # Default to working
            if not channel.get('url'):
                status = "❌"
            elif 'backup' in channel.get('url', '').lower():
                status = "⚠️"
            
            values = (
                "☐",  # Checkbox
                str(i),  # Number
                status,  # Status
                channel.get('name', 'Unknown'),
                channel.get('group', ''),
                channel.get('url', ''),
                ', '.join(channel.get('tags', [])) if isinstance(channel.get('tags'), list) else channel.get('tags', '')
            )
            tree.insert("", "end", values=values, tags=('unchecked',))
    
    def _toggle_checkbox_bulk(self, event, tree, editor):
        """Toggle checkbox in bulk editor"""
        region = tree.identify_region(event.x, event.y)
        if region == "cell":
            column = tree.identify_column(event.x)
            if column == "#1":  # Checkbox column
                item = tree.identify_row(event.y)
                if item:
                    current = tree.item(item)['values']
                    if current[0] == "☐":
                        tree.set(item, "✓", "☑")
                        tree.item(item, tags=('checked',))
                        editor.selected_items.add(item)
                    else:
                        tree.set(item, "✓", "☐")
                        tree.item(item, tags=('unchecked',))
                        editor.selected_items.discard(item)
                    
                    # Update status
                    count = len(editor.selected_items)
                    editor.status_label.config(text=f"{count} items selected")
    
    def _select_all_bulk(self, editor):
        """Select all items in bulk editor"""
        tree = editor.tree
        for item in tree.get_children():
            tree.set(item, "✓", "☑")
            tree.item(item, tags=('checked',))
            editor.selected_items.add(item)
        editor.status_label.config(text=f"All {len(editor.selected_items)} items selected")
    
    def _select_none_bulk(self, editor):
        """Deselect all items in bulk editor"""
        tree = editor.tree
        for item in tree.get_children():
            tree.set(item, "✓", "☐")
            tree.item(item, tags=('unchecked',))
        editor.selected_items.clear()
        editor.status_label.config(text="No items selected")
    
    def _invert_selection_bulk(self, editor):
        """Invert selection in bulk editor"""
        tree = editor.tree
        for item in tree.get_children():
            current = tree.item(item)['values']
            if current[0] == "☐":
                tree.set(item, "✓", "☑")
                tree.item(item, tags=('checked',))
                editor.selected_items.add(item)
            else:
                tree.set(item, "✓", "☐")
                tree.item(item, tags=('unchecked',))
                editor.selected_items.discard(item)
        editor.status_label.config(text=f"{len(editor.selected_items)} items selected")
    
    def _find_replace_bulk(self, editor):
        """Find and replace in selected items"""
        if not editor.selected_items:
            messagebox.showwarning("No Selection", "Please select items first!")
            return
        
        # Create find/replace dialog
        dialog = tk.Toplevel(editor)
        dialog.title("Find & Replace")
        dialog.geometry("400x250")
        dialog.configure(bg="#2c3e50")
        
        tk.Label(dialog, text="Find:", fg="#ecf0f1", bg="#2c3e50").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        find_var = tk.StringVar()
        tk.Entry(dialog, textvariable=find_var, width=30).grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Replace:", fg="#ecf0f1", bg="#2c3e50").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        replace_var = tk.StringVar()
        tk.Entry(dialog, textvariable=replace_var, width=30).grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="In field:", fg="#ecf0f1", bg="#2c3e50").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        field_var = tk.StringVar(value="Name")
        field_menu = ttk.Combobox(dialog, textvariable=field_var, values=["Name", "Group", "URL", "Tags"], width=27)
        field_menu.grid(row=2, column=1, padx=10, pady=10)
        
        def do_replace():
            find_text = find_var.get()
            replace_text = replace_var.get()
            field = field_var.get()
            
            if not find_text:
                messagebox.showwarning("Empty Find", "Please enter text to find!")
                return
            
            tree = editor.tree
            field_map = {"Name": 3, "Group": 4, "URL": 5, "Tags": 6}
            col_index = field_map.get(field, 3)
            
            replaced = 0
            for item in editor.selected_items:
                values = list(tree.item(item)['values'])
                original = str(values[col_index])
                if find_text in original:
                    values[col_index] = original.replace(find_text, replace_text)
                    tree.item(item, values=values)
                    replaced += 1
            
            editor.status_label.config(text=f"Replaced {replaced} occurrences")
            dialog.destroy()
        
        tk.Button(dialog, text="Replace All", command=do_replace,
                 bg="#27ae60", fg="#fff", width=15).grid(row=3, column=1, padx=10, pady=20)
    
    def _change_group_bulk(self, editor):
        """Change group for selected items"""
        if not editor.selected_items:
            messagebox.showwarning("No Selection", "Please select items first!")
            return
        
        new_group = simpledialog.askstring("Change Group", "Enter new group name:")
        if new_group is not None:
            tree = editor.tree
            for item in editor.selected_items:
                values = list(tree.item(item)['values'])
                values[4] = new_group  # Group column
                tree.item(item, values=values)
            editor.status_label.config(text=f"Changed group for {len(editor.selected_items)} items")
    
    def _add_tag_bulk(self, editor):
        """Add tag to selected items"""
        if not editor.selected_items:
            messagebox.showwarning("No Selection", "Please select items first!")
            return
        
        new_tag = simpledialog.askstring("Add Tag", "Enter tag to add:")
        if new_tag:
            tree = editor.tree
            for item in editor.selected_items:
                values = list(tree.item(item)['values'])
                current_tags = str(values[6])
                if current_tags and current_tags != '':
                    values[6] = f"{current_tags}, {new_tag}"
                else:
                    values[6] = new_tag
                tree.item(item, values=values)
            editor.status_label.config(text=f"Added tag to {len(editor.selected_items)} items")
    
    def _update_urls_bulk(self, editor):
        """Bulk update URLs with pattern"""
        if not editor.selected_items:
            messagebox.showwarning("No Selection", "Please select items first!")
            return
        
        # Create URL update dialog
        dialog = tk.Toplevel(editor)
        dialog.title("Bulk URL Update")
        dialog.geometry("500x200")
        dialog.configure(bg="#2c3e50")
        
        tk.Label(dialog, text="URL Pattern (use {name} for channel name):", 
                fg="#ecf0f1", bg="#2c3e50").pack(padx=10, pady=10)
        
        pattern_var = tk.StringVar(value="http://example.com/stream/{name}.m3u8")
        tk.Entry(dialog, textvariable=pattern_var, width=60).pack(padx=10, pady=10)
        
        tk.Label(dialog, text="Example: http://server.com/{name}/index.m3u8", 
                fg="#95a5a6", bg="#2c3e50", font=("Arial", 9)).pack(padx=10, pady=5)
        
        def apply_pattern():
            pattern = pattern_var.get()
            tree = editor.tree
            updated = 0
            
            for item in editor.selected_items:
                values = list(tree.item(item)['values'])
                name = str(values[3]).replace(' ', '_')  # Name column
                new_url = pattern.replace('{name}', name)
                values[5] = new_url  # URL column
                tree.item(item, values=values)
                updated += 1
            
            editor.status_label.config(text=f"Updated URLs for {updated} items")
            dialog.destroy()
        
        tk.Button(dialog, text="Apply Pattern", command=apply_pattern,
                 bg="#27ae60", fg="#fff", width=20).pack(pady=20)
    
    def _apply_filter_bulk(self, editor, filter_type):
        """Apply status filter to bulk editor"""
        tree = editor.tree
        
        # Clear current view
        for item in tree.get_children():
            tree.delete(item)
        
        # Repopulate based on filter
        for i, channel in enumerate(self.channels, 1):
            # Determine status
            status = "✅"
            if not channel.get('url'):
                status = "❌"
            elif 'backup' in channel.get('url', '').lower():
                status = "⚠️"
            
            # Apply filter
            if filter_type == "all":
                show = True
            elif filter_type == "working" and status == "✅":
                show = True
            elif filter_type == "dead" and status == "❌":
                show = True
            elif filter_type == "slow" and status == "⚠️":
                show = True
            else:
                show = False
            
            if show:
                values = (
                    "☐", str(i), status,
                    channel.get('name', 'Unknown'),
                    channel.get('group', ''),
                    channel.get('url', ''),
                    ', '.join(channel.get('tags', [])) if isinstance(channel.get('tags'), list) else ''
                )
                tree.insert("", "end", values=values, tags=('unchecked',))
        
        editor.selected_items.clear()
        editor.status_label.config(text=f"Filter applied: {filter_type}")
    
    def _edit_cell_bulk(self, event, tree):
        """Enable inline editing for cells"""
        region = tree.identify_region(event.x, event.y)
        if region == "cell":
            column = tree.identify_column(event.x)
            item = tree.identify_row(event.y)
            
            # Skip checkbox and status columns
            if column in ["#1", "#2", "#3"]:
                return
            
            if item:
                # Get column index
                col_index = int(column.replace('#', '')) - 1
                values = tree.item(item)['values']
                current_value = values[col_index]
                
                # Create entry widget for editing
                x, y, width, height = tree.bbox(item, column)
                
                entry = tk.Entry(tree, width=width//8)
                entry.place(x=x, y=y, width=width, height=height)
                entry.insert(0, current_value)
                entry.focus()
                entry.select_range(0, tk.END)
                
                def save_edit(event=None):
                    new_value = entry.get()
                    values = list(tree.item(item)['values'])
                    values[col_index] = new_value
                    tree.item(item, values=values)
                    entry.destroy()
                
                def cancel_edit(event=None):
                    entry.destroy()
                
                entry.bind('<Return>', save_edit)
                entry.bind('<Escape>', cancel_edit)
                entry.bind('<FocusOut>', save_edit)
    
    def _apply_bulk_changes(self, editor):
        """Apply bulk editor changes back to main channel list"""
        tree = editor.tree
        
        # Update channels from tree
        updated_channels = []
        for item in tree.get_children():
            values = tree.item(item)['values']
            channel = {
                'name': values[3],
                'group': values[4],
                'url': values[5],
                'tags': values[6].split(', ') if values[6] else []
            }
            updated_channels.append(channel)
        
        # Apply to main channel list
        self.channels = updated_channels
        self.fill()  # Refresh main view
        
        messagebox.showinfo("Success", f"Applied changes to {len(updated_channels)} channels")
        editor.destroy()
    
    def _export_csv_bulk(self, editor):
        """Export bulk editor data to CSV"""
        import csv
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            tree = editor.tree
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Number', 'Status', 'Name', 'Group', 'URL', 'Tags'])
                
                # Write data
                for item in tree.get_children():
                    values = tree.item(item)['values']
                    writer.writerow(values[1:])  # Skip checkbox column
            
            editor.status_label.config(text=f"Exported to {filename}")
    
    def open_version_control(self):
        """Open Version Control system for playlist history and rollback"""
        # Create version control directory if not exists
        version_dir = Path("playlist_versions")
        version_dir.mkdir(exist_ok=True)
        
        # Create version control window
        vc_window = tk.Toplevel(self.root)
        vc_window.title("🔄 Playlist Version Control")
        vc_window.geometry("900x600")
        vc_window.configure(bg="#1e2329")
        
        # Header
        header = tk.Frame(vc_window, bg="#2d3339", height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🔄 VERSION CONTROL", 
                font=("Arial", 20, "bold"), fg="#3498db", bg="#2d3339").pack(side=tk.LEFT, padx=20, pady=20)
        
        current_count = len(self.channels) if self.channels else 0
        tk.Label(header, text=f"Current playlist: {current_count} channels",
                font=("Arial", 11), fg="#bdc3c7", bg="#2d3339").pack(side=tk.LEFT, padx=20)
        
        # Toolbar
        toolbar = tk.Frame(vc_window, bg="#34495e", height=60)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        btn_frame = tk.Frame(toolbar, bg="#34495e")
        btn_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Button(btn_frame, text="📸 Save Snapshot", command=lambda: self._save_version(vc_window),
                 bg="#27ae60", fg="#fff", font=("Arial", 10, "bold"),
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🔄 Restore Version", command=lambda: self._restore_version(vc_window),
                 bg="#e67e22", fg="#fff", font=("Arial", 10, "bold"),
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📊 Compare Versions", command=lambda: self._compare_versions(vc_window),
                 bg="#9b59b6", fg="#fff", font=("Arial", 10, "bold"),
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑️ Delete Version", command=lambda: self._delete_version(vc_window),
                 bg="#e74c3c", fg="#fff", font=("Arial", 10, "bold"),
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        # Auto-save toggle
        auto_frame = tk.Frame(toolbar, bg="#34495e")
        auto_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        vc_window.auto_save_var = tk.BooleanVar(value=False)
        tk.Checkbutton(auto_frame, text="Auto-save on changes", 
                      variable=vc_window.auto_save_var,
                      bg="#34495e", fg="#ecf0f1", selectcolor="#2c3e50",
                      font=("Arial", 10)).pack(side=tk.LEFT)
        
        # Main content - Version list
        content = tk.Frame(vc_window, bg="#1e2329")
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Version list
        list_frame = tk.Frame(content, bg="#2d3339", relief=tk.RIDGE, bd=2)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(list_frame, text="📚 Saved Versions", 
                font=("Arial", 12, "bold"), fg="#3498db", bg="#2d3339").pack(pady=10)
        
        # Create Treeview for versions
        columns = ("Version", "Date", "Time", "Channels", "Size", "Description")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        tree.heading("Version", text="Version")
        tree.column("Version", width=80)
        tree.heading("Date", text="Date")
        tree.column("Date", width=100)
        tree.heading("Time", text="Time")
        tree.column("Time", width=80)
        tree.heading("Channels", text="Channels")
        tree.column("Channels", width=80)
        tree.heading("Size", text="Size")
        tree.column("Size", width=80)
        tree.heading("Description", text="Description")
        tree.column("Description", width=350)
        
        # Style
        style = ttk.Style()
        style.configure("Treeview", 
                       background="#2d3339",
                       foreground="#ecf0f1",
                       fieldbackground="#2d3339")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        vc_window.tree = tree
        
        # Load existing versions
        self._load_versions(tree, version_dir)
        
        # Statistics panel
        stats_frame = tk.Frame(vc_window, bg="#2d3339", height=100)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        stats_frame.pack_propagate(False)
        
        tk.Label(stats_frame, text="📈 Version Statistics", 
                font=("Arial", 11, "bold"), fg="#3498db", bg="#2d3339").pack(pady=5)
        
        stats_text = tk.Text(stats_frame, height=3, bg="#1e2329", fg="#ecf0f1", 
                            font=("Courier", 9), relief=tk.FLAT)
        stats_text.pack(fill=tk.BOTH, padx=10, pady=5)
        
        # Calculate statistics
        version_files = list(version_dir.glob("*.json"))
        total_versions = len(version_files)
        total_size = sum(f.stat().st_size for f in version_files) / 1024  # KB
        oldest = min(version_files, key=lambda f: f.stat().st_mtime).name if version_files else "N/A"
        
        stats_text.insert("1.0", f"Total Versions: {total_versions} | Storage Used: {total_size:.1f} KB | Oldest: {oldest}")
        stats_text.config(state=tk.DISABLED)
        
        # Bind double-click to view version details
        tree.bind("<Double-1>", lambda e: self._view_version_details(tree, version_dir))
    
    def _save_version(self, vc_window):
        """Save current playlist as a version"""
        if not self.channels:
            messagebox.showwarning("No Playlist", "No playlist loaded to save!")
            return
        
        # Create save dialog
        dialog = tk.Toplevel(vc_window)
        dialog.title("Save Version")
        dialog.geometry("400x200")
        dialog.configure(bg="#2c3e50")
        
        tk.Label(dialog, text="Version Description:", fg="#ecf0f1", bg="#2c3e50",
                font=("Arial", 11)).pack(pady=10)
        
        desc_text = tk.Text(dialog, height=4, width=45, bg="#34495e", fg="#ecf0f1")
        desc_text.pack(padx=20, pady=10)
        desc_text.insert("1.0", f"Snapshot of {len(self.channels)} channels")
        
        def save():
            description = desc_text.get("1.0", "end").strip()
            timestamp = datetime.now()
            version_name = f"v{timestamp.strftime('%Y%m%d_%H%M%S')}"
            
            version_data = {
                "version": version_name,
                "timestamp": timestamp.isoformat(),
                "description": description,
                "channel_count": len(self.channels),
                "channels": self.channels,
                "groups": list(set(ch.get('group', '') for ch in self.channels))
            }
            
            # Save to file
            version_file = Path("playlist_versions") / f"{version_name}.json"
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(version_data, f, indent=2, ensure_ascii=False)
            
            # Refresh version list
            self._load_versions(vc_window.tree, Path("playlist_versions"))
            
            messagebox.showinfo("Success", f"Version {version_name} saved successfully!")
            dialog.destroy()
        
        tk.Button(dialog, text="💾 Save Version", command=save,
                 bg="#27ae60", fg="#fff", width=20).pack(pady=10)
    
    def _restore_version(self, vc_window):
        """Restore a selected version"""
        selection = vc_window.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a version to restore!")
            return
        
        item = vc_window.tree.item(selection[0])
        version_name = item['values'][0]
        
        if messagebox.askyesno("Restore Version", 
                               f"Are you sure you want to restore version {version_name}?\n"
                               f"Current playlist will be replaced!"):
            # Load version data
            version_file = Path("playlist_versions") / f"{version_name}.json"
            if version_file.exists():
                with open(version_file, 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
                
                # Restore channels
                self.channels = version_data['channels']
                self.fill()  # Refresh main display
                
                messagebox.showinfo("Success", f"Restored {len(self.channels)} channels from {version_name}")
                self.stat.config(text=f"Restored from {version_name}")
    
    def _compare_versions(self, vc_window):
        """Compare two versions"""
        selection = vc_window.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a version to compare with current!")
            return
        
        item = vc_window.tree.item(selection[0])
        version_name = item['values'][0]
        
        # Load selected version
        version_file = Path("playlist_versions") / f"{version_name}.json"
        if not version_file.exists():
            return
        
        with open(version_file, 'r', encoding='utf-8') as f:
            version_data = json.load(f)
        
        old_channels = version_data['channels']
        current_channels = self.channels if self.channels else []
        
        # Create comparison window
        comp_window = tk.Toplevel(vc_window)
        comp_window.title(f"Compare: Current vs {version_name}")
        comp_window.geometry("700x500")
        comp_window.configure(bg="#1e2329")
        
        # Header
        tk.Label(comp_window, text=f"📊 Comparison: Current ({len(current_channels)} ch) vs {version_name} ({len(old_channels)} ch)",
                font=("Arial", 12, "bold"), fg="#3498db", bg="#1e2329").pack(pady=10)
        
        # Analysis
        current_names = set(ch.get('name', '') for ch in current_channels)
        old_names = set(ch.get('name', '') for ch in old_channels)
        
        added = current_names - old_names
        removed = old_names - current_names
        unchanged = current_names & old_names
        
        # Display results
        notebook = ttk.Notebook(comp_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Added channels tab
        added_frame = tk.Frame(notebook, bg="#2d3339")
        notebook.add(added_frame, text=f"➕ Added ({len(added)})")
        
        added_list = tk.Listbox(added_frame, bg="#34495e", fg="#2ecc71", 
                               font=("Courier", 10))
        added_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for name in sorted(added):
            added_list.insert(tk.END, name)
        
        # Removed channels tab
        removed_frame = tk.Frame(notebook, bg="#2d3339")
        notebook.add(removed_frame, text=f"➖ Removed ({len(removed)})")
        
        removed_list = tk.Listbox(removed_frame, bg="#34495e", fg="#e74c3c",
                                 font=("Courier", 10))
        removed_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for name in sorted(removed):
            removed_list.insert(tk.END, name)
        
        # Unchanged channels tab
        unchanged_frame = tk.Frame(notebook, bg="#2d3339")
        notebook.add(unchanged_frame, text=f"✓ Unchanged ({len(unchanged)})")
        
        unchanged_list = tk.Listbox(unchanged_frame, bg="#34495e", fg="#95a5a6",
                                   font=("Courier", 10))
        unchanged_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for name in sorted(unchanged):
            unchanged_list.insert(tk.END, name)
        
        # Summary
        summary_frame = tk.Frame(comp_window, bg="#2c3e50", height=60)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        summary_text = f"Summary: {len(added)} added, {len(removed)} removed, {len(unchanged)} unchanged"
        tk.Label(summary_frame, text=summary_text, fg="#ecf0f1", bg="#2c3e50",
                font=("Arial", 11)).pack(pady=20)
    
    def _delete_version(self, vc_window):
        """Delete a selected version"""
        selection = vc_window.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a version to delete!")
            return
        
        item = vc_window.tree.item(selection[0])
        version_name = item['values'][0]
        
        if messagebox.askyesno("Delete Version", 
                               f"Are you sure you want to delete version {version_name}?\n"
                               f"This cannot be undone!"):
            version_file = Path("playlist_versions") / f"{version_name}.json"
            if version_file.exists():
                version_file.unlink()
                self._load_versions(vc_window.tree, Path("playlist_versions"))
                messagebox.showinfo("Success", f"Version {version_name} deleted")
    
    def _load_versions(self, tree, version_dir):
        """Load all saved versions into tree"""
        # Clear existing
        for item in tree.get_children():
            tree.delete(item)
        
        # Load version files
        version_files = sorted(version_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        
        for vf in version_files:
            try:
                with open(vf, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                timestamp = datetime.fromisoformat(data['timestamp'])
                size_kb = vf.stat().st_size / 1024
                
                values = (
                    data['version'],
                    timestamp.strftime('%Y-%m-%d'),
                    timestamp.strftime('%H:%M:%S'),
                    data['channel_count'],
                    f"{size_kb:.1f} KB",
                    data.get('description', '')[:50]  # Truncate long descriptions
                )
                tree.insert("", "end", values=values)
            except:
                continue
    
    def _view_version_details(self, tree, version_dir):
        """View detailed information about a version"""
        selection = tree.selection()
        if not selection:
            return
        
        item = tree.item(selection[0])
        version_name = item['values'][0]
        
        version_file = version_dir / f"{version_name}.json"
        if not version_file.exists():
            return
        
        with open(version_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create details window
        details = tk.Toplevel()
        details.title(f"Version Details: {version_name}")
        details.geometry("600x400")
        details.configure(bg="#2c3e50")
        
        # Display details
        text = tk.Text(details, bg="#34495e", fg="#ecf0f1", font=("Courier", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        details_text = f"""VERSION INFORMATION
{'='*50}
Version: {data['version']}
Created: {data['timestamp']}
Channels: {data['channel_count']}
Description: {data.get('description', 'No description')}

CHANNEL GROUPS:
{', '.join(data.get('groups', []))}

SAMPLE CHANNELS (First 10):
{'='*50}
"""
        for i, ch in enumerate(data['channels'][:10], 1):
            details_text += f"{i}. {ch.get('name', 'Unknown')} - {ch.get('group', 'No Group')}\n"
        
        text.insert("1.0", details_text)
        text.config(state=tk.DISABLED)
    
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
                    # Use OutputManager for organized JSON saves
                    try:
                        from output_manager import get_output_manager
                        manager = get_output_manager()
                        json_dir = manager.json_data_dir
                    except:
                        json_dir = Path("M3U_Matrix_Output") / "json_data"
                        json_dir.mkdir(exist_ok=True, parents=True)
                    
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
                    # Use OutputManager for organized JSON saves
                    try:
                        from output_manager import get_output_manager
                        manager = get_output_manager()
                        json_dir = manager.json_data_dir
                    except:
                        json_dir = Path("M3U_Matrix_Output") / "json_data"
                        json_dir.mkdir(exist_ok=True, parents=True)
                    
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
    parser = argparse.ArgumentParser(
        description="M3U Matrix Pro - Playlist Manager & ScheduleFlow Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python M3U_MATRIX_PRO.py              # Run in Advanced Mode (GUI)
  python M3U_MATRIX_PRO.py --headless   # Run in Silent Background Mode (Daemon)
  python M3U_MATRIX_PRO.py --help       # Show this help message
        """)
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode (daemon for API control, no GUI)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='M3U Matrix Pro v2.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        if args.headless:
            # Silent Background Mode (Daemon)
            logging.info("Starting M3U Matrix Pro in HEADLESS mode")
            app = M3UMatrix(headless=True)
            logging.info("M3U Matrix Pro is running in headless mode")
            logging.info("Control via: REST API, Control Dashboard, Numeric Keypad")
            logging.info("Process ID: %d", os.getpid())
            
            # Keep the process alive
            try:
                while True:
                    threading.Event().wait(1)
            except KeyboardInterrupt:
                logging.info("Received interrupt signal, shutting down...")
                if hasattr(app, 'safe_exit'):
                    app.safe_exit()
        else:
            # Advanced Mode (GUI)
            logging.info("Starting M3U Matrix Pro in ADVANCED (GUI) mode")
            app = M3UMatrix(headless=False)
            if app.root:
                app.root.protocol("WM_DELETE_WINDOW", app.safe_exit)
    except Exception as e:
        logging.error(f"Failed to start M3U Matrix: {e}", exc_info=True)
        if not args.headless:
            messagebox.showerror("Startup Error",
                                 f"Failed to start application: {e}")

