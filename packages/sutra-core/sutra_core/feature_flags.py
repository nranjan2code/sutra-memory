"""
Sutra AI Edition & Feature Flag System

Production-grade edition management with:
- Three-tier licensing (Simple/Community/Enterprise)
- Quota enforcement (rate limits, storage, concepts)
- Topology control (single-node vs HA+Grid)
- License validation

Philosophy: All features in all editions. Differentiation = scale + SLA.
"""

import os
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import hashlib
import hmac
import json
import base64
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class Edition(Enum):
    """Sutra AI editions"""
    SIMPLE = "simple"        # Free - single-node, low limits
    COMMUNITY = "community"  # $99/mo - single-node, higher limits
    ENTERPRISE = "enterprise"  # $999/mo - HA + Grid + highest limits


@dataclass
class EditionLimits:
    """Rate limits and quotas per edition"""
    # API rate limits (per minute)
    learn_per_min: int
    reason_per_min: int
    
    # Ingestion limits
    ingest_workers: int
    max_dataset_gb: int  # 0 = unlimited
    
    # Storage limits
    max_concepts: int
    retention_days: int  # Audit log retention
    
    # Topology
    ha_enabled: bool
    grid_enabled: bool
    sharded_storage: bool
    
    # Security
    secure_mode_required: bool
    
    # Support SLA
    support_sla_hours: Optional[int]  # Response time in hours, None = community


# Edition configuration matrix
EDITION_LIMITS = {
    Edition.SIMPLE: EditionLimits(
        learn_per_min=10,
        reason_per_min=50,
        ingest_workers=2,
        max_dataset_gb=1,
        max_concepts=100_000,
        retention_days=7,
        ha_enabled=False,
        grid_enabled=False,
        sharded_storage=False,
        secure_mode_required=False,
        support_sla_hours=None,  # Community support only
    ),
    Edition.COMMUNITY: EditionLimits(
        learn_per_min=100,
        reason_per_min=500,
        ingest_workers=4,
        max_dataset_gb=10,
        max_concepts=1_000_000,
        retention_days=30,
        ha_enabled=False,
        grid_enabled=False,
        sharded_storage=False,
        secure_mode_required=False,
        support_sla_hours=48,  # 48-hour email support
    ),
    Edition.ENTERPRISE: EditionLimits(
        learn_per_min=1000,
        reason_per_min=5000,
        ingest_workers=16,
        max_dataset_gb=0,  # Unlimited
        max_concepts=10_000_000,
        retention_days=365,
        ha_enabled=True,
        grid_enabled=True,
        sharded_storage=True,
        secure_mode_required=True,
        support_sla_hours=4,  # 4-hour dedicated support
    ),
}


