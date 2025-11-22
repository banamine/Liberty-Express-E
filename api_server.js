const express = require('express');
const https = require('https');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(express.json());
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  res.header('Cache-Control', 'no-cache, no-store, must-revalidate');
  next();
});

// Middleware to serve .html files when no extension is provided
app.use((req, res, next) => {
  if (!path.extname(req.path)) {
    const htmlPath = path.join(__dirname, 'generated_pages', req.path + '.html');
    if (fs.existsSync(htmlPath)) {
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

// ========== SCHEDULEFLOW API ENDPOINTS ==========

// Get system info
app.get('/api/system-info', (req, res) => {
  try {
    const pagesDir = path.join(__dirname, 'generated_pages');
    let pageCount = 0;
    if (fs.existsSync(pagesDir)) {
      pageCount = fs.readdirSync(pagesDir).filter(f => f.endsWith('.html')).length;
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

// List all generated pages
app.get('/api/pages', (req, res) => {
  try {
    const pagesDir = path.join(__dirname, 'generated_pages');
    const pages = [];
    
    if (fs.existsSync(pagesDir)) {
      fs.readdirSync(pagesDir).forEach(file => {
        if (file.endsWith('.html')) {
          const filePath = path.join(pagesDir, file);
          const stat = fs.statSync(filePath);
          pages.push({
            name: file,
            path: `/generated_pages/${file}`,
            size: stat.size,
            modified: stat.mtime.toISOString()
          });
        }
      });
    }
    
    res.json({ status: 'success', pages, count: pages.length });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Save a new playlist to file
app.post('/api/save-playlist', (req, res) => {
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
    fs.writeFileSync(filepath, m3uContent);
    
    res.json({ status: 'success', path: filepath, items: items.length });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Get configuration
app.get('/api/config', (req, res) => {
  try {
    const configPath = path.join(__dirname, 'm3u_matrix_settings.json');
    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      res.json({ status: 'success', config });
    } else {
      res.json({ status: 'success', config: { playlists: [], schedules: [] } });
    }
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Save configuration
app.post('/api/config', (req, res) => {
  try {
    const configPath = path.join(__dirname, 'm3u_matrix_settings.json');
    fs.writeFileSync(configPath, JSON.stringify(req.body, null, 2));
    res.json({ status: 'success', message: 'Configuration saved' });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Import schedule from file (triggers Python backend)
app.post('/api/import-schedule', (req, res) => {
  try {
    const { filepath, format } = req.body;
    if (!filepath || !format) {
      return res.status(400).json({ status: 'error', message: 'Missing filepath or format' });
    }
    
    // Call Python script to import schedule
    const args = format === 'xml' 
      ? ['M3U_Matrix_Pro.py', '--import-schedule-xml', filepath]
      : ['M3U_Matrix_Pro.py', '--import-schedule-json', filepath];
    
    const python = spawn('python3', args);
    let output = '';
    let errorOutput = '';
    
    python.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    python.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });
    
    python.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(output);
          res.json(result);
        } catch (e) {
          res.status(500).json({ status: 'error', message: 'Invalid JSON from Python: ' + output });
        }
      } else {
        res.status(500).json({ status: 'error', message: 'Import failed: ' + errorOutput });
      }
    });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Get schedules list
app.get('/api/schedules', (req, res) => {
  try {
    const python = spawn('python3', ['M3U_Matrix_Pro.py', '--list-schedules']);
    let output = '';
    
    python.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    python.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(output);
          res.json(result);
        } catch (e) {
          res.status(500).json({ status: 'error', message: 'Failed to parse schedules' });
        }
      } else {
        res.status(500).json({ status: 'error', message: 'Failed to get schedules' });
      }
    });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Get playlists list
app.get('/api/playlists', (req, res) => {
  try {
    const python = spawn('python3', ['M3U_Matrix_Pro.py', '--list-playlists']);
    let output = '';
    
    python.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    python.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(output);
          res.json(result);
        } catch (e) {
          res.status(500).json({ status: 'error', message: 'Failed to parse playlists' });
        }
      } else {
        res.status(500).json({ status: 'error', message: 'Failed to get playlists' });
      }
    });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Export schedule to XML
app.post('/api/export-schedule-xml', (req, res) => {
  try {
    const { schedule_id, filename } = req.body;
    if (!schedule_id) {
      return res.status(400).json({ status: 'error', message: 'Missing schedule_id' });
    }
    
    const outputFile = path.join(__dirname, filename || `schedule_${schedule_id}.xml`);
    const python = spawn('python3', ['M3U_Matrix_Pro.py', '--export-schedule-xml', schedule_id, outputFile]);
    let output = '';
    
    python.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    python.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(output);
          res.json(result);
        } catch (e) {
          res.status(500).json({ status: 'error', message: 'Failed to parse export result' });
        }
      } else {
        res.status(500).json({ status: 'error', message: 'Export failed' });
      }
    });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Export schedule to JSON
app.post('/api/export-schedule-json', (req, res) => {
  try {
    const { schedule_id, filename } = req.body;
    if (!schedule_id) {
      return res.status(400).json({ status: 'error', message: 'Missing schedule_id' });
    }
    
    const outputFile = path.join(__dirname, filename || `schedule_${schedule_id}.json`);
    const python = spawn('python3', ['M3U_Matrix_Pro.py', '--export-schedule-json', schedule_id, outputFile]);
    let output = '';
    
    python.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    python.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(output);
          res.json(result);
        } catch (e) {
          res.status(500).json({ status: 'error', message: 'Failed to parse export result' });
        }
      } else {
        res.status(500).json({ status: 'error', message: 'Export failed' });
      }
    });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Export all schedules to XML
app.post('/api/export-all-schedules-xml', (req, res) => {
  try {
    const filename = req.body.filename || 'all_schedules.xml';
    const outputFile = path.join(__dirname, filename);
    const python = spawn('python3', ['M3U_Matrix_Pro.py', '--export-all-xml', outputFile]);
    let output = '';
    
    python.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    python.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(output);
          res.json(result);
        } catch (e) {
          res.status(500).json({ status: 'error', message: 'Failed to parse export result' });
        }
      } else {
        res.status(500).json({ status: 'error', message: 'Export failed' });
      }
    });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// API endpoint to fetch real Infowars videos
app.get('/api/infowars-videos', (req, res) => {
  try {
    // Use Python script to fetch videos
    const python = spawn('python3', ['infowars_fetcher.py']);
    let output = '';
    let errorOutput = '';

    python.stdout.on('data', (data) => {
      output += data.toString();
    });

    python.stderr.on('data', (data) => {
      errorOutput += data.toString();
      console.error('Python stderr:', data.toString());
    });

    python.on('close', (code) => {
      if (code === 0) {
        try {
          // Find JSON in output (skip print statements)
          const jsonMatch = output.match(/\{[\s\S]*\}/);
          if (jsonMatch) {
            const data = JSON.parse(jsonMatch[0]);
            res.json(data);
          } else {
            res.status(500).json({
              success: false,
              error: 'Could not parse Python output',
              timestamp: new Date().toISOString()
            });
          }
        } catch (e) {
          console.error('JSON parse error:', e);
          res.status(500).json({
            success: false,
            error: 'Invalid JSON response from Python',
            timestamp: new Date().toISOString()
          });
        }
      } else {
        console.error('Python script failed with code:', code, 'Error:', errorOutput);
        res.status(500).json({
          success: false,
          error: 'Python script error: ' + errorOutput,
          timestamp: new Date().toISOString()
        });
      }
    });

  } catch (error) {
    console.error('Error setting up Infowars video fetch:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
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
  
  // If path includes /generated_pages/ prefix, remove it
  if (req.path.startsWith('/generated_pages/')) {
    const cleanPath = req.path.substring('/generated_pages'.length); // Remove /generated_pages, keep the /
    filePath = path.join(__dirname, 'generated_pages', cleanPath.substring(1) + '.html'); // Remove leading /
  } else {
    filePath = path.join(__dirname, 'generated_pages', req.path.substring(1) + '.html'); // Remove leading /
  }
  
  if (fs.existsSync(filePath)) {
    return res.sendFile(filePath);
  }
  
  // Not found
  res.status(404).json({ error: 'Not found' });
});

const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`
╔════════════════════════════════════════════════╗
║   ScheduleFlow API Server Running              ║
║                                                ║
║   API Endpoint:                                ║
║   http://localhost:${PORT}/api/infowars-videos  ║
║                                                ║
║   Static Files:                                ║
║   http://localhost:${PORT}/generated_pages/    ║
╚════════════════════════════════════════════════╝
  `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  server.close(() => {
    console.log('Server terminated');
    process.exit(0);
  });
});
