"""Job advertisements endpoints."""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from api.models.schemas import JobAd, JobsAggregated
from api.utils.database import get_data_access

router = APIRouter()


@router.get("/jobs", response_model=List[JobAd])
async def get_job_ads(
    occupation: Optional[str] = Query(None, description="Filter by occupation code (e.g., 2512)"),
    region: Optional[str] = Query(None, description="Filter by region name"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results")
):
    """Get job advertisements with optional filters.
    
    This endpoint returns historical job advertisements from Arbetsförmedlingen.
    Data sourced from JobTech Historical Ads API.
    
    Available occupation codes:
    - 2511: Systems analysts and IT architects
    - 2512: Software and systems developers
    """
    data_access = get_data_access()
    records = data_access.get_job_ads(
        occupation=occupation,
        region=region,
        limit=limit,
    )
    
    return records


@router.get("/jobs/aggregated", response_model=List[JobsAggregated])
async def get_jobs_aggregated(
    occupation: Optional[str] = Query(None, description="Filter by occupation code"),
    region: Optional[str] = Query(None, description="Filter by region name"),
):
    """Get aggregated job statistics by region and occupation.
    
    Returns counts of job ads and total vacancies grouped by region and occupation.
    Useful for map visualizations and regional comparisons.
    """
    data_access = get_data_access()
    records = data_access.get_jobs_aggregated(
        occupation=occupation,
        region=region,
    )
    
    return records


@router.get("/jobs/{job_id}", response_model=JobAd)
async def get_job_ad(job_id: str):
    """Get a specific job advertisement by ID.
    
    Returns detailed information about a specific job advertisement.
    """
    data_access = get_data_access()
    records = data_access.get_job_ads()
    
    # Find the job with matching ID
    for record in records:
        if record.get("id") == job_id:
            return record
    
    raise HTTPException(status_code=404, detail=f"Job ad with ID {job_id} not found")
