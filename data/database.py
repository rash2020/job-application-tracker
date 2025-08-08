
# data/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "jobs.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    if not os.path.exists(DB_PATH):
        print("📁 jobs.db not found. Creating new database...")
        Base.metadata.create_all(bind=engine)
    else:
        print("✅ jobs.db already exists.")
