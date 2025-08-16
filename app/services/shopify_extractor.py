"""
Main Shopify extraction service.
Orchestrates the entire extraction process for Shopify stores.
"""

import json
import time
from typing import Dict, Any, List, Optional
import requests
from app.core.exceptions import (
    WebsiteNotFoundError,
    WebsiteAccessError,
    ContentExtractionError
)
from app.core.config import get_settings
from app.services.url_validator import URLValidator
from app.services.content_parser import ContentParser
from app.services.llm_processor import LLMProcessor
from app.models.response import (
    StoreInsights,
    BrandInfo,
    ProductCatalog,
    Policies,
    FAQ,
    SocialHandle,
    ContactInfo,
    ImportantLink,
    Product,
    PolicyDocument
)
from app.utils.constants import (
    SHOPIFY_PRODUCTS_ENDPOINT,
    SHOPIFY_PAGES_ENDPOINT,
    DEFAULT_HEADERS,
    SHOPIFY_PAGE_PATTERNS
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class ShopifyExtractor:
    """Main service for extracting insights from Shopify stores."""
    
    def __init__(self):
        self.settings = get_settings()
        self.url_validator = URLValidator()
        self.content_parser = ContentParser()
        self.llm_processor = LLMProcessor() if self.settings.openai_api_key else None
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
    
    def extract_insights(self, website_url: str, **kwargs) -> StoreInsights:
        """
        Extract comprehensive insights from a Shopify store.
        
        Args:
            website_url: URL of the Shopify store
            **kwargs: Additional extraction options
            
        Returns:
            StoreInsights object with extracted data
        """
        logger.info(f"Starting extraction for: {website_url}")
        
        # Validate and normalize URL
        normalized_url = self.url_validator.validate_shopify_url(website_url)
        
        # Extract homepage content
        homepage_content = self._fetch_homepage(normalized_url)
        
        # Extract products
        products_data = self._extract_products(normalized_url, **kwargs)
        
        # Extract policies and other pages
        policies_data = self._extract_policies(normalized_url)
        
        # Extract FAQs
        faqs_data = self._extract_faqs(normalized_url)
        
        # Extract social handles and contact info
        social_data = self._extract_social_and_contact(homepage_content, normalized_url)
        
        # Extract important links
        important_links = self._extract_important_links(homepage_content, normalized_url)
        
        # Build brand info
        brand_info = self._build_brand_info(homepage_content, normalized_url)
        
        # Create StoreInsights object
        store_insights = StoreInsights(
            brand_info=brand_info,
            products=products_data,
            policies=policies_data,
            faqs=faqs_data,
            social_handles=social_data['social_handles'],
            contact_info=social_data['contact_info'],
            important_links=important_links,
            extraction_metadata={
                'source_url': normalized_url,
                'extraction_timestamp': time.time(),
                'extraction_options': kwargs
            }
        )
        
        logger.info(f"Successfully extracted insights for: {normalized_url}")
        return store_insights
    
    def _fetch_homepage(self, url: str) -> str:
        """Fetch homepage content."""
        try:
            response = self.session.get(url, timeout=self.settings.request_timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch homepage: {e}")
            raise WebsiteAccessError(f"Failed to access website: {str(e)}")
    
    def _extract_products(self, base_url: str, **kwargs) -> ProductCatalog:
        """Extract product catalog from Shopify store."""
        try:
            products_url = self.url_validator.build_shopify_endpoint(
                base_url, SHOPIFY_PRODUCTS_ENDPOINT
            )
            
            response = self.session.get(products_url, timeout=self.settings.request_timeout)
            response.raise_for_status()
            
            products_data = response.json()
            products = products_data.get('products', [])
            
            # Convert to Product objects
            product_objects = []
            for product in products:
                product_obj = Product(
                    id=str(product.get('id', '')),
                    title=product.get('title', ''),
                    description=product.get('body_html', ''),
                    price=product.get('variants', [{}])[0].get('price', '') if product.get('variants') else None,
                    images=[img.get('src', '') for img in product.get('images', [])],
                    variants=product.get('variants', []),
                    tags=product.get('tags', []),
                    product_type=product.get('product_type', ''),
                    vendor=product.get('vendor', ''),
                    handle=product.get('handle', ''),
                    url=f"{base_url}/products/{product.get('handle', '')}",
                    available=product.get('published_at') is not None,
                    created_at=product.get('created_at', ''),
                    updated_at=product.get('updated_at', '')
                )
                product_objects.append(product_obj)
            
            # Identify hero products (first few products)
            hero_products = product_objects[:5] if len(product_objects) > 5 else product_objects
            
            return ProductCatalog(
                total_count=len(product_objects),
                hero_products=hero_products,
                catalog=product_objects,
                categories=list(set(p.product_type for p in product_objects if p.product_type)),
                collections=[]
            )
            
        except Exception as e:
            logger.error(f"Failed to extract products: {e}")
            return ProductCatalog(total_count=0)
    
    def _extract_policies(self, base_url: str) -> Policies:
        """Extract policy documents from Shopify store."""
        policies = Policies()
        
        try:
            # Try to fetch pages
            pages_url = self.url_validator.build_shopify_endpoint(
                base_url, SHOPIFY_PAGES_ENDPOINT
            )
            
            response = self.session.get(pages_url, timeout=self.settings.request_timeout)
            if response.status_code == 200:
                pages_data = response.json()
                pages = pages_data.get('pages', [])
                
                for page in pages:
                    page_handle = page.get('handle', '').lower()
                    page_title = page.get('title', '')
                    page_content = page.get('body_html', '')
                    
                    # Map page to policy type
                    if any(pattern in page_handle for pattern in ['privacy', 'privacy-policy']):
                        policies.privacy_policy = PolicyDocument(
                            title=page_title,
                            content=self.content_parser.clean_text(page_content),
                            url=f"{base_url}/pages/{page_handle}"
                        )
                    elif any(pattern in page_handle for pattern in ['return', 'returns']):
                        policies.return_policy = PolicyDocument(
                            title=page_title,
                            content=self.content_parser.clean_text(page_content),
                            url=f"{base_url}/pages/{page_handle}"
                        )
                    elif any(pattern in page_handle for pattern in ['refund', 'refunds']):
                        policies.refund_policy = PolicyDocument(
                            title=page_title,
                            content=self.content_parser.clean_text(page_content),
                            url=f"{base_url}/pages/{page_handle}"
                        )
                    elif any(pattern in page_handle for pattern in ['shipping']):
                        policies.shipping_policy = PolicyDocument(
                            title=page_title,
                            content=self.content_parser.clean_text(page_content),
                            url=f"{base_url}/pages/{page_handle}"
                        )
                    elif any(pattern in page_handle for pattern in ['terms']):
                        policies.terms_of_service = PolicyDocument(
                            title=page_title,
                            content=self.content_parser.clean_text(page_content),
                            url=f"{base_url}/pages/{page_handle}"
                        )
        
        except Exception as e:
            logger.warning(f"Failed to extract policies: {e}")
        
        return policies
    
    def _extract_faqs(self, base_url: str) -> List[FAQ]:
        """Extract FAQ content from Shopify store."""
        faqs = []
        
        try:
            # Try to find FAQ page
            faq_urls = [
                f"{base_url}/pages/faq",
                f"{base_url}/pages/faqs",
                f"{base_url}/pages/help",
                f"{base_url}/pages/support"
            ]
            
            for faq_url in faq_urls:
                try:
                    response = self.session.get(faq_url, timeout=self.settings.request_timeout)
                    if response.status_code == 200:
                        self.content_parser.parse_html(response.text)
                        extracted_faqs = self.content_parser.extract_faqs()
                        
                        for faq in extracted_faqs:
                            faqs.append(FAQ(
                                question=faq['question'],
                                answer=faq['answer'],
                                url=faq_url
                            ))
                        
                        if faqs:
                            break
                            
                except Exception as e:
                    logger.debug(f"Failed to extract FAQs from {faq_url}: {e}")
                    continue
        
        except Exception as e:
            logger.warning(f"Failed to extract FAQs: {e}")
        
        return faqs
    
    def _extract_social_and_contact(self, homepage_content: str, base_url: str) -> Dict[str, Any]:
        """Extract social media handles and contact information."""
        self.content_parser.parse_html(homepage_content)
        
        # Extract contact info
        contact_data = self.content_parser.extract_contact_info()
        contact_info = ContactInfo(
            emails=contact_data['emails'],
            phone_numbers=contact_data['phone_numbers']
        )
        
        # Extract social handles
        social_handles = []
        extracted_social = self.content_parser.extract_social_handles()
        
        for social in extracted_social:
            social_handles.append(SocialHandle(
                platform=social['platform'],
                handle=social['handle'],
                url=social['url']
            ))
        
        return {
            'social_handles': social_handles,
            'contact_info': contact_info
        }
    
    def _extract_important_links(self, homepage_content: str, base_url: str) -> List[ImportantLink]:
        """Extract important links from homepage."""
        self.content_parser.parse_html(homepage_content)
        extracted_links = self.content_parser.extract_important_links(base_url)
        
        important_links = []
        for link in extracted_links:
            important_links.append(ImportantLink(
                title=link['title'],
                url=link['url'],
                category=link.get('category', 'other')
            ))
        
        return important_links
    
    def _build_brand_info(self, homepage_content: str, base_url: str) -> BrandInfo:
        """Build brand information from homepage content."""
        self.content_parser.parse_html(homepage_content)
        extracted_brand = self.content_parser.extract_brand_info()
        
        return BrandInfo(
            name=extracted_brand.get('name', ''),
            description=extracted_brand.get('description', ''),
            website_url=base_url,
            about_text=extracted_brand.get('about_text', '')
        )
    
    def __del__(self):
        """Cleanup session on deletion."""
        if hasattr(self, 'session'):
            self.session.close()
