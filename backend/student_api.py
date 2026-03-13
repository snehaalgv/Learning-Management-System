from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
import sqlite3
from pydantic import BaseModel
import os
from pathlib import Path

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

@router.post("/submit-assignment")
async def submit_assignment(
    assignment_id: int = Form(...),
    student_id: int = Form(...),
    pdf_file: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db_connection)
):
    # Verify that the student_id exists and is a student
    cursor = db.execute("SELECT role FROM users WHERE id = ?", (student_id,))
    user = cursor.fetchone()
    if not user or user["role"] != "student":
        raise HTTPException(status_code=400, detail="Invalid student_id")

    # Verify that the assignment exists and get the course_id
    cursor = db.execute("SELECT course_id FROM assignments WHERE id = ?", (assignment_id,))
    assignment_row = cursor.fetchone()
    if not assignment_row:
        raise HTTPException(status_code=400, detail="Invalid assignment_id")

    course_id = assignment_row["course_id"]

    # Verify that the student is enrolled in the course
    cursor = db.execute(
        "SELECT 1 FROM enrollments WHERE student_id = ? AND course_id = ?",
        (student_id, course_id),
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=403, detail="Student not enrolled in the course for this assignment")

    # Ensure the uploads directory exists
    uploads_dir = Path(__file__).parent / "uploads"
    uploads_dir.mkdir(exist_ok=True)

    # Save the PDF file
    file_path = uploads_dir / f"submission_{assignment_id}_{student_id}.pdf"
    with open(file_path, "wb") as f:
        content = await pdf_file.read()
        f.write(content)

    # Store submission data in the database
    cursor = db.execute(
        "INSERT INTO submissions (assignment_id, student_id, pdf_file) VALUES (?, ?, ?)",
        (assignment_id, student_id, str(file_path)),
    )
    db.commit()
    submission_id = cursor.lastrowid

    return {"submission_id": submission_id, "message": "Assignment submitted successfully"}

@router.get("/student/dashboard/{student_id}")
def get_student_dashboard(student_id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    # Verify that the student_id exists and is a student
    cursor = db.execute("SELECT role FROM users WHERE id = ?", (student_id,))
    user = cursor.fetchone()
    if not user or user["role"] != "student":
        raise HTTPException(status_code=400, detail="Invalid student_id")

    # Total enrolled courses
    cursor = db.execute("SELECT COUNT(*) as count FROM enrollments WHERE student_id = ?", (student_id,))
    total_enrolled = cursor.fetchone()["count"]

    # Total modules completed (assuming modules are assignments, completed means submitted)
    cursor = db.execute("SELECT COUNT(DISTINCT assignment_id) as count FROM submissions WHERE student_id = ?", (student_id,))
    modules_completed = cursor.fetchone()["count"]

    # Progress percentage: (completed assignments / total assignments in enrolled courses) * 100
    # First, get enrolled course_ids
    cursor = db.execute("SELECT course_id FROM enrollments WHERE student_id = ?", (student_id,))
    enrolled_course_ids = [row["course_id"] for row in cursor.fetchall()]

    if enrolled_course_ids:
        # Total assignments in enrolled courses
        placeholders = ','.join('?' for _ in enrolled_course_ids)
        cursor = db.execute(f"SELECT COUNT(*) as count FROM assignments WHERE course_id IN ({placeholders})", enrolled_course_ids)
        total_assignments = cursor.fetchone()["count"]
        progress_percentage = (modules_completed / total_assignments * 100) if total_assignments > 0 else 0
    else:
        progress_percentage = 0

    return {
        "total_enrolled_courses": total_enrolled,
        "total_modules_completed": modules_completed,
        "progress_percentage": round(progress_percentage, 2)
    }