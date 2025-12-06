"""
FastAPI Application Main

Entry point for the ETF Analysis REST API.
Provides portfolio analysis capabilities via HTTP endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from api.routers import (
    simulation_router,
    optimization_router,
    portfolio_router,
    instruments_router,
    rebalancing_router,
    tasks_router,
)
from api.auth import router as auth_router
from api.exceptions import exception_handlers


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Create FastAPI application
app = FastAPI(
    title="ETF Analysis API",
    description="REST API for portfolio analysis, optimization, and risk metrics with JWT authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",  # NextJS dev server (backup port)
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8501",  # Streamlit app
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(auth_router, prefix="/api")
app.include_router(simulation_router, prefix="/api")
app.include_router(optimization_router, prefix="/api")
app.include_router(portfolio_router, prefix="/api")
app.include_router(instruments_router, prefix="/api")
app.include_router(rebalancing_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")


@app.middleware("http")
async def log_requests(request, call_next):
    """Log all HTTP requests with duration."""
    start_time = datetime.now()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = (datetime.now() - start_time).total_seconds()
    
    # Log request details
    logger.info(
        f"{request.method} {request.url.path} "
        f"- Status: {response.status_code} "
        f"- Duration: {duration:.3f}s"
    )
    
    return response


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": "ETF Analysis API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/auth",
            "simulation": "/api/simulation",
            "optimization": "/api/optimization",
            "portfolio": "/api/portfolio",
            "instruments": "/api/instruments",
            "rebalancing": "/api/rebalancing",
            "tasks": "/api/tasks"
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# Register exception handlers
for exception_type, handler in exception_handlers.items():
    app.add_exception_handler(exception_type, handler)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
