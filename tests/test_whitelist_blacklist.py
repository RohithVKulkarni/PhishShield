"""
Test script for whitelist/blacklist functionality
"""

import requests
import json

API_URL = "http://localhost:8000/api/v1"

def test_whitelist_blacklist():
    print("=" * 60)
    print("Testing PhishShield Whitelist/Blacklist Feature")
    print("=" * 60)
    
    # Test 1: Add to whitelist
    print("\n1. Adding example.com to whitelist...")
    response = requests.post(
        f"{API_URL}/lists",
        json={
            "list_type": "whitelist",
            "pattern": "example.com",
            "note": "Trusted test site"
        }
    )
    print(f"   Status: {response.status_code}")
    if response.ok:
        print(f"   Added: {response.json()}")
    
    # Test 2: Add to blacklist
    print("\n2. Adding evil-phishing.xyz to blacklist...")
    response = requests.post(
        f"{API_URL}/lists",
        json={
            "list_type": "blacklist",
            "pattern": "evil-phishing.xyz",
            "note": "Known phishing site"
        }
    )
    print(f"   Status: {response.status_code}")
    if response.ok:
        print(f"   Added: {response.json()}")
    
    # Test 3: Get all lists
    print("\n3. Retrieving all lists...")
    response = requests.get(f"{API_URL}/lists")
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   Whitelist entries: {len(data['whitelist'])}")
        print(f"   Blacklist entries: {len(data['blacklist'])}")
    
    # Test 4: Scan whitelisted URL
    print("\n4. Scanning whitelisted URL (http://example.com)...")
    response = requests.post(
        f"{API_URL}/score",
        json={"url": "http://example.com"}
    )
    print(f"   Status: {response.status_code}")
    if response.ok:
        result = response.json()
        print(f"   Is Phishing: {result['is_phishing']}")
        print(f"   Score: {result['phishing_probability']}")
        print(f"   Reasons: {result['reasons']}")
    
    # Test 5: Scan blacklisted URL
    print("\n5. Scanning blacklisted URL (http://evil-phishing.xyz)...")
    response = requests.post(
        f"{API_URL}/score",
        json={"url": "http://evil-phishing.xyz"}
    )
    print(f"   Status: {response.status_code}")
    if response.ok:
        result = response.json()
        print(f"   Is Phishing: {result['is_phishing']}")
        print(f"   Score: {result['phishing_probability']}")
        print(f"   Reasons: {result['reasons']}")
    
    # Test 6: Check URL
    print("\n6. Checking if example.com is in any list...")
    response = requests.post(
        f"{API_URL}/lists/check?url=http://example.com"
    )
    print(f"   Status: {response.status_code}")
    if response.ok:
        result = response.json()
        print(f"   Matched: {result['matched']}")
        if result['matched']:
            print(f"   List Type: {result['list_type']}")
            print(f"   Pattern: {result['pattern']}")
    
    # Test 7: Export lists
    print("\n7. Exporting lists to JSON...")
    response = requests.get(f"{API_URL}/lists/export?format=json")
    print(f"   Status: {response.status_code}")
    if response.ok:
        export_data = response.json()
        print(f"   Export successful (length: {len(export_data['data'])} chars)")
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_whitelist_blacklist()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to backend. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"ERROR: {e}")
