#!/usr/bin/env python3
"""
Add a Risk Management course to the university
"""

import requests
import json

API_URL = "http://localhost:8000/api/v1/university/courses/"

course = {
    "title": "Risk Management Mastery",
    "level": "Intermediate",
    "description": "Master professional risk management techniques used by institutional traders. Learn position sizing, drawdown control, and how to protect your capital.",
    "tags": ["Risk Management", "Position Sizing", "Psychology", "Drawdown Control"],
    "estimated_hours": 8,
    "status": "published"
}

print("Adding course to university...")
response = requests.post(API_URL, json=course)

if response.status_code == 200:
    print("✅ Course added successfully!")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"❌ Failed to add course: {response.status_code}")
    print(response.text)
