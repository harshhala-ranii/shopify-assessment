"""
URL validation service for Shopify stores.
Handles URL validation, normalization, and Shopify store detection.
"""

import re
from typing import Optional
from urllib.parse import urlparse, urlunparse
from app.core.exceptions import ValidationError
from app.utils.constants import SHOPIFY_PAGE_PATTERNS
import requests


class URLValidator:
    """Service for validating and normalizing Shopify store URLs."""
    
    @staticmethod
    def validate_shopify_url(url: str) -> str:
        """
        Validate and normalize a Shopify store URL.
        
        Args:
            url: Raw URL string
            
        Returns:
            Normalized Shopify store URL
            
        Raises:
            ValidationError: If URL is invalid or not a Shopify store
        """
        if not url:
            raise ValidationError("URL cannot be empty")
        
        # Clean the URL
        url = url.strip()
        
        # Ensure protocol is present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Validate URL format
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                raise ValidationError("Invalid URL format")
        except Exception:
            raise ValidationError("Invalid URL format")
        
        # Check if it's a Shopify store
        if not URLValidator._is_shopify_store(url):
            raise ValidationError("URL does not appear to be a Shopify store")
        
        # Normalize the URL
        normalized_url = URLValidator._normalize_url(url)
        
        return normalized_url


    @staticmethod
    def _is_shopify_store(url: str) -> bool:
        """Detect if the given site is a Shopify store."""
        try:
            if not url.startswith("http"):
                url = "https://" + url

            if url.endswith("/"):
                url = url[:-1]

            # 1. Check products.json
            products_url = f"{url}/products.json"
            resp = requests.get(products_url, timeout=8, allow_redirects=True)
            if resp.status_code == 200:
                # Shopify always returns JSON with 'products' key
                try:
                    data = resp.json()
                    if isinstance(data, dict) and "products" in data:
                        return True
                except ValueError:
                    pass  # Not valid JSON → fallback to next check

            # 2. Check shop.json (another Shopify API endpoint)
            shop_url = f"{url}/shop.json"
            resp = requests.get(shop_url, timeout=8, allow_redirects=True)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if isinstance(data, dict) and "shop" in data:
                        return True
                except ValueError:
                    pass

            # 3. Check homepage for Shopify CDN
            resp = requests.get(url, timeout=8, allow_redirects=True)
            if "cdn.shopify.com" in resp.text.lower():
                return True

        except requests.RequestException as e:
            print(f"Error checking {url}: {e}")
            return False

        return False

    
    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalize URL format."""
        parsed = urlparse(url)
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip('/'),
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
        return normalized
    
    @staticmethod
    def build_shopify_endpoint(base_url: str, endpoint: str) -> str:
        """Build a complete Shopify API endpoint URL."""
        base_url = base_url.rstrip('/')
        endpoint = endpoint.lstrip('/')
        return f"{base_url}/{endpoint}"
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return ""
