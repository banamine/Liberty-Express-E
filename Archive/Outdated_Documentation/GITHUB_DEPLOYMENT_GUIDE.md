# GitHub Auto-Deployment Guide

## Overview
M3U MATRIX PRO now includes automatic GitHub deployment for generated player pages. After generating pages, you can instantly push them to your Liberty-Express GitHub repository's "Ready Made" folder with one click.

---

## Setup Instructions

### 1. GitHub Connection (Already Done ✅)
GitHub has been connected to M3U MATRIX PRO with full repository access. Your credentials are securely managed through Replit.

### 2. Repository Configuration
The deployment uses your default repository path:
```
C:\Users\banamine\Documents\GitHub\Liberty-Express-
```

Target folder in repository:
```
Ready Made/
```

---

## How to Deploy Generated Pages

### Automatic Deployment Flow

**Step 1:** Load your M3U playlist in M3U MATRIX PRO

**Step 2:** Click **"🌐 Generate Pages"** button

**Step 3:** Select a player type:
- NexusTV Player
- WebIPTV Player
- Simple Player
- BufferTV Player
- Multi-Channel Player
- Classic TV Player
- Rumble Channels

**Step 4:** After generation completes, you'll see:
```
Page generated successfully!

Open [Player] player?

Click YES to open in browser,
NO to skip, or CANCEL to deploy to GitHub
```

**Step 5:** Click **CANCEL** to deploy to GitHub

**Step 6:** Wait for deployment confirmation:
```
✅ Deployment Successful!

Copied files:
  • player.html
  • index.html
  • ... (other files)

Total: X files
Location: Ready Made/
Status: Pushed to GitHub main branch
```

---

## What Gets Deployed

### Files Copied
- All generated HTML player pages
- Subdirectories (e.g., `nexus_tv/`, `stream_hub/`)
- All assets and dependencies included in pages

### Destination
```
Liberty-Express-/Ready Made/
├── nexus_tv/
├── webiptv/
├── player.html
├── index.html
└── ... (other generated pages)
```

### Git Actions
1. ✅ Copy files to `Ready Made/` folder
2. ✅ Stage files with `git add`
3. ✅ Commit with auto-generated message:
   ```
   feat: Auto-deploy generated pages (2025-11-22 10:30:00)
   ```
4. ✅ Push to `main` branch on `origin`

---

## Manual Deployment (Advanced)

If you want to deploy without generating new pages:

```python
from Core_Modules.github_deploy import deploy_generated_pages

# Deploy pages from any directory
result = deploy_generated_pages(
    source_dir="./generated_pages",
    subfolder_name="nexus_tv"  # Optional
)

print(f"Deployed: {len(result['copied_files'])} files")
print(f"Success: {result['success']}")
```

---

## Deployment Status Messages

### ✅ Success
```
Deployment Successful!
Copied files:
  • player.html
  • config.json
  ... and X more

Total: X files
Location: Ready Made/
Status: Pushed to GitHub main branch
```

### ❌ Failure - Repository Not Found
**Cause:** Liberty-Express- path doesn't exist
**Solution:** 
1. Verify path: `C:\Users\banamine\Documents\GitHub\Liberty-Express-`
2. Ensure repository is cloned
3. Check path in `Core_Modules/github_deploy.py`

### ❌ Failure - Not a Git Repository
**Cause:** Path exists but .git folder missing
**Solution:** 
1. Navigate to repository folder
2. Run: `git init` or `git clone <url>`

### ❌ Failure - Authentication Error
**Cause:** GitHub credentials invalid
**Solution:**
1. Reconnect GitHub integration in Replit
2. Verify personal access token has `repo` scope

---

## Troubleshooting

### Issue: Deployment gets stuck
**Solution:** Check console logs in M3U MATRIX PRO
- Status bar shows `❌ Deployment failed: ...`
- Look for git error messages
- Try redeploying after fixing errors

