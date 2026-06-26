#!/usr/bin/env python3
"""
Research Tracker Launcher
Run this script to start the application
"""

import os
import sys
import subprocess
import webbrowser
from time import sleep

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import streamlit
        import plotly
        import pandas
        import bcrypt
        return True
    except ImportError as e:
        print(f"❌ Missing requirement: {e}")
        print("\nInstalling requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def create_data_directory():
    """Create data directory if it doesn't exist"""
    if not os.path.exists("data"):
        os.makedirs("data")
        print("✅ Created data directory")

def main():
    """Main function"""
    print("=" * 50)
    print("🔬 Lahore Science Foundry Research Tracker")
    print("=" * 50)
    
    # Check requirements
    print("\n📦 Checking requirements...")
    check_requirements()
    
    # Create data directory
    create_data_directory()
    
    # Initialize database
    print("\n🗄️ Initializing database...")
    from database import Database
    db = Database()
    print("✅ Database ready")
    
    # Start Streamlit
    print("\n🚀 Starting application...")
    print("The application will open in your browser shortly.")
    print("Press Ctrl+C to stop the server.")
    
    # Open browser after a delay
    def open_browser():
        sleep(2)
        webbrowser.open("http://localhost:8501")
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run streamlit
    os.system(f"{sys.executable} -m streamlit run app.py --server.port 8501")

if __name__ == "__main__":
    main()