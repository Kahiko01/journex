import requests
import json

print("=== ADDING COURSE AND VERIFYING ===\n")

course = {
    "title": "Trading Psychology Mastery",
    "level": "Beginner",
    "description": "Master your emotions and become a disciplined trader",
    "tags": ["Psychology", "Discipline"],
    "estimated_hours": 5
}

print("1. Adding course...")
response = requests.post('http://localhost:8000/api/v1/university/courses/', json=course)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print("   ✅ Course added successfully")
    print("   Response:", json.dumps(response.json(), indent=2))
else:
    print("   ❌ Failed:", response.text)

print("\n2. Checking debug endpoint...")
debug = requests.get('http://localhost:8000/api/v1/university/courses/debug/all')
print("   Response:", json.dumps(debug.json(), indent=2))

print("\n3. Checking regular endpoint...")
regular = requests.get('http://localhost:8000/api/v1/university/courses/')
print("   Response:", json.dumps(regular.json(), indent=2))

print("\n=== DONE ===")
