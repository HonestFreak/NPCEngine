#!/bin/bash

echo "🚀 Building NPC Engine for Render deployment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if Node.js is available
if command -v node &> /dev/null; then
    echo "✅ Node.js found: $(node --version)"
    
    # Install frontend dependencies and build
    echo "📦 Installing frontend dependencies..."
    cd web-gui
    npm ci
    
    echo "🔨 Building frontend..."
    npm run build
    
    cd ..
    echo "✅ Frontend built successfully"
else
    echo "⚠️  Node.js not found, frontend will not be built"
    echo "   The application will run in API-only mode"
fi

echo "🎉 Build completed!" 