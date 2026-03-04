#!/bin/bash
# Quick restore script

echo "🔄 Journex Course Restore Utility"
echo "================================"

cd ~/Documents/journex/backend

# Activate virtual environment
source venv/bin/activate

# List available backups
python3 scripts/backup_courses.py list

echo ""
read -p "Enter backup filename to restore (or press Enter for latest): " backup_file

if [ -z "$backup_file" ]; then
    python3 scripts/backup_courses.py restore
else
    python3 scripts/backup_courses.py restore "scripts/course_backups/$backup_file"
fi

echo ""
echo "✨ Restore complete! Check your courses at http://localhost:3000/university"
