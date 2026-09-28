import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code} - {response.json()}")

def test_root():
    response = requests.get(f"{BASE_URL}/")
    print(f"Root endpoint: {response.status_code} - {response.json()}")

def test_signup():
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/signup", json=user_data)
    print(f"Signup: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        return response.json()
    else:
        print(f"Error: {response.text}")
        return None

def test_login():
    login_data = {
        "username": "test@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    print(f"Login: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        return response.json()["access_token"]
    else:
        print(f"Error: {response.text}")
        return None

if __name__ == "__main__":
    test_health()
    test_root()
    user = test_signup()
    if user:
        token = test_login()
        if token:
            print("\nAuthentication successful!")
        else:
            print("\nLogin failed")
    else:
        print("\nSignup failed")