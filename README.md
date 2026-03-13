# Learning Management System (LMS)

A FastAPI-based Learning Management System with role-based access for students and educators.

## Features

- User authentication with JWT tokens
- Role-based access control (Student/Educator)
- Course management
- Assignment submission system
- SQLite database
- CORS enabled for frontend integration

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   cd backend
   python run.py
   ```

   Or using uvicorn:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

3. Access the API documentation at: http://localhost:8000/docs

## API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/token` - User login
- `GET /auth/me` - Get current user info

### Student Endpoints
- `GET /student/courses` - Get enrolled courses
- `GET /student/assignments/{course_id}` - Get assignments for a course
- `POST /student/submit-assignment/{assignment_id}` - Submit an assignment

### Educator Endpoints
- `POST /educator/courses` - Create a new course
- `GET /educator/courses` - Get courses created by the educator
- `POST /educator/assignments` - Create an assignment
- `GET /educator/enrollments/{course_id}` - Get enrollments for a course

## Database

The application uses SQLite (`lms.db`) for data storage. Tables are created automatically on startup.

## Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Role-based authorization

## Future Enhancements

- Course enrollment system
- Dashboard analytics
- File upload for assignments
- Grading system
- Notifications