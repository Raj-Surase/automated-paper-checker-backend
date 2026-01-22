import requests
import json

# Login to get token
base_url = "http://127.0.0.1:8000"

def get_token():
    try:
        response = requests.post(f"{base_url}/token", data={"username": "teacher@example.com", "password": "password123"})
        if response.status_code == 200:
            return response.json()["access_token"]
    except:
        pass
    
    # Register if login fails
    requests.post(f"{base_url}/register", json={
        "email": "teacher@example.com", 
        "password": "password123", 
        "full_name": "Teacher", 
        "mobile": "1234567890"
    })
    response = requests.post(f"{base_url}/token", data={"username": "teacher@example.com", "password": "password123"})
    return response.json()["access_token"]

token = get_token()
headers = {"Authorization": f"Bearer {token}"}

# 1. Test PDF Parsing for creating a Test
print("\n--- Testing PDF Upload for Test Creation ---")
with open("sample_questions.pdf", "rb") as f:
    files = {"file": ("sample_questions.pdf", f, "application/pdf")}
    res = requests.post(f"{base_url}/tests/upload-pdf/", files=files, headers=headers)
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        extracted = res.json()["extracted_data"]
        print(f"Extracted: {json.dumps(extracted, indent=2)}")
        
        # Create the test using this data
        subject_res = requests.get(f"{base_url}/subjects/", headers=headers)
        if not subject_res.json():
            requests.post(f"{base_url}/subjects/", json={"name": "Science"}, headers=headers)
            subject_id = 1
        else:
            subject_id = subject_res.json()[0]["id"]
            
        test_data = {
            "title": "PDF Created Test",
            "max_marks": 100,
            "subject_id": subject_id,
            "question_paper": extracted,
            "student_ids": [] 
        }
        test_res = requests.post(f"{base_url}/tests/", json=test_data, headers=headers)
        print(f"Test Created: {test_res.status_code}")
        test_id = test_res.json().get("id")
    else:
        print(res.text)

# 2. Test Student Answer Sheet Upload
if 'test_id' in locals() and test_id:
    print("\n--- Testing Student Answer Sheet Upload ---")
    
    # Needs a student
    student_res = requests.get(f"{base_url}/students/", headers=headers)
    if not student_res.json():
        requests.post(f"{base_url}/students/", json={"roll_no": "102", "name": "Student A", "mobile": "999"}, headers=headers)
        student_id = 1
    else:
        student_id = student_res.json()[0]["id"]
        
    # Assign student to test (update test)
    # Get current test
    # test_data["student_ids"] = [student_id]
    # requests.put(f"{base_url}/tests/{test_id}", json=test_data, headers=headers) # Using the new PUT endpoint if available or recreating
    # Actually create_test assigns students. Let's create a NEW test with students.
    
    test_data["student_ids"] = [student_id]
    test_res_2 = requests.post(f"{base_url}/tests/", json=test_data, headers=headers)
    test_id_2 = test_res_2.json().get("id")

    with open("sample_student_answers.pdf", "rb") as f:
        files = {"file": ("sample_student_answers.pdf", f, "application/pdf")}
        upload_res = requests.post(f"{base_url}/tests/{test_id_2}/students/{student_id}/upload-answer-sheet/", files=files, headers=headers)
        print(f"Upload Status: {upload_res.status_code}")
        print(json.dumps(upload_res.json(), indent=2))
        
