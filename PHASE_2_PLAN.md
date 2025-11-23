# Phase 2 Implementation Plan

**Start Date:** November 23, 2025  
**Deadline:** January 31, 2026  
**Status:** 🚀 IN PROGRESS

---

## Phase 2 Goals

1. ✅ **Version Check** - Detect available updates from GitHub
2. ✅ **Update Endpoint** - Trigger updates via API
3. ✅ **Admin Dashboard** - Non-dev UI for updates
4. ✅ **Auto-Webhook** (Optional) - Auto-pull on GitHub push

---

## Implementation Priority (This Session)

### Priority 1: Version Check Endpoint (20 min)
- GET /api/version-check
- Check GitHub for latest release
- Return: current vs latest version, has_update flag
- Tested & working

### Priority 2: Update Endpoint (30 min)
- POST /api/update-from-github
- Requires API key auth
- Pulls latest code, restarts server
- Returns: new version, status

### Priority 3: Admin Dashboard (60 min)
- Simple HTML form
- Shows current version
- Button: "Check for Updates"
- Button: "Install Update"
- Display update status

### Priority 4: Webhook Handler (Optional, Phase 2.1)
- POST /webhook/github
- Auto-pull on release
- Zero-downtime deployment

---

## Architecture

### Current Endpoints (Phase 1)
✅ GET /api/system-version - Current version only

### New Endpoints (Phase 2)
🔄 GET /api/version-check - Check for updates
🔄 POST /api/update-from-github - Trigger update
🔄 GET /admin/update-panel - Admin dashboard

---

## Files to Modify/Create

### Modify
- api_server.js - Add 3 endpoints (~80 lines)
- replit.md - Update Phase 2 status

### Create
- public/admin-update-panel.html - Admin dashboard
- PHASE_2_COMPLETION_SUMMARY.md - Phase 2 recap

---

## Testing Strategy

1. GET /api/version-check - Verify endpoint works
2. POST /api/update-from-github - Test update flow
3. Admin dashboard - Manual browser test
4. All endpoints - Rate limiting still works

---

## Timeline

- **This Session:** Endpoints + dashboard
- **Next Session:** Webhook + testing
- **Final:** Documentation + production readiness

