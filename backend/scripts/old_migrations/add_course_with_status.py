import requests
import json

print("=== ADDING TEST COURSE WITH STATUS ===\n")

course = {
    "title": "Trading Psychology Mastery",
    "level": "Beginner",
    "description": "Master your emotions and become a disciplined trader",
    "tags": ["Psychology", "Discipline"],
    "estimated_hours": 5,
    "status": "published"
}

print("Sending course data:")
print(json.dumps(course, indent=2))
print()

try:
    response = requests.post('http://localhost:8000/api/v1/university/courses/', json=course)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Success!")
        print("Response:", json.dumps(response.json(), indent=2))
    else:
        print("❌ Failed!")
        print("Error:", response.text)
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n=== DONE ===")
