import re
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class EpisodeParser:
    def __init__(self):
        self.patterns = [
            (r'S(\d{2})E(\d{2})\s*-\s*(.+)', 'standard'),
            (r'S(\d{2})E(\d{2})\s+(.+)', 'no_dash'),
            (r'Season\s*(\d+)\s*Episode\s*(\d+)\s*-\s*(.+)', 'verbose'),
            (r'(\d+)x(\d+)\s*-\s*(.+)', 'compact'),
            (r'#EXTINF:\d+,The Odd Couple S(\d{2})E(\d{2}) - (.+)', 'extinf')
        ]

    def parse_episode_from_line(self, line: str, next_line: str = None) -> Optional[Dict]:
        """Parse episode information from M3U line"""
        if not line or not line.strip():
            return None

        line = line.strip()
        
        for pattern, pattern_type in self.patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    return self._build_episode_data(match, pattern_type, next_line)
                except Exception as e:
                    logger.warning(f"Error parsing line: {e}")
                    continue

        return None

    def _build_episode_data(self, match: re.Match, pattern_type: str, next_line: str) -> Dict:
        """Build episode data dictionary from regex match"""
        if pattern_type in ['standard', 'no_dash', 'extinf']:
            season, episode, title = match.groups()
        elif pattern_type == 'verbose':
            season, episode, title = match.groups()
            season = season.zfill(2)
            episode = episode.zfill(2)
        elif pattern_type == 'compact':
            season, episode, title = match.groups()
            season = season.zfill(2)
            episode = episode.zfill(2)
        else:
            raise ValueError(f"Unknown pattern type: {pattern_type}")

        season = int(season)
        episode = int(episode)
        key = f"S{season:02d}E{episode:02d}"
        
        # Extract URL from next line if provided
        url = None
        if next_line and next_line.strip().startswith('http'):
            url = next_line.strip()

        return {
            "key": key,
            "season": season,
            "episode": episode,
            "title": title.strip(),
            "url": url,
            "duration": 0,
            "thumb": "",
            "valid": False,
            "imported_at": None
        }

    def parse_m3u_file(self, file_path: str) -> Tuple[List[Dict], List[str]]:
        """Parse entire M3U file and return episodes and errors"""
        episodes = []
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            i = 0
            while i < len(lines):
                line = lines[i]
                next_line = lines[i + 1] if i + 1 < len(lines) else None
                
                if line.startswith('#EXTINF:'):
                    episode = self.parse_episode_from_line(line, next_line)
                    if episode and episode.get('url'):
                        episodes.append(episode)
                        i += 2  # Skip URL line
                        continue
                    elif episode:
                        errors.append(f"Missing URL for: {episode['key']}")
                
                i += 1

        except Exception as e:
            errors.append(f"Error reading file: {e}")

        return episodes, errors