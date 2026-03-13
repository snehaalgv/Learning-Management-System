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

def truncate_for_bcrypt(password: str) -> str:
    # bcrypt has a 72-byte limit. Ensure the string we hash is <= 72 bytes in UTF-8.
    encoded = password.encode('utf-8')
    if len(encoded) <= 72:
        return password

    # Truncate and safely decode to avoid breaking multibyte characters
    truncated = encoded[:72].decode('utf-8', errors='ignore')
    return truncated


def get_password_hash(password: str) -> str:
    safe_password = truncate_for_bcrypt(password)
    return pwd_context.hash(safe_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    safe_password = truncate_for_bcrypt(plain_password)
    return pwd_context.verify(safe_password, hashed_password)

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

    # Hash the password before storing
    hashed_password = get_password_hash(request.password)

    # Insert the new user
    cursor = db.execute(
        "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
        (request.name, request.email, hashed_password, request.role),
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

    # Verify password using bcrypt
    if not verify_password(request.password, user_row["password"]):
        return {"error": "Invalid email or password"}

    return {"user_id": user_row["id"], "name": user_row["name"], "role": user_row["role"]}