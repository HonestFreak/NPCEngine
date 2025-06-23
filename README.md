<div align="center">

![NPC Engine Logo](./assets/NPCENGINE.png)

# 🎮 NPC Engine - Google ADK Multi-Agent Framework

</div>

A sophisticated **multi-agent orchestration system** built with **Google Agent Development Kit (ADK)** for creating intelligent, personality-driven NPCs in games and interactive applications.

## 🎯 Project Focus: Automation of Complex Processes

This project demonstrates **sophisticated multi-agent workflows** that automate complex character interactions, dynamic personality modeling, and intelligent decision-making using Google ADK's agent orchestration capabilities.

## ✨ Key Features

### 🤖 **Google ADK Integration**
- **Real-time LLM integration** with Gemini 1.5 Flash
- **Multi-agent orchestration** with intelligent agent-to-agent communication
- **Dynamic tool usage** and function calling
- **Flexible session persistence** - In-Memory, Database (PostgreSQL/MySQL/SQLite), and Vertex AI

### 🧠 **Advanced AI Capabilities**
- **Personality-driven responses** based on traits, background, and goals
- **Contextual memory systems** (short-term and long-term)
- **Relationship tracking** between characters
- **Sequential action support** for complex behaviors
- **Emotion and mood modeling**

### 🎯 **Professional Architecture**
- **RESTful API** with FastAPI and auto-generated documentation
- **Real-time frontend** with React + TypeScript + Vite
- **Modular design** with clean separation of concerns
- **Comprehensive validation** with Pydantic models
- **Production-ready** error handling and logging

![NPC Engine Diagram](./assets/simple_diagram.png)


## 📁 Project Structure

```
npc-engine/
├── 📂 npc_engine/               # Core engine package
│   ├── 📂 core/                 # Core business logic
│   │   ├── 🧠 npc_agent.py      # Google ADK agent implementation
│   │   ├── 🎮 game_session.py   # Session management
│   │   ├── 🌍 environment_manager.py # World state management
│   │   └── ⚡ action_system.py  # Action validation & processing
│   ├── 📂 models/               # Data models & schemas
│   │   ├── 👥 npc_models.py     # NPC personality, state, memory
│   │   ├── 🎯 action_models.py  # Action definitions & validation
│   │   ├── 🌍 environment_models.py # Locations, weather, events
│   │   └── 🌐 api_models.py     # Request/response schemas
│   ├── 📂 api/                  # REST API layer
│   │   └── 🚀 npc_api.py        # FastAPI server with all endpoints
│   └── 📂 config/               # Configuration system
│       ├── ⚙️ config_loader.py  # YAML config management
│       ├── 👥 npc_config.py     # NPC schema definitions
│       ├── 🎯 action_config.py  # Action configuration
│       └── 🌍 environment_config.py # Environment settings
├── 📂 config/                   # Configuration files
│   ├── 📄 actions.yaml          # Action definitions
│   ├── 📄 environment.yaml      # Environment settings
│   ├── 📄 sample_npcs.yaml      # Sample NPC configurations
│   ├── 📄 sample_actions.yaml   # Sample action examples
│   └── 📄 sample_environment.yaml # Sample environment setup
├── 📂 web-gui/                  # Frontend application
│   ├── 📂 src/
│   │   ├── 📂 components/       # React components
│   │   │   ├── 🎛️ Dashboard.tsx  # Main control panel
│   │   │   ├── 👥 NPCManager.tsx # NPC creation & management
│   │   │   ├── 🎯 ActionConfig.tsx # Action configuration UI
│   │   │   ├── 🌍 EnvironmentConfig.tsx # Environment setup
│   │   │   ├── 🎮 SessionManager.tsx # Game session controls
│   │   │   └── 👁️ NPCViewer.tsx  # NPC state visualization
│   │   └── 📱 App.tsx           # Main application
├── 📂 examples/                 # Usage examples
│   ├── 🏰 medieval_town_demo.py # Complex multi-NPC scenario
│   └── 🎲 simple_demo.py       # Basic usage example
├── 🧪 test_npc_engine.py       # Comprehensive test suite
├── 🧪 test_complete_demo.py     # Full integration demo
├── 🚀 run_server.py             # API server launcher
├── 🎮 start_npc_engine.py       # Full-stack launcher
└── 📋 requirements.txt          # Python dependencies
```

