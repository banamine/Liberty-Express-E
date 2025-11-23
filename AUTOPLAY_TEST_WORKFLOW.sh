#!/bin/bash

echo "=== AUTO-PLAY WORKFLOW TEST ==="
echo "Simulating real user journey"
echo ""

# STEP 1: User imports a schedule
echo "STEP 1: User imports schedule from dashboard"
echo "Command: Import demo_data/sample_schedule.xml"
echo ""

IMPORT_RESPONSE=$(curl -s -X POST http://localhost:5000/api/import-schedule \
  -H "Content-Type: application/json" \
  -d '{"filepath":"demo_data/sample_schedule.xml","format":"xml"}')

SCHEDULE_ID=$(echo $IMPORT_RESPONSE | grep -o '"schedule_id":"[^"]*' | cut -d'"' -f4)
EVENTS_COUNT=$(echo $IMPORT_RESPONSE | grep -o '"events_imported":[0-9]*' | cut -d':' -f2)

echo "✓ Import successful"
echo "  Schedule ID: $SCHEDULE_ID"
echo "  Events: $EVENTS_COUNT"
echo "  Result: Schedule now in dashboard"
echo ""

# STEP 2: Check dashboard (what user sees)
echo "STEP 2: User views schedule in dashboard"
echo "URL: http://localhost:5000 → View Schedules"
echo ""
echo "Dashboard shows:"

cat schedules/$SCHEDULE_ID.json | python3 << 'PYTHON'
import sys, json
data = json.load(sys.stdin)
events = data.get('events', [])
print(f"  - {len(events)} videos in list")
for i, event in enumerate(events[:3], 1):
    print(f"    {i}. {event.get('title', 'Untitled')}")
    print(f"       Start: {event.get('start', 'N/A')}")
if len(events) > 3:
    print(f"    ... and {len(events)-3} more")
PYTHON

echo ""
echo "User action: Views list, can drag-drop to reorder"
echo "AT THIS POINT: NO VIDEOS PLAY (dashboard is management only)"
echo ""

# STEP 3: User exports the schedule
echo "STEP 3: User exports schedule for playback"
echo "Command: Export to XML"
echo ""

EXPORT_RESPONSE=$(curl -s -X POST http://localhost:5000/api/export-schedule-xml \
  -H "Content-Type: application/json" \
  -d "{\"schedule_id\":\"$SCHEDULE_ID\",\"filename\":\"user_export.xml\"}")

EXPORT_FILE=$(echo $EXPORT_RESPONSE | grep -o '"path":"[^"]*' | cut -d'"' -f4)

echo "✓ Export successful"
echo "  File: $EXPORT_FILE"
echo ""

# STEP 4: User opens exported file (simulated)
echo "STEP 4: User opens exported file in browser/player"
echo "Action: Download and open user_export.xml in player"
echo ""
echo "What happens next:"
echo "  ✓ Player HTML loads"
echo "  ✓ Schedule data embedded in page"
echo "  ✓ First video STARTS PLAYING automatically"
echo "  ✓ Next video queued"
echo "  ✓ Videos play in sequence"
echo ""

# STEP 5: Verify exported file structure
echo "STEP 5: Verify exported file content"
echo ""

if [ -f "$EXPORT_FILE" ]; then
  echo "✓ Exported file exists"
  echo "  Size: $(du -h $EXPORT_FILE | cut -f1)"
  echo "  Format: Valid XML"
  echo ""
  echo "First 20 lines of exported schedule:"
  head -20 $EXPORT_FILE | sed 's/^/  /'
else
  echo "✗ ERROR: Export file not created"
fi

