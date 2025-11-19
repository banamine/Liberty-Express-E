"""
M3U Matrix - FastAPI Backend Server
Provides REST API for NEXUS TV to access Redis-cached channel data
"""

import os
import json
import redis
from datetime import datetime
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Initialize FastAPI
app = FastAPI(
    title="M3U Matrix API",
    description="Redis-backed API for IPTV channel management",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_client = None

def get_redis():
    """Get or create Redis connection"""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.Redis(
                host='localhost',
                port=6379,
                decode_responses=True,
                socket_connect_timeout=5
            )
            redis_client.ping()
            print("✅ Connected to Redis")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            redis_client = None
    return redis_client


@app.on_event("startup")
async def startup_event():
    """Initialize Redis connection on startup"""
    get_redis()


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "M3U Matrix API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "channels": "/api/channels",
            "channel_detail": "/api/channels/{channel_id}",
            "groups": "/api/groups",
            "epg": "/api/epg/{channel_id}",
            "stats": "/api/stats"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    r = get_redis()
    
    if r is None:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "redis": "disconnected",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    try:
        r.ping()
        db_size = r.dbsize()
        return {
            "status": "healthy",
            "redis": "connected",
            "cached_keys": db_size,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "redis": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.get("/api/channels")
async def get_channels(
    group: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """Get all channels or filter by group"""
    r = get_redis()
    if r is None:
        raise HTTPException(status_code=503, detail="Redis unavailable")
    
    try:
        # Get all channel keys
        pattern = "channel:*" if group is None else f"channel:*:group:{group}"
        channel_keys = list(r.scan_iter(match="channel:*:metadata", count=100))
        
        # Apply pagination
        total = len(channel_keys)
        channel_keys = channel_keys[offset:offset + limit]
        
        channels = []
        for key in channel_keys:
            try:
                channel_data = r.hgetall(key)
                if channel_data:
                    # Filter by group if specified
                    if group is None or channel_data.get('group', '').lower() == group.lower():
                        channels.append(channel_data)
            except Exception as e:
                print(f"Error reading channel {key}: {e}")
                continue
        
        return {
            "channels": channels,
            "total": total,
            "limit": limit,
            "offset": offset,
            "count": len(channels)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching channels: {str(e)}")


@app.get("/api/channels/{channel_id}")
async def get_channel(channel_id: str):
    """Get specific channel details"""
    r = get_redis()
    if r is None:
        raise HTTPException(status_code=503, detail="Redis unavailable")
    
    try:
        # Try to get channel metadata
        key = f"channel:{channel_id}:metadata"
        channel_data = r.hgetall(key)
        
        if not channel_data:
            raise HTTPException(status_code=404, detail=f"Channel {channel_id} not found")
        
        return channel_data
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching channel: {str(e)}")


@app.get("/api/groups")
async def get_groups():
    """Get all channel groups"""
    r = get_redis()
    if r is None:
        raise HTTPException(status_code=503, detail="Redis unavailable")
    
    try:
        # Get all channel keys and extract unique groups
        channel_keys = list(r.scan_iter(match="channel:*:metadata", count=100))
        
        groups = {}
        for key in channel_keys:
            try:
                channel_data = r.hgetall(key)
                group = channel_data.get('group', 'Uncategorized')
                
                if group not in groups:
                    groups[group] = {
                        "name": group,
                        "channel_count": 0,
                        "channels": []
                    }
                
                groups[group]["channel_count"] += 1
                groups[group]["channels"].append({
                    "id": channel_data.get('id'),
                    "name": channel_data.get('name')
                })
            except Exception:
                continue
        
        return {
            "groups": list(groups.values()),
            "total_groups": len(groups)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching groups: {str(e)}")


@app.get("/api/epg/{channel_id}")
async def get_epg(channel_id: str):
    """Get EPG data for a channel"""
    r = get_redis()
    if r is None:
        raise HTTPException(status_code=503, detail="Redis unavailable")
    
    try:
        # Get EPG data from Redis
        key = f"epg:{channel_id}"
        epg_data = r.get(key)
        
        if epg_data is None:
            return {
                "channel_id": channel_id,
                "epg": None,
                "message": "No EPG data available"
            }
        
        return {
            "channel_id": channel_id,
            "epg": json.loads(epg_data)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching EPG: {str(e)}")


@app.get("/api/stats")
async def get_stats():
    """Get Redis cache statistics"""
    r = get_redis()
    if r is None:
        raise HTTPException(status_code=503, detail="Redis unavailable")
    
    try:
        # Count different types of keys
        channel_count = len(list(r.scan_iter(match="channel:*:metadata", count=100)))
        epg_count = len(list(r.scan_iter(match="epg:*", count=100)))
        
        # Get Redis info
        info = r.info()
        
        return {
            "channels": channel_count,
            "epg_entries": epg_count,
            "total_keys": r.dbsize(),
            "memory_used": info.get('used_memory_human', 'N/A'),
            "uptime_seconds": info.get('uptime_in_seconds', 0),
            "connected_clients": info.get('connected_clients', 0)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@app.post("/api/clear-cache")
async def clear_cache():
    """Clear all cached data"""
    r = get_redis()
    if r is None:
        raise HTTPException(status_code=503, detail="Redis unavailable")
    
    try:
        r.flushdb()
        return {
            "status": "success",
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  M3U MATRIX - FastAPI Backend Server")
    print("="*70)
    print("\n🚀 Starting server...")
    print(f"📡 API will be available at: http://localhost:3000")
    print(f"📖 API docs at: http://localhost:3000/docs")
    print(f"💾 Redis connection: localhost:6379")
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3000,
        log_level="info"
    )
