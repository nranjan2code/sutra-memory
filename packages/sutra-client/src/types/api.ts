export interface ReasoningPath {
  concepts: string[]
  confidence: number
  explanation: string
}

export interface ReasoningResult {
  query: string
  answer: string
  confidence: number
  paths: ReasoningPath[]
  concepts_accessed: number
}

export interface LearnResponse {
  concept_id: string
  message: string
  concepts_created: number
  associations_created: number
}

export interface MetricsResponse {
  total_concepts: number
  total_associations: number
  total_embeddings: number
  embedding_provider: string
  embedding_dimension: number
  average_strength: number
  memory_usage_mb: number | null
}

export interface HealthResponse {
  status: string
  version: string
  uptime_seconds: number
  concepts_loaded: number
}

export interface EditionLimits {
  learn_per_min: number
  reason_per_min: number
  max_concepts: number
  max_dataset_gb: number
  ingest_workers: number
}

export interface EditionFeatures {
  ha_enabled: boolean
  grid_enabled: boolean
  observability_enabled: boolean
  multi_node: boolean
}

export interface EditionResponse {
  edition: 'simple' | 'community' | 'enterprise'
  limits: EditionLimits
  features: EditionFeatures
  license_valid: boolean
  license_expires: string | null
  upgrade_url: string
}

// Conversation & Message Types
export interface Message {
  id: string
  conversation_id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: string
  metadata?: {
    reasoning_paths?: ReasoningPath[]
    concepts_used?: string[]
    confidence?: number
  }
}

export interface Conversation {
  id: string
  user_id: string
  space_id: string
  organization: string
  domain_storage: string
  title: string
  message_count: number
  created_at: string
  updated_at: string
  metadata?: {
    starred?: boolean
    tags?: string[]
    last_message?: string
  }
}

export interface CreateConversationRequest {
  space_id: string
  domain_storage?: string
  title?: string
}

export interface CreateConversationResponse {
  conversation: Conversation
}

export interface ListConversationsResponse {
  conversations: Conversation[]
  total: number
  page: number
  page_size: number
}

export interface LoadMessagesResponse {
  messages: Message[]
  total: number
  has_more: boolean
}

export interface SendMessageRequest {
  message: string
}

export interface SendMessageResponse {
  user_message: Message
  assistant_message: Message
}

// Space & Member Types
export interface Space {
  space_id: string
  name: string
  description: string
  domain_storage: string
  icon: string
  color: string
  conversation_count: number
  member_count: number
  created_at: string
  updated_at?: string
  created_by?: string
  role: 'admin' | 'write' | 'read'
  active: boolean
}

export interface SpaceMember {
  user_id: string
  email: string
  full_name?: string
  role: 'admin' | 'write' | 'read'
  added_at: string
  added_by?: string
}

export interface CreateSpaceRequest {
  name: string
  domain_storage: string
  description?: string
  icon?: string
  color?: string
}

export interface UpdateSpaceRequest {
  name?: string
  description?: string
  icon?: string
  color?: string
}

export interface AddMemberRequest {
  user_id: string
  role: 'admin' | 'write' | 'read'
}

export interface UpdateMemberRoleRequest {
  user_id: string
  new_role: 'admin' | 'write' | 'read'
}

export interface SpaceResponse {
  space_id: string
  name: string
  description: string
  domain_storage: string
  icon: string
  color: string
  conversation_count: number
  member_count: number
  created_at: string
  updated_at?: string
  created_by?: string
  role: string
  active: boolean
}

export interface SpaceListResponse {
  spaces: Space[]
  total: number
}

export interface SpaceMemberListResponse {
  members: SpaceMember[]
  total: number
}

export interface SpaceActionResponse {
  message: string
  space_id?: string
  user_id?: string
  role?: string
}

// ========== Graph API Types ==========

export interface GraphNode {
  id: string
  content: string
  type: string
  metadata?: Record<string, unknown>
  confidence?: number
  created_at?: string
}

export interface GraphEdge {
  source: string
  target: string
  type: string
  strength?: number
  metadata?: Record<string, unknown>
}

export interface ReasoningPathAssociation {
  source: string
  target: string
  type: string
}

export interface ReasoningPathData {
  path_id: string
  concepts: string[]
  associations: ReasoningPathAssociation[]
  confidence: number
  reasoning_steps: string[]
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  concept_count: number
  edge_count: number
}

export interface MessageGraphRequest {
  message_id: string
  conversation_id: string
  max_depth?: number
}

export interface MessageGraphResponse {
  message_id: string
  graph: GraphData
  reasoning_paths: unknown[]
  confidence: number
}

export interface ConceptGraphRequest {
  concept_id: string
  domain_storage: string
  depth?: number
  max_nodes?: number
}

export interface ConceptGraphResponse {
  concept_id: string
  graph: GraphData
  depth: number
}

export interface QueryGraphRequest {
  query: string
  domain_storage: string
  max_paths?: number
}

export interface QueryGraphResponse {
  query: string
  paths: ReasoningPathData[]
  path_count: number
}

export interface GraphStatisticsResponse {
  total_concepts: number
  total_associations: number
  storage_name: string
  timestamp: string
}
