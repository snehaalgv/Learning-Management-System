import requests
import json
import os

# Base URL
BASE_URL = "http://localhost:8003"

# Create a dummy PDF file for testing
dummy_pdf_path = "dummy_submission.pdf"
with open(dummy_pdf_path, "wb") as f:
    f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Test Submission) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000200 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n284\n%%EOF")

print("Creating student...")
student_signup_data = {
    "name": "Student Test",
    "email": "student@test.com",
    "password": "password123",
    "role": "student"
}
response = requests.post(f"{BASE_URL}/auth/signup", json=student_signup_data)
print("Student Signup Response:", response.status_code, response.text)
student_id = response.json()["user_id"]

print("Creating educator...")
educator_signup_data = {
    "name": "Educator Test",
    "email": "educator@test.com",
    "password": "password123",
    "role": "educator"
}
response = requests.post(f"{BASE_URL}/auth/signup", json=educator_signup_data)
print("Educator Signup Response:", response.status_code, response.text)
educator_id = response.json()["user_id"]

print("Creating course...")
course_data = {
    "title": "Test Course",
    "description": "This is a test course",
    "educator_id": educator_id
}
response = requests.post(f"{BASE_URL}/educator/create-course", json=course_data)
print("Create Course Response:", response.status_code, response.text)
course_id = response.json()["course_id"]

print("Enrolling student...")
enroll_data = {
    "student_id": student_id,
    "course_id": course_id
}
response = requests.post(f"{BASE_URL}/student/enroll", json=enroll_data)
print("Enroll Response:", response.status_code, response.text)

print("Creating assignment...")
# I need to add an assignment creation endpoint or manually insert. Since there's no endpoint, I'll assume we need to create one, but for now, let's skip and test submission assuming assignment exists.

# For testing, I'll manually create an assignment in the database, but since I can't, let's assume the assignment exists with id 1.

# Actually, I need to add assignment creation. But the user didn't ask for it. For testing, I'll create a simple script to insert into DB, but that's not possible.

# Since the database is SQLite, I can use a direct connection to insert.

# But to keep it simple, let's modify the test to assume assignment_id = 1, and manually insert it.

# Actually, let's add a simple assignment creation in the test by directly executing SQL, but that's not clean.

# Since the educator_api has create_assignment, but it's commented out. Let me check if I can use it.

# In educator_api.py, there is @router.post("/assignments") but it's not included.

# For testing, I'll create the assignment manually by running a script that connects to DB.

# Let me create a small script to insert an assignment.

import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "lms.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("INSERT INTO assignments (course_id, title, pdf_path) VALUES (?, ?, ?)", (course_id, "Test Assignment", "dummy.pdf"))
assignment_id = cursor.lastrowid
conn.commit()
conn.close()

print(f"Created assignment with ID: {assignment_id}")

# Now submit the assignment
print("Submitting assignment...")
with open(dummy_pdf_path, "rb") as f:
    files = {"pdf_file": ("submission.pdf", f, "application/pdf")}
    data = {"assignment_id": assignment_id, "student_id": student_id}
    response = requests.post(f"{BASE_URL}/student/submit-assignment", files=files, data=data)
    print("Submit Response:", response.status_code, response.text)

# Clean up
os.remove(dummy_pdf_path)