"""
Streamlit Web Interface for Chameleon-Honeypot
Interactive testing and demonstration dashboard
"""

import streamlit as st
import requests
import hashlib
import json
import time
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Chameleon-Honeypot Demo",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_URL = "http://localhost:8000"
SECRET = b"CHAMELEON_HONEYPOT_SECRET_2024"
API_KEY = hashlib.sha256(SECRET).hexdigest()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .scammer-message {
        background-color: #FFE5E5;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        margin: 1rem 0;
    }
    .agent-message {
        background-color: #E5F5FF;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4B8BFF;
        margin: 1rem 0;
    }
    .intelligence-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #F5F5F5;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"streamlit-{int(time.time())}"
if 'intelligence' not in st.session_state:
    st.session_state.intelligence = {
        "bankAccounts": [],
        "upiIds": [],
        "phishingLinks": [],
        "phoneNumbers": [],
        "emails": []
    }
if 'scam_detected' not in st.session_state:
    st.session_state.scam_detected = False
if 'persona' not in st.session_state:
    st.session_state.persona = None
if 'turn_count' not in st.session_state:
    st.session_state.turn_count = 0

# Helper Functions
def check_server_health():
    """Check if API server is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_message(message_text):
    """Send message to honeypot API"""
    payload = {
        "sessionId": st.session_state.session_id,
        "message": {
            "sender": "scammer",
            "text": message_text,
            "timestamp": datetime.now().isoformat()
        },
        "conversationHistory": st.session_state.conversation_history,
        "metadata": {"source": "streamlit"}
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/honeypot",
            json=payload,
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server. Make sure it's running on http://localhost:8000")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def get_statistics():
    """Get system statistics"""
    try:
        response = requests.get(
            f"{API_URL}/stats",
            headers={"X-API-Key": API_KEY},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def extract_intelligence_from_text(text):
    """Extract intelligence from text using regex"""
    import re
    intel = {
        "upiIds": re.findall(r'([a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64})', text),
        "phoneNumbers": re.findall(r'\b([789]\d{9})\b', text),
        "phishingLinks": re.findall(r'(https?://[^\s]+)', text),
        "bankAccounts": re.findall(r'\b(\d{12,18})\b', text)
    }
    return {k: list(set(v)) for k, v in intel.items() if v}

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x100/FF4B4B/FFFFFF?text=Chameleon+Honeypot", use_column_width=True)
    st.markdown("## 🎭 Control Panel")
    
    # Server status
    server_online = check_server_health()
    if server_online:
        st.success("✅ Server Online")
    else:
        st.error("❌ Server Offline")
        st.info("Start server with:\n```bash\ndocker-compose up -d\n```\nor\n```bash\npython production_honeypot_api.py\n```")
    
    st.markdown("---")
    
    # Session info
    st.markdown("### 📊 Session Info")
    st.info(f"**Session ID:**\n`{st.session_state.session_id[:20]}...`")
    st.metric("Turn Count", st.session_state.turn_count)
    
    if st.session_state.scam_detected:
        st.success("🚨 Scam Detected!")
        if st.session_state.persona:
            st.info(f"**Active Persona:**\n{st.session_state.persona}")
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("🔄 Reset Session"):
        st.session_state.conversation_history = []
        st.session_state.session_id = f"streamlit-{int(time.time())}"
        st.session_state.intelligence = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "emails": []
        }
        st.session_state.scam_detected = False
        st.session_state.persona = None
        st.session_state.turn_count = 0
        st.rerun()
    
    if st.button("📊 View Statistics"):
        st.session_state.show_stats = True
    
    if st.button("📥 Export Conversation"):
        conversation_json = json.dumps(st.session_state.conversation_history, indent=2)
        st.download_button(
            label="Download JSON",
            data=conversation_json,
            file_name=f"conversation_{st.session_state.session_id}.json",
            mime="application/json"
        )

# Main Content
st.markdown('<h1 class="main-header">🎭 Chameleon-Honeypot Interactive Demo</h1>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Live Chat", 
    "🎯 Intelligence", 
    "📊 Statistics", 
    "🧪 Pre-built Scenarios",
    "📖 Documentation"
])

# Tab 1: Live Chat
with tab1:
    st.markdown("## 💬 Interactive Scam Simulation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Conversation")
        
        # Display conversation history
        if st.session_state.conversation_history:
            for i, msg in enumerate(st.session_state.conversation_history):
                if msg['sender'] == 'scammer':
                    st.markdown(f"""
                    <div class="scammer-message">
                        <strong>🔴 Scammer:</strong><br>
                        {msg['text']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="agent-message">
                        <strong>🤖 Agent ({st.session_state.persona or 'System'}):</strong><br>
                        {msg['text']}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("👋 Start a conversation by typing a scam message below!")
        
        # Message input
        st.markdown("### Send Scam Message")
        message_text = st.text_area(
            "Type your scam message:",
            placeholder="Example: Your bank account will be blocked! Update KYC immediately!",
            height=100,
            key="message_input"
        )
        
        col_send, col_clear = st.columns([3, 1])
        
        with col_send:
            if st.button("📤 Send Message", disabled=not server_online):
                if message_text.strip():
                    with st.spinner("Processing..."):
                        # Send message
                        result = send_message(message_text)
                        
                        if result:
                            st.session_state.turn_count += 1
                            
                            # Add to conversation history
                            st.session_state.conversation_history.append({
                                "sender": "scammer",
                                "text": message_text,
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            st.session_state.conversation_history.append({
                                "sender": "agent",
                                "text": result['reply'],
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            # Update state
                            if 'internal_metrics' in result:
                                metrics = result['internal_metrics']
                                if 'persona' in metrics:
                                    st.session_state.persona = metrics['persona']
                                    st.session_state.scam_detected = True
                            
                            # Extract intelligence
                            extracted = extract_intelligence_from_text(message_text)
                            for key, values in extracted.items():
                                st.session_state.intelligence[key].extend(values)
                                st.session_state.intelligence[key] = list(set(st.session_state.intelligence[key]))
                            
                            st.rerun()
                else:
                    st.warning("Please enter a message")
        
        with col_clear:
            if st.button("🗑️ Clear"):
                st.session_state.message_input = ""
    
    with col2:
        st.markdown("### 💡 Tips")
        st.info("""
        **Try these scam patterns:**
        
        🏦 **Banking Scam:**
        - "Account will be blocked"
        - "Update KYC immediately"
        - "Verify your details"
        
        💰 **UPI Fraud:**
        - "Payment failed"
        - "Refund pending"
        - "Send Rs 1 to verify"
        
        🔗 **Phishing:**
        - "Click this link"
        - "Verify account here"
        - "Suspicious activity detected"
        """)
        
        st.markdown("### 🎯 What to Expect")
        st.success("""
        1. System detects scam type
        2. Selects appropriate persona
        3. Engages naturally
        4. Extracts intelligence
        5. Shows real-time results
        """)

# Tab 2: Intelligence
with tab2:
    st.markdown("## 🎯 Extracted Intelligence")
    
    # Summary metrics
    total_intel = sum(len(v) for v in st.session_state.intelligence.values())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏦 Bank Accounts", len(st.session_state.intelligence['bankAccounts']))
    with col2:
        st.metric("💳 UPI IDs", len(st.session_state.intelligence['upiIds']))
    with col3:
        st.metric("📞 Phone Numbers", len(st.session_state.intelligence['phoneNumbers']))
    with col4:
        st.metric("🔗 Phishing URLs", len(st.session_state.intelligence['phishingLinks']))
    
    st.markdown("---")
    
    # Detailed intelligence display
    if total_intel > 0:
        col_left, col_right = st.columns(2)
        
        with col_left:
            if st.session_state.intelligence['bankAccounts']:
                st.markdown("### 🏦 Bank Accounts")
                for acc in st.session_state.intelligence['bankAccounts']:
                    st.code(acc)
            
            if st.session_state.intelligence['upiIds']:
                st.markdown("### 💳 UPI IDs")
                for upi in st.session_state.intelligence['upiIds']:
                    st.code(upi)
        
        with col_right:
            if st.session_state.intelligence['phoneNumbers']:
                st.markdown("### 📞 Phone Numbers")
                for phone in st.session_state.intelligence['phoneNumbers']:
                    st.code(phone)
            
            if st.session_state.intelligence['phishingLinks']:
                st.markdown("### 🔗 Phishing URLs")
                for url in st.session_state.intelligence['phishingLinks']:
                    st.code(url)
        
        # Intelligence timeline
        st.markdown("### 📈 Extraction Timeline")
        
        # Create visualization
        intel_data = []
        for category, items in st.session_state.intelligence.items():
            for item in items:
                intel_data.append({
                    "Type": category,
                    "Value": item[:30] + "..." if len(item) > 30 else item,
                    "Count": 1
                })
        
        if intel_data:
            df = pd.DataFrame(intel_data)
            fig = px.bar(
                df.groupby('Type').size().reset_index(name='Count'),
                x='Type',
                y='Count',
                color='Type',
                title="Intelligence by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📭 No intelligence extracted yet. Send scam messages with UPIs, phone numbers, or URLs!")

# Tab 3: Statistics
with tab3:
    st.markdown("## 📊 System Statistics")
    
    if st.button("🔄 Refresh Statistics"):
        st.rerun()
    
    stats = get_statistics()
    
    if stats:
        # Overview metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🔴 Active Sessions", stats['active_sessions'])
        with col2:
            total_scams = sum(stats['scam_types_detected'].values()) if stats['scam_types_detected'] else 0
            st.metric("🚨 Scams Detected", total_scams)
        with col3:
            total_intel = sum(stats['total_intelligence_extracted'].values())
            st.metric("🎯 Total Intelligence", total_intel)
        
        st.markdown("---")
        
        # Intelligence breakdown
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("### 🎯 Intelligence Breakdown")
            intel_df = pd.DataFrame([
                {"Type": "Bank Accounts", "Count": stats['total_intelligence_extracted']['bankAccounts']},
                {"Type": "UPI IDs", "Count": stats['total_intelligence_extracted']['upiIds']},
                {"Type": "Phone Numbers", "Count": stats['total_intelligence_extracted']['phoneNumbers']},
                {"Type": "Phishing Links", "Count": stats['total_intelligence_extracted']['phishingLinks']},
                {"Type": "Emails", "Count": stats['total_intelligence_extracted']['emails']}
            ])
            
            fig1 = px.pie(
                intel_df,
                values='Count',
                names='Type',
                title='Intelligence Distribution'
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col_right:
            st.markdown("### 🚨 Scam Types Detected")
            if stats['scam_types_detected']:
                scam_df = pd.DataFrame([
                    {"Scam Type": k.replace('_', ' ').title(), "Count": v}
                    for k, v in stats['scam_types_detected'].items()
                ])
                
                fig2 = px.bar(
                    scam_df,
                    x='Scam Type',
                    y='Count',
                    title='Scam Types Distribution'
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No scams detected yet")
        
        # Raw data
        with st.expander("📄 View Raw Statistics"):
            st.json(stats)
    else:
        st.error("Unable to fetch statistics. Make sure the server is running.")

# Tab 4: Pre-built Scenarios
with tab4:
    st.markdown("## 🧪 Pre-built Scam Scenarios")
    st.info("Click any scenario to automatically run a complete scam conversation")
    
    scenarios = {
        "🏦 Banking KYC Scam": [
            "Hello, this is from State Bank of India customer care",
            "Your account has been flagged for KYC verification",
            "Account will be blocked within 2 hours if not verified",
            "Please provide your account number for urgent verification",
            "Send Rs 1 to sbicare@paytm to complete verification",
            "Our helpline number is 9876543210 for assistance"
        ],
        "💰 UPI Refund Scam": [
            "Your UPI payment of Rs 5000 has failed",
            "To get refund, you need to verify your account",
            "Send Rs 1 to refund.verify@paytm",
            "Contact our support at 8765432109",
            "Click here to verify: https://upi-refund-verify.xyz"
        ],
        "🎁 Prize/Lottery Scam": [
            "Congratulations! You have won Rs 50,000 in lucky draw",
            "To claim your prize, visit: https://claim-prize-now.tk",
            "Send processing fee Rs 500 to winner@phonepe",
            "Call 7654321098 to confirm your prize",
            "Transfer to account 987654321012 IFSC: HDFC0001234"
        ],
        "💼 Job Offer Scam": [
            "Congratulations! Selected for Work From Home position",
            "Salary: Rs 40,000/month for data entry work",
            "Registration fee: Rs 2,500 (refundable)",
            "Send to hr.recruitment@paytm",
            "Contact HR: 9988776655",
            "More details: https://jobs-wfh-guaranteed.xyz"
        ],
        "🔐 Account Security Alert": [
            "Security Alert: Suspicious login detected on your account",
            "Click here immediately: https://secure-verify-account.ml",
            "Your account will be locked in 1 hour",
            "Call security team: 8877665544",
            "Verify via UPI: security@googlepay"
        ]
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        for scenario_name, messages in scenarios.items():
            with st.expander(scenario_name):
                st.markdown("**Messages:**")
                for i, msg in enumerate(messages, 1):
                    st.markdown(f"{i}. {msg}")
                
                if st.button(f"▶️ Run {scenario_name}", key=f"run_{scenario_name}"):
                    if server_online:
                        with st.spinner(f"Running {scenario_name}..."):
                            # Reset session
                            st.session_state.conversation_history = []
                            st.session_state.session_id = f"scenario-{int(time.time())}"
                            st.session_state.intelligence = {
                                "bankAccounts": [],
                                "upiIds": [],
                                "phishingLinks": [],
                                "phoneNumbers": [],
                                "emails": []
                            }
                            st.session_state.turn_count = 0
                            
                            # Run scenario
                            for msg in messages:
                                result = send_message(msg)
                                if result:
                                    st.session_state.turn_count += 1
                                    
                                    st.session_state.conversation_history.append({
                                        "sender": "scammer",
                                        "text": msg,
                                        "timestamp": datetime.now().isoformat()
                                    })
                                    
                                    st.session_state.conversation_history.append({
                                        "sender": "agent",
                                        "text": result['reply'],
                                        "timestamp": datetime.now().isoformat()
                                    })
                                    
                                    if 'internal_metrics' in result:
                                        metrics = result['internal_metrics']
                                        if 'persona' in metrics:
                                            st.session_state.persona = metrics['persona']
                                            st.session_state.scam_detected = True
                                    
                                    extracted = extract_intelligence_from_text(msg)
                                    for key, values in extracted.items():
                                        st.session_state.intelligence[key].extend(values)
                                        st.session_state.intelligence[key] = list(set(st.session_state.intelligence[key]))
                                    
                                    time.sleep(0.5)
                            
                            st.success(f"✅ {scenario_name} completed!")
                            st.rerun()
                    else:
                        st.error("Server is offline. Please start it first.")
    
    with col2:
        st.markdown("### 📊 Scenario Stats")
        st.info(f"""
        **Available Scenarios:** {len(scenarios)}
        
        **Coverage:**
        - Banking Scams
        - UPI Fraud
        - Prize/Lottery
        - Job Offers
        - Security Alerts
        """)

# Tab 5: Documentation
with tab5:
    st.markdown("## 📖 Documentation")
    
    with st.expander("🎯 How It Works"):
        st.markdown("""
        ### Chameleon-Honeypot Detection System
        
        **1. Scam Detection (Multi-Layer)**
        - Pattern matching for urgency, threats, rewards
        - Authority claim detection (bank, government, etc.)
        - Personal information request identification
        - Confidence scoring (threshold: 60%)
        
        **2. Persona Selection**
        - **Elderly (Ramesh Kumar)**: Banking scams, tech support
        - **Student (Priya Sharma)**: Job offers, phishing
        - **Professional (Arun Mehra)**: Investment, UPI fraud
        
        **3. Intelligence Extraction**
        - UPI IDs: `username@provider`
        - Bank Accounts: 9-18 digit numbers
        - Phone Numbers: Indian mobile (789XXXXXXX)
        - URLs: Phishing links
        - IFSC Codes: Bank identifiers
        
        **4. Engagement Strategy**
        - Turns 1-2: Initial contact
        - Turns 3-5: Build trust
        - Turns 6-15: Extract information
        - Turns 16-20: Add verification questions
        - Turns 21-25: Delay tactics
        - Turn 25+: End and report
        """)
    
    with st.expander("🚀 Quick Start Guide"):
        st.markdown("""
        ### Running the Demo
        
        **Step 1: Start the Server**
        ```bash
        # Option A: Docker
        docker-compose up -d
        
        # Option B: Python
        python production_honeypot_api.py
        ```
        
        **Step 2: Start Streamlit**
        ```bash
        streamlit run streamlit_app.py
        ```
        
        **Step 3: Test**
        1. Check server status in sidebar (should be green)
        2. Go to "Pre-built Scenarios" tab
        3. Click any scenario to run
        4. Watch the results in real-time!
        """)
    
    with st.expander("📊 API Endpoints"):
        st.markdown("""
        ### Available Endpoints
        
        **1. Health Check**
        ```
        GET /health
        ```
        
        **2. Honeypot (Main)**
        ```
        POST /api/honeypot
        Headers: X-API-Key: <your-key>
        Body: {sessionId, message, conversationHistory}
        ```
        
        **3. Statistics**
        ```
        GET /stats
        Headers: X-API-Key: <your-key>
        ```
        """)
    
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        ### Common Issues
        
        **Server Offline**
        - Check if server is running: `curl http://localhost:8000/health`
        - Start server: `python production_honeypot_api.py`
        - Check port 8000 is not in use: `lsof -i :8000`
        
        **No Intelligence Extracted**
        - Make sure messages contain UPIs, phone numbers, or URLs
        - Check scam message patterns
        - Review extraction logs
        
        **API Key Issues**
        - Regenerate key: `python3 -c "import hashlib; print(hashlib.sha256(b'CHAMELEON_HONEYPOT_SECRET_2024').hexdigest())"`
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🎭 Chameleon-Honeypot v1.0 | Built for GUVI Hackathon | 
    <a href="https://github.com" target="_blank">GitHub</a> | 
    Made with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
