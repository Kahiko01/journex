#!/usr/bin/env python3
"""
Add multiple courses to the university
"""

import requests
import json

API_URL = "http://localhost:8000/api/v1/university/courses/"

courses = [
    {
        "title": "Risk Management Mastery",
        "level": "Intermediate",
        "description": "Master professional risk management techniques used by institutional traders. Learn position sizing, drawdown control, and how to protect your capital.",
        "tags": ["Risk Management", "Position Sizing", "Psychology", "Drawdown Control"],
        "estimated_hours": 8,
        "status": "published"
    },
    {
        "title": "Trading Psychology Mastery",
        "level": "Beginner",
        "description": "Master your emotions and develop the mindset of a professional trader. Learn to control fear, greed, and develop unshakable discipline.",
        "tags": ["Psychology", "Discipline", "Emotions", "Mindset"],
        "estimated_hours": 5,
        "status": "published"
    },
    {
        "title": "Advanced Trading Strategies",
        "level": "Advanced",
        "description": "Learn professional trading strategies including mean reversion, breakout systems, and institutional order flow analysis.",
        "tags": ["Strategies", "Breakout", "Order Flow", "Mean Reversion"],
        "estimated_hours": 12,
        "status": "published"
    },
    {
        "title": "Technical Analysis Fundamentals",
        "level": "Beginner",
        "description": "Learn to read charts, identify trends, and use technical indicators to make better trading decisions.",
        "tags": ["Technical Analysis", "Charts", "Indicators", "Trends"],
        "estimated_hours": 6,
        "status": "published"
    },
    {
        "title": "Price Action Trading",
        "level": "Intermediate",
        "description": "Master pure price action trading without indicators. Learn to read market structure, supply and demand, and candlestick patterns.",
        "tags": ["Price Action", "Candlesticks", "Market Structure", "Supply Demand"],
        "estimated_hours": 10,
        "status": "published"
    }
]

print("=" * 60)
print("ADDING COURSES TO JOURNEX UNIVERSITY")
print("=" * 60)

success_count = 0
for i, course in enumerate(courses):
    print(f"\nAdding course {i+1}: {course['title']}...")
    
    try:
        response = requests.post(API_URL, json=course)
        if response.status_code == 200:
            print(f"  ✅ Success!")
            success_count += 1
        else:
            print(f"  ❌ Failed: {response.status_code}")
            print(f"     {response.text}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print(f"\n{'=' * 60}")
print(f"Added {success_count} out of {len(courses)} courses")
print(f"{'=' * 60}")

# Verify what we have
print("\nVerifying courses in database...")
response = requests.get("http://localhost:8000/api/v1/university/courses/")
if response.status_code == 200:
    data = response.json()
    courses_list = data.get('courses', [])
    print(f"Total courses now: {len(courses_list)}")
    for course in courses_list:
        print(f"  - {course['title']} ({course['level']})")
