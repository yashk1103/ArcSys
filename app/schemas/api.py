"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    """Request schema for analysis endpoint."""
    
    query: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="The user query to analyze"
    )
    
    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate query content."""
        if not v.strip():
            raise ValueError("Query cannot be empty or only whitespace")
        
        # Basic security checks
        if any(keyword in v.lower() for keyword in ["script", "eval", "exec"]):
            raise ValueError("Query contains potentially unsafe content")
        
        return v.strip()


class AnalyzeResponse(BaseModel):
    """Response schema for analysis endpoint."""
    
    final_markdown: str = Field(..., description="The final analysis in markdown format")
    critic_score: float = Field(..., ge=0.0, le=10.0, description="Quality score from critic")
    bias_score: float = Field(..., ge=0.0, le=1.0, description="Bias/hallucination risk score")
    iteration_count: int = Field(..., ge=1, description="Number of iterations performed")
    processing_time: float = Field(..., gt=0.0, description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Response schema for health check."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = Field(None, description="Request ID for tracking")