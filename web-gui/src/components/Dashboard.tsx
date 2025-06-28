import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'

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

interface NPCTemplate {
  npc_id: string
  name: string
  role: string
  personality_traits: string[]
  background: string
  location: string
}

interface CreateSessionForm {
  session_id: string
  game_title: string
  npcs: NPCTemplate[]
  selectedGlobalNPCs: string[]
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
    selectedGlobalNPCs: [],
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

  const [globalNPCs, setGlobalNPCs] = useState<any[]>([])

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

  const loadGlobalNPCs = async () => {
    try {
      console.log('🌐 Loading global NPCs...')
      const response = await axios.get(`${API_BASE}/config/npcs/instances`)
      console.log('📦 Global NPCs loaded:', response.data)
      setGlobalNPCs(response.data || [])
    } catch (err) {
      console.error('Error loading global NPCs:', err)
      setGlobalNPCs([])
    }
  }

  useEffect(() => {
    loadServerStatus()
    loadDashboardData()
    loadAvailableActions()
    loadGlobalNPCs() // Load global NPCs on component mount
  }, [])

  const createSession = async () => {
    if (!createForm.session_id || !createForm.game_title) {
      alert('Please fill in Session ID and Game Title')
      return
    }

    setCreating(true)
    try {
      console.log('🚀 Creating session with form data:', createForm)

      // Combine manually created NPCs with selected global NPCs
      let allNPCs = [...createForm.npcs]
      
      // Convert selected global NPCs to NPCTemplate format
      const selectedGlobalNPCObjects = globalNPCs.filter(npc => 
        createForm.selectedGlobalNPCs.includes(npc.id)
      )
      
      for (const globalNPC of selectedGlobalNPCObjects) {
        const npcTemplate: NPCTemplate = {
          npc_id: globalNPC.id,
          name: globalNPC.name,
          role: globalNPC.properties?.job || 'villager',
          personality_traits: Array.isArray(globalNPC.properties?.personality_traits) 
            ? globalNPC.properties.personality_traits 
            : typeof globalNPC.properties?.personality_traits === 'string'
            ? globalNPC.properties.personality_traits.split(', ')
            : ['friendly'],
          background: globalNPC.description || '',
          location: globalNPC.properties?.location || 'village_center'
        }
        allNPCs.push(npcTemplate)
      }
      
      // Sessions can be created without NPCs (will be added later)
      if (allNPCs.length === 0) {
        console.log('Creating session without NPCs - they can be added later')
      }

      // Convert NPCTemplate to NPCData format expected by backend
      const npcs = allNPCs.map(npc => ({
        personality: {
          name: npc.name,
          role: npc.role,
          personality_traits: npc.personality_traits,
          background: npc.background,
          goals: ["help visitors", "live peacefully"], // Default goals
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

      // Create proper Environment structure
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

      // Get available actions with proper ActionDefinition structure
      // Filter to only use valid action types that the backend accepts
      const validActionTypes = ['speak', 'move', 'interact', 'attack', 'use_item', 'give_item', 'take_item', 'emote', 'wait', 'follow', 'trade', 'flee', 'investigate', 'work', 'rest', 'remember_event', 'custom']
      
      const availableActions = actionDefinitions.length > 0 ? actionDefinitions
        .filter(action => validActionTypes.includes(action.action_id))
        .map(action => ({
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
        })) : [
        {
          action_type: "speak",
          description: "Speak to someone",
          properties: [
            {
              name: "message",
              type: "string",
              required: true,
              description: "What to say",
              default_value: "",
              validation: {}
            },
            {
              name: "tone",
              type: "string",
              required: false,
              description: "Tone of voice",
              default_value: "neutral",
              validation: {}
            }
          ],
          preconditions: [],
          examples: []
        },
        {
          action_type: "move",
          description: "Move to a location",
          properties: [
            {
              name: "destination",
              type: "string",
              required: true,
              description: "Where to move",
              default_value: "",
              validation: {}
            }
          ],
          preconditions: [],
          examples: []
        },
        {
          action_type: "emote",
          description: "Express emotion",
          properties: [
            {
              name: "emotion",
              type: "string",
              required: true,
              description: "Type of emotion",
              default_value: "",
              validation: {}
            },
            {
              name: "intensity",
              type: "integer",
              required: false,
              description: "Intensity level 1-10",
              default_value: 5,
              validation: {}
            }
          ],
          preconditions: [],
          examples: []
        }
      ]

      const sessionConfig = {
        session_id: createForm.session_id,
        game_title: createForm.game_title,
        persistence: createForm.persistence,
        npcs: npcs,
        environment: environment,
        available_actions: availableActions,
        settings: {}
      }

      console.log('📋 Final session config:', JSON.stringify(sessionConfig, null, 2))

      const response = await axios.post(`${API_BASE}/sessions`, sessionConfig)
      console.log('✅ Session created successfully:', response.data)
      
      alert('Session created successfully!')
      setShowCreateSession(false)
      setCreateForm({
        session_id: '',
        game_title: '',
        npcs: [],
        selectedGlobalNPCs: [], // Reset selected global NPCs
        persistence: { type: 'memory' }
      })
      loadDashboardData()
    } catch (error: any) {
      console.error('❌ Error creating session:', error)
      
      let errorMessage = 'Unknown error'
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail
        if (Array.isArray(detail)) {
          // Handle validation errors (422)
          const validationErrors = detail.map(err => {
            const field = err.loc ? err.loc.join('.') : 'unknown field'
            return `${field}: ${err.msg}`
          }).join('\n')
          errorMessage = `Validation errors:\n${validationErrors}`
        } else if (typeof detail === 'string') {
          // Handle string error messages
          errorMessage = detail
        } else {
          errorMessage = JSON.stringify(detail)
        }
      } else {
        errorMessage = error.message || 'Unknown error'
      }
      
      alert(`Failed to create session:\n${errorMessage}`)
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
            onClick={() => {
              setShowCreateSession(true)
              loadGlobalNPCs() // Refresh global NPCs when opening form
            }}
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
                onClick={() => {
                  setShowCreateSession(true)
                  loadGlobalNPCs() // Refresh global NPCs when opening form
                }}
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

              {/* NPC Configuration */}
              <div>
                <label className="block text-sm font-medium mb-3 text-slate-700 dark:text-slate-300">
                  🎭 NPCs Configuration
                </label>
                <div className="space-y-4">
                  {/* Global NPCs Selection */}
                  {globalNPCs.length > 0 && (
                    <div className="border border-blue-200 dark:border-blue-800 rounded-lg p-4 bg-blue-50 dark:bg-blue-900/20">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-medium text-blue-800 dark:text-blue-200 flex items-center">
                          🌐 Global NPCs
                          <span className="ml-2 text-sm font-normal text-blue-600 dark:text-blue-300">
                            ({globalNPCs.length} available)
                          </span>
                        </h4>
                        <div className="flex gap-2">
                          <button
                            type="button"
                            onClick={() => {
                              const allNPCIds = globalNPCs.map(npc => npc.id)
                              setCreateForm({ ...createForm, selectedGlobalNPCs: allNPCIds })
                            }}
                            className="text-xs btn-secondary py-1 px-2"
                          >
                            Select All
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              setCreateForm({ ...createForm, selectedGlobalNPCs: [] })
                            }}
                            className="text-xs btn-secondary py-1 px-2"
                          >
                            Clear All
                          </button>
                        </div>
                      </div>
                      <p className="text-sm text-blue-700 dark:text-blue-300 mb-3">
                        Select NPCs from your global collection to include in this session. These NPCs were created in the NPC Manager.
                      </p>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-48 overflow-y-auto">
                        {globalNPCs.map((npc) => {
                          const npcId = npc.id
                          const isSelected = createForm.selectedGlobalNPCs.includes(npcId)
                          return (
                            <div
                              key={npcId}
                              className={`p-3 rounded border cursor-pointer transition-all ${
                                isSelected
                                  ? 'border-blue-500 bg-blue-100 dark:bg-blue-800/30'
                                  : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                              }`}
                              onClick={() => {
                                const newSelected = isSelected
                                  ? createForm.selectedGlobalNPCs.filter(id => id !== npcId)
                                  : [...createForm.selectedGlobalNPCs, npcId]
                                setCreateForm({ ...createForm, selectedGlobalNPCs: newSelected })
                              }}
                            >
                              <div className="flex items-center justify-between mb-1">
                                <span className="font-medium text-sm text-gray-800 dark:text-gray-200">
                                  {npc.name}
                                </span>
                                {isSelected && (
                                  <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                  </svg>
                                )}
                              </div>
                              <div className="text-xs text-gray-600 dark:text-gray-400">
                                <div>ID: {npcId}</div>
                                <div>Role: {npc.properties?.job || 'Unknown'}</div>
                                <div>Location: {npc.properties?.location || 'Unknown'}</div>
                              </div>
                              {npc.description && (
                                <div className="text-xs text-gray-500 dark:text-gray-500 mt-1 line-clamp-2">
                                  {npc.description}
                                </div>
                              )}
                            </div>
                          )
                        })}
                      </div>
                      {createForm.selectedGlobalNPCs.length > 0 && (
                        <div className="mt-3 p-2 bg-blue-100 dark:bg-blue-800/20 rounded text-sm text-blue-800 dark:text-blue-200">
                          ✅ {createForm.selectedGlobalNPCs.length} global NPC{createForm.selectedGlobalNPCs.length !== 1 ? 's' : ''} selected
                        </div>
                      )}
                    </div>
                  )}

                  {/* Manual NPC Creation */}
                  <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-3 flex items-center">
                      ➕ Create New NPCs
                      <span className="ml-2 text-sm font-normal text-gray-600 dark:text-gray-400">
                        (Optional - add custom NPCs for this session)
                      </span>
                    </h4>
                  {createForm.npcs.length === 0 ? (
                    <div className="text-center py-8 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
                      <div className="text-gray-500 dark:text-gray-400">
                        <svg className="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                        </svg>
                        <p className="text-lg font-medium">No NPCs added yet</p>
                        <p className="text-sm">Add NPCs to populate your game world</p>
                      </div>
                      <div className="flex flex-col sm:flex-row gap-3 mt-4">
                        <button
                          type="button"
                          onClick={() => {
                            const newNPC: NPCTemplate = {
                              npc_id: `npc_${Date.now()}`,
                              name: '',
                              role: 'villager',
                              personality_traits: ['friendly'],
                              background: '',
                              location: 'village_center'
                            }
                            setCreateForm({ ...createForm, npcs: [...createForm.npcs, newNPC] })
                          }}
                          className="flex-1 btn-primary"
                        >
                          Add Your First NPC
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            const defaultNPCs: NPCTemplate[] = [
                              {
                                npc_id: 'guard_001',
                                name: 'Village Guard',
                                role: 'guard',
                                personality_traits: ['stern', 'protective'],
                                background: 'A loyal guard protecting the village entrance',
                                location: 'village_gate'
                              },
                              {
                                npc_id: 'merchant_001',
                                name: 'Trader Bob',
                                role: 'merchant',
                                personality_traits: ['cheerful', 'helpful'],
                                background: 'A friendly merchant selling goods at the market',
                                location: 'market_square'
                              },
                              {
                                npc_id: 'elder_001',
                                name: 'Village Elder',
                                role: 'elder',
                                personality_traits: ['wise', 'mysterious'],
                                background: 'The wise elder who knows the village\'s secrets',
                                location: 'village_center'
                              },
                              {
                                npc_id: 'innkeeper_001',
                                name: 'Sarah the Innkeeper',
                                role: 'artisan',
                                personality_traits: ['friendly', 'curious'],
                                background: 'Runs the local inn and knows all the gossip',
                                location: 'inn'
                              }
                            ]
                            setCreateForm({ ...createForm, npcs: defaultNPCs })
                          }}
                          className="flex-1 btn-secondary"
                        >
                          🎭 Add Demo NPCs
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {createForm.npcs.map((npc, index) => (
                        <div key={index} className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
                          <div className="flex items-center justify-between mb-3">
                            <h4 className="font-medium text-gray-800 dark:text-gray-200">
                              NPC #{index + 1}
                            </h4>
                            <button
                              type="button"
                              onClick={() => {
                                const newNPCs = createForm.npcs.filter((_, i) => i !== index)
                                setCreateForm({ ...createForm, npcs: newNPCs })
                              }}
                              className="text-red-500 hover:text-red-700 p-1"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </button>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div>
                              <label className="block text-xs font-medium mb-1 text-gray-700 dark:text-gray-300">
                                NPC ID
                              </label>
                              <input
                                type="text"
                                value={npc.npc_id}
                                onChange={(e) => {
                                  const newNPCs = [...createForm.npcs]
                                  newNPCs[index] = { ...newNPCs[index], npc_id: e.target.value }
                                  setCreateForm({ ...createForm, npcs: newNPCs })
                                }}
                                className="input-field text-sm"
                                placeholder="npc_guard_001"
                              />
                            </div>
                            
                            <div>
                              <label className="block text-xs font-medium mb-1 text-gray-700 dark:text-gray-300">
                                Name
                              </label>
                              <input
                                type="text"
                                value={npc.name}
                                onChange={(e) => {
                                  const newNPCs = [...createForm.npcs]
                                  newNPCs[index] = { ...newNPCs[index], name: e.target.value }
                                  setCreateForm({ ...createForm, npcs: newNPCs })
                                }}
                                className="input-field text-sm"
                                placeholder="Village Guard"
                              />
                            </div>
                            
                            <div>
                              <label className="block text-xs font-medium mb-1 text-gray-700 dark:text-gray-300">
                                Role
                              </label>
                              <select
                                value={npc.role}
                                onChange={(e) => {
                                  const newNPCs = [...createForm.npcs]
                                  newNPCs[index] = { ...newNPCs[index], role: e.target.value }
                                  setCreateForm({ ...createForm, npcs: newNPCs })
                                }}
                                className="input-field text-sm"
                              >
                                <option value="villager">Villager</option>
                                <option value="guard">Guard</option>
                                <option value="merchant">Merchant</option>
                                <option value="scholar">Scholar</option>
                                <option value="noble">Noble</option>
                                <option value="artisan">Artisan</option>
                                <option value="child">Child</option>
                                <option value="elder">Elder</option>
                              </select>
                            </div>
                            
                            <div>
                              <label className="block text-xs font-medium mb-1 text-gray-700 dark:text-gray-300">
                                Location
                              </label>
                              <select
                                value={npc.location}
                                onChange={(e) => {
                                  const newNPCs = [...createForm.npcs]
                                  newNPCs[index] = { ...newNPCs[index], location: e.target.value }
                                  setCreateForm({ ...createForm, npcs: newNPCs })
                                }}
                                className="input-field text-sm"
                              >
                                <option value="village_center">Village Center</option>
                                <option value="village_gate">Village Gate</option>
                                <option value="tavern">Tavern</option>
                                <option value="market_square">Market Square</option>
                                <option value="blacksmith">Blacksmith</option>
                                <option value="temple">Temple</option>
                                <option value="library">Library</option>
                                <option value="inn">Inn</option>
                              </select>
                            </div>
                          </div>
                          
                          <div className="mt-3">
                            <label className="block text-xs font-medium mb-1 text-gray-700 dark:text-gray-300">
                              Background Story
                            </label>
                            <textarea
                              value={npc.background}
                              onChange={(e) => {
                                const newNPCs = [...createForm.npcs]
                                newNPCs[index] = { ...newNPCs[index], background: e.target.value }
                                setCreateForm({ ...createForm, npcs: newNPCs })
                              }}
                              className="input-field text-sm"
                              rows={2}
                              placeholder="A brief background story for this NPC..."
                            />
                          </div>
                          
                          <div className="mt-3">
                            <label className="block text-xs font-medium mb-1 text-gray-700 dark:text-gray-300">
                              Personality Traits
                            </label>
                            <div className="flex flex-wrap gap-2 mb-2">
                              {npc.personality_traits.map((trait, traitIndex) => (
                                <span
                                  key={traitIndex}
                                  className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                                >
                                  {trait}
                                  <button
                                    type="button"
                                    onClick={() => {
                                      const newNPCs = [...createForm.npcs]
                                      newNPCs[index] = {
                                        ...newNPCs[index],
                                        personality_traits: newNPCs[index].personality_traits.filter((_, ti) => ti !== traitIndex)
                                      }
                                      setCreateForm({ ...createForm, npcs: newNPCs })
                                    }}
                                    className="ml-1 text-blue-600 hover:text-blue-800"
                                  >
                                    ×
                                  </button>
                                </span>
                              ))}
                            </div>
                            <div className="flex gap-2">
                              <select
                                onChange={(e) => {
                                  if (e.target.value && !npc.personality_traits.includes(e.target.value)) {
                                    const newNPCs = [...createForm.npcs]
                                    newNPCs[index] = {
                                      ...newNPCs[index],
                                      personality_traits: [...newNPCs[index].personality_traits, e.target.value]
                                    }
                                    setCreateForm({ ...createForm, npcs: newNPCs })
                                    e.target.value = ''
                                  }
                                }}
                                className="input-field text-sm flex-1"
                              >
                                <option value="">Add personality trait...</option>
                                <option value="friendly">Friendly</option>
                                <option value="stern">Stern</option>
                                <option value="wise">Wise</option>
                                <option value="curious">Curious</option>
                                <option value="protective">Protective</option>
                                <option value="cheerful">Cheerful</option>
                                <option value="grumpy">Grumpy</option>
                                <option value="mysterious">Mysterious</option>
                                <option value="helpful">Helpful</option>
                                <option value="suspicious">Suspicious</option>
                                <option value="brave">Brave</option>
                                <option value="cowardly">Cowardly</option>
                              </select>
                            </div>
                          </div>
                        </div>
                      ))}
                      
                      <button
                        type="button"
                        onClick={() => {
                          const newNPC: NPCTemplate = {
                            npc_id: `npc_${Date.now()}`,
                            name: '',
                            role: 'villager',
                            personality_traits: ['friendly'],
                            background: '',
                            location: 'village_center'
                          }
                          setCreateForm({ ...createForm, npcs: [...createForm.npcs, newNPC] })
                        }}
                        className="w-full btn-secondary border-dashed"
                      >
                        + Add Another NPC
                      </button>
                    </div>
                  )}
                  </div>
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

            {/* Validation Messages */}
            {(!createForm.session_id || !createForm.game_title || (createForm.npcs.length === 0 && createForm.selectedGlobalNPCs.length === 0) || createForm.npcs.some(npc => !npc.name.trim() || !npc.npc_id.trim())) && (
              <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-amber-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-amber-800 dark:text-amber-200">
                      Complete Required Fields
                    </h3>
                    <div className="mt-2 text-sm text-amber-700 dark:text-amber-300">
                      <ul className="list-disc list-inside space-y-1">
                        {!createForm.session_id && <li>Session ID is required</li>}
                        {!createForm.game_title && <li>Game Title is required</li>}
                        {(createForm.npcs.length === 0 && createForm.selectedGlobalNPCs.length === 0) && <li>At least one NPC must be added (global or custom)</li>}
                        {createForm.npcs.some(npc => !npc.name.trim() || !npc.npc_id.trim()) && 
                          <li>All custom NPCs must have both a name and NPC ID</li>
                        }
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}

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
                disabled={creating || !createForm.session_id || !createForm.game_title || (createForm.npcs.length === 0 && createForm.selectedGlobalNPCs.length === 0) || createForm.npcs.some(npc => !npc.name.trim() || !npc.npc_id.trim())}
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