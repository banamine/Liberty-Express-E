"""
GUI Components - Reusable GUI components and utilities
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict, Any, Tuple
import logging


class ButtonFactory:
    """
    Factory for creating styled buttons with smart text color.
    """
    
    @staticmethod
    def get_contrasting_text_color(bg_color: str) -> str:
        """
        Calculate if text should be dark or light based on background brightness.
        
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
    
    @staticmethod
    def create_styled_button(parent: tk.Widget, text: str, command: Callable,
                           bg_color: str = "#F2E1C1", width: int = 15,
                           font_size: int = 10, font_weight: str = "bold") -> tk.Button:
        """
        Create a button with smart text color and consistent styling.
        
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
        fg_color = ButtonFactory.get_contrasting_text_color(bg_color)
        
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
        
        # Add hover effect
        def on_enter(e):
            button.configure(relief=tk.RAISED, bd=3)
        
        def on_leave(e):
            button.configure(relief=tk.RAISED, bd=2)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button


class DialogFactory:
    """
    Factory for creating dialogs and windows.
    """
    
    @staticmethod
    def create_error_dialog(parent: tk.Widget, title: str, message: str,
                          exception: Optional[Exception] = None) -> tk.Toplevel:
        """
        Create user-friendly error dialog with helpful suggestions.
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Error message
            exception: Optional exception for technical details
            
        Returns:
            Error dialog window
        """
        logger = logging.getLogger(__name__)
        
        # Log the full error
        if exception:
            logger.error(f"{title}: {message} - {str(exception)}")
        else:
            logger.error(f"{title}: {message}")
        
        # Create dialog
        dialog = tk.Toplevel(parent)
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
        suggestions = DialogFactory._get_error_suggestions(message, exception)
        
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
        
        return dialog
    
    @staticmethod
    def _get_error_suggestions(message: str, exception: Optional[Exception]) -> list:
        """
        Get helpful suggestions based on error type.
        
        Args:
            message: Error message
            exception: Optional exception
            
        Returns:
            List of suggestion strings
        """
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
        
        return suggestions


class ProgressManager:
    """
    Manages progress dialogs and updates.
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize the progress manager.
        
        Args:
            parent: Parent widget
        """
        self.parent = parent
        self.dialog: Optional[tk.Toplevel] = None
        self.progress_var: Optional[tk.IntVar] = None
        self.status_label: Optional[tk.Label] = None
        self.cancel_flag: Dict[str, bool] = {"cancelled": False}
    
    def show_progress(self, title: str, max_value: int) -> None:
        """
        Show progress dialog.
        
        Args:
            title: Dialog title
            max_value: Maximum progress value
        """
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.configure(bg="#1e1e1e")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Title label
        tk.Label(self.dialog, text=title, font=("Arial", 12, "bold"),
                bg="#1e1e1e", fg="white").pack(pady=10)
        
        # Progress bar
        self.progress_var = tk.IntVar()
        progress_bar = ttk.Progressbar(self.dialog, variable=self.progress_var,
                                       maximum=max_value, length=350)
        progress_bar.pack(pady=10, padx=25)
        
        # Status label
        self.status_label = tk.Label(self.dialog, text="Starting...",
                                    bg="#1e1e1e", fg="#aaa")
        self.status_label.pack(pady=5)
        
        # Cancel button
        tk.Button(self.dialog, text="Cancel", command=self.cancel,
                 bg="#e74c3c", fg="white", width=10).pack(pady=10)
        
        # Prevent closing with X button
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def update_progress(self, value: int, status: str = "") -> None:
        """
        Update progress dialog.
        
        Args:
            value: Progress value
            status: Status text
        """
        if self.progress_var:
            self.progress_var.set(value)
        
        if self.status_label and status:
            self.status_label.config(text=status)
        
        if self.dialog:
            self.dialog.update()
    
    def cancel(self) -> None:
        """Cancel operation and close dialog"""
        self.cancel_flag["cancelled"] = True
        self.close()
    
    def close(self) -> None:
        """Close progress dialog"""
        if self.dialog:
            self.dialog.destroy()
            self.dialog = None
        
        self.progress_var = None
        self.status_label = None
    
    def is_cancelled(self) -> bool:
        """
        Check if operation was cancelled.
        
        Returns:
            True if cancelled
        """
        return self.cancel_flag.get("cancelled", False)
    
    def reset(self) -> None:
        """Reset cancel flag"""
        self.cancel_flag["cancelled"] = False


class TreeviewManager:
    """
    Manages treeview operations and styling.
    """
    
    @staticmethod
    def setup_treeview_style() -> None:
        """Setup treeview styling"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                       background="#1e1e1e",
                       foreground="#ffffff",
                       fieldbackground="#1e1e1e",
                       rowheight=28)
        style.configure("Treeview.Heading",
                       background="#333",
                       foreground="gold",
                       font=("Arial", 11, "bold"))
    
    @staticmethod
    def create_channel_treeview(parent: tk.Widget) -> ttk.Treeview:
        """
        Create a styled treeview for channels.
        
        Args:
            parent: Parent widget
            
        Returns:
            Configured treeview widget
        """
        columns = ("#", "Now Playing", "Next", "Group", "Name", "URL", 
                  "Backs", "Tags", "Del")
        
        tv = ttk.Treeview(parent, columns=columns, show="headings")
        
        # Column configuration with responsive sizing
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
        
        for col in columns:
            width, minwidth, stretch = column_config[col]
            tv.column(col,
                     width=width,
                     minwidth=minwidth,
                     stretch=stretch,
                     anchor="center" if col in ("#", "Backs", "Tags", "Del") else "w")
            tv.heading(col, text=col)
        
        return tv