"""
production_honeypot_api.py
Chameleon-Honeypot: Production-Ready Scam Intelligence Extraction System
"""

from fastapi import FastAPI, Header, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
import uvicorn
import hashlib
import requests
import re
import time
import logging
import json
from datetime import datetime
from collections import defaultdict
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('honeypot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Chameleon-Honeypot API",
    description="Adaptive Multi-Persona Scam Intelligence Extraction System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATA MODELS
# ============================================================================

class Message(BaseModel):
    sender: str
    text: str
    timestamp: str
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Message text cannot be empty')
        return v

class ConversationInput(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message] = []
    metadata: Optional[Dict[str, Any]] = {}
    
    @validator('sessionId')
    def session_id_must_be_valid(cls, v):
        if not v or len(v) < 10:
            raise ValueError('Session ID must be at least 10 characters')
        return v

class AgentOutput(BaseModel):
    status: str
    reply: str
    internal_metrics: Optional[Dict[str, Any]] = {}

class FinalIntelligence(BaseModel):
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: Dict[str, Any]
    agentNotes: str

# ============================================================================
# SCAM DETECTION ENGINE
# ============================================================================

class ScamDetector:
    """Multi-layer scam detection with pattern matching and scoring"""
    
    def __init__(self):
        self.urgency_patterns = [
            r'\b(immediate|urgent|now|asap|today|within.*hours?)\b',
            r'\b(expire|expiring|last chance|limited time)\b',
            r'\b(act fast|hurry|quick|don\'t wait)\b'
        ]
        
        self.authority_patterns = [
            r'\b(bank|SBI|HDFC|ICICI|Axis|RBI)\b',
            r'\b(government|police|court|CBI|income tax)\b',
            r'\b(official|authorized|verified)\b'
        ]
        
        self.threat_patterns = [
            r'\b(block|suspend|freeze|close|terminate)\b',
            r'\b(legal action|FIR|case|arrest|fine)\b',
            r'\b(penalty|charge|consequences)\b'
        ]
        
        self.reward_patterns = [
            r'\b(prize|reward|won|winner|lottery)\b',
            r'\b(cashback|bonus|offer|discount)\b',
            r'\b(free|complimentary|gift)\b'
        ]
        
        self.personal_info_patterns = [
            r'\b(account number|IFSC|CVV|PIN|password)\b',
            r'\b(OTP|verification code|security code)\b',
            r'\b(card details|expiry|CVV)\b'
        ]
        
        self.scam_type_keywords = {
            "banking_scam": ["KYC", "account block", "deactivate", "verify account", "update details"],
            "upi_fraud": ["payment failed", "refund", "UPI", "transaction", "money transfer"],
            "phishing": ["click here", "verify", "suspicious activity", "confirm identity"],
            "investment_scam": ["guaranteed returns", "investment", "profit", "scheme", "opportunity"],
            "job_scam": ["work from home", "earn", "registration fee", "joining bonus"],
            "lottery_scam": ["won", "lottery", "prize", "claim", "lucky draw"],
            "tech_support": ["virus", "infected", "expired", "renewal", "antivirus"]
        }
    
    def detect_scam(self, message: str, history: List[Message], metadata: Dict) -> Dict:
        """Comprehensive scam detection with confidence scoring"""
        text_lower = message.lower()
        
        # Calculate pattern scores
        urgency_score = self._pattern_score(text_lower, self.urgency_patterns)
        authority_score = self._pattern_score(text_lower, self.authority_patterns)
        threat_score = self._pattern_score(text_lower, self.threat_patterns)
        reward_score = self._pattern_score(text_lower, self.reward_patterns)
        personal_info_score = self._pattern_score(text_lower, self.personal_info_patterns)
        
        # Weighted scoring
        total_score = (
            urgency_score * 0.2 +
            authority_score * 0.25 +
            threat_score * 0.25 +
            reward_score * 0.15 +
            personal_info_score * 0.15
        )
        
        # Behavioral analysis
        if history:
            behavioral_score = self._analyze_behavior(history)
            total_score = (total_score * 0.7) + (behavioral_score * 0.3)
        
        # Detect scam type
        scam_type = self._classify_scam_type(message)
        
        # Recommend persona
        recommended_persona = self._recommend_persona(scam_type, total_score)
        
        is_scam = total_score > 0.6
        
        result = {
            "is_scam": is_scam,
            "confidence": min(total_score, 1.0),
            "scam_type": scam_type if is_scam else None,
            "recommended_persona": recommended_persona if is_scam else None,
            "scores": {
                "urgency": urgency_score,
                "authority": authority_score,
                "threat": threat_score,
                "reward": reward_score,
                "personal_info": personal_info_score
            }
        }
        
        logger.info(f"Scam detection result: {json.dumps(result, indent=2)}")
        return result
    
    def _pattern_score(self, text: str, patterns: List[str]) -> float:
        """Calculate pattern matching score"""
        matches = sum(1 for pattern in patterns if re.search(pattern, text, re.IGNORECASE))
        return min(matches / len(patterns), 1.0) if patterns else 0.0
    
    def _analyze_behavior(self, history: List[Message]) -> float:
        """Analyze conversation behavior for scam indicators"""
        if len(history) < 2:
            return 0.0
        
        info_requests = sum(
            1 for msg in history 
            if any(keyword in msg.text.lower() for keyword in ['your', 'send', 'provide', 'share'])
        )
        
        behavioral_score = (info_requests / len(history)) * 0.5
        return min(behavioral_score, 1.0)
    
    def _classify_scam_type(self, message: str) -> str:
        """Classify the type of scam"""
        text_lower = message.lower()
        
        scores = {}
        for scam_type, keywords in self.scam_type_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            scores[scam_type] = score
        
        if not any(scores.values()):
            return "general_scam"
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _recommend_persona(self, scam_type: str, confidence: float) -> str:
        """Recommend appropriate persona based on scam type"""
        persona_mapping = {
            "banking_scam": "elderly",
            "upi_fraud": "professional",
            "phishing": "student",
            "investment_scam": "professional",
            "job_scam": "student",
            "lottery_scam": "elderly",
            "tech_support": "elderly",
            "general_scam": "professional"
        }
        
        return persona_mapping.get(scam_type, "professional")

# ============================================================================
# INTELLIGENCE EXTRACTOR
# ============================================================================

class IntelligenceExtractor:
    """Advanced pattern-based intelligence extraction"""
    
    def __init__(self):
        self.patterns = {
            "upi_id": [
                r'([a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64})',
                r'([0-9]{10}@[a-zA-Z]{2,10})',
                r'([a-zA-Z0-9]+@paytm|@phonepe|@googlepay)',
            ],
            "bank_account": [
                r'\b([0-9]{9,18})\b',
                r'([A-Z]{4}0[A-Z0-9]{6})',
            ],
            "phone_number": [
                r'\b([789]\d{9})\b',
                r'(\+91[-\s]?[789]\d{9})',
            ],
            "phishing_link": [
                r'(https?://[^\s]+)',
                r'(bit\.ly/[a-zA-Z0-9]+)',
            ],
            "email": [
                r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
            ],
        }
    
    def extract_all(self, text: str) -> Dict[str, List[str]]:
        """Extract all intelligence patterns from text"""
        intelligence = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "emails": [],
            "suspiciousKeywords": []
        }
        
        for category, patterns in self.patterns.items():
            extracted = []
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                extracted.extend(matches)
            
            unique_items = list(set(extracted))
            
            key_mapping = {
                "upi_id": "upiIds",
                "bank_account": "bankAccounts",
                "phishing_link": "phishingLinks",
                "phone_number": "phoneNumbers",
                "email": "emails"
            }
            
            output_key = key_mapping.get(category, category)
            intelligence[output_key].extend(unique_items)
        
        logger.info(f"Extracted intelligence: {json.dumps(intelligence, indent=2)}")
        return intelligence

