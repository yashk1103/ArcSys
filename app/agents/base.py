"""Base agent class with common functionality."""

from abc import ABC, abstractmethod
from typing import Any, Dict

import structlog
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage

from app.core.llm import get_llm_client
from app.graph.state import LabState, AgentResponse
from app.utils.exceptions import AgentError

logger = structlog.get_logger(__name__)


class BaseAgent(ABC):
    """Base class for all agents with common functionality."""

    def __init__(self, name: str, temperature: float = 0.3):
        self.name = name
        self.temperature = temperature
        self.llm_client = get_llm_client(temperature)
        self.logger = logger.bind(agent=name)

    @abstractmethod
    def get_prompt_template(self) -> ChatPromptTemplate:
        """Get the prompt template for this agent."""
        pass

    @abstractmethod
    def process_response(self, response: str, state: LabState) -> Dict[str, Any]:
        """Process the LLM response and return state updates."""
        pass

    def execute(self, state: LabState) -> Dict[str, Any]:
        """Execute the agent with error handling and logging."""
        try:
            self.logger.info("agent_execution_started")
            
            # Validate inputs
            self._validate_inputs(state)
            
            # Get prompt template and format
            prompt_template = self.get_prompt_template()
            prompt_vars = self._extract_prompt_variables(state)
            
            # Create message
            formatted_prompt = prompt_template.format(**prompt_vars)
            messages = [HumanMessage(content=formatted_prompt)]
            
            # Invoke LLM (sync version for LangGraph compatibility)
            response = self.llm_client.client.invoke(messages)
            response_content = response.content
            
            # Process response
            result = self.process_response(response_content, state)
            
            # Add metadata
            result.update({
                "iteration_count": state.get("iteration_count", 0) + 1,
            })
            
            self.logger.info("agent_execution_completed", response_length=len(response_content))
            return result
            
        except Exception as e:
            self.logger.error("agent_execution_failed", error=str(e))
            error_msg = f"{self.name} failed: {str(e)}"
            
            return {
                "error_messages": state.get("error_messages", []) + [error_msg],
                "iteration_count": state.get("iteration_count", 0)
            }

    def _validate_inputs(self, state: LabState) -> None:
        """Validate agent inputs."""
        required_fields = self._get_required_fields()
        
        for field in required_fields:
            value = state.get(field, "")
            if not value or (isinstance(value, str) and not value.strip()):
                raise AgentError(f"Required field '{field}' is missing or empty")
            
            if isinstance(value, str) and not self.llm_client.validate_input(value):
                raise AgentError(f"Invalid input in field '{field}'")

    @abstractmethod
    def _get_required_fields(self) -> list[str]:
        """Get list of required state fields for this agent."""
        pass

    def _extract_prompt_variables(self, state: LabState) -> Dict[str, Any]:
        """Extract variables needed for prompt from state."""
        return {key: value for key, value in state.items() if isinstance(value, str)}

    def _calculate_confidence(self, response: str) -> float:
        """Calculate confidence score for response."""
        base_confidence = 0.8
        length_factor = min(len(response) / 1000, 1.0)  # Longer responses get higher confidence
        return base_confidence + (length_factor * 0.2)