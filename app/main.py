from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from .routes import router

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Project Management System", 
    version="1.0.0",
    description="AI-powered project planning and management system"
)

# Get allowed origins from environment
allowed_origins = [
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.0.108:3000",
    "http://localhost:3001",  # Alternative frontend port
]

# Add additional origins from environment variable
additional_origins = os.getenv("ALLOWED_ORIGINS", "")
if additional_origins:
    allowed_origins.extend(additional_origins.split(","))

# For production deployment, also allow common deployment URLs
if os.getenv("DEBUG", "True").lower() == "false":
    # Add common deployment domains
    allowed_origins.extend([
        "https://*.vercel.app",
        "https://*.netlify.app", 
        "https://*.render.com",
        "https://*.herokuapp.com"
    ])

logger.info(f"Configured CORS origins: {allowed_origins}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint for deployment platforms
@app.get("/")
async def root():
    return {
        "message": "Project Management System API", 
        "status": "healthy",
        "version": "1.0.0"
    }

# Include the main router
app.include_router(router)

logger.info("FastAPI application initialized successfully")

# Include the router
app.include_router(router)

