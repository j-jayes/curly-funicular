"""Data models and schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class IncomeData(BaseModel):
    """Income data model."""
    
    occupation: str = Field(..., description="Occupation name")
    occupation_code: str = Field(..., description="SSYK occupation code")
    region: str = Field(..., description="Region name")
    region_code: str = Field(..., description="Region code")
    year: int = Field(..., description="Year")
    age_group: Optional[str] = Field(None, description="Age group")
    gender: Optional[str] = Field(None, description="Gender")
    median_income: Optional[float] = Field(None, description="Median income in SEK")
    mean_income: Optional[float] = Field(None, description="Mean income in SEK")
    income_percentile_10: Optional[float] = Field(None, description="10th percentile income")
    income_percentile_90: Optional[float] = Field(None, description="90th percentile income")


class JobAd(BaseModel):
    """Job advertisement model."""
    
    id: str = Field(..., description="Job ad ID")
    headline: str = Field(..., description="Job headline")
    employer: Optional[str] = Field(None, description="Employer name")
    occupation: str = Field(..., description="Occupation")
    occupation_code: str = Field(..., description="Occupation code")
    region: str = Field(..., description="Region")
    region_code: str = Field(..., description="Region code")
    published_date: Optional[datetime] = Field(None, description="Publication date")
    application_deadline: Optional[datetime] = Field(None, description="Application deadline")
    number_of_vacancies: int = Field(1, description="Number of vacancies")
    employment_type: Optional[str] = Field(None, description="Employment type")
    working_hours_type: Optional[str] = Field(None, description="Working hours type")


class Occupation(BaseModel):
    """Occupation model."""
    
    code: str = Field(..., description="SSYK occupation code")
    name: str = Field(..., description="Occupation name")


class Region(BaseModel):
    """Region model."""
    
    code: str = Field(..., description="Region code")
    name: str = Field(..., description="Region name")


class StatsResponse(BaseModel):
    """Statistics response model."""
    
    total_occupations: int = Field(..., description="Total number of occupations")
    total_regions: int = Field(..., description="Total number of regions")
    total_job_ads: int = Field(..., description="Total number of active job ads")
    avg_income: Optional[float] = Field(None, description="Average income across all data")
