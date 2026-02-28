"""Researcher agent for deep technical analysis."""

from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.graph.state import LabState


class ResearcherAgent(BaseAgent):
    """Agent responsible for deep technical research and analysis."""

    def __init__(self):
        super().__init__("researcher", temperature=0.4)

    def get_prompt_template(self) -> ChatPromptTemplate:
        """Get prompt template for technical research."""
        template = """You are the Researcher Agent in a technical research lab.

Your task is to provide deep technical analysis and research based on the requirements.

Requirements:
{requirements}

Please provide comprehensive research covering:

1. **Technology Stack Analysis**
   - Relevant technologies, frameworks, and tools
   - Trade-offs between different approaches
   - Industry best practices

2. **Technical Challenges**
   - Known challenges and common pitfalls
   - Performance considerations
   - Security considerations

3. **Implementation Patterns**
   - Proven design patterns
   - Architecture patterns
   - Data flow patterns

4. **Scalability & Performance**
   - Bottlenecks and optimization strategies
   - Monitoring and observability needs
   - Resource requirements

Provide detailed, technical explanations with specific examples.
Focus on actionable insights that will guide the architecture design.

Research Analysis:"""

        return ChatPromptTemplate.from_template(template)

    def process_response(self, response: str, state: LabState) -> Dict[str, Any]:
        """Process researcher response."""
        return {
            "research": response.strip(),
        }

    def _get_required_fields(self) -> list[str]:
        """Required fields for researcher agent."""
        return ["requirements"]