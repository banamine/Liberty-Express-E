# 🔄 3-WAY SYNC WORKFLOW

**Sync Circle:** Replit ↔ GitHub ↔ Local Windows

---

## 🎯 Overview

This guide sets up automatic syncing between:
1. **Replit** - Where you develop and generate pages
2. **GitHub** - Central backup (cloud)
3. **Local Windows** - `C:\Users\banamine\Videos\M3U MATRIX ALL IN ONE`

**GitHub is the Hub** - Everything syncs through GitHub as the single source of truth.

---

## 📊 Sync Flow Diagram

```
┌─────────────┐
│   REPLIT    │ ──push──→ ┌─────────────┐ ←──pull── ┌──────────────┐
│  (Develop)  │ ←─pull─── │   GITHUB    │ ──push──→ │ LOCAL WINDOWS│
└─────────────┘           │    (Hub)    │           │  (Backup)    │
                          └─────────────┘           └──────────────┘
                                 │
                          ┌──────┴──────┐
                          │   Backups   │
                          │  Archives   │
                          └─────────────┘
```

---

## 🚀 SETUP GUIDE

### **Step 1: Set Up GitHub (Central Hub)**

1. **Create Repository**
   - Go to: https://github.com/new
   - Name: `M3U-MATRIX-ALL-IN-ONE`
   - Public or Private (your choice)
   - **Don't** initialize with README
   - Click "Create repository"

2. **Copy Your Repo URL**
   ```
   https://github.com/YOUR-USERNAME/M3U-MATRIX-ALL-IN-ONE.git
   ```

---

### **Step 2: Connect Replit to GitHub**

**Option A: Replit Version Control (Easiest)**
1. In Replit, click three dots (...)
2. Select "Version control"
3. Click "Connect to GitHub"
4. Authorize Replit
5. Select your repository
6. ✅ Done! Auto-syncs enabled

**Option B: Git Commands (Manual)**
```bash
# In Replit Shell:
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
git remote add origin https://github.com/YOUR-USERNAME/M3U-MATRIX-ALL-IN-ONE.git
git push -u origin main
```

---

### **Step 3: Set Up Local Windows Sync**

#### **Install GitHub Desktop (Recommended)**

1. **Download GitHub Desktop**
   - Visit: https://desktop.github.com/
   - Install on Windows

2. **Clone Repository**
   - Open GitHub Desktop
   - File → Clone Repository
   - Find your repo
   - **Local Path:** `C:\Users\banamine\Videos\M3U MATRIX ALL IN ONE`
   - Click "Clone"

3. **Enable Auto-Fetch**
   - GitHub Desktop → File → Options
   - Git → Enable "Periodically fetch"
   - Set to every 15 minutes
   - ✅ Auto-sync enabled!

---

## 🔄 DAILY WORKFLOW

### **Working on Replit:**

```bash
# 1. BEFORE starting work - PULL latest
git pull origin main

# 2. Work on your project (generate pages, edit files, etc.)

# 3. AFTER work - COMMIT and PUSH
git add .
git commit -m "Generated 5 new channels"
git push origin main
```

### **Working on Local Windows:**

1. **Before work:**
   - Open GitHub Desktop
   - Click "Fetch origin"
   - Click "Pull origin" if updates available

2. **After work:**
   - GitHub Desktop shows your changes
   - Write commit message
   - Click "Commit to main"
   - Click "Push origin"

---

## 💾 AUTOMATED BACKUPS

### **Replit Auto-Backup (Nightly)**

Create this file: `backup_script.sh`

```bash
#!/bin/bash
# Automatic nightly backup

DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"

# Create timestamped archive
tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" \
  src/ \
  templates/ \
  generated_pages/ \
  *.m3u \
  *.m3u8 \
  *.md \
  requirements.txt \
  package.json

echo "Backup created: backup_$DATE.tar.gz"

# Keep only last 7 days
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete

# Optional: Push to GitHub backup branch
git checkout -b backup-$DATE
git add "$BACKUP_DIR/backup_$DATE.tar.gz"
git commit -m "Automated backup $DATE"
git push origin backup-$DATE
git checkout main
```

**Make it executable:**
```bash
chmod +x backup_script.sh
```

**Run nightly:**
Add to Replit's cron or run manually before bed.

---

### **Windows Auto-Backup (PowerShell)**

Create: `C:\Users\banamine\Videos\backup_script.ps1`

