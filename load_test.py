"""Load testing script for ScheduleFlow
Run with: locust -f load_test.py
"""

from locust import HttpUser, task, between
import random
import json


class ScheduleFlowUser(HttpUser):
    """Simulates a ScheduleFlow user"""
    wait_time = between(1, 5)
    
    def on_start(self):
        """Register and login"""
        # Register user
        response = self.client.post("/api/auth/register", json={
            "username": f"user_{random.randint(1000, 9999)}",
            "email": f"user_{random.randint(1000, 9999)}@example.com",
            "password": "password123"
        })
        
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            self.token = None
    
    @task(3)
    def get_status(self):
        """Get system status"""
        self.client.get("/api/status")
    
    @task(5)
    def create_schedule(self):
        """Create a schedule"""
        schedule_data = {
            "videos": [
                {"url": f"http://example.com/video{i}.mp4", "duration": 300}
                for i in range(10)
            ],
            "duration_seconds": 3600
        }
        
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        self.client.post(
            "/api/schedules",
            json=schedule_data,
            headers=headers
        )
    
    @task(2)
    def get_schedules(self):
        """List schedules"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        self.client.get("/api/schedules", headers=headers)
    
    @task(4)
    def validate_schedule(self):
        """Validate a schedule"""
        events = [
            {
                "start": "2025-12-01T10:00:00Z",
                "duration": 300,
                "video_url": f"http://example.com/video{i}.mp4"
            }
            for i in range(5)
        ]
        
        self.client.post("/api/validate", json={"events": events})
    
    @task(1)
    def extract_media(self):
        """Extract media from URL (will fail in test, but tests endpoint)"""
        self.client.post(
            "/api/stripper/extract",
            json={"url": "http://example.com"}
        )


class HighLoadUser(HttpUser):
    """Simulates high-load user doing rapid scheduling"""
    wait_time = between(0.5, 2)
    
    @task(10)
    def rapid_scheduling(self):
        """Rapidly create schedules"""
        schedule = {
            "videos": [
                {"url": f"http://example.com/v{random.randint(1,1000)}.mp4", 
                 "duration": random.randint(300, 600)}
                for _ in range(20)
            ],
            "duration_seconds": 7200
        }
        
        self.client.post("/api/schedules", json=schedule)
