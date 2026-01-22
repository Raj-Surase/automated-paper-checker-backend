from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

# User/Teacher Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    mobile: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Subject Schemas
class SubjectBase(BaseModel):
    name: str

class SubjectCreate(SubjectBase):
    pass

class Subject(SubjectBase):
    id: int
    teacher_id: int
    class Config:
        from_attributes = True

# Student Schemas
class StudentBase(BaseModel):
    roll_no: str
    name: str
    mobile: str

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    id: int
    class Config:
        from_attributes = True

# Test Schemas
class Question(BaseModel):
    question: str
    answer: str
    marks: float

class TestBase(BaseModel):
    title: str
    max_marks: float
    subject_id: int
    question_paper: List[Question]

class TestCreate(TestBase):
    student_ids: List[int]

class Test(TestBase):
    id: int
    class Config:
        from_attributes = True

# Test Result Schemas
class TestResultBase(BaseModel):
    test_id: int
    student_id: int
    score: float
    student_answers: List[Dict[str, Any]]
    answer_sheet_url: Optional[str] = None

class TestResult(TestResultBase):
    id: int
    class Config:
        from_attributes = True

# Dashboard Schema
class DashboardStats(BaseModel):
    total_tests: int
    total_subjects: int
    total_students: int
    average_score: float
    recent_tests: List[Dict[str, Any]]
    recent_students: List[Dict[str, Any]]
