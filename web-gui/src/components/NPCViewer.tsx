import { useState } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'

interface NPCData {
  npc_id: string
  status: any
  personality: any
  memory_summary: {
    short_term_count: number
    long_term_count: number
    recent_memories: string[]
  }
}

const NPCViewer: React.FC = () => {
  const [sessionId, setSessionId] = useState<string>('')
  const [npcs, setNpcs] = useState<NPCData[]>([])
  const [selectedNPC, setSelectedNPC] = useState<string>('')
  const [npcDetails, setNpcDetails] = useState<NPCData | null>(null)
  const [loading, setLoading] = useState(false)

  const loadNPCs = async () => {
    if (!sessionId) {
      alert('Please enter a session ID')
      return
    }

    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE}/sessions/${sessionId}/npcs`)
      
      // Convert the NPCs object to array format
      const npcArray = Object.entries(response.data.npcs || {}).map(([id, data]: [string, any]) => ({
        npc_id: id,
        status: data,
        personality: {},
        memory_summary: {
          short_term_count: 0,
          long_term_count: 0,
          recent_memories: []
        }
      }))
      
      setNpcs(npcArray)
    } catch (err) {
      console.error('Error loading NPCs:', err)
      alert('Failed to load NPCs. Make sure the session exists.')
    } finally {
      setLoading(false)
    }
  }

  const loadNPCDetails = async (npcId: string) => {
    if (!sessionId) return

    try {
      const response = await axios.get(`${API_BASE}/sessions/${sessionId}/npcs/${npcId}`)
      setNpcDetails(response.data)
    } catch (err) {
      console.error('Error loading NPC details:', err)
      alert('Failed to load NPC details')
    }
  }

  const handleNPCSelect = (npcId: string) => {
    setSelectedNPC(npcId)
    loadNPCDetails(npcId)
  }

  return (
    <div className="npc-viewer">
      <h2>NPC Viewer</h2>

      <div className="session-input">
        <h3>Session Selection</h3>
        <div className="input-group">
          <input
            type="text"
            placeholder="Enter Session ID"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            className="session-id-input"
          />
          <button 
            onClick={loadNPCs}
            className="btn btn-primary"
            disabled={!sessionId || loading}
          >
            {loading ? 'Loading...' : 'Load NPCs'}
          </button>
        </div>
      </div>

      {npcs.length > 0 && (
        <div className="npcs-grid">
          <div className="npcs-list">
            <h3>NPCs in Session</h3>
            <div className="npc-cards">
              {npcs.map(npc => (
                <div 
                  key={npc.npc_id}
                  className={`npc-card ${selectedNPC === npc.npc_id ? 'selected' : ''}`}
                  onClick={() => handleNPCSelect(npc.npc_id)}
                >
                  <h4>{npc.npc_id}</h4>
                  <p><strong>Location:</strong> {npc.status?.location || 'Unknown'}</p>
                  <p><strong>Activity:</strong> {npc.status?.activity || 'Unknown'}</p>
                  <p><strong>Mood:</strong> {npc.status?.mood || 'Unknown'}</p>
                  <p><strong>Energy:</strong> {npc.status?.energy || 'Unknown'}</p>
                </div>
              ))}
            </div>
          </div>

          {npcDetails && (
            <div className="npc-details">
              <h3>NPC Details: {npcDetails.npc_id}</h3>
              
              <div className="detail-section">
                <h4>Current Status</h4>
                <div className="status-grid">
                  <div><strong>Location:</strong> {npcDetails.status?.location}</div>
                  <div><strong>Activity:</strong> {npcDetails.status?.activity}</div>
                  <div><strong>Mood:</strong> {npcDetails.status?.mood}</div>
                  <div><strong>Health:</strong> {npcDetails.status?.health}</div>
                  <div><strong>Energy:</strong> {npcDetails.status?.energy}</div>
                </div>
              </div>

              <div className="detail-section">
                <h4>Personality</h4>
                <div className="personality-info">
                  <p><strong>Name:</strong> {npcDetails.personality?.name}</p>
                  <p><strong>Role:</strong> {npcDetails.personality?.role}</p>
                  <p><strong>Traits:</strong> {npcDetails.personality?.traits?.join(', ')}</p>
                  <p><strong>Background:</strong> {npcDetails.personality?.background}</p>
                  <p><strong>Goals:</strong> {npcDetails.personality?.goals?.join(', ')}</p>
                </div>
              </div>

              <div className="detail-section">
                <h4>Memory</h4>
                <div className="memory-info">
                  <p><strong>Short-term memories:</strong> {npcDetails.memory_summary?.short_term_count}</p>
                  <p><strong>Long-term memories:</strong> {npcDetails.memory_summary?.long_term_count}</p>
                  
                  {npcDetails.memory_summary?.recent_memories?.length > 0 && (
                    <div className="recent-memories">
                      <strong>Recent memories:</strong>
                      <ul>
                        {npcDetails.memory_summary.recent_memories.map((memory, idx) => (
                          <li key={idx}>{memory}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>

              <div className="detail-section">
                <h4>Inventory</h4>
                <div className="inventory-info">
                  {npcDetails.status?.inventory?.length > 0 ? (
                    <ul>
                      {npcDetails.status.inventory.map((item: string, idx: number) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  ) : (
                    <p>No items in inventory</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {sessionId && npcs.length === 0 && !loading && (
        <div className="no-npcs">
          <p>No NPCs found in this session. Make sure the session exists and has NPCs.</p>
        </div>
      )}
    </div>
  )
}

export default NPCViewer 