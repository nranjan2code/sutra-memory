"""
Schema constants for Sutra storage.

This module mirrors the schema defined in packages/sutra-storage/src/schema.rs,
providing Python constants for concept types and association types used in
user storage and domain storage.
"""

from enum import Enum


class ConceptType(str, Enum):
    """
    Types of concepts stored in Sutra storage.
    
    - Domain concepts: Domain-specific knowledge (medical, legal, financial)
    - User concepts: Users, sessions, conversations, messages, etc.
    """
    
    # Domain knowledge (stored in domain-storage.dat)
    DOMAIN_CONCEPT = "domain_concept"
    
    # User management (stored in user-storage.dat)
    USER = "user"
    SESSION = "session"
    ORGANIZATION = "organization"
    ROLE = "role"
    PERMISSION = "permission"
    
    # Conversations (stored in user-storage.dat)
    CONVERSATION = "conversation"
    USER_MESSAGE = "user_message"
    ASSISTANT_MESSAGE = "assistant_message"
    SPACE = "space"
    
    # Audit logging
    AUDIT_LOG = "audit_log"


class AssociationType(str, Enum):
    """
    Types of associations between concepts in the knowledge graph.
    
    Associations are directed edges that link concepts with semantic meaning.
    """
    
    # Domain associations (original behavior)
    SEMANTIC = "semantic"
    CAUSAL = "causal"
    TEMPORAL = "temporal"
    HIERARCHICAL = "hierarchical"
    COMPOSITIONAL = "compositional"
    
    # User/organization associations
    HAS_SESSION = "has_session"                  # User -> Session
    BELONGS_TO_ORGANIZATION = "belongs_to_organization"  # User -> Organization
    HAS_ROLE = "has_role"                        # User -> Role
    HAS_PERMISSION = "has_permission"            # Role -> Permission
    
    # Conversation associations
    OWNS_CONVERSATION = "owns_conversation"      # User -> Conversation
    CONTAINS_CONVERSATION = "contains_conversation"  # Space -> Conversation
    HAS_MESSAGE = "has_message"                  # Conversation -> Message
    AUTHORED_BY = "authored_by"                  # Message -> User
    IN_SPACE = "in_space"                        # Conversation -> Space
    
    # Cross-storage associations
    USES_KNOWLEDGE_BASE = "uses_knowledge_base"  # Conversation -> DomainConcept
    
    # Audit trail
    TRIGGERED_BY = "triggered_by"                # AuditLog -> User
    RELATES_TO = "relates_to"                    # AuditLog -> (any concept)


# Metadata field constants
class MetadataField:
    """Standard metadata field names for consistent querying."""
    
    # Common fields
    TYPE = "type"
    ORGANIZATION_ID = "organization_id"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    ACTIVE = "active"
    
    # User fields
    EMAIL = "email"
    PASSWORD_HASH = "password_hash"
    FULL_NAME = "full_name"
    ROLE = "role"
    LAST_LOGIN = "last_login"
    
    # Session fields
    USER_ID = "user_id"
    SESSION_TOKEN = "session_token"
    EXPIRES_AT = "expires_at"
    
    # Conversation fields
    SPACE_ID = "space_id"
    DOMAIN_STORAGE = "domain_storage"
    MESSAGE_COUNT = "message_count"
    TITLE = "title"
    STARRED = "starred"
    TAGS = "tags"
    
    # Message fields
    CONVERSATION_ID = "conversation_id"
    TIMESTAMP = "timestamp"
    REASONING_DEPTH = "reasoning_depth"
    CONCEPTS_USED = "concepts_used"
    CONFIDENCE = "confidence"
    REASONING_PATHS = "reasoning_paths"


# Content templates for consistent formatting
class ContentTemplate:
    """Templates for generating concept content strings."""
    
    @staticmethod
    def user(email: str) -> str:
        """Format user concept content."""
        return f"User {email}"
    
    @staticmethod
    def session(email: str) -> str:
        """Format session concept content."""
        return f"Session for {email}"
    
    @staticmethod
    def conversation(title: str = "New conversation") -> str:
        """Format conversation concept content."""
        return title
    
    @staticmethod
    def user_message(content: str) -> str:
        """Format user message concept content."""
        return content
    
    @staticmethod
    def assistant_message(content: str) -> str:
        """Format assistant message concept content."""
        return content
    
    @staticmethod
    def space(name: str) -> str:
        """Format space concept content."""
        return f"Space: {name}"
    
    @staticmethod
    def organization(name: str) -> str:
        """Format organization concept content."""
        return f"Organization: {name}"
    
    @staticmethod
    def role(name: str) -> str:
        """Format role concept content."""
        return f"Role: {name}"
    
    @staticmethod
    def audit_log(action: str, entity_type: str) -> str:
        """Format audit log concept content."""
        return f"Audit: {action} on {entity_type}"
