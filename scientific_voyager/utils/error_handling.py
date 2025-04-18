"""
Error handling utilities for Scientific Voyager.

This module provides error handling and retry mechanisms for network operations
and other potentially failing operations.
"""

import time
import logging
import functools
import random
from typing import Type, Callable, Any, Optional, List, Dict, Union, TypeVar, cast
import traceback
import inspect
from datetime import datetime, timedelta
import threading
from enum import Enum

from scientific_voyager.config.config_manager import get_config

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryStrategy(Enum):
    """Retry strategies for the retry decorator."""
    
    # Fixed delay between retries
    FIXED = "fixed"
    
    # Exponential backoff (delay increases exponentially)
    EXPONENTIAL = "exponential"
    
    # Exponential backoff with jitter (random variation)
    EXPONENTIAL_JITTER = "exponential_jitter"


class RetryableError(Exception):
    """Base class for errors that should be retried."""
    pass


class NetworkError(RetryableError):
    """Error that occurs during network operations."""
    pass


class RateLimitError(RetryableError):
    """Error that occurs when a rate limit is exceeded."""
    pass


class APIError(Exception):
    """Error that occurs during API operations."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Any = None):
        """
        Initialize an API error.
        
        Args:
            message: Error message
            status_code: HTTP status code (if applicable)
            response: API response (if available)
        """
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ErrorHandler:
    """
    Error handler for Scientific Voyager.
    
    This class provides methods for handling errors and retrying operations.
    """
    
    @staticmethod
    def is_retryable_error(error: Exception) -> bool:
        """
        Check if an error should be retried.
        
        Args:
            error: The error to check
            
        Returns:
            True if the error should be retried, False otherwise
        """
        # Check if the error is a RetryableError or a subclass
        if isinstance(error, RetryableError):
            return True
        
        # Check for common network errors
        error_type = type(error).__name__
        if error_type in [
            "ConnectionError", "Timeout", "ConnectTimeout", "ReadTimeout",
            "RequestException", "HTTPError", "ConnectionRefusedError",
            "ConnectionResetError", "ConnectionAbortedError"
        ]:
            return True
        
        # Check for API rate limit errors (status code 429)
        if isinstance(error, APIError) and error.status_code == 429:
            return True
        
        return False
    
    @staticmethod
    def get_retry_delay(
        attempt: int,
        strategy: RetryStrategy,
        base_delay: float,
        max_delay: float
    ) -> float:
        """
        Get the delay before the next retry attempt.
        
        Args:
            attempt: The current attempt number (0-based)
            strategy: The retry strategy
            base_delay: The base delay in seconds
            max_delay: The maximum delay in seconds
            
        Returns:
            The delay in seconds
        """
        if strategy == RetryStrategy.FIXED:
            return base_delay
        
        elif strategy == RetryStrategy.EXPONENTIAL:
            # Exponential backoff: base_delay * 2^attempt
            delay = base_delay * (2 ** attempt)
            return min(delay, max_delay)
        
        elif strategy == RetryStrategy.EXPONENTIAL_JITTER:
            # Exponential backoff with jitter
            delay = base_delay * (2 ** attempt)
            delay = min(delay, max_delay)
            # Add jitter: random value between 0 and delay
            jitter = random.uniform(0, delay * 0.5)
            return delay + jitter
        
        # Default to fixed delay
        return base_delay
    
    @staticmethod
    def format_error(error: Exception) -> str:
        """
        Format an error for logging.
        
        Args:
            error: The error to format
            
        Returns:
            Formatted error string
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        if isinstance(error, APIError) and error.status_code is not None:
            return f"{error_type} (status {error.status_code}): {error_message}"
        
        return f"{error_type}: {error_message}"
    
    @staticmethod
    def log_error(
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        level: int = logging.ERROR
    ) -> None:
        """
        Log an error with context.
        
        Args:
            error: The error to log
            context: Additional context for the error
            level: Logging level (default: ERROR)
        """
        error_message = ErrorHandler.format_error(error)
        
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            message = f"{error_message} [Context: {context_str}]"
        else:
            message = error_message
        
        logger.log(level, message)
        
        # Log traceback for non-retryable errors
        if level >= logging.ERROR and not ErrorHandler.is_retryable_error(error):
            logger.log(level, "Traceback:\n%s", traceback.format_exc())


