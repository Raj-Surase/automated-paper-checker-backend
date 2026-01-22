# Automated Question Paper Checking Backend

This is a FastAPI-based backend for an Automated Question Paper Checking system.

## Features
- **Authentication**: JWT-based login and registration.
- **Dashboard**: Statistics for tests, subjects, students, and scores.
- **Subjects**: Full CRUD operations for managing subjects.
- **Students**: Full CRUD operations for managing students.
- **Tests**: Create tests, assign subjects and students, and define question papers.
- **Automated Checking**: Upload answer sheets and get automated marks based on predefined answers.
- **Teacher Profile**: Manage teacher information.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run the server: `uvicorn main:app --reload`

## API Documentation
Once the server is running, visit `http://localhost:8000/docs` for interactive Swagger UI.
