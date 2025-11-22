# 📺 TV Schedule Center - Complete User Guide

## Overview
The **TV Schedule Center** is a comprehensive television scheduling system integrated with M3U MATRIX PRO. It provides visual calendar management, automated scheduling algorithms, and professional broadcast-quality programming control.

---

## ✨ Key Features

### Visual Calendar Interface
- **Weekly Grid View**: 7-day calendar with 30-minute time slots
- **Drag & Drop**: Move shows between time slots effortlessly
- **Color-Coded Slots**: Visual indicators for empty, filled, selected, and conflicting slots
- **Week Navigation**: Browse past and future weeks with navigation buttons

### Database Management
- **SQLite Persistence**: All schedules saved automatically
- **Channel Management**: Add, edit, delete TV channels
- **Show Library**: Comprehensive show database with metadata
- **Import/Export**: Share schedules via JSON files

### Intelligent Scheduling
- **Random Fill**: Smart algorithm with prime-time weighting
- **Sequential Fill**: Cycle through shows in order
- **Weighted Distribution**: Control show frequency with custom weights
- **Conflict Detection**: Automatic identification and resolution

### Advanced Features
- **Channel Switching Simulation**: Preview viewer experience
- **Utilization Statistics**: Track channel usage and efficiency
- **Schedule Optimization**: AI-powered recommendations
- **Multi-Channel Support**: Manage unlimited channels

---

## 🚀 Getting Started

### Launch from M3U MATRIX PRO
1. Open **M3U MATRIX PRO**
2. Click the **📅 TV Schedule Center** button (green button in toolbar)
3. The Schedule Center opens in a new window

### Standalone Launch
```bash
python Applications/TV_SCHEDULE_CENTER.py
```

---

## 📋 Step-by-Step Guide

### 1. Create Your First Schedule

**Step 1: Create New Schedule**
- Click **📅 New Schedule** button
- Enter schedule name (e.g., "January 2025 Programming")
- Set start date (e.g., 2025-01-01)
- Set end date (e.g., 2025-01-31)
- Click **Create**

**Step 2: Add Channels**
- In left panel, click **➕ Add** under Channels
- Enter channel name (e.g., "Sports Network")
- Add optional description and group
- Click **Add**

**Step 3: Add Shows**
- Select a channel from the list
- Click **➕ Add Show** under Shows
- Enter show details:
  - Name: "Morning Sports News"
  - Duration: 30 minutes
  - Genre: Sports
  - Description: Daily sports updates
- Click **Add**

### 2. Schedule Programming

#### Manual Scheduling
1. Select a show from the left panel
2. Double-click a time slot in the grid
3. Select the show from the popup
4. The slot fills with the show

#### Automatic Scheduling

**Random Fill (Recommended)**
1. Select a channel
2. Click **🎲 Fill Randomly**
3. Algorithm fills week with intelligent distribution:
   - Respects show durations
   - Weights prime time (7-11 PM)
   - Limits consecutive episodes

**Sequential Fill**
1. Select a channel
2. Click **📊 Sequential Fill**
3. Shows cycle in alphabetical order

**Weighted Fill**
1. Select a channel
2. Click **⚖️ Weighted Fill**
3. Longer shows appear less frequently

### 3. Manage Your Schedule

**Edit Time Slots**
- Single-click: View slot details
- Double-click: Quick edit
- Delete key: Remove show from slot
- Drag & drop: Move shows between slots

**Navigate Weeks**
- **◀ Previous Week**: Go back one week
- **Next Week ▶**: Go forward one week
- Current week shown in header

**Check for Conflicts**
- Click **🔍 Check Conflicts**
- Overlapping shows highlighted
- Auto-resolve option available

### 4. Simulate & Optimize

**Channel Switching Simulation**
- Click **🎬 Simulate Viewing**
- Watch simulated viewer behavior
- See channel switching patterns
- Identify popular time slots

**View Statistics**
- Right panel shows real-time stats
- Channel utilization percentages
- Total slots filled
- Most scheduled shows

---

## 📊 Database Schema

### Tables Structure

**channels**
- `channel_id`: Primary key
- `name`: Channel name
- `description`: Channel description
- `channel_group`: Category/group
- `logo_url`: Channel logo

**shows**
- `show_id`: Primary key
- `channel_id`: Foreign key to channels
- `name`: Show name
- `duration_minutes`: Show length
- `genre`: Show category
- `rating`: Content rating

**schedules**
- `schedule_id`: Primary key
- `name`: Schedule name
- `start_date`: Schedule start
- `end_date`: Schedule end

**time_slots**
- `slot_id`: Primary key
- `schedule_id`: Foreign key
- `channel_id`: Foreign key
- `show_id`: Foreign key
- `start_time`: Slot start
- `end_time`: Slot end

---

## 🎨 Interface Guide

### Color Coding
- **Dark Gray** (`#3a3a3a`): Empty time slot
- **Blue** (`#4a90e2`): Filled with show
- **Green** (`#6ab04c`): Selected slot
- **Red** (`#e74c3c`): Conflict detected

### Keyboard Shortcuts
- **Ctrl+N**: New schedule
- **Ctrl+S**: Save schedule
- **Ctrl+O**: Open schedule
- **Delete**: Remove selected slot
- **F5**: Refresh view

---

## 💡 Pro Tips

