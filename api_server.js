require('dotenv').config();

const express = require('express');
const https = require('https');
const path = require('path');
const fs = require('fs').promises;
const fsSync = require('fs');  // Keep for existsSync only
const TaskQueue = require('./task_queue');
const rateLimit = require('express-rate-limit');

const app = express();
const PORT = process.env.PORT || 5000;
const ADMIN_API_KEY = process.env.ADMIN_API_KEY || 'change_me_to_your_secret_key';
const MAX_UPLOAD_SIZE = parseInt(process.env.MAX_UPLOAD_SIZE || '52428800');

// API request logging middleware
app.use((req, res, next) => {
  const startTime = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - startTime;
    const logLevel = res.statusCode >= 400 ? 'error' : 'info';
    console.log(`[${logLevel.toUpperCase()}] ${req.method} ${req.path} - ${res.statusCode} (${duration}ms)`);
  });
  next();
});

// Process pool: limit concurrent Python processes to 4 (prevents OOM)
const pythonQueue = new TaskQueue(4);

// Rate limiting middleware
const limiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute window
  max: 100, // 100 requests per window
  message: 'Too many requests from this IP, please try again later',
  standardHeaders: true,
  legacyHeaders: false
});

// Middleware
app.use(express.json({ limit: '50mb' }));

// JSON error handler - prevent stack trace leakage
app.use((err, req, res, next) => {
  if (err instanceof SyntaxError && 'body' in err) {
    return res.status(400).json({
      status: 'error',
      type: 'json_parse_error',
      message: 'Invalid JSON format',
      hint: 'Check JSON syntax: missing commas, unquoted keys, or trailing commas'
    });
  }
  next(err);
});

// Apply rate limiting to all API routes
app.use('/api/', limiter);

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.header('Cache-Control', 'no-cache, no-store, must-revalidate');
  next();
});

// ========== SECURITY MIDDLEWARE ==========

// Admin API key validation middleware
const validateAdminKey = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) {
    return res.status(401).json({ 
      status: 'error', 
      message: 'Missing Authorization header. Use: Authorization: Bearer YOUR_API_KEY' 
    });
  }

  const parts = authHeader.split(' ');
  if (parts.length !== 2 || parts[0] !== 'Bearer') {
    return res.status(401).json({ 
      status: 'error', 
      message: 'Invalid Authorization format. Use: Bearer YOUR_API_KEY' 
    });
  }

  const apiKey = parts[1];
  if (apiKey !== ADMIN_API_KEY) {
    return res.status(401).json({ 
      status: 'error', 
      message: 'Unauthorized: Invalid API key' 
    });
  }

  next();
};

// File size limit middleware
const checkFileSize = (req, res, next) => {
  if (req.file && req.file.size > MAX_UPLOAD_SIZE) {
    return res.status(413).json({
      status: 'error',
      message: `File too large. Maximum size: ${(MAX_UPLOAD_SIZE / 1024 / 1024).toFixed(2)}MB`
    });
  }
  if (req.body && typeof req.body === 'string' && req.body.length > MAX_UPLOAD_SIZE) {
    return res.status(413).json({
      status: 'error',
      message: `Content too large. Maximum size: ${(MAX_UPLOAD_SIZE / 1024 / 1024).toFixed(2)}MB`
    });
  }
  next();
};

// Middleware to serve .html files when no extension is provided
app.use((req, res, next) => {
  if (!path.extname(req.path)) {
    const htmlPath = path.join(__dirname, 'generated_pages', req.path + '.html');
    if (fsSync.existsSync(htmlPath)) {
      return res.sendFile(htmlPath);
    }
  }
  next();
});

// Serve static files from generated_pages at /generated_pages route
app.use('/generated_pages', express.static('generated_pages'));

// Serve static files from M3U_Matrix_Output
app.use('/M3U_Matrix_Output', express.static('M3U_Matrix_Output'));

// Also serve from root for compatibility
app.use(express.static('generated_pages'));

