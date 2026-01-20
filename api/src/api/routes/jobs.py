"""Job advertisements endpoints."""

from fastapi import APIRouter, Query
from typing import List, Optional
from api.models.schemas import JobAd

router = APIRouter()


@router.get("/jobs", response_model=List[JobAd])
async def get_job_ads(
    occupation: Optional[str] = Query(None, description="Filter by occupation code"),
    region: Optional[str] = Query(None, description="Filter by region code"),
    employment_type: Optional[str] = Query(None, description="Filter by employment type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results")
):
    """Get job advertisements with optional filters.
    
    This endpoint returns current job advertisements from Arbetsförmedlingen.
    Data can be filtered by occupation, region, and employment type.
    """
    # TODO: Implement actual data retrieval from GCS/BigQuery
    # For now, return sample data
    sample_data = [
        {
            "id": "job123",
            "headline": "Software Developer wanted",
            "employer": "Tech Company AB",
            "occupation": "Software Developer",
            "occupation_code": "2512",
            "region": "Stockholm",
            "region_code": "01",
            "published_date": "2024-01-15T10:00:00",
            "application_deadline": "2024-02-15T23:59:59",
            "number_of_vacancies": 2,
            "employment_type": "Full-time",
            "working_hours_type": "Full-time"
        }
    ]
    
    return sample_data


@router.get("/jobs/{job_id}", response_model=JobAd)
async def get_job_ad(job_id: str):
    """Get a specific job advertisement by ID.
    
    Returns detailed information about a specific job advertisement.
    """
    # TODO: Implement actual data retrieval
    return {
        "id": job_id,
        "headline": "Software Developer wanted",
        "employer": "Tech Company AB",
        "occupation": "Software Developer",
        "occupation_code": "2512",
        "region": "Stockholm",
        "region_code": "01",
        "published_date": "2024-01-15T10:00:00",
        "application_deadline": "2024-02-15T23:59:59",
        "number_of_vacancies": 2,
        "employment_type": "Full-time",
        "working_hours_type": "Full-time"
    }
