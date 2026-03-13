import sqlite3
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite file (same database used by SQLAlchemy)
DB_PATH = Path(__file__).resolve().parent / "lms.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# SQLAlchemy session dependency (kept for compatibility)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# sqlite3 connection dependency (returns rows as dicts)
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def create_sqlite_tables():
    """Create the LMS tables if they don't already exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        # Drop existing tables to recreate with correct schema
        conn.execute("DROP TABLE IF EXISTS submissions")
        conn.execute("DROP TABLE IF EXISTS assignments")
        conn.execute("DROP TABLE IF EXISTS lectures")
        conn.execute("DROP TABLE IF EXISTS enrollments")
        conn.execute("DROP TABLE IF EXISTS courses")
        conn.execute("DROP TABLE IF EXISTS users")
        conn.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                educator_id INTEGER NOT NULL,
                FOREIGN KEY (educator_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE lectures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                video_link TEXT,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                pdf_path TEXT,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                FOREIGN KEY (student_id) REFERENCES users(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assignment_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                pdf_file TEXT,
                grade TEXT,
                FOREIGN KEY (assignment_id) REFERENCES assignments(id),
                FOREIGN KEY (student_id) REFERENCES users(id)
            )
            """
        )


# Create tables at import time (safe even if already created)
create_sqlite_tables()