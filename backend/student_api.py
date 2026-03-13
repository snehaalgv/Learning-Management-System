from fastapi import APIRouter, Depends, HTTPException
import sqlite3

from database import get_db_connection
from auth_api import get_current_user

router = APIRouter()

@router.get("/my-courses/{student_id}")
async def get_my_courses(student_id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    # Verify the user exists and is a student
    cursor = db.execute("SELECT role FROM users WHERE id = ?", (student_id,))
    user = cursor.fetchone()
    if not user or user["role"] != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    cursor = db.execute(
        "SELECT c.* FROM courses c JOIN enrollments e ON c.id = e.course_id WHERE e.student_id = ?",
        (student_id,),
    )
    courses = [dict(row) for row in cursor.fetchall()]
    return courses

@router.get("/assignments/{course_id}")
async def get_assignments(course_id: int, current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db_connection)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    cursor = db.execute(
        "SELECT 1 FROM enrollments WHERE student_id = ? AND course_id = ?",
        (current_user["id"], course_id),
    )
    if cursor.fetchone() is None:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")

    cursor = db.execute("SELECT * FROM assignments WHERE course_id = ?", (course_id,))
    assignments = [dict(row) for row in cursor.fetchall()]
    return assignments

@router.post("/submit-assignment/{assignment_id}")
async def submit_assignment(assignment_id: int, content: str, current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db_connection)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    cursor = db.execute("SELECT course_id FROM assignments WHERE id = ?", (assignment_id,))
    assignment_row = cursor.fetchone()
    if not assignment_row:
        raise HTTPException(status_code=404, detail="Assignment not found")

    cursor = db.execute(
        "SELECT 1 FROM enrollments WHERE student_id = ? AND course_id = ?",
        (current_user["id"], assignment_row["course_id"]),
    )
    if cursor.fetchone() is None:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")

    db.execute(
        "INSERT INTO submissions (assignment_id, student_id, content) VALUES (?, ?, ?)",
        (assignment_id, current_user["id"], content),
    )
    db.commit()
    return {"message": "Assignment submitted successfully"}