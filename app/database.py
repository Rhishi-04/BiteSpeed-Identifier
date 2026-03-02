"""
Database connection and session. PostgreSQL via DATABASE_URL (e.g. Neon on Vercel).
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.environ["DATABASE_URL"]
# Some hosts (e.g. Neon) give postgres://; SQLAlchemy expects postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency: yield a DB session, close after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
