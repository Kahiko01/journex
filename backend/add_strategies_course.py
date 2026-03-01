#!/usr/bin/env python3
"""
Add an Advanced Strategies course to the university
"""

import requests
import json

API_URL = "http://localhost:8000/api/v1/university/courses/"

course = {
    "title": "Advanced Trading Strategies",
    "level": "Advanced",
    "description": "Learn professional trading strategies including mean reversion, breakout systems, and institutional order flow analysis.",
    "tags": ["Strategies", "Breakout", "Order Flow", "Mean Reversion"],
    "estimated_hours": 12,
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
