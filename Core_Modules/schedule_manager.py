"""
TV Schedule Manager Module
Handles scheduling logic, algorithms, and conflict resolution
"""

import random
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Tuple
from Core_Modules.tv_schedule_db import TVScheduleDB

class ScheduleManager:
    """Manages TV scheduling logic and algorithms"""
    
    def __init__(self, db_path: str = "tv_schedules.db"):
        """Initialize schedule manager with database"""
        self.db = TVScheduleDB(db_path)
        self.time_slot_duration = 30  # Default 30-minute slots
    
    def create_time_grid(self, start_date: str, end_date: str, 
                        slot_duration: int = 30) -> List[Tuple[str, str]]:
        """
        Create a grid of time slots for the schedule period
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            slot_duration: Duration of each slot in minutes (default 30)
        
        Returns:
            List of (start_time, end_time) tuples
        """
        slots = []
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        while current_date <= end:
            # Create slots for each day (24 hours)
            current_time = datetime.combine(current_date.date(), time(0, 0))
            end_of_day = current_time + timedelta(days=1)
            
            while current_time < end_of_day:
                slot_start = current_time
                slot_end = current_time + timedelta(minutes=slot_duration)
                
                slots.append((
                    slot_start.strftime("%Y-%m-%d %H:%M:%S"),
                    slot_end.strftime("%Y-%m-%d %H:%M:%S")
                ))
                
                current_time = slot_end
            
            current_date += timedelta(days=1)
        
        return slots
    
    def fill_schedule_randomly(self, schedule_id: int, channel_id: int,
                              start_date: str, end_date: str,
                              max_consecutive: int = 3,
                              respect_duration: bool = True,
                              prime_time_weight: float = 1.5) -> Dict:
        """
        Fill schedule with shows randomly with intelligent distribution
        
        Args:
            schedule_id: Schedule to fill
            channel_id: Channel to schedule for
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            max_consecutive: Maximum consecutive episodes of same show
            respect_duration: If True, respect show durations
            prime_time_weight: Weight factor for prime time slots (1.0 = no weight)
        
        Returns:
            Dictionary with scheduling results
        """
        # Get available shows for the channel
        shows = self.db.get_shows(channel_id)
        if not shows:
            return {
                'success': False,
                'message': 'No shows available for this channel',
                'slots_filled': 0
            }
        
        # Create time grid
        time_slots = self.create_time_grid(start_date, end_date, self.time_slot_duration)
        
        # Track scheduling
        slots_filled = 0
        conflicts = 0
        last_show_id = None
        consecutive_count = 0
        
        for slot_start, slot_end in time_slots:
            # Check if slot is already occupied
            if self.db.check_time_conflict(schedule_id, channel_id, slot_start, slot_end):
                conflicts += 1
                continue
            
            # Apply prime time weighting (7 PM - 11 PM)
            slot_hour = datetime.strptime(slot_start, "%Y-%m-%d %H:%M:%S").hour
            is_prime_time = 19 <= slot_hour <= 23
            
            # Select show
            if consecutive_count >= max_consecutive or last_show_id is None:
                # Need to switch shows
                available_shows = [s for s in shows if s['show_id'] != last_show_id]
                if not available_shows:
                    available_shows = shows
                
                # Weight shows for prime time
                if is_prime_time and prime_time_weight > 1.0:
                    # Prefer longer/featured shows in prime time
                    weights = [
                        prime_time_weight if show['duration_minutes'] >= 60 else 1.0
                        for show in available_shows
                    ]
                    show = random.choices(available_shows, weights=weights)[0]
                else:
                    show = random.choice(available_shows)
                
                last_show_id = show['show_id']
                consecutive_count = 1
            else:
                # Continue with same show
                show = next((s for s in shows if s['show_id'] == last_show_id), shows[0])
                consecutive_count += 1
            
            # Calculate actual end time based on show duration
            if respect_duration:
                actual_end = datetime.strptime(slot_start, "%Y-%m-%d %H:%M:%S") + \
                           timedelta(minutes=show['duration_minutes'])
                slot_end = actual_end.strftime("%Y-%m-%d %H:%M:%S")
            
            # Add time slot
            try:
                self.db.add_time_slot(
                    schedule_id, channel_id, show['show_id'],
                    slot_start, slot_end, is_repeat=(consecutive_count > 1),
                    notes=f"Auto-scheduled{'(Prime Time)' if is_prime_time else ''}"
                )
                slots_filled += 1
            except Exception as e:
                conflicts += 1
                continue
        
        return {
            'success': True,
            'slots_filled': slots_filled,
            'conflicts': conflicts,
            'total_slots': len(time_slots)
        }
    
    def fill_schedule_sequential(self, schedule_id: int, channel_id: int,
                                start_date: str, end_date: str) -> Dict:
        """
        Fill schedule sequentially cycling through all shows
        
        Args:
            schedule_id: Schedule to fill
            channel_id: Channel to schedule for
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            Dictionary with scheduling results
        """
        # Get available shows sorted by name
        shows = sorted(self.db.get_shows(channel_id), key=lambda x: x['name'])
        if not shows:
            return {
                'success': False,
                'message': 'No shows available for this channel',
                'slots_filled': 0
            }
        
        # Create time grid
        time_slots = self.create_time_grid(start_date, end_date, self.time_slot_duration)
        
        # Track scheduling
        slots_filled = 0
        conflicts = 0
        show_index = 0
        
        for slot_start, slot_end in time_slots:
            # Check if slot is already occupied
            if self.db.check_time_conflict(schedule_id, channel_id, slot_start, slot_end):
                conflicts += 1
                continue
            
            # Get current show
            show = shows[show_index % len(shows)]
            
            # Calculate end time based on show duration
            actual_end = datetime.strptime(slot_start, "%Y-%m-%d %H:%M:%S") + \
                       timedelta(minutes=show['duration_minutes'])
            slot_end = actual_end.strftime("%Y-%m-%d %H:%M:%S")
            
            # Add time slot
            try:
                self.db.add_time_slot(
                    schedule_id, channel_id, show['show_id'],
                    slot_start, slot_end, is_repeat=False,
                    notes="Sequential scheduling"
                )
                slots_filled += 1
                show_index += 1
            except Exception:
                conflicts += 1
                continue
        
        return {
            'success': True,
            'slots_filled': slots_filled,
            'conflicts': conflicts,
            'total_slots': len(time_slots)
        }
    
    def fill_schedule_weighted(self, schedule_id: int, channel_id: int,
                             start_date: str, end_date: str,
                             weights: Dict[int, float] = None) -> Dict:
        """
        Fill schedule with weighted show distribution
        
        Args:
            schedule_id: Schedule to fill
            channel_id: Channel to schedule for
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            weights: Dictionary mapping show_id to weight (higher = more frequent)
        
        Returns:
            Dictionary with scheduling results
        """
        # Get available shows
        shows = self.db.get_shows(channel_id)
        if not shows:
            return {
                'success': False,
                'message': 'No shows available for this channel',
                'slots_filled': 0
            }
        
        # Apply weights
        if weights:
            show_weights = [weights.get(show['show_id'], 1.0) for show in shows]
        else:
            # Default: weight by duration (longer shows less frequent)
            max_duration = max(s['duration_minutes'] for s in shows)
            show_weights = [
                max_duration / show['duration_minutes'] 
                for show in shows
            ]
        
        # Create time grid
        time_slots = self.create_time_grid(start_date, end_date, self.time_slot_duration)
        
        # Track scheduling
        slots_filled = 0
        conflicts = 0
        
        for slot_start, slot_end in time_slots:
            # Check if slot is already occupied
            if self.db.check_time_conflict(schedule_id, channel_id, slot_start, slot_end):
                conflicts += 1
                continue
            
            # Select show based on weights
            show = random.choices(shows, weights=show_weights)[0]
            
            # Calculate end time based on show duration
            actual_end = datetime.strptime(slot_start, "%Y-%m-%d %H:%M:%S") + \
                       timedelta(minutes=show['duration_minutes'])
            slot_end = actual_end.strftime("%Y-%m-%d %H:%M:%S")
            
            # Add time slot
            try:
                self.db.add_time_slot(
                    schedule_id, channel_id, show['show_id'],
                    slot_start, slot_end, is_repeat=False,
                    notes="Weighted scheduling"
                )
                slots_filled += 1
            except Exception:
                conflicts += 1
                continue
        
        return {
            'success': True,
            'slots_filled': slots_filled,
            'conflicts': conflicts,
            'total_slots': len(time_slots)
        }
    
    def resolve_conflicts(self, schedule_id: int) -> Dict:
        """
        Find and resolve scheduling conflicts
        
        Args:
            schedule_id: Schedule to check
        
        Returns:
            Dictionary with conflict resolution results
        """
        all_slots = self.db.get_time_slots(schedule_id)
        
        conflicts_found = []
        conflicts_resolved = 0
        
        # Group slots by channel
        channels = {}
        for slot in all_slots:
            channel_id = slot['channel_id']
            if channel_id not in channels:
                channels[channel_id] = []
            channels[channel_id].append(slot)
        
        # Check each channel for conflicts
        for channel_id, slots in channels.items():
            # Sort by start time
            slots.sort(key=lambda x: x['start_time'])
            
            for i in range(len(slots) - 1):
                current = slots[i]
                next_slot = slots[i + 1]
                
                # Check for overlap
                if current['end_time'] > next_slot['start_time']:
                    conflicts_found.append({
                        'channel': current['channel_name'],
                        'slot1': current,
                        'slot2': next_slot,
                        'overlap_minutes': (
                            datetime.strptime(current['end_time'], "%Y-%m-%d %H:%M:%S") -
                            datetime.strptime(next_slot['start_time'], "%Y-%m-%d %H:%M:%S")
                        ).total_seconds() / 60
                    })
                    
                    # Attempt to resolve by adjusting end time
                    new_end = next_slot['start_time']
                    if self.db.update_time_slot(current['slot_id'], end_time=new_end):
                        conflicts_resolved += 1
        
        return {
            'conflicts_found': len(conflicts_found),
            'conflicts_resolved': conflicts_resolved,
            'unresolved': conflicts_found[conflicts_resolved:],
            'details': conflicts_found
        }
    
    def get_channel_utilization(self, schedule_id: int) -> Dict:
        """
        Calculate channel utilization statistics
        
        Args:
            schedule_id: Schedule to analyze
        
        Returns:
            Dictionary with utilization statistics per channel
        """
        stats = self.db.get_schedule_statistics(schedule_id)
        
        # Get schedule info
        schedules = self.db.get_schedules()
        schedule = next((s for s in schedules if s['schedule_id'] == schedule_id), None)
        
        if not schedule:
            return {'error': 'Schedule not found'}
        
        # Calculate total possible minutes
        start_date = datetime.strptime(schedule['start_date'], "%Y-%m-%d")
        end_date = datetime.strptime(schedule['end_date'], "%Y-%m-%d")
        total_days = (end_date - start_date).days + 1
        total_minutes = total_days * 24 * 60  # Total minutes in period
        
        # Get utilization per channel
        utilization = {}
        for channel_stat in stats.get('channels', []):
            channel_name = channel_stat['name']
            slot_count = channel_stat['slot_count']
            
            # Get actual scheduled minutes for this channel
            channel_slots = [
                slot for slot in self.db.get_time_slots(schedule_id)
                if slot['channel_name'] == channel_name
            ]
            
            scheduled_minutes = 0
            for slot in channel_slots:
                start = datetime.strptime(slot['start_time'], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(slot['end_time'], "%Y-%m-%d %H:%M:%S")
                scheduled_minutes += (end - start).total_seconds() / 60
            
            utilization[channel_name] = {
                'total_slots': slot_count,
                'scheduled_minutes': scheduled_minutes,
                'total_available_minutes': total_minutes,
                'utilization_percent': (scheduled_minutes / total_minutes) * 100 if total_minutes > 0 else 0
            }
        
        return utilization
    
    def simulate_channel_switching(self, schedule_id: int, start_time: str, 
                                  duration_minutes: int, 
                                  switch_interval_minutes: int = 5) -> List[Dict]:
        """
        Simulate channel switching behavior
        
        Args:
            schedule_id: Schedule to simulate
            start_time: Simulation start time (YYYY-MM-DD HH:MM:SS)
            duration_minutes: Total simulation duration
            switch_interval_minutes: How often to switch channels
        
        Returns:
            List of viewing events
        """
        viewing_events = []
        current_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        end_time = current_time + timedelta(minutes=duration_minutes)
        
        # Get all channels
        channels = self.db.get_channels()
        if not channels:
            return []
        
        current_channel_index = 0
        switch_time = current_time + timedelta(minutes=switch_interval_minutes)
        
        while current_time < end_time:
            channel = channels[current_channel_index % len(channels)]
            
            # Find what's playing on this channel at this time
            date_str = current_time.strftime("%Y-%m-%d")
            time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            slots = self.db.get_time_slots(
                schedule_id, 
                channel_id=channel['channel_id']
            )
            
            # Find the slot that contains current time
            current_show = None
            for slot in slots:
                if slot['start_time'] <= time_str <= slot['end_time']:
                    current_show = slot
                    break
            
            viewing_events.append({
                'time': time_str,
                'channel': channel['name'],
                'channel_id': channel['channel_id'],
                'show': current_show['show_name'] if current_show else 'No programming',
                'show_id': current_show['show_id'] if current_show else None,
                'action': 'switch' if current_time >= switch_time else 'watching'
            })
            
            # Check if time to switch
            if current_time >= switch_time:
                current_channel_index += 1
                switch_time = current_time + timedelta(minutes=switch_interval_minutes)
            
            # Advance time by 1 minute
            current_time += timedelta(minutes=1)
        
        return viewing_events
    
    def recommend_schedule_optimization(self, schedule_id: int) -> Dict:
        """
        Analyze schedule and recommend optimizations
        
        Args:
            schedule_id: Schedule to analyze
        
        Returns:
            Dictionary with optimization recommendations
        """
        recommendations = []
        
        # Get utilization stats
        utilization = self.get_channel_utilization(schedule_id)
        
        # Check for underutilized channels
        for channel, stats in utilization.items():
            if stats['utilization_percent'] < 50:
                recommendations.append({
                    'type': 'underutilized_channel',
                    'channel': channel,
                    'utilization': stats['utilization_percent'],
                    'suggestion': f"Channel '{channel}' is only {stats['utilization_percent']:.1f}% utilized. Consider adding more shows."
                })
        
        # Check for conflicts
        conflicts = self.resolve_conflicts(schedule_id)
        if conflicts['conflicts_found'] > 0:
            recommendations.append({
                'type': 'conflicts',
                'count': conflicts['conflicts_found'],
                'resolved': conflicts['conflicts_resolved'],
                'suggestion': f"Found {conflicts['conflicts_found']} scheduling conflicts. {conflicts['conflicts_resolved']} were auto-resolved."
            })
        
        # Analyze show distribution
        stats = self.db.get_schedule_statistics(schedule_id)
        top_shows = stats.get('top_shows', [])
        
        if top_shows:
            # Check if any show dominates
            total_slots = sum(s['schedule_count'] for s in top_shows)
            if top_shows[0]['schedule_count'] / total_slots > 0.3:
                recommendations.append({
                    'type': 'show_imbalance',
                    'show': top_shows[0]['name'],
                    'percentage': (top_shows[0]['schedule_count'] / total_slots) * 100,
                    'suggestion': f"Show '{top_shows[0]['name']}' appears in {top_shows[0]['schedule_count']} slots ({(top_shows[0]['schedule_count'] / total_slots) * 100:.1f}% of scheduled content). Consider more variety."
                })
        
        # Check for prime time optimization
        all_slots = self.db.get_time_slots(schedule_id)
        prime_time_slots = [
            slot for slot in all_slots
            if 19 <= datetime.strptime(slot['start_time'], "%Y-%m-%d %H:%M:%S").hour <= 23
        ]
        
        if prime_time_slots:
            # Check if prime time has premium content
            short_shows_in_prime = [
                slot for slot in prime_time_slots
                if slot.get('duration_minutes', 30) < 60
            ]
            
            if len(short_shows_in_prime) / len(prime_time_slots) > 0.5:
                recommendations.append({
                    'type': 'prime_time_optimization',
                    'short_shows': len(short_shows_in_prime),
                    'total_prime_slots': len(prime_time_slots),
                    'suggestion': "Consider scheduling longer/featured content during prime time (7 PM - 11 PM)"
                })
        
        return {
            'recommendations': recommendations,
            'total_recommendations': len(recommendations),
            'schedule_health': 'good' if len(recommendations) <= 2 else 'needs_attention'
        }