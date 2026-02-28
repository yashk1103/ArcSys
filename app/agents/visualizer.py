"""Visualizer agent for creating diagrams and visual representations."""

from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.graph.state import LabState


class VisualizerAgent(BaseAgent):
    """Agent responsible for creating visual representations and diagrams."""

    def __init__(self):
        super().__init__("visualizer", temperature=0.1)

    def get_prompt_template(self) -> ChatPromptTemplate:
        """Get prompt template for visualization."""
        template = """You are the Visualizer Agent in a technical research lab.

Your task is to create clear visual representations of the system architecture.

Architecture Design:
{architecture}

Create comprehensive visual documentation including:

1. **System Architecture Diagram**
   ```mermaid
   graph TD
   [Create a clear system architecture diagram showing components and their relationships]
   ```

2. **Data Flow Diagram**
   ```mermaid
   flowchart LR
   [Show how data flows through the system]
   ```

3. **Deployment Diagram** (if applicable)
   ```mermaid
   graph TB
   [Show deployment architecture and infrastructure]
   ```

4. **Sequence Diagram** (for key interactions)
   ```mermaid
   sequenceDiagram
   [Show important interaction sequences]
   ```

Guidelines:
- Use proper Mermaid syntax
- Keep diagrams clear and readable
- Include all major components
- Show relationships and data flow
- Use consistent naming
- Add brief explanations for each diagram

Focus on creating diagrams that effectively communicate the architecture.

Visual Documentation:"""

        return ChatPromptTemplate.from_template(template)

    def process_response(self, response: str, state: LabState) -> Dict[str, Any]:
        """Process visualizer response."""
        return {
            "visualization": response.strip(),
        }

    def _get_required_fields(self) -> list[str]:
        """Required fields for visualizer agent."""
        return ["architecture"]