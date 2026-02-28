"""LangGraph state schema with type safety."""

from typing import Optional
from typing_extensions import TypedDict


class LabState(TypedDict):
    """State schema for the multi-agent lab workflow."""
    
    # Core workflow data
    user_query: str
    requirements: str
    research: str  
    architecture: str
    visualization: str
    
    # Evaluation metrics
    critic_score: float
    critic_feedback: str
    bias_score: float
    
    # Output
    final_markdown: str
    
    # Metadata
    iteration_count: int
    error_messages: list[str]


class AgentResponse(TypedDict):
    """Standard response format for agents."""
    
    content: str
    confidence: float
    metadata: dict[str, str]