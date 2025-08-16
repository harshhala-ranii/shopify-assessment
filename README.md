# Shopify Store Insights Extractor

A Python application that extracts comprehensive insights from Shopify stores without using the official Shopify API. Built with FastAPI, following SOLID principles and best practices.

## Features

- **Product Catalog Extraction**: Fetches complete product listings from `/products.json`
- **Hero Products**: Identifies products featured on the homepage
- **Policy Documents**: Extracts Privacy Policy, Return/Refund policies
- **FAQ Extraction**: Intelligent FAQ detection and structuring
- **Social Media Handles**: Discovers brand social media presence
- **Contact Information**: Extracts emails, phone numbers, and contact details
- **Brand Context**: Captures brand description and about information
- **Important Links**: Identifies order tracking, contact, blog, and other key pages

## Architecture

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation and settings management
- **BeautifulSoup4**: HTML parsing and content extraction
- **LLM Integration**: OpenAI integration for data structuring
- **MySQL**: Database persistence (optional)
- **SOLID Principles**: Clean, maintainable code architecture

## Project Structure

```
shopify/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration management
│   │   ├── exceptions.py       # Custom exception classes
│   │   └── logging.py          # Logging configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py          # Request models
│   │   ├── response.py         # Response models
│   │   └── database.py         # Database models (optional)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── shopify_extractor.py # Main extraction logic
│   │   ├── content_parser.py   # HTML content parsing
│   │   ├── llm_processor.py    # LLM data structuring
│   │   └── url_validator.py    # URL validation utilities
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # API endpoint definitions
│   │   └── middleware.py       # Custom middleware
│   └── utils/
│       ├── __init__.py
│       ├── constants.py        # Application constants
│       └── helpers.py          # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_extractor.py
│   ├── test_parser.py
│   └── test_api.py
├── requirements.txt
├── .env.example
├── docker-compose.yml
└── README.md
```

## Setup

1. **Clone and Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and other configurations
   ```

3. **Run the Application**:
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

## Usage

### Extract Store Insights

```bash
POST /api/v1/extract-insights
Content-Type: application/json

{
  "website_url": "https://example.myshopify.com"
}
```

### Response Format

```json
{
  "success": true,
  "data": {
    "brand_info": {
      "name": "Brand Name",
      "description": "Brand description...",
      "website_url": "https://example.myshopify.com"
    },
    "products": {
      "total_count": 150,
      "hero_products": [...],
      "catalog": [...]
    },
    "policies": {
      "privacy_policy": "...",
      "return_policy": "...",
      "refund_policy": "..."
    },
    "faqs": [...],
    "social_handles": {
      "instagram": "@brandname",
      "facebook": "brandname",
      "tiktok": "@brandname"
    },
    "contact_info": {
      "emails": ["contact@brand.com"],
      "phone_numbers": ["+1-555-0123"]
    },
    "important_links": {
      "order_tracking": "https://...",
      "contact_us": "https://...",
      "blog": "https://..."
    }
  },
  "extracted_at": "2024-01-01T12:00:00Z"
}
```

## Error Handling

- **400**: Invalid URL format
- **401**: Website not found or inaccessible
- **404**: Store not found
- **500**: Internal server error
- **422**: Validation error

## Testing

```bash
pytest tests/ -v
```

## Docker Support

```bash
docker-compose up -d
```

## Best Practices Implemented

- **SOLID Principles**: Single responsibility, open/closed, Liskov substitution, interface segregation, dependency inversion
- **Clean Code**: Meaningful names, small functions, DRY principle
- **Error Handling**: Comprehensive exception handling with proper HTTP status codes
- **Logging**: Structured logging for debugging and monitoring
- **Type Hints**: Full type annotation support
- **Documentation**: Comprehensive API documentation with OpenAPI/Swagger
- **Testing**: Unit tests with pytest
- **Configuration**: Environment-based configuration management
- **Security**: Input validation and sanitization

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation as needed
4. Ensure all tests pass before submitting

## License

MIT License
