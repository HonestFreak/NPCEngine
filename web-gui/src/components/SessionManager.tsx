import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

interface Session {
  session_id: string
  status: string
  npcs_count: number
  uptime: number
  created_at: string
  environment: {
    time_of_day: string
    weather: string
    location: string
  }
}

interface Environment {
  time_of_day: string
  weather: string
  world_properties: Record<string, any>
  events: Array<{
    event_type: string
    description: string
    timestamp: string
  }>
}

const SessionManager: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedSession, setSelectedSession] = useState<string>('')
  const [environment, setEnvironment] = useState<Environment | null>(null)
  const [environmentUpdate, setEnvironmentUpdate] = useState({
    time_of_day: 'morning',
    weather: 'sunny',
    world_properties: {}
  })
  const [updating, setUpdating] = useState(false)
  const [loadingEnv, setLoadingEnv] = useState(false)

  useEffect(() => {
    loadSessions()
  }, [])

  useEffect(() => {
    if (selectedSession) {
      loadEnvironment()
    }
  }, [selectedSession])

  const loadSessions = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE}/sessions`)
      setSessions(response.data)
    } catch (err) {
      console.error('Error loading sessions:', err)
      setSessions([])
    } finally {
      setLoading(false)
    }
  }

  const loadEnvironment = async () => {
    if (!selectedSession) return
    
    try {
      setLoadingEnv(true)
      const response = await axios.get(`${API_BASE}/sessions/${selectedSession}/environment`)
      setEnvironment(response.data)
      setEnvironmentUpdate({
        time_of_day: response.data.time_of_day || 'morning',
        weather: response.data.weather || 'sunny',
        world_properties: response.data.world_properties || {}
      })
    } catch (err) {
      console.error('Error loading environment:', err)
      setEnvironment(null)
    } finally {
      setLoadingEnv(false)
    }
  }

  const updateEnvironment = async () => {
    if (!selectedSession) {
      alert('Please select a session first')
      return
    }

    try {
      setUpdating(true)
      await axios.put(`${API_BASE}/sessions/${selectedSession}/environment`, environmentUpdate)
      await loadEnvironment() // Reload to show updated data
      alert('Environment updated successfully!')
    } catch (err: any) {
      console.error('Error updating environment:', err)
      alert(err.response?.data?.detail || 'Failed to update environment')
    } finally {
      setUpdating(false)
    }
  }

  const deleteSession = async (sessionId: string) => {
    if (!confirm(`Are you sure you want to delete session "${sessionId}"?`)) return

    try {
      await axios.delete(`${API_BASE}/sessions/${sessionId}`)
      await loadSessions()
      if (selectedSession === sessionId) {
        setSelectedSession('')
        setEnvironment(null)
      }
      alert('Session deleted successfully!')
    } catch (err: any) {
      console.error('Error deleting session:', err)
      alert(err.response?.data?.detail || 'Failed to delete session')
    }
  }

  const timeOfDayEmoji = (time: string) => {
    const emojis: Record<string, string> = {
      dawn: '🌅',
      morning: '🌤️',
      noon: '☀️',
      afternoon: '🌞',
      evening: '��',
      night: '🌙',
      midnight: '🌃'
    }
    return emojis[time] || '🌤️'
  }

  const weatherEmoji = (weather: string) => {
    const emojis: Record<string, string> = {
      sunny: '☀️',
      cloudy: '☁️',
      rainy: '🌧️',
      stormy: '⛈️',
      foggy: '🌫️',
      snowy: '❄️'
    }
    return emojis[weather] || '☀️'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-lg font-medium text-gray-600 dark:text-gray-400">Loading sessions...</span>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-200">Session Manager</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Manage game sessions and environments in real-time</p>
        </div>
        <button
          onClick={loadSessions}
          className="btn-secondary flex items-center space-x-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Refresh</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Sessions List */}
        <div className="lg:col-span-1">
          <div className="glass-card p-6">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">Active Sessions</h2>
            
            {sessions.length === 0 ? (
              <div className="text-center py-8">
                <svg className="w-12 h-12 mx-auto text-gray-400 dark:text-gray-600 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                <p className="text-gray-500 dark:text-gray-400">No active sessions</p>
              </div>
            ) : (
              <div className="space-y-3">
                {sessions.map((session) => (
                  <div
                    key={session.session_id}
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      selectedSession === session.session_id
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                    }`}
                    onClick={() => setSelectedSession(session.session_id)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-gray-800 dark:text-gray-200 truncate">
                        {session.session_id}
                      </h3>
                      <span className={`badge ${session.status === 'active' ? 'badge-success' : 'badge-warning'}`}>
                        {session.status}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                      <div className="flex justify-between">
                        <span>NPCs:</span>
                        <span className="font-medium">{session.npcs_count}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Uptime:</span>
                        <span className="font-medium">{Math.floor(session.uptime / 60)}m</span>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        deleteSession(session.session_id)
                      }}
                      className="mt-2 text-red-600 hover:text-red-800 text-sm"
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Environment Controls */}
        <div className="lg:col-span-2">
          {selectedSession ? (
            <div className="space-y-6">
              {/* Current Environment Status */}
              <div className="glass-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                    Environment Status
                  </h2>
                  {loadingEnv && (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                  )}
                </div>

                {environment ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 p-4 rounded-lg border border-amber-200 dark:border-amber-700">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">{timeOfDayEmoji(environment.time_of_day)}</span>
                        <div>
                          <p className="text-sm text-amber-700 dark:text-amber-300">Time of Day</p>
                          <p className="font-semibold text-amber-800 dark:text-amber-200 capitalize">
                            {environment.time_of_day}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-700">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">{weatherEmoji(environment.weather)}</span>
                        <div>
                          <p className="text-sm text-blue-700 dark:text-blue-300">Weather</p>
                          <p className="font-semibold text-blue-800 dark:text-blue-200 capitalize">
                            {environment.weather}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-500 dark:text-gray-400">No environment data available</p>
                  </div>
                )}
              </div>

              {/* Environment Controls */}
              <div className="glass-card p-6">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
                  Update Environment
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Time of Day
                    </label>
                    <select
                      value={environmentUpdate.time_of_day}
                      onChange={(e) => setEnvironmentUpdate({
                        ...environmentUpdate,
                        time_of_day: e.target.value
                      })}
                      className="w-full"
                    >
                      <option value="dawn">🌅 Dawn</option>
                      <option value="morning">🌤️ Morning</option>
                      <option value="noon">☀️ Noon</option>
                      <option value="afternoon">🌞 Afternoon</option>
                      <option value="evening">🌆 Evening</option>
                      <option value="night">🌙 Night</option>
                      <option value="midnight">🌃 Midnight</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Weather
                    </label>
                    <select
                      value={environmentUpdate.weather}
                      onChange={(e) => setEnvironmentUpdate({
                        ...environmentUpdate,
                        weather: e.target.value
                      })}
                      className="w-full"
                    >
                      <option value="sunny">☀️ Sunny</option>
                      <option value="cloudy">☁️ Cloudy</option>
                      <option value="rainy">🌧️ Rainy</option>
                      <option value="stormy">⛈️ Stormy</option>
                      <option value="foggy">🌫️ Foggy</option>
                      <option value="snowy">❄️ Snowy</option>
                    </select>
                  </div>
                </div>

                <button
                  onClick={updateEnvironment}
                  disabled={updating}
                  className="btn-primary disabled:opacity-50"
                >
                  {updating ? 'Updating...' : 'Update Environment'}
                </button>
              </div>

              {/* Quick Actions */}
              <div className="glass-card p-6">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
                  Quick Actions
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button
                    onClick={() => window.open(`/viewer?session=${selectedSession}`, '_blank')}
                    className="p-4 text-left bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg border border-purple-200 dark:border-purple-700 hover:shadow-lg transition-all"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-purple-500 text-white rounded-lg">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="font-semibold text-purple-800 dark:text-purple-200">View NPCs</h3>
                        <p className="text-sm text-purple-600 dark:text-purple-400">Monitor NPC status</p>
                      </div>
                    </div>
                  </button>

                  <button
                    onClick={() => window.open(`${API_BASE}/docs`, '_blank')}
                    className="p-4 text-left bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg border border-green-200 dark:border-green-700 hover:shadow-lg transition-all"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-green-500 text-white rounded-lg">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="font-semibold text-green-800 dark:text-green-200">API Docs</h3>
                        <p className="text-sm text-green-600 dark:text-green-400">View API documentation</p>
                      </div>
                    </div>
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-card p-6">
              <div className="text-center py-12">
                <svg className="w-16 h-16 mx-auto text-gray-400 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <h3 className="text-lg font-medium text-gray-600 dark:text-gray-400 mb-2">
                  Select a Session
                </h3>
                <p className="text-gray-500 dark:text-gray-500">
                  Choose a session from the list to manage its environment and settings
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default SessionManager 