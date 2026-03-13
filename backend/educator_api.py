from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
import sqlite3

from database import get_db_connection
from auth_api import get_current_user

router = APIRouter()

@router.post("/courses")
async def create_course(title: str, description: str, current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db_connection)):
    if current_user["role"] != "educator":
        raise HTTPException(status_code=403, detail="Not authorized")

    cursor = db.execute(
        "INSERT INTO courses (title, description, educator_id) VALUES (?, ?, ?)",
        (title, description, current_user["id"]),
    )
    db.commit()
    course_id = cursor.lastrowid
    cursor = db.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    return dict(cursor.fetchone())

@router.get("/courses")
async def get_my_courses(current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db_connection)):
    if current_user["role"] != "educator":
        raise HTTPException(status_code=403, detail="Not authorized")

    cursor = db.execute("SELECT * FROM courses WHERE educator_id = ?", (current_user["id"],))
    courses = [dict(row) for row in cursor.fetchall()]
    return courses

@router.post("/assignments")
async def create_assignment(course_id: int, title: str, description: str, due_date: str, current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db_connection)):
    if current_user["role"] != "educator":
        raise HTTPException(status_code=403, detail="Not authorized")

    cursor = db.execute(
        "SELECT 1 FROM courses WHERE id = ? AND educator_id = ?",
        (course_id, current_user["id"]),
    )
    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="Course not found or not authorized")

    due = datetime.fromisoformat(due_date)
    cursor = db.execute(
        "INSERT INTO assignments (title, description, course_id, due_date) VALUES (?, ?, ?, ?)",
        (title, description, course_id, due.isoformat()),
    )
    db.commit()
    assignment_id = cursor.lastrowid
    cursor = db.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,))
    return dict(cursor.fetchone())

@router.get("/enrollments/{course_id}")
async def get_enrollments(course_id: int, current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db_connection)):
    if current_user["role"] != "educator":
        raise HTTPException(status_code=403, detail="Not authorized")

    cursor = db.execute(
        "SELECT 1 FROM courses WHERE id = ? AND educator_id = ?",
        (course_id, current_user["id"]),
    )
    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="Course not found or not authorized")

    cursor = db.execute("SELECT * FROM enrollments WHERE course_id = ?", (course_id,))
    enrollments = [dict(row) for row in cursor.fetchall()]
    return enrollments