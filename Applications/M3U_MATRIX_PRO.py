"""
M3U MATRIX PRO - Professional IPTV Playlist Manager
Refactored modular version using Core_Modules architecture
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, font, simpledialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import re, os, threading, tempfile, webbrowser
from datetime import datetime, timedelta
from collections import defaultdict
from urllib.parse import urlparse, unquote
import requests
import sys
import logging
from pathlib import Path
import uuid
import json

# Calculate project root and add to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORE_MODULES_DIR = PROJECT_ROOT / "Core_Modules"
WEB_PLAYERS_DIR = PROJECT_ROOT / "Web_Players"

# Add Core_Modules directory to sys.path for imports
if str(CORE_MODULES_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_MODULES_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Define resource paths
TEMPLATES_DIR = WEB_PLAYERS_DIR
DATA_DIR = PROJECT_ROOT / "data"

# Import Core Modules
from Core_Modules.models.channel import Channel, ChannelDict, ChannelUtils
from Core_Modules.settings.settings_manager import SettingsManager
from Core_Modules.parsers.m3u_parser import M3UParser
from Core_Modules.parsers.epg_parser import EPGParser
from Core_Modules.core.channel_validator import ChannelValidator
from Core_Modules.undo.undo_manager import UndoManager
from Core_Modules.utils.helpers import (
    sanitize_filename, validate_url, validate_file_path,
    sanitize_input, is_valid_m3u, download_and_cache_thumbnail,
    get_cached_thumbnail_stats, SimpleCache, get_file_size,
    create_progress_dialog, open_folder_in_explorer
)
from Core_Modules.gui.components import ButtonFactory, DialogFactory, ProgressManager, TreeviewManager

# Optional imports - only needed for advanced features
try:
    if getattr(sys, 'frozen', False):
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
        from Core_Modules.page_generator import (
            NexusTVPageGenerator, WebIPTVGenerator, SimplePlayerGenerator, 
            RumbleChannelGenerator, MultiChannelGenerator, BufferTVGenerator,
            ClassicTVGenerator
        )
        PAGE_GENERATOR_AVAILABLE = True
        print("Page generators loaded (development mode)")
        
        def get_output_directory(subfolder=""):
            try:
                from output_manager import get_output_manager
                manager = get_output_manager()
                if subfolder:
                    return manager.get_page_output_dir(subfolder)
                else:
                    return manager.pages_dir
            except ImportError:
                output_dir = Path("M3U_Matrix_Output") / "generated_pages"
                if subfolder:
                    output_dir = output_dir / subfolder
                output_dir.mkdir(exist_ok=True, parents=True)
                return output_dir
            
except ImportError as e:
    PAGE_GENERATOR_AVAILABLE = False
    logging.warning(f"Page generator not available: {e}")
    
    def get_output_directory(subfolder=""):
        try:
            from output_manager import get_output_manager
            manager = get_output_manager()
            if subfolder:
                return manager.get_page_output_dir(subfolder)
            else:
                return manager.pages_dir
        except ImportError:
            output_dir = Path("M3U_Matrix_Output") / "generated_pages"
            if subfolder:
                output_dir = output_dir / subfolder
            output_dir.mkdir(exist_ok=True, parents=True)
            return output_dir

# NDI Output import
try:
    from ndi_output import get_ndi_manager
    NDI_AVAILABLE = True
except ImportError as e:
    NDI_AVAILABLE = False
    logging.info(f"NDI output module not available: {e}")

# Setup logging
log_path = Path(__file__).parent / "logs" / "m3u_matrix.log"
log_path.parent.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)


class M3UMatrix:
    """
    Main application class for M3U Matrix Pro
    Refactored to use modular Core_Modules architecture
    """

    def __init__(self):
        """Initialize the M3U Matrix application"""
        self.root = TkinterDnD.Tk()
        self.root.title("M3U MATRIX PRO • DRAG & DROP M3U FILES • DOUBLE-CLICK TO OPEN")
        self.root.geometry("1600x950")
        self.root.minsize(1300, 800)
        self.root.configure(bg="#121212")

        # Set working directory to application folder
        os.chdir(Path(__file__).parent)

        # Initialize data structures
        self.files = []
        self.channels = []
        self.m3u = ""
        self.clipboard = None
        self.drag_data = {"iid": None, "y": 0}
        self.schedule = {}
        self.custom_tags = {}
        self.epg_data = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize Core Module managers
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.get_all_settings()
        self.m3u_parser = M3UParser()
        self.epg_parser = EPGParser()
        self.channel_validator = ChannelValidator()
        self.undo_manager = UndoManager()
        self.progress_manager = ProgressManager(self.root)
        
        # Initialize caches
        self.thumbnail_cache = SimpleCache(max_size=200)
        self.filter_cache = {}
        self.autosave_counter = 0
        self.last_save_time = datetime.now()
        
        # Performance & UX improvements
        self.uuid_to_iid_map = {}  # O(1) lookup for treeview updates
        self.dirty = False  # Track unsaved changes
        self.search_debounce_id = None  # For debounced search

        # Initialize UI components
        self.setup_error_handling()
        self.build_ui()
        self.load_tv_guide()
        self.start_autosave()

    def setup_error_handling(self):
        """Setup comprehensive error handling"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            if exc_type == KeyboardInterrupt:
                self.safe_exit()
            else:
                self.logger.exception("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
                DialogFactory.create_error_dialog(
                    self.root, 
                    "Application Error",
                    "An unexpected error occurred. The application will try to continue.",
                    exc_value
                )
        
        sys.excepthook = handle_exception

    def build_ui(self):
        """Build the main user interface"""
        # Setup styles
        TreeviewManager.setup_treeview_style()
        
        # Main container with responsive grid
        main_frame = tk.Frame(self.root, bg="#121212")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Top frame for search and buttons
        self.build_top_frame(main_frame)
        
        # Middle frame with treeview
        self.build_middle_frame(main_frame)
        
        # Bottom frame with status and controls
        self.build_bottom_frame(main_frame)
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Setup drag and drop
        self.setup_drag_drop()
        
        # Update status
        self.update_status("Ready. Drag & Drop M3U files or click 'Open Files'")

    def build_top_frame(self, parent):
        """Build the top frame with search and buttons"""
        top_frame = tk.Frame(parent, bg="#1a1a1a", relief=tk.RAISED, bd=1)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        parent.grid_columnconfigure(0, weight=1)

        # Search frame
        search_frame = tk.Frame(top_frame, bg="#1a1a1a")
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.grid_columnconfigure(0, weight=1)

        # Search components
        tk.Label(search_frame, text="🔍 Search:", bg="#1a1a1a", fg="white", 
                font=("Arial", 11, "bold")).grid(row=0, column=0, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_changed)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                    width=30, font=("Arial", 11))
        self.search_entry.grid(row=0, column=1, padx=5, sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)

        # Results label
        self.search_results_label = tk.Label(search_frame, text="", bg="#1a1a1a", 
                                            fg="gold", font=("Arial", 10))
        self.search_results_label.grid(row=0, column=2, padx=10)

        # Buttons frame
        buttons_frame = tk.Frame(top_frame, bg="#1a1a1a")
        buttons_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Create buttons using ButtonFactory
        button_configs = [
            ("📂 Open Files", self.open_files, "#F2E1C1"),
            ("💾 Save M3U", self.save_m3u, "#95C77E"),
            ("🔄 Refresh", self.refresh_display, "#FFD700"),
            ("📋 Paste", self.paste, "#87CEEB"),
            ("✂️ Cut", self.cut, "#FFA500"),
            ("🗑️ Delete", self.delete_selected, "#E74C3C"),
            ("🔗 Validate Links", self.validate_links, "#9B59B6"),
            ("📡 EPG Import", self.import_epg, "#3498DB"),
            ("🎬 CLASSIC TV", self.generate_classic, "#FF0000"),  # YOUR BIG RED BUTTON IS BACK!
            ("🌐 More Players", self.show_page_generator_menu, "#2ECC71")
        ]

        for i, (text, command, color) in enumerate(button_configs):
            btn = ButtonFactory.create_styled_button(
                buttons_frame, text, command, color, width=14
            )
            btn.grid(row=0, column=i, padx=3)

    def build_middle_frame(self, parent):
        """Build the middle frame with treeview"""
        middle_frame = tk.Frame(parent, bg="#1e1e1e")
        middle_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        parent.grid_rowconfigure(1, weight=1)

        # Create treeview with scrollbars
        tree_container = tk.Frame(middle_frame, bg="#1e1e1e")
        tree_container.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical")
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal")

        # Treeview
        self.tv = TreeviewManager.create_channel_treeview(tree_container)
        self.tv.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        v_scrollbar.configure(command=self.tv.yview)
        h_scrollbar.configure(command=self.tv.xview)

        # Grid layout
        self.tv.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Bind events
        self.tv.bind("<Double-Button-1>", self.on_double_click)
        self.tv.bind("<Button-3>", self.show_context_menu)
        self.tv.bind("<Control-c>", lambda e: self.copy())
        self.tv.bind("<Control-v>", lambda e: self.paste())

    def build_bottom_frame(self, parent):
        """Build the bottom frame with status and controls"""
        bottom_frame = tk.Frame(parent, bg="#1a1a1a", relief=tk.RAISED, bd=1)
        bottom_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))

        # Status bar
        self.status_label = tk.Label(bottom_frame, text="Ready", bg="#1a1a1a",
                                    fg="white", font=("Arial", 10), anchor="w")
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Stats frame
        stats_frame = tk.Frame(bottom_frame, bg="#1a1a1a")
        stats_frame.pack(side=tk.RIGHT, padx=10, pady=5)

        self.stats_label = tk.Label(stats_frame, text="Channels: 0 | Groups: 0",
                                   bg="#1a1a1a", fg="gold", font=("Arial", 10))
        self.stats_label.pack()

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        shortcuts = {
            "<Control-o>": lambda e: self.open_files(),
            "<Control-s>": lambda e: self.save_m3u(),
            "<Control-z>": lambda e: self.undo(),
            "<Control-y>": lambda e: self.redo(),
            "<Control-a>": lambda e: self.select_all(),
            "<Delete>": lambda e: self.delete_selected(),
            "<F5>": lambda e: self.refresh_display(),
            "<Escape>": lambda e: self.clear_search()
        }
        
        for key, handler in shortcuts.items():
            self.root.bind(key, handler)

    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

    def on_drop(self, event):
        """Handle file drop events"""
        files = self.root.tk.splitlist(event.data)
        self.load_files(list(files))

    def load_files(self, file_paths):
        """Load M3U files"""
        self.progress_manager.show_progress("Loading Files", len(file_paths))
        
        loaded_count = 0
        for i, file_path in enumerate(file_paths):
            if self.progress_manager.is_cancelled():
                break
            
            self.progress_manager.update_progress(i + 1, f"Loading {Path(file_path).name}")
            
            try:
                # Determine file type and parse
                if file_path.lower().endswith(('.m3u', '.m3u8')):
                    channels = self.m3u_parser.parse_file(file_path)
                elif file_path.lower().endswith('.txt'):
                    channels = self.m3u_parser.parse_txt_file(file_path)
                else:
                    continue
                
                if channels:
                    # Track changes for undo
                    old_channels = self.channels.copy()
                    self.channels.extend(channels)
                    self.undo_manager.push_action({
                        'type': 'load',
                        'old_channels': old_channels,
                        'new_channels': self.channels.copy()
                    })
                    
                    loaded_count += 1
                    self.files.append(file_path)
                    
            except Exception as e:
                self.logger.error(f"Failed to load {file_path}: {e}")
                
        self.progress_manager.close()
        
        if loaded_count > 0:
            self.refresh_display()
            self.update_status(f"Loaded {loaded_count} file(s), {len(self.channels)} channels")
        else:
            messagebox.showwarning("No Files Loaded", "No valid M3U files were loaded")

    def refresh_display(self):
        """Refresh the treeview display"""
        # Clear current display
        self.tv.delete(*self.tv.get_children())
        self.uuid_to_iid_map.clear()
        
        # Add channels to treeview
        for idx, channel in enumerate(self.channels, 1):
            # Get current and next programme
            current_prog = self.get_current_programme(channel)
            next_prog = self.get_next_programme(channel)
            
            # Insert into treeview
            values = (
                idx,
                current_prog.get('show', '') if current_prog else '',
                next_prog.get('show', '') if next_prog else '',
                channel.get('group', 'Other'),
                channel.get('name', 'Unknown'),
                channel.get('url', ''),
                len(channel.get('backups', [])),
                len(channel.get('custom_tags', {})),
                '❌'
            )
            
            iid = self.tv.insert('', 'end', values=values)
            
            # Map UUID to treeview item ID
            if 'uuid' in channel:
                self.uuid_to_iid_map[channel['uuid']] = iid
        
        # Update statistics
        self.update_statistics()

    def update_statistics(self):
        """Update channel statistics display"""
        total_channels = len(self.channels)
        groups = set(ch.get('group', 'Other') for ch in self.channels)
        total_groups = len(groups)
        
        self.stats_label.config(text=f"Channels: {total_channels} | Groups: {total_groups}")
        
        # Update window title
        if self.files:
            file_names = [Path(f).name for f in self.files[-3:]]  # Show last 3 files
            files_str = ", ".join(file_names)
            if len(self.files) > 3:
                files_str = f"... {files_str}"
            self.root.title(f"M3U MATRIX PRO • {files_str} • {total_channels} channels")

    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def on_search_changed(self, *args):
        """Handle search text changes with debouncing"""
        if self.search_debounce_id:
            self.root.after_cancel(self.search_debounce_id)
        
        self.search_debounce_id = self.root.after(300, self.perform_search)

    def perform_search(self):
        """Perform the actual search"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self.clear_search()
            return
        
        # Hide all items first
        for item in self.tv.get_children():
            self.tv.detach(item)
        
        # Show matching items
        matches = 0
        for item in self.tv.get_children(''):
            values = self.tv.item(item)['values']
            # Search in name, group, URL, and programmes
            searchable = [
                str(values[1]).lower(),  # Now Playing
                str(values[2]).lower(),  # Next
                str(values[3]).lower(),  # Group
                str(values[4]).lower(),  # Name
                str(values[5]).lower(),  # URL
            ]
            
            if any(search_term in s for s in searchable):
                self.tv.reattach(item, '', 'end')
                matches += 1
        
        # Update search results label
        self.search_results_label.config(text=f"Found: {matches}")

    def clear_search(self):
        """Clear search and show all items"""
        self.search_var.set("")
        for item in self.tv.get_children(''):
            self.tv.reattach(item, '', 'end')
        self.search_results_label.config(text="")

    def open_files(self):
        """Open file dialog to select M3U files"""
        file_types = [
            ("M3U Playlists", "*.m3u *.m3u8"),
            ("Text Files", "*.txt"),
            ("All Files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select M3U Files",
            filetypes=file_types
        )
        
        if files:
            self.load_files(list(files))

    def save_m3u(self):
        """Save channels to M3U file"""
        if not self.channels:
            messagebox.showwarning("No Channels", "No channels to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".m3u",
            filetypes=[("M3U Playlist", "*.m3u"), ("M3U8 Playlist", "*.m3u8")]
        )
        
        if file_path:
            if self.m3u_parser.write_m3u(self.channels, file_path):
                self.update_status(f"Saved {len(self.channels)} channels to {Path(file_path).name}")
                self.dirty = False
            else:
                messagebox.showerror("Save Failed", "Failed to save M3U file")

    def validate_links(self):
        """Validate channel links"""
        if not self.channels:
            messagebox.showwarning("No Channels", "No channels to validate")
            return
        
        self.progress_manager.show_progress("Validating Links", len(self.channels))
        
        def progress_callback(current, total, channel, status, results):
            self.progress_manager.update_progress(
                current,
                f"{channel.get('name', 'Unknown')}: {status}"
            )
            
            # Update treeview item color based on status
            if 'uuid' in channel:
                iid = self.uuid_to_iid_map.get(channel['uuid'])
                if iid:
                    color = {
                        'working': '#00ff00',
                        'broken': '#ff0000',
                        'timeout': '#ffaa00'
                    }.get(status, '#ffffff')
                    
                    self.tv.item(iid, tags=(status,))
                    self.tv.tag_configure(status, foreground=color)
        
        # Run validation in thread
        def validate_thread():
            results = self.channel_validator.validate_channels(
                self.channels,
                progress_callback
            )
            
            self.root.after(0, lambda: self.show_validation_results(results))
        
        thread = threading.Thread(target=validate_thread)
        thread.start()

    def show_validation_results(self, results):
        """Show validation results dialog"""
        self.progress_manager.close()
        
        stats = self.channel_validator.get_validation_stats()
        
        message = f"""
