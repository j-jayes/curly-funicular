"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import income, jobs
from api.utils.database import get_data_access

app = FastAPI(
    title="Swedish Labor Market API",
    description="API for Swedish labor market data including income and job statistics",
    version="0.1.0"
)

# Configure CORS - allow all for demo purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(income.router, prefix="/api/v1", tags=["income"])
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Swedish Labor Market API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/v1/occupations")
async def get_occupations():
    """Get list of available occupations."""
    data_access = get_data_access()
    return data_access.get_occupations()


@app.get("/api/v1/regions")
async def get_regions():
    """Get list of available regions."""
    data_access = get_data_access()
    return data_access.get_regions()


@app.get("/api/v1/stats")
async def get_stats():
    """Get overall statistics."""
    data_access = get_data_access()
    return data_access.get_statistics()
