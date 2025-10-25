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
