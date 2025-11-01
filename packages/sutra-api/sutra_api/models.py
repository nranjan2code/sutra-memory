"""
Pydantic models for API request and response schemas.

Defines all data models used for API validation and documentation.
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class AssociationType(str, Enum):
    """Types of associations between concepts."""

    SEMANTIC = "semantic"
    CAUSAL = "causal"
    TEMPORAL = "temporal"
    HIERARCHICAL = "hierarchical"
    COMPOSITIONAL = "compositional"


class LearnRequest(BaseModel):
    """Request model for learning new knowledge."""

    content: str = Field(..., description="Knowledge content to learn")
    source: Optional[str] = Field(None, description="Source of the knowledge")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")


class LearnResponse(BaseModel):
    """Response model for learning operations."""

    concept_id: str = Field(..., description="ID of the created/updated concept")
    message: str = Field(..., description="Success message")
    concepts_created: int = Field(..., description="Number of concepts created")
    associations_created: int = Field(..., description="Number of associations created")


class BatchLearnRequest(BaseModel):
    """Request model for batch learning."""

    items: List[LearnRequest] = Field(
        ..., description="List of knowledge items to learn"
    )


class BatchLearnResponse(BaseModel):
    """Response model for batch learning operations."""

    concept_ids: List[str] = Field(..., description="IDs of all created concepts")
    total_concepts: int = Field(..., description="Total concepts created")
    total_associations: int = Field(..., description="Total associations created")
    message: str = Field(..., description="Success message")


class ReasonRequest(BaseModel):
    """Request model for reasoning queries."""

    query: str = Field(..., description="Question or reasoning query")
    max_steps: int = Field(
        default=3, ge=1, le=10, description="Maximum reasoning depth"
    )
    num_paths: int = Field(
        default=3, ge=1, le=10, description="Number of reasoning paths to explore"
    )
    threshold: float = Field(
        default=0.3, ge=0.0, le=1.0, description="Minimum confidence threshold"
    )


class ReasoningPath(BaseModel):
    """A single reasoning path through the knowledge graph."""

    concepts: List[str] = Field(..., description="Concept IDs in the path")
    confidence: float = Field(..., description="Path confidence score")
    explanation: str = Field(..., description="Human-readable explanation of the path")


class ReasonResponse(BaseModel):
    """Response model for reasoning operations."""

    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Reasoning result/answer")
    confidence: float = Field(..., description="Overall confidence score")
    paths: List[ReasoningPath] = Field(..., description="Reasoning paths explored")
    concepts_accessed: int = Field(..., description="Number of concepts accessed")


class SemanticSearchRequest(BaseModel):
    """Request model for semantic similarity search."""

    query: str = Field(..., description="Search query")
    top_k: int = Field(
        default=5, ge=1, le=100, description="Number of results to return"
    )
    threshold: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Minimum similarity threshold"
    )


class SearchResult(BaseModel):
    """A single search result."""

    concept_id: str = Field(..., description="Concept ID")
    content: str = Field(..., description="Concept content")
    similarity: float = Field(..., description="Similarity score")
    strength: float = Field(..., description="Concept strength")


class SemanticSearchResponse(BaseModel):
    """Response model for semantic search operations."""

    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="Search results")
    total_found: int = Field(..., description="Total number of results found")


class ConceptDetail(BaseModel):
    """Detailed information about a concept."""

    id: str = Field(..., description="Concept ID")
    content: str = Field(..., description="Concept content")
    strength: float = Field(..., description="Concept strength (1.0-10.0)")
    access_count: int = Field(..., description="Number of times accessed")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    source: Optional[str] = Field(None, description="Source of knowledge")
    associations: List[str] = Field(..., description="IDs of associated concepts")


class SystemStats(BaseModel):
    """System statistics and metrics."""

    total_concepts: int = Field(..., description="Total number of concepts")
    total_associations: int = Field(..., description="Total number of associations")
    total_embeddings: int = Field(..., description="Total number of embeddings")
    embedding_provider: str = Field(..., description="Active embedding provider")
    embedding_dimension: int = Field(..., description="Embedding dimensionality")
    average_strength: float = Field(..., description="Average concept strength")
    memory_usage_mb: Optional[float] = Field(
        None, description="Approximate memory usage in MB"
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    concepts_loaded: int = Field(..., description="Number of concepts loaded")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


class EditionLimitsResponse(BaseModel):
    """Edition-specific limits."""
    
    learn_per_min: int = Field(..., description="Learn API calls per minute")
    reason_per_min: int = Field(..., description="Reason API calls per minute")
    max_concepts: int = Field(..., description="Maximum number of concepts")
    max_dataset_gb: int = Field(..., description="Maximum dataset size in GB")
    ingest_workers: int = Field(..., description="Number of parallel ingest workers")


class EditionFeaturesResponse(BaseModel):
    """Edition-specific features."""
    
    ha_enabled: bool = Field(..., description="High availability enabled")
    grid_enabled: bool = Field(..., description="Grid orchestration enabled")
    observability_enabled: bool = Field(..., description="Event observability enabled")
    multi_node: bool = Field(..., description="Multi-node support enabled")


class EditionResponse(BaseModel):
    """Response model for edition information."""
    
    edition: str = Field(..., description="Current edition (simple/community/enterprise)")
    limits: EditionLimitsResponse = Field(..., description="Edition-specific limits")
    features: EditionFeaturesResponse = Field(..., description="Edition-specific features")
    license_valid: bool = Field(..., description="Whether license is valid")
    license_expires: Optional[str] = Field(None, description="License expiration date (ISO 8601)")
    upgrade_url: str = Field(..., description="URL to upgrade edition")


# ======================== SEMANTIC QUERY MODELS ========================

class SemanticFilterRequest(BaseModel):
    """Semantic filter for concept queries."""
    
    semantic_types: Optional[List[str]] = Field(None, description="Semantic types to filter by")
    domains: Optional[List[str]] = Field(None, description="Domain keywords to filter by")
    temporal: Optional[Dict[str, str]] = Field(None, description="Temporal constraints")
    causal_only: bool = Field(False, description="Only include causal relationships")
    min_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Minimum confidence threshold")
    required_terms: Optional[List[str]] = Field(None, description="Required terms in content")


class SemanticPathRequest(BaseModel):
    """Request for semantic pathfinding."""
    
    start_query: str = Field(..., description="Starting concept (query or ID)")
    end_query: str = Field(..., description="Ending concept (query or ID)")
    max_depth: int = Field(5, ge=1, le=10, description="Maximum path depth")
    filter: Optional[SemanticFilterRequest] = Field(None, description="Optional semantic filter")


class TemporalChainRequest(BaseModel):
    """Request for temporal chain discovery."""
    
    start_query: str = Field(..., description="Starting concept")
    end_query: str = Field(..., description="Ending concept")
    max_depth: int = Field(10, ge=1, le=20, description="Maximum chain depth")
    after: Optional[str] = Field(None, description="Filter events after date (ISO 8601)")
    before: Optional[str] = Field(None, description="Filter events before date (ISO 8601)")


class CausalChainRequest(BaseModel):
    """Request for causal chain discovery."""
    
    start_query: str = Field(..., description="Starting concept")
    end_query: str = Field(..., description="Ending concept")
    max_depth: int = Field(5, ge=1, le=10, description="Maximum chain depth")


class ContradictionRequest(BaseModel):
    """Request for contradiction detection."""
    
    query: str = Field(..., description="Concept to check for contradictions")
    max_depth: int = Field(3, ge=1, le=5, description="Search depth for contradictions")


class SemanticQueryRequest(BaseModel):
    """Request for semantic domain query."""
    
    filter: SemanticFilterRequest = Field(..., description="Semantic filter constraints")
    max_results: int = Field(100, ge=1, le=1000, description="Maximum number of results")


class SemanticPathResponse(BaseModel):
    """Response for semantic pathfinding."""
    
    start_query: str = Field(..., description="Starting concept")
    end_query: str = Field(..., description="Ending concept")
    paths: List[Dict] = Field(..., description="Semantic paths found")
    execution_time_ms: float = Field(..., description="Query execution time")
    filter_applied: bool = Field(..., description="Whether filter was applied")


class TemporalChainResponse(BaseModel):
    """Response for temporal chain discovery."""
    
    start_query: str = Field(..., description="Starting concept")
    end_query: str = Field(..., description="Ending concept")
    chains: List[Dict] = Field(..., description="Temporal chains found")
    temporal_constraints: Dict[str, Optional[str]] = Field(..., description="Applied temporal constraints")
    execution_time_ms: float = Field(..., description="Query execution time")


class CausalChainResponse(BaseModel):
    """Response for causal chain discovery."""
    
    start_query: str = Field(..., description="Starting concept")
    end_query: str = Field(..., description="Ending concept")
    chains: List[Dict] = Field(..., description="Causal chains found")
    execution_time_ms: float = Field(..., description="Query execution time")


class ContradictionResponse(BaseModel):
    """Response for contradiction detection."""
    
    query: str = Field(..., description="Query concept")
    concept_id: str = Field(..., description="Resolved concept ID")
    contradictions: List[Dict] = Field(..., description="Found contradictions")
    count: int = Field(..., description="Number of contradictions found")
    execution_time_ms: float = Field(..., description="Query execution time")


class SemanticQueryResponse(BaseModel):
    """Response for semantic query."""
    
    filter: Dict = Field(..., description="Applied filter")
    results: List[Dict] = Field(..., description="Matching concepts")
    count: int = Field(..., description="Number of results")
    execution_time_ms: float = Field(..., description="Query execution time")


# =============================================================================
# Authentication Models
# =============================================================================


class RegisterRequest(BaseModel):
    """Request model for user registration."""
    
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    organization: str = Field(..., description="Organization ID")
    full_name: Optional[str] = Field(None, description="User's full name")
    role: str = Field(default="user", description="User role (user, admin)")


class LoginRequest(BaseModel):
    """Request model for user login."""
    
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class LoginResponse(BaseModel):
    """Response model for successful login."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: "UserResponse" = Field(..., description="User information")


