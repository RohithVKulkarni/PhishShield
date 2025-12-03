import requests
import json

API_URL = "http://localhost:8000/api/v1"

def test_health():
    try:
        response = requests.get("http://localhost:8000/healthz")
        print(f"Health Check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health Check Failed: {e}")

def test_score_safe():
    payload = {"url": "https://google.com"}
    try:
        response = requests.post(f"{API_URL}/score", json=payload)
        print(f"Safe URL Check: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Safe URL Check Failed: {e}")

def test_score_phish():
    payload = {"url": "http://secure-login-phish.com"}
    try:
        response = requests.post(f"{API_URL}/score", json=payload)
        print(f"Phish URL Check: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Phish URL Check Failed: {e}")

if __name__ == "__main__":
    print("Running Tests...")
    test_health()
    print("-" * 20)
    test_score_safe()
    print("-" * 20)
    test_score_phish()
