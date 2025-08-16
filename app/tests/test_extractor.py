"""
Tests for the Shopify extractor service.
"""

import pytest
from unittest.mock import Mock, patch
from app.services.shopify_extractor import ShopifyExtractor
from app.core.exceptions import WebsiteAccessError, ValidationError


class TestShopifyExtractor:
    """Test cases for ShopifyExtractor service."""
    
    def setup_method(self):
        """Setup method for each test."""
        self.extractor = ShopifyExtractor()
    
    def test_extractor_initialization(self):
        """Test extractor initialization."""
        assert self.extractor is not None
        assert hasattr(self.extractor, 'url_validator')
        assert hasattr(self.extractor, 'content_parser')
    
    @patch('app.services.shopify_extractor.requests.Session')
    def test_fetch_homepage_success(self, mock_session):
        """Test successful homepage fetching."""
        # Mock successful response
        mock_response = Mock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.raise_for_status.return_value = None
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Test
        content = self.extractor._fetch_homepage("https://test.myshopify.com")
        assert content == "<html><body>Test content</body></html>"
    
    @patch('app.services.shopify_extractor.requests.Session')
    def test_fetch_homepage_failure(self, mock_session):
        """Test homepage fetching failure."""
        # Mock failed response
        mock_session_instance = Mock()
        mock_session_instance.get.side_effect = Exception("Connection failed")
        mock_session.return_value = mock_session_instance
        
        # Test
        with pytest.raises(WebsiteAccessError):
            self.extractor._fetch_homepage("https://test.myshopify.com")
    
    def test_extract_products_empty_response(self):
        """Test product extraction with empty response."""
        with patch.object(self.extractor, '_fetch_products_json') as mock_fetch:
            mock_fetch.return_value = {"products": []}
            
            result = self.extractor._extract_products("https://test.myshopify.com")
            assert result.total_count == 0
            assert len(result.catalog) == 0
    
    def test_extract_policies_empty(self):
        """Test policy extraction with no policies."""
        with patch.object(self.extractor, '_fetch_pages_json') as mock_fetch:
            mock_fetch.return_value = {"pages": []}
            
            result = self.extractor._extract_policies("https://test.myshopify.com")
            assert result.privacy_policy is None
            assert result.return_policy is None
    
    def test_extract_faqs_empty(self):
        """Test FAQ extraction with no FAQs."""
        result = self.extractor._extract_faqs("https://test.myshopify.com")
        assert len(result) == 0
    
    def test_build_brand_info(self):
        """Test brand info building."""
        homepage_content = """
        <html>
            <head>
                <title>Test Brand</title>
                <meta name="description" content="Test brand description">
            </head>
            <body>
                <div class="about">About our brand</div>
            </body>
        </html>
        """
        
        result = self.extractor._build_brand_info(homepage_content, "https://test.myshopify.com")
        assert result.website_url == "https://test.myshopify.com"
    
    def test_extract_social_and_contact(self):
        """Test social media and contact extraction."""
        homepage_content = """
        <html>
            <body>
                <a href="https://instagram.com/testbrand">Instagram</a>
                <a href="mailto:contact@testbrand.com">Contact</a>
            </body>
        </html>
        """
        
        result = self.extractor._extract_social_and_contact(homepage_content, "https://test.myshopify.com")
        assert 'social_handles' in result
        assert 'contact_info' in result
    
    def test_extract_important_links(self):
        """Test important links extraction."""
        homepage_content = """
        <html>
            <body>
                <a href="/contact">Contact Us</a>
                <a href="/track-order">Track Order</a>
            </body>
        </html>
        """
        
        result = self.extractor._extract_important_links(homepage_content, "https://test.myshopify.com")
        assert len(result) > 0
    
    def test_cleanup(self):
        """Test extractor cleanup."""
        # This should not raise any errors
        del self.extractor


if __name__ == "__main__":
    pytest.main([__file__])