# ============================================================================
# CHAMELEON AGENT
# ============================================================================

class ChameleonAgent:
    """Autonomous conversational agent with persona management"""
    
    def __init__(self):
        self.persona_profiles = {
            "elderly": {
                "type": "elderly",
                "name": "Ramesh Kumar",
                "age": 68,
                "responses": {
                    "initial": [
                        "Hello? Who is this calling?",
                        "I don't understand what you're saying",
                        "Can you speak more slowly please?"
                    ],
                    "concerned": [
                        "Oh dear, that sounds serious. What should I do?",
                        "I'm worried now. Should I tell my son?",
                        "This has never happened before. Is it really from the bank?"
                    ],
                    "compliant": [
                        "Okay, I'll do whatever you say. Just help me fix this",
                        "I don't want any problems. Please guide me",
                        "Should I give you my account number? Which one?"
                    ],
                    "hesitant": [
                        "Wait, I should ask my son first...",
                        "Can I call you back? I need to check something",
                        "Are you sure this is safe?"
                    ]
                }
            },
            "student": {
                "type": "student",
                "name": "Priya Sharma",
                "age": 22,
                "responses": {
                    "initial": [
                        "Hey, what's this about?",
                        "How did you get my number?",
                        "This seems weird, can you prove you're legit?"
                    ],
                    "skeptical": [
                        "Lol, is this a scam? This sounds too good to be true",
                        "I've heard about these phishing attempts...",
                        "Why would the bank contact me like this?"
                    ],
                    "curious": [
                        "Okay I'm listening, what exactly is the issue?",
                        "What do I need to do? I'm kinda busy rn",
                        "How long will this take?"
                    ],
                    "defensive": [
                        "Wait, I'm not giving out my details just like that",
                        "Can I verify this first? What's your employee ID?",
                        "I'll call the bank directly, thanks"
                    ]
                }
            },
            "professional": {
                "type": "professional",
                "name": "Arun Mehra",
                "age": 42,
                "responses": {
                    "initial": [
                        "Good afternoon. What is this regarding?",
                        "Could you please state your purpose?",
                        "I'd like to verify your credentials first"
                    ],
                    "cautious": [
                        "I appreciate you reaching out. What's the ticket number?",
                        "Could you provide your employee ID and department?",
                        "Let me check this with my relationship manager"
                    ],
                    "procedural": [
                        "What are the official payment coordinates?",
                        "Please share the documentation for this",
                        "I'll need this in writing before proceeding"
                    ],
                    "verification": [
                        "I'd like to call the main office to confirm this",
                        "This doesn't follow standard banking procedure",
                        "Please provide an official email address I can verify"
                    ]
                }
            }
        }
        
        self.current_persona = None
        self.conversation_state = "initial"
        self.turn_count = 0
        
    def select_persona(self, persona_type: str):
        """Select and activate a persona"""
        self.current_persona = self.persona_profiles.get(persona_type, self.persona_profiles["professional"])
        logger.info(f"Activated persona: {self.current_persona['name']} ({persona_type})")
    
    def generate_response(self, message: str, history: List[Message], scam_type: str) -> Dict:
        """Generate contextually appropriate response"""
        self.turn_count += 1
        
        self._update_state(message, self.turn_count)
        
        response_pool = self.current_persona["responses"].get(
            self.conversation_state, 
            self.current_persona["responses"]["initial"]
        )
        
        response_text = random.choice(response_pool)
        
        return {
            "status": "success",
            "reply": response_text,
            "internal_state": {
                "persona": self.current_persona["name"],
                "conversation_state": self.conversation_state,
                "turn_count": self.turn_count
            }
        }
    
    def _update_state(self, message: str, turn: int):
        """Update conversation state based on context"""
        message_lower = message.lower()
        
        if turn <= 2:
            self.conversation_state = "initial"
        elif any(word in message_lower for word in ["urgent", "immediately", "now"]):
            self.conversation_state = "concerned" if self.current_persona["type"] == "elderly" else "cautious"
        elif any(word in message_lower for word in ["account", "number", "details"]):
            self.conversation_state = "compliant" if self.current_persona["type"] == "elderly" else "verification"
        elif turn > 10:
            self.conversation_state = "hesitant" if self.current_persona["type"] == "elderly" else "defensive"
    
    def generate_summary(self) -> str:
        """Generate summary of agent's interaction"""
        return f"Agent {self.current_persona['name']} engaged for {self.turn_count} turns. " \
               f"Final state: {self.conversation_state}. Intelligence extraction attempted."

