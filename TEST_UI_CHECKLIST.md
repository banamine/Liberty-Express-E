# ScheduleFlow UI/UX Validation Checklist

**Date:** November 22, 2025  
**Version:** v2.1.0  
**Component:** Interactive Hub Dashboard  

---

## Manual Validation Tests

### Test Environment Setup
- [ ] Open `/generated_pages/interactive_hub.html` in a modern browser (Chrome, Firefox, Safari)
- [ ] Ensure API server is running on `http://localhost:5000`
- [ ] Clear browser cache/localStorage before testing

---

## Test Group 1: Import Modal

### TC 1.1: Import Modal Opens
**Steps:**
1. Click the "Import Schedule" button (📥 icon)
2. Verify modal window appears

**Expected:**
- [ ] Modal overlay appears with title "Import Schedule"
- [ ] Close button (×) visible in top-right
- [ ] File upload area visible

---

### TC 1.2: File Upload with Drag-Drop
**Steps:**
1. Open Import modal
2. Drag a valid XML/JSON schedule file over the upload area
3. Observe visual feedback
4. Drop the file

**Expected:**
- [ ] Upload area highlights on drag-over (changes background color)
- [ ] "Click to upload or drag file here" text visible
- [ ] File is processed after drop
- [ ] Validation message appears

---

### TC 1.3: Malformed File Rejection
**Steps:**
1. Create a text file with invalid JSON: `{"invalid": json content}`
2. Drag into upload area and drop
3. Observe validation message

**Expected:**
- [ ] Red error message appears: "❌ Invalid format" or similar
- [ ] Form does not submit
- [ ] Error is clear and actionable

---

### TC 1.4: Successful Import
**Steps:**
1. Create a valid XML file:
```xml
<?xml version="1.0"?>
<tvguide>
  <schedule id="test">
    <name>Test Schedule</name>
    <event id="evt1">
      <title>Show 1</title>
      <start>2025-11-22T10:00:00Z</start>
      <end>2025-11-22T11:00:00Z</end>
    </event>
  </schedule>
</tvguide>
```
2. Upload file
3. Click "Import Schedule" button

**Expected:**
- [ ] Green success message: "✅ File valid"
- [ ] Form fields appear (Schedule Name input)
- [ ] Submit button shows "Import Schedule"
- [ ] Toast notification appears: "✅ Imported X events successfully!"
- [ ] Modal closes automatically

---

## Test Group 2: Schedule Modal

### TC 2.1: Schedule Modal Opens
**Steps:**
1. Click "Schedule Playlist" button (📅 icon)

**Expected:**
- [ ] Modal appears with title "Schedule Playlist"
- [ ] Form fields visible: Playlist links, Start date/time, Duration, Cooldown, Shuffle checkbox

---

### TC 2.2: Playlist Input (Multiple URLs)
**Steps:**
1. Open Schedule modal
2. Paste 5 video URLs in textarea:
```
http://example.com/video1.mp4
http://example.com/video2.mp4
http://example.com/video3.mp4
http://example.com/video4.mp4
http://example.com/video5.mp4
```
3. Set Start date/time (e.g., Nov 22, 2025 10:00 AM)
4. Set Duration to 5 hours
5. Keep Cooldown at 48 hours
6. Click "Schedule Playlist"

**Expected:**
- [ ] All URLs accepted in textarea
- [ ] No character limit errors
- [ ] Date/time picker works (can select date and time)
- [ ] Processing spinner appears
- [ ] Success toast: "✅ Scheduled 5 events!"

---

### TC 2.3: Cooldown Configuration
**Steps:**
1. Open Schedule modal
2. Change Cooldown value to 24 hours
3. Submit form

**Expected:**
- [ ] Cooldown field accepts numeric input
- [ ] Form submits with custom cooldown value
- [ ] No "48 hour default enforced" errors

---

### TC 2.4: Shuffle Toggle
**Steps:**
1. Open Schedule modal
2. Uncheck "Shuffle playlist order" checkbox
3. Submit with sequential order

**Expected:**
- [ ] Checkbox is toggleable
- [ ] When checked (default): videos are randomized
- [ ] When unchecked: videos appear in order
- [ ] Form submits regardless of toggle state

---

## Test Group 3: Export Modal

### TC 3.1: Export Modal Opens
**Steps:**
1. Click "Export Schedule" button (📤 icon)

**Expected:**
- [ ] Modal appears with title "Export Schedule"
- [ ] Dropdown to select schedule (populated from imports)
- [ ] Format options: TVGuide XML, JSON
- [ ] Filename input field

