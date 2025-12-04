import requests
import time
import sys

BASE_URL = "http://localhost:8000/api/v1"

def verify():
    print("Waiting for backend to start...")
    time.sleep(5) # Give backend time to start

    # 1. Score a URL
    print("Scoring test URL...")
    test_url = "http://test-db-integration.com"
    try:
        res = requests.post(f"{BASE_URL}/score", json={"url": test_url})
        res.raise_for_status()
        print("Score request successful.")
    except Exception as e:
        print(f"Score request failed: {e}")
        sys.exit(1)

    # 2. Check Recent Scans
    print("Checking recent scans...")
    try:
        res = requests.get(f"{BASE_URL}/score/recent")
        res.raise_for_status()
        scans = res.json()
        found = any(s["url"] == test_url for s in scans)
        if found:
            print("SUCCESS: Test URL found in recent scans (DB read/write working).")
        else:
            print("FAILURE: Test URL NOT found in recent scans.")
            sys.exit(1)
    except Exception as e:
        print(f"Recent scans request failed: {e}")
        sys.exit(1)

    # 3. Check Stats
    print("Checking stats...")
    try:
        res = requests.get(f"{BASE_URL}/stats")
        res.raise_for_status()
        stats = res.json()
        if stats["total_scans"] > 0:
            print(f"SUCCESS: Total scans > 0 ({stats['total_scans']}). Stats working.")
        else:
            print("FAILURE: Total scans is 0.")
            sys.exit(1)
    except Exception as e:
        print(f"Stats request failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify()