![NPC Engine Diagram](./assets/chart1.png)


## 🚀 Setup & Installation

### **📋 Prerequisites**

Before setting up the NPC Engine, ensure you have:

- **Python 3.8+** (Python 3.10+ recommended)
- **Node.js 16+** and **npm** (for frontend)
- **Google API Key** with Gemini API access

### **🔑 Getting Google API Key**

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key for Gemini
3. Copy the API key for later use

### **📥 Step 1: Clone & Install**

```bash
# Clone the repository
git clone <repository-url>
cd npc-engine

# Create and activate virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd web-gui
npm install
cd ..
```

### **⚙️ Step 2: Environment Configuration**

Create your environment configuration:

```bash
# Create .env file with your API key
echo "GOOGLE_API_KEY=your_actual_api_key_here" > .env

# Or set environment variable directly
export GOOGLE_API_KEY="your_actual_api_key_here"
```

**Example .env file:**
```bash
# Required: Google API Key for Gemini LLM
GOOGLE_API_KEY=AIzaSyD...your_key_here

# Optional: Database configuration (for production)
DATABASE_URL=postgresql://user:password@localhost:5432/npc_engine

# Optional: Vertex AI configuration
GOOGLE_CLOUD_PROJECT=your-gcp-project
GOOGLE_CLOUD_LOCATION=us-central1
```

### **🧪 Step 3: Verify Installation**

Test that everything is working:

```bash
# Run the test suite
python test_npc_engine.py

# Expected output:
# ✅ Data model validation tests passed
# ✅ Basic functionality tests passed  
# ✅ API server tests passed
# ✅ All tests completed successfully!
```

### **🚀 Step 4: Launch the System**

Choose your preferred launch method:

#### **🎨 Option A: Full Stack (Recommended)**
```bash
python start_npc_engine.py
```
**This starts:**
- 🚀 **Backend API**: http://localhost:8000
- 🎨 **Frontend GUI**: http://localhost:5173  
- 📖 **API Docs**: http://localhost:8000/docs

#### **⚡ Option B: Backend Only**
```bash
python run_server.py
```
**This starts:**
- 🚀 **Backend API**: http://localhost:8000
- 📖 **API Docs**: http://localhost:8000/docs

#### **🧪 Option C: Demo First**
```bash
# Run a complete demo
python test_complete_demo.py

# Or run specific examples
python examples/simple_demo.py
python examples/medieval_town_demo.py
```

### **✅ Step 5: Verify Everything Works**

1. **Visit the Frontend**: http://localhost:5173
   - You should see the NPC Engine Dashboard
   - Try creating a new session

2. **Check API Documentation**: http://localhost:8000/docs
   - Interactive Swagger documentation
   - Test endpoints directly

3. **Create Your First Session**:
   ```bash
   curl -X POST "http://localhost:8000/sessions" \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "test_session",
       "game_title": "My First Game",
       "npcs": [],
       "environment": {"time_of_day": "morning"},
       "persistence": {"type": "memory"}
     }'
   ```


#### **Database Setup (Optional):**

For production persistence, set up a database:

```bash
# PostgreSQL example
createdb npc_engine
export DATABASE_URL="postgresql://user:password@localhost:5432/npc_engine"

# SQLite example (simpler)
export DATABASE_URL="sqlite:///./npc_engine.db"
```

### **🔧 Development Setup**

For development work:

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black isort mypy

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Run in development mode
export ENVIRONMENT=development
python start_npc_engine.py --reload
```

### **🐳 Docker Setup (Alternative)**

If you prefer Docker:

```bash
# Build the container
docker build -t npc-engine .

# Run with environment variables
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY="your_key_here" \
  npc-engine

# Or use docker-compose
docker-compose up
```

### **📱 Quick Test**

Once everything is running, test the system:

```bash
# Create a test session via API
curl -X POST "http://localhost:8000/sessions" \
  -H "Content-Type: application/json" \
  -d @config/sample_session.json

