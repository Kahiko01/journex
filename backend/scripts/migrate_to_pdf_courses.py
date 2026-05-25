#!/usr/bin/env python3
"""
Migrate existing courses to PDF-based courses
Run this after adding pdf_filename column
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.university import Course
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PDF mapping - course title to filename
PDF_MAPPING = {
    "Babypips Forex School": "babypips.pdf",
    "Candlestick Patterns with Moving Average": "candlestick patterns with moving average (1).pdf",
    "Fibonacci Trading": "fibonacci trading .pdf",
    "Order Blocks Trading": "Order blocks.pdf",
    "Smart Money Concepts Cheat Sheet": "SnD SMC Cheat Sheet.pdf",
    "The Blueprint to Trading Psychology": "The Blueprint to Trading Psychology.pdf",
    "Volatility Indices Trading": "VOLATILITY INDICES.pdf",
    "WWA Trading Guide": "WWA.pdf"
}

def migrate_courses():
    db = SessionLocal()
    try:
        # Get all courses
        courses = db.query(Course).all()
        logger.info(f"Found {len(courses)} courses")
        
        updated = 0
        for course in courses:
            if course.title in PDF_MAPPING:
                course.pdf_filename = PDF_MAPPING[course.title]
                updated += 1
                logger.info(f"Updated: {course.title} -> {course.pdf_filename}")
            else:
                # Delete courses without PDF mapping
                logger.info(f"Deleting course without PDF: {course.title}")
                db.delete(course)
        
        db.commit()
        logger.info(f"Migration complete. Updated {updated} courses, deleted others.")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_courses()
