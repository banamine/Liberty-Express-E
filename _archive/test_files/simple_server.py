#!/usr/bin/env python3
"""
Simple HTTP Server with CORS Support
Serves NEXUS TV pages and handles CORS issues
"""

import http.server
import socketserver
from pathlib import Path

PORT = 8000

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Request Handler with CORS headers"""
    
    def end_headers(self):
        # Add CORS headers to allow cross-origin requests
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    # Change to generated_pages directory if it exists
    pages_dir = Path('generated_pages')
    if pages_dir.exists():
        import os
        os.chdir(pages_dir)
        print(f"📁 Serving files from: {pages_dir.absolute()}")
    else:
        print(f"📁 Serving files from: {Path.cwd()}")
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"")
        print(f"╔══════════════════════════════════════════════════════════════════╗")
        print(f"║              SIMPLE WEB SERVER WITH CORS SUPPORT                 ║")
        print(f"╚══════════════════════════════════════════════════════════════════╝")
        print(f"")
        print(f"🌐 Server running at: http://localhost:{PORT}")
        print(f"")
        print(f"✅ CORS enabled - no cross-origin issues")
        print(f"✅ Cache disabled - always fresh content")
        print(f"")
        print(f"📖 To access your NEXUS TV pages:")
        print(f"   http://localhost:{PORT}/your-page.html")
        print(f"")
        print(f"Press Ctrl+C to stop the server")
        print(f"")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n\n🛑 Server stopped")
