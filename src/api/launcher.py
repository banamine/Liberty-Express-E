"""
FastAPI Server Launcher for ScheduleFlow

Starts the FastAPI server on port 5001 (separate from frontend on 5000).
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.server import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Start FastAPI server"""
    import uvicorn
    
    logger.info("Starting ScheduleFlow FastAPI Server...")
    logger.info("API documentation available at: http://localhost:3000/docs")
    
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=3000,
        log_level="info",
        reload=False
    )


if __name__ == "__main__":
    main()
