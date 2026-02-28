"""Development startup script."""

import os
import sys
from pathlib import Path

def main():
    """Start the development server."""
    
    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("Warning: .env file not found. Copy .env.example to .env and configure it.")
        return False
    
    # Check if virtual environment is active
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Warning: No virtual environment detected. Consider using 'python -m venv venv' and activating it.")
    
    # Start server
    print("Starting OrchestraLab AI development server...")
    print("API Docs: http://localhost:8000/docs")
    print("Metrics: http://localhost:8001")
    print("\nPress Ctrl+C to stop\n")
    
    os.system("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")


if __name__ == "__main__":
    main()