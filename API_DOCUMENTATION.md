# ScheduleFlow API Documentation

**Version:** 2.0.0  
**Framework:** Express.js  
**Authentication:** None (public endpoints)  
**Base URL:** http://localhost:5000/api

---

## Overview

ScheduleFlow provides a REST API for:
- Schedule import (XML/JSON)
- Schedule export (XML/JSON)
- Playlist scheduling with auto-fill
- System information retrieval
- Configuration management

All endpoints return JSON responses.

---

## API Endpoints

### System Information

#### GET /api/system-info
**Description:** Get system status and version info  
**Authentication:** None  
**Parameters:** None  
**Response:**
```json
{
  "status": "success",
  "version": "2.0.0",
  "platform": "Web & Desktop",
  "pages_generated": 42,
  "timestamp": "2025-11-22T23:55:00Z"
}
```
**Status Code:** 200 OK  

---

### Pages Management

#### GET /api/pages
**Description:** List all generated HTML pages  
**Authentication:** None  
**Parameters:** None  
**Response:**
```json
{
  "status": "success",
  "pages": [
    {
      "name": "index.html",
      "path": "/generated_pages/index.html",
      "size": 2048,
      "modified": "2025-11-22T23:55:00Z"
    }
  ],
  "count": 1
}
```
**Status Code:** 200 OK  
**Error Codes:** 500 (server error)  

---

### Playlist Management

#### POST /api/save-playlist
**Description:** Save a new M3U playlist to file  
**Authentication:** None  
**Content-Type:** application/json  
**Request Body:**
```json
{
  "filename": "my_playlist",
  "items": [
    {
      "url": "http://example.com/video1.mp4",
      "label": "Video 1"
    },
    {
      "url": "http://example.com/video2.mp4",
      "label": "Video 2"
    }
  ]
}
```
**Response:**
```json
{
  "status": "success",
  "path": "/path/to/my_playlist.m3u",
  "items": 2
}
```
**Status Code:** 200 OK  
**Error Codes:**
- 400 (missing filename or items)
- 500 (save failed)

---

### Configuration Management

#### GET /api/config
**Description:** Get current configuration  
**Authentication:** None  
**Parameters:** None  
**Response:**
```json
{
  "status": "success",
  "config": {
    "playlists": [],
    "schedules": [],
    "exports": []
  }
}
```
**Status Code:** 200 OK  

#### POST /api/config
**Description:** Save configuration  
**Authentication:** None  
**Content-Type:** application/json  
**Request Body:**
```json
{
  "playlists": [],
  "schedules": [],
  "exports": []
}
```
**Response:**
```json
{
  "status": "success",
  "message": "Configuration saved"
}
```
**Status Code:** 200 OK  
**Error Codes:** 500 (save failed)  

---

### Schedule Import

#### POST /api/import-schedule
**Description:** Import schedule from XML or JSON file  
**Authentication:** None  
**Content-Type:** application/json  
**Request Body:**
```json
{
  "filepath": "/path/to/schedule.xml",
  "format": "xml"
}
```
**Formats:** `xml` or `json`  
**Response:**
```json
{
  "status": "success",
  "schedule_id": "uuid-here",
  "events_imported": 50,
  "duplicates_removed": 2,
  "conflicts_detected": 1,
  "warnings": {
    "duplicates": "2 duplicate events removed",
    "conflicts": "1 overlapping timeslots detected"
  }
}
```
**Status Code:** 200 OK  
**Error Codes:**
- 400 (missing filepath or format)
- 500 (import failed)

---

### Schedule Listing

#### GET /api/schedules
**Description:** List all imported schedules  
**Authentication:** None  
**Parameters:** None  
**Response:**
```json
{
  "status": "success",
  "schedules": [
    {
      "id": "schedule-uuid",
      "name": "My Schedule",
      "source": "xml",
      "events": 48,
      "imported": "2025-11-22T23:55:00Z"
    }
  ],
  "count": 1
}
```
**Status Code:** 200 OK  

#### GET /api/playlists
**Description:** List all playlists  
**Authentication:** None  
**Parameters:** None  
**Response:**
```json
{
  "status": "success",
  "playlists": [
    {
      "name": "My Playlist",
      "items": 25,
      "imported": "2025-11-22T23:55:00Z"
    }
  ],
  "count": 1
}
```
**Status Code:** 200 OK  

---

### Schedule Export

#### POST /api/export-schedule-xml
**Description:** Export schedule to XML (TVGuide format)  
**Authentication:** None  
**Content-Type:** application/json  
**Request Body:**
```json
{
  "schedule_id": "uuid-here",
  "filename": "my_schedule.xml"
}
```
**Response:**
```json
{
  "status": "success",
  "file": "/path/to/my_schedule.xml",
  "size": 15000,
  "events": 48
}
```
**Status Code:** 200 OK  
**Error Codes:**
- 400 (missing schedule_id)
- 500 (export failed)

