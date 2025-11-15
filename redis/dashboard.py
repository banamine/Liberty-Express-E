"""
M3U Matrix - Redis Web Dashboard
Browser-based interface to view cached channel data
"""

import redis
import json
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# Redis connection
def get_redis():
    """Get Redis connection"""
    try:
        r = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True,
            socket_connect_timeout=5
        )
        r.ping()
        return r
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return None


# HTML Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>M3U Matrix - Redis Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        
        h1 {
            color: #667eea;
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #666;
            font-size: 16px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }
        
        .stat-value {
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .stat-label {
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
        }
        
        .content {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        
        .tab {
            padding: 10px 20px;
            background: #f5f5f5;
            border: none;
            border-radius: 8px 8px 0 0;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .tab.active {
            background: #667eea;
            color: white;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .channel-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .channel-card {
            background: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #667eea;
            transition: transform 0.2s;
        }
        
        .channel-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .channel-name {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        
        .channel-info {
            font-size: 14px;
            color: #666;
            margin-bottom: 5px;
        }
        
        .channel-badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            margin-top: 10px;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 20px;
            transition: background 0.3s;
        }
        
        .refresh-btn:hover {
            background: #5568d3;
        }
        
        .search-box {
            width: 100%;
            padding: 12px;
            border: 2px solid #eee;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 20px;
        }
        
        .search-box:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .status-connected {
            color: #28a745;
            font-weight: bold;
        }
        
        .status-disconnected {
            color: #dc3545;
            font-weight: bold;
        }
        
        .json-view {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 M3U Matrix - Redis Dashboard</h1>
            <p class="subtitle">Real-time channel cache monitoring</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="total-channels">-</div>
                <div class="stat-label">Total Channels</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="total-keys">-</div>
                <div class="stat-label">Cached Keys</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="memory-used">-</div>
                <div class="stat-label">Memory Used</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="redis-status">-</div>
                <div class="stat-label">Redis Status</div>
            </div>
        </div>
        
        <div class="content">
            <button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>
            
            <div class="tabs">
                <button class="tab active" onclick="showTab('channels')">Channels</button>
                <button class="tab" onclick="showTab('groups')">Groups</button>
                <button class="tab" onclick="showTab('raw')">Raw Data</button>
            </div>
            
            <div id="channels-tab" class="tab-content active">
                <input type="text" class="search-box" id="search-box" placeholder="🔍 Search channels..." onkeyup="filterChannels()">
                <div id="channels-list" class="channel-grid">
                    <p>Loading channels...</p>
                </div>
            </div>
            
            <div id="groups-tab" class="tab-content">
                <div id="groups-list">
                    <p>Loading groups...</p>
                </div>
            </div>
            
            <div id="raw-tab" class="tab-content">
                <div id="raw-data" class="json-view">
                    <p>Loading raw data...</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let channelsData = [];
        let groupsData = [];
        
        async function loadData() {
            try {
                // Load stats
                const statsRes = await fetch('/api/stats');
                const stats = await statsRes.json();
                
                document.getElementById('total-channels').textContent = stats.channels || 0;
                document.getElementById('total-keys').textContent = stats.total_keys || 0;
                document.getElementById('memory-used').textContent = stats.memory_used || 'N/A';
                
                const statusEl = document.getElementById('redis-status');
                if (stats.status === 'connected') {
                    statusEl.innerHTML = '<span class="status-connected">Connected</span>';
                } else {
                    statusEl.innerHTML = '<span class="status-disconnected">Disconnected</span>';
                }
                
                // Load channels
                const channelsRes = await fetch('/api/channels');
                const channelsJson = await channelsRes.json();
                channelsData = channelsJson.channels || [];
                displayChannels(channelsData);
                
                // Load groups
                const groupsRes = await fetch('/api/groups');
                groupsData = await groupsRes.json();
                displayGroups(groupsData);
                
                // Load raw data
                const rawData = {
                    stats: stats,
                    channels: channelsData,
                    groups: groupsData
                };
                document.getElementById('raw-data').textContent = JSON.stringify(rawData, null, 2);
                
            } catch (error) {
                console.error('Error loading data:', error);
                alert('Failed to load data from Redis. Make sure Redis and API server are running.');
            }
        }
        
        function displayChannels(channels) {
            const container = document.getElementById('channels-list');
            
            if (channels.length === 0) {
                container.innerHTML = '<p>No channels cached yet. Export from M3U Matrix to populate Redis.</p>';
                return;
            }
            
            container.innerHTML = channels.map(channel => `
                <div class="channel-card">
                    <div class="channel-name">${channel.name || 'Unknown Channel'}</div>
                    <div class="channel-info">📺 Group: ${channel.group || 'Uncategorized'}</div>
                    <div class="channel-info">🆔 ID: ${channel.id || 'N/A'}</div>
                    <div class="channel-info">🔗 URL: ${(channel.url || '').substring(0, 50)}...</div>
                    ${channel.logo ? '<div class="channel-badge">Has Logo</div>' : ''}
                </div>
            `).join('');
        }
        
        function displayGroups(data) {
            const container = document.getElementById('groups-list');
            const groups = data.groups || [];
            
            if (groups.length === 0) {
                container.innerHTML = '<p>No groups found.</p>';
                return;
            }
            
            container.innerHTML = groups.map(group => `
                <div class="channel-card">
                    <div class="channel-name">📁 ${group.name}</div>
                    <div class="channel-info">Channels: ${group.channel_count}</div>
                </div>
            `).join('');
        }
        
        function filterChannels() {
            const searchTerm = document.getElementById('search-box').value.toLowerCase();
            const filtered = channelsData.filter(channel => 
                (channel.name || '').toLowerCase().includes(searchTerm) ||
                (channel.group || '').toLowerCase().includes(searchTerm)
            );
            displayChannels(filtered);
        }
        
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
        }
        
        // Load data on page load
        loadData();
        
        // Auto-refresh every 30 seconds
        setInterval(loadData, 30000);
    </script>
</body>
</html>
"""


@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/stats')
def api_stats():
    """Get Redis statistics"""
    r = get_redis()
    if r is None:
        return jsonify({
            "status": "disconnected",
            "channels": 0,
            "total_keys": 0,
            "memory_used": "N/A"
        })
    
    try:
        # Count channels
        channel_keys = list(r.scan_iter(match="channel:*:metadata", count=100))
        channel_count = len(channel_keys)
        
        # Get Redis info
        info = r.info()
        
        return jsonify({
            "status": "connected",
            "channels": channel_count,
            "total_keys": r.dbsize(),
            "memory_used": info.get('used_memory_human', 'N/A'),
            "uptime": info.get('uptime_in_seconds', 0)
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})


@app.route('/api/channels')
def api_channels():
    """Get all channels"""
    r = get_redis()
    if r is None:
        return jsonify({"channels": []})
    
    try:
        channel_keys = list(r.scan_iter(match="channel:*:metadata", count=100))
        channels = []
        
        for key in channel_keys:
            channel_data = r.hgetall(key)
            if channel_data:
                channels.append(channel_data)
        
        return jsonify({"channels": channels})
    except Exception as e:
        return jsonify({"error": str(e), "channels": []})


@app.route('/api/groups')
def api_groups():
    """Get all groups"""
    r = get_redis()
    if r is None:
        return jsonify({"groups": []})
    
    try:
        channel_keys = list(r.scan_iter(match="channel:*:metadata", count=100))
        groups = {}
        
        for key in channel_keys:
            channel_data = r.hgetall(key)
            group = channel_data.get('group', 'Uncategorized')
            
            if group not in groups:
                groups[group] = {
                    "name": group,
                    "channel_count": 0
                }
            
            groups[group]["channel_count"] += 1
        
        return jsonify({"groups": list(groups.values())})
    except Exception as e:
        return jsonify({"error": str(e), "groups": []})


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  M3U MATRIX - Redis Dashboard")
    print("="*70)
    print("\n🚀 Starting dashboard...")
    print(f"🌐 Dashboard will be available at: http://localhost:8080")
    print(f"💾 Redis connection: localhost:6379")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=8080, debug=False)