class LicenseValidator:
    """
    Offline license validation using HMAC-SHA256
    
    License format: base64(json({edition, expires, customer_id})).signature
    Signature = HMAC-SHA256(license_data, SECRET_KEY)
    """
    
    def __init__(self):
        # In production, load from secure storage (e.g., AWS Secrets Manager)
        self.secret_key = os.getenv("SUTRA_LICENSE_SECRET", "").encode()
        if not self.secret_key and os.getenv("SUTRA_EDITION") != "simple":
            logger.warning("SUTRA_LICENSE_SECRET not set - license validation disabled")
    
    def validate(self, license_key: str, expected_edition: Edition) -> bool:
        """
        Validate license key format and signature
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Parse license: base64_data.signature
            if "." not in license_key:
                logger.error("Invalid license format: missing signature")
                return False
            
            license_data, signature = license_key.rsplit(".", 1)
            
            # Verify signature
            expected_sig = hmac.new(
                self.secret_key,
                license_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_sig):
                logger.error("Invalid license signature")
                return False
            
            # Decode and validate license data
            decoded = base64.b64decode(license_data).decode()
            license_info = json.loads(decoded)
            
            # Check edition
            if license_info.get("edition") != expected_edition.value:
                logger.error(f"License edition mismatch: expected {expected_edition.value}, got {license_info.get('edition')}")
                return False
            
            # Check expiration
            expires_str = license_info.get("expires")
            if expires_str:
                expires = datetime.fromisoformat(expires_str)
                if datetime.now() > expires:
                    logger.error(f"License expired on {expires_str}")
                    return False
            
            logger.info(f"License validated: {expected_edition.value} for {license_info.get('customer_id')}")
            return True
            
        except Exception as e:
            logger.error(f"License validation error: {e}")
            return False


class FeatureFlags:
    """
    Runtime edition controller
    
    Responsibilities:
    - Validate license for paid editions
    - Enforce quotas (rate limits, storage, concepts)
    - Control topology (HA, Grid, sharding)
    - Provide edition info for UI/monitoring
    """
    
    def __init__(self):
        # Detect edition from environment
        edition_str = os.getenv("SUTRA_EDITION", "simple").lower()
        try:
            self.edition = Edition(edition_str)
        except ValueError:
            raise ValueError(
                f"Invalid SUTRA_EDITION: {edition_str}. "
                f"Must be: simple, community, enterprise"
            )
        
        self.limits = EDITION_LIMITS[self.edition]
        self.validator = LicenseValidator()
        
        # Validate license for paid editions
        if self.edition != Edition.SIMPLE:
            self._validate_license()
        
        # Enforce security for enterprise
        if self.edition == Edition.ENTERPRISE:
            self._enforce_security()
        
        logger.info(
            f"Sutra AI {self.edition.value.upper()} Edition initialized. "
            f"Limits: {self.limits.learn_per_min} learn/min, "
            f"{self.limits.max_concepts:,} max concepts"
        )
    
    def _validate_license(self):
        """Validate license key for paid editions"""
        license_key = os.getenv("SUTRA_LICENSE_KEY")
        
        if not license_key:
            raise ValueError(
                f"\n{'='*70}\n"
                f"ERROR: {self.edition.value.upper()} edition requires SUTRA_LICENSE_KEY\n"
                f"\n"
                f"Get your license at: https://sutra.ai/pricing\n"
                f"\n"
                f"Current edition: {self.edition.value}\n"
                f"Required: Valid license key\n"
                f"{'='*70}\n"
            )
        
        # Validate license format and signature
        if not self.validator.validate(license_key, self.edition):
            raise ValueError(
                f"\n{'='*70}\n"
                f"ERROR: Invalid license key for {self.edition.value.upper()} edition\n"
                f"\n"
                f"Please check:\n"
                f"  1. License key is correct\n"
                f"  2. License has not expired\n"
                f"  3. License matches edition ({self.edition.value})\n"
                f"\n"
                f"Contact support@sutra.ai for assistance\n"
                f"{'='*70}\n"
            )
    
    def _enforce_security(self):
        """Enforce security requirements for enterprise"""
        if os.getenv("SUTRA_SECURE_MODE") != "true":
            raise ValueError(
                f"\n{'='*70}\n"
                f"ERROR: Enterprise edition requires SUTRA_SECURE_MODE=true\n"
                f"\n"
                f"Enterprise deployments must enable:\n"
                f"  • TLS encryption\n"
                f"  • Authentication\n"
                f"  • Network isolation\n"
                f"\n"
                f"See: docs/security/PRODUCTION_SECURITY_SETUP.md\n"
                f"{'='*70}\n"
            )
    
    def check_quota(self, metric: str, current: int) -> bool:
        """
        Check if quota exceeded
        
        Args:
            metric: Quota type (concepts, dataset_gb)
            current: Current value
            
        Returns:
            True if within quota, False if exceeded
        """
        limits_map = {
            "concepts": self.limits.max_concepts,
            "dataset_gb": self.limits.max_dataset_gb,
        }
        
        limit = limits_map.get(metric, 0)
        
        # 0 = unlimited (enterprise)
        if limit == 0:
            return True
        
        if current >= limit:
            logger.warning(
                f"Quota exceeded: {metric}={current:,} >= limit={limit:,} "
                f"(edition={self.edition.value})"
            )
            return False
        
        # Warn at 80% capacity
        if current >= limit * 0.8:
            logger.warning(
                f"Quota warning: {metric}={current:,} at {current/limit*100:.1f}% "
                f"of limit={limit:,} (edition={self.edition.value})"
            )
        
        return True
    
    def get_rate_limit(self, endpoint: str) -> int:
        """Get rate limit for API endpoint (per minute)"""
        limits_map = {
            "learn": self.limits.learn_per_min,
            "reason": self.limits.reason_per_min,
        }
        return limits_map.get(endpoint, 1000)  # Default
    
    def get_ingest_workers(self) -> int:
        """Get max concurrent ingestion workers"""
        return self.limits.ingest_workers
    
    def get_topology_config(self) -> dict:
        """Get topology configuration for deployment"""
        return {
            "edition": self.edition.value,
            "ha_enabled": self.limits.ha_enabled,
            "grid_enabled": self.limits.grid_enabled,
            "sharded_storage": self.limits.sharded_storage,
            "num_shards": 4 if self.limits.sharded_storage else 1,
            "embedding_replicas": 3 if self.limits.ha_enabled else 1,
            "nlg_replicas": 3 if self.limits.ha_enabled else 1,
        }
    
    def get_edition_info(self) -> dict:
        """Get edition info for UI/monitoring"""
        return {
            "edition": self.edition.value,
            "limits": {
                "learn_per_min": self.limits.learn_per_min,
                "reason_per_min": self.limits.reason_per_min,
                "max_concepts": self.limits.max_concepts,
                "max_dataset_gb": self.limits.max_dataset_gb if self.limits.max_dataset_gb > 0 else "unlimited",
                "ingest_workers": self.limits.ingest_workers,
                "retention_days": self.limits.retention_days,
            },
            "features": {
                "ha_enabled": self.limits.ha_enabled,
                "grid_enabled": self.limits.grid_enabled,
                "sharded_storage": self.limits.sharded_storage,
                "secure_mode": self.limits.secure_mode_required,
            },
            "support": {
                "sla_hours": self.limits.support_sla_hours,
                "type": "dedicated" if self.edition == Edition.ENTERPRISE else "email" if self.edition == Edition.COMMUNITY else "community",
            },
            "upgrade_url": None if self.edition == Edition.ENTERPRISE else "https://sutra.ai/pricing",
        }


# Global singleton
_flags: Optional[FeatureFlags] = None


def get_feature_flags() -> FeatureFlags:
    """Get global feature flags instance (singleton)"""
    global _flags
    if _flags is None:
        _flags = FeatureFlags()
    return _flags


def reset_feature_flags():
    """Reset global instance (for testing)"""
    global _flags
    _flags = None
