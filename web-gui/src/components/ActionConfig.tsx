import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'

interface ActionProperty {
  name: string
  type: string
  required: boolean
  default?: any
  description: string
  validation?: Record<string, any>
}

interface Action {
  action_id: string
  name: string
  description: string
  target_type: string
  requires_target: boolean
  properties: ActionProperty[]
  affects_mood: boolean
  creates_memory: boolean
  visibility: string
  requirements: Record<string, any>
}

interface ActionDefinitions {
  version: string
  enabled_default_actions: string[]
  default_action_definitions: Action[]
  custom_actions: Action[]
  action_categories: Record<string, string[]>
  global_settings: Record<string, any>
}

interface ActionConfig {
  version: string
  custom_actions: Action[]
  enabled_default_actions: string[]
  action_categories: Record<string, string[]>
  global_settings: Record<string, any>
}

const PropertyEditor: React.FC<{
  properties: ActionProperty[]
  onChange: (properties: ActionProperty[]) => void
}> = ({ properties, onChange }) => {
  const [newProperty, setNewProperty] = useState<ActionProperty>({
    name: '',
    type: 'string',
    required: true,
    description: '',
    validation: {}
  })
  const [showAddForm, setShowAddForm] = useState(false)

  const addProperty = () => {
    if (!newProperty.name.trim()) {
      alert('Property name is required')
      return
    }
    
    // Check for duplicate names
    if (properties.some(p => p.name === newProperty.name.trim())) {
      alert('Property name already exists')
      return
    }
    
    onChange([...properties, { 
      ...newProperty, 
      name: newProperty.name.trim(),
      validation: Object.keys(newProperty.validation || {}).length > 0 ? newProperty.validation : undefined
    }])
    
    setNewProperty({
      name: '',
      type: 'string',
      required: true,
      description: '',
      validation: {}
    })
    setShowAddForm(false)
  }

  const removeProperty = (index: number) => {
    onChange(properties.filter((_, i) => i !== index))
  }

  const updateProperty = (index: number, field: keyof ActionProperty, value: any) => {
    const updated = [...properties]
    updated[index] = { ...updated[index], [field]: value }
    onChange(updated)
  }

  const updateValidation = (index: number, rule: string, value: any) => {
    const updated = [...properties]
    const currentValidation = updated[index].validation || {}
    
    if (value === '' || value === null || value === undefined) {
      // Remove the validation rule if value is empty
      const { [rule]: removed, ...rest } = currentValidation
      updated[index].validation = Object.keys(rest).length > 0 ? rest : undefined
    } else {
      updated[index].validation = {
        ...currentValidation,
        [rule]: rule === 'options' ? value.split(',').map((s: string) => s.trim()).filter(Boolean) : value
      }
    }
    onChange(updated)
  }

  return (
    <div className="space-y-4 border border-gray-200 dark:border-gray-600 rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
      <div className="flex items-center justify-between">
        <div>
          <h5 className="text-lg font-semibold text-gray-800 dark:text-gray-200">Action Properties</h5>
          <p className="text-sm text-gray-600 dark:text-gray-400">Define configurable parameters for this action</p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="btn-secondary text-sm"
        >
          {showAddForm ? 'Cancel' : '+ Add Property'}
        </button>
      </div>
      
      {/* Existing Properties */}
      <div className="space-y-4">
        {properties.length === 0 && !showAddForm && (
          <div className="text-center py-6 text-gray-500 dark:text-gray-400">
            <p>No properties defined yet.</p>
            <p className="text-sm">Click "Add Property" to define configurable parameters for this action.</p>
          </div>
        )}
        {properties.map((prop, index) => (
          <div key={index} className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3 mb-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Name</label>
                <input
                  type="text"
                  value={prop.name}
                  onChange={(e) => updateProperty(index, 'name', e.target.value)}
                  placeholder="Property name"
                  className="w-full text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Type</label>
                <select
                  value={prop.type}
                  onChange={(e) => updateProperty(index, 'type', e.target.value)}
                  className="w-full text-sm"
                >
                  <option value="string">String</option>
                  <option value="integer">Integer</option>
                  <option value="float">Float</option>
                  <option value="boolean">Boolean</option>
                  <option value="list">List</option>
                  <option value="dict">Dict</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Default</label>
                <input
                  type="text"
                  value={prop.default || ''}
                  onChange={(e) => updateProperty(index, 'default', e.target.value || undefined)}
                  placeholder="Default value"
                  className="w-full text-sm"
                />
              </div>
              <div className="flex items-center space-x-4 pt-5">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={prop.required}
                    onChange={(e) => updateProperty(index, 'required', e.target.checked)}
                    className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Required</span>
                </label>
              </div>
              <div className="flex justify-end pt-5">
                <button
                  onClick={() => removeProperty(index)}
                  className="text-red-600 hover:text-red-800 text-xs px-3 py-1 rounded hover:bg-red-50 transition-colors"
                >
                  Remove
                </button>
              </div>
            </div>
            
            {/* Description */}
            <div className="mb-3">
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Description</label>
              <input
                type="text"
                value={prop.description}
                onChange={(e) => updateProperty(index, 'description', e.target.value)}
                placeholder="Describe what this property does"
                className="w-full text-sm"
              />
            </div>
            
            {/* Validation Rules */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {prop.type === 'string' && (
                <>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Options (comma-separated)</label>
                    <input
                      type="text"
                      placeholder="option1, option2, option3"
                      value={prop.validation?.options?.join(', ') || ''}
                      onChange={(e) => updateValidation(index, 'options', e.target.value)}
                      className="w-full text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Min Length</label>
                    <input
                      type="number"
                      placeholder="0"
                      value={prop.validation?.min_length || ''}
                      onChange={(e) => updateValidation(index, 'min_length', e.target.value ? parseInt(e.target.value) : '')}
                      className="w-full text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Max Length</label>
                    <input
                      type="number"
                      placeholder="100"
                      value={prop.validation?.max_length || ''}
                      onChange={(e) => updateValidation(index, 'max_length', e.target.value ? parseInt(e.target.value) : '')}
                      className="w-full text-sm"
                    />
                  </div>
                </>
              )}
              
              {(prop.type === 'integer' || prop.type === 'float') && (
                <>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Min Value</label>
                    <input
                      type="number"
                      step={prop.type === 'float' ? '0.1' : '1'}
                      placeholder="Min"
                      value={prop.validation?.min || ''}
                      onChange={(e) => updateValidation(index, 'min', e.target.value ? parseFloat(e.target.value) : '')}
                      className="w-full text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Max Value</label>
                    <input
                      type="number"
                      step={prop.type === 'float' ? '0.1' : '1'}
                      placeholder="Max"
                      value={prop.validation?.max || ''}
                      onChange={(e) => updateValidation(index, 'max', e.target.value ? parseFloat(e.target.value) : '')}
                      className="w-full text-sm"
                    />
                  </div>
                </>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Add New Property Form */}
      {showAddForm && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4">
          <h6 className="text-md font-semibold text-blue-800 dark:text-blue-200 mb-3">Add New Property</h6>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Name*</label>
              <input
                type="text"
                value={newProperty.name}
                onChange={(e) => setNewProperty({...newProperty, name: e.target.value})}
                placeholder="property_name"
                className="w-full text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Type</label>
              <select
                value={newProperty.type}
                onChange={(e) => setNewProperty({...newProperty, type: e.target.value})}
                className="w-full text-sm"
              >
                <option value="string">String</option>
                <option value="integer">Integer</option>
                <option value="float">Float</option>
                <option value="boolean">Boolean</option>
                <option value="list">List</option>
                <option value="dict">Dict</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Default</label>
              <input
                type="text"
                value={newProperty.default || ''}
                onChange={(e) => setNewProperty({...newProperty, default: e.target.value || undefined})}
                placeholder="Default value"
                className="w-full text-sm"
              />
            </div>
            <div className="flex items-center pt-5">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={newProperty.required}
                  onChange={(e) => setNewProperty({...newProperty, required: e.target.checked})}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Required</span>
              </label>
            </div>
          </div>
          <div className="mb-3">
            <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Description</label>
            <input
              type="text"
              value={newProperty.description}
              onChange={(e) => setNewProperty({...newProperty, description: e.target.value})}
              placeholder="Describe what this property does"
              className="w-full text-sm"
            />
          </div>
          <div className="flex space-x-3">
            <button onClick={addProperty} className="btn-primary text-sm">
              Add Property
            </button>
            <button 
              onClick={() => {
                setShowAddForm(false)
                setNewProperty({
                  name: '',
                  type: 'string',
                  required: true,
                  description: '',
                  validation: {}
                })
              }} 
              className="btn-secondary text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

const ActionConfig: React.FC = () => {
  const [config, setConfig] = useState<ActionConfig | null>(null)
  const [actionDefinitions, setActionDefinitions] = useState<ActionDefinitions | null>(null)
  const [allActions, setAllActions] = useState<Action[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [editingAction, setEditingAction] = useState<string | null>(null)
  const [viewingAction, setViewingAction] = useState<string | null>(null)
  const [newAction, setNewAction] = useState<Action>({
    action_id: '',
    name: '',
    description: '',
    target_type: 'none',
    requires_target: false,
    properties: [],
    affects_mood: false,
    creates_memory: true,
    visibility: 'public',
    requirements: {}
  })

  useEffect(() => {
    loadConfig()
  }, [])

  useEffect(() => {
    if (config && actionDefinitions) {
      // Combine all actions into one list
      const defaultActions: Action[] = actionDefinitions.default_action_definitions.map(def => ({
        ...def,
        affects_mood: false,
        creates_memory: true,
        visibility: 'public',
        requirements: {}
      }))
      
      setAllActions([...defaultActions, ...config.custom_actions])
    }
  }, [config, actionDefinitions])

  const loadConfig = async () => {
    try {
      setLoading(true)
      const [configResponse, definitionsResponse] = await Promise.all([
        axios.get(`${API_BASE}/config/actions`),
        axios.get(`${API_BASE}/config/actions/definitions`)
      ])
      setConfig(configResponse.data)
      setActionDefinitions(definitionsResponse.data)
    } catch (err) {
      console.error('Error loading action config:', err)
      alert('Failed to load action configuration')
    } finally {
      setLoading(false)
    }
  }

  const saveConfig = async () => {
    if (!config) return
    
    try {
      setSaving(true)
      await axios.put(`${API_BASE}/config/actions`, config)
      alert('Configuration saved successfully!')
    } catch (err) {
      console.error('Error saving config:', err)
      alert('Failed to save configuration')
    } finally {
      setSaving(false)
    }
  }

  const addAction = () => {
    if (!config || !newAction.action_id || !newAction.name) {
      alert('Please fill in Action ID and Name')
      return
    }

    // Check for duplicate action IDs
    if (allActions.some(a => a.action_id === newAction.action_id)) {
      alert('Action ID already exists')
      return
    }

    const action: Action = {
      action_id: newAction.action_id,
      name: newAction.name,
      description: newAction.description || '',
      target_type: newAction.target_type || 'none',
      requires_target: newAction.requires_target || false,
      properties: newAction.properties || [],
      affects_mood: newAction.affects_mood || false,
      creates_memory: newAction.creates_memory !== false,
      visibility: newAction.visibility || 'public',
      requirements: newAction.requirements || {}
    }

    setConfig({
      ...config,
      custom_actions: [...config.custom_actions, action]
    })

    resetNewAction()
  }

  const editAction = (actionId: string) => {
    const action = allActions.find(a => a.action_id === actionId)
    if (action) {
      setNewAction({ ...action })
      setEditingAction(actionId)
    }
  }

  const saveEditedAction = () => {
    if (!config || !newAction.action_id) return

    const action: Action = {
      action_id: newAction.action_id,
      name: newAction.name || '',
      description: newAction.description || '',
      target_type: newAction.target_type || 'none',
      requires_target: newAction.requires_target || false,
      properties: newAction.properties || [],
      affects_mood: newAction.affects_mood || false,
      creates_memory: newAction.creates_memory !== false,
      visibility: newAction.visibility || 'public',
      requirements: newAction.requirements || {}
    }

    // Remove from enabled defaults if it was a default action
    const updatedDefaults = config.enabled_default_actions.filter(a => a !== editingAction)
    
    // Add to custom actions (or replace if already custom)
    const updatedCustomActions = config.custom_actions.filter(a => a.action_id !== editingAction)
    updatedCustomActions.push(action)

    setConfig({
      ...config,
      enabled_default_actions: updatedDefaults,
      custom_actions: updatedCustomActions
    })

    setEditingAction(null)
    resetNewAction()
  }

  const removeAction = (actionId: string) => {
    if (!config) return
    
    if (window.confirm(`Are you sure you want to delete the action "${actionId}"?`)) {
      setConfig({
        ...config,
        custom_actions: config.custom_actions.filter(a => a.action_id !== actionId),
        enabled_default_actions: config.enabled_default_actions.filter(a => a !== actionId)
      })
    }
  }

  const resetNewAction = () => {
    setNewAction({
      action_id: '',
      name: '',
      description: '',
      target_type: 'none',
      requires_target: false,
      properties: [],
      affects_mood: false,
      creates_memory: true,
      visibility: 'public',
      requirements: {}
    })
  }

  if (loading) {
    return <div className="loading">Loading action configuration...</div>
  }

  if (!config || !actionDefinitions) {
    return <div className="error">Failed to load configuration</div>
  }

  return (
    <div className="p-6 space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-200">Action Configuration</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Configure actions and properties for your NPCs</p>
        </div>
        <button onClick={saveConfig} disabled={saving} className="btn-primary">
          {saving ? 'Saving...' : 'Save Configuration'}
        </button>
      </div>

      {/* Action System Info */}
      <div className="glass-card p-4 mb-6 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
        <h3 className="text-lg font-semibold text-blue-800 dark:text-blue-200 mb-2">Action System Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <h4 className="font-semibold text-blue-700 dark:text-blue-300">✨ AI-Powered</h4>
            <p className="text-blue-600 dark:text-blue-400">NPCs use Google Gemini to select actions based on context, personality, and environment</p>
          </div>
          <div>
            <h4 className="font-semibold text-blue-700 dark:text-blue-300">🔗 Sequential Actions</h4>
            <p className="text-blue-600 dark:text-blue-400">Actions with the same sequence number execute in parallel, different numbers execute in order</p>
          </div>
          <div>
            <h4 className="font-semibold text-blue-700 dark:text-blue-300">🎯 Target Types</h4>
            <p className="text-blue-600 dark:text-blue-400">Actions specify valid targets: player, npc, location, item, object, self, area, or any</p>
          </div>
        </div>
      </div>

      {/* Add/Edit Action Section */}
      <div className="glass-card p-6">
        <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
          {editingAction ? `Editing: ${editingAction}` : 'Add New Action'}
        </h3>
        
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Action ID</label>
              <input
                type="text"
                placeholder="e.g., craft_sword"
                value={newAction.action_id}
                onChange={(e) => setNewAction({...newAction, action_id: e.target.value})}
                disabled={!!editingAction}
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Action Name</label>
              <input
                type="text"
                placeholder="e.g., Craft Sword"
                value={newAction.name}
                onChange={(e) => setNewAction({...newAction, name: e.target.value})}
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Target Type</label>
              <select
                value={newAction.target_type}
                onChange={(e) => setNewAction({...newAction, target_type: e.target.value})}
                className="w-full"
              >
                <option value="none">No Target</option>
                <option value="player">Player</option>
                <option value="npc">NPC</option>
                <option value="location">Location</option>
                <option value="item">Item</option>
                <option value="object">Object</option>
                <option value="self">Self</option>
                <option value="area">Area</option>
                <option value="any">Any</option>
              </select>
            </div>

            <div className="md:col-span-2 lg:col-span-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
              <textarea
                placeholder="Describe what this action does..."
                value={newAction.description}
                onChange={(e) => setNewAction({...newAction, description: e.target.value})}
                className="w-full h-20 resize-none"
              />
            </div>
          </div>

          <PropertyEditor
            properties={newAction.properties || []}
            onChange={(properties) => setNewAction({...newAction, properties})}
          />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={newAction.requires_target}
                onChange={(e) => setNewAction({...newAction, requires_target: e.target.checked})}
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Requires Target</span>
            </label>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={newAction.affects_mood}
                onChange={(e) => setNewAction({...newAction, affects_mood: e.target.checked})}
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Affects Mood</span>
            </label>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={newAction.creates_memory}
                onChange={(e) => setNewAction({...newAction, creates_memory: e.target.checked})}
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Creates Memory</span>
            </label>
          </div>

          <div className="flex space-x-3">
            <button 
              onClick={editingAction ? saveEditedAction : addAction} 
              className="btn-primary"
            >
              {editingAction ? 'Save Changes' : 'Add Action'}
            </button>
            
            {editingAction && (
              <button 
                onClick={() => {
                  setEditingAction(null)
                  resetNewAction()
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
            )}
          </div>
        </div>
      </div>

      {/* All Actions List */}
      <div className="glass-card p-6">
        <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">All Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {allActions.map(action => (
            <div key={action.action_id} className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200">{action.name}</h4>
                  <span className="text-xs bg-gray-100 dark:bg-gray-600 text-gray-600 dark:text-gray-300 px-2 py-1 rounded">
                    {action.action_id}
                  </span>
                </div>
                <div className="flex space-x-1">
                  <button
                    onClick={() => setViewingAction(viewingAction === action.action_id ? null : action.action_id)}
                    className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded hover:bg-blue-200 transition-colors"
                  >
                    {viewingAction === action.action_id ? 'Hide' : 'View'}
                  </button>
                  <button
                    onClick={() => editAction(action.action_id)}
                    className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded hover:bg-green-200 transition-colors"
                  >
                    Edit
                  </button>
                  <button 
                    onClick={() => removeAction(action.action_id)}
                    className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded hover:bg-red-200 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
              
              <div className="space-y-2 text-sm">
                <p className="text-gray-600 dark:text-gray-400">{action.description}</p>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600 dark:text-gray-400">
                    <span className="font-medium">Target:</span> {action.target_type}
                  </span>
                </div>
                <div className="flex space-x-2 text-xs">
                  {action.affects_mood && <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded">Affects Mood</span>}
                  {action.creates_memory && <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded">Creates Memory</span>}
                  {action.requires_target && <span className="bg-orange-100 text-orange-800 px-2 py-1 rounded">Requires Target</span>}
                </div>
              </div>

              {viewingAction === action.action_id && action.properties.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                  <h5 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Properties:</h5>
                  <div className="space-y-2">
                    {action.properties.map((prop, idx) => (
                      <div key={idx} className="text-xs bg-gray-50 dark:bg-gray-800 p-2 rounded">
                        <div className="font-semibold text-gray-700 dark:text-gray-300">
                          {prop.name} ({prop.type}){prop.required && ' *'}
                        </div>
                        <div className="text-gray-600 dark:text-gray-400">{prop.description}</div>
                        {prop.validation?.options && (
                          <div className="text-blue-600 dark:text-blue-400 mt-1">
                            Options: {prop.validation.options.join(', ')}
                          </div>
                        )}
                        {(prop.validation?.min !== undefined || prop.validation?.max !== undefined) && (
                          <div className="text-blue-600 dark:text-blue-400 mt-1">
                            Range: {prop.validation.min || '∞'} - {prop.validation.max || '∞'}
                          </div>
                        )}
                        {prop.validation?.max_length && (
                          <div className="text-blue-600 dark:text-blue-400 mt-1">
                            Max length: {prop.validation.max_length}
                          </div>
                        )}
                        {prop.default && (
                          <div className="text-green-600 dark:text-green-400 mt-1">
                            Default: {prop.default}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ActionConfig 