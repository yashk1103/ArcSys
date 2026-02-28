"""Custom exception classes."""


class OrchestraLabError(Exception):
    """Base exception for OrchestraLab AI."""
    pass


class LLMError(OrchestraLabError):
    """Error during LLM operations."""
    pass


class RateLimitError(OrchestraLabError):
    """Rate limit exceeded."""
    pass


class ValidationError(OrchestraLabError):
    """Input validation error."""
    pass


class AgentError(OrchestraLabError):
    """Error in agent execution."""
    pass


class GraphError(OrchestraLabError):
    """Error in graph execution."""
    pass