```powershell
# Windows PowerShell Backup Script

$date = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$source = "C:\Users\banamine\Videos\M3U MATRIX ALL IN ONE"
$backupRoot = "C:\Users\banamine\Videos\M3U_BACKUPS"
$backupDest = "$backupRoot\backup_$date"

# Create backup directory
New-Item -ItemType Directory -Force -Path $backupDest

# Copy files (excluding node_modules, logs, etc.)
robocopy $source $backupDest /E /XD node_modules .git .cache logs temp /XF *.log

# Create ZIP archive
Compress-Archive -Path $backupDest -DestinationPath "$backupRoot\backup_$date.zip"

# Remove uncompressed backup
Remove-Item -Recurse -Force $backupDest

# Keep only last 10 backups
Get-ChildItem "$backupRoot\backup_*.zip" | 
  Sort-Object CreationTime -Descending | 
  Select-Object -Skip 10 | 
  Remove-Item -Force

Write-Host "Backup complete: backup_$date.zip"
```

**Schedule with Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Name: "M3U Matrix Backup"
4. Trigger: Daily at 11:00 PM
5. Action: Start a program
   - Program: `powershell.exe`
   - Arguments: `-ExecutionPolicy Bypass -File "C:\Users\banamine\Videos\backup_script.ps1"`
6. ✅ Done! Auto-backups every night

---

## ⚠️ CONFLICT RESOLUTION

**What if you edit in two places?**

### **In GitHub Desktop:**
1. GitHub Desktop will show conflicts
2. Click "View Conflicts"
3. Choose which version to keep
4. Mark as resolved
5. Commit and push

### **In Replit:**
```bash
git pull origin main
# If conflicts occur:
git status  # Shows conflicted files
# Edit files to resolve conflicts
git add .
git commit -m "Resolved conflicts"
git push origin main
```

### **Best Practice:**
- **ALWAYS pull before starting work**
- Work in only ONE location at a time
- Push immediately after finishing
- Pull on other locations before working there

---

## 📋 QUICK REFERENCE

### **Replit Quick Commands**
```bash
git pull           # Get latest changes
git add .          # Stage all changes
git commit -m "..."# Save changes
git push           # Upload to GitHub
git status         # Check status
```

### **GitHub Desktop**
- **Fetch** - Check for updates
- **Pull** - Download updates
- **Commit** - Save changes locally
- **Push** - Upload to GitHub

### **Emergency Recovery**
```bash
# If something breaks, restore from GitHub:
git fetch origin
git reset --hard origin/main
```

---

## ✅ VERIFICATION CHECKLIST

Test your 3-way sync:

1. **Replit → GitHub:**
   - [ ] Create a file in Replit
   - [ ] Push to GitHub
   - [ ] See it on GitHub.com

2. **GitHub → Windows:**
   - [ ] Open GitHub Desktop
   - [ ] Fetch and pull
   - [ ] See the file in Windows folder

3. **Windows → GitHub → Replit:**
   - [ ] Edit file on Windows
   - [ ] Commit and push in GitHub Desktop
   - [ ] Pull in Replit
   - [ ] See changes in Replit

4. **Backups:**
   - [ ] Run backup script manually
   - [ ] Verify backup file created
   - [ ] Test restoring from backup

---

## 🎯 SYNC SCHEDULE RECOMMENDATION

**Daily Routine:**
1. **Morning:** Pull latest on both Replit and Windows
2. **Work:** Make changes in ONE location only
3. **Evening:** Push changes, then pull on other location
4. **Night:** Automated backups run (11 PM)

**Weekly:**
- Review backup archives
- Clean old backups (>30 days)
- Verify sync working correctly

---

## 🆘 TROUBLESHOOTING

### **"Already up to date" but files different**
```bash
# Force sync from GitHub:
git fetch origin
git reset --hard origin/main
```

### **Backup script not running**
- Verify file permissions: `chmod +x backup_script.sh`
- Check cron/Task Scheduler logs
- Run manually to test

### **GitHub Desktop not syncing**
- Click "Fetch origin" manually
- Check internet connection
- Re-authenticate GitHub account

---

## 📞 SUPPORT

- GitHub Docs: https://docs.github.com/
- Git Cheatsheet: https://education.github.com/git-cheat-sheet-education.pdf
- GitHub Desktop: https://docs.github.com/desktop

---

**Your 3-Way Sync is Ready! 🎉**

Work anywhere → Push to GitHub → Pull everywhere → Backups run automatically
