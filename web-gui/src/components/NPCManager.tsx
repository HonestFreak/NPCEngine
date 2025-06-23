import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

interface NPCProperty {
  name: string
  type: 'string' | 'integer' | 'float' | 'boolean' | 'list' | 'dict'
  description: string
  default_value: any
  required: boolean
  choices?: any[]
  min_value?: number
  max_value?: number
  min_length?: number
  max_length?: number
}

interface NPCRelationship {
  npc_id: string
  relationship_type: string
  description: string
  strength: number
}

interface NPCSchema {
  schema_id: string
  name: string
  description: string
  core_properties: Record<string, any>
  custom_properties: NPCProperty[]
  example_properties: NPCProperty[]
}

interface NPCInstance {
  id: string
  name: string
  description: string
  schema_id: string
  properties: Record<string, any>
  relationships: NPCRelationship[]
  session_data: Record<string, any>
  created_at: string
  last_updated: string
}

interface NPCConfig {
  schemas: Record<string, NPCSchema>
  instances: Record<string, NPCInstance>
}

const PropertyEditor: React.FC<{
  properties: NPCProperty[]
  onChange: (properties: NPCProperty[]) => void
  title: string
}> = ({ properties, onChange, title }) => {
  const [editingProperty, setEditingProperty] = useState<NPCProperty | null>(null)
  const [showAddForm, setShowAddForm] = useState(false)

  const addProperty = () => {
    const newProperty: NPCProperty = {
      name: '',
      type: 'string',
      description: '',
      default_value: '',
      required: false
    }
    setEditingProperty(newProperty)
    setShowAddForm(true)
  }

  const saveProperty = () => {
    if (!editingProperty || !editingProperty.name) return

    const existingIndex = properties.findIndex(p => p.name === editingProperty.name)
    if (existingIndex >= 0) {
      const updated = [...properties]
      updated[existingIndex] = editingProperty
      onChange(updated)
    } else {
      onChange([...properties, editingProperty])
    }

    setEditingProperty(null)
    setShowAddForm(false)
  }

  const deleteProperty = (name: string) => {
    onChange(properties.filter(p => p.name !== name))
  }

  const editProperty = (property: NPCProperty) => {
    setEditingProperty({ ...property })
    setShowAddForm(true)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold text-slate-800 dark:text-slate-200">{title}</h4>
        <button
          onClick={addProperty}
          className="btn-primary text-sm py-2 px-4"
        >
          Add Property
        </button>
      </div>

      {properties.length === 0 ? (
        <p className="text-slate-500 dark:text-slate-400 text-center py-8">
          No properties defined. Click "Add Property" to create one.
        </p>
      ) : (
        <div className="space-y-3">
          {properties.map((property) => (
            <div key={property.name} className="glass-card p-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <span className="font-medium text-slate-800 dark:text-slate-200">
                      {property.name}
                    </span>
                    <span className="badge badge-info">
                      {property.type}
                    </span>
                    {property.required && (
                      <span className="badge badge-danger">Required</span>
                    )}
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                    {property.description}
                  </p>
                  {property.default_value !== undefined && (
                    <p className="text-xs text-slate-500 dark:text-slate-500 mt-1">
                      Default: {JSON.stringify(property.default_value)}
                    </p>
                  )}
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => editProperty(property)}
                    className="btn-secondary text-sm py-1 px-3"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => deleteProperty(property.name)}
                    className="btn-danger text-sm py-1 px-3"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Property Edit Modal */}
      {showAddForm && editingProperty && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="glass-card max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-slate-800 dark:text-slate-200">
                {properties.find(p => p.name === editingProperty.name) ? 'Edit Property' : 'Add Property'}
              </h3>
              <button
                onClick={() => {
                  setEditingProperty(null)
                  setShowAddForm(false)
                }}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Property Name
                  </label>
                  <input
                    type="text"
                    value={editingProperty.name}
                    onChange={(e) => setEditingProperty({ ...editingProperty, name: e.target.value })}
                    className="input-field"
                    placeholder="e.g., age, job, wealth"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Type
                  </label>
                  <select
                    value={editingProperty.type}
                    onChange={(e) => setEditingProperty({ ...editingProperty, type: e.target.value as any })}
                    className="select-field"
                  >
                    <option value="string">String</option>
                    <option value="integer">Integer</option>
                    <option value="float">Float</option>
                    <option value="boolean">Boolean</option>
                    <option value="list">List</option>
                    <option value="dict">Dictionary</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Description
                </label>
                <textarea
                  value={editingProperty.description}
                  onChange={(e) => setEditingProperty({ ...editingProperty, description: e.target.value })}
                  className="input-field"
                  rows={3}
                  placeholder="Describe what this property represents..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Default Value
                </label>
                <input
                  type="text"
                  value={typeof editingProperty.default_value === 'string' ? editingProperty.default_value : JSON.stringify(editingProperty.default_value)}
                  onChange={(e) => {
                    try {
                      const value = e.target.value === '' ? null : JSON.parse(e.target.value)
                      setEditingProperty({ ...editingProperty, default_value: value })
                    } catch {
                      setEditingProperty({ ...editingProperty, default_value: e.target.value })
                    }
                  }}
                  className="input-field"
                  placeholder="Default value (JSON format for complex types)"
                />
              </div>

              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  id="required"
                  checked={editingProperty.required}
                  onChange={(e) => setEditingProperty({ ...editingProperty, required: e.target.checked })}
                  className="w-4 h-4 text-primary-600 bg-white border-slate-300 rounded focus:ring-primary-500"
                />
                <label htmlFor="required" className="text-sm font-medium text-slate-700 dark:text-slate-300">
                  Required Property
                </label>
              </div>

              {/* Validation Options */}
              {(editingProperty.type === 'string' || editingProperty.type === 'integer') && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Choices (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={editingProperty.choices?.join(', ') || ''}
                    onChange={(e) => {
                      const choices = e.target.value.split(',').map(s => s.trim()).filter(s => s)
                      setEditingProperty({ ...editingProperty, choices: choices.length > 0 ? choices : undefined })
                    }}
                    className="input-field"
                    placeholder="Option 1, Option 2, Option 3"
                  />
                </div>
              )}

              {(editingProperty.type === 'integer' || editingProperty.type === 'float') && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                      Min Value
                    </label>
                    <input
                      type="number"
                      value={editingProperty.min_value || ''}
                      onChange={(e) => setEditingProperty({ 
                        ...editingProperty, 
                        min_value: e.target.value ? Number(e.target.value) : undefined 
                      })}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                      Max Value
                    </label>
                    <input
                      type="number"
                      value={editingProperty.max_value || ''}
                      onChange={(e) => setEditingProperty({ 
                        ...editingProperty, 
                        max_value: e.target.value ? Number(e.target.value) : undefined 
                      })}
                      className="input-field"
                    />
                  </div>
                </div>
              )}
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => {
                  setEditingProperty(null)
                  setShowAddForm(false)
                }}
                className="flex-1 btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={saveProperty}
                className="flex-1 btn-primary"
                disabled={!editingProperty.name}
              >
                Save Property
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

const NPCManager: React.FC = () => {
  const [config, setConfig] = useState<NPCConfig | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'schemas' | 'instances'>('schemas')
  const [editingSchema, setEditingSchema] = useState<NPCSchema | null>(null)
  const [editingInstance, setEditingInstance] = useState<NPCInstance | null>(null)
  const [showSchemaForm, setShowSchemaForm] = useState(false)
  const [showInstanceForm, setShowInstanceForm] = useState(false)

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE}/config/npcs`)
      setConfig(response.data)
    } catch (err) {
      console.error('Error loading NPC config:', err)
    } finally {
      setLoading(false)
    }
  }

  const saveConfig = async () => {
    if (!config) return

    try {
      await axios.put(`${API_BASE}/config/npcs`, config)
      alert('Configuration saved successfully!')
    } catch (err) {
      console.error('Error saving config:', err)
      alert('Failed to save configuration')
    }
  }

  const createSchema = () => {
    const newSchema: NPCSchema = {
      schema_id: '',
      name: '',
      description: '',
      core_properties: {
        id: { type: 'string', required: true, description: 'Unique identifier for the NPC' },
        name: { type: 'string', required: true, description: 'Display name of the NPC' },
        description: { type: 'string', required: true, description: 'Brief description of the NPC' }
      },
      custom_properties: [],
      example_properties: []
    }
    setEditingSchema(newSchema)
    setShowSchemaForm(true)
  }

  const editSchema = (schema: NPCSchema) => {
    setEditingSchema({ ...schema })
    setShowSchemaForm(true)
  }

  const saveSchema = () => {
    if (!editingSchema || !config) return

    const updatedSchemas = { ...config.schemas }
    updatedSchemas[editingSchema.schema_id] = editingSchema
    setConfig({ ...config, schemas: updatedSchemas })
    setEditingSchema(null)
    setShowSchemaForm(false)
  }

  const deleteSchema = (schemaId: string) => {
    if (!config) return
    if (!confirm(`Are you sure you want to delete schema "${schemaId}"? This will also delete all NPCs using this schema.`)) return

    const updatedSchemas = { ...config.schemas }
    delete updatedSchemas[schemaId]

    // Remove instances using this schema
    const updatedInstances = { ...config.instances }
    Object.keys(updatedInstances).forEach(instanceId => {
      if (updatedInstances[instanceId].schema_id === schemaId) {
        delete updatedInstances[instanceId]
      }
    })

    setConfig({ schemas: updatedSchemas, instances: updatedInstances })
  }

  const createInstance = (schemaId?: string) => {
    const newInstance: NPCInstance = {
      id: '',
      name: '',
      description: '',
      schema_id: schemaId || Object.keys(config?.schemas || {})[0] || '',
      properties: {},
      relationships: [],
      session_data: {},
      created_at: new Date().toISOString(),
      last_updated: new Date().toISOString()
    }
    setEditingInstance(newInstance)
    setShowInstanceForm(true)
  }

  const editInstance = (instance: NPCInstance) => {
    setEditingInstance({ ...instance })
    setShowInstanceForm(true)
  }

  const saveInstance = () => {
    if (!editingInstance || !config) return

    const updatedInstances = { ...config.instances }
    updatedInstances[editingInstance.id] = editingInstance
    setConfig({ ...config, instances: updatedInstances })
    setEditingInstance(null)
    setShowInstanceForm(false)
  }

  const deleteInstance = (instanceId: string) => {
    if (!config) return
    if (!confirm(`Are you sure you want to delete NPC "${instanceId}"?`)) return

    const updatedInstances = { ...config.instances }
    delete updatedInstances[instanceId]
    setConfig({ ...config, instances: updatedInstances })
  }

  const bulkCreateInstances = async (schemaId: string, count: number) => {
    if (!config) return

    const schema = config.schemas[schemaId]
    if (!schema) return

    const newInstances = { ...config.instances }
    
    for (let i = 0; i < count; i++) {
      const instanceId = `${schemaId}_${Date.now()}_${i}`
      const newInstance: NPCInstance = {
        id: instanceId,
        name: `${schema.name} ${i + 1}`,
        description: `Auto-generated ${schema.name.toLowerCase()}`,
        schema_id: schemaId,
        properties: {},
        relationships: [],
        session_data: {},
        created_at: new Date().toISOString(),
        last_updated: new Date().toISOString()
      }

      // Set default values from schema
      const allProperties = [...schema.custom_properties, ...schema.example_properties]
      allProperties.forEach(prop => {
        if (prop.default_value !== undefined) {
          newInstance.properties[prop.name] = prop.default_value
        }
      })

      newInstances[instanceId] = newInstance
    }

    setConfig({ ...config, instances: newInstances })
    alert(`Created ${count} new NPCs!`)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <span className="ml-3 text-lg font-medium text-slate-600 dark:text-slate-400">Loading NPC configuration...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gradient">NPC Manager</h1>
          <p className="text-slate-600 dark:text-slate-400 mt-2">
            Create schemas and manage NPC instances with custom properties
          </p>
        </div>
        <button
          onClick={saveConfig}
          className="btn-success flex items-center space-x-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <span>Save Configuration</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="glass-card p-6">
        <div className="flex space-x-1 mb-6">
          <button
            onClick={() => setActiveTab('schemas')}
            className={`tab-button ${activeTab === 'schemas' ? 'active' : ''}`}
          >
            🏗️ Schemas ({Object.keys(config?.schemas || {}).length})
          </button>
          <button
            onClick={() => setActiveTab('instances')}
            className={`tab-button ${activeTab === 'instances' ? 'active' : ''}`}
          >
            👥 NPCs ({Object.keys(config?.instances || {}).length})
          </button>
        </div>

        {/* Schema Management */}
        {activeTab === 'schemas' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200">NPC Schemas</h2>
              <button
                onClick={createSchema}
                className="btn-primary"
              >
                Create New Schema
              </button>
            </div>

            {Object.keys(config?.schemas || {}).length === 0 ? (
              <div className="text-center py-12">
                <svg className="w-16 h-16 mx-auto text-slate-400 dark:text-slate-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                <h3 className="text-lg font-medium text-slate-600 dark:text-slate-400 mb-2">No Schemas Created</h3>
                <p className="text-slate-500 dark:text-slate-500 mb-4">Create your first NPC schema to define reusable templates</p>
                <button
                  onClick={createSchema}
                  className="btn-primary"
                >
                  Create Schema
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.values(config?.schemas || {}).map((schema) => (
                  <div key={schema.schema_id} className="card">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-slate-800 dark:text-slate-200">
                        {schema.name}
                      </h3>
                      <span className="badge badge-info">
                        {(schema.custom_properties.length + schema.example_properties.length)} props
                      </span>
                    </div>
                    
                    <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
                      {schema.description}
                    </p>
                    
                    <div className="text-xs text-slate-500 dark:text-slate-500 mb-4">
                      <p>Schema ID: {schema.schema_id}</p>
                      <p>Instances: {Object.values(config?.instances || {}).filter(i => i.schema_id === schema.schema_id).length}</p>
                    </div>
                    
                    <div className="flex space-x-2">
                      <button
                        onClick={() => editSchema(schema)}
                        className="flex-1 btn-secondary text-sm py-2"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => createInstance(schema.schema_id)}
                        className="flex-1 btn-primary text-sm py-2"
                      >
                        Create NPC
                      </button>
                      <button
                        onClick={() => deleteSchema(schema.schema_id)}
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
        )}

        {/* Instance Management */}
        {activeTab === 'instances' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200">NPC Instances</h2>
              <div className="flex space-x-2">
                <button
                  onClick={() => createInstance()}
                  className="btn-primary"
                >
                  Create NPC
                </button>
              </div>
            </div>

            {Object.keys(config?.instances || {}).length === 0 ? (
              <div className="text-center py-12">
                <svg className="w-16 h-16 mx-auto text-slate-400 dark:text-slate-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                <h3 className="text-lg font-medium text-slate-600 dark:text-slate-400 mb-2">No NPCs Created</h3>
                <p className="text-slate-500 dark:text-slate-500 mb-4">Create your first NPC instance</p>
                <button
                  onClick={() => createInstance()}
                  className="btn-primary"
                >
                  Create NPC
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.values(config?.instances || {}).map((instance) => (
                  <div key={instance.id} className="card">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-slate-800 dark:text-slate-200 truncate">
                        {instance.name}
                      </h3>
                      <span className="badge badge-info">
                        {config?.schemas[instance.schema_id]?.name || instance.schema_id}
                      </span>
                    </div>
                    
                    <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
                      {instance.description}
                    </p>
                    
                    <div className="text-xs text-slate-500 dark:text-slate-500 mb-4 space-y-1">
                      <p>ID: {instance.id}</p>
                      <p>Properties: {Object.keys(instance.properties).length}</p>
                      <p>Relationships: {instance.relationships.length}</p>
                    </div>
                    
                    <div className="flex space-x-2">
                      <button
                        onClick={() => editInstance(instance)}
                        className="flex-1 btn-secondary text-sm py-2"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => deleteInstance(instance.id)}
                        className="btn-danger text-sm py-2 px-3"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Bulk Creation */}
            {Object.keys(config?.schemas || {}).length > 0 && (
              <div className="glass-card p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
                <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-200 mb-4">Bulk Create NPCs</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.values(config?.schemas || {}).map((schema) => (
                    <div key={schema.schema_id} className="flex items-center justify-between p-3 bg-white dark:bg-slate-800 rounded-lg">
                      <div>
                        <span className="font-medium text-slate-800 dark:text-slate-200">{schema.name}</span>
                        <p className="text-xs text-slate-500 dark:text-slate-500">
                          {Object.values(config?.instances || {}).filter(i => i.schema_id === schema.schema_id).length} existing
                        </p>
                      </div>
                      <button
                        onClick={() => bulkCreateInstances(schema.schema_id, 5)}
                        className="btn-primary text-sm py-1 px-3"
                      >
                        +5 NPCs
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Schema Form Modal */}
      {showSchemaForm && editingSchema && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="glass-card max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-slate-800 dark:text-slate-200">
                {config?.schemas[editingSchema.schema_id] ? 'Edit Schema' : 'Create Schema'}
              </h3>
              <button
                onClick={() => {
                  setEditingSchema(null)
                  setShowSchemaForm(false)
                }}
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
                    Schema ID
                  </label>
                  <input
                    type="text"
                    value={editingSchema.schema_id}
                    onChange={(e) => setEditingSchema({ ...editingSchema, schema_id: e.target.value })}
                    className="input-field"
                    placeholder="e.g., custom_villager"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Name
                  </label>
                  <input
                    type="text"
                    value={editingSchema.name}
                    onChange={(e) => setEditingSchema({ ...editingSchema, name: e.target.value })}
                    className="input-field"
                    placeholder="e.g., Custom Villager"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Description
                </label>
                <textarea
                  value={editingSchema.description}
                  onChange={(e) => setEditingSchema({ ...editingSchema, description: e.target.value })}
                  className="input-field"
                  rows={3}
                  placeholder="Describe this NPC type..."
                />
              </div>

              <PropertyEditor
                properties={editingSchema.custom_properties}
                onChange={(properties) => setEditingSchema({ ...editingSchema, custom_properties: properties })}
                title="Custom Properties"
              />

              <PropertyEditor
                properties={editingSchema.example_properties}
                onChange={(properties) => setEditingSchema({ ...editingSchema, example_properties: properties })}
                title="Example Properties (users can modify these)"
              />
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => {
                  setEditingSchema(null)
                  setShowSchemaForm(false)
                }}
                className="flex-1 btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={saveSchema}
                className="flex-1 btn-primary"
                disabled={!editingSchema.schema_id || !editingSchema.name}
              >
                Save Schema
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Instance Form Modal */}
      {showInstanceForm && editingInstance && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="glass-card max-w-3xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-slate-800 dark:text-slate-200">
                {config?.instances[editingInstance.id] ? 'Edit NPC' : 'Create NPC'}
              </h3>
              <button
                onClick={() => {
                  setEditingInstance(null)
                  setShowInstanceForm(false)
                }}
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
                    NPC ID
                  </label>
                  <input
                    type="text"
                    value={editingInstance.id}
                    onChange={(e) => setEditingInstance({ ...editingInstance, id: e.target.value })}
                    className="input-field"
                    placeholder="e.g., npc_001"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Schema
                  </label>
                  <select
                    value={editingInstance.schema_id}
                    onChange={(e) => setEditingInstance({ ...editingInstance, schema_id: e.target.value })}
                    className="select-field"
                  >
                    {Object.values(config?.schemas || {}).map((schema) => (
                      <option key={schema.schema_id} value={schema.schema_id}>
                        {schema.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Name
                </label>
                <input
                  type="text"
                  value={editingInstance.name}
                  onChange={(e) => setEditingInstance({ ...editingInstance, name: e.target.value })}
                  className="input-field"
                  placeholder="e.g., Gareth the Trader"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Description
                </label>
                <textarea
                  value={editingInstance.description}
                  onChange={(e) => setEditingInstance({ ...editingInstance, description: e.target.value })}
                  className="input-field"
                  rows={3}
                  placeholder="Describe this specific NPC..."
                />
              </div>

              {/* Property Values */}
              {editingInstance.schema_id && config?.schemas[editingInstance.schema_id] && (
                <div>
                  <h4 className="text-lg font-semibold text-slate-800 dark:text-slate-200 mb-4">Properties</h4>
                  <div className="space-y-4">
                    {[
                      ...config.schemas[editingInstance.schema_id].custom_properties,
                      ...config.schemas[editingInstance.schema_id].example_properties
                    ].map((prop) => (
                      <div key={prop.name}>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                          {prop.name} ({prop.type})
                          {prop.required && <span className="text-red-500 ml-1">*</span>}
                        </label>
                        <input
                          type={prop.type === 'integer' ? 'number' : prop.type === 'boolean' ? 'checkbox' : 'text'}
                          value={
                            prop.type === 'boolean' 
                              ? editingInstance.properties[prop.name] || false
                              : typeof editingInstance.properties[prop.name] === 'object'
                                ? JSON.stringify(editingInstance.properties[prop.name])
                                : editingInstance.properties[prop.name] || ''
                          }
                          checked={prop.type === 'boolean' ? editingInstance.properties[prop.name] || false : undefined}
                          onChange={(e) => {
                            let value: any = e.target.value
                            if (prop.type === 'integer') value = parseInt(value) || 0
                            if (prop.type === 'float') value = parseFloat(value) || 0
                            if (prop.type === 'boolean') value = e.target.checked
                            if (prop.type === 'list' || prop.type === 'dict') {
                              try {
                                value = JSON.parse(value)
                              } catch {
                                // Keep as string if invalid JSON
                              }
                            }
                            
                            setEditingInstance({
                              ...editingInstance,
                              properties: {
                                ...editingInstance.properties,
                                [prop.name]: value
                              }
                            })
                          }}
                          className={prop.type === 'boolean' ? 'w-4 h-4 text-primary-600' : 'input-field'}
                          placeholder={prop.description}
                        />
                        {prop.choices && (
                          <div className="text-xs text-slate-500 dark:text-slate-500 mt-1">
                            Options: {prop.choices.join(', ')}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => {
                  setEditingInstance(null)
                  setShowInstanceForm(false)
                }}
                className="flex-1 btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={saveInstance}
                className="flex-1 btn-primary"
                disabled={!editingInstance.id || !editingInstance.name}
              >
                Save NPC
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default NPCManager 