"""
TV Schedule Center - Visual TV Programming Manager
Complete scheduling system with calendar grid, drag-and-drop, and channel management
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkfont
from datetime import datetime, timedelta, time
import json
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Core_Modules.tv_schedule_db import TVScheduleDB
from Core_Modules.schedule_manager import ScheduleManager
from Core_Modules.auto_scheduler import AutoScheduler
from Core_Modules.web_epg_server import WebEPGServer


class TVScheduleCenter:
    """Main TV Schedule Center application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📺 TV Schedule Center - Visual Programming Manager")
        
        # Set minimum window size
        self.root.minsize(1200, 700)
        
        # Initialize database and manager
        self.db = TVScheduleDB("tv_schedules.db")
        self.manager = ScheduleManager("tv_schedules.db")
        
        # Current schedule and view
        self.current_schedule_id = None
        self.current_week_start = self.get_week_start(datetime.now())
        self.selected_channel_id = None
        self.selected_slot = None
        
        # Time slot configuration
        self.time_slot_minutes = 30
        self.time_slots = []  # Will hold time labels
        
        # Drag and drop variables
        self.drag_data = {}
        
        # Colors and styling
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'grid_bg': '#2d2d2d',
            'slot_empty': '#3a3a3a',
            'slot_filled': '#4a90e2',
            'slot_selected': '#6ab04c',
            'slot_conflict': '#e74c3c',
            'header_bg': '#252525',
            'button_bg': '#3498db',
            'button_hover': '#2980b9'
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        
        # Create UI
        self.setup_ui()
        
        # Load initial data
        self.load_schedules()
        self.load_channels()
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_schedule())
        self.root.bind('<Control-s>', lambda e: self.save_schedule())
        self.root.bind('<Control-o>', lambda e: self.load_schedule())
        self.root.bind('<Delete>', lambda e: self.delete_selected_slot())
        self.root.bind('<F5>', lambda e: self.refresh_schedule_view())
    
    def setup_ui(self):
        """Setup the main UI components"""
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Top toolbar
        self.create_toolbar(main_container)
        
        # Create paned window for main content
        paned = tk.PanedWindow(main_container, orient='horizontal', 
                              bg=self.colors['bg'], sashwidth=5)
        paned.pack(fill='both', expand=True, pady=10)
        
        # Left panel - Channel and Show management
        left_panel = tk.Frame(paned, bg=self.colors['bg'], width=300)
        self.create_left_panel(left_panel)
        paned.add(left_panel)
        
        # Center panel - Schedule Grid
        center_panel = tk.Frame(paned, bg=self.colors['bg'])
        self.create_schedule_grid(center_panel)
        paned.add(center_panel)
        
        # Right panel - Properties and Actions
        right_panel = tk.Frame(paned, bg=self.colors['bg'], width=250)
        self.create_right_panel(right_panel)
        paned.add(right_panel)
        
        # Status bar
        self.create_status_bar(main_container)
    
    def create_toolbar(self, parent):
        """Create the top toolbar"""
        toolbar = tk.Frame(parent, bg=self.colors['header_bg'], height=50)
        toolbar.pack(fill='x', pady=(0, 10))
        
        # Schedule controls
        tk.Button(
            toolbar, text="📅 New Schedule", command=self.new_schedule,
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            font=('Arial', 10, 'bold'), padx=15, pady=8
        ).pack(side='left', padx=5, pady=10)
        
        tk.Button(
            toolbar, text="💾 Save", command=self.save_schedule,
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            font=('Arial', 10, 'bold'), padx=15, pady=8
        ).pack(side='left', padx=5)
        
        tk.Button(
            toolbar, text="📂 Load", command=self.load_schedule,
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            font=('Arial', 10, 'bold'), padx=15, pady=8
        ).pack(side='left', padx=5)
        
        tk.Button(
            toolbar, text="📁 Import Folder", command=self.import_folder,
            bg='#27ae60', fg=self.colors['fg'],
            font=('Arial', 10, 'bold'), padx=15, pady=8
        ).pack(side='left', padx=5)
        
        tk.Button(
            toolbar, text="🎬 Auto-Build 24/7", command=self.auto_build_schedule,
            bg='#e67e22', fg=self.colors['fg'],
            font=('Arial', 10, 'bold'), padx=15, pady=8
        ).pack(side='left', padx=5)
        
        tk.Button(
            toolbar, text="📊 Export EPG JSON", command=self.export_web_epg,
            bg='#8e44ad', fg=self.colors['fg'],
            font=('Arial', 10, 'bold'), padx=15, pady=8
        ).pack(side='left', padx=5)
        
        tk.Button(
            toolbar, text="🔄 Rebuild Schedule", command=self.rebuild_schedule,
            bg='#c0392b', fg=self.colors['fg'],
            font=('Arial', 10, 'bold'), padx=15, pady=8
        ).pack(side='left', padx=5)
        
        # Schedule selector
        tk.Label(
            toolbar, text="Current Schedule:", bg=self.colors['header_bg'],
            fg=self.colors['fg'], font=('Arial', 10)
        ).pack(side='left', padx=(20, 5))
        
        self.schedule_var = tk.StringVar()
        self.schedule_combo = ttk.Combobox(
            toolbar, textvariable=self.schedule_var,
            state='readonly', width=30
        )
        self.schedule_combo.pack(side='left', padx=5)
        self.schedule_combo.bind('<<ComboboxSelected>>', self.on_schedule_selected)
        
        # Week navigation
        tk.Button(
            toolbar, text="◀ Previous Week", command=self.previous_week,
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            font=('Arial', 10), padx=10, pady=8
        ).pack(side='right', padx=5)
        
        tk.Button(
            toolbar, text="Next Week ▶", command=self.next_week,
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            font=('Arial', 10), padx=10, pady=8
        ).pack(side='right', padx=5)
        
        self.week_label = tk.Label(
            toolbar, text="", bg=self.colors['header_bg'],
            fg=self.colors['fg'], font=('Arial', 11, 'bold')
        )
        self.week_label.pack(side='right', padx=20)
    
    def create_left_panel(self, parent):
        """Create left panel with channels and shows"""
        
        # Channels section
        channel_frame = tk.LabelFrame(
            parent, text="📺 Channels", bg=self.colors['bg'],
            fg=self.colors['fg'], font=('Arial', 11, 'bold')
        )
        channel_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Channel listbox
        self.channel_listbox = tk.Listbox(
            channel_frame, bg=self.colors['grid_bg'],
            fg=self.colors['fg'], selectmode='single',
            font=('Arial', 10), height=8
        )
        self.channel_listbox.pack(fill='both', expand=True, padx=10, pady=10)
        self.channel_listbox.bind('<<ListboxSelect>>', self.on_channel_selected)
        
        # Channel buttons
        btn_frame = tk.Frame(channel_frame, bg=self.colors['bg'])
        btn_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Button(
            btn_frame, text="➕ Add", command=self.add_channel,
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            font=('Arial', 9), width=8
        ).pack(side='left', padx=2)
        
        tk.Button(
            btn_frame, text="✏️ Edit", command=self.edit_channel,
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            font=('Arial', 9), width=8
        ).pack(side='left', padx=2)
        
        tk.Button(
            btn_frame, text="🗑️ Delete", command=self.delete_channel,
            bg='#e74c3c', fg=self.colors['fg'],
            font=('Arial', 9), width=8
        ).pack(side='left', padx=2)
        
        # Shows section
        show_frame = tk.LabelFrame(
            parent, text="🎬 Shows", bg=self.colors['bg'],
            fg=self.colors['fg'], font=('Arial', 11, 'bold')
        )
        show_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Show listbox
        self.show_listbox = tk.Listbox(
            show_frame, bg=self.colors['grid_bg'],
            fg=self.colors['fg'], selectmode='single',
            font=('Arial', 10), height=10
        )
        self.show_listbox.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Enable drag from show listbox
        self.show_listbox.bind('<Button-1>', self.on_show_drag_start)
        self.show_listbox.bind('<B1-Motion>', self.on_show_drag_motion)
        
        # Show buttons
        show_btn_frame = tk.Frame(show_frame, bg=self.colors['bg'])
        show_btn_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Button(
            show_btn_frame, text="➕ Add Show", command=self.add_show,
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            font=('Arial', 9)
        ).pack(side='left', padx=2)
        
        tk.Button(
            show_btn_frame, text="✏️ Edit", command=self.edit_show,
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            font=('Arial', 9)
        ).pack(side='left', padx=2)
        
        tk.Button(
            show_btn_frame, text="🗑️ Delete", command=self.delete_show,
            bg='#e74c3c', fg=self.colors['fg'],
            font=('Arial', 9)
        ).pack(side='left', padx=2)
    
    def create_schedule_grid(self, parent):
        """Create the main schedule grid view"""
        
        # Grid container
        grid_frame = tk.LabelFrame(
            parent, text="📅 Weekly Schedule Grid", bg=self.colors['bg'],
            fg=self.colors['fg'], font=('Arial', 12, 'bold')
        )
        grid_frame.pack(fill='both', expand=True, padx=10)
        
        # Create canvas for scrollable grid
        canvas = tk.Canvas(grid_frame, bg=self.colors['grid_bg'], highlightthickness=0)
        canvas.pack(side='left', fill='both', expand=True)
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(grid_frame, orient='vertical', command=canvas.yview)
        v_scrollbar.pack(side='right', fill='y')
        
        h_scrollbar = tk.Scrollbar(grid_frame, orient='horizontal', command=canvas.xview)
        h_scrollbar.pack(side='bottom', fill='x')
        
        canvas.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Frame inside canvas
        self.grid_inner_frame = tk.Frame(canvas, bg=self.colors['grid_bg'])
        canvas.create_window((0, 0), window=self.grid_inner_frame, anchor='nw')
        
        # Store canvas reference
        self.schedule_canvas = canvas
        
        # Build grid
        self.build_schedule_grid()
        
        # Update canvas scroll region
        self.grid_inner_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox('all'))
        
        # Enable drop on canvas
        canvas.bind('<ButtonRelease-1>', self.on_grid_drop)
    
    def build_schedule_grid(self):
        """Build the actual schedule grid with time slots"""
        
        # Clear existing grid
        for widget in self.grid_inner_frame.winfo_children():
            widget.destroy()
        
        # Days of week
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Time slots (24 hours in 30-minute intervals = 48 slots)
        time_slots = []
        for hour in range(24):
            for minute in [0, 30]:
                time_str = f"{hour:02d}:{minute:02d}"
                time_slots.append(time_str)
        
        self.time_slots = time_slots
        
        # Header row with days
        tk.Label(
            self.grid_inner_frame, text="Time",
            bg=self.colors['header_bg'], fg=self.colors['fg'],
            font=('Arial', 10, 'bold'), width=8, relief='ridge'
        ).grid(row=0, column=0, sticky='nsew')
        
        for col, day in enumerate(days, 1):
            date = self.current_week_start + timedelta(days=col-1)
            tk.Label(
                self.grid_inner_frame, 
                text=f"{day}\n{date.strftime('%m/%d')}",
                bg=self.colors['header_bg'], fg=self.colors['fg'],
                font=('Arial', 10, 'bold'), relief='ridge'
            ).grid(row=0, column=col, sticky='nsew')
        
        # Time slots and grid cells
        self.grid_cells = {}
        
        for row, time_str in enumerate(time_slots, 1):
            # Time label
            tk.Label(
                self.grid_inner_frame, text=time_str,
                bg=self.colors['header_bg'], fg=self.colors['fg'],
                font=('Arial', 9), width=8, relief='ridge'
            ).grid(row=row, column=0, sticky='nsew')
            
            # Grid cells for each day
            for col in range(1, 8):
                date = self.current_week_start + timedelta(days=col-1)
                slot_time = datetime.combine(date.date(), 
                                           datetime.strptime(time_str, "%H:%M").time())
                
                cell = tk.Frame(
                    self.grid_inner_frame, bg=self.colors['slot_empty'],
                    relief='ridge', borderwidth=1, width=120, height=25
                )
                cell.grid(row=row, column=col, sticky='nsew', padx=1, pady=1)
                
                # Store cell reference
                cell_key = f"{date.strftime('%Y-%m-%d')}_{time_str}"
                self.grid_cells[cell_key] = cell
                
                # Bind click events
                cell.bind('<Button-1>', lambda e, key=cell_key: self.on_cell_click(key))
                cell.bind('<Double-Button-1>', lambda e, key=cell_key: self.on_cell_double_click(key))
                
                # Configure grid weights
                self.grid_inner_frame.grid_columnconfigure(col, weight=1, minsize=120)
        
        # Update grid content if schedule is loaded
        if self.current_schedule_id:
            self.update_grid_content()
    
    def create_right_panel(self, parent):
        """Create right panel with properties and actions"""
        
        # Quick Actions
        actions_frame = tk.LabelFrame(
            parent, text="⚡ Quick Actions", bg=self.colors['bg'],
            fg=self.colors['fg'], font=('Arial', 11, 'bold')
        )
        actions_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Button(
            actions_frame, text="🎲 Fill Randomly",
            command=self.fill_schedule_randomly,
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            font=('Arial', 10), width=18
        ).pack(padx=10, pady=5)
        
        tk.Button(
            actions_frame, text="📊 Sequential Fill",
            command=self.fill_schedule_sequential,
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            font=('Arial', 10), width=18
        ).pack(padx=10, pady=5)
        
        tk.Button(
            actions_frame, text="⚖️ Weighted Fill",
            command=self.fill_schedule_weighted,
            bg=self.colors['button_bg'], fg=self.colors['fg'],
            font=('Arial', 10), width=18
        ).pack(padx=10, pady=5)
        
        tk.Button(
            actions_frame, text="🔍 Check Conflicts",
            command=self.check_conflicts,
            bg='#f39c12', fg=self.colors['fg'],
            font=('Arial', 10), width=18
        ).pack(padx=10, pady=5)
        
        tk.Button(
            actions_frame, text="🎬 Simulate Viewing",
            command=self.simulate_viewing,
            bg='#27ae60', fg=self.colors['fg'],
            font=('Arial', 10), width=18
        ).pack(padx=10, pady=5)
        
        # Properties
        props_frame = tk.LabelFrame(
            parent, text="ℹ️ Slot Properties", bg=self.colors['bg'],
            fg=self.colors['fg'], font=('Arial', 11, 'bold')
        )
        props_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.slot_info = tk.Text(
            props_frame, bg=self.colors['grid_bg'],
            fg=self.colors['fg'], font=('Arial', 9),
            height=10, width=25, wrap='word'
        )
        self.slot_info.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Statistics
        stats_frame = tk.LabelFrame(
            parent, text="📈 Statistics", bg=self.colors['bg'],
            fg=self.colors['fg'], font=('Arial', 11, 'bold')
        )
        stats_frame.pack(fill='both', expand=True, padx=10)
        
        self.stats_text = tk.Text(
            stats_frame, bg=self.colors['grid_bg'],
            fg=self.colors['fg'], font=('Arial', 9),
            height=8, width=25, wrap='word'
        )
        self.stats_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_status_bar(self, parent):
        """Create status bar at bottom"""
        status_frame = tk.Frame(parent, bg=self.colors['header_bg'], height=30)
        status_frame.pack(fill='x', side='bottom')
        
        self.status_label = tk.Label(
            status_frame, text="Ready", bg=self.colors['header_bg'],
            fg=self.colors['fg'], font=('Arial', 10), anchor='w'
        )
        self.status_label.pack(side='left', padx=10, pady=5)
        
        # Schedule info
        self.schedule_info_label = tk.Label(
            status_frame, text="", bg=self.colors['header_bg'],
            fg=self.colors['fg'], font=('Arial', 10), anchor='e'
        )
        self.schedule_info_label.pack(side='right', padx=10, pady=5)
    
    # Helper methods
    def get_week_start(self, date):
        """Get the Monday of the week for given date"""
        days_since_monday = date.weekday()
        return date - timedelta(days=days_since_monday)
    
    def update_week_label(self):
        """Update the week label display"""
        end_date = self.current_week_start + timedelta(days=6)
        week_text = f"Week of {self.current_week_start.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
        self.week_label.config(text=week_text)
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    # Data loading methods
    def load_schedules(self):
        """Load all schedules into combo box"""
        schedules = self.db.get_schedules()
        schedule_names = [f"{s['name']} ({s['start_date']} to {s['end_date']})" 
                         for s in schedules]
        self.schedule_combo['values'] = schedule_names
        
        if schedules:
            self.schedule_combo.current(0)
            self.current_schedule_id = schedules[0]['schedule_id']
            self.update_week_label()
    
    def load_channels(self):
        """Load channels into listbox"""
        self.channel_listbox.delete(0, tk.END)
        channels = self.db.get_channels()
        for channel in channels:
            self.channel_listbox.insert(tk.END, channel['name'])
        
        if channels:
            self.channel_listbox.select_set(0)
            self.selected_channel_id = channels[0]['channel_id']
            self.load_shows()
    
    def load_shows(self):
        """Load shows for selected channel"""
        if not self.selected_channel_id:
            return
        
        self.show_listbox.delete(0, tk.END)
        shows = self.db.get_shows(self.selected_channel_id)
        for show in shows:
            self.show_listbox.insert(tk.END, f"{show['name']} ({show['duration_minutes']} min)")
    
    def update_grid_content(self):
        """Update grid cells with scheduled shows"""
        if not self.current_schedule_id:
            return
        
        # Clear all cells
        for cell in self.grid_cells.values():
            for widget in cell.winfo_children():
                widget.destroy()
            cell.config(bg=self.colors['slot_empty'])
        
        # Get time slots for current week
        week_end = self.current_week_start + timedelta(days=7)
        all_slots = self.db.get_time_slots(self.current_schedule_id)
        
        # Filter slots for current week
        for slot in all_slots:
            start_time = datetime.strptime(slot['start_time'], "%Y-%m-%d %H:%M:%S")
            
            if self.current_week_start <= start_time < week_end:
                # Find corresponding grid cell
                date_str = start_time.strftime('%Y-%m-%d')
                time_str = start_time.strftime('%H:%M')
                cell_key = f"{date_str}_{time_str}"
                
                if cell_key in self.grid_cells:
                    cell = self.grid_cells[cell_key]
                    
                    # Add show label to cell
                    label = tk.Label(
                        cell, text=slot['show_name'][:15] if slot['show_name'] else "Empty",
                        bg=self.colors['slot_filled'], fg=self.colors['fg'],
                        font=('Arial', 8), wraplength=110
                    )
                    label.pack(fill='both', expand=True)
                    
                    # Change cell color
                    cell.config(bg=self.colors['slot_filled'])
        
        # Update statistics
        self.update_statistics()
    
    def update_statistics(self):
        """Update statistics display"""
        if not self.current_schedule_id:
            return
        
        stats = self.db.get_schedule_statistics(self.current_schedule_id)
        utilization = self.manager.get_channel_utilization(self.current_schedule_id)
        
        stats_text = f"Total Slots: {stats.get('total_slots', 0)}\n"
        stats_text += f"Channels: {stats.get('total_channels', 0)}\n"
        stats_text += f"Days: {stats.get('total_days', 0)}\n\n"
        
        stats_text += "Channel Utilization:\n"
        for channel, util in utilization.items():
            stats_text += f"  {channel}: {util['utilization_percent']:.1f}%\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    # Event handlers
    def on_schedule_selected(self, event=None):
        """Handle schedule selection"""
        selection = self.schedule_combo.current()
        schedules = self.db.get_schedules()
        if 0 <= selection < len(schedules):
            self.current_schedule_id = schedules[selection]['schedule_id']
            self.update_grid_content()
            self.update_status(f"Loaded schedule: {schedules[selection]['name']}")
    
    def on_channel_selected(self, event=None):
        """Handle channel selection"""
        selection = self.channel_listbox.curselection()
        if selection:
            channels = self.db.get_channels()
            self.selected_channel_id = channels[selection[0]]['channel_id']
            self.load_shows()
    
    def on_cell_click(self, cell_key):
        """Handle single click on grid cell"""
        # Highlight selected cell
        if self.selected_slot:
            if self.selected_slot in self.grid_cells:
                self.grid_cells[self.selected_slot].config(
                    bg=self.colors['slot_empty'] if not self.grid_cells[self.selected_slot].winfo_children() 
                    else self.colors['slot_filled']
                )
        
        self.selected_slot = cell_key
        self.grid_cells[cell_key].config(bg=self.colors['slot_selected'])
        
        # Show slot info
        self.show_slot_info(cell_key)
    
    def on_cell_double_click(self, cell_key):
        """Handle double click on grid cell"""
        # Parse cell key
        parts = cell_key.split('_')
        date_str = parts[0]
        time_str = parts[1]
        
        # Quick add show dialog
        self.quick_add_show_to_slot(date_str, time_str)
    
    def show_slot_info(self, cell_key):
        """Display information about selected slot"""
        parts = cell_key.split('_')
        date_str = parts[0]
        time_str = parts[1]
        
        info_text = f"Date: {date_str}\n"
        info_text += f"Time: {time_str}\n\n"
        
        # Check if slot has content
        if self.current_schedule_id:
            slot_time = f"{date_str} {time_str}:00"
            slots = self.db.get_time_slots(self.current_schedule_id)
            
            for slot in slots:
                if slot['start_time'] <= slot_time < slot['end_time']:
                    info_text += f"Show: {slot['show_name']}\n"
                    info_text += f"Channel: {slot['channel_name']}\n"
                    info_text += f"Duration: {slot['duration_minutes']} min\n"
                    if slot['show_description']:
                        info_text += f"\n{slot['show_description']}"
                    break
            else:
                info_text += "Slot is empty"
        
        self.slot_info.delete(1.0, tk.END)
        self.slot_info.insert(1.0, info_text)
    
    # Drag and drop methods
    def on_show_drag_start(self, event):
        """Start dragging a show"""
        selection = self.show_listbox.curselection()
        if selection:
            shows = self.db.get_shows(self.selected_channel_id)
            if selection[0] < len(shows):
                self.drag_data = {
                    'show_id': shows[selection[0]]['show_id'],
                    'show_name': shows[selection[0]]['name'],
                    'duration': shows[selection[0]]['duration_minutes'],
                    'channel_id': self.selected_channel_id
                }
    
    def on_show_drag_motion(self, event):
        """Handle drag motion"""
        # Visual feedback during drag (optional)
        pass
    
    def on_grid_drop(self, event):
        """Handle drop on grid"""
        if not self.drag_data:
            return
        
        # Find which cell the drop occurred in
        x = self.schedule_canvas.canvasx(event.x)
        y = self.schedule_canvas.canvasy(event.y)
        
        # This is simplified - in production you'd calculate exact cell
        # For now, use selected slot
        if self.selected_slot:
            self.add_show_to_slot(self.selected_slot, self.drag_data)
        
        # Clear drag data
        self.drag_data = {}
    
    def add_show_to_slot(self, cell_key, show_data):
        """Add a show to a time slot"""
        if not self.current_schedule_id:
            messagebox.showwarning("No Schedule", "Please create or select a schedule first")
            return
        
        parts = cell_key.split('_')
        date_str = parts[0]
        time_str = parts[1]
        
        # Calculate start and end times
        start_time = f"{date_str} {time_str}:00"
        start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        end_dt = start_dt + timedelta(minutes=show_data['duration'])
        end_time = end_dt.strftime("%Y-%m-%d %H:%M:%S")
        
        # Check for conflicts
        if self.db.check_time_conflict(
            self.current_schedule_id, show_data['channel_id'],
            start_time, end_time
        ):
            messagebox.showwarning("Conflict", "This time slot conflicts with existing programming")
            return
        
        # Add to database
        self.db.add_time_slot(
            self.current_schedule_id,
            show_data['channel_id'],
            show_data['show_id'],
            start_time,
            end_time
        )
        
        # Update display
        self.update_grid_content()
        self.update_status(f"Added {show_data['show_name']} to schedule")
    
    # Action methods
    def new_schedule(self):
        """Create a new schedule"""
        dialog = ScheduleDialog(self.root, "New Schedule")
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            schedule_id = self.db.create_schedule(
                dialog.result['name'],
                dialog.result['start_date'],
                dialog.result['end_date']
            )
            self.current_schedule_id = schedule_id
            self.load_schedules()
            self.update_grid_content()
            self.update_status(f"Created new schedule: {dialog.result['name']}")
    
    def save_schedule(self):
        """Save current schedule"""
        if not self.current_schedule_id:
            messagebox.showinfo("No Schedule", "No schedule to save")
            return
        
        # Schedule is automatically saved to database
        # This could export to file if needed
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            schedule_data = self.db.export_schedule(self.current_schedule_id)
            with open(filename, 'w') as f:
                json.dump(schedule_data, f, indent=2)
            self.update_status(f"Schedule exported to {filename}")
    
    def load_schedule(self):
        """Load schedule from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            with open(filename, 'r') as f:
                schedule_data = json.load(f)
            
            schedule_id = self.db.import_schedule(schedule_data)
            self.current_schedule_id = schedule_id
            self.load_schedules()
            self.update_grid_content()
            self.update_status(f"Schedule imported from {filename}")
    
    def add_channel(self):
        """Add new channel"""
        dialog = ChannelDialog(self.root, "Add Channel")
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.db.add_channel(
                dialog.result['name'],
                dialog.result.get('description', ''),
                dialog.result.get('group', '')
            )
            self.load_channels()
            self.update_status(f"Added channel: {dialog.result['name']}")
    
    def edit_channel(self):
        """Edit selected channel"""
        # Implementation would open edit dialog
        messagebox.showinfo("Edit Channel", "Edit channel functionality to be implemented")
    
    def delete_channel(self):
        """Delete selected channel"""
        selection = self.channel_listbox.curselection()
        if not selection:
            return
        
        if messagebox.askyesno("Delete Channel", "Delete selected channel and all its shows?"):
            channels = self.db.get_channels()
            channel_id = channels[selection[0]]['channel_id']
            self.db.delete_channel(channel_id)
            self.load_channels()
            self.update_status("Channel deleted")
    
    def add_show(self):
        """Add new show"""
        if not self.selected_channel_id:
            messagebox.showwarning("No Channel", "Please select a channel first")
            return
        
        dialog = ShowDialog(self.root, "Add Show")
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.db.add_show(
                self.selected_channel_id,
                dialog.result['name'],
                dialog.result['duration'],
                dialog.result.get('description', ''),
                dialog.result.get('genre', '')
            )
            self.load_shows()
            self.update_status(f"Added show: {dialog.result['name']}")
    
    def edit_show(self):
        """Edit selected show"""
        messagebox.showinfo("Edit Show", "Edit show functionality to be implemented")
    
    def delete_show(self):
        """Delete selected show"""
        selection = self.show_listbox.curselection()
        if not selection:
            return
        
        if messagebox.askyesno("Delete Show", "Delete selected show?"):
            shows = self.db.get_shows(self.selected_channel_id)
            show_id = shows[selection[0]]['show_id']
            self.db.delete_show(show_id)
            self.load_shows()
            self.update_status("Show deleted")
    
    def delete_selected_slot(self):
        """Delete the selected time slot"""
        if not self.selected_slot or not self.current_schedule_id:
            return
        
        # Find slot in database
        parts = self.selected_slot.split('_')
        date_str = parts[0]
        time_str = parts[1]
        slot_time = f"{date_str} {time_str}:00"
        
        slots = self.db.get_time_slots(self.current_schedule_id)
        for slot in slots:
            if slot['start_time'] <= slot_time < slot['end_time']:
                if messagebox.askyesno("Delete Slot", f"Delete {slot['show_name']} from this time slot?"):
                    self.db.delete_time_slot(slot['slot_id'])
                    self.update_grid_content()
                    self.update_status("Time slot deleted")
                break
    
    def fill_schedule_randomly(self):
        """Fill schedule with random shows"""
        if not self.current_schedule_id or not self.selected_channel_id:
            messagebox.showwarning("Selection Required", 
                                  "Please select a schedule and channel")
            return
        
        # Get date range for current week
        start_date = self.current_week_start.strftime("%Y-%m-%d")
        end_date = (self.current_week_start + timedelta(days=6)).strftime("%Y-%m-%d")
        
        result = self.manager.fill_schedule_randomly(
            self.current_schedule_id,
            self.selected_channel_id,
            start_date,
            end_date,
            max_consecutive=3,
            respect_duration=True,
            prime_time_weight=1.5
        )
        
        if result['success']:
            self.update_grid_content()
            self.update_status(f"Filled {result['slots_filled']} slots randomly")
        else:
            messagebox.showerror("Error", result.get('message', 'Failed to fill schedule'))
    
    def fill_schedule_sequential(self):
        """Fill schedule sequentially"""
        if not self.current_schedule_id or not self.selected_channel_id:
            messagebox.showwarning("Selection Required", 
                                  "Please select a schedule and channel")
            return
        
        start_date = self.current_week_start.strftime("%Y-%m-%d")
        end_date = (self.current_week_start + timedelta(days=6)).strftime("%Y-%m-%d")
        
        result = self.manager.fill_schedule_sequential(
            self.current_schedule_id,
            self.selected_channel_id,
            start_date,
            end_date
        )
        
        if result['success']:
            self.update_grid_content()
            self.update_status(f"Filled {result['slots_filled']} slots sequentially")
    
    def fill_schedule_weighted(self):
        """Fill schedule with weighted distribution"""
        if not self.current_schedule_id or not self.selected_channel_id:
            messagebox.showwarning("Selection Required", 
                                  "Please select a schedule and channel")
            return
        
        start_date = self.current_week_start.strftime("%Y-%m-%d")
        end_date = (self.current_week_start + timedelta(days=6)).strftime("%Y-%m-%d")
        
        result = self.manager.fill_schedule_weighted(
            self.current_schedule_id,
            self.selected_channel_id,
            start_date,
            end_date
        )
        
        if result['success']:
            self.update_grid_content()
            self.update_status(f"Filled {result['slots_filled']} slots with weighted distribution")
    
    def check_conflicts(self):
        """Check and resolve conflicts"""
        if not self.current_schedule_id:
            messagebox.showwarning("No Schedule", "Please select a schedule")
            return
        
        result = self.manager.resolve_conflicts(self.current_schedule_id)
        
        message = f"Found {result['conflicts_found']} conflicts\n"
        message += f"Resolved {result['conflicts_resolved']} automatically\n"
        
        if result['unresolved']:
            message += f"\nUnresolved conflicts: {len(result['unresolved'])}"
        
        messagebox.showinfo("Conflict Check", message)
        self.update_grid_content()
    
    def import_folder(self):
        """Import folder of media files"""
        folder = filedialog.askdirectory(title="Select folder with media files")
        if not folder:
            return
        
        scheduler = AutoScheduler()
        result = scheduler.import_folder(folder, 
                                        channel_name=Path(folder).name,
                                        channel_group="Auto Imported")
        
        if result['success']:
            self.load_channels()
            messagebox.showinfo("Import Complete", 
                              f"Imported {result['shows_imported']} shows\n"
                              f"Channel: {result['channel_name']}")
            self.update_status(f"Imported {result['shows_imported']} shows from {Path(folder).name}")
        else:
            messagebox.showerror("Import Error", result.get('message', 'Failed to import'))
    
    def auto_build_schedule(self):
        """Auto-build 24/7 schedule from channel"""
        if not self.selected_channel_id:
            messagebox.showwarning("No Channel", "Please select a channel")
            return
        
        scheduler = AutoScheduler()
        result = scheduler.auto_build_schedule(
            channel_id=self.selected_channel_id,
            schedule_name=f"Auto-Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            start_datetime="now",
            num_days=30,
            shuffle=True,
            enable_looping=True,
            slot_mode="exact_duration"
        )
        
        if result['success']:
            self.load_schedules()
            messagebox.showinfo("Schedule Created", 
                              f"Created {result['schedule_name']}\n"
                              f"Scheduled: {result['shows_scheduled']} slots\n"
                              f"Looping: {result['enable_looping']}")
            self.update_status(f"Auto-built schedule with {result['shows_scheduled']} slots")
        else:
            messagebox.showerror("Schedule Error", result.get('message', 'Failed to create'))
    
    def export_web_epg(self):
        """Export schedule as Web EPG JSON"""
        if not self.current_schedule_id:
            messagebox.showwarning("No Schedule", "Please select a schedule")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        scheduler = AutoScheduler()
        result = scheduler.export_web_epg_json(self.current_schedule_id, file_path)
        
        if result['success']:
            messagebox.showinfo("Export Complete",
                              f"Exported {result['program_count']} programs\n"
                              f"Saved to: {file_path}")
            self.update_status(f"Exported {result['program_count']} programs to JSON")
        else:
            messagebox.showerror("Export Error", result.get('message', 'Failed to export'))
    
    def rebuild_schedule(self):
        """Rebuild schedule with updated durations"""
        if not self.current_schedule_id:
            messagebox.showwarning("No Schedule", "Please select a schedule")
            return
        
        if messagebox.askyesno("Confirm", 
                              "This will refresh all show durations.\nContinue?"):
            scheduler = AutoScheduler()
            result = scheduler.rebuild_schedule(self.current_schedule_id)
            
            if result['success']:
                self.update_grid_content()
                messagebox.showinfo("Rebuild Complete",
                                  f"Updated {result['slots_updated']} slots")
                self.update_status(f"Rebuilt schedule: {result['slots_updated']} slots updated")
            else:
                messagebox.showerror("Rebuild Error", result.get('message', 'Failed to rebuild'))
    
    def simulate_viewing(self):
        """Simulate channel switching"""
        if not self.current_schedule_id:
            messagebox.showwarning("No Schedule", "Please select a schedule")
            return
        
        # Simple simulation dialog
        start_time = datetime.now().replace(hour=20, minute=0, second=0)
        events = self.manager.simulate_channel_switching(
            self.current_schedule_id,
            start_time.strftime("%Y-%m-%d %H:%M:%S"),
            duration_minutes=60,
            switch_interval_minutes=10
        )
        
        # Show simulation results
        result_text = "Channel Switching Simulation (1 hour):\n\n"
        for event in events[::10]:  # Show every 10th event for brevity
            result_text += f"{event['time']}: {event['channel']} - {event['show']}\n"
        
        messagebox.showinfo("Simulation Results", result_text)
    
    def quick_add_show_to_slot(self, date_str, time_str):
        """Quick add show to a specific time slot"""
        if not self.current_schedule_id or not self.selected_channel_id:
            messagebox.showwarning("Selection Required", 
                                  "Please select a schedule and channel")
            return
        
        shows = self.db.get_shows(self.selected_channel_id)
        if not shows:
            messagebox.showwarning("No Shows", "No shows available for this channel")
            return
        
        # Simple selection dialog
        show_names = [s['name'] for s in shows]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Show")
        dialog.geometry("300x400")
        
        tk.Label(dialog, text=f"Add show to {date_str} at {time_str}:").pack(pady=10)
        
        listbox = tk.Listbox(dialog)
        for name in show_names:
            listbox.insert(tk.END, name)
        listbox.pack(fill='both', expand=True, padx=20, pady=10)
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                show = shows[selection[0]]
                cell_key = f"{date_str}_{time_str}"
                show_data = {
                    'show_id': show['show_id'],
                    'show_name': show['name'],
                    'duration': show['duration_minutes'],
                    'channel_id': self.selected_channel_id
                }
                self.add_show_to_slot(cell_key, show_data)
                dialog.destroy()
        
        tk.Button(dialog, text="Add Show", command=on_select).pack(pady=10)
    
    def previous_week(self):
        """Navigate to previous week"""
        self.current_week_start -= timedelta(days=7)
        self.update_week_label()
        self.build_schedule_grid()
    
    def next_week(self):
        """Navigate to next week"""
        self.current_week_start += timedelta(days=7)
        self.update_week_label()
        self.build_schedule_grid()
    
    def refresh_schedule_view(self):
        """Refresh the schedule view"""
        self.update_grid_content()
        self.update_status("Schedule refreshed")


# Dialog classes
class ScheduleDialog:
    """Dialog for creating/editing schedules"""
    
    def __init__(self, parent, title):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x250")
        
        # Name
        tk.Label(self.dialog, text="Schedule Name:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.name_entry = tk.Entry(self.dialog, width=30)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Start date
        tk.Label(self.dialog, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.start_entry = tk.Entry(self.dialog, width=30)
        self.start_entry.grid(row=1, column=1, padx=10, pady=10)
        self.start_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # End date
        tk.Label(self.dialog, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.end_entry = tk.Entry(self.dialog, width=30)
        self.end_entry.grid(row=2, column=1, padx=10, pady=10)
        self.end_entry.insert(0, (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))
        
        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="Create", command=self.ok_clicked).pack(side='left', padx=10)
        tk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side='left', padx=10)
    
    def ok_clicked(self):
        self.result = {
            'name': self.name_entry.get(),
            'start_date': self.start_entry.get(),
            'end_date': self.end_entry.get()
        }
        self.dialog.destroy()


class ChannelDialog:
    """Dialog for adding/editing channels"""
    
    def __init__(self, parent, title):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        
        # Name
        tk.Label(self.dialog, text="Channel Name:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.name_entry = tk.Entry(self.dialog, width=30)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Description
        tk.Label(self.dialog, text="Description:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.desc_entry = tk.Entry(self.dialog, width=30)
        self.desc_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Group
        tk.Label(self.dialog, text="Group:").grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.group_entry = tk.Entry(self.dialog, width=30)
        self.group_entry.grid(row=2, column=1, padx=10, pady=10)
        
        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="Add", command=self.ok_clicked).pack(side='left', padx=10)
        tk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side='left', padx=10)
    
    def ok_clicked(self):
        self.result = {
            'name': self.name_entry.get(),
            'description': self.desc_entry.get(),
            'group': self.group_entry.get()
        }
        self.dialog.destroy()


class ShowDialog:
    """Dialog for adding/editing shows"""
    
    def __init__(self, parent, title):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        
        # Name
        tk.Label(self.dialog, text="Show Name:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.name_entry = tk.Entry(self.dialog, width=30)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Duration
        tk.Label(self.dialog, text="Duration (minutes):").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.duration_entry = tk.Entry(self.dialog, width=30)
        self.duration_entry.grid(row=1, column=1, padx=10, pady=10)
        self.duration_entry.insert(0, "30")
        
        # Description
        tk.Label(self.dialog, text="Description:").grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.desc_entry = tk.Entry(self.dialog, width=30)
        self.desc_entry.grid(row=2, column=1, padx=10, pady=10)
        
        # Genre
        tk.Label(self.dialog, text="Genre:").grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.genre_entry = tk.Entry(self.dialog, width=30)
        self.genre_entry.grid(row=3, column=1, padx=10, pady=10)
        
        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="Add", command=self.ok_clicked).pack(side='left', padx=10)
        tk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side='left', padx=10)
    
    def ok_clicked(self):
        try:
            duration = int(self.duration_entry.get())
        except ValueError:
            duration = 30
        
        self.result = {
            'name': self.name_entry.get(),
            'duration': duration,
            'description': self.desc_entry.get(),
            'genre': self.genre_entry.get()
        }
        self.dialog.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = TVScheduleCenter(root)
    root.mainloop()


if __name__ == "__main__":
    main()