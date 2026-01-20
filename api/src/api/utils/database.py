"""Database and data access utilities."""

from google.cloud import storage, bigquery
from typing import Optional
import os


class DataAccess:
    """Data access layer for GCS and BigQuery."""
    
    def __init__(self):
        """Initialize data access clients."""
        self.gcs_client = storage.Client()
        self.bq_client = bigquery.Client()
        
        self.bucket_name = os.getenv("GCS_BUCKET_NAME", "labor-market-data")
        self.dataset_name = os.getenv("BIGQUERY_DATASET", "labor_market")
    
    def get_from_gcs(self, blob_name: str) -> bytes:
        """Retrieve data from Google Cloud Storage.
        
        Args:
            blob_name: Name of the blob to retrieve
            
        Returns:
            Blob content as bytes
        """
        bucket = self.gcs_client.bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        return blob.download_as_bytes()
    
    def query_bigquery(self, query: str) -> list:
        """Execute a BigQuery query.
        
        Args:
            query: SQL query to execute
            
        Returns:
            Query results as list of dictionaries
        """
        query_job = self.bq_client.query(query)
        results = query_job.result()
        
        return [dict(row) for row in results]
    
    def get_income_data(
        self,
        occupation: Optional[str] = None,
        region: Optional[str] = None,
        year: Optional[int] = None
    ) -> list:
        """Get income data from BigQuery.
        
        Args:
            occupation: Occupation code filter
            region: Region code filter
            year: Year filter
            
        Returns:
            List of income records
        """
        query = f"""
        SELECT *
        FROM `{self.dataset_name}.income_data`
        WHERE 1=1
        """
        
        if occupation:
            query += f" AND occupation_code = '{occupation}'"
        if region:
            query += f" AND region_code = '{region}'"
        if year:
            query += f" AND year = {year}"
        
        query += " LIMIT 1000"
        
        return self.query_bigquery(query)
    
    def get_job_ads(
        self,
        occupation: Optional[str] = None,
        region: Optional[str] = None
    ) -> list:
        """Get job advertisements from BigQuery.
        
        Args:
            occupation: Occupation code filter
            region: Region code filter
            
        Returns:
            List of job ad records
        """
        query = f"""
        SELECT *
        FROM `{self.dataset_name}.job_ads`
        WHERE 1=1
        """
        
        if occupation:
            query += f" AND occupation_code = '{occupation}'"
        if region:
            query += f" AND region_code = '{region}'"
        
        query += " LIMIT 1000"
        
        return self.query_bigquery(query)
