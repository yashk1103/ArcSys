"""Critic agent for evaluating architecture quality."""

import json
from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.graph.state import LabState


class CriticAgent(BaseAgent):
    """Agent responsible for evaluating and scoring architecture quality."""

    def __init__(self):
        super().__init__("critic", temperature=0.1)

    def get_prompt_template(self) -> ChatPromptTemplate:
        """Get prompt template for architecture evaluation."""
        template = """You are the Critic Agent in a technical research lab.

Your task is to evaluate the quality and completeness of the system architecture.

Original Requirements:
{requirements}

Research Analysis:
{research}

Architecture Design:
{architecture}

Evaluate the architecture against these criteria:

1. **Completeness** (0-10): Does it address all requirements?
2. **Technical Soundness** (0-10): Are the technical decisions appropriate?
3. **Scalability** (0-10): Can it handle growth and load?
4. **Security** (0-10): Are security concerns properly addressed?
5. **Maintainability** (0-10): Is the design maintainable and extensible?
6. **Performance** (0-10): Will it meet performance requirements?
7. **Feasibility** (0-10): Is the design realistic to implement?

Provide your evaluation in this exact JSON format:
{{
    "score": [average score 0-10],
    "feedback": "[Detailed feedback explaining the score, highlighting strengths and weaknesses, specific improvement suggestions]",
    "completeness": [0-10],
    "technical_soundness": [0-10],
    "scalability": [0-10],
    "security": [0-10],
    "maintainability": [0-10],
    "performance": [0-10],
    "feasibility": [0-10]
}}

Be constructive but thorough in your evaluation.
Provide specific, actionable feedback for improvements.

Evaluation:"""

        return ChatPromptTemplate.from_template(template)

    def process_response(self, response: str, state: LabState) -> Dict[str, Any]:
        """Process critic response and extract scores."""
        try:
            # Try to parse JSON response
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            
            result = json.loads(response_clean.strip())
            
            return {
                "critic_score": float(result.get("score", 5.0)),
                "critic_feedback": result.get("feedback", "No feedback provided"),
            }
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.logger.warning("failed_to_parse_critic_response", error=str(e))
            
            # Fallback: try to extract score from text
            score = self._extract_score_from_text(response)
            
            return {
                "critic_score": score,
                "critic_feedback": f"Parsing failed. Raw response: {response[:500]}",
            }

    def _extract_score_from_text(self, text: str) -> float:
        """Extract a score from text as fallback."""
        import re
        
        # Look for score patterns
        score_patterns = [
            r"score[:\s]*(\d+(?:\.\d+)?)",
            r"(\d+(?:\.\d+)?)[/\s]*10",
            r"rating[:\s]*(\d+(?:\.\d+)?)",
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    score = float(match.group(1))
                    return min(max(score, 0.0), 10.0)
                except ValueError:
                    continue
        
        # Default middle score if no pattern found
        return 5.0

    def _get_required_fields(self) -> list[str]:
        """Required fields for critic agent."""
        return ["requirements", "research", "architecture"]