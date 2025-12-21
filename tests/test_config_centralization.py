"""
Comprehensive tests for centralized configuration system.

Validates:
- Edition configuration consistency
- Storage configuration injection
- Type mapping centralization
- Cross-component validation
- Circuit breaker functionality
"""

import os
import pytest
from unittest.mock import patch

from sutra_core.config.edition import (
    Edition,
    EditionSpec,
    EDITION_SPECS,
    get_edition_spec,
    validate_edition_consistency,
)
from sutra_core.config.storage import StorageConfig, create_storage_config
from sutra_core.config.system import (
    ASSOCIATION_TYPE_MAP,
    association_type_to_int,
    int_to_association_type,
    get_vector_dimension,
    SYSTEM_CONFIG,
)
from sutra_core.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerState, CircuitBreakerError
from sutra_core.graph.concepts import AssociationType


class TestEditionConfiguration:
    """Test centralized edition configuration."""

    def test_edition_specs_exist_for_all_editions(self):
        """All editions have complete specifications."""
        assert Edition.SIMPLE in EDITION_SPECS
        assert Edition.COMMUNITY in EDITION_SPECS
        assert Edition.ENTERPRISE in EDITION_SPECS

    def test_simple_edition_spec(self):
        """Simple edition has correct specification."""
        spec = EDITION_SPECS[Edition.SIMPLE]
        assert spec.edition == Edition.SIMPLE
        assert spec.price_usd == 0
        assert spec.num_shards == 1
        assert spec.ha_enabled is False
        assert spec.grid_enabled is False
        assert spec.max_concepts == 100_000
        assert spec.learn_per_min == 10

    def test_community_edition_spec(self):
        """Community edition has correct specification."""
        spec = EDITION_SPECS[Edition.COMMUNITY]
        assert spec.edition == Edition.COMMUNITY
        assert spec.price_usd == 99
        assert spec.num_shards == 1
        assert spec.ha_enabled is True  # HA embedding
        assert spec.grid_enabled is False
        assert spec.max_concepts == 1_000_000
        assert spec.learn_per_min == 100
        assert spec.embedding_replicas == 3

    def test_enterprise_edition_spec(self):
        """Enterprise edition has correct specification."""
        spec = EDITION_SPECS[Edition.ENTERPRISE]
        assert spec.edition == Edition.ENTERPRISE
        assert spec.price_usd == 999
        assert spec.num_shards == 16  # Sharded storage
        assert spec.ha_enabled is True
        assert spec.grid_enabled is True
        assert spec.max_concepts == 10_000_000
        assert spec.learn_per_min == 1000
        assert spec.secure_mode_required is True

    def test_edition_spec_validation_enterprise_shards(self):
        """Enterprise edition requires minimum 4 shards."""
        # Valid enterprise spec
        valid_spec = EDITION_SPECS[Edition.ENTERPRISE]
        valid_spec.validate()  # Should not raise

        # Invalid enterprise spec (would need to create manually)
        # Just verify the existing specs all validate
        for spec in EDITION_SPECS.values():
            spec.validate()

    @patch.dict(os.environ, {"SUTRA_EDITION": "simple"})
    def test_get_edition_spec_from_env(self):
        """get_edition_spec() reads from SUTRA_EDITION env var."""
        spec = get_edition_spec()
        assert spec.edition == Edition.SIMPLE

    @patch.dict(os.environ, {"SUTRA_EDITION": "enterprise"})
    def test_get_edition_spec_enterprise(self):
        """get_edition_spec() correctly loads enterprise."""
        spec = get_edition_spec()
        assert spec.edition == Edition.ENTERPRISE
        assert spec.num_shards == 16

    def test_get_edition_spec_override(self):
        """edition_override parameter takes precedence over env var."""
        spec = get_edition_spec(edition_override="community")
        assert spec.edition == Edition.COMMUNITY

    def test_get_edition_spec_invalid_edition(self):
        """Invalid edition raises ValueError."""
        with pytest.raises(ValueError, match="Invalid edition"):
            get_edition_spec(edition_override="invalid")

    def test_validate_edition_consistency_simple(self):
        """Simple edition with num_shards=1 is valid."""
        validate_edition_consistency(Edition.SIMPLE, num_shards=1)

    def test_validate_edition_consistency_enterprise_valid(self):
        """Enterprise edition with num_shards=16 is valid."""
        validate_edition_consistency(Edition.ENTERPRISE, num_shards=16)

    def test_validate_edition_consistency_enterprise_invalid(self):
        """Enterprise edition with num_shards=1 is invalid."""
        with pytest.raises(ValueError, match="Enterprise edition requires"):
            validate_edition_consistency(Edition.ENTERPRISE, num_shards=1)

    def test_validate_edition_consistency_simple_too_many_shards(self):
        """Simple edition with num_shards > 1 is invalid."""
        with pytest.raises(ValueError, match="single-node"):
            validate_edition_consistency(Edition.SIMPLE, num_shards=16)


