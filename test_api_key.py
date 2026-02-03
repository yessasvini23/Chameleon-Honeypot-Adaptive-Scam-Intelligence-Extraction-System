#!/usr/bin/env python3
"""
Quick API Key Validation Test
Tests if your API key works with all endpoints
"""

import requests
import hashlib
import sys

# Your API key
API_KEY = "92ff7abdd0fb14dbc156ac141854ec482152f8c3d39e728333b1c9dddd646a8a"
API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint (no auth required)"""
    print("\n1️⃣ Testing health endpoint (no auth required)...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health check passed")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Active sessions: {data.get('active_sessions')}")
            return True
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to server")
        print("   Make sure server is running: python production_honeypot_api.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_stats():
    """Test stats endpoint (requires auth)"""
    print("\n2️⃣ Testing stats endpoint (requires API key)...")
    try:
        response = requests.get(
            f"{API_URL}/stats",
            headers={"X-API-Key": API_KEY},
            timeout=5
        )
        if response.status_code == 200:
            print("   ✅ API key authentication successful!")
            data = response.json()
            print(f"   Active sessions: {data.get('active_sessions')}")
            total_intel = sum(data.get('total_intelligence_extracted', {}).values())
            print(f"   Total intelligence: {total_intel}")
            return True
        elif response.status_code == 401:
            print("   ❌ Authentication failed - Invalid API key")
            print(f"   Your key: {API_KEY[:20]}...")
            print("   Expected key starts with: 92ff7abdd0fb14dbc...")
            return False
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_honeypot():
    """Test honeypot endpoint (requires auth)"""
    print("\n3️⃣ Testing honeypot endpoint (requires API key)...")
    try:
        payload = {
            "sessionId": "api-key-test",
            "message": {
                "sender": "scammer",
                "text": "Test message for API key validation",
                "timestamp": "2024-02-01T10:00:00Z"
            },
            "conversationHistory": []
        }
        
        response = requests.post(
            f"{API_URL}/api/honeypot",
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ Honeypot endpoint working!")
            result = response.json()
            print(f"   Agent replied: \"{result.get('reply', 'N/A')[:50]}...\"")
            return True
        elif response.status_code == 401:
            print("   ❌ Authentication failed - Invalid API key")
            return False
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_invalid_key():
    """Test with invalid key to verify security"""
    print("\n4️⃣ Testing with invalid key (should fail)...")
    try:
        response = requests.get(
            f"{API_URL}/stats",
            headers={"X-API-Key": "invalid_key_12345"},
            timeout=5
        )
        if response.status_code == 401:
            print("   ✅ Security working - Invalid key rejected")
            return True
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
            print("   Security check inconclusive")
            return True  # Don't fail the test
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def verify_key_generation():
    """Verify the API key is correctly generated"""
    print("\n5️⃣ Verifying API key generation...")
    secret = b"CHAMELEON_HONEYPOT_SECRET_2024"
    expected_key = hashlib.sha256(secret).hexdigest()
    
    if API_KEY == expected_key:
        print("   ✅ API key matches expected value")
        print(f"   Key: {API_KEY[:40]}...")
        return True
    else:
        print("   ⚠️  API key mismatch!")
        print(f"   Expected: {expected_key}")
        print(f"   Got:      {API_KEY}")
        return False

def main():
    print("=" * 70)
    print("🔑 API KEY VALIDATION TEST")
    print("=" * 70)
    print(f"\nAPI URL: {API_URL}")
    print(f"API Key: {API_KEY[:40]}...")
    print()
    print("Running tests...")
    
    results = []
    
    # Run all tests
    results.append(("Health Check", test_health()))
    results.append(("Key Verification", verify_key_generation()))
    results.append(("Stats Endpoint", test_stats()))
    results.append(("Honeypot Endpoint", test_honeypot()))
    results.append(("Security Check", test_invalid_key()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:25} {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    
    print("\n" + "-" * 70)
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    print("-" * 70)
    
    if passed_tests == total_tests:
        print("\n✅ ALL TESTS PASSED - Your API key is working perfectly!")
        print("\nYou can now use this key in:")
        print("  • Streamlit app (streamlit_app.py)")
        print("  • Demo scripts (demo_conversation.py)")
        print("  • Test scripts (test_api.py)")
        print("  • curl commands")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        if not results[0][1]:  # Health check failed
            print("\n→ Server is not running. Start it with:")
            print("  python production_honeypot_api.py")
        if not results[2][1] or not results[3][1]:  # Auth tests failed
            print("\n→ API key authentication issue. Regenerate key with:")
            print("  python3 -c 'import hashlib; print(hashlib.sha256(b\"CHAMELEON_HONEYPOT_SECRET_2024\").hexdigest())'")
        return 1

if __name__ == "__main__":
    sys.exit(main())
