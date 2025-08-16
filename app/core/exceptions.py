"""
Custom exception classes for the Shopify Insights application.
Provides structured error handling with appropriate HTTP status codes.
"""

from typing import Any, Dict, Optional


class ShopifyInsightsException(Exception):
    """Base exception class for Shopify Insights application."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ShopifyInsightsException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class WebsiteNotFoundError(ShopifyInsightsException):
    """Raised when the target website cannot be found or accessed."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)


class WebsiteAccessError(ShopifyInsightsException):
    """Raised when the target website is inaccessible."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)


class ContentExtractionError(ShopifyInsightsException):
    """Raised when content extraction fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class LLMProcessingError(ShopifyInsightsException):
    """Raised when LLM processing fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class RateLimitError(ShopifyInsightsException):
    """Raised when rate limiting is exceeded."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=429, details=details)


class ConfigurationError(ShopifyInsightsException):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)
