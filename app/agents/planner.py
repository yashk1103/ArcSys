"""Planner agent for extracting structured requirements."""

from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.graph.state import LabState


class PlannerAgent(BaseAgent):
    """Agent responsible for extracting and structuring requirements."""

    def __init__(self):
        super().__init__("planner", temperature=0.1)

    def get_prompt_template(self) -> ChatPromptTemplate:
        """Get prompt template for requirement extraction."""
        template = """You are the Planner Agent in a technical research lab.

Your task is to analyze the user query and extract structured system requirements.

User Query:
{user_query}

Please analyze the query and extract:
1. Functional requirements (what the system should do)
2. Non-functional requirements (performance, security, scalability)
3. Technical constraints and considerations
4. Success criteria

Format your response as clear, actionable bullet points using Markdown.
Be specific and technical. Focus on measurable requirements.

Requirements:"""

        return ChatPromptTemplate.from_template(template)

    def process_response(self, response: str, state: LabState) -> Dict[str, Any]:
        """Process planner response."""
        return {
            "requirements": response.strip(),
        }

    def _get_required_fields(self) -> list[str]:
        """Required fields for planner agent."""
        return ["user_query"]