"""Arbetsförmedlingen (Swedish Public Employment Service) API ingestion."""

import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ArbetsformedlingenIngestion:
    """Handles data ingestion from Arbetsförmedlingen API."""
    
    BASE_URL = "https://jobsearch.api.jobtechdev.se"
    
    def __init__(self):
        """Initialize Arbetsförmedlingen ingestion client."""
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "SwedishLaborMarketAnalytics/1.0"
        })
    
    def fetch_job_ads(
        self,
        occupation: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> pd.DataFrame:
        """Fetch job advertisements.
        
        Args:
            occupation: Occupation to filter by
            region: Region to filter by
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            DataFrame with job advertisements
        """
        logger.info("Fetching job ads from Arbetsförmedlingen")
        
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if occupation:
            params["occupation"] = occupation
        if region:
            params["region"] = region
        
        try:
            endpoint = f"{self.BASE_URL}/search"
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Transform response to DataFrame
            df = self._transform_job_ads(data)
            
            logger.info(f"Successfully fetched {len(df)} job ads")
            return df
            
        except requests.RequestException as e:
            logger.error(f"Error fetching job ads: {e}")
            raise
    
    def fetch_all_job_ads(
        self,
        occupation: Optional[str] = None,
        region: Optional[str] = None,
        max_results: int = 1000
    ) -> pd.DataFrame:
        """Fetch all job advertisements with pagination.
        
        Args:
            occupation: Occupation to filter by
            region: Region to filter by
            max_results: Maximum total results to fetch
            
        Returns:
            DataFrame with all job advertisements
        """
        all_ads = []
        offset = 0
        limit = 100
        
        while len(all_ads) < max_results:
            df = self.fetch_job_ads(
                occupation=occupation,
                region=region,
                limit=limit,
                offset=offset
            )
            
            if df.empty:
                break
            
            all_ads.append(df)
            offset += limit
            
            if len(df) < limit:
                break
        
        if all_ads:
            return pd.concat(all_ads, ignore_index=True)
        return pd.DataFrame()
    
    def _transform_job_ads(self, data: Dict) -> pd.DataFrame:
        """Transform API response to DataFrame.
        
        Args:
            data: Raw response from API
            
        Returns:
            Transformed DataFrame
        """
        if "hits" not in data:
            return pd.DataFrame()
        
        records = []
        for hit in data["hits"]:
            record = {
                "id": hit.get("id"),
                "headline": hit.get("headline"),
                "employer": hit.get("employer", {}).get("name"),
                "occupation": hit.get("occupation", {}).get("label"),
                "occupation_code": hit.get("occupation", {}).get("concept_id"),
                "region": hit.get("workplace_address", {}).get("municipality"),
                "region_code": hit.get("workplace_address", {}).get("municipality_code"),
                "published_date": hit.get("publication_date"),
                "application_deadline": hit.get("application_deadline"),
                "number_of_vacancies": hit.get("number_of_vacancies", 1),
                "employment_type": hit.get("employment_type", {}).get("label"),
                "duration": hit.get("duration", {}).get("label"),
                "working_hours_type": hit.get("working_hours_type", {}).get("label"),
                "salary_type": hit.get("salary_type", {}).get("label"),
                "description": hit.get("description", {}).get("text"),
            }
            records.append(record)
        
        return pd.DataFrame(records)
    
    def save_to_gcs(self, df: pd.DataFrame, bucket_name: str, blob_name: str):
        """Save DataFrame to Google Cloud Storage.
        
        Args:
            df: DataFrame to save
            bucket_name: GCS bucket name
            blob_name: Blob name/path in bucket
        """
        from google.cloud import storage
        
        logger.info(f"Saving data to GCS: gs://{bucket_name}/{blob_name}")
        
        # Save to temporary file
        temp_file = f"/tmp/{blob_name}"
        df.to_parquet(temp_file, index=False)
        
        # Upload to GCS
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(temp_file)
        
        logger.info(f"Successfully saved to GCS")
