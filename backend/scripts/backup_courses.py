#!/usr/bin/env python3
"""
Course Backup and Restore Utility
Prevents courses from disappearing after migrations or changes
"""

import json
import requests
import os
import sys
from datetime import datetime
from pathlib import Path

# Configuration
BACKUP_DIR = Path(__file__).parent / "course_backups"
BACKUP_DIR.mkdir(exist_ok=True)

def get_token():
    """Get authentication token"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            data={"username": "testuser", "password": "Test123456"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
    except:
        return None
    return None

def backup_courses():
    """Backup all courses to a JSON file"""
    token = get_token()
    if not token:
        print("❌ Failed to get authentication token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get all courses
        response = requests.get(
            "http://localhost:8000/api/v1/university/courses/",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch courses: {response.status_code}")
            return False
        
        courses_data = response.json()
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"courses_backup_{timestamp}.json"
        
        # Save to file
        with open(backup_file, 'w') as f:
            json.dump(courses_data, f, indent=2)
        
        course_count = len(courses_data.get('courses', []))
        print(f"✅ Backed up {course_count} courses to {backup_file}")
        return True
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def restore_courses(backup_file=None):
    """Restore courses from a backup file"""
    token = get_token()
    if not token:
        print("❌ Failed to get authentication token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # If no backup file specified, use the most recent
    if not backup_file:
        backup_files = sorted(BACKUP_DIR.glob("courses_backup_*.json"), reverse=True)
        if not backup_files:
            print("❌ No backup files found")
            return False
        backup_file = backup_files[0]
    
    try:
        # Load backup data
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        courses = backup_data.get('courses', [])
        if not courses:
            print("❌ No courses in backup file")
            return False
        
        print(f"📚 Found {len(courses)} courses to restore")
        
        # First, check which courses already exist
        response = requests.get(
            "http://localhost:8000/api/v1/university/courses/",
            headers=headers
        )
        existing_courses = response.json().get('courses', [])
        existing_titles = {c['title'] for c in existing_courses}
        
        restored = 0
        skipped = 0
        
        for course in courses:
            if course['title'] in existing_titles:
                print(f"⏭️  Skipping existing course: {course['title']}")
                skipped += 1
                continue
            
            # Create the course
            create_response = requests.post(
                "http://localhost:8000/api/v1/university/courses/",
                headers=headers,
                json={
                    "title": course['title'],
                    "description": course['description'],
                    "category": course.get('category', 'General'),
                    "difficulty": course.get('difficulty', 'Beginner'),
                    "duration_minutes": course.get('duration_minutes', 60)
                }
            )
            
            if create_response.status_code == 200:
                print(f"✅ Restored: {course['title']}")
                restored += 1
            else:
                print(f"❌ Failed to restore: {course['title']}")
        
        print(f"\n📊 Summary: {restored} restored, {skipped} skipped")
        return True
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False

def list_backups():
    """List all available backups"""
    backup_files = sorted(BACKUP_DIR.glob("courses_backup_*.json"), reverse=True)
    
    if not backup_files:
        print("📭 No backups found")
        return
    
    print("\n📋 Available backups:")
    for i, backup_file in enumerate(backup_files, 1):
        size = backup_file.stat().st_size / 1024  # KB
        modified = datetime.fromtimestamp(backup_file.stat().st_mtime)
        print(f"{i}. {backup_file.name} ({size:.1f} KB) - {modified.strftime('%Y-%m-%d %H:%M:%S')}")

def auto_backup():
    """Automatically backup courses (can be called after changes)"""
    return backup_courses()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "backup":
            backup_courses()
        elif command == "restore":
            if len(sys.argv) > 2:
                restore_courses(sys.argv[2])
            else:
                restore_courses()
        elif command == "list":
            list_backups()
        elif command == "auto":
            auto_backup()
        else:
            print("Usage: python backup_courses.py [backup|restore|list|auto]")
    else:
        # Default to backup
        backup_courses()