# ============================================================================
# SESSION MANAGER
# ============================================================================

class SessionManager:
    """Manages conversation sessions and state"""
    
    def __init__(self):
        self.sessions = {}
        self.max_session_duration = 300
        
    def get_or_create(self, session_id: str) -> Dict:
        """Get existing session or create new one"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "detector": ScamDetector(),
                "agent": ChameleonAgent(),
                "extractor": IntelligenceExtractor(),
                "message_count": 0,
                "scam_detected": False,
                "scam_type": None,
                "intelligence": {
                    "bankAccounts": [],
                    "upiIds": [],
                    "phishingLinks": [],
                    "phoneNumbers": [],
                    "emails": [],
                    "suspiciousKeywords": []
                },
                "created_at": time.time(),
                "last_activity": time.time()
            }
            logger.info(f"Created new session: {session_id}")
        else:
            self.sessions[session_id]["last_activity"] = time.time()
        
        return self.sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = time.time()
        expired = [
            sid for sid, session in self.sessions.items()
            if current_time - session["last_activity"] > self.max_session_duration
        ]
        
        for sid in expired:
            del self.sessions[sid]
            logger.info(f"Cleaned up expired session: {sid}")
    
    def remove_session(self, session_id: str):
        """Remove a specific session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Removed session: {session_id}")

