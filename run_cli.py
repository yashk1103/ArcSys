"""CLI runner for ArcSys."""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.graph.builder import get_workflow
from app.core.logging import setup_logging


async def main():
    """Run ArcSys from command line."""
    
    # Setup logging
    setup_logging()
    
    # Get user query
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter your system design query: ")
    
    if not query.strip():
        print("Error: Please provide a query")
        return
    
    try:
        print(f"Analyzing: {query}")
        print("-" * 50)
        
        # Build workflow
        workflow = get_workflow()
        
        # Initial state
        initial_state = {
            "user_query": query,
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
        
        # Execute workflow
        result = workflow.invoke(initial_state)
        
        # Display results
        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60)
        
        print(f"\nFinal Output:\n{result.get('final_markdown', 'No output generated')}")
        print(f"\nCritic Score: {result.get('critic_score', 0.0)}/10")
        print(f"Bias Score: {result.get('bias_score', 0.0)}")
        print(f"Iterations: {result.get('iteration_count', 0)}")
        
        if result.get('error_messages'):
            print(f"\nErrors: {result['error_messages']}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())