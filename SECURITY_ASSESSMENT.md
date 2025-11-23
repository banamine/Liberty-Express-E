# 🔒 SECURITY ASSESSMENT - ScheduleFlow

**Status:** Security review complete with recommendations  
**Date:** November 23, 2025

---

## CRITICAL FINDINGS

### 🔴 CURRENT STATE: Open Dashboard (By Design)

**End-User Access:**
- ✅ Zero authentication required
- ✅ Intentional open access for scheduling
- ⚠️ **Security implication:** Anyone with URL can import/schedule

**What Anyone Can Do:**
```
✓ Import schedules (XML/JSON)
✓ Create playlists  
✓ Export data
✓ View system info
✓ Schedule videos

❌ Cannot delete (no DELETE endpoint yet)
❌ Cannot modify others' schedules
```

**Risk Level:** 🟡 **MEDIUM** (in private networks) → 🔴 **HIGH** (on public internet)

---

## SECTION 1: WHAT NEEDS PROTECTION

### A. Data Operations (Currently Open)

| Operation | Current | Risk | Recommendation |
|-----------|---------|------|-----------------|
| **Create Schedule** | Open ✓ | Low | No change |
| **Read Schedule** | Open ✓ | Low | No change |
| **Update Schedule** | No endpoint | - | Add with auth |
| **Delete Schedule** | No endpoint | - | Add with admin auth |
| **Import XML** | Open ✓ | 🟡 Medium | Validate + scan |
| **Export Data** | Open ✓ | Low | No change |
| **System Info** | Open ✓ | Low | No change |

### B. Critical Operations Needing Protection

```
DELETE /api/schedule/:id
  → Requires: Admin role
  → Protection: API key or session token

DELETE /api/all-schedules
  → Requires: Super-admin role
  → Protection: API key + confirmation

POST /api/import-schedule (with validation)
  → Requires: None (open) OR Admin approval
  → Protection: XML schema validation, size limits

PUT /api/schedule/:id
  → Requires: Owner or admin
  → Protection: Session token
```

### C. Injection Risks

**XML/JSON Import:**
```xml
<!-- MALICIOUS: Oversized file -->
<?xml version="1.0"?>
<tvguide>
  <event>... (1 GB of events)</event>
</tvguide>

<!-- MALICIOUS: Infinite loop -->
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>

<!-- MALICIOUS: Script injection -->
<event>
  <title>&lt;script&gt;alert('xss')&lt;/script&gt;</title>
</event>
```

**Current Protections:**
- ✅ XML schema validation (test_unit.py)
- ✅ JSON schema validation
- ❌ File size limits (not implemented)
- ❌ XML entity attack prevention (not implemented)
- ✅ HTML escaping in output

---

## SECTION 2: PROPOSED SECURITY MODEL

### Option A: Simple Admin API Key (Recommended for MVP)

```json
// api_config.json (checked into repo)
{
  "apiKey": "scheduleflow_admin_key_12345",
  "allowOpenAccess": true,
  "protectedOperations": ["DELETE", "UPDATE"],
  "fileUploadMaxSize": "50MB",
  "xmlValidation": {
    "maxEvents": 10000,
    "preventXmlEntityAttacks": true,
    "timeoutSeconds": 30
  }
}
```

**API Usage:**
```bash
# Admin operation (protected)
curl -X DELETE http://localhost:5000/api/schedule/123 \
  -H "Authorization: Bearer scheduleflow_admin_key_12345"

# User operation (open)
curl -X POST http://localhost:5000/api/import-schedule \
  -F "file=@schedule.xml"
```

**Workflow:**
1. Protect DELETE endpoints with API key
2. Protect PUT/UPDATE endpoints with API key
3. Keep GET/POST open (no auth)
4. Store API key in api_config.json

**Timeline:** 2-3 hours

---

### Option B: Role-Based Access Control (Full Featured)

```json
// api_roles.json
{
  "roles": {
    "viewer": {
      "permissions": ["read:schedules", "read:system"]
    },
    "editor": {
      "permissions": ["read:schedules", "create:schedule", "export:data"]
    },
    "admin": {
      "permissions": ["*"]
    }
  },
  "users": {
    "user1@example.com": "viewer",
    "user2@example.com": "editor",
    "admin@example.com": "admin"
  }
}
```

**Workflow:**
1. User logs in with username/password
2. System checks role from api_roles.json
3. Dashboard hides operations user can't perform
4. API enforces permissions on each request

**Timeline:** 5-7 days

---

## SECTION 3: IMPLEMENTATION ROADMAP

### Phase 1: Immediate (Today - 2 hours)

**What to add:**
```javascript
// api_server.js

// Add API key validation middleware
function validateAdminKey(req, res, next) {
  const apiKey = req.headers.authorization?.split(' ')[1];
  if (!apiKey || apiKey !== process.env.ADMIN_API_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
}

// Protect DELETE operations
app.delete('/api/schedule/:id', validateAdminKey, async (req, res) => {
  // Delete implementation
});

app.post('/api/import-schedule', (req, res) => {
  // Validate file size
  if (req.file.size > 50 * 1024 * 1024) { // 50MB limit
    return res.status(413).json({ error: 'File too large' });
  }
  // Continue with import
});
```

