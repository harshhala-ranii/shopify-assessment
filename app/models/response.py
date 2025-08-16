"""
Response models for the Shopify Insights API.
Defines the structure for API responses and extracted data.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field,validator


class Product(BaseModel):
    """Model representing a product from the Shopify store."""
    
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    price: Optional[str] = None
    compare_at_price: Optional[str] = None
    currency: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    variants: List[Dict[str, Any]] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    product_type: Optional[str] = None
    vendor: Optional[str] = None
    handle: Optional[str] = None
    url: Optional[HttpUrl] = None
    available: Optional[bool] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class BrandInfo(BaseModel):
    """Model representing brand information."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    website_url: HttpUrl
    logo_url: Optional[str] = None
    about_text: Optional[str] = None
    mission_statement: Optional[str] = None


class PolicyDocument(BaseModel):
    """Model representing a policy document."""
    
    title: str
    content: str
    url: Optional[HttpUrl] = None
    last_updated: Optional[str] = None


class FAQ(BaseModel):
    """Model representing a frequently asked question."""
    
    question: str
    answer: str
    category: Optional[str] = None
    url: Optional[HttpUrl] = None


class SocialHandle(BaseModel):
    """Model representing a social media handle."""
    
    platform: str
    handle: str
    url: Optional[HttpUrl] = None
    followers_count: Optional[int] = None


class ContactInfo(BaseModel):
    """Model representing contact information."""
    
    emails: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    addresses: List[str] = Field(default_factory=list)
    contact_form_url: Optional[HttpUrl] = None
    support_hours: Optional[str] = None

    @validator("phone_numbers",pre=True,each_item=True)
    def cast_phone_to_str(cls,v):
        return str(v)


class ImportantLink(BaseModel):
    """Model representing an important link."""
    
    title: str
    url: str
    description: Optional[str] = None
    category: Optional[str] = None


class ProductCatalog(BaseModel):
    """Model representing the product catalog."""
    
    total_count: int
    hero_products: List[Product] = Field(default_factory=list)
    catalog: List[Product] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    collections: List[Dict[str, Any]] = Field(default_factory=list)


class Policies(BaseModel):
    """Model representing store policies."""
    
    privacy_policy: Optional[PolicyDocument] = None
    return_policy: Optional[PolicyDocument] = None
    refund_policy: Optional[PolicyDocument] = None
    shipping_policy: Optional[PolicyDocument] = None
    terms_of_service: Optional[PolicyDocument] = None
    other_policies: List[PolicyDocument] = Field(default_factory=list)


class StoreInsights(BaseModel):
    """Model representing complete store insights."""
    
    brand_info: BrandInfo
    products: ProductCatalog
    policies: Policies
    faqs: List[FAQ] = Field(default_factory=list)
    social_handles: List[SocialHandle] = Field(default_factory=list)
    contact_info: ContactInfo
    important_links: List[ImportantLink] = Field(default_factory=list)
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    extraction_metadata: Dict[str, Any] = Field(default_factory=dict)


class SuccessResponse(BaseModel):
    """Model for successful API responses."""
    
    success: bool = True
    data: StoreInsights
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Model for error API responses."""
    
    success: bool = False
    error: str
    message: str
    status_code: int
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthCheckResponse(BaseModel):
    """Model for health check responses."""
    
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    uptime: Optional[float] = None
    services: Dict[str, str] = Field(default_factory=dict)


class APIResponse(BaseModel):
    """Generic API response wrapper."""
    
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None
    status_code: int = 200
    timestamp: datetime = Field(default_factory=datetime.utcnow)