class TestStorageConfiguration:
    """Test storage configuration class."""

    @patch.dict(os.environ, {"SUTRA_STORAGE_SERVER": "localhost:50051", "SUTRA_EDITION": "simple"})
    def test_create_storage_config_from_env(self):
        """create_storage_config() reads from environment."""
        config = create_storage_config()
        assert config.server_address == "localhost:50051"
        assert config.edition == Edition.SIMPLE
        assert config.vector_dimension == 768

    def test_create_storage_config_explicit(self):
        """create_storage_config() accepts explicit parameters."""
        config = create_storage_config(
            server_address="custom:9999",
            edition_override="enterprise",
        )
        assert config.server_address == "custom:9999"
        assert config.edition == Edition.ENTERPRISE

    def test_storage_config_vector_dimension_from_model(self):
        """Vector dimension auto-detected from edition's embedding model."""
        config = create_storage_config(edition_override="enterprise")
        # Enterprise uses nomic-embed-text-v1.5 (768D)
        assert config.vector_dimension == 768

    def test_storage_config_defaults(self):
        """Storage config has sensible defaults."""
        config = create_storage_config()
        assert config.timeout_seconds == SYSTEM_CONFIG.TCP_TIMEOUT_SECONDS
        assert config.max_retries == SYSTEM_CONFIG.TCP_MAX_RETRIES
        assert config.circuit_breaker_enabled is True

    def test_storage_config_validation_empty_address(self):
        """Storage config validates server_address."""
        with pytest.raises(ValueError, match="server address is required"):
            StorageConfig(
                server_address="",
                timeout_seconds=30,
                max_retries=3,
                vector_dimension=768,
                edition=Edition.SIMPLE,
            ).validate()


class TestSystemConstants:
    """Test centralized system constants and type mappings."""

    def test_association_type_map_complete(self):
        """All association types have mappings."""
        assert AssociationType.SEMANTIC in ASSOCIATION_TYPE_MAP
        assert AssociationType.CAUSAL in ASSOCIATION_TYPE_MAP
        assert AssociationType.TEMPORAL in ASSOCIATION_TYPE_MAP
        assert AssociationType.HIERARCHICAL in ASSOCIATION_TYPE_MAP
        assert AssociationType.COMPOSITIONAL in ASSOCIATION_TYPE_MAP

    def test_association_type_map_values(self):
        """Association types map to correct integers (matching Rust)."""
        assert ASSOCIATION_TYPE_MAP[AssociationType.SEMANTIC] == 0
        assert ASSOCIATION_TYPE_MAP[AssociationType.CAUSAL] == 1
        assert ASSOCIATION_TYPE_MAP[AssociationType.TEMPORAL] == 2
        assert ASSOCIATION_TYPE_MAP[AssociationType.HIERARCHICAL] == 3
        assert ASSOCIATION_TYPE_MAP[AssociationType.COMPOSITIONAL] == 4

    def test_association_type_to_int(self):
        """association_type_to_int() converts enum to int."""
        assert association_type_to_int(AssociationType.SEMANTIC) == 0
        assert association_type_to_int(AssociationType.CAUSAL) == 1

    def test_association_type_to_int_string_value(self):
        """association_type_to_int() handles string values."""
        assert association_type_to_int("semantic") == 0
        assert association_type_to_int("causal") == 1

    def test_int_to_association_type(self):
        """int_to_association_type() converts int to enum."""
        assert int_to_association_type(0) == AssociationType.SEMANTIC
        assert int_to_association_type(1) == AssociationType.CAUSAL
        assert int_to_association_type(4) == AssociationType.COMPOSITIONAL

    def test_int_to_association_type_invalid(self):
        """int_to_association_type() raises on invalid value."""
        with pytest.raises(ValueError, match="Unknown association type integer"):
            int_to_association_type(999)

    def test_get_vector_dimension(self):
        """get_vector_dimension() returns correct dimensions."""
        assert get_vector_dimension("nomic-embed-text-v1.5") == 768
        assert get_vector_dimension("google/embeddinggemma-300m") == 768
        assert get_vector_dimension("unknown-model") == 768  # Default

    def test_system_config_constants(self):
        """System config has expected constants."""
        assert SYSTEM_CONFIG.VECTOR_DIM_DEFAULT == 768
        assert SYSTEM_CONFIG.TCP_DEFAULT_PORT == 50051
        assert SYSTEM_CONFIG.TCP_TIMEOUT_SECONDS == 30
        assert SYSTEM_CONFIG.TCP_MAX_RETRIES == 3
        assert SYSTEM_CONFIG.TCP_RETRY_BACKOFF_BASE == 0.5


