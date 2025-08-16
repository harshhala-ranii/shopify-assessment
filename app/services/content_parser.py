"""
Content parsing service for extracting information from HTML content.
Handles HTML parsing, text extraction, and content cleaning.
"""

import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from app.core.exceptions import ContentExtractionError
from app.utils.constants import (
    HTML_SELECTORS,
    CONTACT_PATTERNS,
    SOCIAL_MEDIA_PATTERNS,
    IMPORTANT_LINK_PATTERNS
)


class ContentParser:
    """Service for parsing HTML content and extracting structured information."""
    
    def __init__(self):
        self.soup = None
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """
        Parse HTML content using BeautifulSoup.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            BeautifulSoup object for parsing
        """
        try:
            self.soup = BeautifulSoup(html_content, 'html.parser')
            return self.soup
        except Exception as e:
            raise ContentExtractionError(f"Failed to parse HTML: {str(e)}")
    
    def extract_text(self, selector: str = None) -> str:
        """
        Extract text content from HTML.
        
        Args:
            selector: CSS selector for specific element
            
        Returns:
            Extracted text content
        """
        if not self.soup:
            return ""
        
        try:
            if selector:
                element = self.soup.select_one(selector)
                return element.get_text(strip=True) if element else ""
            else:
                return self.soup.get_text(strip=True)
        except Exception:
            return ""
    
    def extract_links(self, base_url: str = None) -> List[Dict[str, str]]:
        """
        Extract all links from HTML content.
        
        Args:
            base_url: Base URL for resolving relative links
            
        Returns:
            List of link dictionaries with text and URL
        """
        if not self.soup:
            return []
        
        links = []
        try:
            for link in self.soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if href and text:
                    # Resolve relative URLs
                    if base_url and not href.startswith(('http://', 'https://')):
                        href = f"{base_url.rstrip('/')}/{href.lstrip('/')}"
                    
                    links.append({
                        'text': text,
                        'url': href
                    })
        except Exception:
            pass
        
        return links
    
    def extract_contact_info(self) -> Dict[str, List[str]]:
        """
        Extract contact information from HTML content.
        
        Returns:
            Dictionary with emails and phone numbers
        """
        if not self.soup:
            return {'emails': [], 'phone_numbers': []}
        
        text_content = self.soup.get_text()
        
        # Extract emails
        emails = re.findall(CONTACT_PATTERNS['email'][0], text_content)
        emails = list(set(email.lower() for email in emails))
        
        # Extract phone numbers
        phone_numbers = []
        for pattern in CONTACT_PATTERNS['phone']:
            matches = re.findall(pattern, text_content)
            phone_numbers.extend(matches)
        phone_numbers = list(set(phone_numbers))
        
        return {
            'emails': emails,
            'phone_numbers': phone_numbers
        }
    
    def extract_social_handles(self) -> List[Dict[str, str]]:
        """
        Extract social media handles from HTML content.
        
        Returns:
            List of social media handle dictionaries
        """
        if not self.soup:
            return []
        
        social_handles = []
        text_content = self.soup.get_text()
        
        for platform, patterns in SOCIAL_MEDIA_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    social_handles.append({
                        'platform': platform,
                        'handle': match.strip(),
                        'url': f"https://{platform}.com/{match.strip()}"
                    })
        
        return social_handles
    
    def extract_important_links(self, base_url: str) -> List[Dict[str, str]]:
        """
        Extract important links like order tracking, contact, etc.
        
        Args:
            base_url: Base URL for resolving relative links
            
        Returns:
            List of important link dictionaries
        """
        if not self.soup:
            return []
        
        important_links = []
        links = self.extract_links(base_url)
        
        for link in links:
            text_lower = link['text'].lower()
            url_lower = link['url'].lower()
            
            for category, patterns in IMPORTANT_LINK_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, text_lower) or re.search(pattern, url_lower):
                        important_links.append({
                            'title': link['text'],
                            'url': link['url'],
                            'category': category
                        })
                        break
        
        return important_links
    
    def extract_faqs(self) -> List[Dict[str, str]]:
        """
        Extract FAQ content from HTML.
        
        Returns:
            List of FAQ dictionaries with questions and answers
        """
        if not self.soup:
            return []
        
        faqs = []
        
        # Look for common FAQ patterns
        faq_selectors = [
            '.faq-item',
            '.faq-question',
            '.faq-answer',
            '[class*="faq"]',
            '.accordion-item'
        ]
        
        for selector in faq_selectors:
            elements = self.soup.select(selector)
            for element in elements:
                question = element.find(['h3', 'h4', 'h5', 'strong'])
                answer = element.find(['p', 'div'])
                
                if question and answer:
                    faqs.append({
                        'question': question.get_text(strip=True),
                        'answer': answer.get_text(strip=True)
                    })
        
        return faqs
    
    def extract_brand_info(self) -> Dict[str, str]:
        """
        Extract brand information from HTML.
        
        Returns:
            Dictionary with brand information
        """
        if not self.soup:
            return {}
        
        brand_info = {}
        
        # Try to find brand name in title or meta tags
        title_tag = self.soup.find('title')
        if title_tag:
            brand_info['name'] = title_tag.get_text(strip=True)
        
        # Look for meta description
        meta_desc = self.soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            brand_info['description'] = meta_desc.get('content', '')
        
        # Look for about/description sections
        about_selectors = [
            '.about',
            '.about-us',
            '.brand-story',
            '.mission-statement'
        ]
        
        for selector in about_selectors:
            element = self.soup.select_one(selector)
            if element:
                brand_info['about_text'] = element.get_text(strip=True)
                break
        
        return brand_info
    
    def clean_text(self, text: str, max_length: Optional[int] = None) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text content
            max_length: Maximum length for truncated text
            
        Returns:
            Cleaned text content
        """
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        # Truncate if max_length is specified
        if max_length and len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0] + "..."
        
        return text
