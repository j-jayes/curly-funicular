"""Income data endpoints."""

from fastapi import APIRouter, Query
from typing import List, Optional
from api.models.schemas import IncomeData, Occupation, Region, StatsResponse

router = APIRouter()


@router.get("/income", response_model=List[IncomeData])
async def get_income_data(
    occupation: Optional[str] = Query(None, description="Filter by occupation code"),
    region: Optional[str] = Query(None, description="Filter by region code"),
    age_group: Optional[str] = Query(None, description="Filter by age group"),
    gender: Optional[str] = Query(None, description="Filter by gender (M/F)"),
    year: Optional[int] = Query(None, description="Filter by year"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results")
):
    """Get income data with optional filters.
    
    This endpoint returns income statistics by occupation and geography.
    Data can be filtered by occupation, region, age group, gender, and year.
    """
    # TODO: Implement actual data retrieval from GCS/BigQuery
    # For now, return sample data
    sample_data = [
        {
            "occupation": "Software Developer",
            "occupation_code": "2512",
            "region": "Stockholm",
            "region_code": "01",
            "year": 2023,
            "age_group": "25-34",
            "gender": "M",
            "median_income": 45000,
            "mean_income": 48000,
            "income_percentile_10": 35000,
            "income_percentile_90": 65000
        }
    ]
    
    return sample_data


@router.get("/occupations", response_model=List[Occupation])
async def get_occupations():
    """Get list of available occupations.
    
    Returns all occupations available in the dataset with their SSYK codes.
    """
    # TODO: Implement actual data retrieval
    sample_occupations = [
        {"code": "2512", "name": "Software Developer"},
        {"code": "2513", "name": "Web Developer"},
        {"code": "2514", "name": "Applications Programmer"},
    ]
    
    return sample_occupations


@router.get("/regions", response_model=List[Region])
async def get_regions():
    """Get list of available regions.
    
    Returns all Swedish regions available in the dataset.
    """
    # TODO: Implement actual data retrieval
    sample_regions = [
        {"code": "01", "name": "Stockholm"},
        {"code": "03", "name": "Uppsala"},
        {"code": "04", "name": "Södermanland"},
    ]
    
    return sample_regions


@router.get("/stats", response_model=StatsResponse)
async def get_statistics():
    """Get aggregated statistics.
    
    Returns overall statistics about the dataset.
    """
    # TODO: Implement actual statistics calculation
    return {
        "total_occupations": 450,
        "total_regions": 21,
        "total_job_ads": 15000,
        "avg_income": 42000
    }
