#!/usr/bin/env python3
"""
Production startup script for deployment platforms
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for production deployment"""
    
    # Get port from environment (deployment platforms set this)
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Debug mode: {os.getenv('DEBUG', 'False')}")
    
    # Import and run the app
    from app.main import app
    import uvicorn
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,  # Never use reload in production
        workers=1,     # Single worker for simplicity
        log_level="info"
    )

if __name__ == "__main__":
    main()