class UserResponse(BaseModel):
    """Response model for user information."""
    
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    organization: str = Field(..., description="Organization ID")
    role: str = Field(..., description="User role")
    full_name: Optional[str] = Field(None, description="User's full name")
    created_at: Optional[str] = Field(None, description="Account creation timestamp")
    last_login: Optional[str] = Field(None, description="Last login timestamp")
    
    class Config:
        # Allow extra fields but ignore them
        extra = "ignore"


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    
    refresh_token: str = Field(..., description="Refresh token")


class LogoutResponse(BaseModel):
    """Response model for logout."""
    
    message: str = Field(..., description="Logout confirmation message")
    success: bool = Field(default=True, description="Logout success status")


class UpdateUserRequest(BaseModel):
    """Request model for updating user profile."""
    
    email: Optional[str] = Field(None, description="New email address")
    full_name: Optional[str] = Field(None, description="New full name")
    organization: Optional[str] = Field(None, description="New organization")


class ChangePasswordRequest(BaseModel):
    """Request model for changing password."""
    
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")


class ForgotPasswordRequest(BaseModel):
    """Request model for forgot password."""
    
    email: str = Field(..., description="User email address")


class ResetPasswordRequest(BaseModel):
    """Request model for password reset."""
    
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")


class PasswordResetResponse(BaseModel):
    """Response model for password reset request."""
    
    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Request success status")


