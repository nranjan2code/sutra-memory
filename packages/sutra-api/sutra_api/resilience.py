"""
Simple resilience helpers for service communication.
Implements basic retry logic and graceful degradation.
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


def retry_on_failure(
    max_retries: int = 3,
    backoff_seconds: float = 0.5,
    exceptions: tuple = (Exception,)
):
    """
    Simple retry decorator for flaky service calls.
    
    Usage:
        @retry_on_failure(max_retries=3)
        def call_storage():
            return storage_client.query(...)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = backoff_seconds * (2 ** attempt)  # Exponential backoff
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}. "
                            f"Retrying in {wait_time}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries} attempts: {e}")
            
            # All retries exhausted
            raise last_exception
        
        return wrapper
    return decorator


class CircuitBreaker:
    """
    Dead simple circuit breaker pattern.
    Opens circuit after N failures, closes after success.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        name: str = "unknown"
    ):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.name = name
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.is_open = False
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        
        # Check if circuit should close (timeout expired)
        if self.is_open and self.last_failure_time:
            if time.time() - self.last_failure_time > self.timeout_seconds:
                logger.info(f"Circuit breaker '{self.name}' - attempting to close after timeout")
                self.is_open = False
                self.failure_count = 0
        
        # Circuit is open - fail fast
        if self.is_open:
            raise Exception(
                f"Circuit breaker '{self.name}' is OPEN - service unavailable. "
                f"Will retry in {self.timeout_seconds}s"
            )
        
        # Try the operation
        try:
            result = func(*args, **kwargs)
            # Success - reset failure count
            if self.failure_count > 0:
                logger.info(f"Circuit breaker '{self.name}' - service recovered")
            self.failure_count = 0
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            # Open circuit if threshold reached
            if self.failure_count >= self.failure_threshold:
                self.is_open = True
                logger.error(
                    f"Circuit breaker '{self.name}' - OPENED after {self.failure_count} failures. "
                    f"Service marked as down for {self.timeout_seconds}s"
                )
            
            raise e


# Global circuit breakers for services
_circuit_breakers = {}


def get_circuit_breaker(service_name: str) -> CircuitBreaker:
    """Get or create circuit breaker for a service."""
    if service_name not in _circuit_breakers:
        _circuit_breakers[service_name] = CircuitBreaker(
            failure_threshold=5,
            timeout_seconds=60,
            name=service_name
        )
    return _circuit_breakers[service_name]


def with_fallback(fallback_value: Any = None):
    """
    Return fallback value instead of raising exception.
    
    Usage:
        @with_fallback(fallback_value={"status": "degraded"})
        def get_stats():
            return storage_client.get_stats()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(
                    f"{func.__name__} failed: {e}. Returning fallback value."
                )
                return fallback_value
        return wrapper
    return decorator
