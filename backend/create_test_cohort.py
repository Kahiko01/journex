import requests
import json
from datetime import datetime, timedelta

print("=== CREATING TEST COHORT ===\n")

start_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
end_date = (datetime.utcnow() + timedelta(days=56)).isoformat()  # 7 weeks

cohort = {
    "name": "January Risk Mastery 2026",
    "description": "Master risk management in 7 weeks",
    "instructor_id": "instructor-123",
    "course_id": "course-123",
    "start_date": start_date,
    "end_date": end_date,
    "max_students": 30,
    "is_private": False,
    "requirements": {
        "min_discipline_score": 70,
        "min_risk_consistency": 65,
        "max_allowed_violations": 5,
        "min_lessons_completed": 80,
        "min_quiz_score": 70
    }
}

print("Sending cohort data:")
print(json.dumps(cohort, indent=2))
print()

try:
    response = requests.post('http://localhost:8000/api/v1/university/cohorts/', json=cohort)
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
