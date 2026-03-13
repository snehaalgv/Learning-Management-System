from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_sqlite_tables
from auth_api import router as auth_router
from student_api import router as student_router
from educator_api import router as educator_router

# Ensure SQLite tables exist before the app starts
create_sqlite_tables()

app = FastAPI(title="Learning Management System API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(student_router, prefix="/student", tags=["Student"])
app.include_router(educator_router, prefix="/educator", tags=["Educator"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Learning Management System API"}