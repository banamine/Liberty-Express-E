"""
Redis Exporter for M3U Matrix
Automatically exports channel data to Redis cache
"""

import redis
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class RedisExporter:
    """Exports M3U Matrix channel data to Redis"""
    
    def __init__(self, host='localhost', port=6379, password=None):
        """Initialize Redis connection"""
        self.host = host
        self.port = port
        self.password = password
        self.redis_client = None
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to Redis server"""
        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                decode_responses=True,
                socket_connect_timeout=3
            )
            self.redis_client.ping()
            self.connected = True
            logger.info(f"✅ Connected to Redis at {self.host}:{self.port}")
            return True
        except redis.ConnectionError as e:
            logger.warning(f"⚠️  Redis connection failed: {e}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"❌ Redis error: {e}")
            self.connected = False
            return False
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            self.connected = False
            return False
    
    def export_channels(self, channels: List[Dict[str, Any]]) -> bool:
        """
        Export channel list to Redis
        
        Args:
            channels: List of channel dictionaries
            
        Returns:
            bool: True if export successful, False otherwise
        """
        if not self.is_connected():
            if not self.connect():
                return False
        
        try:
            pipe = self.redis_client.pipeline()
            exported_count = 0
            
            for channel in channels:
                channel_id = channel.get('id') or channel.get('uuid') or str(hash(channel.get('name', '')))
                
                # Create metadata hash
                metadata_key = f"channel:{channel_id}:metadata"
                metadata = {
                    'id': channel_id,
                    'name': channel.get('name', 'Unknown'),
                    'url': channel.get('url', ''),
                    'logo': channel.get('logo', ''),
                    'group': channel.get('group', 'Uncategorized'),
                    'tvg_id': channel.get('tvg-id', ''),
                    'tvg_name': channel.get('tvg-name', ''),
                    'duration': str(channel.get('duration', 0)),
                    'start_time': channel.get('start_time', ''),
                    'end_time': channel.get('end_time', ''),
                    'uuid': channel.get('uuid', ''),
                    'exported_at': str(channel.get('exported_at', ''))
                }
                
                # Remove empty values
                metadata = {k: v for k, v in metadata.items() if v}
                
                # Store in Redis
                pipe.delete(metadata_key)
                pipe.hset(metadata_key, mapping=metadata)
                pipe.expire(metadata_key, 86400)  # 24 hour TTL
                
                # Add to group index
                group = channel.get('group', 'Uncategorized')
                group_key = f"group:{group}:channels"
                pipe.sadd(group_key, channel_id)
                pipe.expire(group_key, 86400)
                
                exported_count += 1
            
            # Execute pipeline
            pipe.execute()
            
            # Store export metadata
            export_meta = {
                'total_channels': len(channels),
                'exported_at': json.dumps({'timestamp': str(channels[0].get('exported_at', '')) if channels else ''}),
                'version': '1.0'
            }
            self.redis_client.hset('m3u_matrix:export_meta', mapping=export_meta)
            
            logger.info(f"✅ Exported {exported_count} channels to Redis")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exporting to Redis: {e}")
            return False
    
    def export_epg(self, channel_id: str, epg_data: Dict[str, Any]) -> bool:
        """Export EPG data for a channel"""
        if not self.is_connected():
            if not self.connect():
                return False
        
        try:
            key = f"epg:{channel_id}"
            self.redis_client.set(key, json.dumps(epg_data), ex=86400)
            logger.info(f"✅ Exported EPG for channel {channel_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error exporting EPG: {e}")
            return False
    
    def clear_cache(self) -> bool:
        """Clear all cached channel data"""
        if not self.is_connected():
            if not self.connect():
                return False
        
        try:
            # Delete all channel keys
            for key in self.redis_client.scan_iter("channel:*"):
                self.redis_client.delete(key)
            
            # Delete all group keys
            for key in self.redis_client.scan_iter("group:*"):
                self.redis_client.delete(key)
            
            # Delete all EPG keys
            for key in self.redis_client.scan_iter("epg:*"):
                self.redis_client.delete(key)
            
            # Delete metadata
            self.redis_client.delete('m3u_matrix:export_meta')
            
            logger.info("✅ Cleared Redis cache")
            return True
        except Exception as e:
            logger.error(f"❌ Error clearing cache: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics"""
        if not self.is_connected():
            return {"connected": False}
        
        try:
            channel_count = len(list(self.redis_client.scan_iter("channel:*:metadata")))
            group_count = len(list(self.redis_client.scan_iter("group:*")))
            epg_count = len(list(self.redis_client.scan_iter("epg:*")))
            
            info = self.redis_client.info()
            
            return {
                "connected": True,
                "channels": channel_count,
                "groups": group_count,
                "epg_entries": epg_count,
                "total_keys": self.redis_client.dbsize(),
                "memory_used": info.get('used_memory_human', 'N/A'),
                "uptime": info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {"connected": False, "error": str(e)}
    
    def close(self):
        """Close Redis connection"""
        if self.redis_client:
            try:
                self.redis_client.close()
                logger.info("✅ Closed Redis connection")
            except Exception as e:
                logger.error(f"❌ Error closing Redis: {e}")
            finally:
                self.redis_client = None
                self.connected = False


# Global instance
_redis_exporter = None

def get_redis_exporter(host='localhost', port=6379, password=None) -> RedisExporter:
    """Get or create global Redis exporter instance"""
    global _redis_exporter
    if _redis_exporter is None:
        _redis_exporter = RedisExporter(host, port, password)
    return _redis_exporter