# Send a test event
curl -X POST "http://localhost:8000/sessions/test_session/events" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "speak",
    "initiator": "player",
    "action_properties": {"message": "Hello!"}
  }'
```

🎉 **Congratulations!** Your NPC Engine is now running and ready for intelligent multi-agent interactions!

![NPC Engine Diagram](./assets/chart2.png)

## 💾 Session Persistence

The NPC Engine supports multiple persistence strategies using Google ADK SessionService implementations:

### **📦 Persistence Types**
- **💾 In-Memory**: Fast, zero-config, perfect for development (data lost on restart)
- **🗄️ Database**: Production-ready with PostgreSQL, MySQL, or SQLite support  
- **☁️ Vertex AI**: Cloud-native with Google AI integration and RAG capabilities

### **⚙️ Configuration**
```json
{
  "persistence": {
    "type": "database",
    "database_url": "postgresql://user:pass@localhost:5432/npc_engine"
  }
}
```

### **🎯 Use Cases**
- **Development**: Use in-memory for rapid prototyping
- **Production**: Use database for persistent, scalable sessions
- **AI-Enhanced**: Use Vertex AI for cloud-native deployments with enhanced memory

📖 **Full Documentation**: See [SESSION_PERSISTENCE.md](./SESSION_PERSISTENCE.md) for complete setup guide, API usage, and best practices.

## 📋 Core Components Deep Dive

### 🧠 **NPCAgent** (`npc_engine/core/npc_agent.py`)

The heart of the system - a Google ADK agent that powers intelligent NPC behavior.

**Key Functions:**
- `__init__(npc_data, model_name)` - Initialize ADK agent with personality
- `process_event(event, context)` - Main event processing with LLM integration  
- `_generate_intelligent_response(event, context)` - Context-aware AI decision making
- `_build_comprehensive_prompt(event, context)` - Dynamic prompt generation
- `get_state_snapshot()` - Current NPC state for frontend
- `update_relationship(character, relationship)` - Dynamic relationship management

**ADK Integration:**
- Uses `LlmAgent` for Gemini LLM integration
- Implements `InMemorySessionService` for session management
- Custom tools: `speak()`, `show_emotion()`, `move_to()`

### 🎮 **GameSession** (`npc_engine/core/game_session.py`)

Orchestrates multiple NPC agents and manages the game world.

**Key Functions:**
- `__init__(config)` - Initialize session with NPCs and environment
- `start()` - Activate all NPCs and systems
- `process_event(event)` - Route events to appropriate NPCs
- `get_session_status()` - Real-time session information
- `stop()` - Clean shutdown of all agents

### 🌍 **EnvironmentManager** (`npc_engine/core/environment_manager.py`)

Manages the game world state, locations, weather, and global events.

**Key Functions:**
- `update_time_and_weather()` - Dynamic world progression
- `add_location(location)` - Expand the world
- `get_npcs_in_location(location_id)` - Spatial queries
- `trigger_event(event)` - World-wide event broadcasting

### 🎯 **ActionSystem** (`npc_engine/core/action_system.py`)

Validates and manages all possible NPC actions with rich property validation.

**Key Functions:**
- `validate_action(action)` - Comprehensive action validation
- `get_action_definition(action_type)` - Action schema lookup
- `get_actions_for_category(category)` - Filtered action lists
- `_validate_property(value, prop_def)` - Property validation with rules

## 🎯 Available Actions

The system supports rich, configurable actions with validation:

### 💬 **SPEAK**
- `message` (string, required): What to say
- `tone` (string, optional): neutral|friendly|angry|excited|sad|mysterious|formal|casual

### 🚶 **MOVE** 
- `destination` (string, required): Location to move to
- `movement_type` (string, optional): walk|run|sneak|rush
- `reason` (string, optional): Why moving there

### 😊 **EMOTE**
- `emotion` (string, required): happy|sad|angry|excited|curious|confused|surprised|worried|relieved|proud
- `intensity` (int, optional): 1-10 intensity level

### 🔧 **INTERACT**
- `interaction_type` (string, required): use|examine|take|give|open|close|activate|repair|clean|craft  
- `item` (string, optional): Item to use in interaction

### ⏸️ **WAIT**
- `duration` (float, optional): Seconds to wait (0.1-10.0)
- `reason` (string, optional): Why waiting

## 🌐 API Endpoints

### **🏥 System Health**
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0", 
  "uptime": 3600.5,
  "active_sessions": 2,
  "total_npcs": 8
}
```

