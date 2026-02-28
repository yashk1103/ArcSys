"""Meta-critic agent for detecting hallucinations and bias."""

import re
from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.graph.state import LabState


class MetaCriticAgent(BaseAgent):
    """Agent responsible for detecting hallucinations and bias in architecture."""

    def __init__(self):
        super().__init__("meta_critic", temperature=0.1)

    def get_prompt_template(self) -> ChatPromptTemplate:
        """Get prompt template for meta-evaluation."""
        template = """You are the Meta-Critic Agent in a technical research lab.

Your task is to detect potential hallucinations, overconfidence, or bias in the architecture analysis.

Architecture Design:
{architecture}

Requirements Context:
{requirements}

Analyze the architecture for these potential issues:

1. **Hallucination Detection**
   - Are there claims about specific technologies without proper justification?
   - Are there unrealistic performance claims?
   - Are there references to non-existent features or capabilities?

2. **Overconfidence Analysis**  
   - Are the claims too absolute without acknowledging limitations?
   - Is there insufficient discussion of trade-offs?
   - Are alternative approaches dismissed too quickly?

3. **Bias Detection**
   - Is there bias toward specific technologies or vendors?
   - Are there unsupported assumptions about user behavior?
   - Is there insufficient consideration of diverse use cases?

4. **Completeness Check**
   - Are there significant gaps in the analysis?
   - Are edge cases adequately addressed?
   - Is error handling properly considered?

Provide a risk score between 0.0 and 1.0 where:
- 0.0 = No concerning issues detected
- 0.3 = Minor issues that should be noted
- 0.5 = Moderate concerns requiring attention
- 0.7 = Significant issues affecting credibility
- 1.0 = Major hallucinations or bias detected

Return only the numerical risk score (e.g., 0.2) followed by a brief explanation.

Risk Assessment:"""

        return ChatPromptTemplate.from_template(template)

    def process_response(self, response: str, state: LabState) -> Dict[str, Any]:
        """Process meta-critic response and extract bias score."""
        try:
            # Extract numerical score from response
            score_match = re.search(r'(\d+(?:\.\d+)?)', response.strip())
            
            if score_match:
                score = float(score_match.group(1))
                # Ensure score is in valid range
                score = min(max(score, 0.0), 1.0)
            else:
                # Fallback analysis based on keywords
                score = self._analyze_text_for_risk(response)
            
            return {
                "bias_score": score,
            }
            
        except (ValueError, AttributeError) as e:
            self.logger.warning("failed_to_parse_bias_score", error=str(e))
            return {
                "bias_score": 0.5,  # Middle score as fallback
            }

    def _analyze_text_for_risk(self, text: str) -> float:
        """Analyze text for risk indicators as fallback."""
        risk_indicators = {
            # High risk indicators
            "major": ["hallucination", "false", "incorrect", "misleading", "bias"],
            # Medium risk indicators  
            "moderate": ["concern", "issue", "problem", "questionable", "unclear"],
            # Low risk indicators
            "minor": ["minor", "small", "trivial", "acceptable"]
        }
        
        text_lower = text.lower()
        
        major_count = sum(1 for word in risk_indicators["major"] if word in text_lower)
        moderate_count = sum(1 for word in risk_indicators["moderate"] if word in text_lower)
        minor_count = sum(1 for word in risk_indicators["minor"] if word in text_lower)
        
        if major_count > 0:
            return min(0.7 + (major_count * 0.1), 1.0)
        elif moderate_count > 0:
            return min(0.3 + (moderate_count * 0.1), 0.6)
        elif minor_count > 0:
            return min(0.1 + (minor_count * 0.05), 0.3)
        else:
            return 0.2  # Default low risk

    def _get_required_fields(self) -> list[str]:
        """Required fields for meta-critic agent."""
        return ["architecture", "requirements"]