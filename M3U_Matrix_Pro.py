#!/usr/bin/env python3
"""
ScheduleFlow M3U Matrix Pro - Desktop Control Application
Manages M3U playlists, generates players, exports schedules
Production-ready with schema validation, timestamp parsing, duplicate/conflict detection
"""

import json
import os
import sys
import subprocess
import requests
import xml.etree.ElementTree as ET
import hashlib
import uuid
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple, Optional


class TimestampParser:
    """Parse and normalize timestamps to UTC"""
    
    @staticmethod
    def parse_iso8601(timestamp_str: str) -> Optional[datetime]:
        """Parse ISO 8601 timestamp and return as UTC datetime"""
        if not timestamp_str:
            return None
        
        try:
            # Try parsing with timezone
            # Handle formats: 2025-11-22T10:00:00Z, 2025-11-22T10:00:00-05:00, 2025-11-22T10:00:00+00:00
            if timestamp_str.endswith('Z'):
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(timestamp_str)
            
            # Ensure UTC
            if dt.tzinfo is None:
                # Naive datetime - assume UTC
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                # Convert to UTC
                dt = dt.astimezone(timezone.utc)
            
            return dt
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def to_utc_string(dt: datetime) -> str:
        """Convert datetime to ISO 8601 UTC string"""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


