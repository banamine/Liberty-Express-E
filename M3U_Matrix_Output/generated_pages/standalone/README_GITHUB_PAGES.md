# Standalone Secure Player - GitHub Pages Deployment

## Quick Setup

1. **Create GitHub Repository**
   - Go to GitHub.com and create a new repository
   - Name it (e.g., `my-iptv-player`)
   - Make it PUBLIC (required for free GitHub Pages)

2. **Upload Generated Files**
   - Upload all files from `generated_pages/standalone/` folder
   - Make sure `index.html` is in the root (rename one of your players if needed)

3. **Enable GitHub Pages**
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: main (or master)
   - Folder: / (root)
   - Click Save

4. **Access Your Player**
   - Wait 2-5 minutes for deployment
   - Your site will be available at: `https://YOUR-USERNAME.github.io/REPO-NAME/`

## Features
- ✅ Completely self-contained (no server needed)
- ✅ URLs hidden from user view
- ✅ Smart loading (20% chunks for large playlists)
- ✅ Works offline once loaded
- ✅ Mobile responsive

## Multiple Players
You can host multiple players:
- `index.html` - Main player (accessible at root)
- `player2.html` - Additional player
- `player3.html` - Another player

Access them at:
- `https://YOUR-USERNAME.github.io/REPO-NAME/`
- `https://YOUR-USERNAME.github.io/REPO-NAME/player2.html`
- `https://YOUR-USERNAME.github.io/REPO-NAME/player3.html`

## Custom Domain (Optional)
1. Create file named `CNAME` with your domain
2. Configure DNS at your domain provider
3. Enable HTTPS in GitHub Pages settings

## Updates
Simply upload new HTML files to update your players. Changes go live in 1-2 minutes.
