"""
API routes for the Shopify Insights application.
Defines the main endpoints for extracting store insights.
"""

from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from app.core.config import get_settings
from app.core.exceptions import ShopifyInsightsException
from app.models.request import ExtractInsightsRequest, HealthCheckRequest
from app.models.response import (
    SuccessResponse,
    ErrorResponse,
    HealthCheckResponse,
    StoreInsights
)
from app.services.shopify_extractor import ShopifyExtractor
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter()

# Get settings
settings = get_settings()


@router.post("/extract-insights", response_model=SuccessResponse)
async def extract_insights(
    request: ExtractInsightsRequest,
    background_tasks: BackgroundTasks = None
) -> SuccessResponse:
    """
    Extract comprehensive insights from a Shopify store.
    
    Args:
        request: ExtractInsightsRequest containing the website URL and options
        background_tasks: Optional background tasks for async processing
        
    Returns:
        SuccessResponse with extracted store insights
        
    Raises:
        HTTPException: If extraction fails
    """
    try:
        logger.info(f"Starting insights extraction for: {request.website_url}")
        
        # Initialize extractor
        extractor = ShopifyExtractor()
        
        # Extract insights
        store_insights = extractor.extract_insights(
            str(request.website_url),
            include_products=request.include_products,
            include_policies=request.include_policies,
            include_faqs=request.include_faqs,
            include_social=request.include_social,
            include_contact=request.include_contact,
            max_products=request.max_products
        )
        
        # Create success response
        response = SuccessResponse(
            data=store_insights,
            message="Successfully extracted insights from store"
        )
        
        logger.info(f"Successfully extracted insights for: {request.website_url}")
        return response
        
    except ShopifyInsightsException as e:
        logger.error(f"Extraction failed for {request.website_url}: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "error": e.__class__.__name__,
                "message": e.message,
                "details": e.details
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during extraction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "InternalServerError",
                "message": "An unexpected error occurred during extraction",
                "details": {"original_error": str(e)}
            }
        )


@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint to verify service status.
    
    Returns:
        HealthCheckResponse with service status information
    """
    try:
        # Basic health checks
        services_status = {
            "shopify_extractor": "healthy",
            "content_parser": "healthy",
            "url_validator": "healthy"
        }
        
        # Check if LLM is available
        if settings.openai_api_key:
            services_status["llm_processor"] = "healthy"
        else:
            services_status["llm_processor"] = "not_configured"
        
        response = HealthCheckResponse(
            status="healthy",
            version=settings.app_version,
            services=services_status
        )
        
        logger.debug("Health check completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "HealthCheckFailed",
                "message": "Health check failed",
                "details": {"error": str(e)}
            }
        )


@router.get("/", response_model=Dict[str, Any])
async def root() -> Dict[str, Any]:
    """
    Root endpoint with API information.
    
    Returns:
        Dictionary with API information
    """
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "description": "Shopify Store Insights Extractor API",
        "endpoints": {
            "extract_insights": f"{settings.api_prefix}/extract-insights",
            "health_check": f"{settings.api_prefix}/health",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "features": [
            "Product catalog extraction",
            "Policy document extraction",
            "FAQ extraction",
            "Social media handle detection",
            "Contact information extraction",
            "Brand context analysis",
            "Important link identification"
        ]
    }
