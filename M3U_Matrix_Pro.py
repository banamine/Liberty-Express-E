#!/usr/bin/env python3
"""
ScheduleFlow M3U Matrix Pro - Desktop Control Application
Manages M3U playlists, generates players, exports schedules
"""

import json
import os
import sys
import subprocess
import requests
from pathlib import Path
from datetime import datetime

class M3UMatrixPro:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.config_file = self.base_dir / "m3u_matrix_settings.json"
        self.generated_dir = self.base_dir / "generated_pages"
        self.load_config()

    def load_config(self):
        """Load configuration from JSON"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                self.config = json.load(f)
        else:
            self.config = {"playlists": [], "schedules": [], "exports": []}

    def save_config(self):
        """Save configuration to JSON"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def import_m3u(self, filepath):
        """Import M3U playlist"""
        try:
            with open(filepath) as f:
                lines = f.readlines()
            
            playlist = {
                "name": Path(filepath).stem,
                "path": str(filepath),
                "items": [],
                "imported": datetime.now().isoformat()
            }
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    playlist["items"].append({
                        "url": line,
                        "label": Path(line).stem if '/' in line else line
                    })
            
            self.config["playlists"].append(playlist)
            self.save_config()
            return {"status": "success", "items": len(playlist["items"])}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def export_m3u(self, items, output_path):
        """Export items as M3U playlist"""
        try:
            m3u_content = "#EXTM3U\n"
            for item in items:
                label = item.get("label", "Item")
                url = item.get("url", "")
                m3u_content += f"#EXTINF:-1,{label}\n{url}\n"
            
            with open(output_path, 'w') as f:
                f.write(m3u_content)
            
            return {"status": "success", "path": str(output_path)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def export_to_caspar(self, schedule, output_path):
        """Export schedule to CasparCG XML format"""
        try:
            xml = '<?xml version="1.0" encoding="utf-8"?>\n<schedule>\n'
            for item in schedule:
                url = item.get("url", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                label = item.get("label", "Item")
                xml += f'  <event id="{item.get("id", "0")}"><uri>{url}</uri><label>{label}</label></event>\n'
            xml += '</schedule>'
            
            with open(output_path, 'w') as f:
                f.write(xml)
            
            return {"status": "success", "path": str(output_path)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_schedule(self, name, items):
        """Create a 24-hour schedule"""
        try:
            schedule = {
                "name": name,
                "items": items,
                "created": datetime.now().isoformat(),
                "duration_seconds": sum(item.get("duration", 300) for item in items)
            }
            self.config["schedules"].append(schedule)
            self.save_config()
            return {"status": "success", "schedule": schedule}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_playlists(self):
        """Get all loaded playlists"""
        return {
            "status": "success",
            "playlists": self.config.get("playlists", []),
            "count": len(self.config.get("playlists", []))
        }

    def get_schedules(self):
        """Get all schedules"""
        return {
            "status": "success",
            "schedules": self.config.get("schedules", []),
            "count": len(self.config.get("schedules", []))
        }

    def list_generated_pages(self):
        """List all generated HTML pages"""
        try:
            if not self.generated_dir.exists():
                return {"status": "error", "message": "generated_pages directory not found"}
            
            pages = []
            for f in self.generated_dir.glob("*.html"):
                pages.append({
                    "name": f.name,
                    "path": str(f),
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                })
            
            return {"status": "success", "pages": pages, "count": len(pages)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_system_info(self):
        """Get system information"""
        playlists = len(self.config.get("playlists", []))
        schedules = len(self.config.get("schedules", []))
        
        if self.generated_dir.exists():
            pages = len(list(self.generated_dir.glob("*.html")))
        else:
            pages = 0
        
        return {
            "status": "success",
            "version": "2.0.0",
            "playlists_loaded": playlists,
            "schedules_created": schedules,
            "pages_generated": pages,
            "config_path": str(self.config_file),
            "generated_dir": str(self.generated_dir)
        }

    def clear_config(self):
        """Clear all configurations"""
        self.config = {"playlists": [], "schedules": [], "exports": []}
        self.save_config()
        return {"status": "success", "message": "All configurations cleared"}


# API Endpoints for web integration
def get_api_server():
    """Start a local API server for the web UI"""
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    matrix = M3UMatrixPro()
    
    @app.route('/api/playlists', methods=['GET'])
    def list_playlists():
        return jsonify(matrix.get_playlists())
    
    @app.route('/api/schedules', methods=['GET'])
    def list_schedules():
        return jsonify(matrix.get_schedules())
    
    @app.route('/api/pages', methods=['GET'])
    def list_pages():
        return jsonify(matrix.list_generated_pages())
    
    @app.route('/api/system-info', methods=['GET'])
    def system_info():
        return jsonify(matrix.get_system_info())
    
    @app.route('/api/import-m3u', methods=['POST'])
    def import_playlist():
        data = request.json
        result = matrix.import_m3u(data.get('filepath'))
        return jsonify(result)
    
    @app.route('/api/create-schedule', methods=['POST'])
    def create_schedule():
        data = request.json
        result = matrix.create_schedule(data.get('name'), data.get('items', []))
        return jsonify(result)
    
    @app.route('/api/export-m3u', methods=['POST'])
    def export_playlist():
        data = request.json
        result = matrix.export_m3u(data.get('items', []), data.get('output_path'))
        return jsonify(result)
    
    @app.route('/api/export-caspar', methods=['POST'])
    def export_caspar():
        data = request.json
        result = matrix.export_to_caspar(data.get('schedule', []), data.get('output_path'))
        return jsonify(result)
    
    @app.route('/api/clear-all', methods=['POST'])
    def clear_all():
        return jsonify(matrix.clear_config())
    
    return app


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ScheduleFlow M3U Matrix Pro")
    parser.add_argument('--server', action='store_true', help='Start Flask API server')
    parser.add_argument('--port', type=int, default=5001, help='API server port')
    parser.add_argument('--info', action='store_true', help='Show system info')
    parser.add_argument('--import-m3u', metavar='FILE', help='Import M3U playlist')
    parser.add_argument('--list-playlists', action='store_true', help='List all playlists')
    parser.add_argument('--list-schedules', action='store_true', help='List all schedules')
    parser.add_argument('--list-pages', action='store_true', help='List generated pages')
    
    args = parser.parse_args()
    matrix = M3UMatrixPro()
    
    if args.server:
        print(f"🚀 Starting ScheduleFlow API server on port {args.port}...")
        app = get_api_server()
        app.run(host='127.0.0.1', port=args.port, debug=False)
    elif args.info:
        print(json.dumps(matrix.get_system_info(), indent=2))
    elif args.import_m3u:
        print(json.dumps(matrix.import_m3u(args.import_m3u), indent=2))
    elif args.list_playlists:
        print(json.dumps(matrix.get_playlists(), indent=2))
    elif args.list_schedules:
        print(json.dumps(matrix.get_schedules(), indent=2))
    elif args.list_pages:
        print(json.dumps(matrix.list_generated_pages(), indent=2))
    else:
        print("ScheduleFlow M3U Matrix Pro v2.0.0")
        print("Use --help for available commands")
        print("\nQuick start:")
        print("  python M3U_Matrix_Pro.py --info              # Show system info")
        print("  python M3U_Matrix_Pro.py --list-pages        # List generated pages")
        print("  python M3U_Matrix_Pro.py --import-m3u FILE   # Import playlist")
        print("  python M3U_Matrix_Pro.py --server --port 5001 # Start API server")
