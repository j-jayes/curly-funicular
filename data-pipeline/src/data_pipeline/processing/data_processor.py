"""Data processing modules."""

import pandas as pd
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and combine data from multiple sources."""
    
    def __init__(self):
        """Initialize data processor."""
        pass
    
    def merge_income_and_jobs(
        self,
        income_df: pd.DataFrame,
        jobs_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Merge income and job advertisement data.
        
        Args:
            income_df: Income data from SCB
            jobs_df: Job ads from Arbetsförmedlingen
            
        Returns:
            Merged DataFrame
        """
        logger.info("Merging income and job data")
        
        # Aggregate job data by occupation and region
        jobs_agg = jobs_df.groupby(['occupation_code', 'region_code']).agg({
            'id': 'count',
            'number_of_vacancies': 'sum'
        }).reset_index()
        jobs_agg.columns = ['occupation_code', 'region_code', 'num_job_ads', 'total_vacancies']
        
        # Merge with income data
        merged = pd.merge(
            income_df,
            jobs_agg,
            left_on=['occupation_code', 'region_code'],
            right_on=['occupation_code', 'region_code'],
            how='left'
        )
        
        logger.info(f"Merged data has {len(merged)} records")
        return merged
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate data.
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        logger.info("Cleaning data")
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        df = df.fillna({
            'num_job_ads': 0,
            'total_vacancies': 0
        })
        
        logger.info(f"Cleaned data has {len(df)} records")
        return df
    
    def add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features to the dataset.
        
        Args:
            df: DataFrame with basic features
            
        Returns:
            DataFrame with additional features
        """
        logger.info("Adding derived features")
        
        # Add features if needed
        # Example: income percentiles, job density, etc.
        
        return df
