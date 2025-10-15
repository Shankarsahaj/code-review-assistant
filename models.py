# models.py
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./code_reviews.db")
Base = declarative_base()

class ReviewReport(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    language = Column(String, index=True)  # ✅ NEW COLUMN
    report = Column(Text)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ THIS LINE RECREATES THE DATABASE SCHEMA
Base.metadata.create_all(bind=engine)
