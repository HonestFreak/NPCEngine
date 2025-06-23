# Session Creation 422 Error Fix

## Issue
The frontend was receiving a 422 Unprocessable Entity error when making POST requests to `/sessions`.

## Root Cause
The frontend was sending data in a format that didn't match the backend's `SessionConfig` Pydantic model expectations:

### Frontend Was Sending:
```typescript
{
  session_id: string,
  game_title: string,
  npcs: NPCTemplate[],        // Wrong structure
  environment: {...},         // Wrong structure  
  available_actions: [...],   // Wrong structure
  persistence: {...}
}
```

### Backend Expected (SessionConfig):
```python
{
  session_id: str,
  game_title: str,
  persistence: SessionPersistenceConfig,
  npcs: List[NPCData],        # Needs personality, state, memory
  environment: Environment,   # Needs proper structure with locations dict
  available_actions: List[ActionDefinition],  # Needs proper ActionDefinition structure
  settings: Dict[str, Any]
}
```

## Fix Applied

### 1. NPCData Structure
Updated frontend to convert `NPCTemplate` to proper `NPCData` format:
```typescript
const npcs = allNPCs.map(npc => ({
  personality: {
    name: npc.name,
    role: npc.role,
    personality_traits: npc.personality_traits,
    background: npc.background,
    goals: ["help visitors", "live peacefully"],
    relationships: {},
    dialogue_style: "friendly"
  },
  state: {
    npc_id: npc.npc_id,
    current_location: npc.location,
    current_activity: "idle",
    mood: "neutral",
    health: 100.0,
    energy: 100.0,
    inventory: [],
    status_effects: [],
    custom_attributes: {}
  },
  memory: {
    short_term: [],
    long_term: [],
    relationships_memory: {}
  }
}))
```

### 2. Environment Structure
Updated to match backend `Environment` model:
```typescript
const environment = {
  session_id: createForm.session_id,
  locations: {
    "village_center": {
      location_id: "village_center",
      name: "Village Center", 
      location_type: "town",
      description: "The bustling center of the village where people gather",
      connected_locations: [],
      properties: {},
      npcs_present: npcs.map(npc => npc.state.npc_id),
      items_present: []
    }
  },
  time_of_day: "morning",
  weather: "sunny",
  game_time: 0,
  world_properties: {},
  active_events: []
}
```

### 3. ActionDefinition Structure  
Updated to match backend `ActionDefinition` model:
```typescript
const availableActions = actionDefinitions.map(action => ({
  action_type: action.action_id,
  properties: action.properties.map(prop => ({
    name: prop.name,
    type: prop.type,
    required: prop.required,
    description: prop.description || "",
    default_value: prop.default,
    validation: prop.validation || {}
  })),
  description: action.description || "",
  preconditions: [],
  examples: []
}))
```

### 4. Complete SessionConfig
Final structure sent to backend:
```typescript
const sessionConfig = {
  session_id: createForm.session_id,
  game_title: createForm.game_title,
  persistence: createForm.persistence,
  npcs: npcs,
  environment: environment,
  available_actions: availableActions,
  settings: {}
}
```

## Validation Results
- ✅ Empty session creation: Status 200 
- ✅ Session with NPCs: Status 200
- ✅ Frontend build: No TypeScript errors
- ✅ Backend validation: Accepts new format

## Key Lessons
1. Always validate frontend data structures against backend Pydantic models
2. 422 errors typically indicate schema/validation mismatches
3. Use tools like `curl` or Python `requests` to test API endpoints directly
4. Ensure TypeScript interfaces match backend model expectations

## Files Modified
- `web-gui/src/components/Dashboard.tsx` - Fixed `createSession()` function
- Added proper data structure conversion for all SessionConfig fields
- Removed unused TypeScript variables

The fix ensures the frontend sends data in the exact format expected by the backend's Pydantic validation, resolving the 422 Unprocessable Entity error. 