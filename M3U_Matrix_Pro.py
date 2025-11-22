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


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ScheduleFlow M3U Matrix Pro - CLI Control Tool")
    parser.add_argument('--info', action='store_true', help='Show system info')
    parser.add_argument('--import-m3u', metavar='FILE', help='Import M3U playlist')
    parser.add_argument('--list-playlists', action='store_true', help='List all playlists')
    parser.add_argument('--list-schedules', action='store_true', help='List all schedules')
    parser.add_argument('--list-pages', action='store_true', help='List generated pages')
    parser.add_argument('--export-m3u', nargs=2, metavar=('ITEMS_JSON', 'OUTPUT_FILE'), help='Export items to M3U file')
    parser.add_argument('--export-caspar', nargs=2, metavar=('SCHEDULE_JSON', 'OUTPUT_FILE'), help='Export schedule to CasparCG XML')
    
    args = parser.parse_args()
    matrix = M3UMatrixPro()
    
    if args.info:
        print(json.dumps(matrix.get_system_info(), indent=2))
    elif args.import_m3u:
        print(json.dumps(matrix.import_m3u(args.import_m3u), indent=2))
    elif args.list_playlists:
        print(json.dumps(matrix.get_playlists(), indent=2))
    elif args.list_schedules:
        print(json.dumps(matrix.get_schedules(), indent=2))
    elif args.list_pages:
        print(json.dumps(matrix.list_generated_pages(), indent=2))
    elif args.export_m3u:
        items = json.loads(args.export_m3u[0])
        print(json.dumps(matrix.export_m3u(items, args.export_m3u[1]), indent=2))
    elif args.export_caspar:
        schedule = json.loads(args.export_caspar[0])
        print(json.dumps(matrix.export_to_caspar(schedule, args.export_caspar[1]), indent=2))
    else:
        print("ScheduleFlow M3U Matrix Pro v2.0.0 - CLI Tool")
        print("Use --help for available commands")
        print("\nQuick start:")
        print("  python M3U_Matrix_Pro.py --info                    # Show system info")
        print("  python M3U_Matrix_Pro.py --list-pages              # List all generated pages")
        print("  python M3U_Matrix_Pro.py --list-playlists          # List imported playlists")
        print("  python M3U_Matrix_Pro.py --import-m3u FILE         # Import M3U playlist")
        print("  python M3U_Matrix_Pro.py --list-schedules          # List created schedules")
        print("\nNote: Web API available at http://localhost:5000/api/*")
