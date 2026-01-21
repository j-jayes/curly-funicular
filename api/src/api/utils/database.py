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

# SSYK code to occupation name mapping (ICT, data science, and related)
SSYK_OCCUPATION_MAP = {
    # ICT Professionals (25xx)
    "2511": "System analysts and ICT-architects",
    "2512": "Software- and system developers",
    "2513": "Games and digital media developers",
    "2514": "System testers and test managers",
    "2515": "System administrators",
    "2516": "Security specialists (ICT)",
    "2519": "ICT-specialist professionals not elsewhere classified",
    # Data Science related (21xx)
    "2121": "Mathematicians and actuaries",
    "2122": "Statisticians",
    # Design (21xx)
    "2173": "Game and digital media designers",
    # Electronics/Telecom Engineering (21xx)
    "2143": "Engineering professionals in electrical, electronics and telecommunications",
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
        self._dispersion_df: Optional[pd.DataFrame] = None
        self._skills_df: Optional[pd.DataFrame] = None
        
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
    
    def _load_dispersion_data(self) -> pd.DataFrame:
        """Load salary dispersion data from Parquet file."""
        if self._dispersion_df is None:
            dispersion_path = self.data_path / "income_dispersion.parquet"
            if dispersion_path.exists():
                self._dispersion_df = pd.read_parquet(dispersion_path)
                logger.info(f"Loaded {len(self._dispersion_df)} dispersion records")
            else:
                logger.warning(f"Dispersion file not found at {dispersion_path}")
                self._dispersion_df = pd.DataFrame()
        return self._dispersion_df

    def _load_skills_data(self) -> pd.DataFrame:
        """Load skills data extracted from job ads."""
        if self._skills_df is None:
            skills_path = self.data_path / "skills.parquet"
            if skills_path.exists():
                self._skills_df = pd.read_parquet(skills_path)
                # Ensure ssyk_code is string for filtering
                if "ssyk_code" in self._skills_df.columns:
                    self._skills_df["ssyk_code"] = self._skills_df["ssyk_code"].astype(str)
                logger.info(f"Loaded {len(self._skills_df)} skills records")
            else:
                logger.warning(f"Skills file not found at {skills_path}")
                self._skills_df = pd.DataFrame()
        return self._skills_df

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
        occupations: Optional[List[str]] = None,
        region: Optional[str] = None,
        year: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get summarized income data by occupation and region.
        
        Pivots the data to show monthly_salary and num_employees as columns.
        
        Args:
            occupations: List of occupation codes/names to filter by (supports multiple)
            region: Region name filter
            year: Year filter
        """
        df = self._load_income_data()
        
        if df.empty:
            return []
        
        # Filter to monthly salary only
        mask = df["observations"].str.contains("salary", case=False, na=False)
        
        # Support multiple occupations
        if occupations and len(occupations) > 0:
            occ_mask = pd.Series([False] * len(df))
            for occ in occupations:
                occ_mask |= df["occupation (SSYK 2012)"].str.contains(occ, case=False, na=False)
            mask &= occ_mask
        if region:
            mask &= df["region"].str.contains(region, case=False, na=False)
        if year:
            mask &= df["year"].astype(str) == str(year)
        
        filtered = df[mask]
        
        # Also get number of employees for weighting
        emp_mask = df["observations"].str.contains("employees", case=False, na=False)
        if occupations and len(occupations) > 0:
            occ_mask = pd.Series([False] * len(df))
            for occ in occupations:
                occ_mask |= df["occupation (SSYK 2012)"].str.contains(occ, case=False, na=False)
            emp_mask &= occ_mask
        if region:
            emp_mask &= df["region"].str.contains(region, case=False, na=False)
        if year:
            emp_mask &= df["year"].astype(str) == str(year)
        
        emp_df = df[emp_mask]
        
        # Create lookup for employee counts
        emp_lookup = {}
        for _, row in emp_df.iterrows():
            key = (row.get("occupation (SSYK 2012)", ""), row.get("region", ""), row.get("sex", ""), row.get("year", ""))
            emp_lookup[key] = float(row.get("value", 0)) if pd.notna(row.get("value")) else 0
        
        records = []
        for _, row in filtered.iterrows():
            occ_name = row.get("occupation (SSYK 2012)", "")
            # Look up SSYK code from occupation name
            occ_code = OCCUPATION_TO_SSYK.get(occ_name, "")
            
            # Get employee count for this record
            emp_key = (occ_name, row.get("region", ""), row.get("sex", ""), row.get("year", ""))
            num_employees = emp_lookup.get(emp_key, 0)
            
            records.append({
                "occupation": occ_name,
                "occupation_code": occ_code,
                "region": row.get("region", ""),
                "region_code": row.get("region", ""),
                "year": int(row.get("year", 0)) if pd.notna(row.get("year")) else None,
                "gender": row.get("sex", ""),
                "monthly_salary": float(row.get("value")) if pd.notna(row.get("value")) else None,
                "num_employees": num_employees,
            })
        
        return records

    def get_job_ads(
        self,
        occupations: Optional[List[str]] = None,
        region: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get job advertisements with optional filters.
        
        Args:
            occupations: List of occupation codes to filter by (supports multiple)
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
        
        # Support multiple occupations
        if occupations and len(occupations) > 0:
            occ_mask = pd.Series([False] * len(df))
            for occ in occupations:
                occ_mask |= df["ssyk_code"].str.contains(occ, na=False)
            mask &= occ_mask
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
        occupations: Optional[List[str]] = None,
        region: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get aggregated job statistics by region and occupation.
        
        Args:
            occupations: List of occupation codes to filter by (supports multiple)
            region: Region name filter
            
        Returns:
            List of aggregated job statistics
        """
        df = self._load_jobs_aggregated()
        
        if df.empty:
            return []
        
        # Apply filters
        mask = pd.Series([True] * len(df))
        
        # Support multiple occupations
        if occupations and len(occupations) > 0:
            occ_mask = pd.Series([False] * len(df))
            for occ in occupations:
                occ_mask |= df["ssyk_code"].str.contains(occ, na=False)
            mask &= occ_mask
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

    def get_top_employers(
        self,
        occupations: Optional[List[str]] = None,
        region: Optional[str] = None,
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        """Get top employers by job ad count.
        
        Args:
            occupations: List of occupation codes to filter by (supports multiple)
            region: Region name filter
            limit: Maximum number of employers to return
            
        Returns:
            List of top employers with ad and vacancy counts
        """
        df = self._load_jobs_data()
        
        if df.empty:
            return []
        
        # Apply filters
        mask = pd.Series([True] * len(df))
        
        # Support multiple occupations
        if occupations and len(occupations) > 0:
            occ_mask = pd.Series([False] * len(df))
            for occ in occupations:
                occ_mask |= df["ssyk_code"].str.contains(occ, na=False)
            mask &= occ_mask
        if region:
            mask &= df["region"].str.contains(region, case=False, na=False)
        
        filtered = df[mask]
        
        if filtered.empty:
            return []
        
        # Aggregate by employer
        employer_stats = filtered.groupby("employer_name").agg({
            "id": "count",
            "number_of_vacancies": "sum",
            "region": lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else "Unknown"
        }).reset_index()
        
        employer_stats.columns = ["employer", "ad_count", "total_vacancies", "primary_region"]
        employer_stats = employer_stats.sort_values("ad_count", ascending=False).head(limit)
        
        records = []
        for _, row in employer_stats.iterrows():
            records.append({
                "employer": row["employer"],
                "ad_count": int(row["ad_count"]),
                "total_vacancies": int(row["total_vacancies"]) if pd.notna(row["total_vacancies"]) else int(row["ad_count"]),
                "primary_region": row["primary_region"],
            })
        
        return records
    
    def get_income_dispersion(
        self,
        occupations: Optional[List[str]] = None,
        year: Optional[int] = None,
        gender: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get salary dispersion data with percentiles for box plots.
        
        Returns data with P10, P25, Median, P75, P90 for each occupation/gender.
        
        Args:
            occupations: List of occupation names to filter by (supports multiple)
            year: Year filter
            gender: Gender filter ("men", "women")
            
        Returns:
            List of dispersion records with percentile columns
        """
        df = self._load_dispersion_data()
        
        if df.empty:
            return []
        
        # Apply filters
        mask = pd.Series([True] * len(df))
        
        # Support multiple occupations
        if occupations and len(occupations) > 0:
            occ_col = "occupation (SSYK 2012)" if "occupation (SSYK 2012)" in df.columns else "occupation"
            if occ_col in df.columns:
                occ_mask = pd.Series([False] * len(df))
                for occ in occupations:
                    occ_mask |= df[occ_col].str.contains(occ, case=False, na=False)
                mask &= occ_mask
        if year:
            mask &= df["year"].astype(str) == str(year)
        if gender:
            mask &= df["sex"].str.lower() == gender.lower()
        
        filtered = df[mask]
        
        # Pivot the data to wide format (one row per occupation/year/gender)
        occ_col = "occupation (SSYK 2012)" if "occupation (SSYK 2012)" in df.columns else "occupation"
        id_cols = [c for c in [occ_col, "year", "sex"] if c in filtered.columns]
        
        if "observations" not in filtered.columns or "value" not in filtered.columns:
            logger.warning("Missing required columns for dispersion pivot")
            return []
        
        try:
            pivot_df = filtered.pivot_table(
                index=id_cols,
                columns="observations",
                values="value",
                aggfunc="first"
            ).reset_index()
            
            # Rename columns for API
            column_map = {
                "Monthly salary": "mean",
                "Median": "median",
                "10th percentile": "p10",
                "25th percentile": "p25",
                "75th percentile": "p75",
                "90th percentile": "p90",
            }
            pivot_df = pivot_df.rename(columns=column_map)
            
            records = []
            for _, row in pivot_df.iterrows():
                occ_name = row.get(occ_col, "")
                # Look up SSYK code from occupation name
                occ_code = OCCUPATION_TO_SSYK.get(str(occ_name), "")
                
                records.append({
                    "occupation": occ_name,
                    "occupation_code": occ_code,
                    "year": int(row.get("year", 0)) if pd.notna(row.get("year")) else None,
                    "gender": row.get("sex", ""),
                    "mean": float(row.get("mean")) if pd.notna(row.get("mean")) else None,
                    "median": float(row.get("median")) if pd.notna(row.get("median")) else None,
                    "p10": float(row.get("p10")) if pd.notna(row.get("p10")) else None,
                    "p25": float(row.get("p25")) if pd.notna(row.get("p25")) else None,
                    "p75": float(row.get("p75")) if pd.notna(row.get("p75")) else None,
                    "p90": float(row.get("p90")) if pd.notna(row.get("p90")) else None,
                })
            
            return records
            
        except Exception as e:
            logger.error(f"Error pivoting dispersion data: {e}")
            return []
    
    def get_top_skills(
        self,
        occupations: Optional[List[str]] = None,
        skill_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get top skills extracted from job advertisements.
        
        Args:
            occupations: List of occupation codes to filter by
            skill_type: Filter by type: "competency", "trait", or "occupation"
            limit: Maximum number of skills to return
            
        Returns:
            List of skills with occurrence counts
        """
        skills_df = self._load_skills_data()
        
        if skills_df.empty:
            return []
        
        # Apply filters
        mask = pd.Series([True] * len(skills_df))
        
        if occupations and len(occupations) > 0:
            if "ssyk_code" in skills_df.columns:
                occ_mask = pd.Series([False] * len(skills_df))
                for occ in occupations:
                    occ_mask |= skills_df["ssyk_code"].str.contains(occ, na=False)
                mask &= occ_mask
        
        if skill_type:
            if "skill_type" in skills_df.columns:
                mask &= skills_df["skill_type"] == skill_type
        
        filtered = skills_df[mask]
        
        if filtered.empty:
            return []
        
        # Aggregate by skill
        if "skill" in filtered.columns:
            skill_counts = filtered.groupby(["skill", "skill_type"]).agg({
                "occurrence_count": "sum" if "occurrence_count" in filtered.columns else "size",
                "avg_probability": "mean" if "avg_probability" in filtered.columns else lambda x: 0.8
            }).reset_index()
            
            if "occurrence_count" not in skill_counts.columns:
                skill_counts["occurrence_count"] = filtered.groupby(["skill", "skill_type"]).size().values
            if "avg_probability" not in skill_counts.columns:
                skill_counts["avg_probability"] = 0.8
            
            skill_counts = skill_counts.sort_values("occurrence_count", ascending=False).head(limit)
            
            records = []
            for _, row in skill_counts.iterrows():
                records.append({
                    "skill": row["skill"],
                    "skill_type": row["skill_type"],
                    "occurrence_count": int(row["occurrence_count"]),
                    "avg_probability": float(row["avg_probability"]),
                })
            
            return records
        
        return []


# Singleton instance
_data_access: Optional[DataAccess] = None


def get_data_access() -> DataAccess:
    """Get or create the DataAccess singleton."""
    global _data_access
    if _data_access is None:
        _data_access = DataAccess()
    return _data_access