**Config:**
```env
# .env file (added to .gitignore)
ADMIN_API_KEY=scheduleflow_admin_key_12345
MAX_UPLOAD_SIZE=52428800  # 50MB
```

**Benefits:**
- ✅ Simple to implement
- ✅ No database required
- ✅ Works immediately
- ✅ Protects deletion

---

### Phase 2: Full Implementation (1-2 weeks)

**What to add:**
- Role-based access control
- User authentication (GitHub OAuth)
- Permission checks on all endpoints
- Audit logging

---

## SECTION 4: SPECIFIC SECURITY QUESTIONS ANSWERED

### Q18: Can anyone delete schedules?

**Current State:** ❌ NO - Delete endpoint doesn't exist

**Future:** Will require admin API key (Phase 1) or login (Phase 2)

**How to Fix:**
```javascript
// Add DELETE endpoint with protection
app.delete('/api/schedule/:id', validateAdminKey, async (req, res) => {
  // Only admins can delete
  const output = await pythonQueue.execute([
    'M3U_Matrix_Pro.py', '--delete-schedule', req.params.id
  ]);
  res.json(JSON.parse(output));
});
```

---

### Q19: Can anyone inject malicious XML?

**Current State:** ⚠️ PARTIALLY PROTECTED

**Protections in Place:**
- ✅ XML schema validation (validates structure)
- ✅ HTML escaping (prevents XSS)
- ✅ JSON schema validation

**Missing Protections:**
- ❌ File size limits
- ❌ XML entity attack prevention
- ❌ Timeout on parsing

**How to Fix:**
```javascript
// Add size limit and entity protection
app.post('/api/import-schedule', (req, res) => {
  // Check file size
  if (req.file.size > 50 * 1024 * 1024) {
    return res.status(413).json({ error: 'File too large' });
  }

  // Disable XML entity expansion
  const parser = new DOMParser({
    resolveExternalEntities: false,  // Prevent XXE
    processingInstructions: false
  });

  try {
    const doc = parser.parseFromString(fileContent, 'text/xml');
    // Continue with validation
  } catch (e) {
    return res.status(400).json({ error: 'Malformed XML' });
  }
});
```

---

### Q20: Where do permissions live?

**Recommended Location:**
```
config/
  ├── api_config.json (public - settings)
  ├── api_roles.json (private - DO NOT COMMIT)
  ├── security.json (private - DO NOT COMMIT)
  └── .gitignore (ignore json files)
```

**Example api_config.json:**
```json
{
  "port": 5000,
  "apiKeyRequired": true,
  "allowOpenAccess": true,
  "protectedOperations": ["DELETE", "PUT"],
  "fileUploadMaxSize": "50MB",
  "xmlValidation": {
    "preventEntityAttacks": true,
    "maxEvents": 10000
  }
}
```

---

### Q21: Is this only for developers?

**Answer:** No - Security can be configured without code changes

**Non-Developer Admin Workflow:**
1. Get ADMIN_API_KEY from admin
2. Edit config/api_config.json
3. Set apiKeyRequired: true
4. Restart server

**Developer Workflow:**
1. Clone repo
2. Create .env file with ADMIN_API_KEY
3. Run npm install
4. Run node api_server.js
5. API is now protected

---

## SECTION 5: SECURITY CHECKLIST

### For Private Networks (Current Use Case)

- ✅ No auth needed for end-users (open dashboard)
- ⚠️ **TODO:** Add API key for admin deletion
- ⚠️ **TODO:** Add file size limits on imports
- ⚠️ **TODO:** Add XML entity attack prevention
- ✅ HTML escaping prevents XSS

**Timeline to Implement:** 2-3 hours

### For Public Internet (Future)

- ❌ Add authentication system
- ❌ Add authorization/roles
- ❌ Add rate limiting
- ❌ Add audit logging
- ❌ Add HTTPS enforcement

**Timeline to Implement:** 1-2 weeks

---

## SUMMARY: WHAT NEEDS TO HAPPEN

### Immediate (Today)

```javascript
// Add to api_server.js

// 1. Validate admin API key
const validateAdminKey = (req, res, next) => {
  const key = req.headers.authorization?.split(' ')[1];
  if (key !== process.env.ADMIN_API_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
};

// 2. Add DELETE endpoint
app.delete('/api/schedule/:id', validateAdminKey, async (req, res) => {
  const output = await pythonQueue.execute(['M3U_Matrix_Pro.py', '--delete-schedule', req.params.id]);
  res.json(JSON.parse(output));
});

// 3. Add size limits
app.post('/api/import-schedule', (req, res) => {
  if (req.file.size > 50 * 1024 * 1024) {
    return res.status(413).json({ error: 'File too large' });
  }
  // Continue...
});
```

### Files to Create

```
.env                          # API key storage (add to .gitignore)
config/api_config.json        # Configuration
config/.gitignore             # Ignore secrets
```

### Files to Update

```
api_server.js                 # Add validation middleware
replit.md                     # Document security model
```

---

## VERDICT

**Current State for Private Networks:** ✅ Safe (open access is intentional)

**Current State for Public Internet:** 🔴 Needs admin key protection

**Recommendation:** Implement Phase 1 (admin API key) immediately before expanding to public use.

**Effort:** 2-3 hours for core implementation
