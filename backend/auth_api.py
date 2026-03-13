from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
import sqlite3

from database import get_db_connection
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str  # "student" or "educator"

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupResponse(BaseModel):
    message: str
    user_id: int

class LoginResponse(BaseModel):
    user_id: int
    name: str
    role: str

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def get_current_user(user_id: int = Header(..., alias="X-User-ID"), db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    if not user_row:
        raise HTTPException(status_code=401, detail="Invalid user")
    return dict(user_row)

@router.get("/test")
def test():
    print("Test endpoint called")
    return {"message": "Auth test updated"}

@router.post("/signup")
def signup(request: SignupRequest, db: sqlite3.Connection = Depends(get_db_connection)):
    # Check if email already exists
    cursor = db.execute("SELECT id FROM users WHERE email = ?", (request.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")

    # For now, store password as plain text (in production, hash it)
    password = request.password

    # Insert the new user
    cursor = db.execute(
        "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
        (request.name, request.email, password, request.role),
    )
    db.commit()
    user_id = cursor.lastrowid

    return {"message": "User created successfully", "user_id": user_id}

@router.post("/login")
async def login(request: LoginRequest, db: sqlite3.Connection = Depends(get_db_connection)):
    # Fetch user by email
    cursor = db.execute("SELECT id, name, password, role FROM users WHERE email = ?", (request.email,))
    user_row = cursor.fetchone()

    if not user_row:
        return {"error": "Invalid email or password"}

    # For now, check plain text password
    if request.password != user_row["password"]:
        return {"error": "Invalid email or password"}

    return {"user_id": user_row["id"], "name": user_row["name"], "role": user_row["role"]}