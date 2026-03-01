#!/usr/bin/env python3
"""
Add a Trading Psychology course to the university
"""

import requests
import json

API_URL = "http://localhost:8000/api/v1/university/courses/"

course = {
    "title": "Trading Psychology Mastery",
    "level": "Beginner",
    "description": "Master your emotions and develop the mindset of a professional trader. Learn to control fear, greed, and develop unshakable discipline.",
    "tags": ["Psychology", "Discipline", "Emotions", "Mindset"],
    "estimated_hours": 5,
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
