# Production Monitoring & Health Checks

**Date:** November 23, 2025  
**New Feature:** Health check and queue statistics endpoints

---

## Quick Status Check (No Code Needed)

### Health Check
```bash
curl http://your-app/api/health
```

**Response (Healthy):**
```json
{
  "status": "healthy",
  "uptime_ms": 12345678,
  "timestamp": "2025-11-23T02:15:30Z",
  "process_pool": {
    "active": 2,
    "max": 4,
    "utilization_percent": 50,
    "queued": 0
  }
}
HTTP Status: 200
```

**Response (Degraded - all 4 slots in use):**
```json
{
  "status": "degraded",
  "uptime_ms": 12345678,
  "timestamp": "2025-11-23T02:15:30Z",
  "process_pool": {
    "active": 4,
    "max": 4,
    "utilization_percent": 100,
    "queued": 5
  }
}
HTTP Status: 503
```

### Queue Statistics
```bash
curl http://your-app/api/queue-stats
```

**Response:**
```json
{
  "status": "success",
  "queue": {
    "active_processes": 2,
    "queued_tasks": 3,
    "max_concurrency": 4,
    "utilization_percent": 50
  },
  "statistics": {
    "total_processed": 156,
    "total_queued": 159,
    "total_errors": 2,
    "peak_active": 4,
    "peak_queue_size": 8
  },
  "timestamp": "2025-11-23T02:15:30Z"
}
```

---

## Monitoring in Production

### Simple Health Check (Uptime Monitor)
```bash
# Every 30 seconds
while true; do
  curl -s http://your-app/api/health | grep "status" | grep "healthy" && echo "✓ OK" || echo "✗ FAILED"
  sleep 30
done
```

### Track Queue Buildup
```bash
# Every minute
curl -s http://your-app/api/queue-stats | jq '.queue.queued_tasks'
```

### Error Tracking
```bash
# Watch for errors
curl -s http://your-app/api/queue-stats | jq '.statistics.total_errors'
```

### Peak Utilization
```bash
# See if system ever maxed out
curl -s http://your-app/api/queue-stats | jq '.statistics.peak_active'
# If shows 4 = system hit max concurrency
```

---

## What Each Field Means

### Health Endpoint
| Field | Meaning |
|-------|---------|
| `status` | "healthy" = space available, "degraded" = all slots in use |
| `uptime_ms` | How long API server has been running |
| `active` | Python processes currently running |
| `max` | Maximum allowed concurrent processes (always 4) |
| `utilization_percent` | (active / max) × 100 |
| `queued` | Requests waiting for a free slot |

### Queue Stats Endpoint
| Field | Meaning |
|-------|---------|
| `active_processes` | Python processes running now |
| `queued_tasks` | Waiting to run |
| `total_processed` | All operations ever completed |
| `total_errors` | Failed operations |
| `peak_active` | Highest concurrent processes seen |
| `peak_queue_size` | Largest queue size ever seen |

---

## Real Production Scenarios

### Scenario 1: Healthy Operation
```
GET /api/health
{
  "active": 1,
  "max": 4,
  "queued": 0
}
```
✅ **System is fine.** One operation running, plenty of capacity.

### Scenario 2: Busy But Healthy
```
{
  "active": 3,
  "max": 4,
  "queued": 0
}
```
✅ **System is busy.** Three operations running, one slot available. No queue.

### Scenario 3: Queue Building (Monitor)
```
{
  "active": 4,
  "max": 4,
  "queued": 5
}
```
⚠️ **System at capacity.** All 4 slots in use, 5 requests waiting. System will recover as operations complete. **This is OK if temporary.**

### Scenario 4: Large Queue (Investigate)
```
{
  "active": 4,
  "max": 4,
  "queued": 50
}
```
❌ **Something is wrong.** Queue is growing faster than operations complete. Options:
1. **Check logs for errors:** `grep ERROR logs/scheduleflow.log`
2. **Check for hung processes:** Operations might be exceeding 30-second timeout
3. **Check system resources:** Memory/CPU might be exhausted

### Scenario 5: Errors Increasing
```
{
  "total_errors": 150,  // was 50 an hour ago
  "peak_active": 4,
  "peak_queue_size": 15
}
```
⚠️ **Error rate increasing.** Investigation needed:
```bash
grep ERROR logs/scheduleflow.log | tail -20
```

---

## Example: Simple Monitoring Dashboard

```javascript
// Browser console or Node.js script
async function monitorScheduleFlow() {
  const health = await fetch('/api/health').then(r => r.json());
  const queue = await fetch('/api/queue-stats').then(r => r.json());
  
  console.clear();
  console.log('=== ScheduleFlow System Status ===');
  console.log(`Status: ${health.status === 'healthy' ? '✅' : '⚠️'} ${health.status}`);
  console.log(`Uptime: ${(health.uptime_ms / 1000 / 60).toFixed(1)} minutes`);
  console.log(``);
  console.log(`Queue: ${queue.queue.active_processes}/${queue.queue.max} active, ${queue.queue.queued_tasks} waiting`);
  console.log(`Utilization: ${queue.queue.utilization_percent}%`);
  console.log(``);
  console.log(`Total Operations: ${queue.statistics.total_processed}`);
  console.log(`Errors: ${queue.statistics.total_errors}`);
  console.log(`Peak Utilization: ${queue.statistics.peak_active} processes`);
  console.log(`Peak Queue: ${queue.statistics.peak_queue_size} tasks`);
}

// Run every 30 seconds
setInterval(monitorScheduleFlow, 30000);
```

---

## Adding to Your Monitoring

### Uptime Robot / Pingdom
```
Endpoint: https://your-app.replit.dev/api/health
Expected: Status 200, "status": "healthy"
Check Frequency: Every 5 minutes
Alert if: Status ≠ 200 or offline > 5 min
```

### DataDog / New Relic
```
Monitor: /api/queue-stats.statistics.total_errors
Alert if: total_errors increases by >10 in 1 hour
Monitor: /api/health.process_pool.queued
Alert if: queued_tasks > 20 for >5 minutes
```

---

## Architecture Now Visible ✅

Previously:
- ❌ No way to check if system is healthy
- ❌ No visibility into process queue
- ❌ Hidden process failures

Now:
- ✅ Health check shows system status (200 = healthy, 503 = degraded)
- ✅ Queue statistics show capacity + errors
- ✅ Can monitor process pool utilization
- ✅ Error tracking for debugging

---

## Summary

**Two new endpoints added:**
1. **GET /api/health** - Quick health status (200 = healthy, 503 = degraded)
2. **GET /api/queue-stats** - Detailed queue and process statistics

**Use cases:**
- Uptime monitoring (health endpoint)
- Capacity monitoring (queue stats)
- Error tracking (total_errors field)
- Peak load analysis (peak_active, peak_queue_size)

**Production readiness:** Now fully observable ✅

