"""Main API routes for OrchestraLab AI."""

import time
import uuid
from typing import Dict, Any

import structlog
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse

from app.schemas.api import (
    AnalyzeRequest, 
    AnalyzeResponse, 
    HealthResponse,
    ErrorResponse
)
from app.graph.builder import get_workflow
from app.core.config import get_settings
from app.utils.exceptions import OrchestraLabError, ValidationError, RateLimitError
from app.monitoring.metrics import MetricsCollector

logger = structlog.get_logger(__name__)
router = APIRouter()


# Dependency to get workflow
async def get_workflow_dependency():
    """Dependency to provide workflow graph."""
    try:
        return get_workflow()
    except Exception as e:
        logger.error("workflow_initialization_failed", error=str(e))
        raise HTTPException(
            status_code=500, 
            detail="Workflow initialization failed"
        )


# Dependency for request validation and rate limiting
async def validate_request(request: Request) -> str:
    """Validate request and return request ID."""
    request_id = str(uuid.uuid4())
    
    # Add request ID to context
    request.state.request_id = request_id
    
    # Basic rate limiting check (implementation depends on your needs)
    # This is a simple example - in production, use Redis or similar
    
    logger.info("request_received", request_id=request_id)
    return request_id


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_system(
    request: AnalyzeRequest,
    workflow=Depends(get_workflow_dependency),
    request_id: str = Depends(validate_request)
) -> AnalyzeResponse:
    """Analyze a system design query using multi-agent workflow."""
    
    start_time = time.time()
    
    try:
        logger.info(
            "analysis_started",
            request_id=request_id,
            query_length=len(request.query)
        )
        
        # Initialize state
        initial_state = {
            "user_query": request.query,
            "requirements": "",
            "research": "",
            "architecture": "",
            "visualization": "",
            "critic_score": 0.0,
            "critic_feedback": "",
            "bias_score": 0.0,
            "final_markdown": "",
            "iteration_count": 0,
            "error_messages": [],
        }
        
        # Execute workflow
        result = workflow.invoke(initial_state)
        
        processing_time = time.time() - start_time
        
        logger.info(
            "analysis_completed",
            request_id=request_id,
            processing_time=processing_time,
            critic_score=result.get("critic_score", 0.0),
            iterations=result.get("iteration_count", 0)
        )
        
        # Record metrics
        MetricsCollector.record_request_duration(processing_time)
        MetricsCollector.record_request_success()
        
        return AnalyzeResponse(
            final_markdown=result.get("final_markdown", "No output generated"),
            critic_score=result.get("critic_score", 0.0),
            bias_score=result.get("bias_score", 0.0),
            iteration_count=result.get("iteration_count", 0),
            processing_time=processing_time
        )
        
    except ValidationError as e:
        logger.warning("validation_error", request_id=request_id, error=str(e))
        MetricsCollector.record_request_error("validation")
        raise HTTPException(status_code=400, detail=str(e))
        
    except RateLimitError as e:
        logger.warning("rate_limit_error", request_id=request_id, error=str(e))
        MetricsCollector.record_request_error("rate_limit")
        raise HTTPException(status_code=429, detail=str(e))
        
    except OrchestraLabError as e:
        logger.error("orchestralab_error", request_id=request_id, error=str(e))
        MetricsCollector.record_request_error("internal")
        raise HTTPException(status_code=500, detail=str(e))
        
    except Exception as e:
        logger.error("unexpected_error", request_id=request_id, error=str(e))
        MetricsCollector.record_request_error("unexpected")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred during analysis"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )


@router.get("/metrics")
async def get_metrics():
    """Get application metrics (Prometheus format)."""
    
    settings = get_settings()
    
    # In development, allow metrics access
    if settings.environment != "production":
        from prometheus_client import generate_latest
        return JSONResponse(
            content=generate_latest().decode("utf-8"),
            media_type="text/plain"
        )
    else:
        raise HTTPException(
            status_code=404,
            detail="Metrics endpoint not available in production"
        )