"""Job advertisements endpoints."""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from api.models.schemas import JobAd, JobsAggregated, TopEmployer, Skill
from api.utils.database import get_data_access

router = APIRouter()


def parse_occupations(occupation: Optional[str]) -> Optional[List[str]]:
    """Parse comma-separated occupation codes into a list."""
    if not occupation:
        return None
    return [occ.strip() for occ in occupation.split(",") if occ.strip()]


@router.get("/jobs", response_model=List[JobAd])
async def get_job_ads(
    occupation: Optional[str] = Query(None, description="Filter by occupation code(s), comma-separated (e.g., 2512,2511)"),
    region: Optional[str] = Query(None, description="Filter by region name"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results")
):
    """Get job advertisements with optional filters.
    
    This endpoint returns historical job advertisements from Arbetsförmedlingen.
    Data sourced from JobTech Historical Ads API.
    
    Supports multiple occupations via comma-separated values.
    """
    data_access = get_data_access()
    occupations = parse_occupations(occupation)
    records = data_access.get_job_ads(
        occupations=occupations,
        region=region,
        limit=limit,
    )
    
    return records


@router.get("/jobs/aggregated", response_model=List[JobsAggregated])
async def get_jobs_aggregated(
    occupation: Optional[str] = Query(None, description="Filter by occupation code(s), comma-separated"),
    region: Optional[str] = Query(None, description="Filter by region name"),
):
    """Get aggregated job statistics by region and occupation.
    
    Returns counts of job ads and total vacancies grouped by region and occupation.
    Useful for map visualizations and regional comparisons.
    """
    data_access = get_data_access()
    occupations = parse_occupations(occupation)
    records = data_access.get_jobs_aggregated(
        occupations=occupations,
        region=region,
    )
    
    return records


@router.get("/jobs/top-employers", response_model=List[TopEmployer])
async def get_top_employers(
    occupation: Optional[str] = Query(None, description="Filter by occupation code(s), comma-separated"),
    region: Optional[str] = Query(None, description="Filter by region name"),
    limit: int = Query(15, ge=1, le=50, description="Maximum number of employers"),
):
    """Get top employers by job ad count.
    
    Returns the most active employers based on job advertisement count.
    Data sourced from JobTech Historical Ads API.
    """
    data_access = get_data_access()
    occupations = parse_occupations(occupation)
    records = data_access.get_top_employers(
        occupations=occupations,
        region=region,
        limit=limit,
    )
    
    return records


@router.get("/jobs/skills", response_model=List[Skill])
async def get_skills(
    occupation: Optional[str] = Query(None, description="Filter by occupation code(s), comma-separated"),
    skill_type: Optional[str] = Query(None, description="Filter by skill type: competency, trait, or occupation"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of skills"),
):
    """Get top skills extracted from job advertisements.
    
    Returns skills and competencies extracted from job ad descriptions
    using AI-based text enrichment.
    Data sourced from JobTech JobAd Enrichments API.
    """
    data_access = get_data_access()
    occupations = parse_occupations(occupation)
    records = data_access.get_top_skills(
        occupations=occupations,
        skill_type=skill_type,
        limit=limit,
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
