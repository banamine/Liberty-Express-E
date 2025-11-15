"""
M3U Matrix Redis Integration Patch
Add this code to M3U_MATRIX_PRO.py to enable Redis export
"""

# ADD TO IMPORTS (line 15):
"""
try:
    from redis_exporter import get_redis_exporter
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    get_redis_exporter = None
"""

# ADD TO __init__ method (after line 176):
"""
        # Redis exporter
        self.redis_exporter = None
        if REDIS_AVAILABLE:
            self.redis_exporter = get_redis_exporter()
            self.logger.info("Redis exporter initialized")
"""

# ADD TO build_ui method ROW 1 buttons (line 343-347):
"""
        # ROW 1: File Operations
        tb1 = tk.Frame(toolbar_container, bg="#1e1e1e")
        tb1.pack(fill=tk.X, pady=2)
        row1 = [("LOAD", "#2980b9", self.load),
                ("SAVE", "#c0392b", self.save),
                ("M3U OUTPUT", "#16a085", self.export_m3u_output),
                ("EXPORT JSON", "#16a085", self.export_json),
                ("EXPORT REDIS", "#FF5733", self.export_to_redis),  # NEW BUTTON
                ("NEW", "#34495e", self.new_project)]
"""

# ADD THIS METHOD (after export_json method, around line 2500):
"""
    def export_to_redis(self):
        '''Export channels to Redis cache'''
        if not REDIS_AVAILABLE:
            messagebox.showwarning(
                "Redis Not Available",
                "Redis integration is not installed.\\n\\n"
                "Install with: pip install redis\\n\\n"
                "Then restart M3U Matrix."
            )
            return
        
        if not self.channels:
            messagebox.showwarning("No Channels", "Load a playlist first!")
            return
        
        # Show progress dialog
        progress_win = tk.Toplevel(self.root)
        progress_win.title("Exporting to Redis")
        progress_win.geometry("500x200")
        progress_win.configure(bg="#1a1a2e")
        progress_win.transient(self.root)
        progress_win.grab_set()
        
        tk.Label(
            progress_win,
            text="📡 Exporting Channels to Redis",
            font=("Arial", 16, "bold"),
            fg="#00ff88",
            bg="#1a1a2e"
        ).pack(pady=20)
        
        status_label = tk.Label(
            progress_win,
            text="Connecting to Redis...",
            font=("Arial", 12),
            fg="#ffffff",
            bg="#1a1a2e"
        )
        status_label.pack(pady=10)
        
        progress = ttk.Progressbar(
            progress_win,
            length=400,
            mode='indeterminate'
        )
        progress.pack(pady=20)
        progress.start()
        
        def do_export():
            try:
                # Connect to Redis
                if not self.redis_exporter.connect():
                    progress_win.after(0, lambda: messagebox.showerror(
                        "Redis Connection Failed",
                        "Could not connect to Redis server.\\n\\n"
                        "Make sure Redis is running on localhost:6379\\n\\n"
                        "Start with: redis\\START_ALL_SERVICES.bat"
                    ))
                    progress_win.after(0, progress_win.destroy)
                    return
                
                status_label.config(text=f"Exporting {len(self.channels)} channels...")
                
                # Prepare channel data with timestamps
                from datetime import datetime
                export_time = datetime.now().isoformat()
                
                channels_for_export = []
                for ch in self.channels:
                    channel_data = ch.copy()
                    channel_data['exported_at'] = export_time
                    channels_for_export.append(channel_data)
                
                # Export to Redis
                success = self.redis_exporter.export_channels(channels_for_export)
                
                if success:
                    stats = self.redis_exporter.get_stats()
                    progress_win.after(0, lambda: messagebox.showinfo(
                        "Export Successful",
                        f"✅ Exported {len(self.channels)} channels to Redis!\\n\\n"
                        f"📊 Cache Statistics:\\n"
                        f"   • Total Channels: {stats.get('channels', 0)}\\n"
                        f"   • Total Keys: {stats.get('total_keys', 0)}\\n"
                        f"   • Memory Used: {stats.get('memory_used', 'N/A')}\\n\\n"
                        f"🌐 View dashboard at: http://localhost:8080\\n"
                        f"📡 API available at: http://localhost:3000"
                    ))
                    progress_win.after(0, lambda: self.stat.config(
                        text=f"✅ Exported {len(self.channels)} channels to Redis"
                    ))
                else:
                    progress_win.after(0, lambda: messagebox.showerror(
                        "Export Failed",
                        "Failed to export channels to Redis.\\n\\n"
                        "Check the logs for details."
                    ))
                
            except Exception as e:
                self.logger.error(f"Redis export error: {e}")
                progress_win.after(0, lambda: messagebox.showerror(
                    "Export Error",
                    f"Error exporting to Redis:\\n\\n{str(e)}"
                ))
            finally:
                progress_win.after(0, progress.stop)
                progress_win.after(0, progress_win.destroy)
        
        # Run export in background thread
        threading.Thread(target=do_export, daemon=True).start()
"""

print("Redis integration code ready!")
print("\nTo integrate into M3U_MATRIX_PRO.py:")
print("1. Add imports at the top")
print("2. Add redis_exporter initialization in __init__")
print("3. Update build_ui row1 to include EXPORT REDIS button")
print("4. Add export_to_redis method")
print("\nOr run the automatic patcher script!")
