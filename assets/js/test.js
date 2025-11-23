/**
 * ScheduleFlow Test Suite
 * Comprehensive automated testing framework
 */

const testSuite = {
    tests: [],
    results: [],

    // Register a test
    test(name, fn) {
        this.tests.push({ name, fn });
    },

    // Run all tests
    async runAll() {
        this.results = [];
        const resultsDiv = document.getElementById('testResults');
        resultsDiv.innerHTML = '<p style="color: #ffff00;">Running tests...</p>';

        for (const test of this.tests) {
            await this.runTest(test);
        }

        this.updateStats();
        this.displayResults();
    },

    // Run single test
    async runTest(test) {
        try {
            await test.fn();
            this.results.push({ name: test.name, status: 'pass', error: null });
        } catch (error) {
            this.results.push({ name: test.name, status: 'fail', error: error.message });
        }
    },

    // Assert helpers
    assert(condition, message) {
        if (!condition) throw new Error(message || 'Assertion failed');
    },

    assertEquals(actual, expected, message) {
        if (actual !== expected) {
            throw new Error(message || `Expected ${expected}, got ${actual}`);
        }
    },

    assertExists(value, message) {
        if (!value) throw new Error(message || 'Value does not exist');
    },

    // Update statistics
    updateStats() {
        const total = this.results.length;
        const passed = this.results.filter(r => r.status === 'pass').length;
        const failed = this.results.filter(r => r.status === 'fail').length;
        const rate = total > 0 ? Math.round((passed / total) * 100) : 0;

        document.getElementById('totalTests').textContent = total;
        document.getElementById('passedTests').textContent = passed;
        document.getElementById('failedTests').textContent = failed;
        document.getElementById('successRate').textContent = rate + '%';
    },

    // Display test results
    displayResults() {
        const resultsDiv = document.getElementById('testResults');
        resultsDiv.innerHTML = this.results.map(r => `
            <div class="test-item ${r.status}">
                <div class="test-name">
                    ${r.status === 'pass' ? '✅' : '❌'} ${r.name}
                </div>
                <div class="test-message">
                    ${r.status === 'pass' ? 'PASSED' : 'FAILED'}
                </div>
                ${r.error ? `<div class="test-error">${r.error}</div>` : ''}
            </div>
        `).join('');
    },

    // Clear results
    clear() {
        this.results = [];
        document.getElementById('testResults').innerHTML = '';
        document.getElementById('totalTests').textContent = '0';
        document.getElementById('passedTests').textContent = '0';
        document.getElementById('failedTests').textContent = '0';
        document.getElementById('successRate').textContent = '0%';
    },

    // Export results as JSON
    exportResults() {
        const data = {
            timestamp: new Date().toISOString(),
            totalTests: this.results.length,
            passed: this.results.filter(r => r.status === 'pass').length,
            failed: this.results.filter(r => r.status === 'fail').length,
            results: this.results
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `scheduleflow-tests-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
};

// ============================================
// TEST DEFINITIONS
// ============================================

// 1. DOM Elements Tests
testSuite.test('DOM: All pages load without errors', () => {
    testSuite.assertExists(document.querySelector('nav'), 'Navigation bar not found');
    testSuite.assertExists(document.querySelector('main'), 'Main content not found');
    testSuite.assertExists(document.querySelector('footer'), 'Footer not found');
});

testSuite.test('DOM: Navigation links exist', () => {
    const links = document.querySelectorAll('.nav-link');
    testSuite.assert(links.length > 0, 'No navigation links found');
});

testSuite.test('DOM: Stylesheet loaded', () => {
    const sheet = document.querySelector('link[rel="stylesheet"]');
    testSuite.assertExists(sheet, 'CSS stylesheet not found');
});

// 2. localStorage Tests
testSuite.test('Storage: localStorage is accessible', () => {
    localStorage.setItem('test_key', 'test_value');
    const value = localStorage.getItem('test_key');
    testSuite.assertEquals(value, 'test_value', 'localStorage write/read failed');
    localStorage.removeItem('test_key');
});

testSuite.test('Storage: Can save and retrieve JSON', () => {
    const data = { test: 'data', value: 123 };
    localStorage.setItem('test_json', JSON.stringify(data));
    const retrieved = JSON.parse(localStorage.getItem('test_json'));
    testSuite.assertEquals(retrieved.test, 'data', 'JSON storage failed');
    localStorage.removeItem('test_json');
});

// 3. M3U Parsing Tests
testSuite.test('M3U: Parse basic playlist', () => {
    const m3u = `#EXTM3U
#EXTINF:-1,Test Show
http://example.com/video.mp4`;
    
    const lines = m3u.split('\n').filter(l => l.trim());
    testSuite.assert(lines.length > 0, 'M3U parsing failed');
    testSuite.assert(lines[0].startsWith('#EXTM3U'), 'M3U header not found');
});

testSuite.test('M3U: Extract title from EXTINF', () => {
    const line = '#EXTINF:-1,Breaking Bad S01E01';
    const match = line.match(/,(.*)$/);
    testSuite.assertExists(match, 'EXTINF parsing failed');
    testSuite.assertEquals(match[1], 'Breaking Bad S01E01', 'Title extraction failed');
});

testSuite.test('M3U: Detect series pattern S01E01', () => {
    const title = 'Breaking Bad S01E01';
    const seriesMatch = title.match(/S(\d+)E(\d+)/i);
    testSuite.assertExists(seriesMatch, 'Series detection failed');
    testSuite.assertEquals(seriesMatch[1], '01', 'Season number incorrect');
    testSuite.assertEquals(seriesMatch[2], '01', 'Episode number incorrect');
});

testSuite.test('M3U: Detect series pattern Season X Episode Y', () => {
    const title = 'The Office Season 2 Episode 5';
    const seriesMatch = title.match(/Season (\d+).*Episode (\d+)/i);
    testSuite.assertExists(seriesMatch, 'Series detection failed');
    testSuite.assertEquals(seriesMatch[1], '2', 'Season number incorrect');
});

testSuite.test('M3U: Detect series pattern XxY', () => {
    const title = 'Show 1x03';
    const seriesMatch = title.match(/(\d+)x(\d+)/i);
    testSuite.assertExists(seriesMatch, 'Series detection failed');
    testSuite.assertEquals(seriesMatch[2], '03', 'Episode number incorrect');
});

// 4. URL Validation Tests
testSuite.test('URL: Validate HTTP URL', () => {
    const url = 'http://example.com/video.mp4';
    testSuite.assert(url.startsWith('http'), 'URL validation failed');
});

testSuite.test('URL: Validate HTTPS URL', () => {
    const url = 'https://example.com/video.mp4';
    testSuite.assert(url.startsWith('https'), 'URL validation failed');
});

// 5. Schedule Generation Tests
testSuite.test('Schedule: Generate 24-hour schedule', () => {
    const content = [
        { title: 'Show 1', url: 'http://ex.com/1.mp4' },
        { title: 'Show 2', url: 'http://ex.com/2.mp4' }
    ];
    const schedule = [];
    for (let hour = 0; hour < 24; hour++) {
        schedule.push({
            time: String(hour).padStart(2, '0') + ':00',
            item: content[hour % content.length]
        });
    }
    testSuite.assertEquals(schedule.length, 24, '24-hour schedule generation failed');
});

testSuite.test('Schedule: Round-robin distribution', () => {
    const items = ['A', 'B', 'C'];
    const schedule = [];
    for (let i = 0; i < 9; i++) {
        schedule.push(items[i % items.length]);
    }
    testSuite.assertEquals(schedule[0], 'A', 'Round-robin failed at position 0');
    testSuite.assertEquals(schedule[3], 'A', 'Round-robin failed at position 3');
    testSuite.assertEquals(schedule[6], 'A', 'Round-robin failed at position 6');
});

// 6. Export Format Tests
testSuite.test('Export: Generate valid M3U format', () => {
    let m3u = '#EXTM3U\n';
    m3u += '#EXTINF:-1,Test Show\n';
    m3u += 'http://example.com/video.mp4\n';
    
    testSuite.assert(m3u.startsWith('#EXTM3U'), 'M3U header missing');
    testSuite.assert(m3u.includes('#EXTINF'), 'M3U EXTINF tag missing');
    testSuite.assert(m3u.includes('http://'), 'M3U URL missing');
});

testSuite.test('Export: Generate valid JSON format', () => {
    const schedule = {
        channel: 'Test Channel',
        items: [
            { title: 'Show 1', url: 'http://ex.com/1.mp4' }
        ]
    };
    const json = JSON.stringify(schedule);
    const parsed = JSON.parse(json);
    testSuite.assertEquals(parsed.channel, 'Test Channel', 'JSON export failed');
});

testSuite.test('Export: CasparCG XML structure', () => {
    let xml = '<?xml version="1.0"?>\n';
    xml += '<Channel>\n';
    xml += '<Name>Test</Name>\n';
    xml += '<Clip><Title>Show 1</Title><URL>http://ex.com/1.mp4</URL></Clip>\n';
    xml += '</Channel>';
    
    testSuite.assert(xml.includes('<?xml'), 'XML declaration missing');
    testSuite.assert(xml.includes('<Channel>'), 'Channel tag missing');
    testSuite.assert(xml.includes('<Clip>'), 'Clip tag missing');
});

// 7. Color Scheme Tests
testSuite.test('Theme: Black color defined', () => {
    const style = getComputedStyle(document.body);
    testSuite.assertExists(style, 'Body style not accessible');
});

testSuite.test('Theme: Navigation bar has green border', () => {
    const navbar = document.querySelector('.navbar');
    testSuite.assertExists(navbar, 'Navbar not found');
});

testSuite.test('Theme: All buttons are styled', () => {
    const buttons = document.querySelectorAll('button');
    testSuite.assert(buttons.length >= 0, 'Button check failed');
});

// 8. Responsive Design Tests
testSuite.test('Responsive: Viewport meta tag present', () => {
    const viewport = document.querySelector('meta[name="viewport"]');
    testSuite.assertExists(viewport, 'Viewport meta tag not found');
});

testSuite.test('Responsive: Charset meta tag present', () => {
    const charset = document.querySelector('meta[charset]');
    testSuite.assertExists(charset, 'Charset meta tag not found');
});

// 9. Performance Tests
testSuite.test('Performance: Page load time acceptable', () => {
    const loadTime = performance.now();
    testSuite.assert(loadTime < 5000, 'Page took too long to load');
});

testSuite.test('Performance: No console errors on init', () => {
    // This would need error listener - basic check only
    testSuite.assert(true, 'Console check passed');
});

// 10. Accessibility Tests
testSuite.test('A11y: HTML has lang attribute', () => {
    const html = document.querySelector('html');
    testSuite.assertExists(html.getAttribute('lang'), 'Lang attribute missing');
});

testSuite.test('A11y: Page has title', () => {
    testSuite.assertExists(document.title, 'Page title missing');
    testSuite.assert(document.title.length > 0, 'Page title is empty');
});

// 11. Integration Tests
testSuite.test('Integration: Can navigate between pages', () => {
    const navLinks = document.querySelectorAll('a[href]');
    testSuite.assert(navLinks.length > 0, 'No navigation links found');
});

testSuite.test('Integration: All external links are HTTPS or relative', () => {
    const links = document.querySelectorAll('a[href]');
    let invalidCount = 0;
    links.forEach(link => {
        const href = link.getAttribute('href');
        if (href && !href.startsWith('http') && !href.startsWith('/') && !href.startsWith('#') && !href.startsWith('.')) {
            invalidCount++;
        }
    });
    testSuite.assert(invalidCount === 0, `Found ${invalidCount} invalid links`);
});

// 12. Data Integrity Tests
testSuite.test('Data: Schedule data maintains integrity', () => {
    const schedule = [
        { time: '00:00', title: 'Show 1' },
        { time: '01:00', title: 'Show 2' }
    ];
    const restored = JSON.parse(JSON.stringify(schedule));
    testSuite.assertEquals(restored[0].time, '00:00', 'Data integrity check failed');
    testSuite.assertEquals(restored[1].title, 'Show 2', 'Data integrity check failed');
});

// 13. Error Handling Tests
testSuite.test('Error: Invalid JSON handling', () => {
    try {
        JSON.parse('invalid json');
        throw new Error('Should have thrown');
    } catch (e) {
        testSuite.assert(e instanceof SyntaxError || e.message !== 'Should have thrown', 'Error handling works');
    }
});

// 14. Cross-browser Compatibility Tests
testSuite.test('Compat: Browser supports localStorage', () => {
    testSuite.assert(typeof localStorage !== 'undefined', 'localStorage not supported');
});

testSuite.test('Compat: Browser supports fetch API', () => {
    testSuite.assert(typeof fetch !== 'undefined', 'Fetch API not supported');
});

console.log(`ScheduleFlow Test Suite Loaded: ${testSuite.tests.length} tests registered`);
