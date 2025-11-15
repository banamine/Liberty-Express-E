#!/usr/bin/env python3
"""
NEXUS TV - Local Web Server
Run this to serve generated pages on http://localhost:5000
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 5000
DIRECTORY = Path.cwd()

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Expires', '0')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print("=" * 60)
        print("🌐 NEXUS TV WEB SERVER STARTED")
        print("=" * 60)
        print(f"\n✅ Server running at: http://localhost:{PORT}/")
        print(f"📁 Serving from: {DIRECTORY}")
        print(f"\n🎬 OPEN IN BROWSER:")
        print(f"   → http://localhost:{PORT}/")
        print(f"   → http://localhost:{PORT}/generated_pages/")
        print(f"\n⚠️  Press CTRL+C to stop the server\n")
        print("=" * 60)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped")
