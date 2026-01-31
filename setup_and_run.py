"""
Complete Setup and Run Script for Fingerprint Attendance System
This script will:
1. Check and install dependencies
2. Initialize the database
3. Start both backend and frontend
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def check_python_version():
    """Check if Python version is adequate"""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required!")
        sys.exit(1)
    
    print("✅ Python version is compatible")

def check_dependencies():
    """Check if required packages are installed"""
    print_header("Checking Dependencies")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'streamlit',
        'pillow',
        'reportlab',
        'bcrypt',
        'requests',
        'pandas',
        'pydantic',
        'pyjwt'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("\nInstalling missing packages...")
        
        # Install missing packages
        subprocess.check_call([
            sys.executable, "-m", "pip", "install"
        ] + missing_packages)
        
        print("✅ All packages installed!")
    else:
        print("\n✅ All dependencies are installed")

def initialize_database():
    """Initialize the database"""
    print_header("Initializing Database")
    
    db_path = Path(__file__).parent / 'attendance.db'
    
    if db_path.exists():
        response = input(f"⚠️  Database already exists at {db_path}\nDo you want to recreate it? (y/N): ")
        if response.lower() != 'y':
            print("ℹ️  Using existing database")
            return
        else:
            os.remove(db_path)
            print("🗑️  Removed old database")
    
    # Run database setup
    print("Creating database...")
    try:
        import database_setup
        database_setup.create_database()
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        sys.exit(1)

def check_port(port):
    """Check if a port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0  # True if port is available

def start_backend():
    """Start the FastAPI backend"""
    print_header("Starting Backend Server")
    
    if not check_port(8000):
        print("⚠️  Port 8000 is already in use!")
        print("Backend might already be running or another service is using the port.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return None
    
    backend_dir = Path(__file__).parent / 'backend'
    
    if not backend_dir.exists():
        print(f"❌ Backend directory not found at {backend_dir}")
        print("Please ensure the backend folder exists with main.py")
        return None
    
    print(f"Starting backend from: {backend_dir}")
    print("Backend will run at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    
    # Start backend process
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(backend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for backend to start
    print("Waiting for backend to start...")
    time.sleep(3)
    
    # Check if backend started successfully
    if backend_process.poll() is None:
        print("✅ Backend started successfully!")
        return backend_process
    else:
        print("❌ Backend failed to start!")
        stderr = backend_process.stderr.read().decode()
        print(f"Error: {stderr}")
        return None

def start_frontend():
    """Start the Streamlit frontend"""
    print_header("Starting Frontend Application")
    
    if not check_port(8501):
        print("⚠️  Port 8501 is already in use!")
        print("Frontend might already be running or another service is using the port.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return None
    
    frontend_dir = Path(__file__).parent / 'frontend'
    
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found at {frontend_dir}")
        print("Please ensure the frontend folder exists with app.py")
        return None
    
    print(f"Starting frontend from: {frontend_dir}")
    print("Frontend will run at: http://localhost:8501")
    
    # Start frontend process
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py"],
        cwd=str(frontend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for frontend to start
    print("Waiting for frontend to start...")
    time.sleep(5)
    
    # Check if frontend started successfully
    if frontend_process.poll() is None:
        print("✅ Frontend started successfully!")
        return frontend_process
    else:
        print("❌ Frontend failed to start!")
        stderr = frontend_process.stderr.read().decode()
        print(f"Error: {stderr}")
        return None

def main():
    """Main setup and run function"""
    print("\n" + "="*70)
    print("  🔐 FINGERPRINT ATTENDANCE SYSTEM - SETUP & RUN")
    print("="*70)
    
    try:
        # Step 1: Check Python version
        check_python_version()
        
        # Step 2: Check and install dependencies
        check_dependencies()
        
        # Step 3: Initialize database
        initialize_database()
        
        # Step 4: Start backend
        backend_process = start_backend()
        if backend_process is None:
            print("\n❌ Failed to start backend. Exiting...")
            sys.exit(1)
        
        # Step 5: Start frontend
        frontend_process = start_frontend()
        if frontend_process is None:
            print("\n❌ Failed to start frontend. Stopping backend...")
            backend_process.terminate()
            sys.exit(1)
        
        # Success message
        print_header("🎉 SYSTEM STARTED SUCCESSFULLY!")
        print("Backend API:  http://localhost:8000")
        print("API Docs:     http://localhost:8000/docs")
        print("Frontend UI:  http://localhost:8501")
        print("\n🔐 Default Login Credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n⚠️  Press Ctrl+C to stop both services")
        print("="*70)
        
        # Keep script running
        try:
            while True:
                time.sleep(1)
                # Check if processes are still running
                if backend_process.poll() is not None:
                    print("\n❌ Backend stopped unexpectedly!")
                    break
                if frontend_process.poll() is not None:
                    print("\n❌ Frontend stopped unexpectedly!")
                    break
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down services...")
            backend_process.terminate()
            frontend_process.terminate()
            print("✅ Services stopped successfully")
            
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()