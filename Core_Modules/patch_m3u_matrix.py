"""
Automatic patcher to add Redis export to M3U Matrix PRO
Run this to automatically integrate Redis export functionality
"""

import re
from pathlib import Path

def patch_m3u_matrix():
    """Patch M3U_MATRIX_PRO.py to add Redis export"""
    
    m3u_path = Path("../src/M3U_MATRIX_PRO.py")
    
    if not m3u_path.exists():
        print("❌ M3U_MATRIX_PRO.py not found!")
        return False
    
    print("📖 Reading M3U_MATRIX_PRO.py...")
    with open(m3u_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already patched
    if 'export_to_redis' in content:
        print("✅ Already patched! Redis export is already integrated.")
        return True
    
    print("🔧 Patching file...")
    
    # 1. Add import
    import_patch = """try:
    from redis_exporter import get_redis_exporter
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    get_redis_exporter = None

"""
    
    # Find where to add import (after PAGE_GENERATOR_AVAILABLE block)
    content = content.replace(
        "except ImportError:\n    PAGE_GENERATOR_AVAILABLE = False\n\n",
        "except ImportError:\n    PAGE_GENERATOR_AVAILABLE = False\n\n" + import_patch
    )
    
    # 2. Add to __init__
    init_patch = """
        # Redis exporter
        self.redis_exporter = None
        if REDIS_AVAILABLE:
            self.redis_exporter = get_redis_exporter()
            self.logger.info("Redis exporter initialized")
"""
    
    # Find __init__ initialization section
    content = content.replace(
        "        # Theme (dark/light)",
        init_patch + "        # Theme (dark/light)"
    )
    
    # 3. Add button to toolbar
    content = content.replace(
        '        row1 = [("LOAD", "#2980b9", self.load),\n'
        '                ("SAVE", "#c0392b", self.save),\n'
        '                ("M3U OUTPUT", "#16a085", self.export_m3u_output),\n'
        '                ("EXPORT JSON", "#16a085", self.export_json),\n'
        '                ("NEW", "#34495e", self.new_project)]',
        
        '        row1 = [("LOAD", "#2980b9", self.load),\n'
        '                ("SAVE", "#c0392b", self.save),\n'
        '                ("M3U OUTPUT", "#16a085", self.export_m3u_output),\n'
        '                ("EXPORT JSON", "#16a085", self.export_json),\n'
        '                ("EXPORT REDIS", "#FF5733", self.export_to_redis),\n'
        '                ("NEW", "#34495e", self.new_project)]'
    )
    
    # 4. Add export_to_redis method (find a good place after export_json)
    method_code = '''
    def export_to_redis(self):
        """Export channels to Redis cache"""
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
                        "Start with: redis\\\\START_ALL_SERVICES.bat"
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
'''
    
    # Find where to insert (after export_json method)
    # Look for the end of export_json method
    content = content.replace(
        '    def export_json(self):',
        method_code + '\n    def export_json(self):'
    )
    
    # Write patched file
    backup_path = m3u_path.with_suffix('.py.backup')
    print(f"💾 Creating backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content.replace(method_code + '\n    def export_json(self):', '    def export_json(self):'))
    
    print(f"✍️  Writing patched file...")
    with open(m3u_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "="*70)
    print("✅ PATCHING COMPLETE!")
    print("="*70)
    print("\n🎯 Changes made:")
    print("   1. ✅ Added Redis import")
    print("   2. ✅ Initialized Redis exporter in __init__")
    print("   3. ✅ Added 'EXPORT REDIS' button to toolbar")
    print("   4. ✅ Added export_to_redis() method")
    print(f"\n💾 Backup saved to: {backup_path}")
    print("\n🚀 Restart M3U Matrix to see the new 'EXPORT REDIS' button!")
    
    return True

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║     M3U MATRIX - Automatic Redis Integration Patcher           ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    
    success = patch_m3u_matrix()
    
    if success:
        print("\n🎉 Ready to export to Redis!")
        print("\nNext steps:")
        print("1. Start Redis services: redis\\START_ALL_SERVICES.bat")
        print("2. Launch M3U Matrix: python src\\M3U_MATRIX_PRO.py")
        print("3. Load a playlist and click 'EXPORT REDIS'")
        print("4. View dashboard at: http://localhost:8080")
    else:
        print("\n❌ Patching failed. Please check the error messages above.")
    
    input("\nPress Enter to exit...")
