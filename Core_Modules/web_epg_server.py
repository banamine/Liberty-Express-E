"""
Web EPG Server
Provides /now.json API endpoint for current and next shows
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from Core_Modules.tv_schedule_db import TVScheduleDB


class EPGHandler(BaseHTTPRequestHandler):
    """HTTP handler for EPG requests"""
    
    db = None  # Will be set by server
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        if path == "/now.json":
            self.handle_now_json(query_params)
        elif path == "/schedules.json":
            self.handle_schedules(query_params)
        elif path == "/epg.json":
            self.handle_epg(query_params)
        else:
            self.send_error(404, "Not Found")
    
    def handle_now_json(self, params):
        """
        Get current and next 5 shows for a channel
        Query params: channel=<channel_id>, schedule=<schedule_id>
        """
        channel_id = params.get('channel', [None])[0]
        schedule_id = params.get('schedule', [None])[0]
        
        if not channel_id or not schedule_id:
            self.send_json_response(
                {"error": "Missing channel or schedule parameter"},
                400
            )
            return
        
        try:
            channel_id = int(channel_id)
            schedule_id = int(schedule_id)
        except ValueError:
            self.send_json_response({"error": "Invalid channel or schedule ID"}, 400)
            return
        
        # Get current time
        now = datetime.now()
        
        # Get all time slots for this channel
        slots = self.db.get_time_slots(schedule_id)
        
        # Filter by channel and find current/upcoming
        relevant_slots = [
            s for s in slots 
            if s['channel_id'] == channel_id
        ]
        
        # Parse times and find current + next 5
        programs = []
        for slot in relevant_slots:
            try:
                start = datetime.strptime(slot['start_time'], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(slot['end_time'], "%Y-%m-%d %H:%M:%S")
                
                # Check if this slot is current or upcoming
                if start <= now <= end or start > now:
                    programs.append({
                        "id": slot['slot_id'],
                        "show_id": slot.get('show_id'),
                        "show_name": self._get_show_name(slot.get('show_id')),
                        "start": start.isoformat(),
                        "end": end.isoformat(),
                        "duration_minutes": int((end - start).total_seconds() / 60),
                        "is_current": start <= now <= end,
                        "is_next": start > now
                    })
            except:
                continue
        
        # Sort by start time and take current + next 5
        programs.sort(key=lambda x: x['start'])
        current = next((p for p in programs if p['is_current']), None)
        
        if current:
            # Include current + next 5
            upcoming_idx = programs.index(current)
            programs = [programs[upcoming_idx]] + programs[upcoming_idx+1:upstream_idx+6]
        else:
            # Just take next 6
            programs = programs[:6]
        
        response = {
            "schedule_id": schedule_id,
            "channel_id": channel_id,
            "current_time": now.isoformat(),
            "current_program": current,
            "next_programs": programs[1:] if current else programs,
            "program_count": len(programs)
        }
        
        self.send_json_response(response)
    
    def handle_schedules(self, params):
        """Get all available schedules"""
        schedules = self.db.get_schedules()
        
        response = {
            "schedules": [
                {
                    "id": s['schedule_id'],
                    "name": s.get('name'),
                    "start_date": s.get('start_date'),
                    "end_date": s.get('end_date'),
                    "enable_looping": s.get('enable_looping', 0)
                }
                for s in schedules
            ],
            "schedule_count": len(schedules)
        }
        
        self.send_json_response(response)
    
    def handle_epg(self, params):
        """Get full EPG for a schedule"""
        schedule_id = params.get('schedule', [None])[0]
        
        if not schedule_id:
            self.send_json_response(
                {"error": "Missing schedule parameter"},
                400
            )
            return
        
        try:
            schedule_id = int(schedule_id)
        except ValueError:
            self.send_json_response({"error": "Invalid schedule ID"}, 400)
            return
        
        # Get schedule details
        schedules = self.db.get_schedules()
        schedule = next((s for s in schedules if s['schedule_id'] == schedule_id), None)
        
        if not schedule:
            self.send_json_response({"error": "Schedule not found"}, 404)
            return
        
        # Get time slots
        slots = self.db.get_time_slots(schedule_id)
        
        # Build EPG by channel
        epg_by_channel = {}
        for slot in slots:
            channel_id = slot['channel_id']
            if channel_id not in epg_by_channel:
                channel = self._get_channel(channel_id)
                epg_by_channel[channel_id] = {
                    "channel": channel,
                    "programs": []
                }
            
            try:
                start = datetime.strptime(slot['start_time'], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(slot['end_time'], "%Y-%m-%d %H:%M:%S")
                
                epg_by_channel[channel_id]["programs"].append({
                    "id": slot['slot_id'],
                    "show_id": slot.get('show_id'),
                    "show_name": self._get_show_name(slot.get('show_id')),
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "duration_minutes": int((end - start).total_seconds() / 60)
                })
            except:
                continue
        
        response = {
            "schedule": {
                "id": schedule_id,
                "name": schedule.get('name'),
                "start_date": schedule.get('start_date'),
                "end_date": schedule.get('end_date'),
                "enable_looping": schedule.get('enable_looping', 0)
            },
            "channels": epg_by_channel,
            "generated_at": datetime.now().isoformat()
        }
        
        self.send_json_response(response)
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass
    
    def _get_show_name(self, show_id):
        """Get show name from ID"""
        if not show_id:
            return "Unknown"
        try:
            shows = self.db.get_shows()
            show = next((s for s in shows if s['show_id'] == show_id), None)
            return show.get('name') if show else "Unknown"
        except:
            return "Unknown"
    
    def _get_channel(self, channel_id):
        """Get channel details"""
        try:
            channels = self.db.get_channels()
            channel = next((c for c in channels if c['channel_id'] == channel_id), None)
            return {
                "id": channel_id,
                "name": channel.get('name') if channel else f"Channel {channel_id}",
                "description": channel.get('description') if channel else ""
            }
        except:
            return {
                "id": channel_id,
                "name": f"Channel {channel_id}",
                "description": ""
            }


class WebEPGServer:
    """Web EPG Server wrapper"""
    
    def __init__(self, db_path: str = "tv_schedules.db", host: str = "0.0.0.0", port: int = 8000):
        """Initialize EPG server"""
        self.db_path = db_path
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        
        # Set database for handler
        EPGHandler.db = TVScheduleDB(db_path)
    
    def start(self):
        """Start the server in a background thread"""
        self.server = HTTPServer((self.host, self.port), EPGHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"EPG Server started at http://{self.host}:{self.port}")
    
    def stop(self):
        """Stop the server"""
        if self.server:
            self.server.shutdown()
            print("EPG Server stopped")
    
    def get_now_json(self, channel_id: int, schedule_id: int) -> dict:
        """Get current/next programs (local method)"""
        handler = EPGHandler
        # Manually call handler method
        params = {'channel': [str(channel_id)], 'schedule': [str(schedule_id)]}
        
        now = datetime.now()
        slots = handler.db.get_time_slots(schedule_id)
        
        relevant_slots = [s for s in slots if s['channel_id'] == channel_id]
        programs = []
        
        for slot in relevant_slots:
            try:
                start = datetime.strptime(slot['start_time'], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(slot['end_time'], "%Y-%m-%d %H:%M:%S")
                
                if start <= now <= end or start > now:
                    programs.append({
                        "id": slot['slot_id'],
                        "show_id": slot.get('show_id'),
                        "show_name": self._get_show_name(slot.get('show_id')),
                        "start": start.isoformat(),
                        "end": end.isoformat(),
                        "duration_minutes": int((end - start).total_seconds() / 60),
                        "is_current": start <= now <= end,
                        "is_next": start > now
                    })
            except:
                continue
        
        programs.sort(key=lambda x: x['start'])
        current = next((p for p in programs if p['is_current']), None)
        
        if current:
            upcoming_idx = programs.index(current)
            programs = [programs[upcoming_idx]] + programs[upcoming_idx+1:upstream_idx+6]
        else:
            programs = programs[:6]
        
        return {
            "schedule_id": schedule_id,
            "channel_id": channel_id,
            "current_time": now.isoformat(),
            "current_program": current,
            "next_programs": programs[1:] if current else programs
        }
    
    def _get_show_name(self, show_id):
        """Get show name"""
        if not show_id:
            return "Unknown"
        try:
            shows = EPGHandler.db.get_shows()
            show = next((s for s in shows if s['show_id'] == show_id), None)
            return show.get('name') if show else "Unknown"
        except:
            return "Unknown"
