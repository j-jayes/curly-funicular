"""Data models and schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class IncomeData(BaseModel):
    """Income data model.
    
    Represents salary statistics from SCB (Statistics Sweden).
    """
    
    occupation: str = Field(..., description="Occupation name with SSYK code")
    occupation_code: str = Field(..., description="SSYK occupation code (e.g., 2512)")
    region: str = Field(..., description="Region name (e.g., Stockholm)")
    region_code: str = Field(..., description="Region identifier")
    year: Optional[int] = Field(None, description="Year of data")
    gender: Optional[str] = Field(None, description="Gender (men/women)")
    monthly_salary: Optional[float] = Field(None, description="Monthly salary in SEK")
    
    class Config:
        """Pydantic config for flexible validation."""
        extra = "allow"


class IncomeDispersion(BaseModel):
    """Income dispersion data model for box plots.
    
    Represents salary distribution with percentiles from SCB.
    """
    
    occupation: str = Field(..., description="Occupation name")
    occupation_code: str = Field(default="", description="SSYK occupation code")
    year: Optional[int] = Field(None, description="Year of data")
    gender: Optional[str] = Field(None, description="Gender (men/women)")
    mean: Optional[float] = Field(None, description="Mean monthly salary in SEK")
    median: Optional[float] = Field(None, description="Median (P50) monthly salary in SEK")
    p10: Optional[float] = Field(None, description="10th percentile salary in SEK")
    p25: Optional[float] = Field(None, description="25th percentile (Q1) salary in SEK")
    p75: Optional[float] = Field(None, description="75th percentile (Q3) salary in SEK")
    p90: Optional[float] = Field(None, description="90th percentile salary in SEK")
    
    class Config:
        """Pydantic config for flexible validation."""
        extra = "allow"


class JobAd(BaseModel):
    """Job advertisement model.
    
    Represents a job ad from Arbetsförmedlingen.
    """
    
    id: str = Field(..., description="Job ad ID")
    headline: str = Field(..., description="Job headline")
    employer: Optional[str] = Field(None, description="Employer name")
    occupation: Optional[str] = Field(None, description="Occupation name")
    occupation_code: str = Field(..., description="SSYK occupation code")
    region: Optional[str] = Field(None, description="Region name")
    region_code: Optional[str] = Field(None, description="Region identifier")
    published_date: Optional[str] = Field(None, description="Publication date")
    application_deadline: Optional[str] = Field(None, description="Application deadline")
    number_of_vacancies: int = Field(1, description="Number of vacancies")
    employment_type: Optional[str] = Field(None, description="Employment type")
    working_hours_type: Optional[str] = Field(None, description="Working hours type")


class JobsAggregated(BaseModel):
    """Aggregated job statistics by region and occupation."""
    
    year: int = Field(..., description="Year")
    region: Optional[str] = Field(None, description="Region name")
    occupation: str = Field(..., description="Occupation name")
    ssyk_code: str = Field(..., description="SSYK occupation code")
    ad_count: int = Field(..., description="Number of job ads")
    total_vacancies: int = Field(..., description="Total number of vacancies")


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
    total_job_ads: int = Field(..., description="Total number of job ads")
    avg_income: Optional[float] = Field(None, description="Average monthly salary")
