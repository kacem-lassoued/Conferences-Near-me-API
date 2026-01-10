
import requests
import json

BASE_URL = "http://localhost:5000"

def test_public_access():
    print("\n--- Testing Public Access ---")
    try:
        response = requests.get(f"{BASE_URL}/conferences")
        if response.status_code == 200:
            print("SUCCESS: Public access to conferences allowed.")
        else:
            print(f"FAILURE: Access denied? Status: {response.status_code}")
    except Exception as e:
        print(f"FAILURE: Could not connect: {e}")

def test_submission():
    print("\n--- Testing Anonymous Submission ---")
    payload = {
        "type": "new_conference",
        "payload": {
            "name": "Test Conf",
            "country": "Testland",
            "acronym": "TC"
        }
    }
    try:
        response = requests.post(f"{BASE_URL}/submissions", json=payload)
        if response.status_code == 201:
            print("SUCCESS: Anonymous submission accepted.")
        else:
            print(f"FAILURE: Submission failed. Status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"FAILURE: Could not connect: {e}")

def test_auth_and_admin():
    print("\n--- Testing Auth and Admin Access ---")
    
    # 1. Login with wrong password
    try:
        resp = requests.post(f"{BASE_URL}/login", json={"password": "wrong"})
        if resp.status_code == 401:
             print("SUCCESS: Wrong password rejected.")
        else:
             print(f"FAILURE: Wrong password accepted? {resp.status_code}")
    except: pass
    
    # 2. Login with correct password (default: adminpassword)
    try:
        resp = requests.post(f"{BASE_URL}/login", json={"password": "adminpassword"})
        if resp.status_code == 200:
            token = resp.json().get('access_token')
            print("SUCCESS: Admin login successful.")
            
            # 3. Access Pending (Protected)
            headers = {"Authorization": f"Bearer {token}"}
            pending_resp = requests.get(f"{BASE_URL}/admin/pending", headers=headers)
            if pending_resp.status_code == 200:
                 print(f"SUCCESS: Admin accessed pending list. Count: {len(pending_resp.json())}")
            else:
                 print(f"FAILURE: Admin denied access to pending? {pending_resp.status_code} - Body: {pending_resp.text}")
        else:
            print(f"FAILURE: Admin login failed. {resp.status_code}")
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    test_public_access()
    test_submission()
    test_auth_and_admin()
