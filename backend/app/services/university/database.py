# app/services/university/database.py
# Central in-memory storage for all university modules

# In-memory storage
courses_db = []
modules_db = []
lessons_db = []
cohorts_db = []
certificates_db = []

def get_courses_db():
    return courses_db

def get_modules_db():
    return modules_db

def get_lessons_db():
    return lessons_db

def get_cohorts_db():
    return cohorts_db

def get_certificates_db():
    return certificates_db