def retry(
    max_attempts: int = 3,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_JITTER,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_exceptions: Optional[List[Type[Exception]]] = None,
    on_retry: Optional[Callable[[Exception, int, float], None]] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for retrying operations that may fail.
    
    Args:
        max_attempts: Maximum number of attempts (default: 3)
        strategy: Retry strategy (default: EXPONENTIAL_JITTER)
        base_delay: Base delay between retries in seconds (default: 1.0)
        max_delay: Maximum delay between retries in seconds (default: 60.0)
        retryable_exceptions: List of exceptions to retry (default: None)
        on_retry: Callback function called before each retry (default: None)
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            attempt = 0
            
            while True:
                try:
                    return func(*args, **kwargs)
                
                except Exception as e:
                    attempt += 1
                    
                    # Check if we should retry
                    should_retry = False
                    
                    # Check if we've reached the maximum number of attempts
                    if attempt >= max_attempts:
                        # Log the error and re-raise
                        context = {"attempt": attempt, "max_attempts": max_attempts}
                        ErrorHandler.log_error(e, context)
                        raise
                    
                    # Check if the exception is retryable
                    if retryable_exceptions and any(isinstance(e, exc) for exc in retryable_exceptions):
                        should_retry = True
                    elif ErrorHandler.is_retryable_error(e):
                        should_retry = True
                    
                    if not should_retry:
                        # Log the error and re-raise
                        context = {"attempt": attempt, "max_attempts": max_attempts}
                        ErrorHandler.log_error(e, context)
                        raise
                    
                    # Calculate delay before next retry
                    delay = ErrorHandler.get_retry_delay(
                        attempt - 1,  # 0-based for delay calculation
                        strategy,
                        base_delay,
                        max_delay
                    )
                    
                    # Log the retry
                    context = {
                        "attempt": attempt,
                        "max_attempts": max_attempts,
                        "delay": delay
                    }
                    ErrorHandler.log_error(
                        e, context, level=logging.WARNING
                    )
                    
                    # Call the on_retry callback if provided
                    if on_retry:
                        on_retry(e, attempt, delay)
                    
                    # Wait before retrying
                    time.sleep(delay)
        
        return wrapper
    
    return decorator


class RateLimiter:
    """
    Rate limiter for API calls.
    
    This class provides rate limiting for API calls to avoid exceeding API rate limits.
    """
    
    def __init__(self, 
                 calls: int = 10, 
                 period: float = 1.0,
                 raise_on_limit: bool = True):
        """
        Initialize the rate limiter.
        
        Args:
            calls: Maximum number of calls per period (default: 10)
            period: Time period in seconds (default: 1.0)
            raise_on_limit: Whether to raise an exception when the rate limit is exceeded (default: True)
        """
        self.calls = calls
        self.period = period
        self.raise_on_limit = raise_on_limit
        
        self.call_times: List[float] = []
        self.lock = threading.RLock()
        
        logger.info("Initialized rate limiter: %d calls per %.2f seconds", calls, period)
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator for rate-limited functions.
        
        Args:
            func: The function to decorate
            
        Returns:
            Decorated function
        """
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            with self.lock:
                # Remove old call times
                current_time = time.time()
                self.call_times = [t for t in self.call_times if current_time - t <= self.period]
                
                # Check if we've reached the rate limit
                if len(self.call_times) >= self.calls:
                    if self.raise_on_limit:
                        oldest_call = min(self.call_times)
                        wait_time = self.period - (current_time - oldest_call)
                        raise RateLimitError(
                            f"Rate limit exceeded: {self.calls} calls per {self.period} seconds. "
                            f"Try again in {wait_time:.2f} seconds."
                        )
                    else:
                        # Wait until we can make another call
                        oldest_call = min(self.call_times)
                        wait_time = self.period - (current_time - oldest_call)
                        time.sleep(wait_time + 0.01)  # Add a small buffer
                        # Update current time after waiting
                        current_time = time.time()
                
                # Record this call
                self.call_times.append(current_time)
            
            # Call the function
            return func(*args, **kwargs)
        
        return wrapper
    
    def wait_if_needed(self) -> None:
        """
        Wait if necessary to respect the rate limit.
        
        This method can be called directly instead of using the decorator.
        """
        with self.lock:
            # Remove old call times
            current_time = time.time()
            self.call_times = [t for t in self.call_times if current_time - t <= self.period]
            
            # Check if we've reached the rate limit
            if len(self.call_times) >= self.calls:
                # Wait until we can make another call
                oldest_call = min(self.call_times)
                wait_time = self.period - (current_time - oldest_call)
                time.sleep(wait_time + 0.01)  # Add a small buffer
                # Update current time after waiting
                current_time = time.time()
            
            # Record this call
            self.call_times.append(current_time)


def rate_limit(
    calls: int = 10,
    period: float = 1.0,
    raise_on_limit: bool = True
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for rate-limited functions.
    
    Args:
        calls: Maximum number of calls per period (default: 10)
        period: Time period in seconds (default: 1.0)
        raise_on_limit: Whether to raise an exception when the rate limit is exceeded (default: True)
        
    Returns:
        Decorated function
    """
    limiter = RateLimiter(calls=calls, period=period, raise_on_limit=raise_on_limit)
    return limiter
