import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

interface ServerStatus {
  status: string
  uptime: number
  active_sessions: number
  total_npcs: number
  version: string
}

interface SessionInfo {
  session_id: string
  created_at: string
  npc_count: number
  environment: string | { time_of_day?: string; [key: string]: any }
  status: string
  persistence?: {
    type: string
    service_type: string
    configured: boolean
  }
}

interface SessionPersistenceConfig {
  type: 'memory' | 'database' | 'vertexai'
  database_url?: string
  vertexai_project?: string
  vertexai_location?: string
  vertexai_corpus?: string
}

interface CreateSessionForm {
  session_id: string
  game_title: string
  npcs: string[]
  persistence: SessionPersistenceConfig
}

interface EventTestForm {
  session_id: string
  interaction_type: 'player_to_npc' | 'npc_to_npc'
  source_id: string // player_id or npc_id
  target_id: string // npc_id
  action: string
  action_data: string
}

interface EventResponse {
  success?: boolean
  error?: string
  debug?: any
  response?: string
  npc_response?: string
  effects?: string[]
  event_id?: string
  session_id?: string
  event_type?: string
  timestamp?: string
  responses?: Array<{
    npc_id: string
    npc_name: string
    response: string
    action_taken: string
  }>
  npc_actions?: Array<{
    npc_id: string
    npc_name: string
    success: boolean
    action_type: string
    action_properties: Record<string, any>
    reasoning: string
    message: string
  }>
  processing_complete?: boolean
}

interface SessionNPC {
  npc_id: string
  name: string
  status: any
}

interface ActionProperty {
  name: string
  type: string
  required: boolean
  description?: string
  default?: any
  validation?: {
    choices?: string[]
    min?: number
    max?: number
    min_length?: number
    max_length?: number
  }
}

interface ActionDefinition {
  action_id: string
  name: string
  description?: string
  properties: ActionProperty[]
}

