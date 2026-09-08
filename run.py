#!/usr/bin/env python
"""
Application Launcher
Starts the Timor-Leste Tourism Intelligence Platform
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import pandas
        import sklearn
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("\nPlease install required packages:")
        print("pip install -r requirements.txt")
        return False

def setup_database():
    """Initialize and seed the database"""
    try:
        from backend.seed import seed_database
        print("Seeding database with sample data...")
        seed_database()
        print("Database seeded successfully!")
        return True
    except Exception as e:
        print(f"Error seeding database: {e}")
        return False

def main():
    """Main entry point"""
    print("=" * 60)
    print("🌴 Timor-Leste Tourism Intelligence Platform")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Setup database
    db_path = Path("database/tourism.db")
    if not db_path.exists() or db_path.stat().st_size == 0:
        setup_database()
    
    # Start the server
    print("\n🚀 Starting server...")
    print(f"📍 Backend: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"🌐 Frontend: http://localhost:8000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:8000")
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run uvicorn
    try:
        import uvicorn
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped.")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()