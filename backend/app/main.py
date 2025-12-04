"""
PhishShield AI - Main Application Entry Point

This module initializes the FastAPI application and configures:
- CORS middleware for cross-origin requests
- API routing for all endpoints
- Health check endpoints

The application serves as the backend API for the PhishShield phishing
detection system, providing real-time URL analysis using machine learning.

Author: PhishShield Team
Version: 1.0.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Import endpoint routers directly
from app.api.v1.endpoints import score, feedback, stats

# Initialize FastAPI application with metadata
app = FastAPI(
    title=settings.PROJECT_NAME,  # "PhishShield AI"
    openapi_url=f"{settings.API_V1_STR}/openapi.json"  # OpenAPI schema location
)

# ============================================================================
# CORS Configuration
# ============================================================================
# CORS (Cross-Origin Resource Sharing) allows the frontend dashboard and
# browser extension to communicate with this backend API from different origins.
# In production, these should be restricted to specific domains.

# List of allowed origins (frontend URLs that can access this API)
origins = [
    "http://localhost:3000",  # Next.js dashboard (default port)
    "http://localhost:3001",  # Alternative dashboard port
    "http://localhost:3002",  # Alternative dashboard port
    "http://localhost:8000",  # Backend itself (for testing)
    "*",                      # Allow all origins (required for browser extension)
]

# Add CORS middleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # Allowed origins list
    allow_credentials=True,             # Allow cookies and authentication
    allow_methods=["*"],                # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],                # Allow all headers
)

# ============================================================================
# API Router Registration
# ============================================================================
# Register all API endpoints under the /api/v1 prefix
app.include_router(score.router, prefix=settings.API_V1_STR, tags=["score"])
app.include_router(feedback.router, prefix=f"{settings.API_V1_STR}/feedback", tags=["feedback"])
app.include_router(stats.router, prefix=settings.API_V1_STR, tags=["stats"])

# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "PhishShield AI Backend is running"}
