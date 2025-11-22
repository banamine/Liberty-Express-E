const express = require('express');
const https = require('https');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 5000;

// Enable CORS for API endpoints
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  next();
});

// Middleware to serve .html files when no extension is provided
app.use((req, res, next) => {
  if (!path.extname(req.path)) {
    // Try to serve as .html if no extension
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
