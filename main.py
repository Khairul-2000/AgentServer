#!/usr/bin/env python3
"""
Main entry point for deployment platforms
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the FastAPI app
from app.main import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# This is what deployment platforms will import
__all__ = ["app"]

# For direct execution (python main.py)
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=debug,  # Only reload in debug mode
        log_level="info"
    )
