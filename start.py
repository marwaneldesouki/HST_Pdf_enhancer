import subprocess
import sys
import time
import os
from pathlib import Path

def check_mongodb():
    """Check if MongoDB is running."""
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()  # Will raise an exception if MongoDB is not running
        print("✅ MongoDB is running")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection error: {e}")
        print("Please make sure MongoDB is installed and running on port 27017")
        return False

def create_directories():
    """Create necessary directories if they don't exist."""
    Path("documents").mkdir(exist_ok=True)
    Path("templates").mkdir(exist_ok=True)
    Path("static").mkdir(exist_ok=True)
    print("✅ Required directories created")

def start_services():
    """Start the document watcher and web application."""
    if not check_mongodb():
        return
    
    create_directories()
    
    print("\n📝 Starting document watcher...")
    watcher_process = subprocess.Popen([sys.executable, "document_watcher.py"], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE,
                                      text=True)
    
    print("🌐 Starting web application...")
    web_process = subprocess.Popen([sys.executable, "app.py"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  text=True)
    
    print("\n✅ System started successfully!")
    print("📂 Place documents in the 'documents' folder for processing")
    print("🔍 Access the web interface at: http://localhost:8000")
    print("\nPress Ctrl+C to stop all services\n")
    
    try:
        while True:
            # Print output from processes
            watcher_out = watcher_process.stdout.readline().strip()
            if watcher_out:
                print(f"[Watcher] {watcher_out}")
                
            web_out = web_process.stdout.readline().strip()
            if web_out:
                print(f"[Web App] {web_out}")
            
            # Check if processes are still running
            if watcher_process.poll() is not None:
                print("❌ Document watcher stopped unexpectedly")
                break
                
            if web_process.poll() is not None:
                print("❌ Web application stopped unexpectedly")
                break
                
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n⏹️ Stopping services...")
    finally:
        # Terminate processes
        if watcher_process.poll() is None:
            watcher_process.terminate()
        if web_process.poll() is None:
            web_process.terminate()
        print("✅ All services stopped")

if __name__ == "__main__":
    start_services() 