#### POST /api/export-schedule-json
**Description:** Export schedule to JSON  
**Authentication:** None  
**Content-Type:** application/json  
**Request Body:**
```json
{
  "schedule_id": "uuid-here",
  "filename": "my_schedule.json"
}
```
**Response:**
```json
{
  "status": "success",
  "file": "/path/to/my_schedule.json",
  "size": 12000,
  "events": 48
}
```
**Status Code:** 200 OK  
**Error Codes:**
- 400 (missing schedule_id)
- 500 (export failed)

#### POST /api/export-all-schedules-xml
**Description:** Export all schedules to single XML file  
**Authentication:** None  
**Content-Type:** application/json  
**Request Body:**
```json
{
  "filename": "all_schedules.xml"
}
```
**Response:**
```json
{
  "status": "success",
  "file": "/path/to/all_schedules.xml",
  "schedules": 5,
  "events": 240
}
```
**Status Code:** 200 OK  

---

### Scheduling

#### POST /api/schedule-playlist
**Description:** Schedule playlist with auto-fill over time period  
**Authentication:** None  
**Content-Type:** application/json  
**Request Body:**
```json
{
  "links": [
    "http://example.com/video1.mp4",
    "http://example.com/video2.mp4"
  ],
  "start_time": "2025-11-23T08:00:00Z",
  "duration_hours": 24,
  "cooldown_hours": 48,
  "shuffle": true
}
```
**Parameters:**
- `links` (required): Array of video URLs
- `start_time` (required): ISO 8601 timestamp
- `duration_hours` (optional): Hours to schedule (default: 24)
- `cooldown_hours` (optional): Hours between repeats (default: 48)
- `shuffle` (optional): Randomize order (default: true)

**Response:**
```json
{
  "status": "success",
  "schedule_id": "uuid-here",
  "events": 48,
  "duration": "24 hours",
  "coverage": "100%"
}
```
**Status Code:** 200 OK  
**Error Codes:**
- 400 (missing or invalid links/start_time)
- 500 (scheduling failed)

---

### External Data

#### GET /api/infowars-videos
**Description:** Fetch video metadata from external source  
**Authentication:** None  
**Parameters:** None  
**Response:**
```json
{
  "status": "success",
  "videos": [
    {
      "url": "http://example.com/video.mp4",
      "title": "Video Title",
      "duration": 3600
    }
  ],
  "count": 10
}
```
**Status Code:** 200 OK  
**Error Codes:** 500 (fetch failed)

---

## Response Format

### Success Response
```json
{
  "status": "success",
  "data": {}
}
```
**Status Code:** 200 OK

### Error Response
```json
{
  "status": "error",
  "message": "Human-readable error message",
  "type": "error_type"
}
```
**Status Codes:** 400, 404, 500

---

## Error Types

| Type | Cause | Status |
|------|-------|--------|
| validation | Missing or invalid fields | 400 |
| parse_error | Invalid XML/JSON syntax | 400 |
| not_found | Resource doesn't exist | 404 |
| unexpected | Unhandled server error | 500 |

---

## Usage Examples

### Import a Schedule
```bash
curl -X POST http://localhost:5000/api/import-schedule \
  -H "Content-Type: application/json" \
  -d '{
    "filepath": "/schedules/my_schedule.xml",
    "format": "xml"
  }'
```

### Export Schedule
```bash
curl -X POST http://localhost:5000/api/export-schedule-xml \
  -H "Content-Type: application/json" \
  -d '{
    "schedule_id": "abc-123",
    "filename": "exported.xml"
  }'
```

### Create Schedule with Auto-Fill
```bash
curl -X POST http://localhost:5000/api/schedule-playlist \
  -H "Content-Type: application/json" \
  -d '{
    "links": [
      "http://example.com/video1.mp4",
      "http://example.com/video2.mp4"
    ],
    "start_time": "2025-11-23T08:00:00Z",
    "duration_hours": 24,
    "cooldown_hours": 48,
    "shuffle": true
  }'
```

---

## Rate Limiting

Not implemented. No rate limits currently.

---

## CORS

All endpoints allow:
- Origins: `*` (all origins)
- Methods: `GET, POST, OPTIONS, DELETE`
- Headers: `Content-Type`

---

## Caching

All responses include:
```
Cache-Control: no-cache, no-store, must-revalidate
```

This prevents caching of dynamic content.

---

## Timeout

External requests timeout after 10 seconds.

---

## Authentication

**Current Status:** Not implemented  
**Recommendation:** Implement before production use

---

## Version History

**v2.0.0** (Nov 22, 2025)
- Added schedule-playlist endpoint
- Added cooldown support
- Added validation
- Added error handling

---

**Last Updated:** November 22, 2025  
**Status:** Complete
