"""
LLM processor service for structuring and enhancing extracted data.
Uses OpenAI to improve data quality and structure.
"""

import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
from app.core.exceptions import LLMProcessingError
from app.core.config import get_settings
from app.core.logging import get_logger
from app.utils.helpers import sanitize_json

logger = get_logger(__name__)


class LLMProcessor:
    """Service for processing data using OpenAI LLM."""
    
    def __init__(self):
        self.settings = get_settings()
        if not self.settings.openai_api_key:
            raise LLMProcessingError("OpenAI API key not configured")
        
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.model = self.settings.openai_model
    
    def structure_faqs(self, raw_faqs: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Use LLM to structure and improve FAQ data.
        
        Args:
            raw_faqs: Raw FAQ data
            
        Returns:
            Structured FAQ data
        """
        if not raw_faqs:
            return []
        
        try:
            prompt = self._create_faq_prompt(raw_faqs)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that structures FAQ data."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.settings.openai_max_tokens,
                temperature=self.settings.openai_temperature
            )
            
            structured_data = json.loads(response.choices[0].message.content)
            return structured_data.get('faqs', raw_faqs)
            
        except Exception as e:
            logger.warning(f"LLM FAQ processing failed: {e}")
            return raw_faqs
    
    def enhance_brand_description(self, raw_description: str) -> str:
        """
        Use LLM to enhance brand description.
        
        Args:
            raw_description: Raw brand description
            
        Returns:
            Enhanced brand description
        """
        if not raw_description:
            return ""
        
        try:
            prompt = f"""
            Please enhance and structure the following brand description. 
            Make it more professional and engaging while maintaining accuracy:
            
            {raw_description}
            
            Return only the enhanced description, no additional text.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a brand copywriter that enhances brand descriptions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.settings.openai_max_tokens,
                temperature=self.settings.openai_temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.warning(f"LLM brand description enhancement failed: {e}")
            return raw_description
    
    def categorize_products(self, products: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Use LLM to categorize products.
        
        Args:
            products: List of product data
            
        Returns:
            Dictionary mapping categories to product IDs
        """
        if not products:
            return {}
        
        try:
            product_summaries = []
            for product in products[:20]:  # Limit to first 20 products
                summary = f"ID: {product.get('id', '')}, Title: {product.get('title', '')}, Type: {product.get('product_type', '')}"
                product_summaries.append(summary)
            
            prompt = f"""
            Please categorize the following products into logical categories. 
            Return a JSON object with categories as keys and lists of product IDs as values.
            
            Products:
            {chr(10).join(product_summaries)}
            
            Return only valid JSON.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a product categorization expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.settings.openai_max_tokens,
                temperature=self.settings.openai_temperature
            )
            
            categories = json.loads(response.choices[0].message.content)
            return categories
            
        except Exception as e:
            logger.warning(f"LLM product categorization failed: {e}")
            return {}
    
    def extract_key_insights(self, store_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to extract key insights from store data.
        
        Args:
            store_data: Complete store data
            
        Returns:
            Dictionary of key insights
        """
        try:
            # Create a summary of the store data
            summary = self._create_store_summary(store_data)
            
            prompt = f"""
            Based on the following Shopify store data, please extract key business insights:
            
            {summary}
            
            Please provide insights in the following areas:
            1. Brand positioning and market niche
            2. Product strategy and assortment
            3. Customer engagement opportunities
            4. Business model indicators
            5. Competitive advantages
            
            Return a JSON object with these insights.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a business analyst specializing in e-commerce insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.settings.openai_max_tokens,
                temperature=self.settings.openai_temperature
            )
            
            insights = json.loads(response.choices[0].message.content)
            return insights
            
        except Exception as e:
            logger.warning(f"LLM insight extraction failed: {e}")
            return {}
    
    def _create_faq_prompt(self, raw_faqs: List[Dict[str, str]]) -> str:
        """Create prompt for FAQ structuring."""
        faq_text = ""
        for i, faq in enumerate(raw_faqs):
            faq_text += f"{i+1}. Q: {faq.get('question', '')}\n   A: {faq.get('answer', '')}\n\n"
        
        return f"""
        Please structure the following FAQ data into a clean format. 
        For each FAQ, ensure the question and answer are clear and properly formatted.
        
        {faq_text}
        
        Return a JSON object with the following structure:
        {{
            "faqs": [
                {{
                    "question": "structured question",
                    "answer": "structured answer"
                }}
            ]
        }}
        
        Return only valid JSON.
        """
    
    def _create_store_summary(self, store_data: Dict[str, Any]) -> str:
        """Create a summary of store data for LLM processing."""
        summary_parts = []
        
        # Brand info
        if 'brand_info' in store_data:
            brand = store_data['brand_info']
            summary_parts.append(f"Brand: {brand.get('name', 'Unknown')}")
            summary_parts.append(f"Description: {brand.get('description', 'N/A')}")
        
        # Products
        if 'products' in store_data:
            products = store_data['products']
            summary_parts.append(f"Total Products: {products.get('total_count', 0)}")
            if 'categories' in products:
                summary_parts.append(f"Categories: {', '.join(products['categories'])}")
        
        # Policies
        if 'policies' in store_data:
            policies = store_data['policies']
            available_policies = [k for k, v in policies.items() if v is not None]
            summary_parts.append(f"Available Policies: {', '.join(available_policies)}")
        
        # Social media
        if 'social_handles' in store_data:
            social = store_data['social_handles']
            platforms = [s.get('platform', '') for s in social]
            summary_parts.append(f"Social Platforms: {', '.join(platforms)}")
        
        return "\n".join(summary_parts)
    
    def __del__(self):
        """Cleanup OpenAI client."""
        if hasattr(self, 'client'):
            try:
                self.client.close()
            except:
                pass
    
    def analyze_competitors(self, brand_name: str, brand_website: str, brand_products: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Get competitor brands for the given website and analyze their stores.
        """
        system_prompt = (
            "You are a market research assistant. Given a brand and its website, "
            "list 3-5 direct competitors (similar market and audience). "
            "Return JSON with an array of competitors, each having {name, website}."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Brand: {brand_name}\nWebsite: {brand_website}"}
        ]
        competitors_raw = self._call_llm(messages, response_format="json")
        competitors = sanitize_json(competitors_raw, fallback={"competitors": []}).get("competitors", [])

        results = {"brand": brand_name, "competitors": []}

        for comp in competitors:
            cname = comp.get("name")
            csite = comp.get("website", "")

            comp_result = {
                "name": cname,
                "website": csite,
                "categorization": self.categorize_products(brand_products),
                "enhanced_description": self.enhance_brand_description(f"{cname} store"),
                "faq": self.structure_faq([
                    "What products do you offer?",
                    "What is your return policy?",
                    "Do you provide international shipping?"
                ])
            }
            results["competitors"].append(comp_result)

        return results
