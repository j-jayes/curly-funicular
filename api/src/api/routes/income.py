"""Income data endpoints."""

from fastapi import APIRouter, Query
from typing import List, Optional
from api.models.schemas import IncomeData, IncomeDispersion, Occupation, Region, StatsResponse
from api.utils.database import get_data_access

router = APIRouter()


def parse_occupations(occupation: Optional[str]) -> Optional[List[str]]:
    """Parse comma-separated occupation codes into a list."""
    if not occupation:
        return None
    return [occ.strip() for occ in occupation.split(",") if occ.strip()]


@router.get("/income", response_model=List[IncomeData])
async def get_income_data(
    occupation: Optional[str] = Query(None, description="Filter by occupation code(s), comma-separated (e.g., 2512,2511)"),
    region: Optional[str] = Query(None, description="Filter by region name (e.g., Stockholm)"),
    gender: Optional[str] = Query(None, description="Filter by gender (men/women)"),
    year: Optional[int] = Query(None, description="Filter by year (2023, 2024)"),
    limit: int = Query(2000, ge=1, le=5000, description="Maximum number of results")
):
    """Get income data with optional filters.
    
    This endpoint returns income statistics by occupation and geography.
    Data sourced from Statistics Sweden (SCB).
    
    Supports multiple occupations via comma-separated values.
    """
    data_access = get_data_access()
    occupations = parse_occupations(occupation)
    records = data_access.get_income_summary(
        occupations=occupations,
        region=region,
        year=year,
    )
    
    # Apply gender filter if provided
    if gender:
        records = [r for r in records if r.get("gender", "").lower() == gender.lower()]
    
    return records[:limit]


@router.get("/income/dispersion", response_model=List[IncomeDispersion])
async def get_income_dispersion(
    occupation: Optional[str] = Query(None, description="Filter by occupation name(s), comma-separated"),
    year: Optional[int] = Query(None, description="Filter by year (2023, 2024)"),
    gender: Optional[str] = Query(None, description="Filter by gender (men/women)"),
):
    """Get salary distribution data with percentiles for box plots.
    
    Returns P10, P25, Median, P75, P90 percentiles for each occupation/gender.
    Data sourced from Statistics Sweden (SCB).
    
    Note: This data is national-level only (no regional breakdown available).
    """
    data_access = get_data_access()
    occupations = parse_occupations(occupation)
    return data_access.get_income_dispersion(
        occupations=occupations,
        year=year,
        gender=gender,
    )


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
