"""FastAPI application factory and configuration."""

import asyncio
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.api.routes import router
from app.monitoring.metrics import RequestMetricsMiddleware, start_metrics_server
from app.schemas.api import ErrorResponse

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    
    # Startup
    setup_logging()
    logger.info("application_startup")
    
    # Start metrics server in development
    settings = get_settings()
    if settings.environment == "development":
        try:
            start_metrics_server(8001)
            logger.info("metrics_server_started", port=8001)
        except Exception as e:
            logger.warning("metrics_server_failed", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    settings = get_settings()
    
    app = FastAPI(
        title="ArcSys",
        description="Multi-agent AI research lab using LangChain, LangGraph, and FastAPI",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan
    )
    
    # Security middleware
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.environment == "development" else [],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    
    # Metrics middleware
    app.add_middleware(RequestMetricsMiddleware)
    
    # Global exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors."""
        
        logger.warning(
            "validation_error",
            path=request.url.path,
            errors=exc.errors()
        )
        
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="Validation failed",
                error_code="VALIDATION_ERROR",
                request_id=getattr(request.state, "request_id", None)
            ).model_dump(mode="json")
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions."""
        
        logger.warning(
            "http_exception",
            path=request.url.path,
            status_code=exc.status_code,
            detail=exc.detail
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.detail,
                error_code=f"HTTP_{exc.status_code}",
                request_id=getattr(request.state, "request_id", None)
            ).model_dump(mode="json")
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        
        logger.error(
            "unexpected_exception",
            path=request.url.path,
            error=str(exc),
            exc_info=True
        )
        
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal server error",
                error_code="INTERNAL_ERROR",
                request_id=getattr(request.state, "request_id", None)
            ).model_dump(mode="json")
        )
    
    # Include routers
    app.include_router(router, prefix="/api/v1")
    
    # Mount static files for chat UI
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Serve chat UI at root
    @app.get("/")
    async def chat_ui():
        """Serve the chat interface."""
        from fastapi.responses import FileResponse
        return FileResponse("static/index.html")
    
    return app


# Create application instance
app = create_app()