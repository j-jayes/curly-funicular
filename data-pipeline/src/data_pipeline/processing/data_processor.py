"""Data processing modules.

Handles transformation, cleaning, and aggregation of labor market data.
"""

import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Occupation labels for SSYK codes
SSYK_LABELS = {
    "2511": "Systems analysts and IT architects",
    "2512": "Software and systems developers",
}


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
            "ContentsCode": "measure",
            "value": "value",
        }
        
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Add occupation labels
        if "ssyk_code" in df.columns:
            df["occupation"] = df["ssyk_code"].map(SSYK_LABELS)
        
        # Pivot measure codes to columns for easier analysis
        if "measure" in df.columns and "value" in df.columns:
            measure_labels = {
                "000000NV": "avg_monthly_salary",
                "000000O0": "percentile_10",
                "000000O1": "median_salary",
                "000000O2": "percentile_90",
            }
            df["measure_name"] = df["measure"].map(measure_labels)
            
            # Keep both long and wide format options
            df_long = df.copy()
            
            # Create wide format for common use cases
            id_cols = [c for c in ["year", "region_code", "region_name", "ssyk_code", 
                                   "occupation", "gender_code", "gender"] 
                       if c in df.columns]
            
            if "measure_name" in df.columns and df["measure_name"].notna().any():
                try:
                    df_wide = df.pivot_table(
                        index=id_cols,
                        columns="measure_name",
                        values="value",
                        aggfunc="first"
                    ).reset_index()
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
        
        # Add occupation labels
        if "ssyk_code" in df.columns:
            df["occupation"] = df["ssyk_code"].map(SSYK_LABELS)
        
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
        
        # Add occupation labels
        if "ssyk_code" in agg.columns:
            agg["occupation"] = agg["ssyk_code"].map(SSYK_LABELS)
        
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
            salary_cols = ["avg_monthly_salary", "median_salary", "value"]
            salary_col = next((c for c in salary_cols if c in income_df.columns), None)
            
            if salary_col:
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
        
        # Add occupation labels
        if "ssyk_code" in df.columns:
            df["occupation"] = df["ssyk_code"].map(SSYK_LABELS)
        
        # Standardize gender column
        if "gender" not in df.columns:
            if "gender_code" in df.columns:
                gender_map = {"1": "men", "2": "women", "1+2": "total"}
                df["gender"] = df["gender_code"].map(gender_map)
        
        logger.info(f"Processed {len(df)} dispersion records")
        logger.info(f"Columns: {list(df.columns)}")
        
        return df
    
    def save_processed_data(
        self,
        income_df: pd.DataFrame,
        jobs_df: pd.DataFrame,
        jobs_agg_df: pd.DataFrame,
        dispersion_df: Optional[pd.DataFrame] = None,
        skills_df: Optional[pd.DataFrame] = None,
    ) -> Dict[str, Path]:
        """Save all processed data to parquet files.
        
        Args:
            income_df: Processed income data
            jobs_df: Processed job ads (detail)
            jobs_agg_df: Aggregated job ads
            dispersion_df: Optional salary dispersion data
            skills_df: Optional skills data
            
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
        }
        
        for name, df in files.items():
            if df is not None and not df.empty:
                filepath = self.processed_dir / f"{name}.parquet"
                df.to_parquet(filepath, index=False, engine="pyarrow")
                paths[name] = filepath
                logger.info(f"Saved {name} to {filepath}")
        
        return paths
