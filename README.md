# 🦎 Chameleon Honeypot  
**Adaptive Scam Engagement & Intelligence Extraction API**

---

## What It Does

Chameleon Honeypot is an **agentic honeypot API** that simulates real human victims to **engage scammers**, delay them safely, and **extract actionable scam intelligence** such as UPI IDs, phone numbers, phishing links, and bank details.

Instead of simply blocking scams, it **learns from them**.

---

## Problem

Most anti-scam systems are reactive:
- They block messages
- They discard scammer data
- No intelligence is retained or reused

This allows scammers to repeatedly reuse the same payment IDs, links, and phone numbers.

---

## Solution

Chameleon Honeypot flips the approach:

1. Detects scam intent  
2. Responds using adaptive personas  
3. Keeps scammers engaged without escalation  
4. Extracts and structures scam indicators  

---

## Key Features

- Scam intent & pattern detection  
- Persona-based agent responses (elderly / student / professional)  
- Automatic extraction of:
  - UPI IDs  
  - Phone numbers  
  - Bank accounts & IFSC  
  - URLs & emails  
- Stateless REST API  
- API-key secured endpoint  

---

## API Endpoint

**POST** `/api/honeypot`

x-api-key: demo-honeypot-key-123
Content-Type: application/json


### Request Body
```json
{
  "sessionId": "session-001",
  "message": {
    "sender": "scammer",
    "text": "Your account will be blocked. Send money now.",
    "timestamp": "2024-02-01T10:00:00Z"
  },
  "conversationHistory": [],
  "metadata": {}
}

##Response
{
  "status": "success",
  "reply": "Oh no… this sounds serious. What should I do?",
  "extracted": {
    "upiIds": [],
    "phoneNumbers": [],
    "links": []
  }
}


#Architecture
Request
  ↓
Auth Check
  ↓
Scam Detection
  ↓
Persona Agent
  ↓
Intelligence Extraction
  ↓
JSON Response


#Run Locally
pip install fastapi uvicorn requests
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000


Open:
http://127.0.0.1:8000/docs


# Test with Official Honeypot Tester:
python test_endpoint.py http://127.0.0.1:8000 demo-honeypot-key-123


# Expected output:
[PASS] API responded successfully.


#Ethics & Safety
Defensive engagement only
No impersonation of authorities
No hacking or exploitation
Extracts only scammer-provided data
Designed for research, prevention, and awareness.


#Future Scope
* Multilingual personas
* ML-based scam classification
* Persistent intelligence storage
* Analyst dashboard


#Built for the GUVI Hackathon
Focused on practical defense, ethical design, and real-world scam intelligence.

