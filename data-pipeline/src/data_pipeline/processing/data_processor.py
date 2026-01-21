"""Data processing modules.

Handles transformation, cleaning, and aggregation of labor market data.
"""

import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """Process and combine data from multiple sources."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize data processor.
        
        Args:
            data_dir: Directory for data files (default: data-pipeline/data)
        """
        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent.parent.parent / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.processed_dir = self.data_dir / "processed"
        self.raw_dir = self.data_dir / "raw"
        
        # Create directories if needed
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
    
    def process_income_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process raw SCB income data into analysis-ready format.
        
        Args:
            df: Raw income data from SCB
            
        Returns:
            Processed DataFrame in tidy format
        """
        logger.info(f"Processing {len(df)} income records")
        
        df = df.copy()
        
        # Standardize column names
        column_mapping = {
            "Tid": "year",
            "Region": "region_code", 
            "Yrke2012": "ssyk_code",
            "Kon": "gender_code",
            "ContentsCode": "measure_code",
            "value": "value",
        }
        
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Ensure occupation label exists
        if "occupation_name" in df.columns:
            df["occupation"] = df["occupation_name"]
        elif "occupation" not in df.columns and "ssyk_code" in df.columns:
             # Fallback (unlikely if ingestion works)
             df["occupation"] = df["ssyk_code"]
        
        # Ensure measure column works for pivoting
        # Ingestion produces 'measure' column with values like 'monthly_salary', 'num_employees'
        if "measure" in df.columns:
            # We can use this directly for pivoting
            pass
        else:
             # Fallback mapping if ingestion didn't run _add_labels
             logger.warning("Measure column missing, raw codes might be used")
             df["measure"] = df.get("measure_code", df.get("ContentsCode"))

        # Create wide format for common use cases
        # We want columns: year, region, occupation, gender, monthly_salary, num_employees
        if "measure" in df.columns and "value" in df.columns:
             try:
                id_cols = [c for c in ["year", "region_code", "region_name", "ssyk_code", 
                                       "occupation", "gender_code", "gender", "sector_name", "sector"] 
                           if c in df.columns]
                
                # Check duplicates before pivoting
                if df.duplicated(subset=id_cols + ["measure"]).any():
                    logger.warning("Duplicates found in income data, taking first")
                
                df_wide = df.pivot_table(
                    index=id_cols,
                    columns="measure",
                    values="value",
                    aggfunc="first"
                ).reset_index()
                
                # Cleanup column names (remove name of index)
                df_wide.columns.name = None
                
                logger.info(f"Created wide format with {len(df_wide)} records")
                return df_wide
             except Exception as e:
                logger.warning(f"Could not pivot to wide format: {e}")
        
        logger.info(f"Processed {len(df)} income records (long format)")
        return df
    
    def process_jobs_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process raw job ads data.
        
        Args:
            df: Raw job ads from Arbetsförmedlingen
            
        Returns:
            Processed DataFrame
        """
        logger.info(f"Processing {len(df)} job ad records")
        
        df = df.copy()
        
        # Convert dates
        if "published_date" in df.columns:
            df["published_date"] = pd.to_datetime(df["published_date"], errors="coerce")
            df["year"] = df["published_date"].dt.year
            df["month"] = df["published_date"].dt.month
            df["year_month"] = df["published_date"].dt.to_period("M").astype(str)
        
        # Clean vacancies
        if "number_of_vacancies" in df.columns:
            df["number_of_vacancies"] = pd.to_numeric(
                df["number_of_vacancies"], errors="coerce"
            ).fillna(1).astype(int)
        
        logger.info(f"Processed {len(df)} job ad records")
        return df
    
    def aggregate_jobs_by_region(
        self, 
        df: pd.DataFrame,
        period: str = "year"
    ) -> pd.DataFrame:
        """Aggregate job ads by region and time period.
        
        Args:
            df: Processed job ads DataFrame
            period: Aggregation period ('year', 'month', 'year_month')
            
        Returns:
            Aggregated DataFrame
        """
        if df.empty:
            return df
        
        group_cols = [period, "region", "ssyk_code"]
        group_cols = [c for c in group_cols if c in df.columns]
        
        if not group_cols:
            logger.warning("No valid group columns found")
            return df
        
        agg = df.groupby(group_cols, dropna=False).agg({
            "id": "count",
            "number_of_vacancies": "sum",
        }).reset_index()
        
        agg = agg.rename(columns={
            "id": "ad_count",
            "number_of_vacancies": "total_vacancies",
        })
        
        logger.info(f"Aggregated to {len(agg)} records")
        return agg
    
    def create_summary_stats(self, income_df: pd.DataFrame, jobs_df: pd.DataFrame) -> Dict:
        """Create summary statistics for the dashboard.
        
        Args:
            income_df: Processed income data
            jobs_df: Processed job ads data
            
        Returns:
            Dictionary with summary statistics
        """
        stats = {
            "income": {},
            "jobs": {},
        }
        
        # Income stats
        if not income_df.empty:
            # Look for monthly_salary column (from pivot) OR 'value' if long format
            salary_cols = ["monthly_salary", "avg_monthly_salary", "median_salary", "value"]
            salary_col = next((c for c in salary_cols if c in income_df.columns), None)
            
            if salary_col and pd.api.types.is_numeric_dtype(income_df[salary_col]):
                stats["income"] = {
                    "mean_salary": float(income_df[salary_col].mean()),
                    "min_salary": float(income_df[salary_col].min()),
                    "max_salary": float(income_df[salary_col].max()),
                    "record_count": len(income_df),
                }
            
            if "year" in income_df.columns:
                stats["income"]["years"] = sorted(income_df["year"].dropna().unique().tolist())
        
        # Jobs stats
        if not jobs_df.empty:
            stats["jobs"] = {
                "total_ads": len(jobs_df),
                "total_vacancies": int(jobs_df.get("number_of_vacancies", pd.Series([0])).sum()),
                "unique_employers": int(jobs_df.get("employer_name", pd.Series()).nunique()),
            }
            
            if "region" in jobs_df.columns:
                stats["jobs"]["top_regions"] = (
                    jobs_df["region"].value_counts().head(5).to_dict()
                )
        
        return stats
    
    def process_dispersion_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process raw SCB salary dispersion data.
        
        The dispersion data contains percentiles (P10, P25, median, P75, P90)
        for salary distributions by occupation and gender.
        
        Args:
            df: Raw dispersion data from SCB
            
        Returns:
            Processed DataFrame with percentile columns
        """
        logger.info(f"Processing {len(df)} dispersion records")
        
        df = df.copy()
        
        # Standardize column names
        column_mapping = {
            "Tid": "year",
            "Yrke2012": "ssyk_code",
            "Kon": "gender_code",
            "Sektor": "sector_code",
        }
        
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns and new_name not in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        if "occupation_name" in df.columns:
            df["occupation"] = df["occupation_name"]

        # Standardize gender column
        if "gender" not in df.columns:
            if "gender_code" in df.columns:
                gender_map = {"1": "men", "2": "women", "1+2": "total"}
                df["gender"] = df["gender_code"].map(gender_map)
        
        logger.info(f"Processed {len(df)} dispersion records")
        
        return df

    def process_income_by_age_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process income data by age."""
        if df.empty:
            return df
        
        logger.info(f"Processing {len(df)} income by age records")
        df = df.copy()
        
        column_mapping = {
            "Tid": "year", 
            "Yrke2012": "ssyk_code", 
            "Kon": "gender_code", 
            "Alder": "age_group", 
            "value": "monthly_salary",
            "Sektor": "sector_code"
        }
        for old, new in column_mapping.items():
            if old in df.columns:
                df = df.rename(columns={old: new})
        
        if "occupation_name" in df.columns:
            df["occupation"] = df["occupation_name"]

        # Standardize gender
        if "gender" not in df.columns and "gender_code" in df.columns:
            gender_map = {"1": "men", "2": "women", "1+2": "total"}
            df["gender"] = df["gender_code"].map(gender_map)
            
        return df

    def process_income_by_education_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process income data by education."""
        if df.empty:
            return df
            
        logger.info(f"Processing {len(df)} income by education records")
        df = df.copy()
        
        column_mapping = {
            "Tid": "year", 
            "Yrke2012": "ssyk_code", 
            "Kon": "gender_code", 
            "Utbildningsniva": "education_level", 
            "value": "monthly_salary",
            "Sektor": "sector_code"
        }
        for old, new in column_mapping.items():
            if old in df.columns:
                df = df.rename(columns={old: new})
                
        if "occupation_name" in df.columns:
            df["occupation"] = df["occupation_name"]

        if "gender" not in df.columns and "gender_code" in df.columns:
            gender_map = {"1": "men", "2": "women", "1+2": "total"}
            df["gender"] = df["gender_code"].map(gender_map)
            
        return df
    
    def save_processed_data(
        self,
        income_df: pd.DataFrame,
        jobs_df: pd.DataFrame,
        jobs_agg_df: pd.DataFrame,
        dispersion_df: Optional[pd.DataFrame] = None,
        skills_df: Optional[pd.DataFrame] = None,
        age_df: Optional[pd.DataFrame] = None,
        education_df: Optional[pd.DataFrame] = None,
    ) -> Dict[str, Path]:
        """Save all processed data to parquet files.
        
        Args:
            income_df: Processed income data (regional)
            jobs_df: Processed job ads (detail)
            jobs_agg_df: Aggregated job ads
            dispersion_df: Optional salary dispersion data
            skills_df: Optional skills data
            age_df: Optional income by age data
            education_df: Optional income by education data
            
        Returns:
            Dictionary with paths to saved files
        """
        paths = {}
        
        files = {
            "income": income_df,
            "jobs_detail": jobs_df,
            "jobs_aggregated": jobs_agg_df,
            "income_dispersion": dispersion_df,
            "skills": skills_df,
            "income_by_age": age_df,
            "income_by_education": education_df,
        }
        
        for name, df in files.items():
            if df is not None and not df.empty:
                filepath = self.processed_dir / f"{name}.parquet"
                df.to_parquet(filepath, index=False, engine="pyarrow")
                paths[name] = filepath
                logger.info(f"Saved {name} to {filepath}")
        
        return paths
