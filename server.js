const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 5000;
const MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.mp4': 'video/mp4',
    '.mp3': 'audio/mpeg'
};

const server = http.createServer((req, res) => {
    let filePath = path.join(__dirname, req.url === '/' ? 'index.html' : req.url);
    
    // Prevent directory traversal
    const normalized = path.normalize(filePath);
    if (!normalized.startsWith(__dirname)) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
    }

    fs.readFile(filePath, (err, data) => {
        if (err) {
            // Try index.html for directories
            if (fs.existsSync(path.join(filePath, 'index.html'))) {
                filePath = path.join(filePath, 'index.html');
                fs.readFile(filePath, (err, data) => {
                    if (err) {
                        res.writeHead(404);
                        res.end('Not Found');
                        return;
                    }
                    const ext = path.extname(filePath);
                    res.writeHead(200, { 'Content-Type': MIME_TYPES[ext] || 'text/plain' });
                    res.end(data);
                });
            } else {
                res.writeHead(404);
                res.end('Not Found');
            }
            return;
        }

        const ext = path.extname(filePath);
        res.writeHead(200, { 
            'Content-Type': MIME_TYPES[ext] || 'text/plain',
            'Cache-Control': 'no-cache, no-store, must-revalidate'
        });
        res.end(data);
    });
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`ScheduleFlow running at http://0.0.0.0:${PORT}`);
    console.log('All pages served locally. Ready for GitHub Pages deployment.');
});
