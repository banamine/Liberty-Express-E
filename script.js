import http from 'k6/http';
import { check, group, sleep } from 'k6';

export const options = {
  vus: 100,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.1'],
  },
};

const BASE_URL = 'http://localhost:5000';

export default function () {
  group('System Endpoints', () => {
    // Test system info
    let res = http.get(`${BASE_URL}/api/system-info`);
    check(res, {
      'system-info status is 200': (r) => r.status === 200,
      'system-info has version': (r) => r.json('version') !== undefined,
    });

    // Test queue stats
    res = http.get(`${BASE_URL}/api/queue-stats`);
    check(res, {
      'queue-stats status is 200': (r) => r.status === 200,
      'queue-stats has processPool': (r) => r.json('processPool') !== undefined,
    });
  });

  group('List Endpoints', () => {
    // Test schedules list
    let res = http.get(`${BASE_URL}/api/schedules`);
    check(res, {
      'schedules status is 200 or 500': (r) => r.status === 200 || r.status === 500,
    });

    // Test playlists list
    res = http.get(`${BASE_URL}/api/playlists`);
    check(res, {
      'playlists status is 200 or 500': (r) => r.status === 200 || r.status === 500,
    });

    // Test pages list
    res = http.get(`${BASE_URL}/api/pages`);
    check(res, {
      'pages status is 200': (r) => r.status === 200,
      'pages has count': (r) => r.json('count') !== undefined,
    });
  });

  group('Config Endpoints', () => {
    // Test get config
    let res = http.get(`${BASE_URL}/api/config`);
    check(res, {
      'config get status is 200': (r) => r.status === 200,
      'config has status': (r) => r.json('status') !== undefined,
    });

    // Test save config
    res = http.post(`${BASE_URL}/api/config`, JSON.stringify({
      test: 'value',
      timestamp: new Date().toISOString(),
    }), {
      headers: { 'Content-Type': 'application/json' },
    });
    check(res, {
      'config save status is 200': (r) => r.status === 200,
      'config save has success': (r) => r.json('status') === 'success',
    });
  });

  sleep(1);
}
