"""
Retry utilities for external service calls
Provides exponential backoff and configurable retry logic
"""
import time
import logging
from typing import TypeVar, Callable, Optional, Any
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior"""
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


def retry_with_backoff(
    exceptions: tuple = (Exception,),
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator to retry function calls with exponential backoff
    
    Args:
        exceptions: Tuple of exception types to catch and retry
        config: RetryConfig instance for retry behavior
        on_retry: Optional callback function(exception, attempt) called on each retry
    
    Example:
        @retry_with_backoff(exceptions=(ConnectionError, TimeoutError))
        def call_external_api():
            return requests.get('http://api.example.com')
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            attempt = 0
            delay = config.initial_delay
            
            while attempt < config.max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    
                    if attempt >= config.max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {attempt} attempts: {str(e)}"
                        )
                        raise
                    
                    # Calculate next delay with exponential backoff
                    if config.jitter:
                        import random
                        jitter_delay = delay * (0.5 + random.random())
                    else:
                        jitter_delay = delay
                    
                    actual_delay = min(jitter_delay, config.max_delay)
                    
                    logger.warning(
                        f"{func.__name__} attempt {attempt}/{config.max_attempts} "
                        f"failed: {str(e)}. Retrying in {actual_delay:.2f}s..."
                    )
                    
                    # Call retry callback if provided
                    if on_retry:
                        on_retry(e, attempt)
                    
                    time.sleep(actual_delay)
                    delay *= config.exponential_base
            
            # Should never reach here, but for type safety
            raise RuntimeError(f"{func.__name__} exceeded max retries")
        
        return wrapper
    return decorator


# Async version for async functions
import asyncio
from typing import Coroutine


def async_retry_with_backoff(
    exceptions: tuple = (Exception,),
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator to retry async function calls with exponential backoff
    
    Example:
        @async_retry_with_backoff(exceptions=(aiohttp.ClientError,))
        async def call_external_api():
            async with session.get('http://api.example.com') as resp:
                return await resp.json()
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            attempt = 0
            delay = config.initial_delay
            
            while attempt < config.max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    
                    if attempt >= config.max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {attempt} attempts: {str(e)}"
                        )
                        raise
                    
                    # Calculate next delay with exponential backoff
                    if config.jitter:
                        import random
                        jitter_delay = delay * (0.5 + random.random())
                    else:
                        jitter_delay = delay
                    
                    actual_delay = min(jitter_delay, config.max_delay)
                    
                    logger.warning(
                        f"{func.__name__} attempt {attempt}/{config.max_attempts} "
                        f"failed: {str(e)}. Retrying in {actual_delay:.2f}s..."
                    )
                    
                    # Call retry callback if provided
                    if on_retry:
                        on_retry(e, attempt)
                    
                    await asyncio.sleep(actual_delay)
                    delay *= config.exponential_base
            
            raise RuntimeError(f"{func.__name__} exceeded max retries")
        
        return wrapper
    return decorator


# Predefined retry configs for common scenarios
class RetryConfigs:
    """Predefined retry configurations"""
    
    # Quick retries for fast operations
    FAST = RetryConfig(
        max_attempts=3,
        initial_delay=0.1,
        max_delay=1.0,
        exponential_base=2.0
    )
    
    # Standard retries for most operations
    STANDARD = RetryConfig(
        max_attempts=3,
        initial_delay=1.0,
        max_delay=10.0,
        exponential_base=2.0
    )
    
    # Aggressive retries for critical operations
    AGGRESSIVE = RetryConfig(
        max_attempts=5,
        initial_delay=1.0,
        max_delay=30.0,
        exponential_base=2.0
    )
    
    # Patient retries for slow external services
    PATIENT = RetryConfig(
        max_attempts=3,
        initial_delay=5.0,
        max_delay=60.0,
        exponential_base=2.0
    )
