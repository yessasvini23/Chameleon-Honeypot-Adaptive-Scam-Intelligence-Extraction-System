#!/usr/bin/env python3
"""
Test script for Chameleon-Honeypot API
"""

import requests
import json
import hashlib
import time

# Configuration
API_URL = "http://localhost:8000"
SECRET = b"CHAMELEON_HONEYPOT_SECRET_2024"
API_KEY = hashlib.sha256(SECRET).hexdigest()

def test_health_check():
    """Test health endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_banking_scam():
    """Test banking scam detection and engagement"""
    print("\n=== Testing Banking Scam Detection ===")
    
    session_id = f"test-banking-{int(time.time())}"
    
    messages = [
        "Hello, this is from SBI bank customer care",
        "Your account has been flagged for suspicious activity",
        "We need to update your KYC details immediately or your account will be blocked",
        "Please provide your account number for verification",
        "Also share your registered mobile number and email"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n--- Turn {i} ---")
        
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": message,
                "timestamp": f"2024-02-01T10:{i:02d}:00Z"
            },
            "conversationHistory": []
        }
        
        response = requests.post(
            f"{API_URL}/api/honeypot",
            json=payload,
            headers={"X-API-Key": API_KEY}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Agent Reply: {result['reply']}")
            if 'internal_metrics' in result:
                print(f"Metrics: {json.dumps(result['internal_metrics'], indent=2)}")
        else:
            print(f"Error: {response.text}")
        
        time.sleep(0.5)
    
    return response.status_code == 200

def test_upi_scam():
    """Test UPI fraud detection"""
    print("\n=== Testing UPI Scam Detection ===")
    
    session_id = f"test-upi-{int(time.time())}"
    
    messages = [
        "Your UPI payment of Rs 5000 has failed",
        "To get refund, please send Rs 1 to verify account",
        "Send to ramesh.scammer@paytm",
        "Call us at 9876543210 for assistance"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n--- Turn {i} ---")
        
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": message,
                "timestamp": f"2024-02-01T11:{i:02d}:00Z"
            },
            "conversationHistory": []
        }
        
        response = requests.post(
            f"{API_URL}/api/honeypot",
            json=payload,
            headers={"X-API-Key": API_KEY}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Agent Reply: {result['reply']}")
        
        time.sleep(0.5)
    
    return response.status_code == 200

def test_phishing_scam():
    """Test phishing detection"""
    print("\n=== Testing Phishing Scam Detection ===")
    
    session_id = f"test-phishing-{int(time.time())}"
    
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Your account security update required. Click here: https://fake-bank.xyz/verify",
            "timestamp": "2024-02-01T12:00:00Z"
        },
        "conversationHistory": []
    }
    
    response = requests.post(
        f"{API_URL}/api/honeypot",
        json=payload,
        headers={"X-API-Key": API_KEY}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Agent Reply: {result['reply']}")
    
    return response.status_code == 200

def test_stats():
    """Test statistics endpoint"""
    print("\n=== Testing Statistics ===")
    
    response = requests.get(
        f"{API_URL}/stats",
        headers={"X-API-Key": API_KEY}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Stats: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def test_invalid_api_key():
    """Test invalid API key handling"""
    print("\n=== Testing Invalid API Key ===")
    
    payload = {
        "sessionId": "test-invalid",
        "message": {
            "sender": "scammer",
            "text": "Test message",
            "timestamp": "2024-02-01T10:00:00Z"
        },
        "conversationHistory": []
    }
    
    response = requests.post(
        f"{API_URL}/api/honeypot",
        json=payload,
        headers={"X-API-Key": "invalid_key"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    return response.status_code == 401

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Chameleon-Honeypot API Test Suite")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Banking Scam", test_banking_scam),
        ("UPI Scam", test_upi_scam),
        ("Phishing Scam", test_phishing_scam),
        ("Statistics", test_stats),
        ("Invalid API Key", test_invalid_api_key)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} failed with error: {e}")
            results[test_name] = False
        
        time.sleep(1)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