### **🎮 Session Management**

#### Create New Session
```http
POST /sessions
Content-Type: application/json

{
  "session_id": "my_game_session",
  "game_title": "Medieval Adventure",
  "npcs": [
    {
      "npc_id": "merchant_01",
      "name": "Gareth the Trader",
      "role": "Merchant",
      "personality_traits": ["shrewd", "honest", "worldly"],
      "background": "A well-traveled merchant",
      "dialogue_style": "formal",
      "goals": ["help visitors", "trade goods"]
    }
  ],
  "environment": {
    "locations": [
      {
        "location_id": "market_square",
        "name": "Market Square",
        "description": "Bustling marketplace"
      }
    ],
    "time_of_day": "afternoon",
    "weather": "sunny"
  },
  "persistence": {
    "type": "memory" // or "database" or "vertexai"
  }
}
```

#### List All Sessions
```http
GET /sessions
```
**Response:**
```json
[
  {
    "session_id": "my_game_session",
    "game_title": "Medieval Adventure", 
    "created_at": "2024-01-01T12:00:00Z",
    "last_activity": "2024-01-01T12:30:00Z",
    "npc_count": 3,
    "total_events": 45,
    "status": "active",
    "environment": "afternoon"
  }
]
```

#### Get Session Status
```http
GET /sessions/{session_id}
```

#### Delete Session
```http
DELETE /sessions/{session_id}
```

#### Get Session Services Info
```http
GET /sessions/services
```
**Response:**
```json
{
  "services_summary": {
    "total_services": 2,
    "service_types": ["InMemorySessionService", "DatabaseSessionService"]
  },
  "sessions": {
    "session_1": {
      "persistence_type": "memory",
      "service_type": "InMemorySessionService",
      "status": "active"
    }
  }
}
```

### **🎯 Event Processing**

#### Send Event to NPCs
```http
POST /sessions/{session_id}/events
Content-Type: application/json

{
  "action": "speak",
  "initiator": "player",
  "target": "merchant_01",
  "location": "market_square",
  "action_properties": {
    "message": "Hello! What do you have for sale?",
    "tone": "friendly"
  },
  "additional_context": {
    "source": "game_client",
    "timestamp": "2024-01-01T12:00:00Z"
  },
  "priority": 5
}
```
**Response:**
```json
{
  "success": true,
  "event_id": "evt_123456",
  "session_id": "my_game_session",
  "message": "Event 'speak' processed successfully",
  "action_details": [
    {
      "npc_id": "merchant_01",
      "npc_name": "Gareth the Trader",
      "action_type": "speak",
      "action_properties": {
        "message": "Welcome! I have fine goods from distant lands.",
        "tone": "enthusiastic"
      },
      "reasoning": "Responding to friendly greeting from potential customer",
      "success": true
    }
  ],
  "processing_complete": true
}
```

#### Test Event (Simplified)
```http
POST /sessions/{session_id}/events/test
Content-Type: application/json

{
  "event_type": "player_to_npc",
  "action": "attack",
  "source_id": "player",
  "target_id": "merchant_01",
  "action_data": {}
}
```

### **👥 NPC Management**

#### List Session NPCs
```http
GET /sessions/{session_id}/npcs
```
**Response:**
```json
[
  {
    "npc_id": "merchant_01",
    "name": "Gareth the Trader",
    "role": "Merchant",
    "location": "market_square",
    "activity": "standing",
    "mood": "content",
    "health": 100.0,
    "energy": 85.0,
    "adk_available": true
  }
]
```

#### Get Specific NPC Status
```http
GET /sessions/{session_id}/npcs/{npc_id}
```

#### Spawn NPCs in Session
```http
POST /sessions/{session_id}/spawn-npcs
Content-Type: application/json

{
  "npc_ids": ["npc_villager_001", "npc_guard_001"] // Optional, spawns all if not provided
}
```

