"""Architect agent for system design."""

from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.graph.state import LabState


class ArchitectAgent(BaseAgent):
    """Agent responsible for system architecture design."""

    def __init__(self):
        super().__init__("architect", temperature=0.2)

    def get_prompt_template(self) -> ChatPromptTemplate:
        """Get prompt template for architecture design."""
        template = """You are the Architect Agent in a technical research lab.

Your task is to design a comprehensive system architecture based on the research.

Research Notes:
{research}

Requirements Context:
{requirements}

Please design a detailed system architecture that includes:

1. **System Overview**
   - High-level architecture description
   - Key architectural decisions and rationale
   - System boundaries and interfaces

2. **Component Design**
   - Core components and their responsibilities
   - Component interactions and dependencies
   - Data flow between components

3. **Data Architecture**
   - Data models and schemas
   - Data storage strategy
   - Data processing pipelines

4. **Infrastructure & Deployment**
   - Deployment architecture
   - Infrastructure requirements
   - Scalability strategy

5. **Security Architecture**
   - Security controls and measures
   - Authentication and authorization
   - Data protection strategies

6. **Monitoring & Observability**
   - Logging strategy
   - Metrics and monitoring
   - Error handling and recovery

Provide specific, implementable architectural decisions.
Include technology choices with justification.
Consider both functional and non-functional requirements.

Architecture Design:"""

        return ChatPromptTemplate.from_template(template)

    def process_response(self, response: str, state: LabState) -> Dict[str, Any]:
        """Process architect response."""
        return {
            "architecture": response.strip(),
        }

    def _get_required_fields(self) -> list[str]:
        """Required fields for architect agent."""
        return ["research", "requirements"]