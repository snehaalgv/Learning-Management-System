from fastapi import APIRouter, Depends, HTTPException
import sqlite3
from pydantic import BaseModel

from database import get_db_connection

router = APIRouter()

class CreateCourseRequest(BaseModel):
    title: str
    description: str
    educator_id: int

@router.post("/educator/create-course")
def create_course(request: CreateCourseRequest, db: sqlite3.Connection = Depends(get_db_connection)):
    # Verify that the educator_id exists and is an educator
    cursor = db.execute("SELECT role FROM users WHERE id = ?", (request.educator_id,))
    user = cursor.fetchone()
    if not user or user["role"] != "educator":
        raise HTTPException(status_code=400, detail="Invalid educator_id")

    cursor = db.execute(
        "INSERT INTO courses (title, description, educator_id) VALUES (?, ?, ?)",
        (request.title, request.description, request.educator_id),
    )
    db.commit()
    course_id = cursor.lastrowid
    return {"course_id": course_id, "message": "Course created successfully"}

@router.get("/courses")
def get_all_courses(db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.execute("SELECT id, title, description, educator_id FROM courses")
    courses = [dict(row) for row in cursor.fetchall()]
    return courses

@router.get("/dashboard/{educator_id}")
def get_educator_dashboard(educator_id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    # Verify that the educator_id exists and is an educator
    cursor = db.execute("SELECT role FROM users WHERE id = ?", (educator_id,))
    user = cursor.fetchone()
    if not user or user["role"] != "educator":
        raise HTTPException(status_code=400, detail="Invalid educator_id")

    # Number of courses created
    cursor = db.execute("SELECT COUNT(*) as count FROM courses WHERE educator_id = ?", (educator_id,))
    courses_created = cursor.fetchone()["count"]

    # Number of students enrolled in each course
    cursor = db.execute("""
        SELECT c.id, c.title, COUNT(e.student_id) as enrolled_students
        FROM courses c
        LEFT JOIN enrollments e ON c.id = e.course_id
        WHERE c.educator_id = ?
        GROUP BY c.id, c.title
    """, (educator_id,))
    course_enrollments = [{"course_id": row["id"], "course_title": row["title"], "enrolled_students": row["enrolled_students"]} for row in cursor.fetchall()]

    # Number of assignment submissions
    cursor = db.execute("""
        SELECT COUNT(*) as count
        FROM submissions s
        JOIN assignments a ON s.assignment_id = a.id
        JOIN courses c ON a.course_id = c.id
        WHERE c.educator_id = ?
    """, (educator_id,))
    submissions_count = cursor.fetchone()["count"]

    return {
        "courses_created": courses_created,
        "course_enrollments": course_enrollments,
        "total_assignment_submissions": submissions_count
    }