Validation Complete!

✅ Working: {stats['working']}
❌ Broken: {stats['broken']}
⏱️ Timeout: {stats['timeout']}

Success Rate: {stats['success_rate']:.1f}%
"""
        
        messagebox.showinfo("Validation Results", message)

    def import_epg(self):
        """Import EPG data"""
        file_path = filedialog.askopenfilename(
            title="Select EPG XML File",
            filetypes=[("XML Files", "*.xml"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.update_status("Loading EPG data...")
            epg_data = self.epg_parser.parse_from_file(file_path)
            
            if 'error' in epg_data:
                messagebox.showerror("EPG Import Failed", epg_data['error'])
            else:
                self.epg_data = epg_data
                self.schedule = epg_data.get('schedule', {})
                
                # Update display to show EPG data
                self.refresh_display()
                
                self.update_status(
                    f"Loaded EPG: {epg_data['total_channels']} channels, "
                    f"{epg_data['total_programmes']} programmes"
                )

    def get_current_programme(self, channel):
        """Get current programme for a channel"""
        channel_id = channel.get('tvg_id', channel.get('name', ''))
        if channel_id and self.schedule:
            return self.epg_parser.get_current_programme(channel_id, self.schedule)
        return None

    def get_next_programme(self, channel):
        """Get next programme for a channel"""
        channel_id = channel.get('tvg_id', channel.get('name', ''))
        if channel_id and self.schedule:
            return self.epg_parser.get_next_programme(channel_id, self.schedule)
        return None

    def show_page_generator_menu(self):
        """Show page generator menu"""
        if not PAGE_GENERATOR_AVAILABLE:
            messagebox.showwarning(
                "Not Available",
                "Page generators are not available. Please install the page_generator module."
            )
            return
        
        if not self.channels:
            messagebox.showwarning("No Channels", "Please load channels first")
            return
        
        # Create generator menu
        menu = tk.Menu(self.root, tearoff=0)
        generators = [
            ("NexusTV Player", self.generate_nexustv),
            ("WebIPTV Player", self.generate_webiptv),
            ("Simple Player", self.generate_simple),
            ("BufferTV Player", self.generate_buffertv),
            ("Multi-Channel Player", self.generate_multi),
            ("Classic TV Player", self.generate_classic),
            ("Rumble Channels", self.generate_rumble)
        ]
        
        for name, command in generators:
            menu.add_command(label=name, command=command)
        
        # Show menu at button position
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def generate_nexustv(self):
        """Generate NexusTV player page"""
        self._generate_page(NexusTVPageGenerator, "NexusTV")

    def generate_webiptv(self):
        """Generate WebIPTV player page"""
        self._generate_page(WebIPTVGenerator, "WebIPTV")

    def generate_simple(self):
        """Generate Simple player page"""
        self._generate_page(SimplePlayerGenerator, "SimplePlayer")

    def generate_buffertv(self):
        """Generate BufferTV player page"""
        self._generate_page(BufferTVGenerator, "BufferTV")

    def generate_multi(self):
        """Generate Multi-Channel player page"""
        self._generate_page(MultiChannelGenerator, "MultiChannel")

    def generate_classic(self):
        """Generate Classic TV player page"""
        self._generate_page(ClassicTVGenerator, "ClassicTV")

    def generate_rumble(self):
        """Generate Rumble channels page"""
        # Filter Rumble channels
        rumble_channels = [
            ch for ch in self.channels
            if 'rumble.com' in ch.get('url', '').lower()
        ]
        
        if not rumble_channels:
            messagebox.showinfo("No Rumble Channels", "No Rumble channels found in playlist")
            return
        
        self._generate_page(RumbleChannelGenerator, "RumbleChannels", rumble_channels)

    def _generate_page(self, generator_class, name, channels=None):
        """Generate a player page"""
        try:
            if channels is None:
                channels = self.channels
            
            # Prepare channel data
            channel_data = []
            for ch in channels:
                channel_data.append({
                    'name': ch.get('name', 'Unknown'),
                    'url': ch.get('url', ''),
                    'logo': ch.get('logo', ''),
                    'group': ch.get('group', 'Other'),
                    'backups': ch.get('backups', []),
                    'custom_tags': ch.get('custom_tags', {}),
                    'schedule': self.get_channel_schedule(ch)
                })
            
            # Generate page
            generator = generator_class()
            output_dir = get_output_directory(name)
            
            result = generator.generate(
                channels=channel_data,
                output_dir=str(output_dir),
                m3u_file=self.files[0] if self.files else "playlist.m3u",
                schedule_data=self.schedule
            )
            
            if result and 'output_file' in result:
                self.update_status(f"Generated {name} page")
                
                # Ask to open
                if messagebox.askyesno("Page Generated", f"Page generated successfully!\n\nOpen {name} player?"):
                    webbrowser.open(f"file:///{result['output_file']}")
            else:
                messagebox.showerror("Generation Failed", f"Failed to generate {name} page")
                
        except Exception as e:
            self.logger.error(f"Failed to generate {name} page: {e}")
            messagebox.showerror("Generation Error", str(e))

    def get_channel_schedule(self, channel):
        """Get schedule for a channel"""
        channel_id = channel.get('tvg_id', channel.get('name', ''))
        return self.schedule.get(channel_id, [])

    def show_context_menu(self, event):
        """Show right-click context menu"""
        # Select item under cursor
        item = self.tv.identify_row(event.y)
        if item:
            self.tv.selection_set(item)
        
        # Create context menu
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Copy", command=self.copy)
        menu.add_command(label="Cut", command=self.cut)
        menu.add_command(label="Paste", command=self.paste)
        menu.add_separator()
        menu.add_command(label="Delete", command=self.delete_selected)
        menu.add_separator()
        menu.add_command(label="Edit Channel", command=self.edit_channel)
        menu.add_command(label="Duplicate", command=self.duplicate_selected)
        
        menu.post(event.x_root, event.y_root)

    def copy(self):
        """Copy selected channels to clipboard"""
        selected = self.tv.selection()
        if selected:
            indices = [self.tv.index(item) for item in selected]
            self.clipboard = [self.channels[i].copy() for i in indices]
            self.update_status(f"Copied {len(self.clipboard)} channel(s)")

    def cut(self):
        """Cut selected channels to clipboard"""
        self.copy()
        self.delete_selected()

    def paste(self):
        """Paste channels from clipboard"""
        if not self.clipboard:
            messagebox.showinfo("No Data", "Nothing to paste")
            return
        
        # Track for undo
        old_channels = self.channels.copy()
        
        # Insert at current selection or end
        selected = self.tv.selection()
        if selected:
            insert_index = self.tv.index(selected[0])
        else:
            insert_index = len(self.channels)
        
        # Insert channels
        for i, channel in enumerate(self.clipboard):
            # Generate new UUID for pasted channel
            new_channel = channel.copy()
            new_channel['uuid'] = str(uuid.uuid4())
            self.channels.insert(insert_index + i, new_channel)
        
        # Update undo stack
        self.undo_manager.push_action({
            'type': 'paste',
            'old_channels': old_channels,
            'new_channels': self.channels.copy()
        })
        
        self.refresh_display()
        self.update_status(f"Pasted {len(self.clipboard)} channel(s)")

    def delete_selected(self):
        """Delete selected channels"""
        selected = self.tv.selection()
        if not selected:
            return
        
        if messagebox.askyesno("Delete Channels", f"Delete {len(selected)} channel(s)?"):
            # Track for undo
            old_channels = self.channels.copy()
            
            # Delete in reverse order to maintain indices
            indices = sorted([self.tv.index(item) for item in selected], reverse=True)
            for idx in indices:
                del self.channels[idx]
            
            # Update undo stack
            self.undo_manager.push_action({
                'type': 'delete',
                'old_channels': old_channels,
                'new_channels': self.channels.copy()
            })
            
            self.refresh_display()
            self.update_status(f"Deleted {len(indices)} channel(s)")

    def duplicate_selected(self):
        """Duplicate selected channels"""
        selected = self.tv.selection()
        if not selected:
            return
        
        # Track for undo
        old_channels = self.channels.copy()
        
        # Duplicate channels
        indices = [self.tv.index(item) for item in selected]
        for idx in sorted(indices, reverse=True):
            new_channel = self.channels[idx].copy()
            new_channel['uuid'] = str(uuid.uuid4())
            new_channel['name'] = f"{new_channel.get('name', '')} (Copy)"
            self.channels.insert(idx + 1, new_channel)
        
        # Update undo stack
        self.undo_manager.push_action({
            'type': 'duplicate',
            'old_channels': old_channels,
            'new_channels': self.channels.copy()
        })
        
        self.refresh_display()
        self.update_status(f"Duplicated {len(indices)} channel(s)")

    def edit_channel(self):
        """Edit selected channel"""
        selected = self.tv.selection()
        if not selected or len(selected) > 1:
            messagebox.showinfo("Select One", "Please select exactly one channel to edit")
            return
        
        idx = self.tv.index(selected[0])
        channel = self.channels[idx]
        
        # Create edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Channel: {channel.get('name', 'Unknown')}")
        dialog.geometry("600x400")
        dialog.configure(bg="#1e1e1e")
        
        # Channel fields
        fields = [
            ("Name:", channel.get('name', '')),
            ("Group:", channel.get('group', '')),
            ("URL:", channel.get('url', '')),
            ("Logo:", channel.get('logo', '')),
            ("TVG ID:", channel.get('tvg_id', ''))
        ]
        
        entries = {}
        for i, (label, value) in enumerate(fields):
            tk.Label(dialog, text=label, bg="#1e1e1e", fg="white").grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(dialog, width=60)
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[label.rstrip(':')] = entry
        
        # Save button
        def save_changes():
            # Track for undo
            old_channels = self.channels.copy()
            
            # Update channel
            self.channels[idx]['name'] = entries['Name'].get()
            self.channels[idx]['group'] = entries['Group'].get()
            self.channels[idx]['url'] = entries['URL'].get()
            self.channels[idx]['logo'] = entries['Logo'].get()
            self.channels[idx]['tvg_id'] = entries['TVG ID'].get()
            
            # Update undo stack
            self.undo_manager.push_action({
                'type': 'edit',
                'old_channels': old_channels,
                'new_channels': self.channels.copy()
            })
            
            self.refresh_display()
            dialog.destroy()
        
        tk.Button(dialog, text="Save", command=save_changes, bg="#95C77E", fg="white").grid(row=len(fields), column=0, columnspan=2, pady=20)

    def select_all(self):
        """Select all channels"""
        self.tv.selection_set(self.tv.get_children())

    def on_double_click(self, event):
        """Handle double-click on channel"""
        selected = self.tv.selection()
        if selected:
            idx = self.tv.index(selected[0])
            channel = self.channels[idx]
            
            # Try to play channel
            url = channel.get('url', '')
            if url:
                if url.startswith(('http://', 'https://')):
                    webbrowser.open(url)
                else:
                    messagebox.showinfo("Cannot Play", f"Cannot directly play: {url}")

    def undo(self):
        """Undo last action"""
        action = self.undo_manager.undo()
        if action:
            self.channels = action['old_channels'].copy()
            self.refresh_display()
            self.update_status(f"Undone: {action['type']}")

    def redo(self):
        """Redo last undone action"""
        action = self.undo_manager.redo()
        if action:
            self.channels = action['new_channels'].copy()
            self.refresh_display()
            self.update_status(f"Redone: {action['type']}")

    def load_tv_guide(self):
        """Load TV guide data if available"""
        guide_file = Path("tv_guide.json")
        if guide_file.exists():
            try:
                with open(guide_file, 'r') as f:
                    self.schedule = json.load(f)
                self.logger.info(f"Loaded TV guide with {len(self.schedule)} channels")
            except Exception as e:
                self.logger.error(f"Failed to load TV guide: {e}")

    def start_autosave(self):
        """Start autosave timer"""
        def autosave():
            if self.dirty and self.channels:
                # Save to temp file
                temp_file = Path("autosave.m3u")
                if self.m3u_parser.write_m3u(self.channels, str(temp_file)):
                    self.logger.info(f"Autosaved {len(self.channels)} channels")
                    self.dirty = False
            
            # Schedule next autosave
            self.root.after(300000, autosave)  # 5 minutes
        
        self.root.after(300000, autosave)

    def safe_exit(self):
        """Safely exit the application"""
        if self.dirty and self.channels:
            if messagebox.askyesno("Save Changes", "You have unsaved changes. Save before exit?"):
                self.save_m3u()
        
        # Save settings
        self.settings_manager.save_settings()
        
        self.root.quit()


if __name__ == "__main__":
    try:
        app = M3UMatrix()
        app.root.protocol("WM_DELETE_WINDOW", app.safe_exit)
        app.root.mainloop()
    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        messagebox.showerror("Startup Error", f"Failed to start M3U Matrix Pro:\n{str(e)}")
        sys.exit(1)