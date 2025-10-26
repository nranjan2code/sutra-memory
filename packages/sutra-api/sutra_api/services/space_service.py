"""
Space Management Service.

Handles space (workspace) creation, updates, member management, and permissions.
Spaces organize conversations by project, department, or domain.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from ..schema import (
    AssociationType,
    ConceptType,
    ContentTemplate,
    MetadataField,
)

logger = logging.getLogger(__name__)


class SpaceService:
    """
    Space management service using Sutra storage.
    
    Spaces organize conversations into logical groupings (projects, departments,
    domains). Each space has:
    - Name and description
    - Associated domain storage (which knowledge base to query)
    - Members with roles (admin, write, read)
    - Conversations scoped to the space
    
    All space data is stored in user-storage.dat with associations for
    relationships (space -> conversations, user -> space with role metadata).
    """
    
    def __init__(self, user_storage_client):
        """
        Initialize space service with storage client.
        
        Args:
            user_storage_client: StorageClient connected to user-storage.dat
        """
        self.storage = user_storage_client
        logger.info("SpaceService initialized with storage client")
    
    async def create_space(
        self,
        name: str,
        organization_id: str,
        creator_user_id: str,
        domain_storage: str,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None
    ) -> Dict:
        """
        Create a new space.
        
        Args:
            name: Space name (e.g., "Surgery Protocols", "Legal Research")
            organization_id: Organization ID (for multi-tenancy)
            creator_user_id: User ID of space creator
            domain_storage: Name of domain storage to query (e.g., "domain_surgery")
            description: Optional space description
            icon: Optional icon name (e.g., "medical", "legal")
            color: Optional color hex code (e.g., "#3b82f6")
        
        Returns:
            Dict with space_id and space details
        
        Raises:
            ValueError: If validation fails or storage errors occur
        """
        # Validate inputs
        if not name or len(name.strip()) == 0:
            raise ValueError("Space name cannot be empty")
        
        if len(name) > 100:
            raise ValueError("Space name too long (max 100 characters)")
        
        if not domain_storage:
            raise ValueError("Domain storage must be specified")
        
        try:
            # Create space concept
            timestamp = datetime.utcnow().isoformat()
            
            space_concept = self.storage.learn_concept(
                content=ContentTemplate.space(name),
                semantic_patterns=["Space", name],
                metadata={
                    MetadataField.TYPE: ConceptType.SPACE.value,
                    MetadataField.ORGANIZATION_ID: organization_id,
                    "name": name,
                    "description": description or "",
                    "domain_storage": domain_storage,
                    "icon": icon or "folder",
                    "color": color or "#6b7280",
                    "conversation_count": 0,
                    "member_count": 1,  # Creator
                    "created_by": creator_user_id,
                    MetadataField.CREATED_AT: timestamp,
                    MetadataField.UPDATED_AT: timestamp,
                    MetadataField.ACTIVE: True,
                }
            )
            
            space_id = space_concept["concept_id"]
            logger.info(f"Created space: {space_id} (name={name}, org={organization_id})")
            
            # Create creator membership with admin role
            await self._add_member_internal(
                space_id=space_id,
                user_id=creator_user_id,
                role="admin",
                added_by=creator_user_id,
                organization_id=organization_id
            )
            
            return {
                "space_id": space_id,
                "name": name,
                "description": description or "",
                "domain_storage": domain_storage,
                "icon": icon or "folder",
                "color": color or "#6b7280",
                "created_at": timestamp,
                "conversation_count": 0,
                "member_count": 1,
                "role": "admin"  # Creator's role
            }
        
        except Exception as e:
            logger.error(f"Failed to create space: {e}")
            raise ValueError(f"Failed to create space: {e}")
    
    async def list_spaces(
        self,
        user_id: str,
        organization_id: str,
        include_inactive: bool = False
    ) -> List[Dict]:
        """
        List all spaces accessible to a user.
        
        Args:
            user_id: User ID
            organization_id: Organization ID for filtering
            include_inactive: Whether to include soft-deleted spaces
        
        Returns:
            List of space dicts with metadata and user's role
        """
        try:
            # Find all space concepts for organization
            filters = {
                MetadataField.TYPE: ConceptType.SPACE.value,
                MetadataField.ORGANIZATION_ID: organization_id,
            }
            
            if not include_inactive:
                filters[MetadataField.ACTIVE] = True
            
            space_concepts = self.storage.query_by_metadata(
                filters=filters,
                limit=100
            )
            
            # For each space, check user's permission and get role
            spaces = []
            for concept in space_concepts:
                # Check if user has access to this space
                permission = await self._get_user_permission(
                    space_id=concept["concept_id"],
                    user_id=user_id
                )
                
                if permission:
                    metadata = concept.get("metadata", {})
                    spaces.append({
                        "space_id": concept["concept_id"],
                        "name": metadata.get("name", "Unknown"),
                        "description": metadata.get("description", ""),
                        "domain_storage": metadata.get("domain_storage", ""),
                        "icon": metadata.get("icon", "folder"),
                        "color": metadata.get("color", "#6b7280"),
                        "conversation_count": metadata.get("conversation_count", 0),
                        "member_count": metadata.get("member_count", 0),
                        "created_at": metadata.get(MetadataField.CREATED_AT),
                        "updated_at": metadata.get(MetadataField.UPDATED_AT),
                        "role": permission["role"],
                        "active": metadata.get(MetadataField.ACTIVE, True)
                    })
            
            logger.info(f"Listed {len(spaces)} spaces for user {user_id}")
            return spaces
        
        except Exception as e:
            logger.error(f"Failed to list spaces: {e}")
            raise ValueError(f"Failed to list spaces: {e}")
    
    async def get_space(
        self,
        space_id: str,
        user_id: str,
        organization_id: str
    ) -> Dict:
        """
        Get details for a specific space.
        
        Args:
            space_id: Space ID
            user_id: User ID (for permission check)
            organization_id: Organization ID for validation
        
        Returns:
            Dict with space details and user's role
        
        Raises:
            ValueError: If space not found or user lacks permission
        """
        try:
            # Get space concept
            space_concept = self.storage.get_concept(space_id)
            
            if not space_concept:
                raise ValueError("Space not found")
            
            metadata = space_concept.get("metadata", {})
            
            # Verify organization
            if metadata.get(MetadataField.ORGANIZATION_ID) != organization_id:
                raise ValueError("Space not found")
            
            # Check user permission
            permission = await self._get_user_permission(space_id, user_id)
            if not permission:
                raise ValueError("Access denied")
            
            return {
                "space_id": space_id,
                "name": metadata.get("name", "Unknown"),
                "description": metadata.get("description", ""),
                "domain_storage": metadata.get("domain_storage", ""),
                "icon": metadata.get("icon", "folder"),
                "color": metadata.get("color", "#6b7280"),
                "conversation_count": metadata.get("conversation_count", 0),
                "member_count": metadata.get("member_count", 0),
                "created_at": metadata.get(MetadataField.CREATED_AT),
                "updated_at": metadata.get(MetadataField.UPDATED_AT),
                "created_by": metadata.get("created_by"),
                "role": permission["role"],
                "active": metadata.get(MetadataField.ACTIVE, True)
            }
        
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to get space: {e}")
            raise ValueError(f"Failed to get space: {e}")
    
    async def update_space(
        self,
        space_id: str,
        user_id: str,
        organization_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None
    ) -> Dict:
        """
        Update space details.
        
        Requires admin or write permission.
        
        Args:
            space_id: Space ID
            user_id: User ID (for permission check)
            organization_id: Organization ID for validation
            name: Optional new name
            description: Optional new description
            icon: Optional new icon
            color: Optional new color
        
        Returns:
            Updated space dict
        
        Raises:
            ValueError: If user lacks permission or space not found
        """
        try:
            # Check permission (must be admin or write)
            permission = await self._get_user_permission(space_id, user_id)
            if not permission or permission["role"] not in ["admin", "write"]:
                raise ValueError("Insufficient permissions")
            
            # Get current space
            space_concept = self.storage.get_concept(space_id)
            if not space_concept:
                raise ValueError("Space not found")
            
            metadata = space_concept.get("metadata", {})
            
            # Verify organization
            if metadata.get(MetadataField.ORGANIZATION_ID) != organization_id:
                raise ValueError("Space not found")
            
            # Build updates
            updates = {
                MetadataField.UPDATED_AT: datetime.utcnow().isoformat()
            }
            
            if name is not None:
                if len(name.strip()) == 0:
                    raise ValueError("Space name cannot be empty")
                updates["name"] = name
            
            if description is not None:
                updates["description"] = description
            
            if icon is not None:
                updates["icon"] = icon
            
            if color is not None:
                updates["color"] = color
            
            # Update metadata
            self.storage.update_concept_metadata(space_id, updates)
            
            logger.info(f"Updated space {space_id}")
            
            # Return updated space
            return await self.get_space(space_id, user_id, organization_id)
        
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to update space: {e}")
            raise ValueError(f"Failed to update space: {e}")
    
    async def delete_space(
        self,
        space_id: str,
        user_id: str,
        organization_id: str
    ) -> Dict:
        """
        Soft delete a space.
        
        Requires admin permission. Sets active=False.
        
        Args:
            space_id: Space ID
            user_id: User ID (for permission check)
            organization_id: Organization ID for validation
        
        Returns:
            Dict with success message
        
        Raises:
            ValueError: If user lacks admin permission or space not found
        """
        try:
            # Check permission (must be admin)
            permission = await self._get_user_permission(space_id, user_id)
            if not permission or permission["role"] != "admin":
                raise ValueError("Only admins can delete spaces")
            
            # Get current space
            space_concept = self.storage.get_concept(space_id)
            if not space_concept:
                raise ValueError("Space not found")
            
            metadata = space_concept.get("metadata", {})
            
            # Verify organization
            if metadata.get(MetadataField.ORGANIZATION_ID) != organization_id:
                raise ValueError("Space not found")
            
            # Soft delete
            self.storage.update_concept_metadata(
                space_id,
                {
                    MetadataField.ACTIVE: False,
                    MetadataField.UPDATED_AT: datetime.utcnow().isoformat(),
                    "deleted_by": user_id,
                    "deleted_at": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Soft deleted space {space_id}")
            
            return {"message": "Space deleted successfully"}
        
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete space: {e}")
            raise ValueError(f"Failed to delete space: {e}")
    
    async def add_member(
        self,
        space_id: str,
        user_id: str,
        target_user_id: str,
        role: str,
        organization_id: str
    ) -> Dict:
        """
        Add a member to a space.
        
        Requires admin permission.
        
        Args:
            space_id: Space ID
            user_id: User ID of requester (for permission check)
            target_user_id: User ID to add
            role: Role to grant (admin, write, read)
            organization_id: Organization ID for validation
        
        Returns:
            Dict with success message and member details
        
        Raises:
            ValueError: If user lacks admin permission or validation fails
        """
        try:
            # Validate role
            if role not in ["admin", "write", "read"]:
                raise ValueError("Invalid role. Must be: admin, write, or read")
            
            # Check permission (must be admin)
            permission = await self._get_user_permission(space_id, user_id)
            if not permission or permission["role"] != "admin":
                raise ValueError("Only admins can add members")
            
            # Verify space exists and belongs to organization
            space_concept = self.storage.get_concept(space_id)
            if not space_concept:
                raise ValueError("Space not found")
            
            metadata = space_concept.get("metadata", {})
            if metadata.get(MetadataField.ORGANIZATION_ID) != organization_id:
                raise ValueError("Space not found")
            
            # Check if user already has permission
            existing_permission = await self._get_user_permission(space_id, target_user_id)
            if existing_permission:
                raise ValueError("User is already a member of this space")
            
            # Add member
            await self._add_member_internal(
                space_id=space_id,
                user_id=target_user_id,
                role=role,
                added_by=user_id,
                organization_id=organization_id
            )
            
            # Update member count
            current_count = metadata.get("member_count", 0)
            self.storage.update_concept_metadata(
                space_id,
                {
                    "member_count": current_count + 1,
                    MetadataField.UPDATED_AT: datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Added user {target_user_id} to space {space_id} with role {role}")
            
            return {
                "message": "Member added successfully",
                "user_id": target_user_id,
                "role": role
            }
        
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to add member: {e}")
            raise ValueError(f"Failed to add member: {e}")
    
    async def list_members(
        self,
        space_id: str,
        user_id: str,
        organization_id: str
    ) -> List[Dict]:
        """
        List all members of a space.
        
        Args:
            space_id: Space ID
            user_id: User ID (for permission check)
            organization_id: Organization ID for validation
        
        Returns:
            List of member dicts with user details and roles
        
        Raises:
            ValueError: If user lacks permission or space not found
        """
        try:
            # Check permission
            permission = await self._get_user_permission(space_id, user_id)
            if not permission:
                raise ValueError("Access denied")
            
            # Verify space exists
            space_concept = self.storage.get_concept(space_id)
            if not space_concept:
                raise ValueError("Space not found")
            
            metadata = space_concept.get("metadata", {})
            if metadata.get(MetadataField.ORGANIZATION_ID) != organization_id:
                raise ValueError("Space not found")
            
            # Find all permission concepts for this space
            permission_concepts = self.storage.query_by_metadata(
                filters={
                    MetadataField.TYPE: ConceptType.PERMISSION.value,
                    "resource_type": "space",
                    "resource_id": space_id,
                    MetadataField.ACTIVE: True
                },
                limit=1000
            )
            
            # Get user details for each permission
            members = []
            for perm_concept in permission_concepts:
                perm_metadata = perm_concept.get("metadata", {})
                target_user_id = perm_metadata.get(MetadataField.USER_ID)
                
                if target_user_id:
                    # Get user details
                    user_concept = self.storage.get_concept(target_user_id)
                    if user_concept:
                        user_metadata = user_concept.get("metadata", {})
                        members.append({
                            "user_id": target_user_id,
                            "email": user_metadata.get(MetadataField.EMAIL, ""),
                            "full_name": user_metadata.get(MetadataField.FULL_NAME, ""),
                            "role": perm_metadata.get(MetadataField.ROLE, "read"),
                            "added_at": perm_metadata.get(MetadataField.CREATED_AT),
                            "added_by": perm_metadata.get("granted_by")
                        })
            
            logger.info(f"Listed {len(members)} members for space {space_id}")
            return members
        
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to list members: {e}")
            raise ValueError(f"Failed to list members: {e}")
    
    async def remove_member(
        self,
        space_id: str,
        user_id: str,
        target_user_id: str,
        organization_id: str
    ) -> Dict:
        """
        Remove a member from a space.
        
        Requires admin permission. Cannot remove the last admin.
        
        Args:
            space_id: Space ID
            user_id: User ID of requester (for permission check)
            target_user_id: User ID to remove
            organization_id: Organization ID for validation
        
        Returns:
            Dict with success message
        
        Raises:
            ValueError: If user lacks admin permission or validation fails
        """
        try:
            # Check permission (must be admin)
            permission = await self._get_user_permission(space_id, user_id)
            if not permission or permission["role"] != "admin":
                raise ValueError("Only admins can remove members")
            
            # Verify space exists
            space_concept = self.storage.get_concept(space_id)
            if not space_concept:
                raise ValueError("Space not found")
            
            metadata = space_concept.get("metadata", {})
            if metadata.get(MetadataField.ORGANIZATION_ID) != organization_id:
                raise ValueError("Space not found")
            
            # Get target user's permission
            target_permission = await self._get_user_permission(space_id, target_user_id)
            if not target_permission:
                raise ValueError("User is not a member of this space")
            
            # Check if removing last admin
            if target_permission["role"] == "admin":
                # Count admins
                all_permissions = self.storage.query_by_metadata(
                    filters={
                        MetadataField.TYPE: ConceptType.PERMISSION.value,
                        "resource_type": "space",
                        "resource_id": space_id,
                        MetadataField.ROLE: "admin",
                        MetadataField.ACTIVE: True
                    },
                    limit=100
                )
                
                if len(all_permissions) <= 1:
                    raise ValueError("Cannot remove the last admin from a space")
            
            # Soft delete permission
            permission_id = target_permission["permission_id"]
            self.storage.update_concept_metadata(
                permission_id,
                {
                    MetadataField.ACTIVE: False,
                    MetadataField.UPDATED_AT: datetime.utcnow().isoformat(),
                    "revoked_by": user_id,
                    "revoked_at": datetime.utcnow().isoformat()
                }
            )
            
            # Update member count
            current_count = metadata.get("member_count", 0)
            self.storage.update_concept_metadata(
                space_id,
                {
                    "member_count": max(0, current_count - 1),
                    MetadataField.UPDATED_AT: datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Removed user {target_user_id} from space {space_id}")
            
            return {"message": "Member removed successfully"}
        
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to remove member: {e}")
            raise ValueError(f"Failed to remove member: {e}")
    
    async def update_member_role(
        self,
        space_id: str,
        user_id: str,
        target_user_id: str,
        new_role: str,
        organization_id: str
    ) -> Dict:
        """
        Update a member's role in a space.
        
        Requires admin permission. Cannot demote the last admin.
        
        Args:
            space_id: Space ID
            user_id: User ID of requester (for permission check)
            target_user_id: User ID to update
            new_role: New role (admin, write, read)
            organization_id: Organization ID for validation
        
        Returns:
            Dict with success message and new role
        
        Raises:
            ValueError: If user lacks admin permission or validation fails
        """
        try:
            # Validate role
            if new_role not in ["admin", "write", "read"]:
                raise ValueError("Invalid role. Must be: admin, write, or read")
            
            # Check permission (must be admin)
            permission = await self._get_user_permission(space_id, user_id)
            if not permission or permission["role"] != "admin":
                raise ValueError("Only admins can update member roles")
            
            # Verify space exists
            space_concept = self.storage.get_concept(space_id)
            if not space_concept:
                raise ValueError("Space not found")
            
            metadata = space_concept.get("metadata", {})
            if metadata.get(MetadataField.ORGANIZATION_ID) != organization_id:
                raise ValueError("Space not found")
            
            # Get target user's permission
            target_permission = await self._get_user_permission(space_id, target_user_id)
            if not target_permission:
                raise ValueError("User is not a member of this space")
            
            # Check if demoting last admin
            if target_permission["role"] == "admin" and new_role != "admin":
                # Count admins
                all_permissions = self.storage.query_by_metadata(
                    filters={
                        MetadataField.TYPE: ConceptType.PERMISSION.value,
                        "resource_type": "space",
                        "resource_id": space_id,
                        MetadataField.ROLE: "admin",
                        MetadataField.ACTIVE: True
                    },
                    limit=100
                )
                
                if len(all_permissions) <= 1:
                    raise ValueError("Cannot demote the last admin")
            
            # Update role
            permission_id = target_permission["permission_id"]
            self.storage.update_concept_metadata(
                permission_id,
                {
                    MetadataField.ROLE: new_role,
                    MetadataField.UPDATED_AT: datetime.utcnow().isoformat(),
                    "updated_by": user_id
                }
            )
            
            logger.info(f"Updated user {target_user_id} role to {new_role} in space {space_id}")
            
            return {
                "message": "Member role updated successfully",
                "user_id": target_user_id,
                "new_role": new_role
            }
        
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to update member role: {e}")
            raise ValueError(f"Failed to update member role: {e}")
    
    # Internal helper methods
    
    async def _add_member_internal(
        self,
        space_id: str,
        user_id: str,
        role: str,
        added_by: str,
        organization_id: str
    ) -> str:
        """
        Internal method to add a member (creates permission concept).
        
        Returns:
            Permission concept ID
        """
        timestamp = datetime.utcnow().isoformat()
        
        permission_concept = self.storage.learn_concept(
            content=f"User access to space",
            semantic_patterns=["Permission", role],
            metadata={
                MetadataField.TYPE: ConceptType.PERMISSION.value,
                MetadataField.ORGANIZATION_ID: organization_id,
                MetadataField.USER_ID: user_id,
                "resource_type": "space",
                "resource_id": space_id,
                MetadataField.ROLE: role,
                "granted_by": added_by,
                MetadataField.CREATED_AT: timestamp,
                MetadataField.UPDATED_AT: timestamp,
                MetadataField.ACTIVE: True,
            }
        )
        
        permission_id = permission_concept["concept_id"]
        
        # Create associations
        self.storage.create_association(
            from_concept_id=user_id,
            to_concept_id=space_id,
            association_type=AssociationType.HAS_PERMISSION.value,
            metadata={"role": role}
        )
        
        return permission_id
    
    async def _get_user_permission(
        self,
        space_id: str,
        user_id: str
    ) -> Optional[Dict]:
        """
        Get user's permission for a space.
        
        Returns:
            Dict with permission details or None if no permission
        """
        try:
            permissions = self.storage.query_by_metadata(
                filters={
                    MetadataField.TYPE: ConceptType.PERMISSION.value,
                    MetadataField.USER_ID: user_id,
                    "resource_type": "space",
                    "resource_id": space_id,
                    MetadataField.ACTIVE: True
                },
                limit=1
            )
            
            if permissions:
                perm_metadata = permissions[0].get("metadata", {})
                return {
                    "permission_id": permissions[0]["concept_id"],
                    "role": perm_metadata.get(MetadataField.ROLE, "read"),
                    "granted_at": perm_metadata.get(MetadataField.CREATED_AT)
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error checking user permission: {e}")
            return None
    
    def check_permission(
        self,
        space_id: str,
        user_id: str,
        required_role: str = "read"
    ) -> bool:
        """
        Check if user has required permission for a space.
        
        Args:
            space_id: Space ID
            user_id: User ID
            required_role: Minimum required role (admin > write > read)
        
        Returns:
            True if user has sufficient permission, False otherwise
        """
        role_hierarchy = {"admin": 3, "write": 2, "read": 1}
        
        permission = self._get_user_permission(space_id, user_id)
        if not permission:
            return False
        
        user_role_level = role_hierarchy.get(permission["role"], 0)
        required_role_level = role_hierarchy.get(required_role, 0)
        
        return user_role_level >= required_role_level
