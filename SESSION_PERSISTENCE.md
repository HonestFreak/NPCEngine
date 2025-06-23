# Session Persistence in NPC Engine

The NPC Engine now supports multiple session persistence options using Google Agent Development Kit (ADK) SessionService implementations. This allows you to choose the best persistence strategy for your use case.

## Overview

Session persistence determines how your game sessions, NPC states, conversations, and events are stored and maintained. The engine supports three persistence types:

- **💾 In-Memory**: Fast, no setup, but data is lost on restart
- **🗄️ Database**: Persistent SQL storage with full query capabilities  
- **☁️ Vertex AI**: Google Cloud integration with AI-enhanced features

## Persistence Types

### In-Memory Persistence

**Best for**: Development, testing, temporary sessions

```json
{
  "persistence": {
    "type": "memory"
  }
}
```

**Pros:**
- Fastest performance
- No configuration required
- No external dependencies

**Cons:**
- Data lost when server restarts
- Not suitable for production
- Limited scalability

### Database Persistence

**Best for**: Production deployments, data archival, analytics

```json
{
  "persistence": {
    "type": "database",
    "database_url": "postgresql://user:password@localhost:5432/npc_engine"
  }
}
```

**Supported databases:**
- PostgreSQL: `postgresql://user:password@host:port/database`
- MySQL: `mysql://user:password@host:port/database`
- SQLite: `sqlite:///path/to/database.db`

**Pros:**
- Persistent storage across restarts
- Full SQL query capabilities
- Scalable for multiple sessions
- Data backup and recovery options

**Cons:**
- Requires database setup
- Additional infrastructure complexity
- Slightly slower than in-memory

### Vertex AI Persistence

**Best for**: AI-enhanced applications, cloud-native deployments

```json
{
  "persistence": {
    "type": "vertexai",
    "vertexai_project": "your-gcp-project-id",
    "vertexai_location": "us-central1",
    "vertexai_corpus": "optional-rag-corpus-id"
  }
}
```

**Pros:**
- Cloud-native with auto-scaling
- Integration with Google AI services
- RAG (Retrieval-Augmented Generation) support
- Managed infrastructure

**Cons:**
- Requires Google Cloud Platform account
- Higher costs for large volumes
- Requires GCP setup and authentication

## Configuration

### Frontend Configuration

When creating a session through the dashboard, you can select the persistence type and configure its settings:

1. **Session Creation Modal**: Choose from three persistence options
2. **Configuration Forms**: Each type shows relevant configuration fields
3. **Validation**: Form validates required fields before submission
4. **Persistence Indicators**: Active sessions show their persistence type with icons

### Programmatic Configuration

#### Creating a Session with Persistence

```python
from npc_engine.models.api_models import SessionConfig, SessionPersistenceConfig

# Memory persistence (default)
memory_config = SessionPersistenceConfig(type="memory")

# Database persistence
db_config = SessionPersistenceConfig(
    type="database",
    database_url="postgresql://user:pass@localhost:5432/npc_engine"
)

# Vertex AI persistence
vertexai_config = SessionPersistenceConfig(
    type="vertexai",
    vertexai_project="my-gcp-project",
    vertexai_location="us-central1",
    vertexai_corpus="my-rag-corpus"  # Optional
)

# Create session with chosen persistence
session_config = SessionConfig(
    session_id="my_session",
    game_title="My Game",
    persistence=db_config,  # Use any of the above configs
    npcs=[],
    environment=environment,
    available_actions=[]
)
```

#### API Usage

```bash
# Create session with database persistence
curl -X POST "http://localhost:8000/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "persistent_session",
    "game_title": "My Persistent Game",
    "persistence": {
      "type": "database",
      "database_url": "sqlite:///./game_sessions.db"
    },
    "npcs": [],
    "environment": {...},
    "available_actions": []
  }'
```

## Monitoring and Management

### Session Services Endpoint

Monitor active session services:

```bash
curl http://localhost:8000/sessions/services
```

Response:
```json
{
  "services_summary": {
    "active_services": 2,
    "service_types": ["InMemorySessionService", "DatabaseSessionService"],
    "has_default": false
  },
  "sessions": {
    "session_1": {
      "persistence_type": "memory",
      "service_type": "InMemorySessionService",
      "game_title": "Test Game",
      "status": "active"
    },
    "session_2": {
      "persistence_type": "database", 
      "service_type": "DatabaseSessionService",
      "game_title": "Production Game",
      "status": "active"
    }
  },
  "total_sessions": 2
}
```

