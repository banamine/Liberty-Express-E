"""
EPG Parser - Handles parsing of Electronic Program Guide (EPG) XML files
"""

import re
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests


class EPGParser:
    """
    Parser for EPG (Electronic Program Guide) data in XMLTV format.
    Handles parsing of programme schedules and channel mappings.
    """
    
    def __init__(self):
        """Initialize the EPG parser"""
        self.logger = logging.getLogger(__name__)
        self.channel_mapping = {}
        self.programmes = []
    
    def parse_epg_xml(self, xml_content: str) -> Dict[str, Any]:
        """
        Parse EPG XML content and extract programme information.
        
        Args:
            xml_content: XML content as string
            
        Returns:
            Dictionary containing parsed EPG data
        """
        try:
            # Clean XML content
            xml_content = self._clean_xml(xml_content)
            
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Extract channel mappings
            self._parse_channels(root)
            
            # Extract programmes
            self._parse_programmes(root)
            
            # Build schedule
            schedule = self._build_schedule()
            
            return {
                'channels': self.channel_mapping,
                'programmes': self.programmes,
                'schedule': schedule,
                'total_channels': len(self.channel_mapping),
                'total_programmes': len(self.programmes)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse EPG XML: {e}")
            return {
                'channels': {},
                'programmes': [],
                'schedule': {},
                'error': str(e)
            }
    
    def _clean_xml(self, xml_content: str) -> str:
        """
        Clean XML content to handle common issues.
        
        Args:
            xml_content: Raw XML content
            
        Returns:
            Cleaned XML content
        """
        # Remove invalid XML characters
        xml_content = re.sub(
            r'[^\x09\x0A\x0D\x20-\x7E\x85\xA0-\uD7FF\uE000-\uFFFD]', '',
            xml_content
        )
        
        # Fix ampersands
        entities = ['&amp;', '&lt;', '&gt;', '&quot;', '&apos;', '&#']
        placeholders = {}
        
        # Protect existing entities
        for i, entity in enumerate(entities):
            placeholder = f'__PROTECT_{i}__'
            placeholders[placeholder] = entity
            xml_content = xml_content.replace(entity, placeholder)
        
        # Escape bare ampersands
        xml_content = xml_content.replace('&', '&amp;')
        
        # Restore protected entities
        for placeholder, entity in placeholders.items():
            xml_content = xml_content.replace(placeholder, entity)
        
        return xml_content
    
    def _parse_channels(self, root: ET.Element) -> None:
        """
        Parse channel elements from EPG XML.
        
        Args:
            root: XML root element
        """
        self.channel_mapping = {}
        
        for channel in root.findall('.//channel'):
            channel_id = channel.get('id')
            if not channel_id:
                continue
            
            channel_info = {
                'id': channel_id,
                'display_name': '',
                'icon': '',
                'url': ''
            }
            
            # Get display name
            display_name = channel.find('display-name')
            if display_name is not None and display_name.text:
                channel_info['display_name'] = display_name.text
            
            # Get icon
            icon = channel.find('icon')
            if icon is not None:
                channel_info['icon'] = icon.get('src', '')
            
            # Get URL
            url = channel.find('url')
            if url is not None and url.text:
                channel_info['url'] = url.text
            
            self.channel_mapping[channel_id] = channel_info
    
    def _parse_programmes(self, root: ET.Element) -> None:
        """
        Parse programme elements from EPG XML.
        
        Args:
            root: XML root element
        """
        self.programmes = []
        
        for programme in root.findall('.//programme'):
            try:
                prog_info = self._parse_single_programme(programme)
                if prog_info:
                    self.programmes.append(prog_info)
            except Exception as e:
                self.logger.debug(f"Failed to parse programme: {e}")
                continue
    
    def _parse_single_programme(self, programme: ET.Element) -> Optional[Dict[str, Any]]:
        """
        Parse a single programme element.
        
        Args:
            programme: Programme XML element
            
        Returns:
            Dictionary with programme information or None
        """
        channel_id = programme.get('channel')
        start = programme.get('start')
        
        if not channel_id or not start:
            return None
        
        prog_info = {
            'channel_id': channel_id,
            'channel_name': self.channel_mapping.get(channel_id, {}).get('display_name', channel_id),
            'start': self._parse_time(start),
            'stop': None,
            'title': '',
            'description': '',
            'category': '',
            'episode': '',
            'icon': '',
            'rating': ''
        }
        
        # Get stop time
        stop = programme.get('stop')
        if stop:
            prog_info['stop'] = self._parse_time(stop)
        
        # Get title
        title_elem = programme.find('title')
        if title_elem is not None and title_elem.text:
            prog_info['title'] = title_elem.text
        
        # Get description
        desc_elem = programme.find('desc')
        if desc_elem is not None and desc_elem.text:
            prog_info['description'] = desc_elem.text
        
        # Get category
        category_elem = programme.find('category')
        if category_elem is not None and category_elem.text:
            prog_info['category'] = category_elem.text
        
        # Get episode info
        episode_elem = programme.find('episode-num')
        if episode_elem is not None and episode_elem.text:
            prog_info['episode'] = episode_elem.text
        
        # Get icon
        icon_elem = programme.find('icon')
        if icon_elem is not None:
            prog_info['icon'] = icon_elem.get('src', '')
        
        # Get rating
        rating_elem = programme.find('.//value')
        if rating_elem is not None and rating_elem.text:
            prog_info['rating'] = rating_elem.text
        
        return prog_info
    
    def _parse_time(self, time_str: str) -> Optional[datetime]:
        """
        Parse EPG time format (YYYYMMDDHHMMSS +0000).
        
        Args:
            time_str: Time string in EPG format
            
        Returns:
            Parsed datetime object or None
        """
        try:
            if len(time_str) >= 14:
                dt_str = time_str[:14]
                dt = datetime.strptime(dt_str, '%Y%m%d%H%M%S')
                
                # Handle timezone offset if present
                if len(time_str) > 14:
                    tz_str = time_str[14:].strip()
                    if tz_str.startswith('+') or tz_str.startswith('-'):
                        # Parse timezone offset
                        sign = 1 if tz_str[0] == '+' else -1
                        if len(tz_str) >= 5:
                            hours = int(tz_str[1:3])
                            minutes = int(tz_str[3:5])
                            offset = timedelta(hours=sign * hours, minutes=sign * minutes)
                            dt = dt - offset  # Convert to UTC
                
                return dt
        except Exception as e:
            self.logger.debug(f"Failed to parse time '{time_str}': {e}")
        
        return None
    
    def _build_schedule(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Build a schedule dictionary organized by channel.
        
        Returns:
            Dictionary with channel IDs as keys and programme lists as values
        """
        schedule = {}
        
        for prog in self.programmes:
            channel_id = prog['channel_id']
            
            if channel_id not in schedule:
                schedule[channel_id] = []
            
            schedule_entry = {
                'time': prog['start'].strftime('%H:%M') if prog['start'] else '',
                'end': prog['stop'].strftime('%H:%M') if prog['stop'] else '',
                'show': prog['title'],
                'description': prog['description'],
                'category': prog['category'],
                'source': 'EPG'
            }
            
            schedule[channel_id].append(schedule_entry)
        
        # Sort programmes by start time
        for channel_id in schedule:
            schedule[channel_id].sort(key=lambda x: x['time'])
        
        return schedule
    
    def parse_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse EPG data from a file.
        
        Args:
            file_path: Path to EPG XML file
            
        Returns:
            Parsed EPG data
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return self.parse_epg_xml(content)
            
        except Exception as e:
            self.logger.error(f"Failed to read EPG file {file_path}: {e}")
            return {
                'channels': {},
                'programmes': [],
                'schedule': {},
                'error': str(e)
            }
    
    def parse_from_url(self, url: str) -> Dict[str, Any]:
        """
        Fetch and parse EPG data from a URL.
        
        Args:
            url: URL to EPG XML file
            
        Returns:
            Parsed EPG data
        """
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            return self.parse_epg_xml(response.text)
            
        except Exception as e:
            self.logger.error(f"Failed to fetch EPG from {url}: {e}")
            return {
                'channels': {},
                'programmes': [],
                'schedule': {},
                'error': str(e)
            }
    
    def get_current_programme(self, channel_id: str, schedule: Dict[str, List[Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
        """
        Get the current programme for a channel.
        
        Args:
            channel_id: Channel ID
            schedule: Programme schedule
            
        Returns:
            Current programme information or None
        """
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        
        programmes = schedule.get(channel_id, [])
        
        for prog in reversed(programmes):
            if prog['time'] <= current_time:
                # Check if programme has ended
                if prog.get('end') and prog['end'] < current_time:
                    continue
                return prog
        
        return None
    
    def get_next_programme(self, channel_id: str, schedule: Dict[str, List[Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
        """
        Get the next programme for a channel.
        
        Args:
            channel_id: Channel ID
            schedule: Programme schedule
            
        Returns:
            Next programme information or None
        """
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        
        programmes = schedule.get(channel_id, [])
        
        for prog in programmes:
            if prog['time'] > current_time:
                return prog
        
        return None
    
    def export_schedule_json(self, schedule: Dict[str, List[Dict[str, Any]]], output_path: str) -> bool:
        """
        Export schedule to JSON file.
        
        Args:
            schedule: Programme schedule
            output_path: Path to output file
            
        Returns:
            True if successful
        """
        try:
            import json
            
            # Convert datetime objects to strings for JSON serialization
            export_data = {}
            for channel_id, programmes in schedule.items():
                export_data[channel_id] = []
                for prog in programmes:
                    prog_copy = prog.copy()
                    # Ensure all values are JSON serializable
                    export_data[channel_id].append(prog_copy)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"Exported schedule to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export schedule: {e}")
            return False