### **🌍 Environment Management**

#### Update Environment
```http
PUT /sessions/{session_id}/environment
Content-Type: application/json

{
  "time_of_day": "evening",
  "weather": "rainy", 
  "world_properties": {
    "magic_level": "high",
    "danger_level": 3
  }
}
```

#### Get Environment Status
```http
GET /sessions/{session_id}/environment
```

### **⚙️ Configuration Management**

#### Action Configuration
```http
GET /config/actions                    # Get action config
PUT /config/actions                    # Update action config
GET /config/actions/definitions        # Get all action definitions with properties
```

#### NPC Configuration
```http
GET /config/npcs                       # Get NPC configuration
PUT /config/npcs                       # Update NPC configuration
GET /config/npcs/schemas               # Get NPC schemas/templates
POST /config/npcs/schemas              # Add new NPC schema
PUT /config/npcs/schemas/{schema_id}   # Update NPC schema
DELETE /config/npcs/schemas/{schema_id} # Delete NPC schema
GET /config/npcs/instances             # Get NPC instances
POST /config/npcs/instances            # Add NPC instance
PUT /config/npcs/instances/{npc_id}    # Update NPC instance
DELETE /config/npcs/instances/{npc_id} # Delete NPC instance
POST /config/npcs/instances/bulk       # Add multiple NPC instances
```

#### Environment Configuration
```http
GET /config/environment                # Get environment config
PUT /config/environment                # Update environment config
```

#### Player Actions Configuration
```http
GET /config/player-actions             # Get player action config
PUT /config/player-actions             # Update player action config
```

#### Game Templates
```http
GET /templates/session                 # Get session template
GET /config/game/{game_name}          # Get specific game configuration
POST /sessions/from-config/{config_name} # Create session from saved config
POST /config/generate-samples          # Generate sample configurations
```

### **📋 Request/Response Models**

#### SessionConfig Model
```json
{
  "session_id": "string",
  "game_title": "string", 
  "npcs": [NPCData],
  "environment": EnvironmentConfig,
  "persistence": {
    "type": "memory|database|vertexai",
    "database_url": "string", // for database type
    "vertexai_project": "string", // for vertexai type
    "vertexai_location": "string", // for vertexai type
    "vertexai_corpus": "string" // optional for vertexai type
  }
}
```

#### EventRequest Model
```json
{
  "action": "string",
  "initiator": "string",
  "target": "string|null",
  "location": "string",
  "action_properties": {},
  "additional_context": {},
  "priority": 1-10
}
```

#### NPCData Model
```json
{
  "npc_id": "string",
  "name": "string",
  "role": "string", 
  "personality_traits": ["string"],
  "background": "string",
  "dialogue_style": "string",
  "goals": ["string"],
  "relationships": {},
  "state": {
    "current_location": "string",
    "current_activity": "string", 
    "mood": "string",
    "health": 0-100,
    "energy": 0-100
  }
}
```

### **🔍 Interactive API Documentation**

Visit **http://localhost:8000/docs** when running the server for:
- 📖 **Complete API documentation** with interactive testing
- 🧪 **Try-it-out functionality** for all endpoints
- 📝 **Request/response schemas** with examples
- 🔐 **Authentication details** (if applicable)

### **💡 Usage Examples**

#### Complete Session Workflow
```bash
# 1. Create session
curl -X POST "http://localhost:8000/sessions" \
  -H "Content-Type: application/json" \
  -d @session_config.json

# 2. Send player action
curl -X POST "http://localhost:8000/sessions/my_session/events" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "speak",
    "initiator": "player", 
    "target": "merchant_01",
    "location": "market_square",
    "action_properties": {
      "message": "Hello there!"
    }
  }'

# 3. Check NPC status
curl "http://localhost:8000/sessions/my_session/npcs/merchant_01"

# 4. Update environment
curl -X PUT "http://localhost:8000/sessions/my_session/environment" \
  -H "Content-Type: application/json" \
  -d '{"time_of_day": "night", "weather": "stormy"}'
```

### **⚡ WebSocket Support**
*Coming Soon: Real-time event streaming for live game integration*