class TestCircuitBreaker:
    """Test circuit breaker pattern."""

    def test_circuit_breaker_initial_state(self):
        """Circuit breaker starts in CLOSED state."""
        breaker = CircuitBreaker(name="test")
        assert breaker.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_successful_call(self):
        """Successful calls keep circuit CLOSED."""
        breaker = CircuitBreaker(name="test")

        def success_func():
            return "success"

        result = breaker.call(success_func)
        assert result == "success"
        assert breaker.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_opens_after_failures(self):
        """Circuit opens after failure threshold."""
        breaker = CircuitBreaker(name="test")
        breaker.config.failure_threshold = 3

        def fail_func():
            raise RuntimeError("Service failed")

        # Fail 3 times (threshold)
        for _ in range(3):
            with pytest.raises(RuntimeError):
                breaker.call(fail_func)

        # Circuit should now be OPEN
        assert breaker.state == CircuitBreakerState.OPEN

    def test_circuit_breaker_open_fails_fast(self):
        """Open circuit fails fast without calling function."""
        breaker = CircuitBreaker(name="test")
        breaker.config.failure_threshold = 1

        def fail_func():
            raise RuntimeError("Service failed")

        # Open the circuit
        with pytest.raises(RuntimeError):
            breaker.call(fail_func)

        assert breaker.state == CircuitBreakerState.OPEN

        # Next call should fail fast with CircuitBreakerError
        with pytest.raises(CircuitBreakerError, match="Circuit breaker .* is OPEN"):
            breaker.call(lambda: "should not execute")

    def test_circuit_breaker_manual_reset(self):
        """Manual reset closes circuit."""
        breaker = CircuitBreaker(name="test")
        breaker.config.failure_threshold = 1

        # Open circuit
        with pytest.raises(RuntimeError):
            breaker.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))

        assert breaker.state == CircuitBreakerState.OPEN

        # Manual reset
        breaker.reset()
        assert breaker.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_stats(self):
        """Circuit breaker provides statistics."""
        breaker = CircuitBreaker(name="test_service")
        stats = breaker.get_stats()

        assert stats["name"] == "test_service"
        assert stats["state"] == "closed"
        assert stats["failure_count"] == 0
        assert "config" in stats


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""

    def test_feature_flags_edition_limits(self):
        """feature_flags.EditionLimits wraps EditionSpec correctly."""
        from sutra_core.feature_flags import EditionLimits

        spec = EDITION_SPECS[Edition.ENTERPRISE]
        limits = EditionLimits(spec)

        assert limits.learn_per_min == 1000
        assert limits.max_concepts == 10_000_000
        assert limits.sharded_storage is True  # num_shards > 1
        assert limits.ha_enabled is True

    def test_feature_flags_edition_limits_dict(self):
        """feature_flags.EDITION_LIMITS dict is populated."""
        from sutra_core.feature_flags import EDITION_LIMITS

        assert Edition.SIMPLE in EDITION_LIMITS
        assert Edition.COMMUNITY in EDITION_LIMITS
        assert Edition.ENTERPRISE in EDITION_LIMITS

    @patch.dict(os.environ, {"SUTRA_EDITION": "enterprise"})
    def test_feature_flags_class_uses_centralized_config(self):
        """FeatureFlags class uses centralized edition config."""
        from sutra_core.feature_flags import FeatureFlags

        flags = FeatureFlags()
        assert flags.edition == Edition.ENTERPRISE
        assert flags.limits.learn_per_min == 1000


class TestNoDuplication:
    """Test that type mappings are not duplicated."""

    def test_tcp_adapter_uses_centralized_mapping(self):
        """tcp_adapter.py imports from config.system, not defining own mapping."""
        from sutra_core.storage.tcp_adapter import TcpStorageAdapter
        import inspect

        source = inspect.getsource(TcpStorageAdapter)

        # Should NOT contain hardcoded type_map definitions
        assert 'type_map = {' not in source or source.count('type_map = {') == 0
        # Should import from config.system
        module_source = inspect.getsource(inspect.getmodule(TcpStorageAdapter))
        assert 'from ..config.system import' in module_source

    def test_reasoning_engine_uses_storage_config(self):
        """reasoning/engine.py uses StorageConfig, not hardcoded values."""
        from sutra_core.reasoning.engine import ReasoningEngine
        import inspect

        init_source = inspect.getsource(ReasoningEngine.__init__)

        # Should import create_storage_config
        module_source = inspect.getsource(inspect.getmodule(ReasoningEngine))
        assert 'create_storage_config' in module_source

        # Should NOT contain hardcoded vector_dim = 768
        # (It might appear in comments, so check for assignment)
        assert 'vector_dim = 768' not in init_source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
