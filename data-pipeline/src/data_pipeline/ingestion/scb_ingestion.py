"""SCB (Statistics Sweden) data ingestion module.

This module fetches income data from SCB's API using JSON-stat2 format.
Implements rate limiting (3 req/sec) and request chunking to stay within
SCB's limits (30 req/10 sec, 150K cells/request).
"""

import httpx
import pandas as pd
from pyjstat import pyjstat
from typing import Dict, List, Optional
from pathlib import Path
import time
import logging
import hashlib

logger = logging.getLogger(__name__)

# NUTS region code to name mapping (used in this SCB table)
NUTS_REGION_CODES = {
    "SE": "Sweden",
    "SE11": "Stockholm",
    "SE12": "East-Central Sweden",
    "SE21": "Småland and islands",
    "SE22": "South Sweden",
    "SE23": "West Sweden",
    "SE31": "North-Central Sweden",
    "SE32": "Central Norrland",
    "SE33": "Upper Norrland",
}

# All NUTS region codes for full coverage
ALL_REGION_CODES = list(NUTS_REGION_CODES.keys())

# Sector codes
SECTOR_CODES = {
    "0": "All sectors",
    "1-3": "Public sector",
    "4-5": "Private sector",
}

# Gender code mapping
GENDER_CODES = {"1": "men", "2": "women", "1+2": "total"}

# Contents code mapping  
CONTENTS_CODES = {
    "000007AQ": "basic_salary",
    "000007AS": "monthly_salary",
    "000007AR": "gender_salary_ratio",
    "000007AP": "num_employees",
}

# SSYK 2012 occupation codes for ICT, data science, and related fields
# Full 4-digit codes for software engineers, data scientists, and related
DEFAULT_SSYK_CODES = [
    # ICT Professionals (25xx)
    "2511",  # System analysts and ICT-architects
    "2512",  # Software- and system developers
    "2513",  # Games and digital media developers
    "2514",  # System testers and test managers
    "2515",  # System administrators
    "2516",  # Security specialists (ICT)
    "2519",  # ICT-specialist professionals not elsewhere classified
    # Data Science related (21xx)
    "2121",  # Mathematicians and actuaries
    "2122",  # Statisticians
    # Design (21xx)
    "2173",  # Game and digital media designers
    # Electronics/Telecom Engineering (21xx)
    "2143",  # Engineering professionals in electrical, electronics and telecommunications
]

SSYK_OCCUPATION_MAP = {
    "2511": "System analysts and ICT-architects",
    "2512": "Software- and system developers",
    "2513": "Games and digital media developers",
    "2514": "System testers and test managers",
    "2515": "System administrators",
    "2516": "Security specialists (ICT)",
    "2519": "ICT-specialist professionals not elsewhere classified",
    "2121": "Mathematicians and actuaries",
    "2122": "Statisticians",
    "2173": "Game and digital media designers",
    "2143": "Engineering professionals in electrical, electronics and telecommunications",
}


