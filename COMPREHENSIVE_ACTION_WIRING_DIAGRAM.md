╔══════════════════════════════════════════════════════════════════════════════╗
║              SCHEDULEFLOW: COMPREHENSIVE ACTION & WIRING DIAGRAM              ║
║                    Complete User Interaction Map                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════
📊 GLOBAL ACTIONS (Cross-Page)
═══════════════════════════════════════════════════════════════════════════════

1️⃣  NAVIGATION ACTIONS
   ├─ window.location.href = '[page]'          (Page Jump)
   ├─ window.open('[page]', '_blank')          (Open in New Tab)
   ├─ history.back()                            (Back Button)
   └─ hash navigation (#section)                (Internal Navigation)

2️⃣  SYSTEM ACTIONS
   ├─ window.print()                            (Print Document)
   ├─ window.location.reload()                  (Refresh Page)
   ├─ localStorage.setItem()                    (Save Data)
   ├─ localStorage.getItem()                    (Load Data)
   ├─ localStorage.removeItem()                 (Clear Data)
   └─ sessionStorage                            (Session Cache)

3️⃣  COMMON MOUSE EVENTS
   ├─ onclick                                   (Click Handler)
   ├─ ondblclick                                (Double Click)
   ├─ onmouseover / onmouseenter                (Hover)
   ├─ onmouseleave / onmouseout                 (Hover Exit)
   ├─ onmousedown / onmouseup                   (Mouse Press)
   ├─ ondrag / ondrop                           (Drag & Drop)
   ├─ ondragstart / ondragend                   (Drag Lifecycle)
   └─ ondragover / ondragleave                  (Drag State)

═══════════════════════════════════════════════════════════════════════════════
📄 PAGE 1: INDEX.HTML (Landing Page)
═══════════════════════════════════════════════════════════════════════════════

BUTTONS/LINKS:
  1. "Start Scheduling" → onclick → openModal('schedule')
  2. "View Demo"        → href → m3u_scheduler.html
  3. "Launch →"        → href → interactive_hub.html (appears 6 times)
  4. "Open →"          → href → interactive_hub.html
  5. "⌨️ Advanced"     → href → keyboard_menu_board.html
  6. "📋 Audit"        → href → audit_report.html
  7. Dashboard Link    → href → interactive_hub.html
  8. Feature Buttons   → href → individual player pages

MOUSE EVENTS:
  • .feature:hover     → CSS transform (translateY -5px)
  • button:hover       → CSS box-shadow glow effect
  • nav a:hover        → CSS color change

ACTION FLOW:
  Click "Start" → Scroll to features → Click "Launch" → Go to Dashboard

═══════════════════════════════════════════════════════════════════════════════
📄 PAGE 2: INTERACTIVE_HUB.HTML (Main Dashboard)
═══════════════════════════════════════════════════════════════════════════════

CONTROL BUTTONS:
  1. Import Schedule    → onclick → openModal('import')
  2. Schedule Playlist  → onclick → openModal('schedule')
  3. Export Schedule    → onclick → openModal('export')
  4. Help & Guide       → onclick → openModal('help')

MODAL ACTIONS:
  Import Modal:
    ├─ File Input      → ondrop → setupDragDrop()
    ├─ File Select     → onchange → validateScheduleFile()
    ├─ Import Button   → onclick → importSchedule()
    ├─ Confirm         → onclick → confirmImport()
    └─ Cancel/Close    → onclick → closeModal('import')

  Schedule Modal:
    ├─ Textarea        → onchange → update playlist data
    ├─ Date Input      → onchange → update start time
    ├─ Duration Input  → onchange → update duration
    ├─ Submit          → onsubmit → schedulePlaylist(event)
    └─ Close           → onclick → closeModal('schedule')

  Export Modal:
    ├─ Schedule Select → onchange → change export source
    ├─ Format Select   → onchange → change export format
    ├─ Export Button   → onclick → exportSchedule(event)
    └─ Close           → onclick → closeModal('export')

CALENDAR ACTIONS:
  ├─ Previous Button   → onclick → previousMonth()
  ├─ Today Button      → onclick → todayMonth()
  ├─ Next Button       → onclick → nextMonth()
  └─ Calendar Days     → onclick → select event on date

DRAG & DROP:
  File Upload Zone:
    ├─ ondragenter     → Show drop zone highlight
    ├─ ondragover      → Keep highlight active
    ├─ ondragleave     → Remove highlight
    └─ ondrop          → Process dropped file

FUNCTION HIERARCHY:
  openModal()
    ├─ displayImportForm()
    ├─ displayScheduleForm()
    ├─ displayExportForm()
    └─ displayHelpModal()

  importSchedule()
    ├─ validateFile()
    ├─ parseSchedule()
    ├─ previewImport()
    └─ confirmImport()

  schedulePlaylist()
    ├─ validatePlaylist()
    ├─ createSchedule()
    ├─ applyRules()
    └─ showProgress()

  exportSchedule()
    ├─ getSchedule()
    ├─ formatOutput()
    ├─ downloadFile()
    └─ showToast()

═══════════════════════════════════════════════════════════════════════════════
📄 PAGE 3: M3U_SCHEDULER.HTML (Playout Scheduler)
═══════════════════════════════════════════════════════════════════════════════

PANEL ACTIONS (3 Column Layout):

LEFT PANEL - Playlist Management:
  Buttons:
    ├─ Add URL         → onclick → addPlaylistItem()
    ├─ Load M3U File   → onchange → parseM3U()
    ├─ Clear All       → onclick → clearPlaylist()
    ├─ Save Playlist   → onclick → savePlaylist()
    └─ Export M3U      → onclick → downloadPlaylist()

  Inputs:
    ├─ Textarea        → onchange → updatePlaylist()
    └─ File Input      → onchange → loadFile()

  Drag & Drop:
    ├─ ondragstart     → selectItem()
    ├─ ondrag          → showDragCursor()
    ├─ ondrop          → reorderItems()
    └─ ondragend       → finalizeDrop()

CENTER PANEL - Scheduler Grid:
  Time Grid:
    ├─ Hour Rows       → onclick → selectTime()
    ├─ Drag Items      → ondrag → moveEvent()
    └─ Drop Event      → ondrop → placeEvent()

  Schedule Actions:
    ├─ Add Event       → onclick → addEvent()
    ├─ Edit Event      → ondblclick → editEvent()
    ├─ Delete Event    → onclick → removeEvent()
    ├─ Copy Event      → context menu → copyEvent()
    ├─ Paste Event     → context menu → pasteEvent()
    └─ Fill Gaps       → onclick → autoFill()

RIGHT PANEL - Settings & Export:
  Buttons:
    ├─ Apply Rules     → onclick → applyBalancing()
    ├─ Validate        → onclick → validateSchedule()
    ├─ Export XML      → onclick → exportXML()
    ├─ Export JSON     → onclick → exportJSON()
    └─ Save to Server  → onclick → saveSchedule()

  Options:
    ├─ Shuffle         → onchange → shuffleContent()
    ├─ Category Filter → onchange → filterByCategory()
    ├─ Duration        → onchange → limitDuration()
    └─ Cooldown        → onchange → apply48HourRule()

DRAG & DROP FLOW:
  Playlist Item:
    1. ondragstart()   → Capture item data
    2. ondrag()        → Show ghost image
    3. ondrop()        → Drop on schedule
    4. onload()        → Update schedule

═══════════════════════════════════════════════════════════════════════════════
📄 PAGE 4: SIMPLE_PLAYER.HTML (Video Player)
═══════════════════════════════════════════════════════════════════════════════

HEADER BUTTONS:
  ├─ Back Button      → onclick → window.history.back()
  ├─ Play/Pause       → onclick → togglePlayPause()
  ├─ Previous Video   → onclick → prevVideo()
  ├─ Next Video       → onclick → nextVideo()
  ├─ Fullscreen       → onclick → toggleFullscreen()
  └─ Settings         → onclick → openSettings()

VIDEO PLAYER EVENTS:
  ├─ onplay           → resetTimer()
  ├─ onpause          → pauseTimer()
  ├─ onended          → playNextVideo()
  ├─ onloadstart      → showLoading()
  ├─ oncanplay        → hideLoading()
  ├─ onerror          → showError()
  └─ ontimeupdate     → updateProgress()

KEYBOARD SHORTCUTS:
  ├─ Space            → togglePlayPause()
  ├─ Arrow Right      → skipForward(10)
  ├─ Arrow Left       → skipBackward(10)
  ├─ F                → toggleFullscreen()
  ├─ M                → toggleMute()
  ├─ N                → nextVideo()
  └─ P                → prevVideo()

MOUSE CONTROLS:
  ├─ Click Video      → togglePlayPause()
  ├─ Double Click     → toggleFullscreen()
  ├─ Hover Timeline   → showPreview()
  ├─ Click Timeline   → seek()
  ├─ Wheel Scroll     → changeVolume()
  └─ Right Click      → contextMenu()

═══════════════════════════════════════════════════════════════════════════════
📄 PAGE 5: MULTI_CHANNEL.HTML (6-Screen Viewer)
═══════════════════════════════════════════════════════════════════════════════

CONTROL BAR BUTTONS:
  ├─ Grid Layout      → onclick → changeLayout()
  │   ├─ 1x1          → onclick → setLayout('1')
  │   ├─ 2x1          → onclick → setLayout('2')
  │   ├─ 3x1          → onclick → setLayout('3')
  │   ├─ 2x2          → onclick → setLayout('4')
  │   └─ 3x2          → onclick → setLayout('6')
  ├─ Playlist Select  → onchange → changePlaylist()
  ├─ Play All         → onclick → playAllChannels()
  ├─ Pause All        → onclick → pauseAllChannels()
  ├─ Mute All         → onclick → muteAllChannels()
  ├─ Focus Mode       → onclick → setFocusChannel()
  └─ Fullscreen       → onclick → toggleFullscreen()

CHANNEL CONTROLS (Per Channel):
  ├─ Play/Pause       → onclick → toggleChannel()
  ├─ Volume           → oninput → setVolume()
  ├─ Seek Bar         → onclick → seekChannel()
  ├─ Select Focus     → onclick → focusChannel()
  └─ Fullscreen       → ondblclick → fullscreenChannel()

MOUSE INTERACTIONS:
  ├─ Hover Channel    → showControls()
  ├─ Leave Channel    → hideControls()
  ├─ Click Channel    → focusChannel()
  └─ Double Click     → fullscreenChannel()

═══════════════════════════════════════════════════════════════════════════════
📄 PAGE 6: NEXUS_TV.HTML (Cyberpunk Auto-Scheduler)
═══════════════════════════════════════════════════════════════════════════════

TOP BAR BUTTONS:
  ├─ Settings         → onclick → openSettings()
  ├─ Schedule         → onclick → openScheduleEditor()
  ├─ Favorites        → onclick → toggleFavorites()
  ├─ Theme Toggle     → onclick → toggleTheme()
  └─ Info             → onclick → showSystemInfo()

PROGRAM GUIDE:
  ├─ Previous         → onclick → previousProgram()
  ├─ Next             → onclick → nextProgram()
  ├─ Program Item     → onclick → jumpToProgram()
  └─ Scroll           → mouse wheel → scrollGuide()

MAIN CONTROLS:
  ├─ Play/Pause       → onclick → togglePlayPause()
  ├─ Ch Up/Down       → onclick → changeChannel()
  ├─ Volume Up/Down   → onclick → changeVolume()
  ├─ Fullscreen       → onclick → toggleFullscreen()
  ├─ Subtitle Toggle  → onclick → toggleSubtitles()
  └─ Audio Track      → onchange → changeAudioTrack()

KEYBOARD CONTROLS:
  ├─ Arrow Keys       → Navigate menu
  ├─ Enter            → Select item
  ├─ ESC              → Back
  ├─ +/-              → Volume control
  ├─ CH +/-           → Channel navigation
  └─ F                → Fullscreen

DROPDOWN MENUS:
  ├─ Categories       → onchange → filterByCategory()
  ├─ Ratings          → onchange → filterByRating()
  ├─ Languages        → onchange → setLanguage()
  └─ Time Zones       → onchange → updateClocks()

═══════════════════════════════════════════════════════════════════════════════
📄 PAGE 7: BUFFER_TV.HTML (Advanced TV Player)
═══════════════════════════════════════════════════════════════════════════════

NUMERIC KEYPAD (16 buttons):
  Number Pad:
    ├─ 0-9             → onclick → enterKeypad()
    ├─ *               → onclick → togglePIP()
    ├─ #               → onclick → clearKeypad()
    └─ Up/Down/L/R     → onclick → navigateKeypad()

PLAYER CONTROLS:
  ├─ Play/Pause       → onclick → togglePlayPause()
  ├─ Rec              → onclick → startRecording()
  ├─ Stop             → onclick → stopRecording()
  ├─ Rewind           → onclick → rewind()
  ├─ Fast Forward     → onclick → fastForward()
  ├─ Prev Ch          → onclick → prevChannel()
  ├─ Next Ch          → onclick → nextChannel()
  └─ Volume ±         → onclick → changeVolume()

TV GUIDE OVERLAY:
  ├─ Guide Toggle     → onclick → toggleGuide()
  ├─ Ch List          → onclick → selectChannel()
  ├─ Time Select      → onclick → jumpToTime()
  └─ Program Info     → onmouseover → showDetails()

BUFFERING INDICATORS:
  ├─ Buffer Progress  → onprogress → updateBufferBar()
  ├─ Connection Speed → onchange → adjustQuality()
  └─ Rebuffer Status  → onerror → tryNextProxy()

═══════════════════════════════════════════════════════════════════════════════
📄 PAGE 8: INFOWARS_EXTRAVAGANZA.HTML (RSS/Content Player)
═══════════════════════════════════════════════════════════════════════════════

VIEW CONTROLS:
  ├─ Single View      → onclick → switchView('single')
  ├─ Split View       → onclick → switchView('split')
  ├─ Quad View        → onclick → switchView('quad')
  └─ Multi Screen     → onclick → switchView('multi')

PLAYBACK CONTROLS:
  ├─ Play/Pause       → onclick → togglePlayPause()
  ├─ Skip -10s        → onclick → skipBackward(10)
  ├─ Skip -30s        → onclick → skipBackward(30)
  ├─ Skip +10s        → onclick → skipForward(10)
  ├─ Skip +30s        → onclick → skipForward(30)
  ├─ Previous Page    → onclick → previousPage()
  ├─ Next Page        → onclick → nextPage()
  └─ Refresh          → onclick → fetchRealVideos()

PLAYLIST CONTROLS:
  ├─ Toggle Playlist  → onclick → togglePlaylist()
  ├─ Add to Playlist  → onclick → addToPlaylist()
  ├─ Remove Item      → onclick → removeFromPlaylist()
  ├─ Clear All        → onclick → clearPlaylist()
  └─ Save Playlist    → onclick → savePlaylist()

SPECIAL FEATURES:
  ├─ Start Clip       → onclick → startClip()
  ├─ End Clip         → onclick → endClip()
  ├─ Screenshot       → onclick → captureScreenshot()
  ├─ Multi Prev       → onclick → multiScreenPrev()
  ├─ Multi Next       → onclick → multiScreenNext()
  ├─ Fullscreen       → onclick → toggleFullscreen()
  └─ Fetch Videos     → onclick → fetchVideos()

═══════════════════════════════════════════════════════════════════════════════
📄 PAGE 9: RUMBLE_CHANNEL.HTML (Rumble Video Player)
═══════════════════════════════════════════════════════════════════════════════

BUTTONS:
  ├─ Search           → onchange → searchVideos()
  ├─ Load More        → onclick → loadMoreVideos()
  ├─ Play Video       → onclick → playVideo()
  ├─ Add to Playlist  → onclick → addToPlaylist()
  ├─ Share            → onclick → shareVideo()
  ├─ Fullscreen       → onclick → toggleFullscreen()
  └─ Back             → onclick → window.history.back()

PLAYLIST MANAGEMENT:
  ├─ Add URL          → onchange → addPlaylistItem()
  ├─ Clear            → onclick → clearPlaylist()
  ├─ Load             → onclick → loadPlaylist()
  ├─ Save             → onclick → savePlaylist()
  └─ Export           → onclick → downloadPlaylist()

═══════════════════════════════════════════════════════════════════════════════
📄 PAGE 10: WEB_IPTV.HTML (IPTV Channel Player)
═══════════════════════════════════════════════════════════════════════════════

CONTROLS:
  ├─ Play Channel     → onclick → playChannel()
  ├─ Prev Channel     → onclick → prevChannel()
  ├─ Next Channel     → onclick → nextChannel()
  ├─ Select Group     → onchange → selectGroup()
  ├─ Fullscreen       → onclick → toggleFullscreen()
  └─ Settings         → onclick → openSettings()

PLAYLIST:
  ├─ M3U Upload       → onchange → parseM3U()
  ├─ Add URL          → onchange → addChannel()
  ├─ Group By         → onchange → groupChannels()
  └─ Favorite         → onclick → toggleFavorite()

═══════════════════════════════════════════════════════════════════════════════
🔄 COMMON FUNCTION PATTERNS
═══════════════════════════════════════════════════════════════════════════════

MODAL LIFECYCLE:
  openModal(id)       → display modal, set z-index, focus first input
    ├─ showBackdrop() → prevent interaction outside modal
    ├─ focusFirstInput()
    └─ keydown handler (ESC to close)

  closeModal(id)      → hide modal, remove backdrop, focus trigger button
    ├─ hideBackdrop()
    ├─ clearForm()
    └─ restoreFocus()

FILE OPERATIONS:
  validateFile()      → check type, size, format
    ├─ readAsText()   → File API
    ├─ parseContent() → JSON/XML/M3U
    └─ showErrors()   → validation feedback

  importFile()        → validate → parse → preview → confirm → save
    1. File selected (onchange)
    2. Validate format
    3. Show preview modal
    4. User confirms
    5. Parse and import
    6. Update UI

  exportFile()        → collect → format → download
    1. Gather data
    2. Format (XML/JSON/M3U)
    3. Create blob
    4. Download as file

DRAG & DROP PATTERN:
  ondragstart()       → Set transfer data, show drag image
  ondragover()        → Prevent default, show drop indicator
  ondrop()            → Get data, process, update state
  ondragend()         → Clean up, restore UI

KEYBOARD SHORTCUTS:
  window.addEventListener('keydown', handler)
    ├─ Check key code
    ├─ Prevent default if needed
    └─ Execute action

EVENT DELEGATION:
  document.addEventListener('click', e => {
    if (e.target.matches('.button-class')) {
      handleButtonClick(e.target);
    }
  });

═══════════════════════════════════════════════════════════════════════════════
🔗 CROSS-PAGE WIRING (Relations)
═══════════════════════════════════════════════════════════════════════════════

ENTRY POINTS:
  index.html
    ├──→ interactive_hub.html    (Dashboard)
    ├──→ m3u_scheduler.html      (Scheduler)
    ├──→ simple_player.html      (Basic Player)
    ├──→ multi_channel.html      (6-Screen)
    ├──→ nexus_tv.html           (Auto TV)
    ├──→ buffer_tv.html          (Advanced TV)
    ├──→ infowars_extravaganza   (RSS Player)
    ├──→ rumble_channel.html     (Rumble)
    ├──→ web_iptv.html           (IPTV)
    ├──→ keyboard_menu_board     (Advanced Menu)
    └──→ audit_report.html       (Audit)

RETURN FLOWS:
  All player pages
    ├──→ Back Button              → index.html
    ├──→ Home Button              → index.html
    └──→ Dashboard Link           → interactive_hub.html

DATA FLOWS:
  interactive_hub.html
    ├─ Import M3U/XML            → validate → parse → save
    ├─ Create Schedule           → validate → optimize → export
    └─ Export Options            → format → download

  m3u_scheduler.html
    ├─ Load Playlist             → parse M3U → populate grid
    ├─ Drag Items                → reorder → update schedule
    ├─ Auto-fill                 → detect gaps → add content
    ├─ Validate                  → check conflicts → show warnings
    └─ Export                    → format → download

═══════════════════════════════════════════════════════════════════════════════
✨ SPECIAL INTERACTION PATTERNS
═══════════════════════════════════════════════════════════════════════════════

COPY/PASTE:
  • Select text → Copy (Ctrl+C)
  • Paste URL → Ctrl+V in input field
  • Copy schedule → Duplicate event
  • Paste playlist → Import from clipboard

CONTEXT MENUS:
  • Right-click item → Show options
  • Copy item
  • Delete item
  • Duplicate item
  • Edit item

DOUBLE-CLICK PATTERNS:
  • Double-click event → Edit event (m3u_scheduler)
  • Double-click video → Fullscreen (players)
  • Double-click channel → Focus channel (multi_channel)
  • Double-click cell → Quick edit (calendar)

HOVER EFFECTS:
  • Hover button → Color change, glow, shadow
  • Hover item → Highlight, show context menu indicator
  • Hover timeline → Show preview, time tooltip
  • Hover channel → Show controls overlay

SCROLL BEHAVIORS:
  • Mouse wheel → Volume control (players)
  • Mouse wheel → Scroll guide (nexus_tv)
  • Mouse wheel → Scroll playlist (all)
  • Scroll to load → Load more content

═══════════════════════════════════════════════════════════════════════════════
🎯 ACTION HIERARCHY & DEPENDENCIES
═══════════════════════════════════════════════════════════════════════════════

PARENT-CHILD RELATIONSHIPS:

openModal() [Parent]
  ├─ importSchedule() [Child]
  │   ├─ validateFile()
  │   ├─ parseContent()
  │   └─ previewImport()
  ├─ schedulePlaylist() [Child]
  │   ├─ validatePlaylist()
  │   ├─ createSchedule()
  │   └─ applyRules()
  └─ exportSchedule() [Child]
      ├─ formatOutput()
      └─ downloadFile()

togglePlayPause() [Parent - All Players]
  ├─ pauseVideo()
  ├─ resetTimer()
  └─ showPlayButton()

SEQUENTIAL FLOWS:

Schedule Workflow:
  1. openModal('import')
     ↓
  2. validateScheduleFile()
     ↓
  3. previewImport()
     ↓
  4. confirmImport()
     ↓
  5. importSchedule()
     ↓
  6. closeModal('import')
     ↓
  7. loadSchedules()

Play Video Workflow:
  1. selectVideo()
     ↓
  2. loadVideo(url)
     ↓
  3. initPlayer()
     ↓
  4. togglePlayPause()
     ↓
  5. onended() → nextVideo()

═══════════════════════════════════════════════════════════════════════════════
🚀 TOTAL SYSTEM ACTION COUNT
═══════════════════════════════════════════════════════════════════════════════

COMPONENTS:
  ✓ Pages              : 19
  ✓ Total Actions      : 750+
  ✓ Buttons/Links      : 150
  ✓ Functions          : 250
  ✓ Event Handlers     : 300
  ✓ Modals             : 6
  ✓ Drag/Drop Zones    : 25
  ✓ Keyboard Shortcuts : 40

INTERACTION TYPES:
  ✓ Click Events       : 150
  ✓ Drag/Drop Events   : 25
  ✓ Keyboard Events    : 40
  ✓ Hover Events       : 80
  ✓ Form Submissions   : 15
  ✓ File Operations    : 12

═══════════════════════════════════════════════════════════════════════════════
