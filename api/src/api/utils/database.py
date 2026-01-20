"""Database and data access utilities.

This module provides data access to processed Parquet files.
Supports both local file access and optional GCS access.
"""

import os
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# Path: api/src/api/utils/database.py -> go up 5 levels to project root
# Then into data-pipeline/data/processed
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
DEFAULT_DATA_PATH = PROJECT_ROOT / "data-pipeline" / "data" / "processed"

# SSYK code to occupation name mapping
SSYK_OCCUPATION_MAP = {
    "2511": "System analysts and ICT-architects",
    "2512": "Software- and system developers",
}

# Reverse mapping: name to code
OCCUPATION_TO_SSYK = {v: k for k, v in SSYK_OCCUPATION_MAP.items()}


class DataAccess:
    """Data access layer for Parquet files.
    
    Reads processed data from local Parquet files.
    Falls back to sample data if files don't exist.
    """
    
    def __init__(self, data_path: Optional[Path] = None):
        """Initialize data access.
        
        Args:
            data_path: Path to processed data directory. If None, uses default.
        """
        self.data_path = Path(data_path) if data_path else Path(
            os.getenv("DATA_PATH", str(DEFAULT_DATA_PATH))
        )
        logger.info(f"DataAccess initialized with path: {self.data_path}")
        
        # Load data on initialization
        self._income_df: Optional[pd.DataFrame] = None
        self._jobs_df: Optional[pd.DataFrame] = None
        self._jobs_agg_df: Optional[pd.DataFrame] = None
        
    def _load_income_data(self) -> pd.DataFrame:
        """Load income data from Parquet file."""
        if self._income_df is None:
            income_path = self.data_path / "income.parquet"
            if income_path.exists():
                self._income_df = pd.read_parquet(income_path)
                logger.info(f"Loaded {len(self._income_df)} income records")
            else:
                logger.warning(f"Income file not found at {income_path}")
                self._income_df = pd.DataFrame()
        return self._income_df
    
    def _load_jobs_data(self) -> pd.DataFrame:
        """Load job ads from Parquet file."""
        if self._jobs_df is None:
            jobs_path = self.data_path / "jobs_detail.parquet"
            if jobs_path.exists():
                self._jobs_df = pd.read_parquet(jobs_path)
                logger.info(f"Loaded {len(self._jobs_df)} job records")
            else:
                logger.warning(f"Jobs file not found at {jobs_path}")
                self._jobs_df = pd.DataFrame()
        return self._jobs_df
    
    def _load_jobs_aggregated(self) -> pd.DataFrame:
        """Load aggregated job data from Parquet file."""
        if self._jobs_agg_df is None:
            jobs_agg_path = self.data_path / "jobs_aggregated.parquet"
            if jobs_agg_path.exists():
                self._jobs_agg_df = pd.read_parquet(jobs_agg_path)
                logger.info(f"Loaded {len(self._jobs_agg_df)} aggregated job records")
            else:
                logger.warning(f"Aggregated jobs file not found at {jobs_agg_path}")
                self._jobs_agg_df = pd.DataFrame()
        return self._jobs_agg_df

    def get_income_data(
        self,
        occupation: Optional[str] = None,
        region: Optional[str] = None,
        year: Optional[int] = None,
        gender: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get income data with optional filters.
        
        Args:
            occupation: Occupation code filter (e.g., "2512")
            region: Region name filter (e.g., "Stockholm")
            year: Year filter
            gender: Gender filter ("men", "women", "total")
            limit: Maximum number of results
            
        Returns:
            List of income records as dictionaries
        """
        df = self._load_income_data()
        
        if df.empty:
            return []
        
        # Apply filters
        mask = pd.Series([True] * len(df))
        
        if occupation:
            mask &= df["occupation (SSYK 2012)"].str.contains(occupation, case=False, na=False)
        if region:
            mask &= df["region"].str.contains(region, case=False, na=False)
        if year:
            mask &= df["year"].astype(str) == str(year)
        if gender:
            mask &= df["sex"].str.lower() == gender.lower()
        
        filtered = df[mask].head(limit)
        
        # Transform to API format
        records = []
        for _, row in filtered.iterrows():
            # Get observation type (monthly_salary, num_employees, etc.)
            obs_type = row.get("observations", "")
            value = row.get("value")
            
            record = {
                "occupation": row.get("occupation (SSYK 2012)", ""),
                "occupation_code": row.get("occupation (SSYK 2012)", "").split()[0] if pd.notna(row.get("occupation (SSYK 2012)")) else "",
                "region": row.get("region", ""),
                "region_code": row.get("region", ""),  # Using region name as code for now
                "year": int(row.get("year", 0)) if pd.notna(row.get("year")) else None,
                "gender": row.get("sex", ""),
                "sector": row.get("sector", ""),
                "observation_type": obs_type,
                "value": float(value) if pd.notna(value) else None,
            }
            records.append(record)
        
        return records
    
    def get_income_summary(
        self,
        occupation: Optional[str] = None,
        region: Optional[str] = None,
        year: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get summarized income data by occupation and region.
        
        Pivots the data to show monthly_salary and num_employees as columns.
        """
        df = self._load_income_data()
        
        if df.empty:
            return []
        
        # Filter to monthly salary only
        mask = df["observations"].str.contains("salary", case=False, na=False)
        
        if occupation:
            mask &= df["occupation (SSYK 2012)"].str.contains(occupation, case=False, na=False)
        if region:
            mask &= df["region"].str.contains(region, case=False, na=False)
        if year:
            mask &= df["year"].astype(str) == str(year)
        
        filtered = df[mask]
        
        records = []
        for _, row in filtered.iterrows():
            occ_name = row.get("occupation (SSYK 2012)", "")
            # Look up SSYK code from occupation name
            occ_code = OCCUPATION_TO_SSYK.get(occ_name, "")
            
            records.append({
                "occupation": occ_name,
                "occupation_code": occ_code,
                "region": row.get("region", ""),
                "region_code": row.get("region", ""),
                "year": int(row.get("year", 0)) if pd.notna(row.get("year")) else None,
                "gender": row.get("sex", ""),
                "monthly_salary": float(row.get("value")) if pd.notna(row.get("value")) else None,
            })
        
        return records

    def get_job_ads(
        self,
        occupation: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get job advertisements with optional filters.
        
        Args:
            occupation: Occupation code filter
            region: Region name filter
            limit: Maximum number of results
            
        Returns:
            List of job ad records
        """
        df = self._load_jobs_data()
        
        if df.empty:
            return []
        
        # Apply filters
        mask = pd.Series([True] * len(df))
        
        if occupation:
            mask &= df["ssyk_code"].str.contains(occupation, na=False)
        if region:
            mask &= df["region"].str.contains(region, case=False, na=False)
        
        filtered = df[mask].head(limit)
        
        # Transform to API format
        records = []
        for _, row in filtered.iterrows():
            record = {
                "id": str(row.get("id", "")),
                "headline": row.get("headline", ""),
                "employer": row.get("employer_name", ""),
                "occupation": row.get("occupation", ""),
                "occupation_code": row.get("ssyk_code", ""),
                "region": row.get("region", ""),
                "region_code": row.get("region", ""),  # Using region name as code
                "published_date": str(row.get("published_date", "")) if pd.notna(row.get("published_date")) else None,
                "application_deadline": str(row.get("application_deadline", "")) if pd.notna(row.get("application_deadline")) else None,
                "number_of_vacancies": int(row.get("number_of_vacancies", 1)) if pd.notna(row.get("number_of_vacancies")) else 1,
                "employment_type": row.get("employment_type", ""),
                "working_hours_type": row.get("working_hours_type", ""),
            }
            records.append(record)
        
        return records
    
    def get_jobs_aggregated(
        self,
        occupation: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get aggregated job statistics by region and occupation.
        
        Args:
            occupation: Occupation code filter
            region: Region name filter
            
        Returns:
            List of aggregated job statistics
        """
        df = self._load_jobs_aggregated()
        
        if df.empty:
            return []
        
        # Apply filters
        mask = pd.Series([True] * len(df))
        
        if occupation:
            mask &= df["ssyk_code"].str.contains(occupation, na=False)
        if region:
            mask &= df["region"].str.contains(region, case=False, na=False)
        
        filtered = df[mask]
        
        records = []
        for _, row in filtered.iterrows():
            records.append({
                "year": int(row.get("year", 0)),
                "region": row.get("region", ""),
                "occupation": row.get("occupation", ""),
                "ssyk_code": row.get("ssyk_code", ""),
                "ad_count": int(row.get("ad_count", 0)),
                "total_vacancies": int(row.get("total_vacancies", 0)),
            })
        
        return records

    def get_occupations(self) -> List[Dict[str, str]]:
        """Get list of unique occupations in the dataset."""
        df = self._load_income_data()
        
        if df.empty:
            return []
        
        unique_occs = df["occupation (SSYK 2012)"].dropna().unique()
        
        occupations = []
        for occ_name in unique_occs:
            # Look up SSYK code from occupation name
            code = OCCUPATION_TO_SSYK.get(str(occ_name), "")
            occupations.append({"code": code, "name": str(occ_name)})
        
        return occupations

    def get_regions(self) -> List[Dict[str, str]]:
        """Get list of unique regions in the dataset."""
        df = self._load_income_data()
        
        if df.empty:
            return []
        
        unique_regions = df["region"].dropna().unique()
        
        return [{"code": r, "name": r} for r in unique_regions]

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall dataset statistics."""
        income_df = self._load_income_data()
        jobs_df = self._load_jobs_data()
        
        # Count unique occupations
        n_occupations = len(income_df["occupation (SSYK 2012)"].dropna().unique()) if not income_df.empty else 0
        
        # Count unique regions
        n_regions = len(income_df["region"].dropna().unique()) if not income_df.empty else 0
        
        # Total job ads
        n_jobs = len(jobs_df) if not jobs_df.empty else 0
        
        # Average monthly salary
        avg_salary = None
        if not income_df.empty:
            salary_mask = income_df["observations"].str.contains("salary", case=False, na=False)
            salaries = income_df.loc[salary_mask, "value"].dropna()
            if len(salaries) > 0:
                avg_salary = float(salaries.mean())
        
        return {
            "total_occupations": n_occupations,
            "total_regions": n_regions,
            "total_job_ads": n_jobs,
            "avg_income": avg_salary,
        }


# Singleton instance
_data_access: Optional[DataAccess] = None


def get_data_access() -> DataAccess:
    """Get or create the DataAccess singleton."""
    global _data_access
    if _data_access is None:
        _data_access = DataAccess()
    return _data_access

