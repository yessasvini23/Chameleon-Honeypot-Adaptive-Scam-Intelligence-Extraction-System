#!/usr/bin/env python3
"""
Quick test script for Streamlit setup
Verifies all dependencies are installed
"""

import sys

def test_imports():
    """Test if all required packages are installed"""
    
    print("=" * 60)
    print("🧪 STREAMLIT SETUP TEST")
    print("=" * 60)
    
    packages = [
        ("streamlit", "Streamlit"),
        ("plotly", "Plotly"),
        ("pandas", "Pandas"),
        ("requests", "Requests"),
    ]
    
    all_good = True
    
    for package, name in packages:
        try:
            __import__(package)
            print(f"✅ {name:20} - Installed")
        except ImportError:
            print(f"❌ {name:20} - NOT INSTALLED")
            all_good = False
    
    print("=" * 60)
    
    if all_good:
        print("✅ All dependencies installed!")
        print("\nYou can now run:")
        print("  streamlit run streamlit_app.py")
        return True
    else:
        print("❌ Some dependencies missing!")
        print("\nInstall with:")
        print("  pip install streamlit plotly pandas")
        return False

def test_server():
    """Test if API server is accessible"""
    import requests
    
    print("\n" + "=" * 60)
    print("🌐 API SERVER TEST")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running and healthy")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Active sessions: {data.get('active_sessions')}")
            return True
        else:
            print(f"⚠️  Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("\nStart the server with:")
        print("  python production_honeypot_api.py")
        print("  OR")
        print("  docker-compose up -d")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n")
    deps_ok = test_imports()
    server_ok = test_server()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if deps_ok and server_ok:
        print("✅ Everything is ready!")
        print("\nRun the Streamlit demo:")
        print("  streamlit run streamlit_app.py")
        print("\nOr use the quick start script:")
        print("  ./start_streamlit.sh")
        sys.exit(0)
    else:
        print("⚠️  Setup incomplete")
        if not deps_ok:
            print("   → Install missing dependencies")
        if not server_ok:
            print("   → Start the API server")
        sys.exit(1)
