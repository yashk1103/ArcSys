"""Simple test script to debug the workflow step by step."""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.logging import setup_logging
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent


def test_individual_agents():
    """Test agents individually to isolate issues."""
    
    setup_logging()
    
    # Test planner agent
    print("Testing Planner Agent...")
    planner = PlannerAgent()
    
    test_state = {
        "user_query": "Design a simple REST API for user management",
        "requirements": "",
        "research": "",
        "architecture": "",
        "visualization": "",
        "critic_score": 0.0,
        "critic_feedback": "",
        "bias_score": 0.0,
        "final_markdown": "",
        "iteration_count": 0,
        "error_messages": [],
    }
    
    try:
        result = planner.execute(test_state)
        print(f"Planner Result Keys: {list(result.keys())}")
        if "requirements" in result:
            print(f"Requirements length: {len(result['requirements'])}")
            print(f"Requirements preview: {result['requirements'][:200]}...")
        
        # Update state with planner results
        test_state.update(result)
        
        # Test researcher agent if planner succeeded
        if result.get("requirements"):
            print("\nTesting Researcher Agent...")
            researcher = ResearcherAgent()
            researcher_result = researcher.execute(test_state)
            print(f"Researcher Result Keys: {list(researcher_result.keys())}")
            if "research" in researcher_result:
                print(f"Research length: {len(researcher_result['research'])}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_individual_agents()