// Helper function to fetch HTTPS content
function fetchHttp(url) {
  return new Promise((resolve, reject) => {
    const request = https.get(url, (response) => {
      let data = '';

      response.on('data', (chunk) => {
        data += chunk;
      });

      response.on('end', () => {
        if (response.statusCode >= 200 && response.statusCode < 300) {
          resolve(data);
        } else {
          reject(new Error(`HTTP ${response.statusCode}`));
        }
      });
    });

    request.on('error', (error) => {
      reject(error);
    });

    request.setTimeout(10000, () => {
      request.abort();
      reject(new Error('Request timeout'));
    });
  });
}


// ========== SCHEDULEFLOW API ENDPOINTS (All Async) ==========

// Get system info (FIXED: async directory read)
app.get('/api/system-info', async (req, res) => {
  try {
    const pagesDir = path.join(__dirname, 'generated_pages');
    let pageCount = 0;
    
    if (fsSync.existsSync(pagesDir)) {
      const files = await fs.readdir(pagesDir);
      pageCount = files.filter(f => f.endsWith('.html')).length;
    }
    
    res.json({
      status: 'success',
      version: '2.0.0',
      platform: 'Web & Desktop',
      pages_generated: pageCount,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// System version endpoint
app.get('/api/system-version', (req, res) => {
  res.json({
    status: 'success',
    current_version: '2.0.0',
    release_date: '2025-11-23',
    api_version: '2.0',
    environment: 'production',
    features: [
      'schedule_import',
      'schedule_export',
      'cooldown_tracking',
      'conflict_detection',
      'auto_play'
    ]
  });
});

// Version check endpoint - check GitHub for latest release
app.get('/api/version-check', async (req, res) => {
  try {
    // For now, return mock data (Phase 2.1 will add real GitHub API)
    // In production, this would call: https://api.github.com/repos/owner/repo/releases/latest
    res.json({
      status: 'success',
      current_version: '2.0.0',
      latest_version: '2.1.0',
      has_update: true,
      release_notes: 'Version 2.1.0 includes version-check endpoint, update UI, and auto-webhook support',
      release_date: '2025-12-01',
      download_url: 'https://github.com/your-repo/releases/tag/v2.1.0'
    });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Update from GitHub endpoint - admin only
app.post('/api/update-from-github', validateAdminKey, async (req, res) => {
  try {
    console.log('[Update] Starting update from GitHub');
    
    // Phase 2: Execute actual git pull + npm install + restart
    // For Phase 1 testing, we'll simulate the process
    
    res.json({
      status: 'success',
      message: 'Update process started',
      from_version: '2.0.0',
      to_version: '2.1.0',
      timestamp: new Date().toISOString(),
      notes: 'System will restart in 30 seconds to complete update'
    });
    
    // In production Phase 2, schedule restart:
    // setTimeout(() => { server.close(); process.exit(0); }, 30000);
  } catch (error) {
    res.status(500).json({ 
      status: 'error', 
      message: error.message 
    });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  const stats = pythonQueue.getStats();
  const healthStatus = {
    status: stats.activeProcesses < stats.maxConcurrency ? 'healthy' : 'degraded',
    uptime_ms: process.uptime() * 1000,
    timestamp: new Date().toISOString(),
    process_pool: {
      active: stats.activeProcesses,
      max: stats.maxConcurrency,
      utilization_percent: stats.utilizationPercent,
      queued: stats.queuedTasks
    }
  };
  
  const statusCode = healthStatus.status === 'healthy' ? 200 : 503;
  res.status(statusCode).json(healthStatus);
});

// Queue statistics endpoint
app.get('/api/queue-stats', (req, res) => {
  const stats = pythonQueue.getStats();
  res.json({
    status: 'success',
    queue: {
      active_processes: stats.activeProcesses,
      queued_tasks: stats.queuedTasks,
      max_concurrency: stats.maxConcurrency,
      utilization_percent: stats.utilizationPercent
    },
    statistics: {
      total_processed: stats.totalProcessed,
      total_queued: stats.totalQueued,
      total_errors: stats.totalErrors,
      peak_active: stats.peakActive,
      peak_queue_size: stats.peakQueueSize
    },
    timestamp: new Date().toISOString()
  });
});

// List all generated pages (FIXED: async directory/stat read)
app.get('/api/pages', async (req, res) => {
  try {
    const pagesDir = path.join(__dirname, 'generated_pages');
    const pages = [];
    
    if (fsSync.existsSync(pagesDir)) {
      const files = await fs.readdir(pagesDir);
      
      for (const file of files) {
        if (file.endsWith('.html')) {
          const filePath = path.join(pagesDir, file);
          const stat = await fs.stat(filePath);
          pages.push({
            name: file,
            path: `/generated_pages/${file}`,
            size: stat.size,
            modified: stat.mtime.toISOString()
          });
        }
      }
    }
    
    res.json({ status: 'success', pages, count: pages.length });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Save a new playlist to file (FIXED: async write)
app.post('/api/save-playlist', async (req, res) => {
  try {
    const { filename, items } = req.body;
    if (!filename || !items) {
      return res.status(400).json({ status: 'error', message: 'Missing filename or items' });
    }
    
    let m3uContent = '#EXTM3U\n';
    items.forEach(item => {
      m3uContent += `#EXTINF:-1,${item.label || 'Item'}\n${item.url}\n`;
    });
    
    const filepath = path.join(__dirname, `${filename}.m3u`);
    await fs.writeFile(filepath, m3uContent);
    
    res.json({ status: 'success', path: filepath, items: items.length });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Get configuration (FIXED: async read)
app.get('/api/config', async (req, res) => {
  try {
    const configPath = path.join(__dirname, 'm3u_matrix_settings.json');
    if (fsSync.existsSync(configPath)) {
      const configData = await fs.readFile(configPath, 'utf8');
      const config = JSON.parse(configData);
      res.json({ status: 'success', config });
    } else {
      res.json({ status: 'success', config: { playlists: [], schedules: [] } });
    }
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Save configuration (FIXED: async write)
app.post('/api/config', async (req, res) => {
  try {
    const configPath = path.join(__dirname, 'm3u_matrix_settings.json');
    await fs.writeFile(configPath, JSON.stringify(req.body, null, 2));
    res.json({ status: 'success', message: 'Configuration saved' });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Import schedule from file (triggers Python backend) - with size limit check
app.post('/api/import-schedule', checkFileSize, async (req, res) => {
  try {
    const { filepath, format } = req.body;
    if (!filepath || !format) {
      return res.status(400).json({ status: 'error', message: 'Missing filepath or format' });
    }
    
    const args = format === 'xml' 
      ? ['M3U_Matrix_Pro.py', '--import-schedule-xml', filepath]
      : ['M3U_Matrix_Pro.py', '--import-schedule-json', filepath];
    
    const output = await pythonQueue.execute(args);
    const result = JSON.parse(output);
    res.json(result);
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Get schedules list
app.get('/api/schedules', async (req, res) => {
  try {
    const output = await pythonQueue.execute(['M3U_Matrix_Pro.py', '--list-schedules']);
    const result = JSON.parse(output);
    res.json(result);
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Get playlists list
app.get('/api/playlists', async (req, res) => {
  try {
    const output = await pythonQueue.execute(['M3U_Matrix_Pro.py', '--list-playlists']);
    const result = JSON.parse(output);
    res.json(result);
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Export schedule to XML
app.post('/api/export-schedule-xml', async (req, res) => {
  try {
    const { schedule_id, filename } = req.body;
    if (!schedule_id) {
      return res.status(400).json({ status: 'error', message: 'Missing schedule_id' });
    }
    
    const outputFile = path.join(__dirname, filename || `schedule_${schedule_id}.xml`);
    const output = await pythonQueue.execute(['M3U_Matrix_Pro.py', '--export-schedule-xml', schedule_id, outputFile]);
    const result = JSON.parse(output);
    res.json(result);
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Export schedule to JSON
app.post('/api/export-schedule-json', async (req, res) => {
  try {
    const { schedule_id, filename } = req.body;
    if (!schedule_id) {
      return res.status(400).json({ status: 'error', message: 'Missing schedule_id' });
    }
    
    const outputFile = path.join(__dirname, filename || `schedule_${schedule_id}.json`);
    const output = await pythonQueue.execute(['M3U_Matrix_Pro.py', '--export-schedule-json', schedule_id, outputFile]);
    const result = JSON.parse(output);
    res.json(result);
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Export all schedules to XML
app.post('/api/export-all-schedules-xml', async (req, res) => {
  try {
    const filename = req.body.filename || 'all_schedules.xml';
    const outputFile = path.join(__dirname, filename);
    const output = await pythonQueue.execute(['M3U_Matrix_Pro.py', '--export-all-xml', outputFile]);
    const result = JSON.parse(output);
    res.json(result);
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Schedule playlist with auto-fill
app.post('/api/schedule-playlist', async (req, res) => {
  try {
    const { links, start_time, duration_hours, cooldown_hours, shuffle } = req.body;
    
    if (!links || !Array.isArray(links) || links.length === 0) {
      return res.status(400).json({ status: 'error', message: 'No video links provided' });
    }
    if (!start_time) {
      return res.status(400).json({ status: 'error', message: 'Start time required' });
    }
    
    const outputFile = path.join(__dirname, `schedule_${Date.now()}.json`);
    const output = await pythonQueue.execute(['M3U_Matrix_Pro.py', '--schedule-playlist', 
      JSON.stringify(links), start_time, String(duration_hours || 24), outputFile]);
    
    const result = JSON.parse(output);
    res.json(result);
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// API endpoint to fetch external videos
app.get('/api/infowars-videos', async (req, res) => {
  try {
    const output = await pythonQueue.execute(['infowars_fetcher.py']);
    
    // Find JSON in output (skip print statements)
    const jsonMatch = output.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const data = JSON.parse(jsonMatch[0]);
      res.json(data);
    } else {
      res.status(500).json({
        status: 'error',
        error: 'Could not parse Python output'
      });
    }
  } catch (error) {
    res.status(500).json({
      status: 'error',
      error: error.message
    });
  }
});

// Queue statistics endpoint (for monitoring process pool)
app.get('/api/queue-stats', (req, res) => {
  const stats = pythonQueue.getStats();
  res.json({
    status: 'success',
    processPool: stats,
    timestamp: new Date().toISOString()
  });
});

// ========== ADMIN OPERATIONS (Protected with API Key) ==========

// Delete a schedule (ADMIN ONLY)
app.delete('/api/schedule/:id', validateAdminKey, async (req, res) => {
  try {
    const scheduleId = req.params.id;
    
    if (!scheduleId) {
      return res.status(400).json({ 
        status: 'error', 
        message: 'Schedule ID required' 
      });
    }

    const output = await pythonQueue.execute(['M3U_Matrix_Pro.py', '--delete-schedule', scheduleId]);
    const result = JSON.parse(output);
    res.json(result);

  } catch (error) {
    res.status(500).json({ 
      status: 'error', 
      message: error.message 
    });
  }
});

// Delete all schedules (SUPER ADMIN ONLY - requires confirmation)
app.delete('/api/all-schedules', validateAdminKey, async (req, res) => {
  try {
    // Require extra confirmation in body
    if (req.body.confirm !== 'DELETE_ALL_SCHEDULES') {
      return res.status(400).json({
        status: 'error',
        message: 'Confirmation required. Send { "confirm": "DELETE_ALL_SCHEDULES" } in request body'
      });
    }

    const output = await pythonQueue.execute(['M3U_Matrix_Pro.py', '--delete-all-schedules']);
    const result = JSON.parse(output);
    res.json(result);

  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: error.message
    });
  }
});

// Default route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'generated_pages', 'index.html'));
});

// Catch-all handler for .html files (before 404)
app.use((req, res) => {
  let filePath;
  
  if (req.path.startsWith('/generated_pages/')) {
    const cleanPath = req.path.substring('/generated_pages'.length);
    filePath = path.join(__dirname, 'generated_pages', cleanPath.substring(1) + '.html');
  } else {
    filePath = path.join(__dirname, 'generated_pages', req.path.substring(1) + '.html');
  }
  
  if (fsSync.existsSync(filePath)) {
    return res.sendFile(filePath);
  }
  
  res.status(404).json({ error: 'Not found' });
});

// ========== WEEK 1: FastAPI PROXY ENDPOINTS ==========
// These endpoints delegate to the Python FastAPI server (http://localhost:5001)
// This implements the Communication Layer Integration pattern

const axios = require('axios').default;
const PYTHON_API_URL = 'http://localhost:3000';

// Proxy function for FastAPI calls
async function proxyToPythonAPI(req, res, pythonEndpoint) {
  try {
    const response = await axios({
      method: req.method,
      url: `${PYTHON_API_URL}${pythonEndpoint}`,
      data: req.body,
      params: req.query,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    res.json(response.data);
  } catch (error) {
    console.error(`[FastAPI] Error calling ${pythonEndpoint}:`, error.message);
    res.status(error.response?.status || 500).json({
      status: 'error',
      message: 'FastAPI call failed',
      detail: error.message
    });
  }
}

// ===== Python API Endpoints (Proxied) =====

// System version
app.get('/api/system-version', (req, res) => {
  proxyToPythonAPI(req, res, '/api/system-version');
});

// Status
app.get('/api/status', (req, res) => {
  proxyToPythonAPI(req, res, '/api/status');
});

// Channels
app.get('/api/channels', (req, res) => {
  proxyToPythonAPI(req, res, '/api/channels');
});

app.post('/api/channels', (req, res) => {
  proxyToPythonAPI(req, res, '/api/channels');
});

app.post('/api/channels/import', (req, res) => {
  const { file_path } = req.body;
  proxyToPythonAPI(req, res, `/api/channels/import?file_path=${encodeURIComponent(file_path)}`);
});

// Schedule
app.get('/api/schedule', (req, res) => {
  proxyToPythonAPI(req, res, '/api/schedule');
});

app.post('/api/schedule/create', (req, res) => {
  const params = new URLSearchParams();
  if (req.body.show_duration) params.append('show_duration', req.body.show_duration);
  if (req.body.num_days) params.append('num_days', req.body.num_days);
  if (req.body.max_consecutive) params.append('max_consecutive', req.body.max_consecutive);
  proxyToPythonAPI(req, res, `/api/schedule/create?${params}`);
});

// Validation
app.post('/api/validate', (req, res) => {
  proxyToPythonAPI(req, res, '/api/validate');
});

app.get('/api/validate/results', (req, res) => {
  proxyToPythonAPI(req, res, '/api/validate/results');
});

// Export
app.post('/api/export/m3u', (req, res) => {
  const { output_path } = req.body;
  const queryParam = output_path ? `?output_path=${encodeURIComponent(output_path)}` : '';
  proxyToPythonAPI(req, res, `/api/export/m3u${queryParam}`);
});

const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`
╔═══════════════════════════════════════════════════════╗
║   ScheduleFlow API Server Running                    ║
║   ✓ Async I/O: Enabled                               ║
║   ✓ Process Pool: 4 concurrent Python processes      ║
║   ✓ FastAPI Integration: Port 5001                   ║
║                                                       ║
║   API Endpoints:                                     ║
║   • http://localhost:${PORT}/api/system-info         ║
║   • http://localhost:${PORT}/api/queue-stats         ║
║   • http://localhost:${PORT}/api/schedule            ║
║   • http://localhost:${PORT}/api/channels            ║
║   • http://localhost:${PORT}/api/validate            ║
║                                                       ║
║   Static Files:                                      ║
║   • http://localhost:${PORT}/generated_pages/        ║
╚═══════════════════════════════════════════════════════╝
  `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('[Server] Shutting down gracefully...');
  
  // Clear any pending queue tasks
  const cleared = pythonQueue.clearQueue('Server shutting down');
  console.log(`[Server] Cleared ${cleared} pending tasks`);
  
  server.close(() => {
    console.log('[Server] ✓ Terminated gracefully');
    process.exit(0);
  });
});
