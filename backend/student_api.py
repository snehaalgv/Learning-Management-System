from fastapi import APIRouter, Depends, HTTPException
import sqlite3
from pydantic import BaseModel

from database import get_db_connection
from auth_api import get_current_user

router = APIRouter()

@router.get("/courses")
async def get_enrolled_courses(current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db_connection)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    cursor = db.execute(
        "SELECT c.* FROM courses c JOIN enrollments e ON c.id = e.course_id WHERE e.student_id = ?",
        (current_user["id"],),
    )
    courses = [dict(row) for row in cursor.fetchall()]
    return courses

@router.get("/assignments/{course_id}")
async def get_assignments(course_id: int, current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db_connection)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Insert enrollment
    cursor = db.execute(
        "INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
        (request.student_id, request.course_id),
    )
    db.commit()
    enrollment_id = cursor.lastrowid
    return {"enrollment_id": enrollment_id, "message": "Successfully enrolled in course"}

@router.get("/student/my-courses/{student_id}")
def get_student_courses(student_id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    # Verify that the student_id exists and is a student
    cursor = db.execute("SELECT role FROM users WHERE id = ?", (student_id,))
    user = cursor.fetchone()
    if not user or user["role"] != "student":
        raise HTTPException(status_code=400, detail="Invalid student_id")

    # Join enrollments with courses
    cursor = db.execute(
        """
        SELECT c.id, c.title, c.description, c.educator_id
        FROM courses c
        JOIN enrollments e ON c.id = e.course_id
        WHERE e.student_id = ?
        """,
        (student_id,),
    )
    courses = [dict(row) for row in cursor.fetchall()]
    return courses