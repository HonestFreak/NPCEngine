#!/usr/bin/env python3
"""
NPC Engine Server - Main entry point for the API server
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
    """Main server startup function"""
    
    # Check for required environment variables
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Warning: GOOGLE_API_KEY not set. Some features may not work.")
        print("   Set it with: export GOOGLE_API_KEY='your_api_key'")
    
    print("🎮 Starting NPC Engine API Server...")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🔍 Health check available at: http://localhost:8000/health")
    print("🎯 NPC Engine API available at: http://localhost:8000/api/v1/")
    
    # Start the server
    uvicorn.run(
        "npc_engine.api.npc_api:api.app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 