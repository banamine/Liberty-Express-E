# Authentication Setup Guide - Quick Start

**For Developers:** How to use the new JWT authentication system

---

## Quick Start (5 minutes)

### Step 1: Register a User
```bash
curl -X POST "http://localhost:3000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d {
    "username": "myuser",
    "email": "user@example.com", 
    "password": "MySecurePass123"
  }
```

### Step 2: Login
```bash
curl -X POST "http://localhost:3000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d {
    "username": "myuser",
    "password": "MySecurePass123"
  }
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Step 3: Use the Token
```bash
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3000/api/auth/profile
```

Done! 🎉

---

## Complete API Reference

### Authentication Endpoints

#### Register User
```
POST /api/auth/register
Content-Type: application/json

Request:
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123"
}

Response (201 Created):
{
  "status": "success",
  "message": "User john_doe created successfully"
}

Error (400):
{
  "status": "error",
  "message": "Username already exists"
}
```

#### Login
```
POST /api/auth/login
Content-Type: application/json

Request:
{
  "username": "john_doe",
  "password": "SecurePassword123"
}

Response (200 OK):
{
  "status": "success",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Login successful"
}

Error (401):
{
  "detail": "Invalid username or password"
}
```

#### Get Current User Profile
```
GET /api/auth/profile
Authorization: Bearer TOKEN

Response (200 OK):
{
  "status": "success",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "viewer",
    "is_active": 1,
    "created_at": "2025-11-23T05:12:45.123456"
  }
}

Error (401):
{
  "detail": "Not authenticated"
}
```

#### Logout
```
POST /api/auth/logout
Authorization: Bearer TOKEN

Response (200 OK):
{
  "status": "success",
  "message": "Logged out successfully"
}
```

---

### User Management (Admin Only)

#### List All Users
```
GET /api/users
Authorization: Bearer ADMIN_TOKEN

Response:
{
  "status": "success",
  "users": [
    {
      "id": "uuid1",
      "username": "john_doe",
      "email": "john@example.com",
      "role": "viewer",
      "is_active": 1,
      "created_at": "2025-11-23T05:12:45"
    },
    {
      "id": "uuid2",
      "username": "jane_admin",
      "email": "jane@example.com",
      "role": "admin",
      "is_active": 1,
      "created_at": "2025-11-23T05:12:50"
    }
  ]
}
```

#### Delete User
```
DELETE /api/users/{user_id}
Authorization: Bearer ADMIN_TOKEN

Response:
{
  "status": "success",
  "message": "User deleted successfully"
}
```

#### Update User Role
```
PUT /api/users/{user_id}/role
Authorization: Bearer ADMIN_TOKEN
Content-Type: application/json

Request:
{
  "role": "editor"  // or "viewer", "admin"
}

Response:
{
  "status": "success",
  "message": "User role updated to editor"
}
```

---

## Token Usage in Your Application

### JavaScript/Fetch
```javascript
const token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...";

fetch('http://localhost:3000/api/auth/profile', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

### Python/Requests
```python
import requests

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
headers = {'Authorization': f'Bearer {token}'}

response = requests.get(
  'http://localhost:3000/api/auth/profile',
  headers=headers
)
print(response.json())
```

### cURL
```bash
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3000/api/auth/profile
```

---

## Protecting Your Own Endpoints

### In FastAPI
```python
from fastapi import Depends, HTTPException

@app.get("/api/protected-endpoint")
def protected_endpoint(user_id: Optional[str] = Depends(get_current_user)):
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Your code here - user_id is now available
    return {"user_id": user_id}
```

---

## Error Handling

### Common Errors

**Invalid Token**
```json
{
  "detail": "Not authenticated"
}
Status: 401
```

**Missing Authorization Header**
```json
{
  "detail": "Not authenticated"
}
Status: 401
```

**Invalid Username/Password**
```json
{
  "detail": "Invalid username or password"
}
Status: 401
```

**Admin Access Required**
```json
{
  "detail": "Admin access required"
}
Status: 403
```

**User Not Found**
```json
{
  "detail": "User not found"
}
Status: 404
```

---

## Best Practices

### 1. Token Storage
- ✅ Store in httpOnly cookies (most secure)
- ⚠️ Store in localStorage (convenient, less secure)
- ❌ Log tokens or display them

### 2. Token Expiration
- Default: 24 hours
- Check: Always validate token on protected endpoints
- Refresh: Implement refresh tokens for long sessions

### 3. Password Requirements
- Minimum 8 characters
- Mix of uppercase, lowercase, numbers, symbols (recommended)
- Never store plain text
- Always use HTTPS in production

### 4. Admin Account
- Create admin user first (before other users)
- Use strong password
- Keep admin credentials secure
- Rotate regularly

---

## Troubleshooting

### "User already exists"
The username is taken. Choose a different username.

### "Invalid email format"
Email must contain @ symbol and be valid format.

### "Password must be at least 8 characters"
Use a longer password with mix of characters.

### "Invalid username or password"
Check:
1. Username is correct (case-sensitive)
2. Password is correct
3. User account exists

### Token not working
Check:
1. Token hasn't expired (24 hours)
2. Authorization header format: `Bearer TOKEN`
3. Token isn't modified (single space matters)

---

## Migrating from Old API

### Old (No Auth)
```bash
curl http://localhost:3000/api/schedule
```

### New (With Auth)
```bash
# 1. Login first
TOKEN=$(curl -s -X POST "http://localhost:3000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"pass"}' | jq -r '.token')

# 2. Use token in requests
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3000/api/schedule
```

---

## Support

For issues or questions:
1. Check logs: `logs/scheduleflow.log`
2. Review API docs: `http://localhost:3000/docs`
3. See security guide: `SECURITY_IMPROVEMENTS.md`

---

**Ready to use! Start by registering a user.**