class UserListResponse(BaseModel):
    """Response model for user list."""
    
    users: list = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")


class DeleteUserResponse(BaseModel):
    """Response model for user deletion."""
    
    message: str = Field(..., description="Deletion confirmation message")
    success: bool = Field(default=True, description="Deletion success status")
    user_id: str = Field(..., description="Deleted user ID")


# Conversation Models
class CreateConversationRequest(BaseModel):
    """Request model for creating a new conversation."""
    
    title: Optional[str] = Field(None, description="Conversation title")
    description: Optional[str] = Field(None, description="Conversation description")
    space_id: Optional[str] = Field(None, description="Space to create conversation in")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")


class MessageResponse(BaseModel):
    """Response model for a conversation message."""
    
    id: str = Field(..., description="Message ID")
    conversation_id: str = Field(..., description="Conversation ID")
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    created_at: str = Field(..., description="Message creation timestamp")
    metadata: Optional[Dict[str, str]] = Field(None, description="Message metadata")


class ConversationResponse(BaseModel):
    """Response model for conversation details."""
    
    id: str = Field(..., description="Conversation ID")
    title: Optional[str] = Field(None, description="Conversation title")
    description: Optional[str] = Field(None, description="Conversation description")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    message_count: int = Field(default=0, description="Number of messages")
    space_id: Optional[str] = Field(None, description="Space ID if in a space")
    metadata: Optional[Dict[str, str]] = Field(None, description="Conversation metadata")


