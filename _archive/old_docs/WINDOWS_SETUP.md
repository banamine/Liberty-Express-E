# Windows Setup Guide for M3U Matrix Pro

## Quick Start

### 1. Install Python
- Download Python 3.11+ from https://www.python.org/downloads/
- **IMPORTANT:** Check "Add Python to PATH" during installation

### 2. Install Dependencies
Open Command Prompt in your project folder and run:
```cmd
pip install -r requirements.txt
```

### 3. Run the Application
Double-click `run_windows.bat` or run in Command Prompt:
```cmd
python src\M3U_MATRIX_PRO.py
```

---

## Troubleshooting

### Error: "No module named 'tkinterdnd2'"
```cmd
pip install tkinterdnd2
```

### Error: "No module named 'utils'" or "No module named 'page_generator'"
Make sure you're running from the project root folder, NOT from inside the `src\` folder.

**Correct:**
```
C:\Users\banamine\Videos\M3U MATRIX ALL IN ONE> python src\M3U_MATRIX_PRO.py
```

**Wrong:**
```
C:\Users\banamine\Videos\M3U MATRIX ALL IN ONE\src> python M3U_MATRIX_PRO.py
```

### Error: "tkinterdnd2" crashes on Windows
Some Windows systems need the 32-bit version:
```cmd
pip uninstall tkinterdnd2
pip install tkinterdnd2==0.3.0
```

---

## File Structure Required

```
M3U MATRIX ALL IN ONE/
├── src/
│   ├── M3U_MATRIX_PRO.py    ← Main app
│   ├── utils.py              ← Required utilities
│   ├── page_generator.py     ← Required for page generation
│   ├── config.json           ← Auto-created settings
│   └── logs/                 ← Auto-created logs folder
├── requirements.txt          ← Python dependencies
└── run_windows.bat           ← Windows launcher
```

---

## GitHub Sync Workflow

1. **Replit → GitHub:** Push changes from Replit
2. **GitHub → Windows:** Pull to your local folder
3. **Windows → GitHub:** Commit and push your changes
4. **GitHub → Replit:** Pull updates back to Replit

Make sure all three copies (Replit, GitHub, Windows) have the same folder structure.
