#!/usr/bin/env python3
"""
Post-migration check to verify courses still exist
"""

import requests
import sys
from backup_courses import restore_courses

def main():
    print("🔍 Post-migration check running...")
    
    # Check if courses exist
    try:
        response = requests.get("http://localhost:8000/api/v1/university/courses/")
        if response.status_code == 200:
            courses = response.json().get('courses', [])
            if not courses:
                print("⚠️  No courses found after migration!")
                print("🔄 Attempting to restore from latest backup...")
                if restore_courses():
                    print("✅ Courses restored successfully!")
                else:
                    print("❌ Failed to restore courses")
                    return 1
            else:
                print(f"✅ {len(courses)} courses verified")
        else:
            print(f"❌ API returned {response.status_code}")
            return 1
    except Exception as e:
        print(f"❌ Check failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