class SendMessageRequest(BaseModel):
    """Request model for sending a message in a conversation."""
    
    content: str = Field(..., description="Message content")
    role: Optional[str] = Field(default="user", description="Message role")
    stream: Optional[bool] = Field(default=False, description="Stream response")
    metadata: Optional[Dict[str, str]] = Field(None, description="Message metadata")


class SendMessageResponse(BaseModel):
    """Response model for sending a message."""
    
    user_message: MessageResponse = Field(..., description="The user message")
    assistant_message: MessageResponse = Field(..., description="The assistant response")
    conversation_id: str = Field(..., description="Conversation ID")


class UpdateConversationRequest(BaseModel):
    """Request model for updating a conversation."""
    
    title: Optional[str] = Field(None, description="Updated title")
    description: Optional[str] = Field(None, description="Updated description")
    metadata: Optional[Dict[str, str]] = Field(None, description="Updated metadata")


class ListConversationsRequest(BaseModel):
    """Request model for listing conversations."""
    
    space_id: Optional[str] = Field(None, description="Filter by space ID")
    limit: Optional[int] = Field(default=50, description="Maximum number of conversations")
    offset: Optional[int] = Field(default=0, description="Pagination offset")


class ListConversationsResponse(BaseModel):
    """Response model for listing conversations."""
    
    conversations: List[ConversationResponse] = Field(..., description="List of conversations")
    total: int = Field(..., description="Total number of conversations")
    limit: int = Field(..., description="Requested limit")
    offset: int = Field(..., description="Requested offset")


class LoadMessagesRequest(BaseModel):
    """Request model for loading conversation messages."""
    
    limit: Optional[int] = Field(default=50, description="Maximum number of messages")
    before: Optional[str] = Field(None, description="Load messages before this message ID")
    after: Optional[str] = Field(None, description="Load messages after this message ID")


class LoadMessagesResponse(BaseModel):
    """Response model for loading conversation messages."""
    
    messages: List[MessageResponse] = Field(..., description="List of messages")
    conversation_id: str = Field(..., description="Conversation ID")
    total: int = Field(..., description="Total number of messages in conversation")
    has_more: bool = Field(..., description="Whether more messages are available")


# Space Models
class CreateSpaceRequest(BaseModel):
    """Request model for creating a new space."""
    
    name: str = Field(..., description="Space name")
    description: Optional[str] = Field(None, description="Space description")
    visibility: Optional[str] = Field(default="private", description="Space visibility (public, private)")
    metadata: Optional[Dict[str, str]] = Field(None, description="Space metadata")


class UpdateSpaceRequest(BaseModel):
    """Request model for updating a space."""
    
    name: Optional[str] = Field(None, description="Updated name")
    description: Optional[str] = Field(None, description="Updated description")
    visibility: Optional[str] = Field(None, description="Updated visibility")
    metadata: Optional[Dict[str, str]] = Field(None, description="Updated metadata")


class AddMemberRequest(BaseModel):
    """Request model for adding a member to a space."""
    
    user_id: str = Field(..., description="User ID to add")
    role: Optional[str] = Field(default="member", description="Member role (admin, member, viewer)")


class UpdateMemberRoleRequest(BaseModel):
    """Request model for updating a member's role in a space."""
    
    role: str = Field(..., description="New member role")


class RemoveMemberRequest(BaseModel):
    """Request model for removing a member from a space."""
    
    user_id: str = Field(..., description="User ID to remove")


class SpaceMemberResponse(BaseModel):
    """Response model for space member details."""
    
    user_id: str = Field(..., description="User ID")
    role: str = Field(..., description="Member role")
    joined_at: str = Field(..., description="Join timestamp")
    username: Optional[str] = Field(None, description="Username")
    email: Optional[str] = Field(None, description="User email")


