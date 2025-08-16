"""
Request models for the Shopify Insights API.
Defines the structure and validation for incoming requests.
"""

from typing import Optional
from pydantic import BaseModel, HttpUrl, validator


class ExtractInsightsRequest(BaseModel):
    """
    Request model for extracting insights from a Shopify store.
    
    Attributes:
        website_url: The URL of the Shopify store to analyze
        include_products: Whether to include product catalog (default: True)
        include_policies: Whether to include policy documents (default: True)
        include_faqs: Whether to include FAQ extraction (default: True)
        include_social: Whether to include social media handles (default: True)
        include_contact: Whether to include contact information (default: True)
        max_products: Maximum number of products to extract (default: 100)
    """
    
    website_url: HttpUrl
    include_products: bool = True
    include_policies: bool = True
    include_faqs: bool = True
    include_social: bool = True
    include_contact: bool = True
    max_products: Optional[int] = 100
    
    @validator("max_products")
    def validate_max_products(cls, v):
        """Validate maximum products limit."""
        if v is not None and (v < 1 or v > 1000):
            raise ValueError("max_products must be between 1 and 1000")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "website_url": "https://example.myshopify.com",
                "include_products": True,
                "include_policies": True,
                "include_faqs": True,
                "include_social": True,
                "include_contact": True,
                "max_products": 100
            }
        }


class HealthCheckRequest(BaseModel):
    """Request model for health check endpoint."""
    
    class Config:
        schema_extra = {
            "example": {}
        }
