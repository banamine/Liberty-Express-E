# 🔐 Admin Setup - Phase 1 Security Implementation

**Status:** Phase 1 security is now LIVE  
**Date:** November 23, 2025

---

## QUICK START (5 minutes)

### Step 1: Set Your Admin API Key

You need to set the `ADMIN_API_KEY` environment variable. 

**Via Replit Secrets Tab:**
1. Click "Secrets" tab (lock icon) in Replit
2. Add new secret: `ADMIN_API_KEY`
3. Value: Your secure key (e.g., `my_super_secret_admin_key_12345`)
4. Save

**OR Via .env File:**
1. Create `.env` file in root directory
2. Add: `ADMIN_API_KEY=your_secure_key_here`
3. Note: .env is in .gitignore (won't be committed)

### Step 2: Restart the API Server

The workflow will auto-restart. If not:
- Click "Restart" button in Replit

### Step 3: Test Admin Operations

```bash
# Test: Delete without auth (should FAIL)
curl -X DELETE http://localhost:5000/api/schedule/test_123
# Expected: 401 Unauthorized

# Test: Delete with auth (should WORK)
curl -X DELETE http://localhost:5000/api/schedule/test_123 \
  -H "Authorization: Bearer your_secure_key_here"
# Expected: 200 OK (or 404 if schedule doesn't exist)
```

---

## WHAT'S PROTECTED NOW

### Public Endpoints (No Auth Needed)
```
✓ GET /api/system-info
✓ GET /api/schedules
✓ GET /api/playlists
✓ POST /api/import-schedule
✓ POST /api/schedule-playlist
✓ POST /api/export-schedule-xml
✓ POST /api/export-schedule-json
✓ GET /api/queue-stats
```

**Users can freely import/schedule/export - this is intentional!**

### Admin Endpoints (Requires API Key)
```
✗ DELETE /api/schedule/:id
✗ DELETE /api/all-schedules
```

**Only admins with the API key can delete schedules**

---

## API KEY USAGE

### Format
```
Authorization: Bearer YOUR_API_KEY
```

### Example Requests

**Delete a single schedule:**
```bash
curl -X DELETE http://localhost:5000/api/schedule/schedule_123 \
  -H "Authorization: Bearer your_api_key"
```

**Delete all schedules (requires confirmation):**
```bash
curl -X DELETE http://localhost:5000/api/all-schedules \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"confirm":"DELETE_ALL_SCHEDULES"}'
```

---

## SECURITY FEATURES ENABLED

✅ **API Key Validation**
- All DELETE operations require valid API key
- Invalid/missing keys return 401 Unauthorized

✅ **File Size Limits**
- Maximum 50MB per upload
- Files larger rejected with 413 Payload Too Large

✅ **XML Entity Attack Prevention**
- XXE (XML External Entity) attacks blocked
- DTD declarations rejected

✅ **Configuration Management**
- Settings in `config/api_config.json`
- Environment variables in `.env`
- Credentials never hardcoded

---

## TROUBLESHOOTING

### "401 Unauthorized"
**Problem:** API key not working  
**Solution:** Verify exact API key matches what you set in secrets

### "Missing Authorization header"
**Problem:** Forgot to include Authorization header  
**Solution:** Add `-H "Authorization: Bearer YOUR_KEY"` to curl command

### "Invalid Authorization format"
**Problem:** Wrong format for header  
**Solution:** Use `Bearer YOUR_KEY` (with space, not colon)

### "File too large"
**Problem:** Trying to upload > 50MB file  
**Solution:** Split file into smaller chunks or increase MAX_UPLOAD_SIZE

---

## ENVIRONMENT VARIABLES

### Required
```env
ADMIN_API_KEY=your_secure_key_here
```

### Optional (with defaults)
```env
PORT=5000                           # API server port
MAX_UPLOAD_SIZE=52428800            # 50MB in bytes
PYTHON_PATH=python3                 # Python executable
NODE_ENV=production                 # Environment
```

---

## CONFIGURATION FILE

Location: `config/api_config.json`

```json
{
  "security": {
    "adminKeyRequired": true,
    "protectedOperations": ["DELETE", "PUT"]
  },
  "fileUpload": {
    "maxSizeMB": 50
  },
  "endpoints": {
    "open": [
      "GET /api/system-info",
      "POST /api/import-schedule"
    ],
    "adminOnly": [
      "DELETE /api/schedule/:id"
    ]
  }
}
```

---

## NEXT STEPS

### Option 1: Keep as-is (Recommended for Now)
✅ Phase 1 is complete  
✅ Admin operations secured  
✅ Ready for production in private networks  

### Option 2: Implement Phase 2 (Future)
- Role-based access control
- User authentication
- Audit logging
- Permission enforcement

See `FINAL_SECURITY_ROADMAP.md` for details.

---

## VERIFICATION CHECKLIST

- [ ] Set ADMIN_API_KEY in secrets or .env
- [ ] Restarted API server
- [ ] Tested DELETE without auth (should fail)
- [ ] Tested DELETE with auth (should work)
- [ ] Verified file size limits working
- [ ] Users can still import/schedule (open access)
- [ ] No errors in console logs

---

## SUPPORT

For questions about Phase 1 security:
1. Read `SECURITY_ASSESSMENT.md`
2. Check `PHASE_1_QUICK_START.md` (implementation details)
3. Review `RUTHLESS_QA_ANSWERS.md` (Q18-21 security Q&A)

---

**Phase 1 Complete! ✅ System is now production-ready for private networks.**