class SpaceResponse(BaseModel):
    """Response model for space details."""
    
    id: str = Field(..., description="Space ID")
    name: str = Field(..., description="Space name")
    description: Optional[str] = Field(None, description="Space description")
    visibility: str = Field(..., description="Space visibility")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    member_count: int = Field(default=0, description="Number of members")
    owner_id: str = Field(..., description="Space owner ID")
    metadata: Optional[Dict[str, str]] = Field(None, description="Space metadata")


class SpaceListResponse(BaseModel):
    """Response model for listing spaces."""
    
    spaces: List[SpaceResponse] = Field(..., description="List of spaces")
    total: int = Field(..., description="Total number of spaces")
    limit: int = Field(..., description="Requested limit")
    offset: int = Field(..., description="Requested offset")


class SpaceMemberListResponse(BaseModel):
    """Response model for listing space members."""
    
    members: List[SpaceMemberResponse] = Field(..., description="List of members")
    space_id: str = Field(..., description="Space ID")
    total: int = Field(..., description="Total number of members")


class SpaceActionResponse(BaseModel):
    """Response model for space actions."""
    
    success: bool = Field(..., description="Action success status")
    message: str = Field(..., description="Action message")
    space_id: str = Field(..., description="Space ID")


# Graph Models
class GraphNode(BaseModel):
    """Response model for graph node."""
    
    id: str = Field(..., description="Node ID")
    label: str = Field(..., description="Node label")
    type: Optional[str] = Field(None, description="Node type")
    properties: Optional[Dict[str, str]] = Field(None, description="Node properties")


class GraphEdge(BaseModel):
    """Response model for graph edge."""
    
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    label: Optional[str] = Field(None, description="Edge label")
    type: Optional[str] = Field(None, description="Edge type")
    weight: Optional[float] = Field(None, description="Edge weight")


class GraphData(BaseModel):
    """Response model for graph data."""
    
    nodes: List[GraphNode] = Field(..., description="Graph nodes")
    edges: List[GraphEdge] = Field(..., description="Graph edges")


class MessageGraphRequest(BaseModel):
    """Request model for message graph."""
    
    conversation_id: str = Field(..., description="Conversation ID")
    max_nodes: Optional[int] = Field(default=50, description="Maximum nodes")
    include_context: Optional[bool] = Field(default=True, description="Include context")


class MessageGraphResponse(BaseModel):
    """Response model for message graph."""
    
    graph: GraphData = Field(..., description="Graph data")
    conversation_id: str = Field(..., description="Conversation ID")
    node_count: int = Field(..., description="Number of nodes")
    edge_count: int = Field(..., description="Number of edges")


class ConceptGraphRequest(BaseModel):
    """Request model for concept graph."""
    
    concept_ids: List[str] = Field(..., description="Concept IDs to include")
    max_depth: Optional[int] = Field(default=2, description="Maximum depth")
    include_associations: Optional[bool] = Field(default=True, description="Include associations")


class ConceptGraphResponse(BaseModel):
    """Response model for concept graph."""
    
    graph: GraphData = Field(..., description="Graph data")
    concept_count: int = Field(..., description="Number of concepts")
    association_count: int = Field(..., description="Number of associations")


class QueryGraphRequest(BaseModel):
    """Request model for query graph."""
    
    query: str = Field(..., description="Graph query")
    max_nodes: Optional[int] = Field(default=100, description="Maximum nodes")
    filters: Optional[Dict[str, str]] = Field(None, description="Graph filters")


class QueryGraphResponse(BaseModel):
    """Response model for query graph."""
    
    graph: GraphData = Field(..., description="Graph data")
    query: str = Field(..., description="Original query")
    execution_time_ms: float = Field(..., description="Execution time in milliseconds")


class GraphStatisticsResponse(BaseModel):
    """Response model for graph statistics."""
    
    total_nodes: int = Field(..., description="Total number of nodes")
    total_edges: int = Field(..., description="Total number of edges")
    node_types: Dict[str, int] = Field(..., description="Node types and counts")
    edge_types: Dict[str, int] = Field(..., description="Edge types and counts")


