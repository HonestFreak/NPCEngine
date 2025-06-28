# 🚀 NPCEngine - Complete Deployment Guide

## 🏠 Local Development

### **Prerequisites**
```bash
# Required software
- Python 3.9+
- Node.js 18+
- Git
- Google API Key (from Google AI Studio)
```

### **1. Setup Project**
```bash
# Clone repository
git clone <your-repo-url>
cd NPCEngine

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### **2. Environment Configuration**
```bash
# Set Google API Key (REQUIRED)
export GOOGLE_API_KEY="your_gemini_api_key_here"

# Optional: Database configuration
export DATABASE_URL="postgresql://user:pass@localhost:5432/npcengine"
```

### **3. Run Locally**

**Option A: Full Stack Development**
```bash
# Starts both backend (port 8000) and frontend (port 5173)
python start_npc_engine.py
```
- 🎨 **Frontend**: http://localhost:5173
- 🚀 **Backend**: http://localhost:8000
- 📖 **API Docs**: http://localhost:8000/docs

**Option B: Backend Only**
```bash
# Starts only the API server
python run_server.py
```
- 🚀 **Backend**: http://localhost:8000
- 📖 **API Docs**: http://localhost:8000/docs

**Option C: Frontend Only (for development)**
```bash
cd web-gui
npm install
npm run dev
```
- 🎨 **Frontend**: http://localhost:5173

---

## ☁️ Render Deployment

### **Option 1: Separate Services** (Recommended for your setup)
*Deploy frontend and backend as separate services*

#### **🎯 Target URLs:**
- 🎨 **Frontend**: https://npcengine.onrender.com
- 🚀 **Backend**: https://npcengine-1.onrender.com

#### **Step 1: Deploy Backend**
1. **Create Web Service** in Render Dashboard
2. **Connect GitHub Repository**
3. **Configure Service:**
   ```
   Name: npcengine-backend
   Environment: Python
   Build Command: pip install -r requirements.txt
   Start Command: python3 run_server.py
   ```
4. **Environment Variables:**
   ```
   GOOGLE_API_KEY = your_api_key_here
   PORT = 10000
   ```
5. **Deploy** → Will be available at `https://npcengine-1.onrender.com`

#### **Step 2: Deploy Frontend**
1. **Create Static Site** in Render Dashboard
2. **Connect Same GitHub Repository**
3. **Configure Service:**
   ```
   Name: npcengine-frontend
   Root Directory: web-gui
   Build Command: npm ci && npm run build
   Publish Directory: dist
   ```
4. **Environment Variables:**
   ```
   VITE_API_BASE_URL = https://npcengine-1.onrender.com
   ```
5. **Deploy** → Will be available at `https://npcengine.onrender.com`

#### **Custom Domain Setup (Optional)**
- Frontend: Point `npcengine.onrender.com` to your custom domain
- Backend: Point `npcengine-1.onrender.com` to your API subdomain

---

### **Option 2: Single Service Blueprint**
*Everything served from one URL - Simpler setup*

#### **Quick Deploy:**
1. **Push code** with existing `render.yaml`
2. **Render Dashboard** → "New +" → "Blueprint"
3. **Connect repository**
4. **Set Environment Variables:**
   ```
   GOOGLE_API_KEY = your_api_key_here
   ```
5. **Deploy** → Everything at one URL

---

## 🔧 Configuration Files

### **For Separate Services:**
Use the `render-separate.yaml` I created:

```yaml
services:
  # Backend API Service
  - type: web
    name: npcengine-backend
    env: python
    region: oregon
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: python3 run_server.py
    envVars:
      - key: GOOGLE_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: PORT
        value: 10000
    healthCheckPath: /health

  # Frontend Service  
  - type: web
    name: npcengine-frontend
    env: node
    region: oregon
    plan: starter
    buildCommand: cd web-gui && npm ci && npm run build
    startCommand: cd web-gui && npx serve -s dist -l 10000
    envVars:
      - key: NODE_VERSION
        value: 18.17.0
      - key: VITE_API_BASE_URL
        value: https://npcengine-1.onrender.com
```

### **For Single Service:**
Use existing `render.yaml`:

```yaml
services:
  - type: web
    name: npc-engine
    env: python
    region: oregon
    plan: starter
    buildCommand: ./build.sh
    startCommand: python3 render_start.py
    envVars:
      - key: GOOGLE_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.0
    healthCheckPath: /health 
```

---

## 🛠️ Troubleshooting

### **Local Development Issues:**

**❌ "GOOGLE_API_KEY not set"**
```bash
# Set the environment variable
export GOOGLE_API_KEY="your_key_here"
# Or create .env file:
echo "GOOGLE_API_KEY=your_key_here" > .env
```

**❌ Frontend not connecting to backend**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check CORS in browser console
# Make sure API calls are going to correct URL
```

**❌ "Module not found" errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt
cd web-gui && npm install
```

### **Render Deployment Issues:**

**❌ "No open ports detected"**
- ✅ Backend uses `PORT` environment variable (auto-set by Render)
- ✅ Frontend serves on port 10000

**❌ API calls failing**
- ✅ Check `VITE_API_BASE_URL` environment variable
- ✅ Verify backend URL is accessible: `https://npcengine-1.onrender.com/health`
- ✅ Check browser network tab for CORS errors

**❌ Build failures**
- ✅ Check build logs in Render dashboard
- ✅ Verify all dependencies in `requirements.txt` and `package.json`

---

## 📊 Service Status Checks

### **Health Endpoints:**
- **Backend Health**: `https://npcengine-1.onrender.com/health`
- **API Documentation**: `https://npcengine-1.onrender.com/docs`
- **Frontend**: `https://npcengine.onrender.com/`

### **Local Testing:**
```bash
# Test backend health
curl http://localhost:8000/health

# Test session creation
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "game_title": "Test Game", "npcs": [], "environment": {}}'
```

---

## 💰 Render Pricing

### **Separate Services (2 services):**
- **Starter Plan**: Free tier (750 hours/month each)
- **Standard Plan**: $7/month each service = $14/month total
- **Pro Plan**: $25/month each service = $50/month total

### **Single Service (1 service):**
- **Starter Plan**: Free tier (750 hours/month)
- **Standard Plan**: $7/month total
- **Pro Plan**: $25/month total

---

## 🚀 Production Best Practices

### **Environment Variables:**
```bash
# Required
GOOGLE_API_KEY=your_production_key

# Optional
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
LOG_LEVEL=INFO
```

### **Monitoring:**
- Use Render's built-in monitoring
- Check logs regularly: Render Dashboard → Service → Logs
- Set up alerts for service downtime

### **Security:**
- Use strong API keys
- Enable HTTPS (automatic on Render)
- Configure CORS properly for production domains
- Don't commit secrets to GitHub

---

## 🎉 Success Checklist

- [ ] **Local Development Working**: Both frontend and backend run locally
- [ ] **Environment Variables Set**: Google API key configured
- [ ] **Backend Deployed**: API accessible at your backend URL
- [ ] **Frontend Deployed**: Dashboard accessible at your frontend URL
- [ ] **API Integration**: Frontend successfully connects to backend
- [ ] **Health Checks**: All endpoints responding correctly
- [ ] **Testing**: Can create sessions and interact with NPCs

Your NPCEngine is now production-ready! 🎮✨ 