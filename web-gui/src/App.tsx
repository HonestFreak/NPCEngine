import { useState } from 'react'
import './App.css'
import Dashboard from './components/Dashboard'
import PlayerActionConfig from './components/PlayerActionConfig'
import NPCActionConfig from './components/NPCActionConfig'
import EnvironmentConfig from './components/EnvironmentConfig'
import NPCManager from './components/NPCManager'
import NPCViewer from './components/NPCViewer'
import SessionManager from './components/SessionManager'

type TabType = 'dashboard' | 'player-actions' | 'npc-actions' | 'environment' | 'npcs' | 'viewer' | 'sessions'

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard')

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />
      case 'player-actions':
        return <PlayerActionConfig />
      case 'npc-actions':
        return <NPCActionConfig />
      case 'environment':
        return <EnvironmentConfig />
      case 'npcs':
        return <NPCManager />
      case 'viewer':
        return <NPCViewer />
      case 'sessions':
        return <SessionManager />
      default:
        return <Dashboard />
    }
  }

  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: '🏠' },
    { id: 'player-actions', name: 'Player Actions', icon: '🎯' },
    { id: 'npc-actions', name: 'NPC Actions', icon: '⚡' },
    { id: 'environment', name: 'Environment', icon: '🌍' },
    { id: 'npcs', name: 'NPCs', icon: '👥' },
    { id: 'viewer', name: 'NPC Viewer', icon: '👁️' },
    { id: 'sessions', name: 'Sessions', icon: '🕹️' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      {/* Navigation */}
      <nav className="glass-card mx-4 mt-4 mb-6">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">N</span>
              </div>
      <div>
                <h1 className="text-xl font-bold text-gray-800 dark:text-gray-200">NPC Engine</h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">AI-Powered Agent Framework</p>
              </div>
      </div>
            
            <div className="flex items-center space-x-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as TabType)}
                  className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.name}
        </button>
              ))}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 pb-8">
        {renderContent()}
      </main>

      {/* Footer */}
      <footer className="mt-12 py-6 text-center text-gray-600 dark:text-gray-400">
        <p className="text-sm">
          Built with ❤️ using Google Agent Development Kit • 
        </p>
      </footer>
      </div>
  )
}

export default App
