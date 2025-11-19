"""
Rumble Category Browser UI
A visual browser for discovering and importing Rumble channels organized by category.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import json
from typing import Dict, List, Optional, Callable
from PIL import Image, ImageTk
import io
import requests


class RumbleCategoryBrowser(tk.Toplevel):
    """
    Visual browser for Rumble channels organized by category.
    
    Features:
    - Browse 30+ pre-loaded Rumble channels
    - Organized by 11 categories
    - Search and filter channels
    - One-click import to playlist
    - Channel preview with metadata
    """
    
    def __init__(self, parent, on_channel_import: Optional[Callable] = None):
        """
        Initialize the Rumble Category Browser
        
        Args:
            parent: Parent Tkinter window
            on_channel_import: Callback function when channel is imported
                              Receives channel dict as parameter
        """
        super().__init__(parent)
        
        self.parent = parent
        self.on_channel_import = on_channel_import
        
        # Load Rumble channels database
        self.channels_db = self._load_channels_database()
        self.filtered_channels = self.channels_db.copy()
        
        # UI state
        self.current_category = "All Categories"
        self.search_query = ""
        self.channel_cards = []
        
        # Setup window
        self.title("Rumble Category Browser")
        self.geometry("1000x700")
        self.configure(bg="#1e1e1e")
        
        # Initialize UI
        self._create_widgets()
        self._populate_channels()
        
    def _load_channels_database(self) -> List[Dict]:
        """Load Rumble channels from database file"""
        db_path = Path(__file__).resolve().parent.parent / "data" / "rumble_channels.json"
        
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                channels = data.get('channels', [])
                
                if not channels:
                    messagebox.showwarning(
                        "Empty Database",
                        f"No channels found in database:\n{db_path}\n\n"
                        "The database file exists but contains no channels."
                    )
                
                return channels
        except FileNotFoundError:
            messagebox.showerror(
                "Database Not Found",
                f"Rumble channels database not found:\n{db_path}\n\n"
                "Please ensure the database file exists in the data folder."
            )
            return []
        except json.JSONDecodeError as e:
            messagebox.showerror(
                "Database Error",
                f"Failed to parse Rumble channels database:\n{e}\n\n"
                "The JSON file may be corrupted."
            )
            return []
        except Exception as e:
            messagebox.showerror(
                "Unexpected Error",
                f"Error loading Rumble channels database:\n{e}"
            )
            return []
    
    def _get_categories(self) -> List[str]:
        """Get unique categories from channels database"""
        categories = set()
        for channel in self.channels_db:
            categories.add(channel.get('category', 'Uncategorized'))
        
        return ["All Categories"] + sorted(list(categories))
    
    def _create_widgets(self):
        """Create and layout all UI widgets"""
        
        # Top toolbar
        toolbar = tk.Frame(self, bg="#2d2d2d", height=60)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        # Category selector
        tk.Label(toolbar, text="Category:", bg="#2d2d2d", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        self.category_var = tk.StringVar(value="All Categories")
        category_dropdown = ttk.Combobox(
            toolbar,
            textvariable=self.category_var,
            values=self._get_categories(),
            state="readonly",
            width=20,
            font=("Arial", 10)
        )
        category_dropdown.pack(side=tk.LEFT, padx=5)
        category_dropdown.bind("<<ComboboxSelected>>", self._on_category_changed)
        
        # Search box
        tk.Label(toolbar, text="Search:", bg="#2d2d2d", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=(20, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._on_search_changed())
        
        search_entry = tk.Entry(
            toolbar,
            textvariable=self.search_var,
            bg="#3d3d3d",
            fg="white",
            insertbackground="white",
            width=30,
            font=("Arial", 10)
        )
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Clear search button
        clear_btn = tk.Button(
            toolbar,
            text="✕",
            command=self._clear_search,
            bg="#444",
            fg="white",
            font=("Arial", 10),
            width=3,
            relief=tk.FLAT,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        # Results count
        self.results_label = tk.Label(toolbar, text="", bg="#2d2d2d", fg="#888", font=("Arial", 9))
        self.results_label.pack(side=tk.RIGHT, padx=10)
        
        # Scrollable canvas for channel grid
        canvas_frame = tk.Frame(self, bg="#1e1e1e")
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Canvas with scrollbar
        self.canvas = tk.Canvas(canvas_frame, bg="#1e1e1e", highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg="#1e1e1e")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _on_category_changed(self, event=None):
        """Handle category selection change"""
        self.current_category = self.category_var.get()
        self._filter_and_display()
    
    def _on_search_changed(self):
        """Handle search query change"""
        self.search_query = self.search_var.get().lower()
        self._filter_and_display()
    
    def _clear_search(self):
        """Clear search box"""
        self.search_var.set("")
    
    def _filter_and_display(self):
        """Filter channels based on category and search, then display"""
        self.filtered_channels = []
        
        for channel in self.channels_db:
            # Category filter
            if self.current_category != "All Categories":
                if channel.get('category') != self.current_category:
                    continue
            
            # Search filter
            if self.search_query:
                searchable = f"{channel.get('name', '')} {channel.get('handle', '')} {channel.get('description', '')}".lower()
                if self.search_query not in searchable:
                    continue
            
            self.filtered_channels.append(channel)
        
        self._populate_channels()
    
    def _populate_channels(self):
        """Populate the channel grid with filtered channels"""
        # Clear existing cards
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.channel_cards = []
        
        # Update results count
        total = len(self.channels_db)
        showing = len(self.filtered_channels)
        self.results_label.config(text=f"Showing {showing} of {total} channels")
        
        if not self.filtered_channels:
            # No results message
            no_results = tk.Label(
                self.scrollable_frame,
                text="No channels found matching your filters.",
                bg="#1e1e1e",
                fg="#888",
                font=("Arial", 12)
            )
            no_results.pack(pady=50)
            return
        
        # Create grid of channel cards (3 columns)
        columns = 3
        for idx, channel in enumerate(self.filtered_channels):
            row = idx // columns
            col = idx % columns
            
            card = self._create_channel_card(self.scrollable_frame, channel)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            self.channel_cards.append(card)
        
        # Configure grid columns to expand equally
        for col in range(columns):
            self.scrollable_frame.grid_columnconfigure(col, weight=1, uniform="column")
    
    def _create_channel_card(self, parent, channel: Dict) -> tk.Frame:
        """Create a visual card for a channel"""
        card = tk.Frame(parent, bg="#2d2d2d", relief=tk.RAISED, borderwidth=1)
        card.configure(highlightbackground="#444", highlightthickness=1)
        
        # Card content frame
        content = tk.Frame(card, bg="#2d2d2d")
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Channel name (bold, large)
        name = channel.get('name', 'Unknown Channel')
        name_label = tk.Label(
            content,
            text=name,
            bg="#2d2d2d",
            fg="#FFD700",
            font=("Arial", 12, "bold"),
            wraplength=250,
            justify=tk.LEFT
        )
        name_label.pack(anchor="w", pady=(0, 5))
        
        # Category badge
        category = channel.get('category', 'Uncategorized')
        category_badge = tk.Label(
            content,
            text=category,
            bg="#444",
            fg="#aaa",
            font=("Arial", 8),
            padx=6,
            pady=2
        )
        category_badge.pack(anchor="w", pady=(0, 10))
        
        # Description (truncated)
        description = channel.get('description', 'No description available.')
        if len(description) > 100:
            description = description[:97] + "..."
        
        desc_label = tk.Label(
            content,
            text=description,
            bg="#2d2d2d",
            fg="#bbb",
            font=("Arial", 9),
            wraplength=250,
            justify=tk.LEFT,
            height=3
        )
        desc_label.pack(anchor="w", pady=(0, 10))
        
        # Channel reference note
        note_label = tk.Label(
            content,
            text="📌 Channel reference - click to browse on Rumble",
            bg="#2d2d2d",
            fg="#888",
            font=("Arial", 7, "italic"),
            wraplength=250
        )
        note_label.pack(anchor="w", pady=(0, 5))
        
        # Metadata (handle, pub code)
        handle = channel.get('handle', 'N/A')
        pub_code = channel.get('pub_code', 'N/A')
        
        meta_frame = tk.Frame(content, bg="#2d2d2d")
        meta_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            meta_frame,
            text=f"@{handle}",
            bg="#2d2d2d",
            fg="#888",
            font=("Arial", 8, "italic")
        ).pack(anchor="w")
        
        tk.Label(
            meta_frame,
            text=f"Pub: {pub_code}",
            bg="#2d2d2d",
            fg="#888",
            font=("Arial", 8)
        ).pack(anchor="w")
        
        # Add to Playlist button
        add_btn = tk.Button(
            content,
            text="➕ Add to Playlist",
            command=lambda ch=channel: self._import_channel(ch),
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=5
        )
        add_btn.pack(fill=tk.X, pady=(5, 0))
        
        # Hover effects
        def on_enter(e):
            card.configure(highlightbackground="#FFD700", highlightthickness=2)
        
        def on_leave(e):
            card.configure(highlightbackground="#444", highlightthickness=1)
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        return card
    
    def _import_channel(self, channel: Dict):
        """Import selected channel to playlist"""
        if self.on_channel_import:
            try:
                # Call the import callback and check if it succeeded
                result = self.on_channel_import(channel)
                
                # Show success only if import was successful
                if result is not False:  # None or True = success
                    messagebox.showinfo(
                        "Channel Added",
                        f"Successfully added '{channel.get('name')}' to your playlist!",
                        parent=self
                    )
            except Exception as e:
                messagebox.showerror(
                    "Import Failed",
                    f"Failed to import channel:\n{str(e)}",
                    parent=self
                )
        else:
            messagebox.showwarning(
                "Import Error",
                "No import handler configured.",
                parent=self
            )
    
    def destroy(self):
        """Clean up when window is closed"""
        self.canvas.unbind_all("<MouseWheel>")
        super().destroy()


# Testing code
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    def test_import(channel):
        print(f"Importing channel: {channel.get('name')}")
        print(f"Handle: {channel.get('handle')}")
        print(f"Pub Code: {channel.get('pub_code')}")
    
    browser = RumbleCategoryBrowser(root, on_channel_import=test_import)
    browser.mainloop()