const Dashboard: React.FC = () => {
  const [serverStatus, setServerStatus] = useState<ServerStatus | null>(null)
  const [sessions, setSessions] = useState<SessionInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [creating, setCreating] = useState(false)
  const [showCreateSession, setShowCreateSession] = useState(false)
  const [showEventTest, setShowEventTest] = useState(false)
  const [testingEvent, setTestingEvent] = useState(false)
  const [eventResponse, setEventResponse] = useState<EventResponse | null>(null)
  const [sessionNPCs, setSessionNPCs] = useState<SessionNPC[]>([])
  const [availableActions, setAvailableActions] = useState<{ action_id: string; name: string }[]>([])
  const [actionDefinitions, setActionDefinitions] = useState<ActionDefinition[]>([])
  const [actionData, setActionData] = useState<Record<string, any>>({})
  const [createForm, setCreateForm] = useState<CreateSessionForm>({
    session_id: '',
    game_title: '',
    npcs: [],
    persistence: {
      type: 'memory'
    }
  })
  const [eventForm, setEventForm] = useState<EventTestForm>({
    session_id: '',
    interaction_type: 'player_to_npc',
    source_id: '',
    target_id: '',
    action: 'speak',
    action_data: ''
  })

  // Helper function to format environment display
  const formatEnvironment = (environment: string | { time_of_day?: string; [key: string]: any }): string => {
    if (typeof environment === 'string') {
      return environment
    }
    if (typeof environment === 'object' && environment !== null) {
      return environment.time_of_day || 'unknown'
    }
    return 'unknown'
  }

  useEffect(() => {
    loadDashboardData()
    
    // Auto-refresh server status every 10 seconds (not full data)
    const interval = setInterval(() => {
      loadServerStatus()
    }, 10000)
    
    return () => clearInterval(interval)
  }, [])

  // Load server status separately to avoid full page refresh
  const loadServerStatus = async () => {
    try {
      const statusResponse = await axios.get(`${API_BASE}/health`)
      setServerStatus(statusResponse.data)
    } catch (statusErr) {
      console.error('Error loading server status:', statusErr)
      setServerStatus({
        status: 'offline',
        uptime: 0,
        active_sessions: 0,
        total_npcs: 0,
        version: 'unknown'
      })
    }
  }

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load server status
      await loadServerStatus()
      
      // Load sessions
      try {
        const sessionsResponse = await axios.get(`${API_BASE}/sessions`)
        setSessions(sessionsResponse.data)
      } catch (sessionsErr) {
        console.error('Error loading sessions:', sessionsErr)
        setSessions([])
      }
      
    } catch (err) {
      console.error('Error loading dashboard data:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadSessionNPCs = async (sessionId: string) => {
    if (!sessionId) {
      setSessionNPCs([])
      return
    }

    try {
      console.log(`🔍 Loading NPCs for session: ${sessionId}`)
      const response = await axios.get(`${API_BASE}/sessions/${sessionId}/npcs`)
      console.log('📡 NPCs API response:', response.data)
      
      // Convert the NPCs object to array format with proper naming
      const npcArray = Object.entries(response.data.npcs || {}).map(([id, data]: [string, any]) => ({
        npc_id: id,
        name: data.name || id, // Use name if available, fallback to ID
        status: data
      }))
      
      console.log('🎭 Converted NPC array:', npcArray)
      setSessionNPCs(npcArray)
    } catch (err) {
      console.error('❌ Error loading session NPCs:', err)
      setSessionNPCs([])
    }
  }

  const loadAvailableActions = async (interactionType: 'player_to_npc' | 'npc_to_npc' = 'player_to_npc') => {
    try {
      let response, data, allDefinitions

      if (interactionType === 'player_to_npc') {
        // Load player actions
        response = await axios.get(`${API_BASE}/config/player-actions`)
        data = response.data
        allDefinitions = data.player_actions || []
      } else {
        // Load NPC actions  
        response = await axios.get(`${API_BASE}/config/actions/definitions`)
        data = response.data
        allDefinitions = [...(data.default_action_definitions || []), ...(data.custom_actions || [])]
      }
      
      setActionDefinitions(allDefinitions)
      
      // Set available actions for dropdown
      const actions = allDefinitions.map((action: any) => ({
        action_id: action.action_id,
        name: action.name
      }))
      
      setAvailableActions(actions)
    } catch (err) {
      console.error('Error loading available actions:', err)
      // Fallback to basic actions
      setAvailableActions([
        { action_id: 'speak', name: 'Speak' },
        { action_id: 'move', name: 'Move' },
        { action_id: 'emote', name: 'Emote' },
        { action_id: 'interact', name: 'Interact' }
      ])
    }
  }

  // Load actions when component mounts or interaction type changes
  useEffect(() => {
    loadAvailableActions(eventForm.interaction_type)
  }, [eventForm.interaction_type])

  // Load NPCs when session changes
  useEffect(() => {
    console.log(`🔄 Session changed to: ${eventForm.session_id}`)
    if (eventForm.session_id) {
      loadSessionNPCs(eventForm.session_id)
    } else {
      console.log('📭 No session selected, clearing NPCs')
      setSessionNPCs([])
    }
  }, [eventForm.session_id])

  const createSession = async () => {
    if (!createForm.session_id.trim()) {
      alert('Please enter a session ID')
      return
    }

    if (!createForm.game_title.trim()) {
      alert('Please enter a game title')
      return
    }

    // Validate persistence config
    if (createForm.persistence.type === 'database' && !createForm.persistence.database_url?.trim()) {
      alert('Please enter a database URL for database persistence')
      return
    }

    if (createForm.persistence.type === 'vertexai' && !createForm.persistence.vertexai_project?.trim()) {
      alert('Please enter a GCP Project ID for Vertex AI persistence')
      return
    }

    try {
      setCreating(true)
      
      // Create session with persistence configuration - proper backend format
      const sessionConfig = {
        session_id: createForm.session_id,
        game_title: createForm.game_title,
        persistence: createForm.persistence,
        npcs: [
          {
            personality: {
              name: "Demo NPC",
              role: "villager",
              personality_traits: ["friendly", "helpful"],
              background: "A helpful NPC for testing",
              goals: ["assist players", "provide information"],
              relationships: {},
              dialogue_style: "casual"
            },
            state: {
              npc_id: "npc_demo_1",
              current_location: "village_center",
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
          }
        ],
        environment: {
          session_id: createForm.session_id,
          locations: {
            "village_center": {
              location_id: "village_center",
              name: "Village Center",
              location_type: "town",
              description: "The bustling center of the village",
              connected_locations: [],
              properties: {},
              npcs_present: ["npc_demo_1"],
              items_present: []
            }
          },
          time_of_day: "morning",
          weather: "sunny",
          game_time: 0,
          world_properties: {},
          active_events: []
        },
        available_actions: [
          {
            action_type: "speak",
            properties: [
              {
                name: "message",
                type: "string",
                required: true,
                description: "What to say",
                default_value: null,
                validation: {
                  max_length: 500
                }
              },
              {
                name: "tone",
                type: "string",
                required: false,
                description: "Tone of voice",
                default_value: "neutral",
                validation: {
                  options: ["neutral", "friendly", "angry", "excited"]
                }
              }
            ],
            description: "Makes the NPC speak",
            preconditions: [],
            examples: ["Hello there!"]
          },
          {
            action_type: "emote",
            properties: [
              {
                name: "emotion",
                type: "string",
                required: true,
                description: "Emotion to express",
                default_value: null,
                validation: {
                  options: ["happy", "sad", "angry", "excited", "curious"]
                }
              }
            ],
            description: "Makes the NPC show emotion",
            preconditions: [],
            examples: ["Show happiness"]
          }
        ],
        settings: {}
      }
      
      const response = await axios.post(`${API_BASE}/sessions`, sessionConfig)
      
      console.log('Session created:', response.data)

      // Refresh data to show new session
      await loadDashboardData()
      
      // Reset form
      setCreateForm({
        session_id: '',
        game_title: '',
        npcs: [],
        persistence: {
          type: 'memory'
        }
      })
      setShowCreateSession(false)
      
      alert('Session created successfully!')
      
    } catch (err: any) {
      console.error('Error creating session:', err)
      
      // If config-based creation fails, try the simplified creation
      try {
        const fallbackConfig = {
          session_id: createForm.session_id,
          game_title: createForm.game_title || "NPC Engine Demo",
          persistence: createForm.persistence,
          npcs: [],  // Start with no NPCs for simplicity
          environment: {
            session_id: createForm.session_id,
            locations: {},
            time_of_day: "morning",
            weather: "sunny",
            game_time: 0,
            world_properties: {},
            active_events: []
          },
          available_actions: [
            {
              action_type: "speak",
              properties: [
                {
                  name: "message",
                  type: "string",
                  required: true,
                  description: "What to say",
                  default_value: null,
                  validation: {
                    max_length: 500
                  }
                }
              ],
              description: "Makes the NPC speak",
              preconditions: [],
              examples: ["Hello there!"]
            }
          ],
          settings: {}
        }
        
        await axios.post(`${API_BASE}/sessions`, fallbackConfig)
        await loadDashboardData()
        
        setCreateForm({
          session_id: '',
          game_title: '',
          npcs: [],
          persistence: {
            type: 'memory'
          }
        })
        setShowCreateSession(false)
        
        alert('Session created successfully!')
        
      } catch (fallbackErr: any) {
        console.error('Fallback session creation failed:', fallbackErr)
        let errorMessage = 'Failed to create session'
        
        if (fallbackErr.response?.data?.detail) {
          if (Array.isArray(fallbackErr.response.data.detail)) {
            errorMessage = `Validation errors: ${fallbackErr.response.data.detail.map((e: any) => e.msg || e).join(', ')}`
          } else {
            errorMessage = String(fallbackErr.response.data.detail)
          }
        } else if (err.response?.data?.detail) {
          if (Array.isArray(err.response.data.detail)) {
            errorMessage = `Validation errors: ${err.response.data.detail.map((e: any) => e.msg || e).join(', ')}`
          } else {
            errorMessage = String(err.response.data.detail)
          }
        } else if (fallbackErr.message) {
          errorMessage = String(fallbackErr.message)
        } else if (err.message) {
          errorMessage = String(err.message)
        }
        
        alert(errorMessage)
      }
    } finally {
      setCreating(false)
    }
  }

  const deleteSession = async (sessionId: string) => {
    if (!confirm(`Are you sure you want to delete session "${sessionId}"?`)) return

    try {
      await axios.delete(`${API_BASE}/sessions/${sessionId}`)
      await loadDashboardData()
      alert('Session deleted successfully!')
    } catch (err: any) {
      console.error('Error deleting session:', err)
      alert(err.response?.data?.detail || 'Failed to delete session')
    }
  }

  const generateSessionId = () => {
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[-:]/g, '').replace('T', '_')
    setCreateForm({ ...createForm, session_id: `session_${timestamp}` })
  }

  const handleActionChange = (actionId: string) => {
    setEventForm({ ...eventForm, action: actionId })
    // Reset action data when action changes
    setActionData({})
  }

  const handleActionDataChange = (propertyName: string, value: any) => {
    setActionData(prev => ({
      ...prev,
      [propertyName]: value
    }))
  }

  const getSelectedActionDefinition = (): ActionDefinition | null => {
    return actionDefinitions.find(action => action.action_id === eventForm.action) || null
  }

  const renderActionPropertyInput = (property: ActionProperty) => {
    const value = actionData[property.name] ?? property.default ?? ''

    switch (property.type) {
      case 'boolean':
        return (
          <div key={property.name} className="space-y-2">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={value === true}
                onChange={(e) => handleActionDataChange(property.name, e.target.checked)}
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                {property.name} {property.required && <span className="text-red-500">*</span>}
              </span>
            </label>
            {property.description && (
              <p className="text-xs text-gray-500 dark:text-gray-400">{property.description}</p>
            )}
          </div>
        )

      case 'integer':
        return (
          <div key={property.name} className="space-y-2">
            <label className="block text-sm font-medium text-gray-900 dark:text-gray-100">
              {property.name} {property.required && <span className="text-red-500">*</span>}
            </label>
            <input
              type="number"
              value={value}
              onChange={(e) => handleActionDataChange(property.name, parseInt(e.target.value) || 0)}
              min={property.validation?.min}
              max={property.validation?.max}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
              required={property.required}
            />
            {property.description && (
              <p className="text-xs text-gray-500 dark:text-gray-400">{property.description}</p>
            )}
          </div>
        )

      case 'float':
        return (
          <div key={property.name} className="space-y-2">
            <label className="block text-sm font-medium text-gray-900 dark:text-gray-100">
              {property.name} {property.required && <span className="text-red-500">*</span>}
            </label>
            <input
              type="number"
              step="0.1"
              value={value}
              onChange={(e) => handleActionDataChange(property.name, parseFloat(e.target.value) || 0)}
              min={property.validation?.min}
              max={property.validation?.max}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
              required={property.required}
            />
            {property.description && (
              <p className="text-xs text-gray-500 dark:text-gray-400">{property.description}</p>
            )}
          </div>
        )

      case 'string':
      default:
        if (property.validation?.choices) {
          // Dropdown for string choices
          return (
            <div key={property.name} className="space-y-2">
              <label className="block text-sm font-medium text-gray-900 dark:text-gray-100">
                {property.name} {property.required && <span className="text-red-500">*</span>}
              </label>
              <select
                value={value}
                onChange={(e) => handleActionDataChange(property.name, e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                required={property.required}
              >
                <option value="">Select {property.name}</option>
                {property.validation.choices.map(choice => (
                  <option key={choice} value={choice}>{choice}</option>
                ))}
              </select>
              {property.description && (
                <p className="text-xs text-gray-500 dark:text-gray-400">{property.description}</p>
              )}
            </div>
          )
        } else {
          // Text input for regular strings
          return (
            <div key={property.name} className="space-y-2">
              <label className="block text-sm font-medium text-gray-900 dark:text-gray-100">
                {property.name} {property.required && <span className="text-red-500">*</span>}
              </label>
              <input
                type="text"
                value={value}
                onChange={(e) => handleActionDataChange(property.name, e.target.value)}
                minLength={property.validation?.min_length}
                maxLength={property.validation?.max_length}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                required={property.required}
                placeholder={property.description}
              />
              {property.description && (
                <p className="text-xs text-gray-500 dark:text-gray-400">{property.description}</p>
              )}
            </div>
          )
        }
    }
  }

  const generateEvent = async () => {
    if (!eventForm.session_id || !eventForm.action) {
      alert('Please select a session and action')
      return
    }

    // Validate required properties
    const actionDef = getSelectedActionDefinition()
    if (actionDef) {
      const missingRequired = actionDef.properties
        .filter(prop => prop.required && !actionData[prop.name])
        .map(prop => prop.name)
      
      if (missingRequired.length > 0) {
        alert(`Please fill in required fields: ${missingRequired.join(', ')}`)
        return
      }
    }

    setTestingEvent(true)
    setEventResponse(null)

    try {
      console.log('🎮 Generating event with data:', {
        session_id: eventForm.session_id,
        action: eventForm.action,
        action_data: actionData,
        source_id: eventForm.source_id,
        target_id: eventForm.target_id
      })

      const eventData = {
        event_type: eventForm.source_id && eventForm.target_id ? 'npc_to_npc' : 'player_to_npc',
        action: eventForm.action,
        action_data: actionData, // Use the structured action data instead of raw JSON
        source_id: eventForm.source_id || 'player',
        target_id: eventForm.target_id || eventForm.source_id,
        description: `${eventForm.action} action with properties: ${Object.keys(actionData).map(k => `${k}=${actionData[k]}`).join(', ')}`
      }

      const response = await axios.post(`${API_BASE}/sessions/${eventForm.session_id}/events/test`, eventData)
      
      console.log('✅ Event generated successfully:', response.data)
      setEventResponse(response.data)
    } catch (error: any) {
      console.error('❌ Error generating event:', error)
      setEventResponse({
        success: false,
        error: error.response?.data?.detail || error.message || 'Failed to generate event',
        debug: {
          status: error.response?.status,
          data: error.response?.data
        }
      })
    } finally {
      setTestingEvent(false)
    }
  }

  if (loading && !serverStatus) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <span className="ml-3 text-lg font-medium text-slate-600 dark:text-slate-400">Loading dashboard...</span>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-8 animate-fade-in">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gradient">NPC Engine Dashboard</h1>
        <p className="text-lg text-slate-600 dark:text-slate-400">
          AI-Powered Agent Framework with Google ADK
        </p>
      </div>

      {/* Server Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card bg-gradient-to-br from-emerald-500 to-emerald-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-emerald-100 text-sm font-medium">Server Status</p>
              <p className="text-2xl font-bold">{serverStatus?.status || 'Unknown'}</p>
            </div>
            <div className="p-3 bg-white/20 rounded-full">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">Active Sessions</p>
              <p className="text-2xl font-bold">{serverStatus?.active_sessions || 0}</p>
            </div>
            <div className="p-3 bg-white/20 rounded-full">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium">Total NPCs</p>
              <p className="text-2xl font-bold">{serverStatus?.total_npcs || 0}</p>
            </div>
            <div className="p-3 bg-white/20 rounded-full">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-amber-500 to-amber-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-amber-100 text-sm font-medium">Uptime</p>
              <p className="text-2xl font-bold">
                {serverStatus?.uptime ? Math.floor(serverStatus.uptime / 3600) : 0}h
              </p>
            </div>
            <div className="p-3 bg-white/20 rounded-full">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-200">Quick Actions</h2>
          <button
            onClick={() => setShowCreateSession(true)}
            className="btn-primary flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>Create Session</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => window.location.href = '#actions'}
            className="p-4 text-left bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 rounded-lg border border-primary-200 dark:border-primary-700 hover:shadow-lg transition-all duration-200 hover:scale-105"
          >
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-500 text-white rounded-lg">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-slate-800 dark:text-slate-200">Configure Actions</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400">Add custom action properties</p>
              </div>
            </div>
          </button>

          <button
            onClick={() => window.location.href = '#npcs'}
            className="p-4 text-left bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg border border-purple-200 dark:border-purple-700 hover:shadow-lg transition-all duration-200 hover:scale-105"
          >
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-500 text-white rounded-lg">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-slate-800 dark:text-slate-200">Manage NPCs</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400">Create schemas and NPCs</p>
              </div>
            </div>
          </button>

          <button
            onClick={() => window.location.href = '#environment'}
            className="p-4 text-left bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-900/20 dark:to-emerald-800/20 rounded-lg border border-emerald-200 dark:border-emerald-700 hover:shadow-lg transition-all duration-200 hover:scale-105"
          >
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-emerald-500 text-white rounded-lg">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-slate-800 dark:text-slate-200">World Builder</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400">Design environments</p>
              </div>
            </div>
          </button>
        </div>
      </div>

      {/* Event Testing */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200">Event Testing</h2>
          <button
            onClick={() => setShowEventTest(!showEventTest)}
            className="btn-secondary flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span>{showEventTest ? 'Hide' : 'Test Events'}</span>
          </button>
        </div>

        {showEventTest && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Select Session
                </label>
                <select
                  value={eventForm.session_id}
                  onChange={(e) => setEventForm({...eventForm, session_id: e.target.value})}
                  className="w-full"
                >
                  <option value="">Choose a session...</option>
                  {sessions.map(session => (
                    <option key={session.session_id} value={session.session_id}>
                      {session.session_id} ({session.npc_count} NPCs)
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Interaction Type
                </label>
                <select
                  value={eventForm.interaction_type}
                  onChange={(e) => {
                    const newType = e.target.value as 'player_to_npc' | 'npc_to_npc'
                    setEventForm({
                      ...eventForm, 
                      interaction_type: newType,
                      action: '' // Reset action when type changes
                    })
                    setActionData({}) // Reset action data
                  }}
                  className="w-full"
                >
                  <option value="player_to_npc">👤 Player → NPC (Player Actions)</option>
                  <option value="npc_to_npc">🤖 NPC → NPC (NPC Actions)</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {eventForm.interaction_type === 'player_to_npc' ? 'Player ID' : 'Source NPC'}
                </label>
                {eventForm.interaction_type === 'player_to_npc' ? (
                  <input
                    type="text"
                    value={eventForm.source_id}
                    onChange={(e) => setEventForm({...eventForm, source_id: e.target.value})}
                    placeholder="player_1"
                    className="w-full"
                  />
                ) : (
                  <select
                    value={eventForm.source_id}
                    onChange={(e) => setEventForm({...eventForm, source_id: e.target.value})}
                    className="w-full"
                  >
                    <option value="">Choose source NPC...</option>
                    {sessionNPCs.map(npc => (
                      <option key={npc.npc_id} value={npc.npc_id}>
                        {npc.name} ({npc.npc_id})
                      </option>
                    ))}
                  </select>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Target NPC
                </label>
                <select
                  value={eventForm.target_id}
                  onChange={(e) => setEventForm({...eventForm, target_id: e.target.value})}
                  className="w-full"
                >
                  <option value="">Choose target NPC...</option>
                  {sessionNPCs.map(npc => (
                    <option key={npc.npc_id} value={npc.npc_id}>
                      {npc.name} ({npc.npc_id})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Action
                </label>
                <select
                  value={eventForm.action}
                  onChange={(e) => handleActionChange(e.target.value)}
                  className="w-full"
                >
                  <option value="">Choose an action...</option>
                  {availableActions.map(action => (
                    <option key={action.action_id} value={action.action_id}>
                      {action.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  &nbsp;
                </label>
                <button
                  onClick={generateEvent}
                                     disabled={testingEvent || !eventForm.session_id || !eventForm.action}
                  className="w-full btn-primary disabled:opacity-50"
                >
                  {testingEvent ? 'Testing...' : 'Send Interaction'}
                </button>
              </div>
            </div>

            {/* Dynamic Action Properties Form */}
            {eventForm.action && getSelectedActionDefinition() && (
              <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  {getSelectedActionDefinition()?.name} Properties
                </h3>
                {getSelectedActionDefinition()?.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    {getSelectedActionDefinition()?.description}
                  </p>
                )}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {getSelectedActionDefinition()?.properties.map(property => 
                    renderActionPropertyInput(property)
                  )}
                </div>
              </div>
            )}

            {/* Event Response */}
            {eventResponse && (
              <div className="mt-6 p-4 rounded-lg border">
                {eventResponse.success ? (
                  <div className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
                    <h4 className="text-lg font-semibold text-green-800 dark:text-green-200 mb-2">✅ Event Generated Successfully</h4>
                    <div className="text-green-700 dark:text-green-300">
                      <p><strong>Response:</strong> {eventResponse.response}</p>
                      {eventResponse.npc_response && (
                        <p className="mt-2"><strong>NPC Response:</strong> {eventResponse.npc_response}</p>
                      )}
                      
                      {/* Detailed NPC Actions */}
                      {eventResponse.npc_actions && eventResponse.npc_actions.length > 0 && (
                        <div className="mt-4">
                          <strong className="text-green-800 dark:text-green-200">NPC Actions Triggered:</strong>
                          <div className="mt-2 space-y-3">
                            {eventResponse.npc_actions.map((action: any, index: number) => (
                              <div key={index} className="bg-white dark:bg-gray-800 p-3 rounded border border-green-200 dark:border-green-700">
                                <div className="flex items-center justify-between mb-2">
                                  <span className="font-medium text-gray-800 dark:text-gray-200">
                                    {action.npc_name} ({action.npc_id})
                                  </span>
                                  <span className={`text-xs px-2 py-1 rounded ${
                                    action.success 
                                      ? 'bg-green-100 text-green-800' 
                                      : 'bg-red-100 text-red-800'
                                  }`}>
                                    {action.success ? 'Success' : 'Failed'}
                                  </span>
                                </div>
                                
                                <div className="text-sm space-y-1">
                                  <div>
                                    <strong>Action:</strong> 
                                    <span className="ml-1 bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                                      {action.action_type}
                                    </span>
                                  </div>
                                  
                                  {action.action_properties && Object.keys(action.action_properties).length > 0 && (
                                    <div>
                                      <strong>Properties:</strong>
                                      <div className="ml-4 mt-1">
                                        {Object.entries(action.action_properties).map(([key, value]) => (
                                          <div key={key} className="text-xs">
                                            <span className="font-medium">{key}:</span> {String(value)}
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                  
                                  {action.reasoning && (
                                    <div>
                                      <strong>Reasoning:</strong> 
                                      <span className="ml-1 italic">{action.reasoning}</span>
                                    </div>
                                  )}
                                  
                                  {action.message && (
                                    <div>
                                      <strong>Result:</strong> 
                                      <span className="ml-1">{action.message}</span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {eventResponse.effects && eventResponse.effects.length > 0 && (
                        <div className="mt-2">
                          <strong>Effects:</strong>
                          <ul className="list-disc list-inside ml-4">
                            {eventResponse.effects.map((effect: string, index: number) => (
                              <li key={index}>{effect}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {eventResponse.processing_complete === false && (
                        <div className="mt-2 p-2 bg-yellow-100 dark:bg-yellow-900/20 border border-yellow-300 dark:border-yellow-700 rounded">
                          <p className="text-yellow-800 dark:text-yellow-200 text-sm">
                            ⏳ Background processing in progress - some NPC responses may still be pending
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
                    <h4 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">❌ Event Generation Failed</h4>
                    <p className="text-red-700 dark:text-red-300">{eventResponse.error}</p>
                    
                    {eventResponse.debug && (
                      <details className="mt-2">
                        <summary className="cursor-pointer text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200">
                          🔍 Debug Information
                        </summary>
                        <pre className="mt-2 p-2 bg-red-100 dark:bg-red-900/40 rounded text-xs text-red-800 dark:text-red-200 overflow-auto">
                          {JSON.stringify(eventResponse.debug, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Active Sessions */}
      <div className="glass-card p-6">
        <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-200 mb-6">Active Sessions</h2>
        
        {sessions.length === 0 ? (
          <div className="text-center py-12">
            <svg className="w-16 h-16 mx-auto text-slate-400 dark:text-slate-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h3 className="text-lg font-medium text-slate-600 dark:text-slate-400 mb-2">No Active Sessions</h3>
            <p className="text-slate-500 dark:text-slate-500 mb-4">Create your first session to get started</p>
            <button
              onClick={() => setShowCreateSession(true)}
              className="btn-primary"
            >
              Create Session
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sessions.map((session) => (
              <div key={session.session_id} className="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-slate-800 dark:text-slate-200 truncate">
                    {session.session_id}
                  </h3>
                  <span className={`badge ${session.status === 'active' ? 'badge-success' : 'badge-warning'}`}>
                    {session.status}
                  </span>
                </div>
                
                <div className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                  <div className="flex justify-between">
                    <span>NPCs:</span>
                    <span className="font-medium">{session.npc_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Environment:</span>
                    <span className="font-medium truncate ml-2">{formatEnvironment(session.environment)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Persistence:</span>
                    <span className="font-medium flex items-center space-x-1">
                      {session.persistence?.type === 'memory' && <span>💾</span>}
                      {session.persistence?.type === 'database' && <span>🗄️</span>}
                      {session.persistence?.type === 'vertexai' && <span>☁️</span>}
                      <span className="capitalize">{session.persistence?.type || 'memory'}</span>
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Created:</span>
                    <span className="font-medium">{new Date(session.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                
                <div className="flex space-x-2 mt-4">
                  <button
                    onClick={() => window.location.href = `#sessions?session=${session.session_id}`}
                    className="flex-1 btn-secondary text-sm py-2"
                  >
                    Manage
                  </button>
                  <button
                    onClick={() => deleteSession(session.session_id)}
                    className="btn-danger text-sm py-2 px-3"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Session Modal */}
      {showCreateSession && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="glass-card max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6 animate-slide-up">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-slate-800 dark:text-slate-200">Create New Session</h3>
              <button
                onClick={() => setShowCreateSession(false)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Session ID
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={createForm.session_id}
                      onChange={(e) => setCreateForm({ ...createForm, session_id: e.target.value })}
                      placeholder="Enter session ID"
                      className="input-field flex-1"
                    />
                    <button
                      onClick={generateSessionId}
                      className="btn-secondary px-3 py-2 text-sm"
                    >
                      Generate
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Game Title
                  </label>
                  <input
                    type="text"
                    value={createForm.game_title}
                    onChange={(e) => setCreateForm({ ...createForm, game_title: e.target.value })}
                    placeholder="Enter game title"
                    className="input-field"
                  />
                </div>
              </div>

              {/* Session Persistence Configuration */}
              <div>
                <label className="block text-sm font-medium mb-3 text-slate-700 dark:text-slate-300">
                  📦 Session Persistence
                </label>
                <div className="space-y-4">
                  {/* Persistence Type Selection */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {[
                      {
                        type: 'memory' as const,
                        label: 'In-Memory',
                        description: 'Fast, no setup required',
                        warning: 'Lost on restart',
                        icon: '💾',
                        pros: ['Fast performance', 'No configuration'],
                        cons: ['Data lost on restart', 'Not scalable']
                      },
                      {
                        type: 'database' as const,
                        label: 'Database',
                        description: 'Persistent SQL storage',
                        warning: 'Requires database setup',
                        icon: '🗄️',
                        pros: ['Persistent storage', 'Scalable', 'Query capabilities'],
                        cons: ['Requires database setup', 'Additional complexity']
                      },
                      {
                        type: 'vertexai' as const,
                        label: 'Vertex AI',
                        description: 'Google Cloud integration',
                        warning: 'Requires GCP setup',
                        icon: '☁️',
                        pros: ['Cloud-native', 'Auto-scaling', 'Integrated with AI services'],
                        cons: ['Requires GCP account', 'Higher cost for large volumes']
                      }
                    ].map(option => (
                      <div
                        key={option.type}
                        className={`relative p-4 rounded-lg border cursor-pointer transition-all ${
                          createForm.persistence.type === option.type
                            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 ring-2 ring-blue-200 dark:ring-blue-800'
                            : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                        }`}
                        onClick={() => setCreateForm({ 
                          ...createForm, 
                          persistence: { 
                            type: option.type,
                            // Reset other fields when changing type
                            ...(option.type === 'database' && { database_url: '' }),
                            ...(option.type === 'vertexai' && { 
                              vertexai_project: '', 
                              vertexai_location: 'us-central1',
                              vertexai_corpus: ''
                            })
                          }
                        })}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <span className="text-xl">{option.icon}</span>
                            <span className="font-medium text-gray-800 dark:text-gray-200">
                              {option.label}
                            </span>
                          </div>
                          {createForm.persistence.type === option.type && (
                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          {option.description}
                        </p>
                        <div className="text-xs space-y-1">
                          <div className="text-green-600 dark:text-green-400">
                            ✓ {option.pros.join(', ')}
                          </div>
                          <div className="text-orange-600 dark:text-orange-400">
                            ⚠ {option.cons.join(', ')}
                          </div>
                        </div>
                        {option.warning && (
                          <div className="mt-2 text-xs text-amber-600 dark:text-amber-400 font-medium">
                            ⚠️ {option.warning}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Database Configuration */}
                  {createForm.persistence.type === 'database' && (
                    <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg space-y-3">
                      <h4 className="font-medium text-gray-800 dark:text-gray-200">Database Configuration</h4>
                      <div>
                        <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                          Database URL
                        </label>
                        <input
                          type="text"
                          value={createForm.persistence.database_url || ''}
                          onChange={(e) => setCreateForm({
                            ...createForm,
                            persistence: { ...createForm.persistence, database_url: e.target.value }
                          })}
                          className="input-field"
                          placeholder="postgresql://user:password@localhost:5432/npc_engine"
                        />
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          Supports PostgreSQL, MySQL, SQLite. Format: dialect://user:password@host:port/database
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Vertex AI Configuration */}
                  {createForm.persistence.type === 'vertexai' && (
                    <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg space-y-3">
                      <h4 className="font-medium text-gray-800 dark:text-gray-200">Vertex AI Configuration</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                            GCP Project ID
                          </label>
                          <input
                            type="text"
                            value={createForm.persistence.vertexai_project || ''}
                            onChange={(e) => setCreateForm({
                              ...createForm,
                              persistence: { ...createForm.persistence, vertexai_project: e.target.value }
                            })}
                            className="input-field"
                            placeholder="your-gcp-project-id"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                            Location
                          </label>
                          <select
                            value={createForm.persistence.vertexai_location || 'us-central1'}
                            onChange={(e) => setCreateForm({
                              ...createForm,
                              persistence: { ...createForm.persistence, vertexai_location: e.target.value }
                            })}
                            className="input-field"
                          >
                            <option value="us-central1">us-central1</option>
                            <option value="us-east1">us-east1</option>
                            <option value="us-west1">us-west1</option>
                            <option value="europe-west1">europe-west1</option>
                            <option value="asia-east1">asia-east1</option>
                          </select>
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                          RAG Corpus ID (Optional)
                        </label>
                        <input
                          type="text"
                          value={createForm.persistence.vertexai_corpus || ''}
                          onChange={(e) => setCreateForm({
                            ...createForm,
                            persistence: { ...createForm.persistence, vertexai_corpus: e.target.value }
                          })}
                          className="input-field"
                          placeholder="your-corpus-id"
                        />
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          Optional: If specified, will use Vertex AI RAG for enhanced memory capabilities
                        </p>
                      </div>
                      <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded border border-blue-200 dark:border-blue-800">
                        <p className="text-sm text-blue-700 dark:text-blue-300">
                          💡 <strong>Setup Required:</strong> Ensure your environment has:
                        </p>
                        <ul className="text-xs text-blue-600 dark:text-blue-400 mt-1 ml-4 list-disc">
                          <li>Google Cloud SDK installed and authenticated</li>
                          <li>Vertex AI API enabled in your project</li>
                          <li>Appropriate IAM permissions for Vertex AI</li>
                        </ul>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="glass-card p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">🌍 Environment Configuration</h4>
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  All sessions use the same environment. Customize it using <strong>Custom Properties</strong> in the Environment tab after session creation.
                </p>
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowCreateSession(false)}
                className="flex-1 btn-secondary"
                disabled={creating}
              >
                Cancel
              </button>
              <button
                onClick={createSession}
                className="flex-1 btn-primary"
                disabled={creating || !createForm.session_id || !createForm.game_title}
              >
                {creating ? 'Creating...' : 'Create Session'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard 