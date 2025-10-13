"""
🏗️ CENTRALIZED WORKSPACE MANAGER

This module provides rock-solid control over workspace_id management across 
the entire biological intelligence system. It ensures consistency, validation,
and prevents workspace ID mismatches that cause memory loading failures.

Key Features:
- Centralized workspace_id logic
- Automatic validation and conflict detection
- Environment-aware workspace selection
- Migration support for existing workspaces
- Comprehensive error handling and diagnostics
"""

import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger('WorkspaceManager')


class WorkspaceType(Enum):
    """Types of biological intelligence workspaces"""
    GENERAL = "general"           # Default general-purpose training
    ENGLISH = "english"           # English language learning
    DOMAIN_SPECIFIC = "domain"    # Domain-specific knowledge
    EXPERIMENTAL = "experimental" # Testing and experimentation
    PI_OPTIMIZED = "pi"          # Pi-specific optimized workspaces


@dataclass
class WorkspaceConfig:
    """Configuration for a workspace"""
    workspace_id: str
    workspace_type: WorkspaceType
    base_path: str
    description: str
    is_default: bool = False
    migration_source: Optional[str] = None  # For migrating old workspaces


class WorkspaceManager:
    """
    Centralized manager for all workspace operations.
    
    This class ensures consistent workspace_id usage across all components
    and prevents the workspace ID mismatch issues.
    """
    
    # Standard workspace configurations
    STANDARD_WORKSPACES = {
        "core": WorkspaceConfig(
            workspace_id="core",
            workspace_type=WorkspaceType.GENERAL,
            base_path="./biological_workspace",
            description="Default general-purpose biological intelligence",
            is_default=True
        ),
        "english": WorkspaceConfig(
            workspace_id="english",
            workspace_type=WorkspaceType.ENGLISH,
            base_path="./english_biological_workspace", 
            description="English language learning workspace",
            migration_source="biological_service"  # Migrate from old workspace_id
        ),
        "pi_core": WorkspaceConfig(
            workspace_id="pi_core",
            workspace_type=WorkspaceType.PI_OPTIMIZED,
            base_path="/mnt/hdd/biological_intelligence/biological_workspace",
            description="Pi-optimized core workspace"
        )
    }
    
    def __init__(self, auto_migrate: bool = True):
        """
        Initialize workspace manager.
        
        Args:
            auto_migrate: Automatically handle workspace migrations
        """
        self.auto_migrate = auto_migrate
        self.active_workspaces: Dict[str, WorkspaceConfig] = {}
        self._load_configurations()
    
    def _load_configurations(self):
        """Load workspace configurations."""
        self.active_workspaces = self.STANDARD_WORKSPACES.copy()
        
        # Load custom configurations if they exist
        config_path = Path("workspace_config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    custom_configs = json.load(f)
                
                for name, config_data in custom_configs.items():
                    self.active_workspaces[name] = WorkspaceConfig(**config_data)
                    
                logger.info(f"Loaded {len(custom_configs)} custom workspace configurations")
            except Exception as e:
                logger.warning(f"Failed to load custom workspace config: {e}")
    
    def get_workspace_id(self, 
                        workspace_name: Optional[str] = None,
                        workspace_type: Optional[WorkspaceType] = None,
                        environment: str = "desktop") -> str:
        """
        Get the appropriate workspace_id for current context.
        
        Args:
            workspace_name: Specific workspace name (e.g., "core", "english")
            workspace_type: Type of workspace needed
            environment: Environment context ("desktop", "pi", "test")
            
        Returns:
            Appropriate workspace_id string
        """
        # Direct workspace name specified
        if workspace_name and workspace_name in self.active_workspaces:
            return self.active_workspaces[workspace_name].workspace_id
        
        # Find by type
        if workspace_type:
            for config in self.active_workspaces.values():
                if config.workspace_type == workspace_type:
                    return config.workspace_id
        
        # Environment-specific defaults
        if environment == "pi":
            return self.active_workspaces.get("pi_core", self.active_workspaces["core"]).workspace_id
        
        # Default fallback
        default_config = next((c for c in self.active_workspaces.values() if c.is_default), None)
        if default_config:
            return default_config.workspace_id
        
        return "core"  # Ultimate fallback
    
    def get_workspace_path(self, 
                          workspace_name: Optional[str] = None,
                          workspace_id: Optional[str] = None) -> str:
        """
        Get the base path for a workspace.
        
        Args:
            workspace_name: Name of workspace configuration
            workspace_id: Direct workspace ID lookup
            
        Returns:
            Base path for the workspace
        """
        if workspace_name and workspace_name in self.active_workspaces:
            return self.active_workspaces[workspace_name].base_path
        
        if workspace_id:
            for config in self.active_workspaces.values():
                if config.workspace_id == workspace_id:
                    return config.base_path
        
        return "./biological_workspace"  # Default fallback
    
    def get_trainer_config(self, 
                          workspace_name: Optional[str] = None,
                          environment: str = "desktop",
                          **kwargs) -> Dict[str, Any]:
        """
        Get complete BiologicalTrainer configuration for a workspace.
        
        Args:
            workspace_name: Workspace to configure for
            environment: Environment context
            **kwargs: Additional configuration overrides
            
        Returns:
            Dictionary of trainer configuration parameters
        """
        workspace_id = self.get_workspace_id(workspace_name, environment=environment)
        base_path = self.get_workspace_path(workspace_name, workspace_id)
        
        config = {
            'base_path': base_path,
            'workspace_id': workspace_id,
            'use_full_swarm': True,  # Always use full swarm for maximum emergence
        }
        
        # Add environment-specific configurations
        if environment == "pi":
            try:
                from pi_config import PI_BIOLOGICAL_CONFIG
                config.update(PI_BIOLOGICAL_CONFIG)
                config['workspace_id'] = workspace_id  # Override with consistent ID
            except ImportError:
                pass
        
        # Apply any overrides
        config.update(kwargs)
        
        return config
    
    def validate_workspace(self, workspace_id: str, base_path: str) -> Tuple[bool, List[str]]:
        """
        Validate a workspace configuration.
        
        Args:
            workspace_id: ID to validate
            base_path: Path to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check workspace_id format
        if not workspace_id or not workspace_id.strip():
            issues.append("Workspace ID cannot be empty")
        elif not workspace_id.replace('_', '').replace('-', '').isalnum():
            issues.append("Workspace ID should contain only letters, numbers, hyphens, and underscores")
        
        # Check path validity
        try:
            path = Path(base_path)
            if not path.is_absolute() and not str(path).startswith('./'):
                issues.append(f"Base path should be absolute or relative: {base_path}")
        except Exception as e:
            issues.append(f"Invalid base path format: {e}")
        
        return len(issues) == 0, issues
    
    def migrate_workspace(self, 
                         old_workspace_id: str,
                         new_workspace_id: str, 
                         workspace_path: str) -> bool:
        """
        Migrate memory from old workspace_id to new workspace_id.
        
        Args:
            old_workspace_id: Previous workspace ID used in memory
            new_workspace_id: New workspace ID to migrate to
            workspace_path: Path containing the memory nodes
            
        Returns:
            True if migration successful
        """
        nodes_dir = Path(workspace_path) / "nodes"
        if not nodes_dir.exists():
            logger.warning(f"No nodes directory found in {workspace_path}")
            return False
        
        try:
            from src.pure_binary_storage import PureBinaryStorage
            
            storage = PureBinaryStorage(str(nodes_dir))
            nodes = storage.list_all_nodes()
            
            migrated_count = 0
            for node in nodes:
                metadata = node.get("metadata", {})
                if metadata.get("workspace_id") == old_workspace_id:
                    # Update the workspace_id in metadata
                    metadata["workspace_id"] = new_workspace_id
                    metadata["migrated_from"] = old_workspace_id
                    metadata["migration_timestamp"] = str(time.time())
                    
                    # Re-save the node with updated metadata
                    storage.store_node(node)
                    migrated_count += 1
            
            logger.info(f"Migrated {migrated_count} nodes from '{old_workspace_id}' to '{new_workspace_id}'")
            return migrated_count > 0
            
        except Exception as e:
            logger.error(f"Failed to migrate workspace: {e}")
            return False
    
    def auto_migrate_if_needed(self, workspace_name: str) -> bool:
        """
        Automatically migrate workspace if migration source is specified.
        
        Args:
            workspace_name: Name of workspace to check for migration
            
        Returns:
            True if migration was performed or not needed
        """
        if not self.auto_migrate:
            return True
        
        config = self.active_workspaces.get(workspace_name)
        if not config or not config.migration_source:
            return True
        
        workspace_path = config.base_path
        nodes_dir = Path(workspace_path) / "nodes"
        
        if not nodes_dir.exists():
            return True  # No migration needed, no existing data
        
        # Check if migration is needed
        try:
            from src.pure_binary_storage import PureBinaryStorage
            
            storage = PureBinaryStorage(str(nodes_dir))
            nodes = storage.list_all_nodes()
            
            # Count nodes by workspace_id
            workspace_counts = {}
            for node in nodes:
                metadata = node.get("metadata", {})
                ws_id = metadata.get("workspace_id", "unknown")
                workspace_counts[ws_id] = workspace_counts.get(ws_id, 0) + 1
            
            # If we have nodes with the old workspace_id but none with the new one
            old_count = workspace_counts.get(config.migration_source, 0)
            new_count = workspace_counts.get(config.workspace_id, 0)
            
            if old_count > 0 and new_count == 0:
                logger.info(f"Auto-migrating {old_count} nodes from '{config.migration_source}' to '{config.workspace_id}'")
                return self.migrate_workspace(
                    config.migration_source, 
                    config.workspace_id, 
                    workspace_path
                )
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to check migration status: {e}")
            return True
    
    def get_diagnostic_info(self, workspace_path: str) -> Dict[str, Any]:
        """
        Get comprehensive diagnostic information about a workspace.
        
        Args:
            workspace_path: Path to workspace to diagnose
            
        Returns:
            Dictionary with diagnostic information
        """
        info = {
            'workspace_path': workspace_path,
            'exists': False,
            'has_nodes': False,
            'workspace_ids': {},
            'total_nodes': 0,
            'node_types': {},
            'issues': []
        }
        
        workspace_dir = Path(workspace_path)
        info['exists'] = workspace_dir.exists()
        
        if not info['exists']:
            info['issues'].append(f"Workspace directory does not exist: {workspace_path}")
            return info
        
        nodes_dir = workspace_dir / "nodes"
        info['has_nodes'] = nodes_dir.exists()
        
        if not info['has_nodes']:
            info['issues'].append("No nodes directory found")
            return info
        
        try:
            from src.pure_binary_storage import PureBinaryStorage
            
            storage = PureBinaryStorage(str(nodes_dir))
            nodes = storage.list_all_nodes()
            info['total_nodes'] = len(nodes)
            
            for node in nodes:
                # Count by workspace_id
                metadata = node.get("metadata", {})
                ws_id = metadata.get("workspace_id", "unknown")
                info['workspace_ids'][ws_id] = info['workspace_ids'].get(ws_id, 0) + 1
                
                # Count by node type
                node_type = node.get("level", "unknown")
                info['node_types'][node_type] = info['node_types'].get(node_type, 0) + 1
            
            # Check for workspace consistency
            if len(info['workspace_ids']) > 1:
                info['issues'].append(f"Multiple workspace IDs found: {list(info['workspace_ids'].keys())}")
            elif len(info['workspace_ids']) == 0:
                info['issues'].append("No workspace IDs found in node metadata")
            
        except Exception as e:
            info['issues'].append(f"Failed to analyze nodes: {e}")
        
        return info
    
    def create_workspace(self, workspace_name: str, config: WorkspaceConfig) -> bool:
        """
        Create a new workspace configuration.
        
        Args:
            workspace_name: Name for the workspace
            config: Workspace configuration
            
        Returns:
            True if created successfully
        """
        is_valid, issues = self.validate_workspace(config.workspace_id, config.base_path)
        if not is_valid:
            logger.error(f"Invalid workspace configuration: {', '.join(issues)}")
            return False
        
        self.active_workspaces[workspace_name] = config
        
        # Create the workspace directory
        try:
            Path(config.base_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created workspace '{workspace_name}' at {config.base_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create workspace directory: {e}")
            return False


# Global workspace manager instance
_workspace_manager = None

def get_workspace_manager() -> WorkspaceManager:
    """Get the global workspace manager instance."""
    global _workspace_manager
    if _workspace_manager is None:
        _workspace_manager = WorkspaceManager()
    return _workspace_manager


# Convenience functions for common operations
def get_trainer_config(workspace_name: Optional[str] = None, 
                      environment: str = "desktop", 
                      **kwargs) -> Dict[str, Any]:
    """Get trainer configuration with consistent workspace management."""
    return get_workspace_manager().get_trainer_config(workspace_name, environment, **kwargs)


def get_workspace_id(workspace_name: Optional[str] = None,
                    workspace_type: Optional[WorkspaceType] = None,
                    environment: str = "desktop") -> str:
    """Get appropriate workspace ID for context."""
    return get_workspace_manager().get_workspace_id(workspace_name, workspace_type, environment)


def diagnose_workspace(workspace_path: str) -> Dict[str, Any]:
    """Get diagnostic information about a workspace."""
    return get_workspace_manager().get_diagnostic_info(workspace_path)


if __name__ == "__main__":
    # Test the workspace manager
    import time
    
    manager = WorkspaceManager()
    
    print("🏗️ WORKSPACE MANAGER TEST")
    print("=" * 50)
    
    print("Available workspaces:")
    for name, config in manager.active_workspaces.items():
        print(f"  {name}: {config.workspace_id} ({config.workspace_type.value})")
    
    print("\nTesting workspace ID resolution:")
    test_cases = [
        (None, None, "desktop"),
        ("core", None, "desktop"),
        ("english", None, "desktop"),
        (None, WorkspaceType.ENGLISH, "desktop"),
        (None, None, "pi"),
    ]
    
    for name, wtype, env in test_cases:
        workspace_id = manager.get_workspace_id(name, wtype, env)
        path = manager.get_workspace_path(name, workspace_id)
        print(f"  get_workspace_id({name}, {wtype}, {env}) -> '{workspace_id}' @ {path}")
    
    print("\n✅ Workspace manager test completed!")