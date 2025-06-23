#!/usr/bin/env python3
"""
Production start script for Render deployment
Serves both backend API and frontend from a single port
"""

import os
import sys
import subprocess
import uvicorn
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from npc_engine.api.npc_api import api

def build_frontend():
    """Build the frontend for production"""
    print("🏗️  Building frontend for production...")
    
    web_gui_dir = Path(__file__).parent / "web-gui"
    
    if not web_gui_dir.exists():
        print(f"❌ Frontend directory not found: {web_gui_dir}")
        return False
    
    try:
        # Change to web-gui directory
        original_dir = os.getcwd()
        os.chdir(web_gui_dir)
        
        # Install dependencies
        print("📦 Installing frontend dependencies...")
        subprocess.run(["npm", "ci"], check=True)
        
        # Build for production
        print("🔨 Building frontend...")
        subprocess.run(["npm", "run", "build"], check=True)
        
        # Return to original directory
        os.chdir(original_dir)
        
        print("✅ Frontend built successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend build failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error building frontend: {e}")
        return False

def main():
    """Main production server startup"""
    
    # Get port from environment (Render sets this to 10000 by default)
    port = int(os.getenv("PORT", 10000))
    host = "0.0.0.0"
    
    print(f"🚀 Starting NPC Engine Production Server on {host}:{port}")
    print(f"📍 PORT environment variable: {os.getenv('PORT', 'not set')}")
    print(f"📍 Binding to host: {host}, port: {port}")
    
    # Check for required environment variables
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not set!")
        print("   Please set it in your Render environment variables.")
        sys.exit(1)
    
    # Build frontend
    if not build_frontend():
        print("❌ Frontend build failed, but continuing with backend only...")
    
    # Configure the API to serve static files
    web_gui_dist = Path(__file__).parent / "web-gui" / "dist"
    if web_gui_dist.exists():
        print(f"📁 Serving frontend from: {web_gui_dist}")
        # The static files will be served by the FastAPI app
    else:
        print("⚠️  Frontend dist directory not found, serving API only")
    
    print(f"📖 API Documentation: http://localhost:{port}/docs")
    print(f"🔍 Health check: http://localhost:{port}/health")
    print(f"🎨 Frontend: http://localhost:{port}/")
    
    # Start the server
    print(f"🌐 Starting uvicorn server...")
    print(f"🔗 Will be accessible at: http://{host}:{port}")
    
    try:
        uvicorn.run(
            "npc_engine.api.npc_api:api.app",
            host=host,
            port=port,
            reload=False,  # Disable reload in production
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 