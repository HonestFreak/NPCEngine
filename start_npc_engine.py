#!/usr/bin/env python3
"""
Start script for NPC Engine with both backend API and frontend GUI
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def start_backend():
    """Start the NPC Engine backend API server"""
    print("🚀 Starting NPC Engine Backend API...")
    
    # Change to the project root directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    try:
        backend_process = subprocess.Popen([
            sys.executable, "run_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return backend_process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the React frontend GUI"""
    print("🎨 Starting NPC Engine Frontend GUI...")
    
    web_gui_dir = Path(__file__).parent / "web-gui"
    
    if not web_gui_dir.exists():
        print(f"❌ Frontend directory not found: {web_gui_dir}")
        return None
    
    os.chdir(web_gui_dir)
    
    try:
        # Install dependencies if node_modules doesn't exist
        if not (web_gui_dir / "node_modules").exists():
            print("📦 Installing frontend dependencies...")
            subprocess.run(["npm", "install"], check=True)
        
        frontend_process = subprocess.Popen([
            "npm", "run", "dev"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return frontend_process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    """Main function to orchestrate both servers"""
    print("🎮 Starting NPC Engine Development Environment")
    print("=" * 50)
    
    processes = []
    
    try:
        # Start backend
        backend_process = start_backend()
        if backend_process:
            processes.append(("Backend API", backend_process))
            print("✅ Backend API started")
            time.sleep(2)  # Give backend time to start
        else:
            print("❌ Failed to start backend, exiting")
            return 1
        
        # Start frontend
        frontend_process = start_frontend()
        if frontend_process:
            processes.append(("Frontend GUI", frontend_process))
            print("✅ Frontend GUI started")
        else:
            print("⚠️  Frontend failed to start, but backend is running")
        
        print("\n" + "=" * 50)
        print("🎯 NPC Engine is ready!")
        print("📡 Backend API: http://localhost:8000")
        print("📖 API Documentation: http://localhost:8000/docs")
        if frontend_process:
            print("🎨 Frontend GUI: http://localhost:5173")
        print("=" * 50)
        print("Press Ctrl+C to stop all services")
        
        # Wait for processes
        while True:
            time.sleep(1)
            
            # Check if any process has died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️  {name} has stopped unexpectedly")
                    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down NPC Engine...")
        
        # Terminate all processes
        for name, process in processes:
            try:
                print(f"   Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
                print(f"   ✅ {name} stopped")
            except subprocess.TimeoutExpired:
                print(f"   🔨 Force killing {name}...")
                process.kill()
            except Exception as e:
                print(f"   ⚠️  Error stopping {name}: {e}")
        
        print("👋 NPC Engine stopped successfully")
        return 0
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 