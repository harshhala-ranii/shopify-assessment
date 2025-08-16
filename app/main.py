"""
Main FastAPI application for the Shopify Insights API.
Configures the application, middleware, and routes.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

from app.core.config import get_settings
from app.core.exceptions import ShopifyInsightsException
from app.api.routes import router
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Shopify Insights API...")
    logger.info(f"App Name: {settings.app_name}")
    logger.info(f"Version: {settings.app_version}")
    logger.info(f"Debug Mode: {settings.debug}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Shopify Insights API...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="A comprehensive API for extracting insights from Shopify stores without using the official Shopify API",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure based on your deployment
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
    
    return response


# Include API routes
app.include_router(router, prefix=settings.api_prefix)


@app.exception_handler(ShopifyInsightsException)
async def shopify_insights_exception_handler(request: Request, exc: ShopifyInsightsException):
    """Global exception handler for ShopifyInsightsException."""
    logger.error(f"ShopifyInsightsException: {exc.message}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.__class__.__name__,
            "message": exc.message,
            "status_code": exc.status_code,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "status_code": 500,
            "details": {"error": str(exc)}
        }
    )


@app.get("/")
async def root():
    """Root endpoint with API information."""
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


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
