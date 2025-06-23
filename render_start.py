#!/usr/bin/env python3
"""
Render deployment startup script for NPC Engine
"""

import os
import sys
import uvicorn

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from npc_engine.api.npc_api import api

def main():
    """Main server startup function for Render deployment"""
    
    # Get port from environment (Render sets this)
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    # Check for required environment variables
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Warning: GOOGLE_API_KEY not set. Some features may not work.")
        print("   Set it in Render environment variables")
    
    print(f"🎮 Starting NPC Engine API Server on {host}:{port}...")
    print(f"📖 API Documentation will be available at: http://localhost:{port}/docs")
    print(f"🔍 Health check available at: http://localhost:{port}/health")
    
    # Start the server with production settings
    uvicorn.run(
        "npc_engine.api.npc_api:api.app",
        host=host,
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )

if __name__ == "__main__":
    main() 