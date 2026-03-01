from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Force PostgreSQL - ignore any environment variables that might be pointing to SQLite
DATABASE_URL = "postgresql://journex_user:journex_password@localhost/journex_db"

# Add echo=True to see all SQL queries (helpful for debugging)
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
