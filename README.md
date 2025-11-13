# 🎬 M3U MATRIX ALL-IN-ONE

**Complete IPTV Management & Streaming Platform**

Transform M3U playlists into beautiful, auto-scheduled streaming TV channels with a neon cyberpunk interface!

![Status](https://img.shields.io/badge/status-fully%20operational-brightgreen)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## 🚀 Quick Start

### **Option 1: Clone from GitHub (Easiest)**

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/M3U-MATRIX-ALL-IN-ONE.git
cd M3U-MATRIX-ALL-IN-ONE

# Install dependencies (Python)
pip install -r requirements.txt

# Install dependencies (Node.js for web server)
npm install

# Launch the playlist manager
./run_m3u_matrix.sh
```

### **Option 2: Run on Replit**

1. Fork this Repl
2. Click the "Run" button
3. Open the webview to see your channels

---

## ✨ Features

### 🎯 **M3U Matrix Pro** (Python Desktop App)
- **Drag & Drop**: Drop M3U files directly into the app
- **Double-Click**: Open files from the list instantly
- **Live Validation**: Check if channel URLs work
- **Smart Organization**: Remove duplicates, sort by group
- **EPG Integration**: TV Guide with XMLTV support
- **Cut/Copy/Paste**: Manage channels like a pro
- **CSV Export**: Analyze playlists in spreadsheets
- **Page Generator**: Create NEXUS TV channels automatically

### 📺 **NEXUS TV** (Web Streaming Player)
- **24-Hour Scheduling**: Auto-play content all day
- **Cyberpunk UI**: Neon glowing interface
- **Channel Selector**: Browse all channels beautifully
- **Fullscreen Player**: Immersive viewing experience
- **Midnight Refresh**: New schedule every day

### 🎨 **Page Generator**
- Injects M3U playlists into NEXUS TV template
- Creates 100+ channel pages
- Group-based or all-in-one generation
- Professional quality matching the template

---

## 📁 Project Structure

```
M3U_MATRIX_ALL_IN_ONE/
├── src/
│   ├── M3U_MATRIX_PRO.py          # Main Python app
│   └── page_generator.py           # Channel generator
├── templates/
│   └── nexus_tv_template.html      # NEXUS TV base template
├── generated_pages/
│   ├── index.html                  # Channel selector
│   └── *.html                      # Individual channel pages
├── Sample Playlists/               # Example M3U files
├── run_m3u_matrix.sh               # Launcher script
├── package.json                    # Node.js dependencies
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 🎮 How to Use

### **Step 1: Load Playlists**

**Method A: Drag & Drop (NEW!)**
- Drag M3U files directly into the "Loaded Files" panel
- Files load automatically

**Method B: Click to Open**
- Click the **LOAD** button
- Select one or more M3U files
- Files appear in the list

**Method C: Double-Click**
- Double-click any file in the list to open it

### **Step 2: Organize (Optional)**
- Click **ORGANIZE** to clean and sort channels
- Click **CHECK** to validate URLs
- Drag rows to reorder channels
- Double-click cells to edit

### **Step 3: Generate NEXUS TV Pages**
- Click **GENERATE PAGES**
- Choose:
  - **"Yes"** = One channel per category (Movies, Sports, etc.)
  - **"No"** = One mega-channel with all programs

### **Step 4: Watch Your Channels**
- Open the webview or visit `http://localhost:5000`
- Browse the channel selector
- Click any channel card to start watching
- Enjoy 24-hour auto-scheduled playback!

---

## 🔄 GitHub Setup & Updates

### **Initial Setup (First Time)**

1. **Create GitHub Repository**
   - Go to [github.com/new](https://github.com/new)
   - Name it: `M3U-MATRIX-ALL-IN-ONE`
   - Keep it Public or Private
   - Don't initialize with README (we have one)

2. **Connect Replit to GitHub**
   ```bash
   # In Replit Shell
   git config --global user.name "Your Name"
   git config --global user.email "your@email.com"
   
   # Add your GitHub repo
   git remote add origin https://github.com/YOUR-USERNAME/M3U-MATRIX-ALL-IN-ONE.git
   
   # Push to GitHub
   git push -u origin main
   ```

3. **Use GitHub Desktop (Easier!)**
   - Download [GitHub Desktop](https://desktop.github.com/)
   - Click "File" → "Clone Repository"
   - Paste your repo URL
   - It syncs automatically!

### **Update Workflow (Regular Updates)**

**In Replit:**
```bash
# Save your changes
git add .
git commit -m "Updated playlists and generated new channels"
git push origin main
```

**In GitHub Desktop:**
1. Open GitHub Desktop
2. See your changes listed
3. Write a summary (e.g., "Added 10 new channels")
4. Click "Commit to main"
5. Click "Push origin"

**Pull Updates (From GitHub to Replit):**
```bash
git pull origin main
```

### **Automatic Sync (Advanced)**

Create `.github/workflows/sync.yml`:

```yaml
name: Auto Sync
on:
  push:
    branches: [main]
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Sync to Replit
        run: echo "Files synced!"
```

---

## 📦 Dependencies

### Python Packages
```
requests
pillow
tkinterdnd2
```

### Node.js Packages
```
serve
```

### Installation
```bash
# Python
pip install -r requirements.txt

# Node.js
npm install
```

---

## 🎨 Generated Page Examples

Each generated page includes:
- **24-hour schedule grid** with movie titles & times
- **Auto-scheduled playback** (content changes throughout the day)
- **Neon cyberpunk interface** with glowing effects
- **Fullscreen player** with volume controls
- **Midnight auto-refresh** for new schedule

**Example Channels:**
- Aliein 3 (53 programs)
- Ancient Aliens 1-18 (208 programs)
- Flux8 (670 programs)

---

## 🛠️ Troubleshooting

### **Python App Won't Start**
```bash
# Check Python version
python3 --version  # Should be 3.10+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check logs
cat src/logs/m3u_matrix.log
```

### **Web Server Issues**
```bash
# Restart web server
npm run dev

# Check if port 5000 is in use
lsof -i :5000

# Clear browser cache
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)
```

### **Drag & Drop Not Working**
- Ensure `tkinterdnd2` is installed
- Only drop `.m3u` or `.m3u8` files
- Try clicking **LOAD** instead

### **Generated Pages Not Showing**
- Check `generated_pages/` folder exists
- Ensure web server is running
- Clear browser cache and refresh

---

## 🎯 Features Roadmap

### ✅ Completed
- [x] Full M3U parser with validation
- [x] Drag & drop file support
- [x] Double-click to open files
- [x] Page generator integration
- [x] Channel selector interface
- [x] 24-hour auto-scheduling
- [x] Cyberpunk UI design

### 🚧 In Progress
- [ ] GitHub Actions auto-sync
- [ ] Multi-language support
- [ ] Theme customization

### 📝 Planned
- [ ] Cloud playlist sync
- [ ] Recording/timeshift
- [ ] User authentication
- [ ] Mobile app
- [ ] API endpoints

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## 🤝 Contributing

Contributions welcome!

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 💡 Tips & Tricks

### **Workflow Shortcuts**
1. **Quick Load**: Drag multiple M3U files at once
2. **Quick Edit**: Double-click any cell in the matrix
3. **Quick Save**: Right-click file → Copy path
4. **Quick Generate**: Load → Organize → Generate Pages

### **M3U Best Practices**
- Validate URLs before generating pages
- Organize by groups (Movies, TV, Sports)
- Use descriptive channel names
- Include logos for better visuals

### **GitHub Tips**
- Commit often (every major change)
- Use descriptive commit messages
- Create branches for experiments
- Use `.gitignore` to exclude logs/temp files

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/YOUR-USERNAME/M3U-MATRIX-ALL-IN-ONE/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR-USERNAME/M3U-MATRIX-ALL-IN-ONE/discussions)
- **Email**: your@email.com

---

## 🌟 Show Your Support

Give a ⭐️ if this project helped you!

---

**M3U MATRIX ALL-IN-ONE** - Professional IPTV Management & Streaming Platform

Made with ❤️ by [Your Name]
