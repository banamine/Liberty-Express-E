# ScheduleFlow Deployment Guide

**Version:** 2.0.0  
**Last Updated:** November 22, 2025  
**Platforms:** Linux, macOS, Windows (via WSL)

---

## Quick Start (Development)

### Prerequisites
- Node.js 16+ (for API server)
- Python 3.8+ (for scheduling logic)
- npm (for dependencies)

### Installation (5 minutes)

```bash
# 1. Install dependencies
npm install
pip install requests Pillow pillow-simd tkinterdnd2 python-vlc numpy opencv-python pdfplumber

# 2. Start the API server
node api_server.js

# 3. Open in browser
http://localhost:5000
```

**Server will be ready at:** `http://localhost:5000`

---

## Project Structure

```
.
├── M3U_Matrix_Pro.py        ← Core scheduling engine (Python)
├── api_server.js            ← REST API (Express.js)
├── generated_pages/         ← Web interface files
│   ├── index.html          ← Main hub
│   ├── interactive_hub.html ← Dashboard
│   └── *.html              ← Player templates
├── schedules/              ← Schedule storage (JSON)
├── m3u_matrix_settings.json ← Configuration
└── package.json            ← Node dependencies
```

---

## Configuration

### m3u_matrix_settings.json

Default configuration structure:
```json
{
  "playlists": [],
  "schedules": [],
  "exports": []
}
```

**View/Edit:**
```bash
curl http://localhost:5000/api/config
```

---

## Starting the Server

### Development Mode
```bash
node api_server.js
```

**Logs to console:**
```
╔════════════════════════════════════════════════╗
║   ScheduleFlow API Server Running              ║
║                                                ║
║   API Endpoint:                                ║
║   http://localhost:5000/api/infowars-videos  ║
║                                                ║
║   Static Files:                                ║
║   http://localhost:5000/generated_pages/      ║
╚════════════════════════════════════════════════╝
```

### Production Mode (Recommended)

Use process manager (PM2):
```bash
# Install PM2
npm install -g pm2

# Start server
pm2 start api_server.js --name "scheduleflow"

# View logs
pm2 logs scheduleflow

# Monitor
pm2 monit

# Restart on reboot
pm2 startup
pm2 save
```

---

## Docker Deployment (Optional)

### Dockerfile
```dockerfile
FROM node:16
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
EXPOSE 5000
CMD ["node", "api_server.js"]
```

### Build and Run
```bash
docker build -t scheduleflow .
docker run -p 5000:5000 scheduleflow
```

---

## Replit Deployment (Current)

### Automated Setup

The project is configured for Replit deployment:

**Workflow:** `ScheduleFlow API Server`
```
Command: node api_server.js
Port: 5000
Output: webview
```

### Manual Configuration (if needed)

1. **In Replit:** Tools → Secrets → Add
   - Add any API keys as secrets (currently none needed)

2. **Start workflow:**
   - Tools → Workflows → Start "ScheduleFlow API Server"

3. **Access:**
   - Replit provides public URL automatically

---

## Environment Variables

### Development
```bash
PORT=5000              # API port (default)
NODE_ENV=development
```

### Production
```bash
PORT=5000
NODE_ENV=production
ENABLE_CACHING=true
LOG_LEVEL=warn
```

**Set in Replit:**
- Tools → Secrets (encrypted)
- Tools → Environment variables (for public values)

---

## Database Setup

### Current (Development)
- Uses JSON files in `schedules/` directory
- Suitable for MVP and small deployments

### Recommended for Production
Migrate to PostgreSQL (not yet implemented):
```sql
CREATE TABLE schedules (
  id UUID PRIMARY KEY,
  name VARCHAR(255),
  source VARCHAR(10),
  events JSONB,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE cooldown_history (
  video_url VARCHAR(500) PRIMARY KEY,
  last_played TIMESTAMP,
  created_at TIMESTAMP
);
```

---

## Performance Optimization

### For 10-50 Concurrent Users
Current setup is sufficient.

### For 50-100 Concurrent Users
Implement async I/O:
```bash
# Convert sync file operations to async
# Timeline: 2-3 days
# Impact: 5x performance improvement
```

### For 100-500 Concurrent Users
Add worker process pool:
```bash
# Keep Python processes alive instead of spawning
# Timeline: 1-2 days
# Impact: 10x throughput improvement
```

