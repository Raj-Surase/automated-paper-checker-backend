from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import models, schemas, auth, database
import models, schemas, auth, database, utils
from database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Automated Question Paper Checking System")

# --- Authentication ---

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email, 
        hashed_password=hashed_password, 
        full_name=user.full_name,
        mobile=user.mobile
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Subjects CRUD ---

@app.post("/subjects/", response_model=schemas.Subject)
def create_subject(subject: schemas.SubjectCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_subject = models.Subject(**subject.dict(), teacher_id=current_user.id)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

@app.get("/subjects/", response_model=List[schemas.Subject])
def read_subjects(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Subject).filter(models.Subject.teacher_id == current_user.id).all()

@app.put("/subjects/{subject_id}", response_model=schemas.Subject)
def update_subject(subject_id: int, subject: schemas.SubjectCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_subject = db.query(models.Subject).filter(models.Subject.id == subject_id, models.Subject.teacher_id == current_user.id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    db_subject.name = subject.name
    db.commit()
    db.refresh(db_subject)
    return db_subject

@app.delete("/subjects/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_subject = db.query(models.Subject).filter(models.Subject.id == subject_id, models.Subject.teacher_id == current_user.id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    db.delete(db_subject)
    db.commit()
    return {"message": "Subject deleted"}

# --- Students CRUD ---

@app.post("/students/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_student = models.Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/students/", response_model=List[schemas.Student])
def read_students(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Student).all()

@app.put("/students/{student_id}", response_model=schemas.Student)
def update_student(student_id: int, student: schemas.StudentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    for key, value in student.dict().items():
        setattr(db_student, key, value)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(db_student)
    db.commit()
    return {"message": "Student deleted"}

# --- Tests CRUD ---

@app.post("/tests/", response_model=schemas.Test)
def create_test(test: schemas.TestCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Verify subject belongs to teacher
    subject = db.query(models.Subject).filter(models.Subject.id == test.subject_id, models.Subject.teacher_id == current_user.id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found or not authorized")
    
    # Get students
    students = db.query(models.Student).filter(models.Student.id.in_(test.student_ids)).all()
    
    # Create test
    db_test = models.Test(
        title=test.title,
        max_marks=test.max_marks,
        subject_id=test.subject_id,
        question_paper=[q.dict() for q in test.question_paper]
    )
    db_test.students = students
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

@app.get("/tests/", response_model=List[schemas.Test])
def read_tests(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Test).join(models.Subject).filter(models.Subject.teacher_id == current_user.id).all()

@app.delete("/tests/{test_id}")
def delete_test(test_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_test = db.query(models.Test).join(models.Subject).filter(models.Test.id == test_id, models.Subject.teacher_id == current_user.id).first()
    if not db_test:
        raise HTTPException(status_code=404, detail="Test not found")
    db.delete(db_test)
    db.commit()
    return {"message": "Test deleted"}

@app.put("/tests/{test_id}", response_model=schemas.Test)
def update_test(test_id: int, test: schemas.TestCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Check if test exists and belongs to user's subject
    db_test = db.query(models.Test).join(models.Subject).filter(models.Test.id == test_id, models.Subject.teacher_id == current_user.id).first()
    if not db_test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Verify new subject belongs to teacher
    subject = db.query(models.Subject).filter(models.Subject.id == test.subject_id, models.Subject.teacher_id == current_user.id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found or not authorized")

    # Update fields
    db_test.title = test.title
    db_test.max_marks = test.max_marks
    db_test.subject_id = test.subject_id
    db_test.question_paper = [q.dict() for q in test.question_paper]
    
    # Update students
    students = db.query(models.Student).filter(models.Student.id.in_(test.student_ids)).all()
    db_test.students = students

    db.commit()
    db.refresh(db_test)
    return db_test

    return db_test

@app.post("/tests/upload-pdf/", response_model=Dict[str, Any])
async def parse_pdf_create_test(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Parses a PDF file to extract Questions and Answers for creating a Test.
    The PDF should have lines starting with 'Q:' and 'A:'.
    """
    try:
        # Save temp file
        file_path = os.path.join(UPLOAD_DIR, f"temp_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Extract text
        text = utils.extract_text_from_pdf(file_path)
        
        # Parse Q&A
        qa_pairs = utils.parse_qa_from_text(text)
        
        # Cleanup
        os.remove(file_path)
        
        # Assign default marks (can be edited on frontend)
        extracted_questions = []
        for pair in qa_pairs:
            extracted_questions.append({
                "question": pair["question"],
                "answer": pair["answer"],
                "marks": 1.0 # Default mark
            })
            
        return {"extracted_data": extracted_questions, "raw_text_preview": text[:500]}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing PDF: {str(e)}")

# --- Dashboard ---

@app.get("/dashboard/", response_model=schemas.DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Total counts
    total_subjects = db.query(models.Subject).filter(models.Subject.teacher_id == current_user.id).count()
    
    test_query = db.query(models.Test).join(models.Subject).filter(models.Subject.teacher_id == current_user.id)
    total_tests = test_query.count()
    
    # Total students assigned to this teacher's tests (unique)
    total_students = db.query(models.Student).join(models.Student.tests).join(models.Test.subject).filter(models.Subject.teacher_id == current_user.id).distinct().count()
    
    # Average score across all tests of this teacher
    results = db.query(models.TestResult).join(models.Test).join(models.Subject).filter(models.Subject.teacher_id == current_user.id).all()
    avg_score = sum([r.score for r in results]) / len(results) if results else 0.0
    
    # Recent tests
    recent_tests = test_query.order_by(models.Test.id.desc()).limit(5).all()
    recent_tests_data = [{"id": t.id, "title": t.title, "subject": t.subject.name} for t in recent_tests]
    
    # Recent students (who took tests)
    recent_results = db.query(models.TestResult).join(models.Test).join(models.Subject).filter(models.Subject.teacher_id == current_user.id).order_by(models.TestResult.id.desc()).limit(5).all()
    recent_students_data = [{"id": r.student.id, "name": r.student.name, "test": r.test.title, "score": r.score} for r in recent_results]
    
    return {
        "total_tests": total_tests,
        "total_subjects": total_subjects,
        "total_students": total_students,
        "average_score": avg_score,
        "recent_tests": recent_tests_data,
        "recent_students": recent_students_data
    }

# --- Teacher Profile ---

@app.get("/profile/", response_model=schemas.User)
def get_profile(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.put("/profile/", response_model=schemas.User)
def update_profile(user_update: schemas.UserBase, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    current_user.full_name = user_update.full_name
    current_user.mobile = user_update.mobile
    current_user.email = user_update.email
    db.commit()
    db.refresh(current_user)
    return current_user

import os
import shutil
from typing import Dict

# Create uploads directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Answer Sheet Processing ---

def check_answers(student_answers: List[Dict[str, str]], question_paper: List[Dict[str, Any]]) -> tuple[float, List[Dict[str, Any]]]:
    """
    Simple automated checking logic. 
    In a real scenario, this would use OCR and NLP.
    For this implementation, we'll compare strings.
    """
    total_score = 0.0
    processed_answers = []
    
    # Create a map for quick lookup
    paper_map = {q['question']: q for q in question_paper}
    
    for ans in student_answers:
        q_text = ans.get('question')
        s_ans = ans.get('answer', '').strip().lower()
        
        if q_text in paper_map:
            correct_ans = paper_map[q_text]['answer'].strip().lower()
            marks = paper_map[q_text]['marks']
            
            # Simple exact match or keyword match
            if s_ans == correct_ans:
                obtained = marks
            elif correct_ans in s_ans: # Partial match logic
                obtained = marks * 0.8
            else:
                obtained = 0.0
                
            total_score += obtained
            processed_answers.append({
                "question": q_text,
                "student_answer": s_ans,
                "correct_answer": correct_ans,
                "marks_obtained": obtained,
                "max_marks": marks
            })
            
    return total_score, processed_answers

@app.post("/tests/{test_id}/students/{student_id}/upload-answer-sheet/")
async def upload_answer_sheet(
    test_id: int, 
    student_id: int, 
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verify test and student
    test = db.query(models.Test).filter(models.Test.id == test_id).first()
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    
    if not test or not student:
        raise HTTPException(status_code=404, detail="Test or Student not found")
        
    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"test_{test_id}_student_{student_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Parse PDF Answer Sheet
    try:
        # Extract text
        text = utils.extract_text_from_pdf(file_path)
        
        # Parse Q&A
        parsed_student_answers = utils.parse_qa_from_text(text)
        
        # Check against Test Questions
        score, processed_results = check_answers(parsed_student_answers, test.question_paper)
        
    except Exception as e:
        # Fallback or Error
        print(f"Error parsing PDF: {e}")
        # If parsing fails, we could either error out or return 0
        raise HTTPException(status_code=400, detail=f"Failed to parse Answer Sheet PDF: {str(e)}")
    
    # Save result
    
    # Save result
    db_result = models.TestResult(
        test_id=test_id,
        student_id=student_id,
        score=score,
        student_answers=processed_results,
        answer_sheet_url=file_path
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    return {
        "message": "Answer sheet processed successfully",
        "score": score,
        "results": processed_results,
        "file_path": file_path
    }

@app.get("/tests/{test_id}/results/", response_model=List[schemas.TestResult])
def get_test_results(test_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.TestResult).filter(models.TestResult.test_id == test_id).all()

@app.put("/results/{result_id}", response_model=schemas.TestResult)
def update_result(
    result_id: int, 
    result_update: schemas.TestResultBase, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    db_result = db.query(models.TestResult).filter(models.TestResult.id == result_id).first()
    if not db_result:
        raise HTTPException(status_code=404, detail="Result not found")
        
    # Verify teacher owns the test
    # (Optional strict check: ensure current_user is the teacher of the subject of the test of this result)
    
    db_result.score = result_update.score
    db_result.student_answers = result_update.student_answers
    
    db.commit()
    db.refresh(db_result)
    return db_result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
