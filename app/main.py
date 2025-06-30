from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from .routes import router


app = FastAPI(title="Project Management System", version="1.0.0")

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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include the router
app.include_router(router)

