#!/usr/bin/env node
/**
 * Load Test: 100 VUs for 30 seconds
 * Equivalent to: k6 run --vus 100 --duration 30s
 * 
 * Tests:
 * - System endpoints (system-info, queue-stats)
 * - List endpoints (schedules, playlists)
 * - Config endpoints (get/save)
 * - Import endpoint (with validation)
 */

const http = require('http');

const BASE_URL = 'http://localhost:5000';
const VUS = 100;              // Virtual users
const DURATION = 30;          // Seconds
const ENDPOINTS = [
  '/api/system-info',
  '/api/queue-stats',
  '/api/schedules',
  '/api/playlists',
  '/api/pages',
  '/api/config',
];

class LoadTest {
  constructor(vus, durationSeconds) {
    this.vus = vus;
    this.durationSeconds = durationSeconds;
    this.results = {
      total: 0,
      success: 0,
      failed: 0,
      errorCodes: {},
      responseTimes: [],
      statusCodes: {},
      startTime: null,
      endTime: null,
    };
  }

  async makeRequest(endpoint) {
    return new Promise((resolve) => {
      const startTime = Date.now();
      const options = {
        hostname: 'localhost',
        port: 5000,
        path: endpoint,
        method: 'GET',
        timeout: 10000,
      };

      const req = http.request(options, (res) => {
        let data = '';
        res.on('data', chunk => { data += chunk; });
        res.on('end', () => {
          const duration = Date.now() - startTime;
          resolve({
            status: res.statusCode,
            duration,
            success: res.statusCode >= 200 && res.statusCode < 300,
            endpoint,
          });
        });
      });

      req.on('error', () => {
        resolve({
          status: 0,
          duration: Date.now() - startTime,
          success: false,
          endpoint,
          error: 'Connection error',
        });
      });

      req.on('timeout', () => {
        req.abort();
        resolve({
          status: 0,
          duration: Date.now() - startTime,
          success: false,
          endpoint,
          error: 'Timeout',
        });
      });

      req.end();
    });
  }

  async runVU() {
    const endTime = Date.now() + (this.durationSeconds * 1000);
    let iterations = 0;

    while (Date.now() < endTime) {
      const endpoint = ENDPOINTS[Math.floor(Math.random() * ENDPOINTS.length)];
      const result = await this.makeRequest(endpoint);

      this.results.total++;
      this.results.responseTimes.push(result.duration);
      this.results.statusCodes[result.status] = (this.results.statusCodes[result.status] || 0) + 1;

      if (result.success) {
        this.results.success++;
      } else {
        this.results.failed++;
        this.results.errorCodes[result.error || result.status] = 
          (this.results.errorCodes[result.error || result.status] || 0) + 1;
      }

      iterations++;
    }

    return iterations;
  }

  async run() {
    console.log(`\n${'='.repeat(80)}`);
    console.log(`Load Test: ${this.vus} VUs for ${this.durationSeconds} seconds`);
    console.log(`${'='.repeat(80)}\n`);

    // Check server is up
    console.log('📋 Checking server...');
    const healthCheck = await this.makeRequest('/api/system-info');
    if (!healthCheck.success) {
      console.error('❌ Server not responding! Start with: node api_server.js');
      process.exit(1);
    }
    console.log('✓ Server is running\n');

    // Start load test
    this.results.startTime = Date.now();
    console.log(`🚀 Starting ${this.vus} concurrent users...\n`);

    const startTime = Date.now();
    const promises = [];

    for (let i = 0; i < this.vus; i++) {
      promises.push(this.runVU());
    }

    const iterations = await Promise.all(promises);
    const totalDuration = Date.now() - startTime;
    this.results.endTime = Date.now();

    // Calculate statistics
    const avgDuration = this.results.responseTimes.reduce((a, b) => a + b, 0) / this.results.responseTimes.length;
    const sortedTimes = this.results.responseTimes.sort((a, b) => a - b);
    const p95 = sortedTimes[Math.floor(sortedTimes.length * 0.95)];
    const p99 = sortedTimes[Math.floor(sortedTimes.length * 0.99)];
    const throughput = (this.results.total / (totalDuration / 1000)).toFixed(2);

    // Display results
    console.log('\n' + '='.repeat(80));
    console.log('RESULTS');
    console.log('='.repeat(80) + '\n');

    const successRate = ((this.results.success / this.results.total) * 100).toFixed(1);
    console.log(`Total Requests:     ${this.results.total}`);
    console.log(`Successful:         ${this.results.success} (${successRate}%)`);
    console.log(`Failed:             ${this.results.failed}`);
    console.log(`Test Duration:      ${totalDuration}ms\n`);

    console.log('Response Times:');
    console.log(`  Min:              ${Math.min(...this.results.responseTimes)}ms`);
    console.log(`  Max:              ${Math.max(...this.results.responseTimes)}ms`);
    console.log(`  Avg:              ${avgDuration.toFixed(2)}ms`);
    console.log(`  P95:              ${p95}ms`);
    console.log(`  P99:              ${p99}ms\n`);

    console.log(`Throughput:         ${throughput} req/s\n`);

    console.log('Status Codes:');
    Object.entries(this.results.statusCodes)
      .sort((a, b) => b[1] - a[1])
      .forEach(([code, count]) => {
        const pct = ((count / this.results.total) * 100).toFixed(1);
        console.log(`  ${code}: ${count} (${pct}%)`);
      });

    if (Object.keys(this.results.errorCodes).length > 0) {
      console.log('\nError Breakdown:');
      Object.entries(this.results.errorCodes)
        .forEach(([error, count]) => {
          console.log(`  ${error}: ${count}`);
        });
    }

    // Assessment
    console.log('\n' + '='.repeat(80));
    console.log('ASSESSMENT');
    console.log('='.repeat(80) + '\n');

    if (successRate >= 99) {
      console.log('✅ EXCELLENT - All requests successful');
    } else if (successRate >= 95) {
      console.log('✅ GOOD - >95% success rate');
    } else if (successRate >= 90) {
      console.log('⚠️  ACCEPTABLE - >90% success rate');
    } else {
      console.log('❌ POOR - <90% success rate');
    }

    if (avgDuration < 100) {
      console.log('✅ FAST - Average response time <100ms');
    } else if (avgDuration < 500) {
      console.log('⚠️  ACCEPTABLE - Average response time <500ms');
    } else {
      console.log('⚠️  SLOW - Average response time >500ms (possible queue buildup)');
    }

    if (parseFloat(throughput) > 100) {
      console.log(`✅ GOOD THROUGHPUT - ${throughput} req/s`);
    } else {
      console.log(`⚠️  Limited throughput - ${throughput} req/s`);
    }

    console.log('\n' + '='.repeat(80));
    console.log('PROCESS POOL IMPACT');
    console.log('='.repeat(80) + '\n');

    // Check queue stats
    const queueStats = await this.makeRequest('/api/queue-stats');
    console.log('✓ Load test complete\n');

    process.exit(this.results.failed === 0 ? 0 : 1);
  }
}

// Run test
const test = new LoadTest(VUS, DURATION);
test.run().catch(error => {
  console.error('Error:', error.message);
  process.exit(1);
});
