from fastapi import APIRouter, Depends, HTTPException
import sqlite3
from pydantic import BaseModel

from database import get_db_connection

router = APIRouter()

class EnrollRequest(BaseModel):
    student_id: int
    course_id: int

@router.post("/student/enroll")
def enroll_student(request: EnrollRequest, db: sqlite3.Connection = Depends(get_db_connection)):
    # Verify that the student_id exists and is a student
    cursor = db.execute("SELECT role FROM users WHERE id = ?", (request.student_id,))
    user = cursor.fetchone()
    if not user or user["role"] != "student":
        raise HTTPException(status_code=400, detail="Invalid student_id")

    # Verify that the course exists
    cursor = db.execute("SELECT id FROM courses WHERE id = ?", (request.course_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=400, detail="Invalid course_id")

    # Check if already enrolled
    cursor = db.execute(
        "SELECT id FROM enrollments WHERE student_id = ? AND course_id = ?",
        (request.student_id, request.course_id),
    )
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Already enrolled in this course")

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