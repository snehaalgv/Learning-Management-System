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