## 🎨 Frontend Features

### 🎛️ **Dashboard** 
- Real-time session monitoring
- NPC status overview
- Environment state display
- Event history timeline

### 👥 **NPC Manager**
- Create/edit NPCs with rich personalities
- Configure traits, background, goals, relationships
- Visual state management
- Memory system visualization

### 🎯 **Action Configuration**
- Browse all available actions
- View detailed property schemas  
- Configure custom actions
- Enable/disable default actions
- See validation rules and examples

### 🌍 **Environment Configuration**
- Create and manage locations
- Set weather and time conditions
- Configure world properties
- Define location connections

### 🎮 **Session Manager**
- Start/stop game sessions
- Load predefined configurations  
- Monitor active NPCs
- View real-time events

## 🧪 Testing

### **Comprehensive Test Suite** (`test_npc_engine.py`)
- ✅ Data model validation
- ✅ Basic functionality testing  
- ✅ API server testing
- ✅ Full demo integration
- ✅ Mock vs real LLM testing

### **Full Integration Demo** (`test_complete_demo.py`)
- 🏰 Multi-NPC medieval town scenario
- 💬 Real conversation dynamics
- 🎯 Action sequence demonstrations
- 📊 Performance metrics
- 🔄 Relationship evolution

```bash
# Run all tests
python test_npc_engine.py

# Run full demo
python test_complete_demo.py

# Run specific examples
python examples/simple_demo.py
python examples/medieval_town_demo.py
```

## ⚙️ Configuration System

### **YAML-Based Configuration**
- `config/actions.yaml` - Action definitions and settings
- `config/environment.yaml` - World configuration  
- `config/sample_npcs.yaml` - Pre-built NPC templates

### **Runtime Configuration**
- Dynamic action enabling/disabling
- Custom property validation rules
- Personality trait templates
- Relationship modeling parameters

## 🎯 Multi-Agent Orchestration

This system demonstrates sophisticated **Google ADK multi-agent workflows**:

### **Agent Communication**
- NPCs can observe and react to each other's actions
- Shared environment state enables coordinated behaviors
- Event propagation system for multi-agent scenarios

### **Intelligent Decision Making**
- Context-aware prompting with full world state
- Personality-driven decision trees
- Memory-informed responses
- Relationship-based interactions

### **Complex Process Automation**
- **Sequential Action Chains**: NPCs can perform multi-step tasks
- **Environmental Adaptation**: Dynamic responses to world changes
- **Social Dynamics**: Relationship evolution and social modeling
- **Event-Driven Architecture**: Reactive behaviors to game events

## 🏆 Project Highlights

### **Technical Excellence**
- ✅ **Google ADK Integration**: Full agent orchestration platform
- ✅ **Production Architecture**: Scalable, maintainable, documented
- ✅ **Real-time Performance**: Sub-second response times
- ✅ **Comprehensive Testing**: Full test coverage with demos

### **Innovation & Sophistication**
- 🧠 **Advanced AI Integration**: Context-aware personality modeling
- 🔗 **Multi-Agent Coordination**: Sophisticated inter-agent communication
- 🎯 **Dynamic Validation**: Real-time action and property validation
- 📊 **Rich Analytics**: Memory systems and relationship tracking

### **User Experience**
- 🎨 **Professional Frontend**: Modern React interface
- 📖 **Complete Documentation**: API docs, examples, tutorials
- 🚀 **Easy Deployment**: One-command setup and launch
- 🔧 **Configurable**: Extensive customization options

## 🚀 Installation & Deployment

### **Development Setup**
```bash
git clone <repo>
cd npc-engine
pip install -r requirements.txt
export GOOGLE_API_KEY="your_key"
python start_npc_engine.py
```

### **Production Deployment**
```bash
# Docker setup (optional)
docker build -t npc-engine .
docker run -p 8000:8000 -e GOOGLE_API_KEY="your_key" npc-engine

# Or direct production
pip install -r requirements.txt
python run_server.py --host 0.0.0.0 --port 8000
```

## 📄 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**Built with ❤️ using Google ADK**

*Demonstrating the future of multi-agent AI systems in interactive applications.* 