session_manager = SessionManager()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.post("/api/honeypot", response_model=AgentOutput)
async def honeypot_endpoint(
    data: ConversationInput,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(None)
):
    """Main honeypot endpoint for scam detection and agent engagement"""
    try:
        if not validate_api_key(x_api_key):
            logger.warning(f"Invalid API key attempt for session {data.sessionId}")
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        session = session_manager.get_or_create(data.sessionId)
        session["message_count"] += 1
        
        logger.info(f"Processing message {session['message_count']} for session {data.sessionId}")
        
        if not session["scam_detected"]:
            detection_result = session["detector"].detect_scam(
                data.message.text,
                data.conversationHistory,
                data.metadata
            )
            
            if detection_result["is_scam"]:
                session["scam_detected"] = True
                session["scam_type"] = detection_result["scam_type"]
                session["agent"].select_persona(detection_result["recommended_persona"])
                logger.info(f"Scam detected in session {data.sessionId}: {detection_result['scam_type']}")
        
        if session["scam_detected"]:
            response = session["agent"].generate_response(
                data.message.text,
                data.conversationHistory,
                session["scam_type"]
            )
            
            extracted = session["extractor"].extract_all(data.message.text)
            
            for key, values in extracted.items():
                if values:
                    session["intelligence"][key] = list(set(
                        session["intelligence"].get(key, []) + values
                    ))
            
            if should_end_engagement(session):
                background_tasks.add_task(send_final_report, data.sessionId, session)
                response["reply"] += " I think I should verify this at the bank branch. Thank you."
                logger.info(f"Ending engagement for session {data.sessionId}")
        else:
            response = {
                "status": "success",
                "reply": get_safe_response(data.message.text),
                "internal_metrics": {"stage": "detection", "confidence": 0.0}
            }
        
        if session["message_count"] % 10 == 0:
            background_tasks.add_task(session_manager.cleanup_expired_sessions)
        
        return AgentOutput(**response)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(session_manager.sessions)
    }

@app.get("/stats")
async def get_stats(x_api_key: str = Header(None)):
    """Get system statistics"""
    if not validate_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    total_intelligence = {
        "bankAccounts": 0,
        "upiIds": 0,
        "phishingLinks": 0,
        "phoneNumbers": 0,
        "emails": 0
    }
    
    scam_types = defaultdict(int)
    
    for session in session_manager.sessions.values():
        if session["scam_detected"]:
            scam_types[session["scam_type"]] += 1
            for key in total_intelligence:
                total_intelligence[key] += len(session["intelligence"].get(key, []))
    
    return {
        "active_sessions": len(session_manager.sessions),
        "total_intelligence_extracted": total_intelligence,
        "scam_types_detected": dict(scam_types),
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_api_key(api_key: str) -> bool:
    """Validate API key"""
    if not api_key:
        return False
    expected_hash = hashlib.sha256(b"CHAMELEON_HONEYPOT_SECRET_2024").hexdigest()
    return api_key == expected_hash

def get_safe_response(message: str) -> str:
    """Generate safe response during detection phase"""
    responses = [
        "I'm sorry, could you clarify what this is about?",
        "I don't quite understand. Can you explain more?",
        "Is this an official communication?",
        "Could you provide more details?",
        "What exactly do you need from me?"
    ]
    return responses[len(message) % len(responses)]

def should_end_engagement(session: Dict) -> bool:
    """Determine if engagement should be terminated"""
    if session["message_count"] >= 25:
        return True
    
    intel_count = sum(len(values) for values in session["intelligence"].values())
    if intel_count >= 3 and session["message_count"] >= 8:
        return True
    
    session_duration = time.time() - session["created_at"]
    if session_duration > 300:
        return True
    
    return False

async def send_final_report(session_id: str, session_data: Dict):
    """Send final intelligence report to GUVI endpoint"""
    payload = {
        "sessionId": session_id,
        "scamDetected": session_data["scam_detected"],
        "totalMessagesExchanged": session_data["message_count"],
        "extractedIntelligence": session_data["intelligence"],
        "agentNotes": session_data["agent"].generate_summary()
    }
    
    try:
        response = requests.post(
            "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Successfully submitted final report for session {session_id}")
            session_manager.remove_session(session_id)
        else:
            logger.error(f"❌ Failed to submit report: {response.status_code}")
    
    except Exception as e:
        logger.error(f"❌ Error sending final report: {str(e)}", exc_info=True)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Chameleon-Honeypot API starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Chameleon-Honeypot API shutting down...")
    for session_id, session in list(session_manager.sessions.items()):
        if session["scam_detected"]:
            await send_final_report(session_id, session)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
