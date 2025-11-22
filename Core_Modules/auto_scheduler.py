"""
Auto-Scheduler Module
Handles auto-building schedules from folders/M3U files with flexible time slots
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from Core_Modules.tv_schedule_db import TVScheduleDB
import re


class AutoScheduler:
    """Automatically builds schedules from media files and M3U playlists"""
    
    VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.m3u8', '.m3u'}
    
    def __init__(self, db_path: str = "tv_schedules.db"):
        """Initialize auto-scheduler"""
        self.db = TVScheduleDB(db_path)
    
    def import_folder(self, folder_path: str, channel_name: str, 
                     channel_group: str = "Auto Imported") -> Dict:
        """
        Import all media files from a folder as shows
        
        Args:
            folder_path: Path to folder containing media files
            channel_name: Name for the channel
            channel_group: Group for the channel
        
        Returns:
            Dict with import results
        """
        folder = Path(folder_path)
        if not folder.exists():
            return {'success': False, 'message': 'Folder not found', 'shows_imported': 0}
        
        # Create channel
        channel_id = self.db.add_channel(channel_name or "Unknown Channel", 
                                         description=f"Auto-imported from {folder_path}",
                                         group=channel_group)
        
        if not channel_id:
            return {'success': False, 'message': 'Failed to create channel', 'shows_imported': 0}
        
        shows_imported = 0
        files = []
        
        # Get all media files
        for ext in self.VIDEO_EXTENSIONS:
            files.extend(folder.glob(f"*{ext}"))
            files.extend(folder.glob(f"**/*{ext}"))  # Recursive
        
        # Remove duplicates and sort
        files = sorted(set(files))
        
        for file_path in files:
            try:
                duration = self._get_file_duration(file_path)
                if duration <= 0:
                    duration = 45  # Default to 45 minutes
                
                show_id = self.db.add_show(
                    channel_id=channel_id,
                    name=file_path.stem,
                    duration_minutes=duration,
                    description=f"From {file_path.parent.name}",
                    metadata={"file_path": str(file_path)}
                )
                shows_imported += 1
            except Exception as e:
                print(f"Error importing {file_path}: {e}")
        
        return {
            'success': True,
            'message': f'Imported {shows_imported} shows',
            'channel_id': channel_id,
            'shows_imported': shows_imported,
            'channel_name': channel_name
        }
    
    def import_m3u(self, m3u_path: str, channel_name: str = None) -> Dict:
        """
        Import M3U playlist
        
        Args:
            m3u_path: Path to M3U file
            channel_name: Optional channel name (uses filename if not provided)
        
        Returns:
            Dict with import results
        """
        m3u_file = Path(m3u_path)
        if not m3u_file.exists():
            return {'success': False, 'message': 'M3U file not found', 'shows_imported': 0}
        
        if not channel_name:
            channel_name = m3u_file.stem or "M3U Channel"
        
        # Create channel
        channel_id = self.db.add_channel(channel_name,
                                        description=f"Imported from {m3u_file.name}",
                                        group="M3U Imports")
        
        if not channel_id:
            return {'success': False, 'message': 'Failed to create channel', 'shows_imported': 0}
        
        shows_imported = 0
        
        try:
            with open(m3u_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#EXTINF'):
                        # Parse EXTINF line
                        duration = self._parse_extinf(line)
                        if duration <= 0:
                            duration = 45
                        
                        # Next line is the URL or name
                        try:
                            next_line = next(f).strip()
                            show_name = Path(next_line).stem or next_line
                            
                            show_id = self.db.add_show(
                                channel_id=channel_id,
                                name=show_name,
                                duration_minutes=duration,
                                metadata={"url": next_line, "from_m3u": m3u_file.name}
                            )
                            shows_imported += 1
                        except StopIteration:
                            break
        except Exception as e:
            return {
                'success': False,
                'message': f'Error reading M3U: {e}',
                'shows_imported': shows_imported
            }
        
        return {
            'success': True,
            'message': f'Imported {shows_imported} shows from M3U',
            'channel_id': channel_id,
            'shows_imported': shows_imported,
            'channel_name': channel_name
        }
    
    def auto_build_schedule(self, channel_id: int, schedule_name: str,
                           start_datetime: str, num_days: int = 7,
                           shuffle: bool = True, enable_looping: bool = True,
                           slot_mode: str = "exact_duration") -> Dict:
        """
        Auto-build schedule from channel's shows
        
        Args:
            channel_id: Channel to schedule
            schedule_name: Name for the schedule
            start_datetime: Start datetime (YYYY-MM-DD HH:MM:SS) or "now"
            num_days: Number of days to schedule (infinite if looping + no end)
            shuffle: Whether to shuffle shows
            enable_looping: Enable infinite looping
            slot_mode: "exact_duration" = respect show duration, "grid_30min" = 30min slots
        
        Returns:
            Dict with schedule details
        """
        # Parse start time
        if start_datetime.lower() == "now":
            start_dt = datetime.now().replace(minute=0, second=0, microsecond=0)
        else:
            start_dt = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")
        
        end_dt = start_dt + timedelta(days=num_days)
        
        # Create schedule
        schedule_id = self.db.create_schedule(
            name=schedule_name,
            start_date=start_dt.strftime("%Y-%m-%d"),
            end_date=end_dt.strftime("%Y-%m-%d"),
            enable_looping=enable_looping,
            loop_end_date="" if enable_looping else end_dt.strftime("%Y-%m-%d")
        )
        
        # Get shows for channel
        shows = self.db.get_shows(channel_id)
        if not shows:
            return {'success': False, 'message': 'No shows in channel', 'schedule_id': schedule_id}
        
        # Shuffle if requested
        if shuffle:
            import random
            shows = shows.copy()
            random.shuffle(shows)
        
        # Build schedule
        current_time = start_dt
        shows_scheduled = 0
        
        # Create infinite show list by repeating
        show_cycle = shows * (num_days + 1)  # Ensure enough shows
        show_idx = 0
        
        while current_time < end_dt:
            if show_idx >= len(show_cycle):
                break
            
            show = show_cycle[show_idx]
            show_duration = show.get('duration_minutes', 45)
            
            # Calculate end time
            slot_end = current_time + timedelta(minutes=show_duration)
            
            # Ensure it doesn't go past end date
            if slot_end > end_dt:
                break
            
            # Add to schedule
            self.db.add_time_slot(
                schedule_id=schedule_id,
                channel_id=channel_id,
                show_id=show['show_id'],
                start_time=current_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time=slot_end.strftime("%Y-%m-%d %H:%M:%S"),
                is_repeat=True
            )
            
            shows_scheduled += 1
            current_time = slot_end
            show_idx += 1
        
        return {
            'success': True,
            'message': f'Created schedule with {shows_scheduled} slots',
            'schedule_id': schedule_id,
            'schedule_name': schedule_name,
            'shows_scheduled': shows_scheduled,
            'start_time': start_dt.isoformat(),
            'end_time': end_dt.isoformat(),
            'enable_looping': enable_looping
        }
    
    def rebuild_schedule(self, schedule_id: int) -> Dict:
        """
        Rebuild schedule by refreshing show durations
        
        Args:
            schedule_id: Schedule to rebuild
        
        Returns:
            Dict with rebuild results
        """
        # Get all time slots
        slots = self.db.get_time_slots(schedule_id)
        
        updated = 0
        for slot in slots:
            show_id = slot.get('show_id')
            if not show_id:
                continue
            
            # Get current show duration
            shows = self.db.get_shows()  # Get all
            show = next((s for s in shows if s['show_id'] == show_id), None)
            
            if show and show.get('duration_minutes'):
                # Update slot end time based on new duration
                old_end = datetime.strptime(slot['end_time'], "%Y-%m-%d %H:%M:%S")
                new_end = datetime.strptime(slot['start_time'], "%Y-%m-%d %H:%M:%S") + \
                         timedelta(minutes=show['duration_minutes'])
                
                self.db.update_time_slot(
                    slot_id=slot['slot_id'],
                    end_time=new_end.strftime("%Y-%m-%d %H:%M:%S")
                )
                updated += 1
        
        return {
            'success': True,
            'message': f'Rebuilt schedule with {updated} updated slots',
            'schedule_id': schedule_id,
            'slots_updated': updated
        }
    
    def export_web_epg_json(self, schedule_id: int, output_path: str = None) -> Dict:
        """
        Export schedule as Web EPG JSON with ISO timestamps
        
        Args:
            schedule_id: Schedule to export
            output_path: Optional output file path
        
        Returns:
            Dict with EPG data or file path
        """
        # Get schedule details
        schedules = self.db.get_schedules()
        schedule = next((s for s in schedules if s['schedule_id'] == schedule_id), None)
        
        if not schedule:
            return {'success': False, 'message': 'Schedule not found'}
        
        # Get all time slots
        slots = self.db.get_time_slots(schedule_id)
        
        # Build EPG JSON structure
        epg_data = {
            "schedule": {
                "id": schedule_id,
                "name": schedule.get('name', 'Untitled'),
                "start_date": schedule.get('start_date'),
                "end_date": schedule.get('end_date'),
                "enable_looping": schedule.get('enable_looping', False),
                "generated_at": datetime.now().isoformat()
            },
            "channels": {},
            "programs": []
        }
        
        # Group slots by channel
        for slot in slots:
            channel_id = slot['channel_id']
            
            # Get channel info
            if channel_id not in epg_data['channels']:
                channels = self.db.get_channels()
                channel = next((c for c in channels if c['channel_id'] == channel_id), None)
                if channel:
                    epg_data['channels'][str(channel_id)] = {
                        "id": channel_id,
                        "name": channel.get('name'),
                        "description": channel.get('description'),
                        "group": channel.get('channel_group')
                    }
            
            # Get show info
            show_id = slot.get('show_id')
            show_name = "Unknown"
            if show_id:
                all_shows = self.db.get_shows()
                show = next((s for s in all_shows if s['show_id'] == show_id), None)
                if show:
                    show_name = show.get('name')
            
            # Add program
            epg_data['programs'].append({
                "id": slot['slot_id'],
                "channel_id": channel_id,
                "show_id": show_id,
                "show_name": show_name,
                "start": datetime.strptime(slot['start_time'], "%Y-%m-%d %H:%M:%S").isoformat(),
                "end": datetime.strptime(slot['end_time'], "%Y-%m-%d %H:%M:%S").isoformat(),
                "duration_minutes": self._calculate_duration(slot['start_time'], slot['end_time']),
                "is_repeat": slot.get('is_repeat', 0)
            })
        
        epg_json = {
            'success': True,
            'message': f'Exported {len(epg_data["programs"])} programs',
            'schedule_id': schedule_id,
            'epg_data': epg_data,
            'program_count': len(epg_data['programs'])
        }
        
        # Save to file if path provided
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(epg_data, f, indent=2)
                epg_json['file_path'] = output_path
            except Exception as e:
                epg_json['error'] = str(e)
        else:
            epg_json['file_path'] = ""
        
        return epg_json
    
    @staticmethod
    def _get_file_duration(file_path: Path) -> int:
        """Get media file duration in minutes (stub - would use FFprobe)"""
        # For now, return default duration
        # In production, use FFprobe to extract real duration
        return 45
    
    @staticmethod
    def _parse_extinf(extinf_line: str) -> int:
        """Parse EXTINF line to extract duration"""
        try:
            # Format: #EXTINF:duration,name
            parts = extinf_line.split(':')
            if len(parts) >= 2:
                duration_str = parts[1].split(',')[0].strip()
                duration = int(float(duration_str))
                return max(duration // 60, 1)  # Convert to minutes, min 1
        except:
            pass
        return 45  # Default
    
    @staticmethod
    def _calculate_duration(start_str: str, end_str: str) -> int:
        """Calculate duration between two datetime strings in minutes"""
        start = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
        return int((end - start).total_seconds() / 60)