---

### TC 3.2: Schedule Selection
**Steps:**
1. Import a schedule (using Import modal)
2. Open Export modal
3. Verify dropdown is populated

**Expected:**
- [ ] Schedule dropdown shows imported schedule names
- [ ] At least 1 option available
- [ ] Can select from dropdown

---

### TC 3.3: Format Selection & Export
**Steps:**
1. Select a schedule from dropdown
2. Select "TVGuide XML" format
3. Enter filename: `my_schedule.xml`
4. Click "Export Schedule"

**Expected:**
- [ ] File download starts
- [ ] Downloaded file is named `my_schedule.xml`
- [ ] File contains valid XML (can open in text editor)
- [ ] Toast notification: "✅ Exported to my_schedule.xml"

---

### TC 3.4: JSON Export Format
**Steps:**
1. Open Export modal
2. Select "JSON (Human Readable)" format
3. Enter filename: `my_schedule.json`
4. Click "Export Schedule"

**Expected:**
- [ ] File downloads as `my_schedule.json`
- [ ] File contains valid JSON (parseable in browser console)
- [ ] File is human-readable with indentation

---

## Test Group 4: Interactive Calendar

### TC 4.1: Calendar Displays Current Month
**Steps:**
1. Load dashboard
2. Observe calendar widget

**Expected:**
- [ ] Calendar shows current month and year
- [ ] Days of week visible (Sun-Sat)
- [ ] Days 1-31 (or less for current month) visible
- [ ] Today's date highlighted with border

---

### TC 4.2: Month Navigation
**Steps:**
1. Click "Next ▶" button to advance month
2. Verify calendar updates
3. Click "◀ Previous" to go back
4. Click "Today" to return to current month

**Expected:**
- [ ] Month title updates (e.g., "November 2025" → "December 2025")
- [ ] Calendar grid updates with new month's dates
- [ ] Navigation buttons work both forward and backward
- [ ] "Today" button returns to current month

---

### TC 4.3: Scheduled Events Display
**Steps:**
1. Schedule a playlist (using Schedule modal)
2. Navigate to month containing scheduled date
3. Observe calendar day cells

**Expected:**
- [ ] Scheduled videos appear in calendar day cells
- [ ] Event title visible (e.g., "video_001.mp4")
- [ ] Green indicator bar on left of event
- [ ] Multiple events per day if applicable

---

### TC 4.4: Cooldown Indicator (if applicable)
**Steps:**
1. Schedule same video twice within 48 hours
2. Observe calendar

**Expected:**
- [ ] First occurrence shows green (scheduled)
- [ ] Second occurrence shows orange/red (cooldown - if enforced and visible)
- [ ] Tooltip or indicator explains cooldown status

---

## Test Group 5: Status Dashboard

### TC 5.1: Stats Display
**Steps:**
1. Load dashboard
2. Observe status cards at top

**Expected:**
- [ ] "Schedules Imported" shows count (0 initially)
- [ ] "Total Events" shows count
- [ ] "Playlists Loaded" shows count
- [ ] "System Version" shows "v2.1.0"

---

### TC 5.2: Stats Update After Import
**Steps:**
1. Import a schedule with 5 events
2. Return to dashboard
3. Observe stats update

**Expected:**
- [ ] "Schedules Imported" increments to 1
- [ ] "Total Events" increments to 5
- [ ] Updates are immediate or within 1 second

---

### TC 5.3: Stats Update After Schedule
**Steps:**
1. Schedule a playlist with 10 videos
2. Observe stats

**Expected:**
- [ ] Total events count increases
- [ ] Stats reflect new schedule

---

## Test Group 6: Error Handling

### TC 6.1: Network Error (API Down)
**Steps:**
1. Stop the API server
2. Try to import a schedule
3. Observe error handling

**Expected:**
- [ ] Error toast appears (red notification)
- [ ] Error message is user-friendly
- [ ] No console errors visible (or caught gracefully)
- [ ] Application remains functional (can retry after server restarts)

---

### TC 6.2: Invalid Date/Time
**Steps:**
1. Open Schedule modal
2. Try to submit without selecting date/time
3. Observe validation

**Expected:**
- [ ] Error message appears: "Please select a start date and time"
- [ ] Form does not submit
- [ ] User is guided to fill required fields

---

### TC 6.3: Empty Playlist Links
**Steps:**
1. Open Schedule modal
2. Leave playlist textarea empty
3. Click "Schedule Playlist"

