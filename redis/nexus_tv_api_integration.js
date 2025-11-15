/**
 * NEXUS TV - Redis API Integration
 * 
 * Add this JavaScript to your NEXUS TV HTML to fetch channels from the Redis API
 * This makes NEXUS TV load faster by using cached Redis data
 */

// Configuration
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:3000'
    : `http://${window.location.hostname}:3000`;

/**
 * Fetch channels from Redis API
 */
async function fetchChannelsFromRedis() {
    try {
        console.log('📡 Fetching channels from Redis API...');
        
        const response = await fetch(`${API_BASE_URL}/api/channels`);
        
        if (!response.ok) {
            throw new Error(`API returned ${response.status}`);
        }
        
        const data = await response.json();
        console.log(`✅ Loaded ${data.channels.length} channels from Redis`);
        
        return data.channels;
    } catch (error) {
        console.error('❌ Failed to fetch from Redis API:', error);
        console.log('💡 Falling back to local data...');
        return null; // Fall back to existing channel data
    }
}

/**
 * Fetch channel groups from Redis API
 */
async function fetchGroupsFromRedis() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/groups`);
        
        if (!response.ok) {
            throw new Error(`API returned ${response.status}`);
        }
        
        const data = await response.json();
        console.log(`✅ Loaded ${data.groups.length} groups from Redis`);
        
        return data.groups;
    } catch (error) {
        console.error('❌ Failed to fetch groups:', error);
        return null;
    }
}

/**
 * Check API health
 */
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        console.log('🏥 API Health:', data);
        return data.status === 'healthy';
    } catch (error) {
        console.warn('⚠️  API health check failed:', error);
        return false;
    }
}

/**
 * Initialize NEXUS TV with Redis data
 */
async function initializeWithRedis() {
    // Check if API is available
    const isHealthy = await checkAPIHealth();
    
    if (!isHealthy) {
        console.log('ℹ️  Redis API not available, using local data');
        return false;
    }
    
    // Fetch channels from Redis
    const channels = await fetchChannelsFromRedis();
    
    if (!channels || channels.length === 0) {
        console.log('ℹ️  No channels in Redis, using local data');
        return false;
    }
    
    // Update global channels array if it exists
    if (typeof window.scheduleData !== 'undefined') {
        window.scheduleData = channels;
        console.log('✅ Updated scheduleData with Redis channels');
    }
    
    return true;
}

/**
 * USAGE INSTRUCTIONS:
 * 
 * Add this to your NEXUS TV HTML <head> section:
 * 
 * <script src="nexus_tv_api_integration.js"></script>
 * 
 * Then in your existing JavaScript, call before loading channels:
 * 
 * <script>
 *   // Initialize with Redis
 *   initializeWithRedis().then(success => {
 *     if (success) {
 *       console.log('Using Redis data');
 *     } else {
 *       console.log('Using local JSON data');
 *       // Load from local JSON as fallback
 *     }
 *     
 *     // Continue with your existing NEXUS TV initialization
 *     populateChannelList();
 *     startPlayback();
 *   });
 * </script>
 * 
 * BENEFITS:
 * - ⚡ Faster loading (Redis cache is much faster than JSON files)
 * - 🔄 Real-time updates (channels update when you export from M3U Matrix)
 * - 🌐 Network sharing (both PUNK and Liberty Express use same cache)
 * - 📊 Centralized data (one source of truth for all players)
 * 
 * FALLBACK:
 * - If Redis API is not available, NEXUS TV automatically falls back to local JSON
 * - No errors, seamless degradation
 */

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        fetchChannelsFromRedis,
        fetchGroupsFromRedis,
        checkAPIHealth,
        initializeWithRedis
    };
}
