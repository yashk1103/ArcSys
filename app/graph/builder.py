"""LangGraph workflow builder with error handling."""

from typing import Any, Dict, Literal, Optional

import structlog
from langgraph.graph import StateGraph, END

from app.graph.state import LabState
from app.core.config import get_settings
from app.utils.exceptions import GraphError

logger = structlog.get_logger(__name__)


class WorkflowBuilder:
    """Build and configure the multi-agent workflow."""

    def __init__(self):
        self.settings = get_settings()
        self.graph: Optional[StateGraph] = None

    def build_graph(self) -> StateGraph:
        """Build the complete workflow graph."""
        if self.graph is not None:
            return self.graph

        try:
            # Import agents here to avoid circular imports
            from app.agents.planner import PlannerAgent
            from app.agents.researcher import ResearcherAgent
            from app.agents.architect import ArchitectAgent
            from app.agents.visualizer import VisualizerAgent
            from app.agents.critic import CriticAgent
            from app.agents.meta_critic import MetaCriticAgent

            # Create workflow
            workflow = StateGraph(LabState)

            # Initialize agents
            planner = PlannerAgent()
            researcher = ResearcherAgent()
            architect = ArchitectAgent()
            visualizer = VisualizerAgent()
            critic = CriticAgent()
            meta_critic = MetaCriticAgent()

            # Add nodes
            workflow.add_node("planner", planner.execute)
            workflow.add_node("researcher", researcher.execute)
            workflow.add_node("architect", architect.execute)
            workflow.add_node("visualizer", visualizer.execute)
            workflow.add_node("critic", critic.execute)
            workflow.add_node("meta_critic", meta_critic.execute)
            workflow.add_node("finalize", self._finalize_output)

            # Set entry point
            workflow.set_entry_point("planner")

            # Define workflow edges
            workflow.add_edge("planner", "researcher")
            workflow.add_edge("researcher", "architect")
            workflow.add_edge("architect", "visualizer")
            workflow.add_edge("visualizer", "critic")

            # Conditional edge for retry logic
            workflow.add_conditional_edges(
                "critic",
                self._should_retry,
                {
                    "retry": "researcher",
                    "proceed": "meta_critic"
                }
            )

            workflow.add_edge("meta_critic", "finalize")
            workflow.add_edge("finalize", END)

            # Compile without checkpointer for simpler usage
            self.graph = workflow.compile()
            
            logger.info("workflow_graph_built")
            return self.graph

        except Exception as e:
            logger.error("workflow_build_failed", error=str(e))
            raise GraphError(f"Failed to build workflow graph: {str(e)}") from e

    def _should_retry(self, state: LabState) -> Literal["retry", "proceed"]:
        """Determine if workflow should retry based on critic score."""
        try:
            max_iterations = self.settings.max_retries
            current_iteration = state.get("iteration_count", 0)
            
            # Check iteration limit first
            if current_iteration >= max_iterations:
                logger.warning(
                    "max_iterations_reached", 
                    iteration=current_iteration,
                    max_iterations=max_iterations
                )
                return "proceed"
            
            # Check critic score
            critic_score = state.get("critic_score", 0.0)
            threshold = self.settings.critic_threshold
            
            if critic_score < threshold:
                logger.info(
                    "retry_due_to_low_score",
                    score=critic_score,
                    threshold=threshold,
                    iteration=current_iteration
                )
                return "retry"
            
            return "proceed"
            
        except Exception as e:
            logger.error("retry_decision_failed", error=str(e))
            return "proceed"  # Fail safe

    def _finalize_output(self, state: LabState) -> Dict[str, Any]:
        """Create final markdown output."""
        try:
            sections = []
            
            if state.get("requirements"):
                sections.append(f"# Requirements\n{state['requirements']}")
            
            if state.get("research"):
                sections.append(f"# Research Notes\n{state['research']}")
            
            if state.get("architecture"):
                sections.append(f"# Architecture Design\n{state['architecture']}")
            
            if state.get("visualization"):
                sections.append(f"# Visualization\n{state['visualization']}")
            
            # Add evaluation section
            eval_section = []
            if state.get("critic_score"):
                eval_section.append(f"**Score:** {state['critic_score']}/10")
            
            if state.get("critic_feedback"):
                eval_section.append(f"**Feedback:** {state['critic_feedback']}")
            
            if state.get("bias_score"):
                eval_section.append(f"**Bias Risk:** {state['bias_score']}")
            
            if eval_section:
                sections.append(f"# Evaluation\n" + "\n".join(eval_section))
            
            final_markdown = "\n\n---\n\n".join(sections)
            
            logger.info("output_finalized", length=len(final_markdown))
            
            return {"final_markdown": final_markdown}
            
        except Exception as e:
            logger.error("finalization_failed", error=str(e))
            return {
                "final_markdown": "Error generating final output",
                "error_messages": state.get("error_messages", []) + [str(e)]
            }


def get_workflow() -> StateGraph:
    """Get the compiled workflow graph."""
    builder = WorkflowBuilder()
    return builder.build_graph()