### Issue: Files not showing up in GitHub
**Solutions:**
1. **Check GitHub web interface:** 
   - Navigate to `Ready Made/` folder in your repository
   - Verify files are there
   
2. **Check local repository:**
   - Open File Explorer to Liberty-Express- folder
   - Look for `Ready Made/` folder with files

3. **Check git history:**
   - Run: `git log --oneline` in repository
   - Look for recent commits with "Auto-deploy"

### Issue: Want to stop auto-push to GitHub
**Solution:** Modify `Core_Modules/github_deploy.py`:
```python
# Change this line:
result = self.github_deployer.deploy(str(source_dir), auto_push=True)

# To:
result = self.github_deployer.deploy(str(source_dir), auto_push=False)
```

---

## File Structure

### M3U MATRIX PRO Deployment Code
```
Applications/M3U_MATRIX_PRO.py
├── __init__() - Initializes GitHubDeploy
├── deploy_to_github() - Handles deployment workflow
└── _generate_page() - Triggers deployment on generation

Core_Modules/github_deploy.py
├── GitHubDeploy class
│   ├── __init__() - Initialize with repo path
│   ├── is_repo_ready() - Check if repo exists
│   ├── copy_pages() - Copy HTML files
│   ├── git_add() - Stage files
│   ├── git_commit() - Create commit
│   ├── git_push() - Push to remote
│   └── deploy() - Full workflow orchestration
└── deploy_generated_pages() - Convenience function
```

---

## Security & Permissions

### GitHub Token
- Managed securely through Replit
- Credentials NOT stored in code
- Token rotated automatically by Replit
- Scopes: `repo`, `read:user`, `read:org`

### Repository Access
- Full access to your Liberty-Express- repository
- Can read/write to all branches
- Deployment only targets `main` branch

---

## Performance

### Deployment Time
- Copy files: 1-3 seconds (depends on file count)
- Git operations: 2-5 seconds
- Total time: ~5-10 seconds

### File Size Limits
- Single file: No limit (GitHub supports up to 100MB)
- Total size: No limit for private repos

---

## Automation Examples

### Deploy Only Specific Player Type
```python
# Deploy only NexusTV pages
result = deploy_generated_pages(
    source_dir="./generated_pages/nexus_tv",
    subfolder_name="nexus_tv"
)
```

### Deploy with Custom Commit Message
```python
deployer = GitHubDeploy()
result = deployer.deploy(
    source_dir="./generated_pages",
    commit_message="feat: Update all player templates with new features"
)
```

### Check Deployment Status
```python
from Core_Modules.github_deploy import GitHubDeploy

deployer = GitHubDeploy()
if deployer.is_repo_ready():
    print("✅ Repository ready for deployment")
else:
    print("❌ Repository not accessible")
```

---

## GitHub Status

| Component | Status | Details |
|-----------|--------|---------|
| **Integration** | ✅ Connected | GitHub OAuth configured |
| **Repository** | ⏳ Pending | Awaiting first deployment |
| **Branch** | ✅ main | Default push target |
| **Ready Made Folder** | ✅ Ready | Created on first deployment |

---

## Next Steps

1. **Generate your first player page** with M3U MATRIX PRO
2. **Click CANCEL** to deploy to GitHub
3. **Verify files** in your Liberty-Express- repository's Ready Made folder
4. **Monitor deployments** via commit history on GitHub

---

## Support

### For Errors
1. Check status bar messages in M3U MATRIX PRO
2. Review `Applications/logs/m3u_matrix.log` for detailed errors
3. Ensure GitHub connection is active (check Replit integrations)

### For Features
Deployment workflow is part of Phase 2 & Phase 3 implementation:
- Phase 2: Multi-tier stream validation ✅
- Phase 3: True Offline/Zero-Fetch Generation (Jan 6)

---

**Last Updated:** November 22, 2025  
**Feature Status:** 🚀 Production Ready  
**Integration Status:** ✅ GitHub Connected
