# 🚀 Deploying NPC Engine to Render

This guide will help you deploy your NPC Engine to [Render](https://render.com/) with both backend API and frontend dashboard.

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **Google API Key**: Get one from [Google AI Studio](https://aistudio.google.com/app/apikey)

## 🔧 Quick Deploy

### Option 1: Using render.yaml (Recommended)

1. **Push your code** to GitHub with the provided `render.yaml` file
2. **Connect to Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Select the repository with your NPC Engine code

3. **Configure Environment Variables**:
   - Render will detect the `render.yaml` file
   - Set your `GOOGLE_API_KEY` in the environment variables section
   - Click "Create"

### Option 2: Manual Setup

1. **Create Web Service**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**:
   ```
   Name: npc-engine
   Environment: Python
   Region: Oregon (or your preferred region)
   Branch: main
   Root Directory: (leave blank)
   Build Command: ./build.sh
   Start Command: python3 render_start.py
   ```

3. **Set Environment Variables**:
   ```
   GOOGLE_API_KEY = your_actual_google_api_key_here
   PORT = 10000
   ```

4. **Deploy**: Click "Create Web Service"

## 📁 Files for Render Deployment

Your repository should include these files:

- ✅ `render.yaml` - Render configuration
- ✅ `render_start.py` - Production startup script
- ✅ `build.sh` - Build script for dependencies
- ✅ `requirements.txt` - Python dependencies

## 🔍 How It Works

### Build Process
1. **Install Python dependencies** from `requirements.txt`
2. **Install Node.js dependencies** in `web-gui/`
3. **Build React frontend** to `web-gui/dist/`
4. **Create production bundle**

### Runtime
1. **Single FastAPI server** serves both API and frontend
2. **Static files** served from `/` (frontend)
3. **API endpoints** available at `/health`, `/sessions`, etc.
4. **Auto-scaling** and **SSL** provided by Render

## 🎯 Accessing Your Deployed App

Once deployed, your app will be available at:
```
https://your-app-name.onrender.com/
```

### Available Endpoints:
- **Frontend Dashboard**: `https://your-app-name.onrender.com/`
- **API Documentation**: `https://your-app-name.onrender.com/docs`
- **Health Check**: `https://your-app-name.onrender.com/health`

## 🛠️ Troubleshooting

### Common Issues:

1. **"No open ports detected"**:
   - ✅ Fixed: `render_start.py` uses `PORT` environment variable
   - ✅ Fixed: Server binds to `0.0.0.0:$PORT`

2. **Frontend not loading**:
   - Check build logs for frontend build errors
   - Verify `web-gui/dist/` directory exists after build
   - Check static file serving in browser developer tools

3. **API not working**:
   - Verify `GOOGLE_API_KEY` is set in environment variables
   - Check application logs in Render dashboard
   - Test health endpoint: `/health`

4. **Build failures**:
   - Check if Node.js is available in build environment
   - Verify `build.sh` script has execute permissions
   - Review build logs for specific error messages

### Debugging Commands:

You can test locally with the production setup:
```bash
# Test the build script
./build.sh

# Test the production server
python3 render_start.py
```

## 🔒 Environment Variables

Required:
- `GOOGLE_API_KEY`: Your Google AI API key

Optional:
- `PORT`: Server port (Render sets this automatically)
- `DATABASE_URL`: For persistent storage (PostgreSQL)

## 📈 Scaling

Render automatically handles:
- **SSL certificates** (HTTPS)
- **Auto-scaling** based on traffic
- **Load balancing** for multiple instances
- **Health checks** and **auto-restart**

## 💰 Pricing

- **Starter Plan**: Free for 750 hours/month
- **Standard Plan**: $7/month for always-on service
- **Pro Plan**: $25/month for enhanced features

## 🎉 Success!

Your NPC Engine is now running in production with:
- ✅ **Full-stack deployment** (API + Frontend)
- ✅ **Automatic HTTPS** and SSL
- ✅ **Professional hosting** with uptime monitoring
- ✅ **Scalable infrastructure**
- ✅ **Easy updates** via Git push

Visit your app at `https://your-app-name.onrender.com/` and start creating intelligent NPCs! 🎮 