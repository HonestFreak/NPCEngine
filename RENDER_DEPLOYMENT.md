# 🚀 Deploying NPC Engine to Render

This guide will help you deploy your NPC Engine to Render.com.

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Google API Key**: Get one from [Google AI Studio](https://aistudio.google.com/app/apikey)

## 🔧 Deployment Steps

### 1. **Push Your Code**

Make sure all the new files are committed and pushed:

```bash
git add .
git commit -m "🚀 Add Render deployment configuration"
git push origin main
```

### 2. **Create Web Service on Render**

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your `npc-engine` repository

### 3. **Configure the Service**

Use these settings:

| Setting | Value |
|---------|-------|
| **Name** | `npc-engine-api` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python render_start.py` |
| **Plan** | `Free` (or your preferred plan) |

### 4. **Set Environment Variables**

In Render's environment variables section, add:

| Key | Value | Notes |
|-----|-------|-------|
| `GOOGLE_API_KEY` | `your_actual_api_key_here` | **Required** - Get from Google AI Studio |
| `ENVIRONMENT` | `production` | Optional - Helps identify the environment |

### 5. **Deploy**

1. Click **"Create Web Service"**
2. Render will automatically deploy your app
3. Wait for the build and deployment to complete

## ✅ Verify Deployment

Once deployed, you should be able to access:

- **API Base**: `https://your-app-name.onrender.com`
- **Health Check**: `https://your-app-name.onrender.com/health`
- **API Docs**: `https://your-app-name.onrender.com/docs`
- **API Endpoints**: `https://your-app-name.onrender.com/api/v1/`

## 🧪 Test Your API

Test with curl:

```bash
# Health check
curl https://your-app-name.onrender.com/health

# Create a session
curl -X POST "https://your-app-name.onrender.com/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_render",
    "game_title": "Render Test",
    "persistence": {"type": "memory"}
  }'
```

## 🔧 Troubleshooting

### **No Open Ports Detected**

If you see this error, make sure:
- Your `render_start.py` uses `PORT` environment variable
- The app binds to `0.0.0.0` (not `localhost`)
- Health check endpoint `/health` is working

### **Build Failures**

Common issues:
- Check `requirements.txt` has all dependencies
- Ensure Python version compatibility
- Check build logs for specific errors

### **Runtime Errors**

- Check environment variables are set correctly
- Verify Google API key is valid
- Check application logs in Render dashboard

## 📱 Frontend Deployment (Optional)

The backend API is now deployed! For the frontend:

1. **Option A**: Deploy separately on Vercel/Netlify
2. **Option B**: Use the API from your local frontend during development
3. **Option C**: Serve static files from the backend (advanced)

## 🔗 Next Steps

1. **Custom Domain**: Add a custom domain in Render settings
2. **Database**: Add PostgreSQL for persistent storage
3. **Monitoring**: Set up health checks and alerts
4. **Environment Variables**: Add any additional config needed

Your NPC Engine API is now live and ready for intelligent multi-agent interactions! 🎉 