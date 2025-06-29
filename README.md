<div align="center">

![NPCEngine Logo](./assets/NPCENGINE.png)

# 🎮 NPCEngine - World-Class Intelligent NPC Framework

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4.svg)](https://github.com/google/adk)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

**A multi-agent NPC framework built with Google Agent Development Kit (ADK)**

Create intelligent, personality-driven NPCs with AI capabilities, dynamic interactions, and production-ready architecture for games and interactive applications.

## 🌟 Why NPCEngine?

NPCEngine revolutionizes game development by providing:

🤖 **Google ADK Integration** - Cutting-edge agent orchestration with Gemini LLM  
🧠 **Intelligent Personalities** - Dynamic character traits, memory, and relationships  
⚡ **Sub-second Response** - Optimized for real-time gaming performance  
🏗️ **Production-Ready** - Enterprise-grade architecture with monitoring and scaling  
🔄 **Multi-Agent Coordination** - Complex inter-NPC interactions and world dynamics  
🎯 **Plug-and-Play** - Easy integration with Unity, Unreal, web games, and more  

## ✨ Key Features

### 🤖 **Advanced AI Capabilities**
- **Multi-Agent Orchestration** using Google ADK's sophisticated workflow system
- **Real-time LLM Integration** with Gemini 2.0 Flash for intelligent responses  
- **Dynamic Personality Modeling** with trait evolution and relationship tracking
- **Contextual Memory Systems** for short-term and long-term character memory
- **Autonomous Behavior** with goal-driven decision making

### 🏗️ **Enterprise Architecture**
- **RESTful API** with FastAPI and auto-generated OpenAPI documentation
- **Real-time Dashboard** with React + TypeScript + Vite frontend
- **Flexible Persistence** - In-Memory, PostgreSQL/MySQL/SQLite, or Vertex AI
- **Horizontal Scaling** with session-based architecture
- **Production Monitoring** with structured logging and metrics

### 🎮 **Game Developer Friendly**
- **Multiple Integration Options** - REST API, WebSockets, or direct Python integration
- **Rich Action System** - Configurable NPC actions with validation and constraints
- **Environment Management** - Dynamic world state, weather, time progression
- **Event-Driven Architecture** - Reactive NPCs that respond to game events
- **Comprehensive Testing** - Full test suite with example implementations

## 🚀 Google ADK Modal Features

<details>
<summary><strong>🎯 Click to see complete Google ADK integration details</strong></summary>

### **Multi-Agent Orchestration**
- **LlmAgent Integration**: Each NPC is a full Google ADK agent with tools and reasoning
- **Session Management**: Persistent conversations using ADK SessionService 
- **Tool Integration**: Custom NPC tools (speak, move, emote) with structured outputs
- **Runner Orchestration**: Async agent execution with event streaming

### **Advanced Memory & Persistence**
- **In-Memory Sessions**: Fast development with ADK InMemorySessionService
- **Database Persistence**: Production-ready with ADK DatabaseSessionService 
- **Vertex AI Integration**: Cloud-native with RAG capabilities using VertexAiSessionService

### **Intelligent Agent Features**  
- **Dynamic Tool Usage**: NPCs choose appropriate actions based on context
- **Conversation Continuity**: Persistent memory across interactions
- **Multi-Turn Reasoning**: Complex decision-making with agent workflows
- **Event-Driven Responses**: Reactive agents that respond to environment changes

### **Production Capabilities**
- **Auto-Scaling**: Vertex AI session services scale automatically
- **Monitoring**: Built-in ADK metrics and logging
- **Error Handling**: Graceful fallbacks when ADK services are unavailable
- **Security**: Proper authentication and session isolation

*NPCEngine showcases the full power of Google ADK for sophisticated multi-agent scenarios.*

</details>

## 📁 Project Architecture

```
npc-engine/
├── 🧠 npc_engine/                   # Core framework
│   ├── 📂 core/                     # Business logic
│   │   ├── 🤖 npc_agent.py          # Google ADK agent implementation  
│   │   ├── 🎮 game_session.py       # Session orchestration
│   │   ├── 🌍 environment_manager.py # World state management
│   │   └── ⚡ action_system.py      # Action validation & processing
│   ├── 📂 models/                   # Pydantic data models
│   ├── 📂 api/                      # FastAPI REST endpoints
│   ├── 📂 config/                   # Configuration management
│   └── 📂 utils/                    # Utilities and helpers
├── 🎨 web-gui/                      # React dashboard
├── 📊 examples/                     # Integration examples
│   ├── 🎲 unity_integration/        # Unity C# examples
│   ├── 🌐 javascript_client/        # JS/Node.js examples  
│   ├── 🐍 python_examples/          # Python integration
│   └── 📱 web_examples/             # Web-based examples
├── 🧪 tests/                        # Comprehensive test suite
└── 📚 docs/                         # Documentation
```

## ⚡ Quick Start

### **1️⃣ Installation**

```bash
# Clone the repository
git clone https://github.com/your-org/npc-engine.git
cd npc-engine

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install frontend dependencies  
cd web-gui && npm install && cd ..
```

### **2️⃣ Configuration**

```bash
# Set your Google API key
export GOOGLE_API_KEY="your_gemini_api_key_here"

# Optional: Configure database (default uses in-memory)
export DATABASE_URL="postgresql://user:pass@localhost:5432/npcengine"
```

### **3️⃣ Launch**

```bash
# Start both backend and frontend
python start_npc_engine.py

# Or start backend only
python run_server.py
```

### **4️⃣ Verify**

- 🎨 **Dashboard**: http://localhost:5173
- 🚀 **API**: http://localhost:8000  
- 📖 **Docs**: http://localhost:8000/docs
- 🏥 **Health**: http://localhost:8000/health

## 🎮 Integration Examples

### **Unity Integration**
```csharp
using UnityEngine;
using System.Collections;

public class NPCEngineClient : MonoBehaviour 
{
    private const string API_BASE = "http://localhost:8000";
    
    public async void SendEventToNPC(string npcId, string action, string message)
    {
        var eventData = new {
            action = action,
            initiator = "player",
            target = npcId,
            action_properties = new { message = message }
        };
        
        string json = JsonUtility.ToJson(eventData);
        await PostToAPI($"/sessions/{sessionId}/events", json);
    }
}
```

### **JavaScript Integration**
```javascript
class NPCEngineClient {
    constructor(apiBase = 'http://localhost:8000') {
        this.apiBase = apiBase;
    }
    
    async sendEvent(sessionId, event) {
        const response = await fetch(`${this.apiBase}/sessions/${sessionId}/events`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(event)
        });
        return response.json();
    }
    
    async createSession(config) {
        const response = await fetch(`${this.apiBase}/sessions`, {
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        return response.json();
    }
}
```

### **Python Integration**
```python
from npc_engine import NPCEngine, SessionConfig, NPCData
import asyncio

async def main():
    # Direct Python integration
    engine = NPCEngine()
    
    # Create session
    session = await engine.create_session(SessionConfig(
        session_id="my_game",
        game_title="My Adventure Game",
        npcs=[...],
        environment=...,
        persistence={"type": "database", "database_url": "..."}
    ))
    
    # Send events
    result = await session.process_event({
        "action": "speak",
        "initiator": "player", 
        "action_properties": {"message": "Hello!"}
    })
    
    print(f"NPC Response: {result.primary_npc_response}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🏗️ Production Deployment

### **Environment Configuration**

#### **Backend Configuration**
```bash
# Production settings
export ENVIRONMENT=production
export GOOGLE_API_KEY="your_production_key"
export DATABASE_URL="postgresql://user:pass@prod-db:5432/npcengine"

# Optional: Vertex AI integration
export GOOGLE_CLOUD_PROJECT="your-gcp-project"
export GOOGLE_CLOUD_LOCATION="us-central1"

# Security (recommended)
export SECRET_KEY="your-secret-key"
export ALLOWED_HOSTS="your-domain.com"
```

#### **Frontend Configuration**
When deploying frontend and backend separately (e.g., on Render.com), configure the frontend to connect to the correct backend URL:

```bash
# Frontend environment variable (set in your hosting platform)
export VITE_API_BASE_URL="https://your-backend-url.onrender.com"

# For local development with remote backend
export VITE_API_BASE_URL="https://your-backend-url.onrender.com"
```

**Common Deployment Scenarios:**
- **Render.com**: Set `VITE_API_BASE_URL` in frontend service environment variables
- **Vercel**: Add to environment variables in project settings  
- **Netlify**: Set in site environment variables
- **Local Development**: Create `.env` file in `web-gui/` directory:
  ```
  VITE_API_BASE_URL=https://your-backend-url.onrender.com
  ```

### **Docker Deployment**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "npc_engine.api.npc_api:api.app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t npc-engine .
docker run -p 8000:8000 -e GOOGLE_API_KEY="..." npc-engine
```

### **Render.com Deployment**

Deploy both backend and frontend as separate services on Render.com:

#### **Backend Service**
1. Create a Web Service from your GitHub repo
2. **Environment Variables**:
   ```bash
   GOOGLE_API_KEY=your_google_api_key_here
   PORT=10000
   ```
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `python3 run_server.py`

#### **Frontend Service**
1. Create another Web Service or Static Site
2. **Environment Variables**:
   ```bash
   VITE_API_BASE_URL=https://your-backend-service-name.onrender.com
   ```
3. **Build Command**: `cd web-gui && npm ci && npm run build`
4. **Start Command**: `cd web-gui && npx serve -s dist -l 10000`

> **💡 Tip**: Use the provided `render-separate.yaml` for automatic deployment configuration.

### **Kubernetes Deployment**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: npc-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: npc-engine
  template:
    metadata:
      labels:
        app: npc-engine
    spec:
      containers:
      - name: npc-engine
        image: npc-engine:latest
        ports:
        - containerPort: 8000
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: npc-engine-secrets
              key: google-api-key
```

## ⚙️ Configuration Management

NPCEngine supports multiple configuration approaches for maximum flexibility:

### **Dashboard Configuration** 
- **Real-time Updates**: Changes via dashboard are immediately applied
- **Persistent Storage**: Configurations saved to your chosen backend (YAML/Database)
- **Version Control**: Track configuration changes with timestamps
- **Validation**: Built-in validation prevents invalid configurations

### **YAML Configuration**
```yaml
# config/environment.yaml
name: "Medieval Fantasy World"
locations:
  - id: "tavern"
    name: "The Prancing Pony"
    description: "A cozy tavern with warm lighting"
  - id: "market"
    name: "Town Market"
    description: "Bustling marketplace"

# config/npcs_default.yaml
schemas:
  - id: "merchant"
    name: "Merchant"
    properties:
      - name: "goods"
        type: "list"
        default: ["bread", "ale"]
```

### **Database Configuration**
For production environments, configurations are stored in your database with full audit trails and atomic updates.

## 🚀 Future Roadmap

### **🎮 Game Engine Integration**
- [ ] **Unity Package** - Native Unity integration with C# SDK
- [ ] **Unreal Engine Plugin** - Blueprint and C++ integration  
- [ ] **Godot Extension** - GDScript native integration
- [ ] **JavaScript SDK** - Enhanced web game library

### **🧠 Advanced AI Features**
- [ ] **Multi-Modal NPCs** - Voice, image, and gesture understanding
- [ ] **Procedural Personality Generation** - AI-generated diverse NPCs

### **🛠️ Developer Experience**
- [ ] **Visual NPC Designer** - Drag-and-drop personality and behavior creation
- [ ] **Integration Templates** - One-click setup for popular game engines
- [ ] **Performance Profiler** - Built-in tools for optimization
- [ ] **A/B Testing Framework** - Compare different NPC configurations


## 🤝 Contributing

We welcome contributions from the community! NPCEngine thrives on collaboration.

### **Getting Started**
```bash
# Fork the repository and clone your fork
git clone https://github.com/your-username/npc-engine.git

# Set up development environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v

# Start development server
python start_npc_engine.py --reload
```

### **Contribution Areas**
- 🐛 **Bug Reports & Fixes** - Help us improve stability
- 🎮 **Game Engine Integrations** - Create plugins for popular engines
- 🧪 **Testing** - Expand test coverage and scenarios


---

<div align="center">

**Built with ❤️ by the HonestFreak*

</div> 