### Session Status

Each session shows its persistence configuration:

```json
{
  "session_id": "my_session",
  "status": "active",
  "persistence": {
    "type": "database",
    "service_type": "DatabaseSessionService", 
    "configured": true
  }
}
```

## Setup Requirements

### Database Persistence Setup

1. **Install database dependencies**:
   ```bash
   pip install sqlalchemy psycopg2-binary  # For PostgreSQL
   pip install sqlalchemy pymysql         # For MySQL
   # SQLite included with Python
   ```

2. **Create database**:
   ```sql
   -- PostgreSQL example
   CREATE DATABASE npc_engine;
   CREATE USER npc_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE npc_engine TO npc_user;
   ```

3. **Configure connection**:
   ```bash
   export DATABASE_URL="postgresql://npc_user:secure_password@localhost:5432/npc_engine"
   ```

### Vertex AI Persistence Setup

1. **Install Vertex AI dependencies**:
   ```bash
   pip install google-adk[vertexai]
   ```

2. **Set up Google Cloud authentication**:
   ```bash
   # Install Google Cloud SDK
   curl https://sdk.cloud.google.com | bash
   
   # Authenticate
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   
   # Enable APIs
   gcloud services enable aiplatform.googleapis.com
   ```

3. **Create RAG Corpus (optional)**:
   ```bash
   gcloud ai rag-corpora create \
     --display-name="NPC Engine Corpus" \
     --location=us-central1
   ```

## Best Practices

### Development
- Use **in-memory** persistence for rapid prototyping
- Switch to **database** for integration testing
- Test persistence layer independently

### Production
- Use **database** persistence for most production scenarios
- Consider **Vertex AI** for AI-enhanced features or cloud deployments
- Always configure backups for database persistence
- Monitor storage usage and performance

### Security
- Use environment variables for database credentials
- Enable SSL/TLS for database connections
- Follow GCP security best practices for Vertex AI
- Regularly update dependencies

### Performance
- Use connection pooling for database persistence
- Monitor session service performance
- Consider session cleanup policies
- Profile memory usage for in-memory persistence

## Migration

### From In-Memory to Database

1. Export existing session data (if possible)
2. Set up database infrastructure
3. Update session creation to use database persistence
4. Test with sample sessions
5. Migrate remaining sessions

### From Database to Vertex AI

1. Export session data from database
2. Set up Vertex AI resources
3. Create migration scripts
4. Test with subset of data
5. Gradually migrate sessions

## Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check database connectivity
telnet localhost 5432

# Verify credentials
psql -h localhost -U npc_user -d npc_engine
```

#### Vertex AI Authentication
```bash
# Check authentication
gcloud auth list

# Verify project access
gcloud projects describe YOUR_PROJECT_ID
```

#### Service Creation Failures
- Check application logs for detailed error messages
- Verify configuration parameters
- Ensure required dependencies are installed
- Test service creation independently

### Debugging

Enable debug logging:
```python
import logging
logging.getLogger('npc_engine').setLevel(logging.DEBUG)
```

Check session service manager:
```python
from npc_engine.core.session_service_factory import session_service_manager
info = session_service_manager.get_active_services_info()
print(info)
```

## API Reference

### SessionPersistenceConfig

```python
class SessionPersistenceConfig(BaseModel):
    type: str  # 'memory', 'database', or 'vertexai'
    database_url: Optional[str] = None
    vertexai_project: Optional[str] = None 
    vertexai_location: Optional[str] = "us-central1"
    vertexai_corpus: Optional[str] = None
```

### Endpoints

- `GET /sessions/services` - Get session services information
- `GET /sessions/{session_id}` - Includes persistence info in response
- `POST /sessions` - Create session with persistence configuration

## Examples

### Complete Session Creation Examples

See the `examples/` directory for complete working examples:

- `examples/memory_session.py` - In-memory session example
- `examples/database_session.py` - Database persistence example  
- `examples/vertexai_session.py` - Vertex AI persistence example
- `examples/migration_script.py` - Session migration utilities

---

For more information about Google ADK SessionService implementations, see the [official ADK documentation](https://google.github.io/adk-docs/sessions/). 