### Best Practices
1. **Start with Templates**: Create base schedules for reuse
2. **Group Similar Shows**: Organize by genre for easier management
3. **Use Prime Time Wisely**: Schedule popular content 7-11 PM
4. **Regular Backups**: Export schedules weekly

### Optimization Strategy
1. **Balance Channels**: Aim for 70-80% utilization
2. **Vary Content**: Mix show lengths and genres
3. **Consider Audience**: Schedule by viewing patterns
4. **Test Simulations**: Preview before broadcasting

### Troubleshooting

**Issue: Schedule not saving**
- Check write permissions for `tv_schedules.db`
- Ensure sufficient disk space

**Issue: Shows not appearing**
- Verify channel is selected
- Check show duration fits time slot
- Refresh view with F5

**Issue: Conflicts detected**
- Use automatic conflict resolution
- Manually adjust overlapping shows
- Check show durations

---

## 📁 File Locations

```
Project Root/
├── Applications/
│   ├── M3U_MATRIX_PRO.py (Launch button)
│   └── TV_SCHEDULE_CENTER.py (Main app)
├── Core_Modules/
│   ├── tv_schedule_db.py (Database)
│   └── schedule_manager.py (Logic)
└── tv_schedules.db (SQLite database)
```

---

## 🔄 Integration with M3U MATRIX PRO

### Export to Player Templates
1. Create schedule in TV Schedule Center
2. Export as JSON
3. Import into M3U MATRIX PRO
4. Generate player pages with schedule

### Workflow Example
```
TV Schedule Center → Create Schedule → Export JSON
                                          ↓
M3U MATRIX PRO ← Import Schedule ← Schedule Data
        ↓
Generate NexusTV/WebIPTV with Schedule
```

---

## 📈 Advanced Features

### Custom Scheduling Algorithms
The system supports three scheduling modes:

**1. Random with Intelligence**
```python
- Prime time weighting (1.5x)
- Max consecutive episodes (3)
- Respects show durations
- Conflict avoidance
```

**2. Sequential Rotation**
```python
- Alphabetical show order
- Even distribution
- No clustering
- Predictable patterns
```

**3. Weighted Distribution**
```python
- Custom weight per show
- Inverse duration weighting
- Popularity-based scheduling
- Manual control
```

### Database Operations

**Export Schedule**
```python
schedule_data = db.export_schedule(schedule_id)
# Returns complete schedule with channels, shows, slots
```

**Import Schedule**
```python
new_id = db.import_schedule(schedule_data)
# Creates new schedule from JSON data
```

**Get Statistics**
```python
stats = db.get_schedule_statistics(schedule_id)
# Returns utilization, channel stats, top shows
```

---

## 🎯 Use Cases

### Local TV Station
- Schedule 24/7 programming
- Manage multiple channels
- Export for broadcast systems

### IPTV Service
- Create channel lineups
- Schedule VOD content
- Simulate viewer experience

### Content Creator
- Plan streaming schedule
- Organize show rotations
- Preview programming

### Hotel/Hospital TV
- Manage in-house channels
- Schedule announcements
- Control content timing

---

## 🚦 Status Indicators

### Bottom Status Bar
- **Ready**: System idle
- **Loading**: Database operation
- **Saved**: Changes persisted
- **Error**: Operation failed

### Schedule Info
- Current schedule name
- Date range
- Total channels
- Utilization percentage

---

## 📤 Export/Import

### Export Format
```json
{
  "name": "Schedule Name",
  "start_date": "2025-01-01",
  "end_date": "2025-01-31",
  "channels": [...],
  "shows": [...],
  "time_slots": [...]
}
```

### Import Process
1. Click **📂 Load**
2. Select JSON file
3. Schedule imported with "(Imported)" suffix
4. All relationships preserved

---

## ⚡ Performance

### Optimization Tips
- **Batch Operations**: Fill entire week at once
- **Conflict Resolution**: Run after bulk changes
- **Database Maintenance**: Compact monthly
- **Memory Usage**: Close unused schedules

### Capacity
- **Channels**: Unlimited
- **Shows per Channel**: Unlimited
- **Time Slots**: 48 per day (30-min intervals)
- **Schedule Duration**: Unlimited days

---

## 🛠️ Maintenance

### Database Backup
```bash
# Backup database
cp tv_schedules.db tv_schedules_backup_$(date +%Y%m%d).db
```

### Clear Old Data
```python
# Remove schedules older than 6 months
old_schedules = db.get_schedules()
for schedule in old_schedules:
    if schedule['end_date'] < six_months_ago:
        db.delete_schedule(schedule['schedule_id'])
```

---

## 📞 Support

### Common Solutions
1. **Restart application** for UI glitches
2. **Check permissions** for database errors
3. **Verify dates** for scheduling issues
4. **Update software** for compatibility

### File Locations
- **Database**: `tv_schedules.db`
- **Exports**: User-selected location
- **Logs**: Check M3U MATRIX PRO logs

---

## 🎉 Summary

The TV Schedule Center provides professional-grade television scheduling with:
- ✅ Visual calendar interface
- ✅ SQLite database persistence
- ✅ Intelligent scheduling algorithms
- ✅ Conflict detection & resolution
- ✅ Channel switching simulation
- ✅ Import/export functionality
- ✅ M3U MATRIX PRO integration

Perfect for IPTV providers, content creators, and broadcast professionals!

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Compatible With**: M3U MATRIX PRO 2.0+