### For 500-1000+ Concurrent Users
Full production stack:
```bash
# - PostgreSQL for data persistence
# - Redis for caching
# - Node.js clustering
# - Load balancer (nginx)
# Timeline: 2-3 weeks
```

---

## Monitoring & Logging

### View Logs (Replit)
- Workflows → Select "ScheduleFlow API Server" → View Logs
- Or via command: Check logs in bottom panel

### Check Server Status
```bash
curl http://localhost:5000/api/system-info
```

Response:
```json
{
  "status": "success",
  "version": "2.0.0",
  "platform": "Web & Desktop",
  "pages_generated": 42,
  "timestamp": "2025-11-22T23:55:00Z"
}
```

### Error Handling
All API errors return JSON with details:
```json
{
  "status": "error",
  "message": "Human-readable error",
  "type": "error_type"
}
```

---

## Backup & Recovery

### Schedule Backup
Schedules are stored in JSON:
```bash
# Backup all schedules
cp -r schedules/ schedules.backup.$(date +%Y%m%d)

# Restore from backup
cp schedules.backup.20251122/* schedules/
```

### Config Backup
```bash
cp m3u_matrix_settings.json m3u_matrix_settings.json.backup
```

---

## SSL/HTTPS

### For Production Website
ScheduleFlow serves over HTTP by default.

For production, use:
1. **Nginx reverse proxy** with SSL
2. **Let's Encrypt** for free SSL certificate
3. **Certbot** for auto-renewal

### Example Nginx config
```nginx
server {
  listen 443 ssl http2;
  server_name scheduleflow.example.com;
  
  ssl_certificate /etc/letsencrypt/live/scheduleflow.example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/scheduleflow.example.com/privkey.pem;
  
  location / {
    proxy_pass http://localhost:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

---

## Troubleshooting

### Server Won't Start
```bash
# Check port is available
netstat -tln | grep 5000

# Kill process using port 5000
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Slow Response Times
```bash
# Check if using sync file I/O
grep "readFileSync\|writeFileSync\|statSync" api_server.js

# Check system resources
top -n 1 | head -10
```

### Memory Leaks
```bash
# Monitor process memory
pm2 monit

# If growing, check for:
# 1. Process spawning without cleanup
# 2. Unbounded data structures
# 3. Event listener cleanup
```

### Schedule Import Failing
```bash
# Check file exists and is readable
ls -la /path/to/schedule.xml

# Test with curl
curl -X POST http://localhost:5000/api/import-schedule \
  -H "Content-Type: application/json" \
  -d '{"filepath": "/path/to/schedule.xml", "format": "xml"}'
```

---

## Scaling Checklist

### For MVP (Current)
- [x] Single server (Node.js + Python)
- [x] JSON file storage
- [x] HTTP only
- [x] No authentication
- [x] No rate limiting

### For Production (100+ users)
- [ ] Async I/O (Node.js)
- [ ] Worker process pool (Python)
- [ ] PostgreSQL database
- [ ] Redis caching
- [ ] HTTPS/SSL
- [ ] Load balancer
- [ ] Authentication/authorization
- [ ] Rate limiting
- [ ] Monitoring (Prometheus/Grafana)
- [ ] Alerting (PagerDuty)
- [ ] Logging (ELK stack)

---

## Maintenance

### Regular Tasks
```bash
# Weekly: Backup schedules
0 0 * * 0 cp -r /app/schedules /backups/schedules.$(date +\%Y\%m\%d)

# Monthly: Clear old logs (if logging enabled)
0 2 1 * * find /app/logs -mtime +30 -delete

# Daily: Check server health
0 */6 * * * curl -f http://localhost:5000/api/system-info || alert
```

### Dependency Updates
```bash
# Check for updates
npm outdated
pip list --outdated

# Update carefully, test in dev first
npm update
pip install --upgrade <package>
```

---

## Support & Troubleshooting

### Debug Mode
Enable verbose logging:
```bash
# Set in environment
LOG_LEVEL=debug node api_server.js
```

### Get Help
1. Check logs: `pm2 logs scheduleflow`
2. Test API: `curl http://localhost:5000/api/system-info`
3. Check configuration: `curl http://localhost:5000/api/config`
4. Review documentation: See API_DOCUMENTATION.md

---

## Version History

**v2.0.0** (Nov 22, 2025)
- Fixed corrupted config file
- Added API documentation
- Added deployment guide
- Identified blocking I/O issues
- Created test suites

---

**Last Updated:** November 22, 2025  
**Status:** Complete  
**For Production:** Implement async I/O first
