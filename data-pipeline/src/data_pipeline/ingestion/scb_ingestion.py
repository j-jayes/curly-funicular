"""SCB (Statistics Sweden) data ingestion module."""

import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SCBIngestion:
    """Handles data ingestion from Statistics Sweden (SCB) API."""
    
    BASE_URL = "https://api.scb.se/OV0104/v1/doris/en/ssd"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize SCB ingestion client.
        
        Args:
            api_key: Optional API key for SCB
        """
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def fetch_income_data(
        self, 
        occupation_codes: Optional[List[str]] = None,
        region_codes: Optional[List[str]] = None,
        years: Optional[List[int]] = None
    ) -> pd.DataFrame:
        """Fetch income data by occupation and geography.
        
        Args:
            occupation_codes: List of occupation codes (SSYK)
            region_codes: List of region codes
            years: List of years to fetch data for
            
        Returns:
            DataFrame with income data
        """
        logger.info("Fetching income data from SCB")
        
        # Example query structure for SCB API
        # This is a skeleton - actual implementation would depend on SCB API structure
        query = {
            "query": [
                {
                    "code": "Yrke",
                    "selection": {
                        "filter": "item",
                        "values": occupation_codes or []
                    }
                },
                {
                    "code": "Region",
                    "selection": {
                        "filter": "item",
                        "values": region_codes or []
                    }
                },
                {
                    "code": "Tid",
                    "selection": {
                        "filter": "item",
                        "values": [str(y) for y in (years or [])]
                    }
                }
            ],
            "response": {
                "format": "json"
            }
        }
        
        try:
            # Placeholder endpoint - actual endpoint would be specific to income statistics
            endpoint = f"{self.BASE_URL}/AM/AM0110/AM0110A/LoneSpridSektorA"
            response = self.session.post(endpoint, json=query)
            response.raise_for_status()
            
            data = response.json()
            
            # Transform SCB response to DataFrame
            df = self._transform_scb_response(data)
            
            logger.info(f"Successfully fetched {len(df)} records from SCB")
            return df
            
        except requests.RequestException as e:
            logger.error(f"Error fetching data from SCB: {e}")
            raise
    
    def _transform_scb_response(self, data: Dict) -> pd.DataFrame:
        """Transform SCB API response to DataFrame.
        
        Args:
            data: Raw response from SCB API
            
        Returns:
            Transformed DataFrame
        """
        # This is a simplified transformation
        # Actual implementation depends on SCB response structure
        if "data" in data:
            records = []
            columns = data.get("columns", [])
            
            for row in data["data"]:
                record = {}
                for i, col in enumerate(columns):
                    if i < len(row.get("key", [])):
                        record[col["code"]] = row["key"][i]
                
                if "values" in row:
                    record["value"] = row["values"][0]
                
                records.append(record)
            
            return pd.DataFrame(records)
        
        return pd.DataFrame()
    
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
