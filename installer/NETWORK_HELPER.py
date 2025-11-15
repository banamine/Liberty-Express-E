"""
M3U MATRIX - Network Connection Helper
Automatic network discovery and one-click setup for non-technical users
"""

import tkinter as tk
from tkinter import messagebox, ttk
import socket
import subprocess
import threading
from pathlib import Path
import platform
import json
import os

class NetworkHelper:
    def __init__(self, parent=None):
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("M3U Matrix - Network Connection Helper")
        self.root.geometry("800x600")
        self.root.configure(bg="#1a1a2a")
        
        self.discovered_pcs = []
        self.selected_pc = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create network helper UI"""
        # Header
        header = tk.Frame(self.root, bg="#6b46c1", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🌐 Network Connection Helper", 
                font=("Arial", 20, "bold"), bg="#6b46c1", fg="#fff").pack(pady=20)
        
        # Content
        content = tk.Frame(self.root, bg="#1a1a2a")
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Instructions
        instr_frame = tk.Frame(content, bg="#2e2e4e", bd=2, relief=tk.RIDGE)
        instr_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(instr_frame, 
                text="📡 Click 'Scan Network' to find other computers on your network",
                font=("Arial", 11), bg="#2e2e4e", fg="#00f3ff",
                wraplength=700, justify=tk.LEFT).pack(padx=20, pady=15)
        
        # Network info
        info_frame = tk.LabelFrame(content, text="Your Computer Information",
                                   font=("Arial", 11, "bold"),
                                   bg="#2e2e4e", fg="#fff")
        info_frame.pack(fill=tk.X, pady=10)
        
        info_inner = tk.Frame(info_frame, bg="#2e2e4e")
        info_inner.pack(fill=tk.X, padx=20, pady=10)
        
        self.hostname = socket.gethostname()
        self.local_ip = self.get_local_ip()
        
        tk.Label(info_inner, text=f"Computer Name: {self.hostname}",
                font=("Arial", 10, "bold"), bg="#2e2e4e", fg="#2ecc71").pack(anchor=tk.W, pady=3)
        tk.Label(info_inner, text=f"IP Address: {self.local_ip}",
                font=("Arial", 10, "bold"), bg="#2e2e4e", fg="#2ecc71").pack(anchor=tk.W, pady=3)
        
        # Scan button
        scan_frame = tk.Frame(content, bg="#1a1a2a")
        scan_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(scan_frame, text="🔍 Scan Network for PCs", 
                 command=self.scan_network,
                 bg="#3498db", fg="#fff", font=("Arial", 12, "bold"),
                 width=30, height=2).pack(side=tk.LEFT, padx=5)
        
        tk.Button(scan_frame, text="🔄 Refresh", 
                 command=self.scan_network,
                 bg="#95a5a6", fg="#fff", font=("Arial", 12, "bold"),
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        # Progress
        self.progress = ttk.Progressbar(content, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=10)
        
        # Status
        self.status_label = tk.Label(content, text="Ready to scan network",
                                     font=("Arial", 10), bg="#1a1a2a", fg="#00f3ff")
        self.status_label.pack(pady=5)
        
        # Discovered PCs list
        list_frame = tk.LabelFrame(content, text="Available Computers on Your Network",
                                   font=("Arial", 11, "bold"),
                                   bg="#2e2e4e", fg="#fff")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview for PCs
        tree_frame = tk.Frame(list_frame, bg="#2e2e4e")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.pc_tree = ttk.Treeview(tree_frame, 
                                    columns=("hostname", "ip", "status"),
                                    show="headings", height=8)
        
        self.pc_tree.heading("hostname", text="Computer Name")
        self.pc_tree.heading("ip", text="IP Address")
        self.pc_tree.heading("status", text="Status")
        
        self.pc_tree.column("hostname", width=250)
        self.pc_tree.column("ip", width=150)
        self.pc_tree.column("status", width=200)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.pc_tree.yview)
        self.pc_tree.configure(yscroll=scrollbar.set)
        
        self.pc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons
        action_frame = tk.Frame(content, bg="#1a1a2a")
        action_frame.pack(fill=tk.X, pady=10)
        
        self.connect_btn = tk.Button(action_frame, text="✅ Connect to Selected PC",
                                     command=self.connect_to_pc,
                                     bg="#2ecc71", fg="#fff", font=("Arial", 12, "bold"),
                                     width=25, state=tk.DISABLED)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="📋 Show Connection Details",
                 command=self.show_connection_details,
                 bg="#f39c12", fg="#fff", font=("Arial", 12, "bold"),
                 width=25).pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="❌ Close",
                 command=self.root.destroy,
                 bg="#e74c3c", fg="#fff", font=("Arial", 12, "bold"),
                 width=15).pack(side=tk.LEFT, padx=5)
        
        # Bind selection
        self.pc_tree.bind("<<TreeviewSelect>>", self.on_pc_selected)
    
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "Unknown"
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        self.root.update()
    
    def scan_network(self):
        """Scan network for available PCs"""
        self.progress.start()
        self.update_status("🔍 Scanning network... This may take a moment...")
        self.pc_tree.delete(*self.pc_tree.get_children())
        
        # Run scan in background thread
        thread = threading.Thread(target=self._scan_network_thread)
        thread.daemon = True
        thread.start()
    
    def _scan_network_thread(self):
        """Background thread for network scanning"""
        discovered = []
        
        # Get network prefix (e.g., 192.168.1)
        if self.local_ip != "Unknown":
            ip_parts = self.local_ip.split('.')
            network_prefix = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
            
            # Scan common IP range
            for i in range(1, 255):
                ip = f"{network_prefix}.{i}"
                
                # Skip own IP
                if ip == self.local_ip:
                    continue
                
                # Try to resolve hostname
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                    
                    # Ping to verify reachability
                    param = '-n' if platform.system().lower() == 'windows' else '-c'
                    command = ['ping', param, '1', '-w', '500', ip]
                    
                    result = subprocess.run(command, 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE,
                                          timeout=2,
                                          creationflags=subprocess.CREATE_NO_WINDOW if platform.system().lower() == 'windows' else 0)
                    
                    if result.returncode == 0:
                        discovered.append({
                            'hostname': hostname,
                            'ip': ip,
                            'status': 'Online ✅'
                        })
                except:
                    # Try just ping without hostname resolution
                    try:
                        param = '-n' if platform.system().lower() == 'windows' else '-c'
                        command = ['ping', param, '1', '-w', '500', ip]
                        
                        result = subprocess.run(command,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE,
                                              timeout=2,
                                              creationflags=subprocess.CREATE_NO_WINDOW if platform.system().lower() == 'windows' else 0)
                        
                        if result.returncode == 0:
                            discovered.append({
                                'hostname': f'Computer at {ip}',
                                'ip': ip,
                                'status': 'Online ✅'
                            })
                    except:
                        pass
        
        # Update UI in main thread
        self.root.after(0, self._update_discovered_pcs, discovered)
    
    def _update_discovered_pcs(self, discovered):
        """Update UI with discovered PCs"""
        self.discovered_pcs = discovered
        
        for pc in discovered:
            self.pc_tree.insert("", tk.END, values=(
                pc['hostname'],
                pc['ip'],
                pc['status']
            ))
        
        self.progress.stop()
        
        if len(discovered) > 0:
            self.update_status(f"✅ Found {len(discovered)} computer(s) on your network!")
        else:
            self.update_status("⚠️ No other computers found. Make sure they are powered on and connected.")
    
    def on_pc_selected(self, event):
        """Handle PC selection"""
        selection = self.pc_tree.selection()
        if selection:
            self.connect_btn.config(state=tk.NORMAL)
            item = self.pc_tree.item(selection[0])
            values = item['values']
            
            self.selected_pc = {
                'hostname': values[0],
                'ip': values[1],
                'status': values[2]
            }
        else:
            self.connect_btn.config(state=tk.DISABLED)
            self.selected_pc = None
    
    def connect_to_pc(self):
        """Connect to selected PC"""
        if not self.selected_pc:
            messagebox.showwarning("No Selection", "Please select a computer first!")
            return
        
        pc_name = self.selected_pc['hostname']
        pc_ip = self.selected_pc['ip']
        
        # Show connection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Connect to Computer")
        dialog.geometry("600x400")
        dialog.configure(bg="#1a1a2a")
        
        tk.Label(dialog, text=f"🔗 Connecting to: {pc_name}",
                font=("Arial", 14, "bold"), bg="#1a1a2a", fg="#00f3ff").pack(pady=20)
        
        info_frame = tk.Frame(dialog, bg="#2e2e4e", bd=2, relief=tk.RIDGE)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(info_frame, text="Connection Information:",
                font=("Arial", 11, "bold"), bg="#2e2e4e", fg="#fff").pack(anchor=tk.W, padx=20, pady=10)
        
        info_text = f"""