class SCBIngestion:
    """Handles data ingestion from Statistics Sweden (SCB) API.
    
    Uses the JSON-stat2 format for efficient data transfer and implements
    rate limiting to comply with SCB's API limits.
    """
    
    # Correct endpoint for regional salary by occupation
    BASE_URL = "https://api.scb.se/OV0104/v1/doris/en/ssd"
    INCOME_ENDPOINT = "/AM/AM0110/AM0110A/LonYrkeRegion4AN"
    
    # Rate limiting: 3 requests per second (safe margin under 30/10 limit)
    MIN_REQUEST_INTERVAL = 0.35  # seconds between requests
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize SCB ingestion client.
        
        Args:
            api_key: Optional API key for SCB (not required for public data)
        """
        self.api_key = api_key
        self._last_request_time = 0.0
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        self.client = httpx.Client(
            headers=headers,
            timeout=60.0,  # SCB can be slow
        )
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.MIN_REQUEST_INTERVAL:
            time.sleep(self.MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.time()
    
    def get_table_metadata(self) -> Dict:
        """Fetch metadata for the income table to get available values.
        
        Returns:
            Dictionary with table metadata including available codes
        """
        self._rate_limit()
        url = f"{self.BASE_URL}{self.INCOME_ENDPOINT}"
        
        logger.info(f"Fetching table metadata from {url}")
        response = self.client.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def fetch_income_data(
        self, 
        occupation_codes: Optional[List[str]] = None,
        region_codes: Optional[List[str]] = None,
        years: Optional[List[str]] = None,
        genders: Optional[List[str]] = None,
        sectors: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Fetch income data by occupation and geography.
        
        Args:
            occupation_codes: List of SSYK 2012 occupation codes (4-digit)
            region_codes: List of NUTS region codes (e.g., SE11 for Stockholm)
            years: List of years as strings
            genders: List of gender codes ("1"=men, "2"=women, "1+2"=total)
            sectors: List of sector codes ("0"=all, "4-5"=private)
            
        Returns:
            DataFrame with income data in tidy/long format
        """
        # Default values
        if occupation_codes is None:
            occupation_codes = DEFAULT_SSYK_CODES  # All ICT and data science occupations
        if region_codes is None:
            region_codes = ALL_REGION_CODES
        if years is None:
            years = ["2023", "2024"]  # Available years in this SCB table
        if genders is None:
            genders = ["1", "2"]  # men, women
        if sectors is None:
            sectors = ["0"]  # All sectors
        
        logger.info(
            f"Fetching income data: occupations={occupation_codes}, "
            f"regions={len(region_codes)}, years={years}"
        )
        
        # Build query using SCB's exact field names for this table
        query = {
            "query": [
                {
                    "code": "Region",
                    "selection": {
                        "filter": "item",
                        "values": region_codes
                    }
                },
                {
                    "code": "Sektor",  # Sector is required for this table
                    "selection": {
                        "filter": "item",
                        "values": sectors
                    }
                },
                {
                    "code": "Yrke2012",  # SSYK 2012 occupation codes
                    "selection": {
                        "filter": "item",
                        "values": occupation_codes
                    }
                },
                {
                    "code": "Kon",  # Gender/sex
                    "selection": {
                        "filter": "item",
                        "values": genders
                    }
                },
                {
                    "code": "ContentsCode",
                    "selection": {
                        "filter": "item",
                        # Monthly salary and number of employees
                        "values": ["000007AS", "000007AP"]
                    }
                },
                {
                    "code": "Tid",  # Time/Year
                    "selection": {
                        "filter": "item",
                        "values": years
                    }
                }
            ],
            "response": {
                "format": "json-stat2"  # Use efficient json-stat2 format
            }
        }
        
        self._rate_limit()
        url = f"{self.BASE_URL}{self.INCOME_ENDPOINT}"
        
        try:
            logger.info(f"Posting query to {url}")
            response = self.client.post(url, json=query)
            response.raise_for_status()
            
            # Parse JSON-stat2 response
            data = response.json()
            df = self._parse_jsonstat2(data)
            
            # Add human-readable labels
            df = self._add_labels(df)
            
            # Add surrogate key for idempotent upserts
            df["surrogate_key"] = df.apply(
                lambda row: self._generate_surrogate_key(row), axis=1
            )
            
            logger.info(f"Successfully fetched {len(df)} records from SCB")
            return df
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching data from SCB: {e}")
            logger.error(f"Response: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error fetching data from SCB: {e}")
            raise
    
    def _parse_jsonstat2(self, data: Dict) -> pd.DataFrame:
        """Parse JSON-stat2 response into a tidy DataFrame.
        
        Args:
            data: JSON-stat2 formatted response
            
        Returns:
            Tidy DataFrame with one row per observation
        """
        # Use pyjstat to parse JSON-stat2
        try:
            # pyjstat.from_json_stat returns a list of DataFrames
            datasets = pyjstat.from_json_stat(data)
            if datasets:
                df = datasets[0]
                
                # Handle missing/suppressed data (SCB uses ".." or ".")
                if "value" in df.columns:
                    df["value"] = pd.to_numeric(df["value"], errors="coerce")
                
                return df
        except Exception as e:
            logger.warning(f"pyjstat parsing failed: {e}, trying manual parse")
        
        # Fallback: manual parsing
        return self._manual_parse_jsonstat2(data)
    
    def _manual_parse_jsonstat2(self, data: Dict) -> pd.DataFrame:
        """Manual parsing fallback for JSON-stat2."""
        records = []
        
        # Get dimensions
        dimensions = data.get("dimension", {})
        dim_ids = data.get("id", [])
        dim_sizes = data.get("size", [])
        values = data.get("value", [])
        
        # Build index mappings for each dimension
        dim_values = {}
        for dim_id in dim_ids:
            dim_info = dimensions.get(dim_id, {})
            category = dim_info.get("category", {})
            index = category.get("index", {})
            label = category.get("label", {})
            
            # Create ordered list of values
            if isinstance(index, dict):
                dim_values[dim_id] = sorted(index.keys(), key=lambda k: index[k])
            else:
                dim_values[dim_id] = list(label.keys()) if label else []
        
        # Iterate through all combinations
        from itertools import product
        
        all_combinations = list(product(*[dim_values[d] for d in dim_ids]))
        
        for i, combo in enumerate(all_combinations):
            if i < len(values):
                record = dict(zip(dim_ids, combo))
                record["value"] = values[i]
                records.append(record)
        
        df = pd.DataFrame(records)
        
        # Convert value to numeric, handling missing data
        if "value" in df.columns:
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
        
        return df
    
    def _add_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add human-readable labels to the DataFrame.
        
        Args:
            df: DataFrame with codes
            
        Returns:
            DataFrame with added label columns
        """
        # Map NUTS region codes to names
        region_col = None
        for col in ["Region", "region"]:
            if col in df.columns:
                region_col = col
                break
        
        if region_col:
            df["region_name"] = df[region_col].map(NUTS_REGION_CODES)
        
        # Map sector codes
        sector_col = None
        for col in ["Sektor", "sector"]:
            if col in df.columns:
                sector_col = col
                break
        
        if sector_col:
            df["sector_name"] = df[sector_col].map(SECTOR_CODES)
        
        # Map gender codes
        gender_col = None
        for col in ["Kon", "sex", "gender", "kön"]:
            if col in df.columns:
                gender_col = col
                break
        
        if gender_col:
            df["gender"] = df[gender_col].map(GENDER_CODES)
        
        # Map contents codes
        contents_col = None
        for col in ["ContentsCode", "contents"]:
            if col in df.columns:
                contents_col = col
                break
        
        if contents_col:
            df["measure"] = df[contents_col].map(CONTENTS_CODES)
        
        return df
    
    def _generate_surrogate_key(self, row: pd.Series) -> str:
        """Generate a surrogate key for idempotent upserts.
        
        Args:
            row: DataFrame row
            
        Returns:
            Hash string as surrogate key
        """
        # Create key from relevant columns
        key_parts = []
        for col in ["Tid", "Region", "Yrke2012", "Kon", "ContentsCode", 
                    "year", "region", "occupation", "sex", "contents"]:
            if col in row.index:
                key_parts.append(str(row[col]))
        
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()[:16]
    
    def save_to_parquet(self, df: pd.DataFrame, filepath: Path) -> Path:
        """Save DataFrame to Parquet file locally.
        
        Args:
            df: DataFrame to save
            filepath: Path to save file
            
        Returns:
            Path to saved file
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_parquet(filepath, index=False, engine="pyarrow")
        logger.info(f"Saved {len(df)} records to {filepath}")
        
        return filepath
    
    def save_to_gcs(self, df: pd.DataFrame, bucket_name: str, blob_name: str):
        """Save DataFrame to Google Cloud Storage.
        
        Args:
            df: DataFrame to save
            bucket_name: GCS bucket name
            blob_name: Blob name/path in bucket
        """
        from google.cloud import storage
        import tempfile
        import os
        
        logger.info(f"Saving data to GCS: gs://{bucket_name}/{blob_name}")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            temp_file = f.name
        
        try:
            df.to_parquet(temp_file, index=False, engine="pyarrow")
            
            # Upload to GCS
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(temp_file)
            
            logger.info(f"Successfully saved to GCS")
        finally:
            os.unlink(temp_file)
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