**Expected:**
- [ ] Error toast: "Please enter at least one video URL"
- [ ] Form does not submit
- [ ] No hang or crash

---

## Test Group 7: Responsive Design

### TC 7.1: Desktop View (1920x1080)
**Steps:**
1. Open dashboard on desktop
2. Verify layout

**Expected:**
- [ ] All buttons visible and clickable
- [ ] Calendar shows full month grid
- [ ] Modals fit on screen
- [ ] Text is readable (no truncation)

---

### TC 7.2: Tablet View (768x1024)
**Steps:**
1. Resize browser to tablet dimensions
2. Verify layout adjusts

**Expected:**
- [ ] Buttons stack vertically or adjust layout
- [ ] Calendar is readable (may show fewer columns)
- [ ] Modals are full-screen or near full-screen
- [ ] Touch-friendly button sizes (>48px)

---

### TC 7.3: Mobile View (375x667)
**Steps:**
1. Resize browser to phone dimensions
2. Verify layout adjusts

**Expected:**
- [ ] Buttons stack vertically
- [ ] Calendar is scrollable or compact
- [ ] Modals are full-screen
- [ ] Text is readable without zooming
- [ ] Touch targets are large enough

---

## Test Group 8: Toast Notifications

### TC 8.1: Success Toast
**Steps:**
1. Perform successful action (import, schedule, export)
2. Observe notification

**Expected:**
- [ ] Green toast appears in bottom-right corner
- [ ] Message text is clear (e.g., "✅ Imported 5 events successfully!")
- [ ] Toast auto-dismisses after 4 seconds
- [ ] Notification is non-blocking

---

### TC 8.2: Error Toast
**Steps:**
1. Attempt invalid action (malformed file, empty input)
2. Observe notification

**Expected:**
- [ ] Red toast appears
- [ ] Error message is actionable
- [ ] User knows what to fix

---

## Test Group 9: Help & Guide

### TC 9.1: Help Modal Opens
**Steps:**
1. Click "Help & Guide" button (❓ icon)

**Expected:**
- [ ] Modal appears with comprehensive guide
- [ ] Contains:
  - [ ] Quick start instructions
  - [ ] Feature descriptions
  - [ ] Audit questions with answers
  - [ ] Pro tips

---

## Regression Tests

### RT 1: Form Reset After Submit
**Steps:**
1. Complete an import/schedule operation
2. Re-open the same modal
3. Observe form state

**Expected:**
- [ ] Form fields are cleared
- [ ] Ready for next operation
- [ ] No residual data from previous session

---

### RT 2: Multiple Operations in Sequence
**Steps:**
1. Import a schedule
2. Then schedule a playlist
3. Then export the schedule

**Expected:**
- [ ] Each operation succeeds without interference
- [ ] Data persists between operations
- [ ] No memory leaks or crashes

---

### RT 3: Browser Back Button
**Steps:**
1. Perform operations
2. Click browser back button
3. Verify state

**Expected:**
- [ ] Application handles back button gracefully
- [ ] Or uses hash routing to prevent page reload
- [ ] No loss of data

---

## Accessibility Tests

### AT 1: Keyboard Navigation
**Steps:**
1. Close all modals
2. Use Tab key to navigate between buttons
3. Press Enter to activate buttons

**Expected:**
- [ ] All buttons receive focus (visible focus indicator)
- [ ] Buttons activate on Enter key
- [ ] Tab order is logical (left-to-right, top-to-bottom)

---

### AT 2: Screen Reader (if applicable)
**Steps:**
1. Use screen reader (e.g., NVDA, JAWS)
2. Navigate dashboard

**Expected:**
- [ ] Buttons have descriptive labels
- [ ] Form fields have associated labels
- [ ] Modal titles are announced

---

## Test Summary

### Passing Criteria
- [ ] All TC tests (Test Cases) pass
- [ ] All TC subtests marked with checkboxes complete
- [ ] No critical errors or crashes
- [ ] UX is intuitive and responsive

### Sign-Off
- **Tester Name:** ___________________
- **Date:** ___________________
- **Status:** ☐ PASS ☐ FAIL ☐ CONDITIONAL

**Notes:**
```
[Space for additional notes/observations]
```

---

## Known Issues / Future Enhancements

- [ ] Tooltip on cooldown status indicator
- [ ] Bulk import multiple files
- [ ] Schedule preview before import
- [ ] Undo/redo functionality
- [ ] Schedule templates
- [ ] Playlist categories/tags

---
