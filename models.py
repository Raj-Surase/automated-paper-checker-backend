from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table, JSON
from sqlalchemy.orm import relationship
from database import Base

# Association table for Test and Student
test_students = Table(
    'test_students',
    Base.metadata,
    Column('test_id', Integer, ForeignKey('tests.id')),
    Column('student_id', Integer, ForeignKey('students.id'))
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(150))
    mobile = Column(String(15))
    subjects = relationship("Subject", back_populates="teacher")

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    teacher = relationship("User", back_populates="subjects")
    tests = relationship("Test", back_populates="subject")

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    roll_no = Column(String(50), unique=True, index=True)
    name = Column(String(150))
    mobile = Column(String(15))
    tests = relationship("Test", secondary=test_students, back_populates="students")
    results = relationship("TestResult", back_populates="student")

class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150))
    max_marks = Column(Float)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    question_paper = Column(JSON)

    subject = relationship("Subject", back_populates="tests")
    students = relationship("Student", secondary=test_students, back_populates="tests")
    results = relationship("TestResult", back_populates="test")

class TestResult(Base):
    __tablename__ = "test_results"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    score = Column(Float)
    student_answers = Column(JSON)
    answer_sheet_url = Column(String(512))

    test = relationship("Test", back_populates="results")
    student = relationship("Student", back_populates="results")