Computer Name: {pc_name}
IP Address: {pc_ip}

Network Path: \\\\{pc_ip}\\M3U_Matrix

To complete the connection:

1. On {pc_name}, create a shared folder called "M3U_Matrix"
2. Set sharing permissions to allow network access
3. Use the network path above to access files

Or use the automatic network deployment:
1. Run NETWORK_DEPLOY.bat on this computer (PUNK)
2. Enter path: \\\\{pc_ip}\\M3U_Matrix
3. On {pc_name}, run INSTALL_FROM_NETWORK.bat
"""
        
        tk.Label(info_frame, text=info_text,
                font=("Arial", 10), bg="#2e2e4e", fg="#fff",
                justify=tk.LEFT).pack(anchor=tk.W, padx=20, pady=10)
        
        # Copy path button
        def copy_path():
            path = f"\\\\{pc_ip}\\M3U_Matrix"
            self.root.clipboard_clear()
            self.root.clipboard_append(path)
            messagebox.showinfo("Copied!", f"Network path copied to clipboard:\n{path}")
        
        tk.Button(info_frame, text="📋 Copy Network Path",
                 command=copy_path,
                 bg="#3498db", fg="#fff", font=("Arial", 11, "bold")).pack(pady=10)
        
        tk.Button(dialog, text="Close", command=dialog.destroy,
                 bg="#e74c3c", fg="#fff", font=("Arial", 11, "bold"),
                 width=20).pack(pady=20)
    
    def show_connection_details(self):
        """Show detailed connection information"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Connection Details")
        dialog.geometry("700x500")
        dialog.configure(bg="#1a1a2a")
        
        tk.Label(dialog, text="📋 Network Connection Guide",
                font=("Arial", 16, "bold"), bg="#1a1a2a", fg="#00f3ff").pack(pady=20)
        
        details_frame = tk.Frame(dialog, bg="#2e2e4e", bd=2, relief=tk.RIDGE)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        details_text = f"""
YOUR COMPUTER (Server):
  Name: {self.hostname}
  IP: {self.local_ip}

STEP-BY-STEP SETUP:

Option 1: Automatic (Easiest!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. On this computer ({self.hostname}):
   • Run: installer\\NETWORK_DEPLOY.bat
   • Enter network path when prompted

2. On other computers:
   • Open the network path shown above
   • Run: INSTALL_FROM_NETWORK.bat
   • Done!

Option 2: Manual Setup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. On this computer ({self.hostname}):
   • Create a shared folder called "M3U_Matrix"
   • Copy M3U Matrix files to this folder
   • Right-click → Properties → Sharing → Share

2. On other computers:
   • Open File Explorer
   • Type in address bar: \\\\{self.local_ip}\\M3U_Matrix
   • Run START_M3U_MATRIX.bat

Quick Tips:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ All computers must be on the same network
✅ Windows Firewall may need to allow file sharing
✅ Use NETWORK_DEPLOY.bat for easiest setup
✅ Both computers can access the same playlists
"""
        
        text_widget = tk.Text(details_frame, bg="#1a1a2a", fg="#fff",
                             font=("Consolas", 9), wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        text_widget.insert(1.0, details_text)
        text_widget.config(state=tk.DISABLED)
        
        tk.Button(dialog, text="Close", command=dialog.destroy,
                 bg="#e74c3c", fg="#fff", font=("Arial", 11, "bold"),
                 width=20).pack(pady=15)
    
    def run(self):
        """Run network helper"""
        self.root.mainloop()


if __name__ == "__main__":
    helper = NetworkHelper()
    helper.run()
