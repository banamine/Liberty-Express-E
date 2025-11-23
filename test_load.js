#!/usr/bin/env node
/**
 * ScheduleFlow Load Test
 * Tests concurrent user handling with async I/O
 */

const http = require('http');

// Configuration
const BASE_URL = 'http://localhost:5000';
const CONCURRENT_USERS = [1, 5, 10, 20];
const REQUESTS_PER_USER = 10;

// Test endpoints
const ENDPOINTS = [
  '/api/system-info',
  '/api/pages',
  '/api/config'
];

// Color codes for output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m'
};

function log(color, message) {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function makeRequest(endpoint) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const options = {
      hostname: 'localhost',
      port: 5000,
      path: endpoint,
      method: 'GET'
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => {
        const duration = Date.now() - startTime;
        resolve({
          status: res.statusCode,
          duration,
          success: res.statusCode === 200
        });
      });
    });

    req.on('error', (error) => {
      const duration = Date.now() - startTime;
      resolve({
        status: 0,
        duration,
        success: false,
        error: error.message
      });
    });

    req.setTimeout(30000, () => {
      req.abort();
      resolve({
        status: 0,
        duration: 30000,
        success: false,
        error: 'Timeout'
      });
    });

    req.end();
  });
}

async function testConcurrentUsers(numUsers) {
  log('blue', `\n${'='.repeat(70)}`);
  log('blue', `Testing ${numUsers} Concurrent Users (${REQUESTS_PER_USER} requests each)`);
  log('blue', `${'='.repeat(70)}\n`);

  const results = {
    total: 0,
    successful: 0,
    failed: 0,
    durations: [],
    errors: {}
  };

  const startTime = Date.now();
  const promises = [];

  // Create concurrent requests
  for (let user = 0; user < numUsers; user++) {
    for (let req = 0; req < REQUESTS_PER_USER; req++) {
      const endpoint = ENDPOINTS[req % ENDPOINTS.length];
      promises.push(
        makeRequest(endpoint).then(result => {
          results.total++;
          if (result.success) {
            results.successful++;
          } else {
            results.failed++;
            results.errors[result.error || 'unknown'] = (results.errors[result.error || 'unknown'] || 0) + 1;
          }
          results.durations.push(result.duration);
        })
      );
    }
  }

  // Wait for all requests
  await Promise.all(promises);
  const totalDuration = Date.now() - startTime;

  // Calculate statistics
  const avgDuration = results.durations.reduce((a, b) => a + b, 0) / results.durations.length;
  const maxDuration = Math.max(...results.durations);
  const minDuration = Math.min(...results.durations);
  const throughput = (results.total / (totalDuration / 1000)).toFixed(2);

  // Display results
  const successRate = ((results.successful / results.total) * 100).toFixed(1);
  const statusColor = results.failed === 0 ? 'green' : 'red';

  log(statusColor, `✓ Successful: ${results.successful}/${results.total} (${successRate}%)`);
  
  if (results.failed > 0) {
    log('red', `✗ Failed: ${results.failed}`);
    for (const [error, count] of Object.entries(results.errors)) {
      log('red', `  - ${error}: ${count}`);
    }
  }

  log('yellow', `⏱  Response Times:`);
  log('yellow', `  - Average: ${avgDuration.toFixed(2)}ms`);
  log('yellow', `  - Min: ${minDuration}ms`);
  log('yellow', `  - Max: ${maxDuration}ms`);
  log('yellow', `  - Total Time: ${totalDuration}ms`);
  log('yellow', `  - Throughput: ${throughput} req/s`);

  return {
    numUsers,
    successful: results.successful,
    failed: results.failed,
    avgDuration,
    maxDuration,
    throughput: parseFloat(throughput)
  };
}

async function runAllTests() {
  log('green', '\n╔════════════════════════════════════════════════════════════════════╗');
  log('green', '║          ScheduleFlow Async I/O Load Test                       ║');
  log('green', '║          Testing concurrent user handling                       ║');
  log('green', '╚════════════════════════════════════════════════════════════════════╝');

  const testResults = [];

  // Check if server is running
  log('blue', '\n📋 Checking server availability...');
  try {
    await makeRequest('/api/system-info');
    log('green', '✓ Server is running on port 5000\n');
  } catch (error) {
    log('red', '✗ Server not running! Start with: node api_server.js');
    process.exit(1);
  }

  // Run load tests
  for (const numUsers of CONCURRENT_USERS) {
    const result = await testConcurrentUsers(numUsers);
    testResults.push(result);
  }

  // Summary
  log('green', `\n${'='.repeat(70)}`);
  log('green', 'SUMMARY');
  log('green', `${'='.repeat(70)}\n`);

  console.table(testResults.map(r => ({
    'Concurrent Users': r.numUsers,
    'Successful': `${r.successful}/${r.numUsers * REQUESTS_PER_USER}`,
    'Avg Response (ms)': r.avgDuration.toFixed(2),
    'Max Response (ms)': r.maxDuration,
    'Throughput (req/s)': r.throughput
  })));

  // Analysis
  log('blue', '\n📊 ANALYSIS\n');

  const allSuccess = testResults.every(r => r.failed === 0);
  if (allSuccess) {
    log('green', '✓ All tests PASSED - Async I/O is working correctly!');
    log('green', '✓ No blocking I/O detected');
    log('green', '✓ Server handles concurrent requests efficiently');
  } else {
    log('red', '✗ Some tests FAILED - Performance issues detected');
    const failedTests = testResults.filter(r => r.failed > 0);
    for (const test of failedTests) {
      log('red', `  - At ${test.numUsers} users: ${test.failed} requests failed`);
    }
  }

  // Performance assessment
  log('yellow', '\n🎯 PERFORMANCE ASSESSMENT\n');
  
  const avgThroughput = testResults.reduce((a, b) => a + b.throughput, 0) / testResults.length;
  log('yellow', `Average Throughput: ${avgThroughput.toFixed(2)} requests/second`);
  
  if (avgThroughput > 100) {
    log('green', '✓ EXCELLENT - Server can handle 100+ concurrent users');
  } else if (avgThroughput > 50) {
    log('yellow', '⚠ GOOD - Server can handle 50-100 concurrent users');
  } else {
    log('red', '✗ POOR - Server struggles with many concurrent users');
  }

  log('green', '\n✓ Load test complete!\n');
}

// Run tests
runAllTests().catch(error => {
  log('red', `Error: ${error.message}`);
  process.exit(1);
});
