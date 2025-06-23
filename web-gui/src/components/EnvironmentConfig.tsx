import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

interface LocationConfig {
  location_id: string
  name: string
  location_type: string
  description: string
  connected_locations: string[]
  properties: Record<string, any>
  available_actions: string[]
  default_objects: Array<{id: string, name: string, interactable: boolean}>
  default_npcs: string[]
  lighting: string
  temperature: string
  noise_level: string
}

interface EnvironmentConfig {
  version: string
  name: string
  description: string
  locations: LocationConfig[]
  weather_patterns: any[]
  default_weather: string
  weather_change_frequency: number
  time_progression_rate: number
  default_time: string
  scheduled_events: any[]
  world_properties: Record<string, any>
  environmental_rules: Record<string, any>
}

const EnvironmentConfig: React.FC = () => {
  const [config, setConfig] = useState<EnvironmentConfig | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [activeTab, setActiveTab] = useState<'world' | 'properties'>('properties')

  const [newPropertyKey, setNewPropertyKey] = useState('')
  const [newPropertyValue, setNewPropertyValue] = useState('')
  const [newPropertyType, setNewPropertyType] = useState<'string' | 'number' | 'boolean'>('string')

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      setLoading(true)
      // Try to load from sample environment first, then default
      try {
        const response = await axios.get(`${API_BASE}/config/environment/sample_environment.yaml`)
        setConfig(response.data)
      } catch {
        const response = await axios.get(`${API_BASE}/config/environment`)
        setConfig(response.data)
      }
    } catch (err) {
      console.error('Error loading environment config:', err)
      // Create default config if none exists
      setConfig({
        version: '1.0',
        name: 'My Game World',
        description: 'A customizable game environment',
        locations: [],
        weather_patterns: [],
        default_weather: 'sunny',
        weather_change_frequency: 0.1,
        time_progression_rate: 1.0,
        default_time: 'morning',
        scheduled_events: [],
        world_properties: {},
        environmental_rules: {}
      })
    } finally {
      setLoading(false)
    }
  }

  const saveConfig = async () => {
    if (!config) return
    
    try {
      setSaving(true)
      await axios.put(`${API_BASE}/config/environment`, config)
      alert('Environment saved successfully! 🎉')
    } catch (err) {
      console.error('Error saving config:', err)
      alert('Failed to save environment configuration')
    } finally {
      setSaving(false)
    }
  }



  const addCustomProperty = () => {
    if (!config || !newPropertyKey.trim()) {
      alert('Please enter a property name')
      return
    }

    if (config.world_properties[newPropertyKey]) {
      alert('Property with this name already exists')
      return
    }

    let value: any = newPropertyValue
    
    // Convert value based on type
    if (newPropertyType === 'number') {
      value = parseFloat(newPropertyValue) || 0
    } else if (newPropertyType === 'boolean') {
      value = newPropertyValue.toLowerCase() === 'true'
    }

    setConfig({
      ...config,
      world_properties: {
        ...config.world_properties,
        [newPropertyKey]: value
      }
    })

    // Reset form
    setNewPropertyKey('')
    setNewPropertyValue('')
    setNewPropertyType('string')
  }

  const removeCustomProperty = (key: string) => {
    if (!config) return
    
    if (confirm(`Are you sure you want to remove the "${key}" property?`)) {
      const updatedProperties = { ...config.world_properties }
      delete updatedProperties[key]
      
      setConfig({
        ...config,
        world_properties: updatedProperties
      })
    }
  }

  const updateCustomProperty = (key: string, value: any) => {
    if (!config) return
    
    setConfig({
      ...config,
      world_properties: {
        ...config.world_properties,
        [key]: value
      }
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <span className="ml-3 text-lg">Loading environment...</span>
      </div>
    )
  }

  if (!config) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <h3 className="text-xl font-semibold text-red-600 mb-2">Failed to load environment</h3>
          <button onClick={loadConfig} className="btn-primary">
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="environment-config min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <div className="glass-card mb-8 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-800 dark:text-slate-200 mb-2">
              🌍 Environment Configuration
            </h1>
            <p className="text-slate-600 dark:text-slate-400">
              Design and customize your game world environment
            </p>
          </div>
          <button 
            onClick={saveConfig} 
            disabled={saving}
            className="btn-primary flex items-center space-x-2"
          >
            {saving ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Saving...</span>
              </>
            ) : (
              <>
                <span>💾</span>
                <span>Save Environment</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="glass-card mb-8">
        <div className="flex border-b border-slate-200 dark:border-slate-700">
          {[
            { id: 'world', label: 'World Settings', icon: '🌍' },
            { id: 'properties', label: 'Custom Properties', icon: '⚙️' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-6 py-4 font-medium transition-colors ${
                activeTab === tab.id
                  ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'world' && (
        <div className="space-y-6">
          {/* Basic World Info */}
          <div className="glass-card p-8">
            <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-200 mb-6">Basic World Information</h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    🏰 World Name
                  </label>
                  <input
                    type="text"
                    value={config.name}
                    onChange={(e) => setConfig({...config, name: e.target.value})}
                    className="input-field"
                    placeholder="Enter world name..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    📝 World Description
                  </label>
                  <textarea
                    value={config.description}
                    onChange={(e) => setConfig({...config, description: e.target.value})}
                    className="input-field h-32 resize-none"
                    placeholder="Describe your world..."
                  />
                </div>
              </div>

              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    📦 Version
                  </label>
                  <input
                    type="text"
                    value={config.version}
                    onChange={(e) => setConfig({...config, version: e.target.value})}
                    className="input-field"
                    placeholder="1.0"
                  />
                </div>
                
                <div className="glass-card p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border border-blue-200 dark:border-blue-800">
                  <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-3 flex items-center">
                    🎯 Everything is Customizable!
                  </h4>
                  <p className="text-sm text-blue-700 dark:text-blue-300 mb-3">
                    Use <strong>Custom Properties</strong> to define any world settings you need:
                  </p>
                  <div className="grid grid-cols-2 gap-2 text-xs text-blue-600 dark:text-blue-400">
                    <div>• Weather & Climate</div>
                    <div>• Time Systems</div>
                    <div>• Magic Settings</div>
                    <div>• Economy State</div>
                    <div>• Difficulty Levels</div>
                    <div>• Locations & Areas</div>
                    <div>• Cultural Elements</div>
                    <div>• Game Mechanics</div>
                  </div>
                  <button
                    onClick={() => setActiveTab('properties')}
                    className="mt-4 text-sm bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
                  >
                    Go to Custom Properties →
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      

       {activeTab === 'properties' && (
         <div className="space-y-6">
           {/* Properties Header */}
           <div className="glass-card p-6">
             <div className="flex items-center justify-between">
               <div>
                 <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-200 mb-2">
                   ⚙️ Custom Properties ({Object.keys(config.world_properties).length})
                 </h2>
                 <p className="text-slate-600 dark:text-slate-400">
                   Add custom properties that NPCs and game logic can reference
                 </p>
               </div>
             </div>
           </div>

           {/* Add New Property Form */}
           <div className="glass-card p-6">
             <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-200 mb-4">
               ➕ Add New Property
             </h3>
             
             <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-end">
               <div>
                 <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                   🏷️ Property Name
                 </label>
                 <input
                   type="text"
                   value={newPropertyKey}
                   onChange={(e) => setNewPropertyKey(e.target.value)}
                   className="input-field"
                   placeholder="property_name"
                 />
               </div>
               
               <div>
                 <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                   📊 Type
                 </label>
                 <select
                   value={newPropertyType}
                   onChange={(e) => setNewPropertyType(e.target.value as any)}
                   className="input-field"
                 >
                   <option value="string">📝 Text</option>
                   <option value="number">🔢 Number</option>
                   <option value="boolean">✅ True/False</option>
                 </select>
               </div>
               
               <div className="md:col-span-2">
                 <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                   💾 Value
                 </label>
                 {newPropertyType === 'boolean' ? (
                   <select
                     value={newPropertyValue}
                     onChange={(e) => setNewPropertyValue(e.target.value)}
                     className="input-field"
                   >
                     <option value="true">✅ True</option>
                     <option value="false">❌ False</option>
                   </select>
                 ) : (
                   <input
                     type={newPropertyType === 'number' ? 'number' : 'text'}
                     value={newPropertyValue}
                     onChange={(e) => setNewPropertyValue(e.target.value)}
                     className="input-field"
                     placeholder={newPropertyType === 'number' ? '123' : 'Enter value...'}
                   />
                 )}
               </div>
               
               <div>
                 <button
                   onClick={addCustomProperty}
                   className="btn-primary w-full"
                   disabled={!newPropertyKey.trim()}
                 >
                   Add
                 </button>
               </div>
             </div>
           </div>

           {/* Existing Properties */}
           <div className="glass-card p-6">
             <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-200 mb-4">
               📋 Current Properties
             </h3>
             
             {Object.keys(config.world_properties).length === 0 ? (
               <div className="text-center py-12">
                 <div className="text-6xl mb-4">⚙️</div>
                 <h4 className="text-xl font-semibold text-slate-700 dark:text-slate-300 mb-2">
                   No custom properties yet
                 </h4>
                 <p className="text-slate-500">
                   Add custom properties to enhance your game world
                 </p>
               </div>
             ) : (
               <div className="space-y-3">
                 {Object.entries(config.world_properties).map(([key, value]) => (
                   <div key={key} className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                     <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                       <div>
                         <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Property</span>
                         <div className="font-semibold text-slate-800 dark:text-slate-200">{key}</div>
                       </div>
                       
                       <div>
                         <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Type</span>
                         <div className="text-blue-600 dark:text-blue-400">
                           {typeof value === 'string' && '📝 Text'}
                           {typeof value === 'number' && '🔢 Number'}
                           {typeof value === 'boolean' && '✅ Boolean'}
                         </div>
                       </div>
                       
                       <div className="flex items-center space-x-3">
                         <div className="flex-1">
                           <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Value</span>
                           {typeof value === 'boolean' ? (
                             <select
                               value={value.toString()}
                               onChange={(e) => updateCustomProperty(key, e.target.value === 'true')}
                               className="input-field mt-1"
                             >
                               <option value="true">✅ True</option>
                               <option value="false">❌ False</option>
                             </select>
                           ) : (
                             <input
                               type={typeof value === 'number' ? 'number' : 'text'}
                               value={value.toString()}
                               onChange={(e) => {
                                 const newValue = typeof value === 'number' 
                                   ? parseFloat(e.target.value) || 0 
                                   : e.target.value
                                 updateCustomProperty(key, newValue)
                               }}
                               className="input-field mt-1"
                             />
                           )}
                         </div>
                         
                         <button
                           onClick={() => removeCustomProperty(key)}
                           className="text-slate-400 hover:text-red-600 transition-colors p-2"
                           title="Remove property"
                         >
                           🗑️
                         </button>
                       </div>
                     </div>
                   </div>
                 ))}
               </div>
             )}
           </div>

           {/* Property Usage Examples */}
           <div className="glass-card p-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
             <h3 className="text-lg font-semibold text-blue-800 dark:text-blue-200 mb-4">
               💡 How Custom Properties Work
             </h3>
             
             <div className="space-y-3 text-sm text-blue-700 dark:text-blue-300">
               <div className="flex items-start space-x-3">
                 <span className="text-blue-500">🎮</span>
                 <div>
                   <strong>Game Logic:</strong> NPCs can reference these properties in their decision-making
                 </div>
               </div>
               
               <div className="flex items-start space-x-3">
                 <span className="text-blue-500">🧠</span>
                 <div>
                   <strong>AI Context:</strong> Properties are included in NPC prompts for more contextual responses
                 </div>
               </div>
               
               <div className="flex items-start space-x-3">
                 <span className="text-blue-500">⚙️</span>
                 <div>
                   <strong>Examples:</strong> "magic_enabled": true, "difficulty_level": 5, "season": "winter"
                 </div>
               </div>
             </div>
           </div>
         </div>
       )}


    </div>
  )
}

export default EnvironmentConfig 