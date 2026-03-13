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
def signup(request: SignupRequest):
    return {"message": "User created successfully", "user_id": 1}

@router.post("/login")
async def login(request: LoginRequest, db: sqlite3.Connection = Depends(get_db_connection)):
    # Fetch user by email
    cursor = db.execute("SELECT id, name, password, role FROM users WHERE email = ?", (request.email,))
    user_row = cursor.fetchone()

    if not user_row:
        return {"error": "Invalid email or password"}

    # Verify password
    if not verify_password(request.password, user_row["password"]):
        return {"error": "Invalid email or password"}

    return {"user_id": user_row["id"], "name": user_row["name"], "role": user_row["role"]}