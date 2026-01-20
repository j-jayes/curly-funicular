"""Income data endpoints."""

from fastapi import APIRouter, Query
from typing import List, Optional
from api.models.schemas import IncomeData, Occupation, Region, StatsResponse
from api.utils.database import get_data_access

router = APIRouter()


@router.get("/income", response_model=List[IncomeData])
async def get_income_data(
    occupation: Optional[str] = Query(None, description="Filter by occupation code (e.g., 2512)"),
    region: Optional[str] = Query(None, description="Filter by region name (e.g., Stockholm)"),
    gender: Optional[str] = Query(None, description="Filter by gender (men/women)"),
    year: Optional[int] = Query(None, description="Filter by year (2023, 2024)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results")
):
    """Get income data with optional filters.
    
    This endpoint returns income statistics by occupation and geography.
    Data sourced from Statistics Sweden (SCB).
    
    Available occupations:
    - 2511: Systems analysts and IT architects
    - 2512: Software and systems developers
    """
    data_access = get_data_access()
    records = data_access.get_income_summary(
        occupation=occupation,
        region=region,
        year=year,
    )
    
    # Apply gender filter if provided
    if gender:
        records = [r for r in records if r.get("gender", "").lower() == gender.lower()]
    
    return records[:limit]


@router.get("/occupations", response_model=List[Occupation])
async def get_occupations():
    """Get list of available occupations.
    
    Returns all occupations available in the dataset with their SSYK codes.
    """
    data_access = get_data_access()
    return data_access.get_occupations()


@router.get("/regions", response_model=List[Region])
async def get_regions():
    """Get list of available regions.
    
    Returns all Swedish regions available in the dataset.
    """
    data_access = get_data_access()
    return data_access.get_regions()


@router.get("/stats", response_model=StatsResponse)
async def get_statistics():
    """Get aggregated statistics.
    
    Returns overall statistics about the dataset.
    """
    data_access = get_data_access()
    return data_access.get_statistics()