class ScheduleValidator:
    """Validate schedule data against expected schemas"""
    
    @staticmethod
    def validate_xml_schedule(root: ET.Element) -> Tuple[bool, List[str]]:
        """Validate XML schedule structure"""
        errors = []
        
        # Check root element
        if root.tag not in ['schedule', 'tvguide', 'playlist']:
            errors.append(f"Invalid root element: {root.tag}. Expected schedule, tvguide, or playlist")
            return False, errors
        
        # Check for event elements
        events = root.findall('.//event') or root.findall('.//item')
        if not events:
            errors.append("No event/item elements found in schedule")
            return False, errors
        
        # Validate each event
        for i, event in enumerate(events):
            event_errors = ScheduleValidator._validate_event(event, i)
            errors.extend(event_errors)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_event(event: ET.Element, index: int) -> List[str]:
        """Validate individual event structure"""
        errors = []
        
        # Check for required fields
        title = event.findtext('title') or event.findtext('name')
        if not title or not title.strip():
            errors.append(f"Event {index}: Missing or empty title/name")
        
        # Check for timestamps
        start = event.findtext('start') or event.findtext('start_time')
        end = event.findtext('end') or event.findtext('end_time')
        
        if not start:
            errors.append(f"Event {index}: Missing start timestamp")
        elif not TimestampParser.parse_iso8601(start):
            errors.append(f"Event {index}: Invalid start timestamp format: {start}")
        
        if not end:
            errors.append(f"Event {index}: Missing end timestamp")
        elif not TimestampParser.parse_iso8601(end):
            errors.append(f"Event {index}: Invalid end timestamp format: {end}")
        
        # Validate start < end
        if start and end:
            start_dt = TimestampParser.parse_iso8601(start)
            end_dt = TimestampParser.parse_iso8601(end)
            if start_dt and end_dt and start_dt >= end_dt:
                errors.append(f"Event {index}: Start time must be before end time")
        
        return errors
    
    @staticmethod
    def validate_json_schedule(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate JSON schedule structure"""
        errors = []
        
        # Check structure
        if not isinstance(data, dict):
            errors.append("JSON must be an object/dictionary")
            return False, errors
        
        # Find schedule items (could be under 'schedule', 'events', 'items', etc.)
        events = data.get('schedule') or data.get('events') or data.get('items') or []
        
        if not isinstance(events, list):
            errors.append("Schedule items must be a list")
            return False, errors
        
        if not events:
            errors.append("No events/items found in schedule")
            return False, errors
        
        # Validate each event
        for i, event in enumerate(events):
            if not isinstance(event, dict):
                errors.append(f"Event {i}: Must be an object")
                continue
            
            # Check required fields
            title = event.get('title') or event.get('name')
            if not title or not str(title).strip():
                errors.append(f"Event {i}: Missing or empty title/name")
            
            # Check timestamps
            start = event.get('start') or event.get('start_time')
            end = event.get('end') or event.get('end_time')
            
            if not start:
                errors.append(f"Event {i}: Missing start timestamp")
            elif not TimestampParser.parse_iso8601(str(start)):
                errors.append(f"Event {i}: Invalid start timestamp: {start}")
            
            if not end:
                errors.append(f"Event {i}: Missing end timestamp")
            elif not TimestampParser.parse_iso8601(str(end)):
                errors.append(f"Event {i}: Invalid end timestamp: {end}")
            
            # Validate start < end
            if start and end:
                start_dt = TimestampParser.parse_iso8601(str(start))
                end_dt = TimestampParser.parse_iso8601(str(end))
                if start_dt and end_dt and start_dt >= end_dt:
                    errors.append(f"Event {i}: Start time must be before end time")
        
        return len(errors) == 0, errors


class DuplicateDetector:
    """Detect duplicate events"""
    
    @staticmethod
    def get_event_hash(event: Dict[str, Any]) -> str:
        """Generate hash for event to detect duplicates"""
        # Use title + start time for duplicate detection
        title_val = event.get('title') or event.get('name') or ''
        title = str(title_val).lower().strip() if title_val else ''
        
        start_val = event.get('start') or event.get('start_time') or ''
        start = str(start_val) if start_val else ''
        
        hash_str = f"{title}:{start}"
        return hashlib.md5(hash_str.encode()).hexdigest()
    
    @staticmethod
    def detect_duplicates(events: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Detect duplicate events
        
        Returns:
            (unique_events, duplicate_events)
        """
        seen_hashes = set()
        unique = []
        duplicates = []
        
        for event in events:
            event_hash = DuplicateDetector.get_event_hash(event)
            if event_hash in seen_hashes:
                duplicates.append(event)
            else:
                seen_hashes.add(event_hash)
                unique.append(event)
        
        return unique, duplicates


class ConflictDetector:
    """Detect overlapping timeslots"""
    
    @staticmethod
    def detect_conflicts(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect overlapping events
        
        Returns:
            List of conflict pairs with details
        """
        conflicts = []
        
        for i, event1 in enumerate(events):
            start1 = TimestampParser.parse_iso8601(str(event1.get('start') or event1.get('start_time') or ''))
            end1 = TimestampParser.parse_iso8601(str(event1.get('end') or event1.get('end_time') or ''))
            
            if not start1 or not end1:
                continue
            
            for j, event2 in enumerate(events[i+1:], start=i+1):
                start2 = TimestampParser.parse_iso8601(str(event2.get('start') or event2.get('start_time') or ''))
                end2 = TimestampParser.parse_iso8601(str(event2.get('end') or event2.get('end_time') or ''))
                
                if not start2 or not end2:
                    continue
                
                # Check if ranges overlap
                if start1 < end2 and start2 < end1:
                    conflicts.append({
                        "type": "overlap",
                        "event1": {
                            "index": i,
                            "title": event1.get('title') or event1.get('name'),
                            "start": TimestampParser.to_utc_string(start1),
                            "end": TimestampParser.to_utc_string(end1)
                        },
                        "event2": {
                            "index": j,
                            "title": event2.get('title') or event2.get('name'),
                            "start": TimestampParser.to_utc_string(start2),
                            "end": TimestampParser.to_utc_string(end2)
                        }
                    })
        
        return conflicts


class ScheduleAlgorithm:
    """Auto-fill calendar with video playlists using Fisher-Yates shuffle and cooldown enforcement"""
    
    @staticmethod
    def fisher_yates_shuffle(items: List[str]) -> List[str]:
        """Fisher-Yates shuffle for unbiased randomization
        
        Returns shuffled copy of items list
        """
        import random
        result = items.copy()
        for i in range(len(result) - 1, 0, -1):
            j = random.randint(0, i)
            result[i], result[j] = result[j], result[i]
        return result
    
    @staticmethod
    def create_schedule_slots(start_time: datetime, duration_hours: int, slot_duration_minutes: int = 30) -> List[Dict[str, datetime]]:
        """Create calendar slots for scheduling
        
        Args:
            start_time: Start datetime for schedule
            duration_hours: Total duration to schedule (hours)
            slot_duration_minutes: Duration of each slot (minutes)
        
        Returns:
            List of slots with start/end times
        """
        slots = []
        current = start_time
        end_time = start_time + timedelta(hours=duration_hours)
        
        while current < end_time:
            slot_end = current + timedelta(minutes=slot_duration_minutes)
            if slot_end > end_time:
                slot_end = end_time
            
            slots.append({
                "start": current,
                "end": slot_end,
                "duration_minutes": slot_duration_minutes
            })
            current = slot_end
        
        return slots
    
    @staticmethod
    def auto_fill_schedule(playlist_links: List[str], 
                          slots: List[Dict[str, datetime]], 
                          cooldown_hours: int = 48,
                          shuffle: bool = True) -> Dict[str, Any]:
        """Auto-fill calendar with playlist links, enforcing cooldown
        
        Args:
            playlist_links: List of video URLs (1-10,000)
            slots: Calendar slots to fill
            cooldown_hours: Minimum hours between same video plays (default 48)
            shuffle: Whether to shuffle playlist order
        
        Returns:
            Scheduled calendar with logs
        """
        
        # Shuffle playlist if requested
        if shuffle:
            shuffled_links = ScheduleAlgorithm.fisher_yates_shuffle(playlist_links)
        else:
            shuffled_links = playlist_links.copy()
        
        # Track last played timestamp for cooldown enforcement
        last_played = {}  # video_url -> last_played_datetime
        scheduled_events = []
        scheduling_log = {
            "total_links": len(playlist_links),
            "total_slots": len(slots),
            "scheduled": 0,
            "skipped_cooldown": 0,
            "decisions": []
        }
        
        link_index = 0
        slot_index = 0
        
        while slot_index < len(slots):
            slot = slots[slot_index]
            
            # Find next available video respecting cooldown
            attempts = 0
            max_attempts = len(shuffled_links)  # Prevent infinite loops
            found_video = False
            
            while attempts < max_attempts:
                if link_index >= len(shuffled_links):
                    link_index = 0  # Wrap around playlist
                
                video_url = shuffled_links[link_index]
                
                # Check cooldown
                if video_url in last_played:
                    last_play = last_played[video_url]
                    cooldown_end = last_play + timedelta(hours=cooldown_hours)
                    
                    if slot['start'] < cooldown_end:
                        # Still in cooldown, skip this video
                        scheduling_log["decisions"].append({
                            "slot": slot_index,
                            "video": video_url,
                            "action": "skip_cooldown",
                            "slot_start": slot['start'].isoformat(),
                            "last_played": last_play.isoformat(),
                            "cooldown_end": cooldown_end.isoformat()
                        })
                        scheduling_log["skipped_cooldown"] += 1
                        link_index += 1
                        attempts += 1
                        continue
                
                # Video is available - schedule it
                event = {
                    "slot_index": slot_index,
                    "video_url": video_url,
                    "start": slot['start'].isoformat(),
                    "end": slot['end'].isoformat(),
                    "duration_minutes": slot['duration_minutes']
                }
                scheduled_events.append(event)
                last_played[video_url] = slot['start']
                
                scheduling_log["decisions"].append({
                    "slot": slot_index,
                    "video": video_url,
                    "action": "scheduled",
                    "slot_start": slot['start'].isoformat()
                })
                scheduling_log["scheduled"] += 1
                
                link_index += 1
                found_video = True
                break
            
            if not found_video:
                # Could not find any video (all in cooldown) - fill with first available
                video_url = shuffled_links[0]
                event = {
                    "slot_index": slot_index,
                    "video_url": video_url,
                    "start": slot['start'].isoformat(),
                    "end": slot['end'].isoformat(),
                    "duration_minutes": slot['duration_minutes'],
                    "warning": "all_videos_in_cooldown"
                }
                scheduled_events.append(event)
                scheduling_log["decisions"].append({
                    "slot": slot_index,
                    "video": video_url,
                    "action": "forced_schedule_cooldown_override",
                    "reason": "all_videos_in_cooldown"
                })
                scheduling_log["scheduled"] += 1
            
            slot_index += 1
        
        return {
            "status": "success",
            "scheduled_events": scheduled_events,
            "log": scheduling_log,
            "coverage": f"{(scheduling_log['scheduled'] / len(slots) * 100):.1f}%"
        }


class M3UMatrixPro:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.config_file = self.base_dir / "m3u_matrix_settings.json"
        self.generated_dir = self.base_dir / "generated_pages"
        self.schedules_dir = self.base_dir / "schedules"
        self.schedules_dir.mkdir(exist_ok=True)
        self.load_config()

    def load_config(self):
        """Load configuration from JSON"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                self.config = json.load(f)
        else:
            self.config = {"playlists": [], "schedules": [], "exports": []}
        
        # Ensure required keys exist (for backward compatibility)
        for key in ["playlists", "schedules", "exports"]:
            if key not in self.config:
                self.config[key] = []

    def save_config(self):
        """Save configuration to JSON"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def import_schedule_xml(self, filepath: str) -> Dict[str, Any]:
        """Import schedule from XML file with full validation"""
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            # Validate XML structure
            is_valid, errors = ScheduleValidator.validate_xml_schedule(root)
            if not is_valid:
                return {
                    "status": "error",
                    "type": "validation",
                    "message": "XML validation failed",
                    "errors": errors
                }
            
            # Extract events
            events = []
            for event_elem in (root.findall('.//event') or root.findall('.//item')):
                event = self._extract_xml_event(event_elem)
                if event:
                    events.append(event)
            
            # Detect duplicates
            unique_events, duplicates = DuplicateDetector.detect_duplicates(events)
            
            # Detect conflicts
            conflicts = ConflictDetector.detect_conflicts(unique_events)
            
            # Create schedule record
            schedule_id = str(uuid.uuid4())
            schedule = {
                "id": schedule_id,
                "name": Path(filepath).stem,
                "source": "xml",
                "filepath": str(filepath),
                "imported": datetime.now(timezone.utc).isoformat(),
                "events": unique_events,
                "metadata": {
                    "total_imported": len(events),
                    "duplicates_removed": len(duplicates),
                    "conflicts_detected": len(conflicts),
                    "unique_events": len(unique_events)
                },
                "warnings": {
                    "duplicates": duplicates if duplicates else [],
                    "conflicts": conflicts if conflicts else []
                }
            }
            
            self.config["schedules"].append(schedule)
            self.save_config()
            
            # Save schedule to separate file
            schedule_file = self.schedules_dir / f"{schedule_id}.json"
            with open(schedule_file, 'w') as f:
                json.dump(schedule, f, indent=2)
            
            return {
                "status": "success",
                "schedule_id": schedule_id,
                "events_imported": len(unique_events),
                "duplicates_removed": len(duplicates),
                "conflicts_detected": len(conflicts),
                "warnings": {
                    "duplicates": f"{len(duplicates)} duplicate events removed" if duplicates else None,
                    "conflicts": f"{len(conflicts)} overlapping timeslots detected" if conflicts else None
                }
            }
        except ET.ParseError as e:
            return {
                "status": "error",
                "type": "parse_error",
                "message": f"Failed to parse XML: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "type": "unexpected",
                "message": str(e)
            }

    def import_schedule_json(self, filepath: str) -> Dict[str, Any]:
        """Import schedule from JSON file with full validation"""
        try:
            with open(filepath) as f:
                data = json.load(f)
            
            # Validate JSON structure
            is_valid, errors = ScheduleValidator.validate_json_schedule(data)
            if not is_valid:
                return {
                    "status": "error",
                    "type": "validation",
                    "message": "JSON schema validation failed",
                    "errors": errors
                }
            
            # Extract events
            events = data.get('schedule') or data.get('events') or data.get('items') or []
            
            # Normalize timestamps to UTC
            for event in events:
                start_val = event.get('start') or event.get('start_time')
                if start_val:
                    dt = TimestampParser.parse_iso8601(str(start_val))
                    if dt:
                        event['start'] = TimestampParser.to_utc_string(dt)
                
                end_val = event.get('end') or event.get('end_time')
                if end_val:
                    dt = TimestampParser.parse_iso8601(str(end_val))
                    if dt:
                        event['end'] = TimestampParser.to_utc_string(dt)
            
            # Detect duplicates
            unique_events, duplicates = DuplicateDetector.detect_duplicates(events)
            
            # Detect conflicts
            conflicts = ConflictDetector.detect_conflicts(unique_events)
            
            # Create schedule record
            schedule_id = str(uuid.uuid4())
            schedule = {
                "id": schedule_id,
                "name": Path(filepath).stem,
                "source": "json",
                "filepath": str(filepath),
                "imported": datetime.now(timezone.utc).isoformat(),
                "events": unique_events,
                "metadata": {
                    "total_imported": len(events),
                    "duplicates_removed": len(duplicates),
                    "conflicts_detected": len(conflicts),
                    "unique_events": len(unique_events)
                },
                "warnings": {
                    "duplicates": duplicates if duplicates else [],
                    "conflicts": conflicts if conflicts else []
                }
            }
            
            self.config["schedules"].append(schedule)
            self.save_config()
            
            # Save schedule to separate file
            schedule_file = self.schedules_dir / f"{schedule_id}.json"
            with open(schedule_file, 'w') as f:
                json.dump(schedule, f, indent=2)
            
            return {
                "status": "success",
                "schedule_id": schedule_id,
                "events_imported": len(unique_events),
                "duplicates_removed": len(duplicates),
                "conflicts_detected": len(conflicts),
                "warnings": {
                    "duplicates": f"{len(duplicates)} duplicate events removed" if duplicates else None,
                    "conflicts": f"{len(conflicts)} overlapping timeslots detected" if conflicts else None
                }
            }
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "type": "parse_error",
                "message": f"Failed to parse JSON: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "type": "unexpected",
                "message": str(e)
            }

    def import_m3u(self, filepath: str) -> Dict[str, Any]:
        """Import M3U playlist"""
        try:
            with open(filepath) as f:
                lines = f.readlines()
            
            playlist = {
                "id": str(uuid.uuid4()),
                "name": Path(filepath).stem,
                "path": str(filepath),
                "items": [],
                "imported": datetime.now(timezone.utc).isoformat()
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
            return {"status": "success", "items": len(playlist["items"]), "playlist_id": playlist["id"]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _extract_xml_event(self, event_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract event from XML element"""
        try:
            title = event_elem.findtext('title') or event_elem.findtext('name')
            start = event_elem.findtext('start') or event_elem.findtext('start_time')
            end = event_elem.findtext('end') or event_elem.findtext('end_time')
            
            if not all([title, start, end]):
                return None
            
            # Parse and normalize timestamps
            start_dt = TimestampParser.parse_iso8601(str(start) if start else '')
            end_dt = TimestampParser.parse_iso8601(str(end) if end else '')
            
            if not (start_dt and end_dt):
                return None
            
            title_str = title.strip() if isinstance(title, str) else str(title)
            return {
                "title": title_str,
                "start": TimestampParser.to_utc_string(start_dt),
                "end": TimestampParser.to_utc_string(end_dt),
                "description": event_elem.findtext('description') or "",
                "category": event_elem.findtext('category') or "",
                "id": event_elem.get('id') or str(uuid.uuid4())
            }
        except Exception:
            return None

    def export_m3u(self, items: List[Dict[str, Any]], output_path: str) -> Dict[str, Any]:
        """Export items as M3U playlist"""
        try:
            m3u_content = "#EXTM3U\n"
            for item in items:
                label = item.get("label", "Item")
                url = item.get("url", "")
                m3u_content += f"#EXTINF:-1,{label}\n{url}\n"
            
            with open(output_path, 'w') as f:
                f.write(m3u_content)
            
            return {"status": "success", "path": str(output_path), "items": len(items)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def export_to_caspar(self, schedule: List[Dict[str, Any]], output_path: str) -> Dict[str, Any]:
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
            
            return {"status": "success", "path": str(output_path), "events": len(schedule)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def export_schedule_xml(self, schedule_id: str, output_path: str) -> Dict[str, Any]:
        """Export schedule to TVGuide XML format (human-readable, schema-compatible)"""
        try:
            # Find schedule
            schedule = None
            for sched in self.config.get("schedules", []):
                if sched.get("id") == schedule_id:
                    schedule = sched
                    break
            
            if not schedule:
                return {"status": "error", "message": f"Schedule {schedule_id} not found"}
            
            # Build XML with proper structure
            xml_parts = [
                '<?xml version="1.0" encoding="utf-8"?>',
                '<tvguide generated="' + datetime.now(timezone.utc).isoformat() + '">',
                f'  <metadata>',
                f'    <name>{self._escape_xml(schedule.get("name", ""))}</name>',
                f'    <source>{self._escape_xml(schedule.get("source", "unknown"))}</source>',
                f'    <imported>{schedule.get("imported", "")}</imported>',
                f'    <event_count>{len(schedule.get("events", []))}</event_count>',
                f'  </metadata>',
                f'  <schedule>'
            ]
            
            # Add events
            for event in schedule.get("events", []):
                xml_parts.append(f'    <event id="{self._escape_xml(event.get("id", ""))}">') 
                xml_parts.append(f'      <title>{self._escape_xml(event.get("title", ""))}</title>')
                xml_parts.append(f'      <start>{event.get("start", "")}</start>')
                xml_parts.append(f'      <end>{event.get("end", "")}</end>')
                if event.get("description"):
                    xml_parts.append(f'      <description>{self._escape_xml(event.get("description", ""))}</description>')
                if event.get("category"):
                    xml_parts.append(f'      <category>{self._escape_xml(event.get("category", ""))}</category>')
                xml_parts.append(f'    </event>')
            
            xml_parts.append(f'  </schedule>')
            xml_parts.append(f'</tvguide>')
            
            xml_content = '\n'.join(xml_parts)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            # Validate exported XML can be parsed
            try:
                ET.fromstring(xml_content)
                is_valid = True
            except ET.ParseError:
                is_valid = False
            
            return {
                "status": "success",
                "path": str(output_path),
                "events": len(schedule.get("events", [])),
                "schema": "tvguide",
                "valid": is_valid,
                "format": "xml",
                "human_readable": True
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def export_schedule_json(self, schedule_id: str, output_path: str) -> Dict[str, Any]:
        """Export schedule to JSON format (human-readable, pretty-printed)"""
        try:
            # Find schedule
            schedule = None
            for sched in self.config.get("schedules", []):
                if sched.get("id") == schedule_id:
                    schedule = sched
                    break
            
            if not schedule:
                return {"status": "error", "message": f"Schedule {schedule_id} not found"}
            
            # Build JSON structure
            export_data = {
                "schedule": {
                    "metadata": {
                        "name": schedule.get("name"),
                        "source": schedule.get("source"),
                        "imported": schedule.get("imported"),
                        "generated": datetime.now(timezone.utc).isoformat(),
                        "event_count": len(schedule.get("events", []))
                    },
                    "events": schedule.get("events", [])
                }
            }
            
            # Write to file with pretty formatting
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            # Validate JSON by re-parsing
            try:
                with open(output_path) as f:
                    json.load(f)
                is_valid = True
            except json.JSONDecodeError:
                is_valid = False
            
            return {
                "status": "success",
                "path": str(output_path),
                "events": len(schedule.get("events", [])),
                "schema": "schedule",
                "valid": is_valid,
                "format": "json",
                "human_readable": True
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def export_all_schedules_xml(self, output_path: str) -> Dict[str, Any]:
        """Export all schedules to single TVGuide XML file"""
        try:
            xml_parts = [
                '<?xml version="1.0" encoding="utf-8"?>',
                '<tvguide generated="' + datetime.now(timezone.utc).isoformat() + '">',
                f'  <metadata>',
                f'    <schedule_count>{len(self.config.get("schedules", []))}</schedule_count>',
                f'    <total_events>{sum(len(s.get("events", [])) for s in self.config.get("schedules", []))}</total_events>',
                f'  </metadata>',
            ]
            
            # Add all schedules
            for schedule in self.config.get("schedules", []):
                xml_parts.append(f'  <schedule id="{self._escape_xml(schedule.get("id", ""))}">') 
                xml_parts.append(f'    <name>{self._escape_xml(schedule.get("name", ""))}</name>')
                
                for event in schedule.get("events", []):
                    xml_parts.append(f'    <event id="{self._escape_xml(event.get("id", ""))}">') 
                    xml_parts.append(f'      <title>{self._escape_xml(event.get("title", ""))}</title>')
                    xml_parts.append(f'      <start>{event.get("start", "")}</start>')
                    xml_parts.append(f'      <end>{event.get("end", "")}</end>')
                    if event.get("description"):
                        xml_parts.append(f'      <description>{self._escape_xml(event.get("description", ""))}</description>')
                    if event.get("category"):
                        xml_parts.append(f'      <category>{self._escape_xml(event.get("category", ""))}</category>')
                    xml_parts.append(f'    </event>')
                
                xml_parts.append(f'  </schedule>')
            
            xml_parts.append(f'</tvguide>')
            xml_content = '\n'.join(xml_parts)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            total_events = sum(len(s.get("events", [])) for s in self.config.get("schedules", []))
            return {
                "status": "success",
                "path": str(output_path),
                "schedules": len(self.config.get("schedules", [])),
                "events": total_events,
                "human_readable": True
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def _escape_xml(text: str) -> str:
        """Escape XML special characters"""
        if not isinstance(text, str):
            text = str(text)
        return (text.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace('"', "&quot;")
                    .replace("'", "&apos;"))

    def create_schedule(self, name: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a schedule from items with validation"""
        try:
            # Validate items
            for i, item in enumerate(items):
                if not item.get('start'):
                    return {"status": "error", "message": f"Item {i}: Missing start timestamp"}
                if not item.get('end'):
                    return {"status": "error", "message": f"Item {i}: Missing end timestamp"}
            
            # Detect duplicates
            unique_items, duplicates = DuplicateDetector.detect_duplicates(items)
            
            # Detect conflicts
            conflicts = ConflictDetector.detect_conflicts(unique_items)
            
            # Calculate duration
            duration_seconds = 0
            for item in unique_items:
                start_dt = TimestampParser.parse_iso8601(str(item.get('start', '')))
                end_dt = TimestampParser.parse_iso8601(str(item.get('end', '')))
                if start_dt and end_dt:
                    duration_seconds += int((end_dt - start_dt).total_seconds())
            
            schedule = {
                "id": str(uuid.uuid4()),
                "name": name,
                "items": unique_items,
                "created": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": duration_seconds,
                "metadata": {
                    "total_items": len(items),
                    "duplicates_removed": len(duplicates),
                    "conflicts": len(conflicts)
                }
            }
            self.config["schedules"].append(schedule)
            self.save_config()
            return {
                "status": "success",
                "schedule": schedule,
                "duplicates_removed": len(duplicates),
                "conflicts": len(conflicts)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_playlists(self) -> Dict[str, Any]:
        """Get all loaded playlists"""
        return {
            "status": "success",
            "playlists": self.config.get("playlists", []),
            "count": len(self.config.get("playlists", []))
        }

    def get_schedules(self) -> Dict[str, Any]:
        """Get all schedules"""
        return {
            "status": "success",
            "schedules": self.config.get("schedules", []),
            "count": len(self.config.get("schedules", []))
        }

    def list_generated_pages(self) -> Dict[str, Any]:
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

    def schedule_playlist(self, playlist_links: List[str], start_time: datetime, 
                         duration_hours: int, slot_minutes: int = 30,
                         cooldown_hours: int = 48, shuffle: bool = True) -> Dict[str, Any]:
        """Auto-fill calendar with playlist links using Fisher-Yates shuffle and cooldown enforcement"""
        try:
            # Create calendar slots
            slots = ScheduleAlgorithm.create_schedule_slots(start_time, duration_hours, slot_minutes)
            
            # Run auto-fill algorithm
            result = ScheduleAlgorithm.auto_fill_schedule(
                playlist_links, 
                slots, 
                cooldown_hours=cooldown_hours, 
                shuffle=shuffle
            )
            
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        playlists = len(self.config.get("playlists", []))
        schedules = len(self.config.get("schedules", []))
        
        if self.generated_dir.exists():
            pages = len(list(self.generated_dir.glob("*.html")))
        else:
            pages = 0
        
        return {
            "status": "success",
            "version": "2.1.0",
            "playlists_loaded": playlists,
            "schedules_created": schedules,
            "pages_generated": pages,
            "config_path": str(self.config_file),
            "generated_dir": str(self.generated_dir)
        }

    def clear_config(self) -> Dict[str, Any]:
        """Clear all configurations"""
        self.config = {"playlists": [], "schedules": [], "exports": []}
        self.save_config()
        return {"status": "success", "message": "All configurations cleared"}


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ScheduleFlow M3U Matrix Pro - CLI Control Tool")
    parser.add_argument('--info', action='store_true', help='Show system info')
    parser.add_argument('--import-m3u', metavar='FILE', help='Import M3U playlist')
    parser.add_argument('--import-schedule-xml', metavar='FILE', help='Import schedule from XML')
    parser.add_argument('--import-schedule-json', metavar='FILE', help='Import schedule from JSON')
    parser.add_argument('--list-playlists', action='store_true', help='List all playlists')
    parser.add_argument('--list-schedules', action='store_true', help='List all schedules')
    parser.add_argument('--list-pages', action='store_true', help='List generated pages')
    parser.add_argument('--export-m3u', nargs=2, metavar=('ITEMS_JSON', 'OUTPUT_FILE'), help='Export items to M3U file')
    parser.add_argument('--export-caspar', nargs=2, metavar=('SCHEDULE_JSON', 'OUTPUT_FILE'), help='Export schedule to CasparCG XML')
    parser.add_argument('--export-schedule-xml', nargs=2, metavar=('SCHEDULE_ID', 'OUTPUT_FILE'), help='Export schedule to TVGuide XML')
    parser.add_argument('--export-schedule-json', nargs=2, metavar=('SCHEDULE_ID', 'OUTPUT_FILE'), help='Export schedule to JSON')
    parser.add_argument('--export-all-xml', metavar='OUTPUT_FILE', help='Export all schedules to TVGuide XML')
    parser.add_argument('--schedule-playlist', nargs=4, metavar=('PLAYLIST_JSON', 'START_TIME', 'HOURS', 'OUTPUT_FILE'), help='Auto-fill schedule with playlist links')
    
    args = parser.parse_args()
    matrix = M3UMatrixPro()
    
    if args.info:
        print(json.dumps(matrix.get_system_info(), indent=2))
    elif args.import_m3u:
        print(json.dumps(matrix.import_m3u(args.import_m3u), indent=2))
    elif args.import_schedule_xml:
        print(json.dumps(matrix.import_schedule_xml(args.import_schedule_xml), indent=2))
    elif args.import_schedule_json:
        print(json.dumps(matrix.import_schedule_json(args.import_schedule_json), indent=2))
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
    elif args.export_schedule_xml:
        print(json.dumps(matrix.export_schedule_xml(args.export_schedule_xml[0], args.export_schedule_xml[1]), indent=2))
    elif args.export_schedule_json:
        print(json.dumps(matrix.export_schedule_json(args.export_schedule_json[0], args.export_schedule_json[1]), indent=2))
    elif args.export_all_xml:
        print(json.dumps(matrix.export_all_schedules_xml(args.export_all_xml), indent=2))
    elif args.schedule_playlist:
        playlist = json.loads(args.schedule_playlist[0])
        start_dt = TimestampParser.parse_iso8601(args.schedule_playlist[1])
        if start_dt:
            hours = int(args.schedule_playlist[2])
            output = args.schedule_playlist[3]
            result = matrix.schedule_playlist(playlist, start_dt, hours)
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
            print(json.dumps({"status": "success", "output": output, "scheduled": result.get("log", {}).get("scheduled")}, indent=2))
        else:
            print(json.dumps({"status": "error", "message": "Invalid start time"}, indent=2))
    else:
        print("ScheduleFlow M3U Matrix Pro v2.1.0 - CLI Tool")
        print("Use --help for available commands")
        print("\nQuick start:")
        print("  python M3U_Matrix_Pro.py --info                      # Show system info")
        print("  python M3U_Matrix_Pro.py --list-pages                # List all generated pages")
        print("  python M3U_Matrix_Pro.py --list-playlists            # List imported playlists")
        print("  python M3U_Matrix_Pro.py --import-m3u FILE           # Import M3U playlist")
        print("  python M3U_Matrix_Pro.py --import-schedule-xml FILE  # Import XML schedule")
        print("  python M3U_Matrix_Pro.py --import-schedule-json FILE # Import JSON schedule")
        print("  python M3U_Matrix_Pro.py --list-schedules            # List created schedules")
        print("\nNote: Web API available at http://localhost:5000/api/*")
