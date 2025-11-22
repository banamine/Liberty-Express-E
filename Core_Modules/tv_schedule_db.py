"""
TV Schedule Database Module
Handles SQLite database operations for TV scheduling system
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import threading

class TVScheduleDB:
    """SQLite database handler for TV scheduling system"""
    
    def __init__(self, db_path: str = "tv_schedules.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = Path(db_path)
        self.lock = threading.Lock()
        self._create_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a new database connection"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Channels table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    channel_group TEXT,
                    logo_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Shows table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shows (
                    show_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id INTEGER,
                    name TEXT NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    description TEXT,
                    genre TEXT,
                    rating TEXT,
                    thumbnail_url TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
                )
            """)
            
            # Schedules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schedules (
                    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Time slots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS time_slots (
                    slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schedule_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    show_id INTEGER,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    is_repeat BOOLEAN DEFAULT 0,
                    notes TEXT,
                    FOREIGN KEY (schedule_id) REFERENCES schedules (schedule_id),
                    FOREIGN KEY (channel_id) REFERENCES channels (channel_id),
                    FOREIGN KEY (show_id) REFERENCES shows (show_id)
                )
            """)
            
            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_time_slots_schedule 
                ON time_slots (schedule_id, start_time)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_time_slots_channel 
                ON time_slots (channel_id, start_time)
            """)
            
            conn.commit()
            conn.close()
    
    # Channel operations
    def add_channel(self, name: str, description: str = "", 
                   group: str = "", logo_url: str = "") -> int:
        """Add a new channel to the database"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO channels (name, description, channel_group, logo_url)
                    VALUES (?, ?, ?, ?)
                """, (name, description, group, logo_url))
                
                channel_id = cursor.lastrowid
                conn.commit()
                return channel_id
            except sqlite3.IntegrityError:
                # Channel already exists
                cursor.execute("SELECT channel_id FROM channels WHERE name = ?", (name,))
                return cursor.fetchone()[0]
            finally:
                conn.close()
    
    def get_channels(self) -> List[Dict]:
        """Get all channels from the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT channel_id, name, description, channel_group, logo_url
            FROM channels
            ORDER BY name
        """)
        
        channels = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return channels
    
    def delete_channel(self, channel_id: int) -> bool:
        """Delete a channel and all associated data"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete associated time slots
            cursor.execute("DELETE FROM time_slots WHERE channel_id = ?", (channel_id,))
            
            # Delete associated shows
            cursor.execute("DELETE FROM shows WHERE channel_id = ?", (channel_id,))
            
            # Delete channel
            cursor.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
            
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
    
    # Show operations
    def add_show(self, channel_id: int, name: str, duration_minutes: int,
                 description: str = "", genre: str = "", rating: str = "",
                 thumbnail_url: str = "", metadata: Dict = None) -> int:
        """Add a new show to the database"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            metadata_str = json.dumps(metadata) if metadata else ""
            
            cursor.execute("""
                INSERT INTO shows (channel_id, name, duration_minutes, description,
                                 genre, rating, thumbnail_url, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (channel_id, name, duration_minutes, description, 
                 genre, rating, thumbnail_url, metadata_str))
            
            show_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return show_id
    
    def get_shows(self, channel_id: Optional[int] = None) -> List[Dict]:
        """Get shows, optionally filtered by channel"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if channel_id:
            cursor.execute("""
                SELECT s.*, c.name as channel_name
                FROM shows s
                JOIN channels c ON s.channel_id = c.channel_id
                WHERE s.channel_id = ?
                ORDER BY s.name
            """, (channel_id,))
        else:
            cursor.execute("""
                SELECT s.*, c.name as channel_name
                FROM shows s
                JOIN channels c ON s.channel_id = c.channel_id
                ORDER BY c.name, s.name
            """)
        
        shows = []
        for row in cursor.fetchall():
            show = dict(row)
            if show['metadata']:
                show['metadata'] = json.loads(show['metadata'])
            shows.append(show)
        
        conn.close()
        return shows
    
    def update_show(self, show_id: int, **kwargs) -> bool:
        """Update show details"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Build update query dynamically
            fields = []
            values = []
            for field, value in kwargs.items():
                if field == 'metadata' and isinstance(value, dict):
                    value = json.dumps(value)
                fields.append(f"{field} = ?")
                values.append(value)
            
            if not fields:
                return False
            
            values.append(show_id)
            query = f"UPDATE shows SET {', '.join(fields)} WHERE show_id = ?"
            
            cursor.execute(query, values)
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
    
    def delete_show(self, show_id: int) -> bool:
        """Delete a show and associated time slots"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete associated time slots
            cursor.execute("DELETE FROM time_slots WHERE show_id = ?", (show_id,))
            
            # Delete show
            cursor.execute("DELETE FROM shows WHERE show_id = ?", (show_id,))
            
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
    
    # Schedule operations
    def create_schedule(self, name: str, start_date: str, end_date: str) -> int:
        """Create a new schedule"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO schedules (name, start_date, end_date)
                VALUES (?, ?, ?)
            """, (name, start_date, end_date))
            
            schedule_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return schedule_id
    
    def get_schedules(self) -> List[Dict]:
        """Get all schedules"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT schedule_id, name, start_date, end_date, created_at, last_modified
            FROM schedules
            ORDER BY last_modified DESC
        """)
        
        schedules = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return schedules
    
    def delete_schedule(self, schedule_id: int) -> bool:
        """Delete a schedule and all its time slots"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete time slots
            cursor.execute("DELETE FROM time_slots WHERE schedule_id = ?", (schedule_id,))
            
            # Delete schedule
            cursor.execute("DELETE FROM schedules WHERE schedule_id = ?", (schedule_id,))
            
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
    
    # Time slot operations
    def add_time_slot(self, schedule_id: int, channel_id: int, show_id: Optional[int],
                     start_time: str, end_time: str, is_repeat: bool = False,
                     notes: str = "") -> int:
        """Add a time slot to a schedule"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO time_slots (schedule_id, channel_id, show_id, 
                                      start_time, end_time, is_repeat, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (schedule_id, channel_id, show_id, start_time, end_time, 
                 is_repeat, notes))
            
            slot_id = cursor.lastrowid
            
            # Update schedule modification time
            cursor.execute("""
                UPDATE schedules SET last_modified = CURRENT_TIMESTAMP
                WHERE schedule_id = ?
            """, (schedule_id,))
            
            conn.commit()
            conn.close()
            return slot_id
    
    def get_time_slots(self, schedule_id: int, channel_id: Optional[int] = None,
                       date: Optional[str] = None) -> List[Dict]:
        """Get time slots for a schedule, optionally filtered by channel or date"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT ts.*, c.name as channel_name, s.name as show_name,
                   s.duration_minutes, s.description as show_description
            FROM time_slots ts
            JOIN channels c ON ts.channel_id = c.channel_id
            LEFT JOIN shows s ON ts.show_id = s.show_id
            WHERE ts.schedule_id = ?
        """
        
        params = [schedule_id]
        
        if channel_id:
            query += " AND ts.channel_id = ?"
            params.append(channel_id)
        
        if date:
            query += " AND DATE(ts.start_time) = ?"
            params.append(date)
        
        query += " ORDER BY ts.start_time, c.name"
        
        cursor.execute(query, params)
        slots = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return slots
    
    def check_time_conflict(self, schedule_id: int, channel_id: int,
                           start_time: str, end_time: str,
                           exclude_slot_id: Optional[int] = None) -> bool:
        """Check if there's a time conflict for a given slot"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT COUNT(*) as count
            FROM time_slots
            WHERE schedule_id = ? AND channel_id = ?
            AND (
                (start_time <= ? AND end_time > ?) OR
                (start_time < ? AND end_time >= ?) OR
                (start_time >= ? AND end_time <= ?)
            )
        """
        
        params = [schedule_id, channel_id, start_time, start_time, 
                 end_time, end_time, start_time, end_time]
        
        if exclude_slot_id:
            query += " AND slot_id != ?"
            params.append(exclude_slot_id)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        
        return result['count'] > 0
    
    def update_time_slot(self, slot_id: int, **kwargs) -> bool:
        """Update a time slot"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Build update query
            fields = []
            values = []
            for field, value in kwargs.items():
                fields.append(f"{field} = ?")
                values.append(value)
            
            if not fields:
                return False
            
            values.append(slot_id)
            query = f"UPDATE time_slots SET {', '.join(fields)} WHERE slot_id = ?"
            
            cursor.execute(query, values)
            
            # Update schedule modification time
            cursor.execute("""
                UPDATE schedules SET last_modified = CURRENT_TIMESTAMP
                WHERE schedule_id = (SELECT schedule_id FROM time_slots WHERE slot_id = ?)
            """, (slot_id,))
            
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
    
    def delete_time_slot(self, slot_id: int) -> bool:
        """Delete a time slot"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get schedule_id before deletion
            cursor.execute("SELECT schedule_id FROM time_slots WHERE slot_id = ?", (slot_id,))
            result = cursor.fetchone()
            
            if result:
                schedule_id = result[0]
                
                # Delete time slot
                cursor.execute("DELETE FROM time_slots WHERE slot_id = ?", (slot_id,))
                
                # Update schedule modification time
                cursor.execute("""
                    UPDATE schedules SET last_modified = CURRENT_TIMESTAMP
                    WHERE schedule_id = ?
                """, (schedule_id,))
                
                conn.commit()
                success = True
            else:
                success = False
            
            conn.close()
            return success
    
    # Export/Import operations
    def export_schedule(self, schedule_id: int) -> Dict:
        """Export a schedule as a dictionary"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get schedule info
        cursor.execute("""
            SELECT * FROM schedules WHERE schedule_id = ?
        """, (schedule_id,))
        schedule = dict(cursor.fetchone())
        
        # Get all time slots
        slots = self.get_time_slots(schedule_id)
        schedule['time_slots'] = slots
        
        # Get all channels used in schedule
        cursor.execute("""
            SELECT DISTINCT c.*
            FROM channels c
            JOIN time_slots ts ON c.channel_id = ts.channel_id
            WHERE ts.schedule_id = ?
        """, (schedule_id,))
        schedule['channels'] = [dict(row) for row in cursor.fetchall()]
        
        # Get all shows used in schedule
        cursor.execute("""
            SELECT DISTINCT s.*
            FROM shows s
            JOIN time_slots ts ON s.show_id = ts.show_id
            WHERE ts.schedule_id = ?
        """, (schedule_id,))
        schedule['shows'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return schedule
    
    def import_schedule(self, schedule_data: Dict) -> int:
        """Import a schedule from a dictionary"""
        with self.lock:
            # Create new schedule
            schedule_id = self.create_schedule(
                schedule_data['name'] + " (Imported)",
                schedule_data['start_date'],
                schedule_data['end_date']
            )
            
            # Map old IDs to new IDs
            channel_map = {}
            show_map = {}
            
            # Import channels
            for channel in schedule_data.get('channels', []):
                new_id = self.add_channel(
                    channel['name'],
                    channel.get('description', ''),
                    channel.get('channel_group', ''),
                    channel.get('logo_url', '')
                )
                channel_map[channel['channel_id']] = new_id
            
            # Import shows
            for show in schedule_data.get('shows', []):
                new_channel_id = channel_map.get(show['channel_id'])
                if new_channel_id:
                    new_id = self.add_show(
                        new_channel_id,
                        show['name'],
                        show['duration_minutes'],
                        show.get('description', ''),
                        show.get('genre', ''),
                        show.get('rating', ''),
                        show.get('thumbnail_url', ''),
                        json.loads(show['metadata']) if show.get('metadata') else None
                    )
                    show_map[show['show_id']] = new_id
            
            # Import time slots
            for slot in schedule_data.get('time_slots', []):
                new_channel_id = channel_map.get(slot['channel_id'])
                new_show_id = show_map.get(slot['show_id']) if slot['show_id'] else None
                
                if new_channel_id:
                    self.add_time_slot(
                        schedule_id,
                        new_channel_id,
                        new_show_id,
                        slot['start_time'],
                        slot['end_time'],
                        slot.get('is_repeat', False),
                        slot.get('notes', '')
                    )
            
            return schedule_id
    
    def get_schedule_statistics(self, schedule_id: int) -> Dict:
        """Get statistics for a schedule"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total time slots
        cursor.execute("""
            SELECT COUNT(*) as total_slots,
                   COUNT(DISTINCT channel_id) as total_channels,
                   COUNT(DISTINCT DATE(start_time)) as total_days,
                   MIN(start_time) as first_slot,
                   MAX(end_time) as last_slot
            FROM time_slots
            WHERE schedule_id = ?
        """, (schedule_id,))
        
        result = dict(cursor.fetchone())
        stats.update(result)
        
        # Shows per channel
        cursor.execute("""
            SELECT c.name, COUNT(*) as slot_count
            FROM time_slots ts
            JOIN channels c ON ts.channel_id = c.channel_id
            WHERE ts.schedule_id = ?
            GROUP BY c.channel_id, c.name
            ORDER BY slot_count DESC
        """, (schedule_id,))
        
        stats['channels'] = [dict(row) for row in cursor.fetchall()]
        
        # Most scheduled shows
        cursor.execute("""
            SELECT s.name, COUNT(*) as schedule_count
            FROM time_slots ts
            JOIN shows s ON ts.show_id = s.show_id
            WHERE ts.schedule_id = ?
            GROUP BY s.show_id, s.name
            ORDER BY schedule_count DESC
            LIMIT 10
        """, (schedule_id,))
        
        stats['top_shows'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return stats