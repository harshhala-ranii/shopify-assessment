"""
Helper utility functions for the Shopify Insights application.
"""

import re
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import json
from app.core.logging import get_logger

logger = get_logger(__name__)


def clean_url(url: str) -> str:
    """Clean and normalize a URL."""
    if not url:
        return ""
    
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return list(set(email.lower() for email in emails))


def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text."""
    phone_patterns = [
        r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
        r'\+?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}'
    ]
    
    phone_numbers = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        phone_numbers.extend(matches)
    
    return list(set(phone_numbers))


def clean_text(text: str, max_length: Optional[int] = None) -> str:
    """Clean and normalize text content."""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    # Truncate if max_length is specified
    if max_length and len(text) > max_length:
        text = text[:max_length].rsplit(' ', 1)[0] + "..."
    
    return text


def is_shopify_store(url: str) -> bool:
    """Check if a URL appears to be a Shopify store."""
    shopify_indicators = [
        '.myshopify.com',
        'shopify.com',
        '/products',
        '/collections'
    ]
    
    url_lower = url.lower()
    return any(indicator in url_lower for indicator in shopify_indicators)

def sanitize_json(content: str, fallback: Any) -> Any:
    if not content:
        return fallback
    try:
        # Strip markdown fences if present
        content = content.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(content)
    except Exception as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return fallback