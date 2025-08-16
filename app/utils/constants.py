"""
Constants and configuration values for the Shopify Insights application.
Centralizes common patterns, URLs, and configuration values.
"""

import re
from typing import List, Dict, Any

# HTTP Headers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Shopify-specific patterns
SHOPIFY_PRODUCTS_ENDPOINT = "/products.json"
SHOPIFY_COLLECTIONS_ENDPOINT = "/collections.json"
SHOPIFY_PAGES_ENDPOINT = "/pages.json"
SHOPIFY_BLOGS_ENDPOINT = "/blogs.json"

# Common Shopify page patterns
SHOPIFY_PAGE_PATTERNS = {
    "privacy_policy": [
        r"/pages/privacy-policy",
        r"/pages/privacy",
        r"/privacy-policy",
        r"/privacy",
        r"/legal/privacy-policy",
        r"/legal/privacy"
    ],
    "return_policy": [
        r"/pages/return-policy",
        r"/pages/returns",
        r"/return-policy",
        r"/returns",
        r"/shipping-returns",
        r"/shipping-returns/returns"
    ],
    "refund_policy": [
        r"/pages/refund-policy",
        r"/pages/refunds",
        r"/refund-policy",
        r"/refunds",
        r"/shipping-returns/refunds"
    ],
    "shipping_policy": [
        r"/pages/shipping-policy",
        r"/pages/shipping",
        r"/shipping-policy",
        r"/shipping",
        r"/shipping-returns",
        r"/shipping-returns/shipping"
    ],
    "terms_of_service": [
        r"/pages/terms-of-service",
        r"/pages/terms",
        r"/terms-of-service",
        r"/terms",
        r"/legal/terms-of-service",
        r"/legal/terms"
    ],
    "about": [
        r"/pages/about",
        r"/about",
        r"/about-us",
        r"/pages/about-us",
        r"/our-story",
        r"/pages/our-story"
    ],
    "contact": [
        r"/pages/contact",
        r"/contact",
        r"/contact-us",
        r"/pages/contact-us",
        r"/get-in-touch",
        r"/pages/get-in-touch"
    ],
    "faq": [
        r"/pages/faq",
        r"/faq",
        r"/faqs",
        r"/pages/faqs",
        r"/help",
        r"/pages/help",
        r"/support",
        r"/pages/support"
    ]
}

# Social media platform patterns
SOCIAL_MEDIA_PATTERNS = {
    "instagram": [
        r"instagram\.com/([^/\s]+)",
        r"@([^/\s]+)",
        r"instagram: ([^/\s]+)"
    ],
    "facebook": [
        r"facebook\.com/([^/\s]+)",
        r"fb\.com/([^/\s]+)",
        r"facebook: ([^/\s]+)"
    ],
    "twitter": [
        r"twitter\.com/([^/\s]+)",
        r"x\.com/([^/\s]+)",
        r"@([^/\s]+)"
    ],
    "tiktok": [
        r"tiktok\.com/@([^/\s]+)",
        r"@([^/\s]+)"
    ],
    "youtube": [
        r"youtube\.com/([^/\s]+)",
        r"youtu\.be/([^/\s]+)",
        r"youtube: ([^/\s]+)"
    ],
    "linkedin": [
        r"linkedin\.com/([^/\s]+)",
        r"linkedin: ([^/\s]+)"
    ],
    "pinterest": [
        r"pinterest\.com/([^/\s]+)",
        r"pinterest: ([^/\s]+)"
    ]
}

# Contact information patterns
CONTACT_PATTERNS = {
    "email": [
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    ],
    "phone": [
        r"\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})",
        r"\+?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}",
        r"\([0-9]{3}\)[0-9]{3}-[0-9]{4}"
    ]
}

# Important link patterns
IMPORTANT_LINK_PATTERNS = {
    "order_tracking": [
        r"track.*order",
        r"order.*track",
        r"tracking",
        r"order-status",
        r"order.*status"
    ],
    "contact_us": [
        r"contact",
        r"get.*touch",
        r"reach.*us",
        r"support"
    ],
    "blog": [
        r"blog",
        r"news",
        r"articles",
        r"stories"
    ],
    "help": [
        r"help",
        r"faq",
        r"support",
        r"customer.*service"
    ],
    "shipping": [
        r"shipping",
        r"delivery",
        r"shipping.*returns"
    ]
}

# HTML selectors for common elements
HTML_SELECTORS = {
    "product_title": [
        "h1.product-title",
        "h1.product__title",
        ".product-title h1",
        ".product__title h1",
        "h1[class*='title']",
        ".product h1"
    ],
    "product_price": [
        ".price",
        ".product-price",
        ".product__price",
        "[class*='price']",
        ".price__regular",
        ".price__sale"
    ],
    "product_description": [
        ".product-description",
        ".product__description",
        ".description",
        "[class*='description']",
        ".product-details"
    ],
    "product_images": [
        ".product-image img",
        ".product__image img",
        ".product-gallery img",
        "[class*='image'] img",
        ".product img"
    ],
    "social_links": [
        "a[href*='instagram.com']",
        "a[href*='facebook.com']",
        "a[href*='twitter.com']",
        "a[href*='tiktok.com']",
        "a[href*='youtube.com']",
        "a[href*='linkedin.com']",
        "a[href*='pinterest.com']"
    ],
    "contact_info": [
        "a[href^='mailto:']",
        "a[href^='tel:']",
        ".contact-info",
        ".contact__info",
        "[class*='contact']"
    ]
}

# Common text patterns for content extraction
TEXT_PATTERNS = {
    "faq_question": [
        r"Q[:\s]*([^A]+)",
        r"Question[:\s]*([^A]+)",
        r"([^?]+\?)",
        r"([^:]+):"
    ],
    "faq_answer": [
        r"A[:\s]*([^Q]+)",
        r"Answer[:\s]*([^Q]+)",
        r"([^?]+\?)([^Q]+)"
    ],
    "brand_description": [
        r"about.*brand",
        r"our.*story",
        r"mission.*statement",
        r"brand.*story",
        r"who.*we.*are"
    ]
}

# Rate limiting and timeout settings
RATE_LIMIT_SETTINGS = {
    "requests_per_minute": 60,
    "requests_per_hour": 1000,
    "max_concurrent_requests": 5,
    "request_timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1
}

# Content extraction settings
CONTENT_EXTRACTION_SETTINGS = {
    "max_content_length": 10000,
    "min_content_length": 50,
    "max_products_per_request": 250,
    "max_pages_to_crawl": 50,
    "content_cleanup_patterns": [
        r"\s+",
        r"<!--.*?-->",
        r"<script.*?</script>",
        r"<style.*?</style>"
    ]
}

# Error messages
ERROR_MESSAGES = {
    "invalid_url": "Invalid URL format provided",
    "website_not_found": "Website not found or inaccessible",
    "extraction_failed": "Failed to extract content from website",
    "rate_limit_exceeded": "Rate limit exceeded. Please try again later",
    "invalid_shopify_store": "URL does not appear to be a Shopify store",
    "content_too_large": "Content is too large to process",
    "timeout_error": "Request timed out",
    "network_error": "Network error occurred",
    "parsing_error": "Failed to parse website content"
}

# Success messages
SUCCESS_MESSAGES = {
    "extraction_successful": "Successfully extracted insights from store",
    "partial_extraction": "Partially extracted insights from store",
    "health_check": "Service is healthy and running"
}
