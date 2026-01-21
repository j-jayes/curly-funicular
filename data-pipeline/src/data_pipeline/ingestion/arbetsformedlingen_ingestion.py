"""Arbetsförmedlingen (Swedish Public Employment Service) API ingestion.

This module fetches job advertisements from:
1. Historical Ads API - archived ads (2016+) for time series analysis
2. Taxonomy API - reference data for SSYK codes and regions

No API key required for these endpoints.
"""

import httpx
import pandas as pd
from typing import Dict, List, Optional, Generator
from datetime import datetime, timedelta
from pathlib import Path
import time
import logging

logger = logging.getLogger(__name__)

# SSYK concept ID mapping (from Taxonomy API)
# These map SSYK codes to concept IDs used in the Historical API
SSYK_CONCEPT_IDS = {
    "2511": "DJh5_yyF_hEM",  # Systems analysts and IT architects
    "2512": "UxT1_dNS_dLU",  # Software and systems developers
    "2513": "dF8v_MFC_5dh",  # Games and digital media developers
    "2514": "RfCH_4qV_XCB",  # System testers and test managers
    "2515": "2fM5_zYK_7x5",  # System administrators
    "2516": "Vhdd_K7y_xAC",  # Security specialists (ICT)
    "2519": "oZE4_Ga3_2Aa",  # ICT-specialist professionals nec
    "2121": "Z5BP_7yS_wD1",  # Mathematicians and actuaries
    "2122": "MYGj_8Ht_NrT",  # Statisticians
    "2173": "Ck5M_Jw9_MpV",  # Game and digital media designers
    "2143": "Pb7Y_Mxa_C4q",  # Engineering professionals in electrical, electronics and telecom
}

# Default SSYK codes for job ads search
DEFAULT_SSYK_CODES = [
    "2511", "2512", "2513", "2514", "2515", "2516", "2519",  # ICT
    "2121", "2122",  # Data Science related
    "2173", "2143",  # Design and Electronics
]


class TaxonomyClient:
    """Client for Arbetsförmedlingen Taxonomy API.
    
    Provides reference data for occupations, regions, and skills.
    No API key required.
    """
    
    BASE_URL = "https://taxonomy.api.jobtechdev.se/v1/taxonomy"
    
    def __init__(self):
        self.client = httpx.Client(
            headers={
                "Accept": "application/json",
                "User-Agent": "SwedishLaborMarketAnalytics/1.0",
            },
            timeout=30.0,
        )
    
    def get_ssyk_codes(self) -> pd.DataFrame:
        """Fetch all SSYK occupation codes.
        
        Returns:
            DataFrame with SSYK codes and labels
        """
        url = f"{self.BASE_URL}/specific/concepts/ssyk"
        params = {
            "type": "ssyk-level-1 ssyk-level-2 ssyk-level-3 ssyk-level-4"
        }
        
        response = self.client.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        records = []
        for item in data:
            records.append({
                "concept_id": item.get("id"),
                "ssyk_code": item.get("ssyk-code-2012", item.get("preferred-label", "")),
                "label": item.get("preferred-label"),
                "type": item.get("type"),
            })
        
        return pd.DataFrame(records)
    
    def get_regions(self) -> pd.DataFrame:
        """Fetch Swedish regions.
        
        Returns:
            DataFrame with region codes and names
        """
        # Use GraphQL to get regions
        url = f"{self.BASE_URL}/graphql"
        
        query = """
        {
            concepts(type: "region") {
                id
                preferred_label
                broader {
                    id
                    preferred_label
                }
            }
        }
        """
        
        response = self.client.post(url, json={"query": query})
        
        if response.status_code != 200:
            logger.warning("GraphQL failed, using fallback region list")
            return self._fallback_regions()
        
        data = response.json()
        concepts = data.get("data", {}).get("concepts", [])
        
        records = []
        for item in concepts:
            records.append({
                "concept_id": item.get("id"),
                "name": item.get("preferred_label"),
            })
        
        return pd.DataFrame(records)
    
    def _fallback_regions(self) -> pd.DataFrame:
        """Fallback region list if API fails."""
        return pd.DataFrame([
            {"concept_id": "CifL_Rzy_Mku", "name": "Stockholm"},
            {"concept_id": "9hXe_F4g_eTG", "name": "Västra Götaland"},
            {"concept_id": "EVpN_aAi_R6p", "name": "Skåne"},
        ])
    
    def close(self):
        self.client.close()


class EnrichmentsClient:
    """Client for Arbetsförmedlingen JobAd Enrichments API.
    
    Extracts skills, traits, and competencies from job description text.
    No API key required, but contact JobTech before production use.
    """
    
    BASE_URL = "https://jobad-enrichments-api.jobtechdev.se"
    
    # Rate limiting
    MIN_REQUEST_INTERVAL = 0.5  # seconds between requests
    BATCH_SIZE = 10  # Process 10 documents at a time
    
    def __init__(self):
        self._last_request_time = 0.0
        self.client = httpx.Client(
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "SwedishLaborMarketAnalytics/1.0",
            },
            timeout=60.0,
        )
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.MIN_REQUEST_INTERVAL:
            time.sleep(self.MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.time()
    
    def enrich_documents(
        self,
        documents: List[Dict[str, str]],
        threshold: float = 0.5,
    ) -> List[Dict]:
        """Enrich job ad texts with skills and competencies.
        
        Args:
            documents: List of dicts with 'id' and 'text' keys
            threshold: Minimum probability threshold for skills (0-1)
            
        Returns:
            List of enriched documents with extracted skills
        """
        self._rate_limit()
        
        url = f"{self.BASE_URL}/enrichtextdocumentsbinary"
        
        payload = {
            "documents_input": documents,
            "include_terms_info": True,
            "include_sentences": False,
            "classification_threshold": threshold,
        }
        
        try:
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.warning(f"Enrichment API error: {e}")
            return []
    
    def enrich_batch(
        self,
        ads_df: pd.DataFrame,
        text_column: str = "description_text",
        id_column: str = "id",
        threshold: float = 0.5,
    ) -> pd.DataFrame:
        """Enrich a batch of job ads with skills data.
        
        Args:
            ads_df: DataFrame with job ads
            text_column: Column containing description text
            id_column: Column containing ad ID
            threshold: Minimum probability for skill extraction
            
        Returns:
            DataFrame with ad_id, skill, skill_type, and probability
        """
        if ads_df.empty:
            return pd.DataFrame(columns=["ad_id", "skill", "skill_type", "probability"])
        
        all_skills = []
        
        # Process in batches
        for i in range(0, len(ads_df), self.BATCH_SIZE):
            batch = ads_df.iloc[i:i + self.BATCH_SIZE]
            
            # Prepare documents for API
            documents = []
            for _, row in batch.iterrows():
                text = row.get(text_column, "")
                if text and isinstance(text, str) and len(text.strip()) > 50:
                    documents.append({
                        "id": str(row[id_column]),
                        "text": text[:10000],  # Limit text length
                    })
            
            if not documents:
                continue
            
            logger.info(f"Enriching batch {i // self.BATCH_SIZE + 1}, {len(documents)} documents")
            
            # Call API
            results = self.enrich_documents(documents, threshold)
            
            # Parse results
            for doc_result in results:
                ad_id = doc_result.get("id")
                enrichments = doc_result.get("enriched_candidates", {})
                
                # Extract skills
                for skill in enrichments.get("competencies", []):
                    all_skills.append({
                        "ad_id": ad_id,
                        "skill": skill.get("term", ""),
                        "skill_type": "competency",
                        "probability": skill.get("prediction", 0),
                    })
                
                # Extract traits (soft skills)
                for trait in enrichments.get("traits", []):
                    all_skills.append({
                        "ad_id": ad_id,
                        "skill": trait.get("term", ""),
                        "skill_type": "trait",
                        "probability": trait.get("prediction", 0),
                    })
                
                # Extract occupation titles
                for occupation in enrichments.get("occupations", []):
                    all_skills.append({
                        "ad_id": ad_id,
                        "skill": occupation.get("term", ""),
                        "skill_type": "occupation",
                        "probability": occupation.get("prediction", 0),
                    })
        
        return pd.DataFrame(all_skills)
    
    def close(self):
        self.client.close()


class HistoricalAdsClient:
    """Client for Arbetsförmedlingen Historical Ads API.
    
    Fetches archived job advertisements for time series analysis.
    Data available from 2016 onwards.
    No API key required.
    """
    
    BASE_URL = "https://historical.api.jobtechdev.se"
    
    # Rate limiting
    MIN_REQUEST_INTERVAL = 0.5  # seconds between requests
    
    def __init__(self):
        self._last_request_time = 0.0
        self.client = httpx.Client(
            headers={
                "Accept": "application/json",
                "User-Agent": "SwedishLaborMarketAnalytics/1.0",
            },
            timeout=300.0,  # Historical API can be slow
        )
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.MIN_REQUEST_INTERVAL:
            time.sleep(self.MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.time()
    
    def search(
        self,
        ssyk_code: Optional[str] = None,
        published_after: Optional[str] = None,
        published_before: Optional[str] = None,
        region: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> Dict:
        """Search historical job ads.
        
        Args:
            ssyk_code: SSYK occupation code (e.g., "2512")
            published_after: ISO timestamp for start date
            published_before: ISO timestamp for end date
            region: Region name or code
            offset: Pagination offset
            limit: Results per page (max 100)
            
        Returns:
            API response as dictionary
        """
        self._rate_limit()
        
        params = {
            "offset": offset,
            "limit": min(limit, 100),
        }
        
        if ssyk_code:
            params["occupation-group"] = ssyk_code
        if published_after:
            params["published-after"] = published_after
        if published_before:
            params["published-before"] = published_before
        if region:
            params["region"] = region
        
        url = f"{self.BASE_URL}/search"
        
        logger.debug(f"Requesting: {url} with params: {params}")
        response = self.client.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def fetch_ads_for_period(
        self,
        ssyk_code: str,
        start_date: str,
        end_date: str,
        max_results: int = 10000,
    ) -> Generator[Dict, None, None]:
        """Fetch all ads for a period with pagination.
        
        Args:
            ssyk_code: SSYK occupation code (e.g., "2512")
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            max_results: Maximum results to fetch
            
        Yields:
            Individual job ad dictionaries
        """
        offset = 0
        limit = 100
        total_fetched = 0
        
        while total_fetched < max_results:
            logger.info(f"Fetching ads offset={offset}, total={total_fetched}")
            
            result = self.search(
                ssyk_code=ssyk_code,
                published_after=start_date,
                published_before=end_date,
                offset=offset,
                limit=limit,
            )
            
            hits = result.get("hits", [])
            
            if not hits:
                break
            
            for hit in hits:
                yield hit
                total_fetched += 1
                
                if total_fetched >= max_results:
                    return
            
            offset += len(hits)
            
            # Check if we've reached the end
            total_available = result.get("total", {}).get("value", 0)
            if offset >= total_available:
                break
    
    def close(self):
        self.client.close()


class ArbetsformedlingenIngestion:
    """Handles data ingestion from Arbetsförmedlingen APIs.
    
    Combines Historical Ads API, Taxonomy API, and Enrichments API for comprehensive
    job market data collection including skills extraction.
    """
    
    def __init__(self, enable_enrichments: bool = False):
        """Initialize ingestion clients.
        
        Args:
            enable_enrichments: Whether to enable skills extraction via Enrichments API
        """
        self.historical_client = HistoricalAdsClient()
        self.taxonomy_client = TaxonomyClient()
        self.enrichments_client = EnrichmentsClient() if enable_enrichments else None
    
    def fetch_historical_ads(
        self,
        ssyk_codes: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_results_per_occupation: int = 5000,
    ) -> pd.DataFrame:
        """Fetch historical job ads for specified occupations.
        
        Args:
            ssyk_codes: List of SSYK codes to fetch (default: 2511, 2512)
            start_date: Start date ISO format (default: 1 year ago)
            end_date: End date ISO format (default: today)
            max_results_per_occupation: Max ads per occupation
            
        Returns:
            DataFrame with job advertisements
        """
        if ssyk_codes is None:
            ssyk_codes = DEFAULT_SSYK_CODES  # All ICT and data science occupations
        
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%dT00:00:00")
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%dT00:00:00")
        
        logger.info(f"Fetching ads for SSYK codes: {ssyk_codes} from {start_date} to {end_date}")
        
        all_records = []
        
        for ssyk_code in ssyk_codes:
            logger.info(f"Fetching ads for SSYK {ssyk_code}")
            
            for ad in self.historical_client.fetch_ads_for_period(
                ssyk_code=ssyk_code,
                start_date=start_date,
                end_date=end_date,
                max_results=max_results_per_occupation,
            ):
                record = self._transform_ad(ad, ssyk_code)
                all_records.append(record)
        
        df = pd.DataFrame(all_records)
        logger.info(f"Fetched {len(df)} total job ads")
        
        return df
    
    def _transform_ad(self, ad: Dict, ssyk_code: str) -> Dict:
        """Transform a job ad to a flat record.
        
        Args:
            ad: Raw job ad from API
            ssyk_code: SSYK code for this ad
            
        Returns:
            Flat dictionary for DataFrame
        """
        workplace = ad.get("workplace_address", {}) or {}
        employer = ad.get("employer", {}) or {}
        occupation = ad.get("occupation", {}) or {}
        description = ad.get("description", {}) or {}
        
        return {
            "id": ad.get("id"),
            "headline": ad.get("headline"),
            "ssyk_code": ssyk_code,
            "occupation_label": occupation.get("label"),
            "occupation_concept_id": occupation.get("concept_id"),
            "employer_name": employer.get("name"),
            "employer_org_number": employer.get("organization_number"),
            "region": workplace.get("region"),
            "region_code": workplace.get("region_code"),
            "municipality": workplace.get("municipality"),
            "municipality_code": workplace.get("municipality_code"),
            "latitude": workplace.get("coordinates", [None, None])[1] if workplace.get("coordinates") else None,
            "longitude": workplace.get("coordinates", [None, None])[0] if workplace.get("coordinates") else None,
            "published_date": ad.get("publication_date"),
            "last_application_date": ad.get("application_deadline"),
            "number_of_vacancies": ad.get("number_of_vacancies", 1),
            "employment_type": ad.get("employment_type", {}).get("label") if ad.get("employment_type") else None,
            "duration": ad.get("duration", {}).get("label") if ad.get("duration") else None,
            "working_hours_type": ad.get("working_hours_type", {}).get("label") if ad.get("working_hours_type") else None,
            "remote_work": ad.get("remote_work"),
            "description_text": description.get("text", ""),
            "description_length": len(description.get("text", "") or ""),
        }
    
    def fetch_taxonomy_data(self) -> Dict[str, pd.DataFrame]:
        """Fetch reference data from Taxonomy API.
        
        Returns:
            Dictionary with 'ssyk' and 'regions' DataFrames
        """
        logger.info("Fetching taxonomy data")
        
        return {
            "ssyk": self.taxonomy_client.get_ssyk_codes(),
            "regions": self.taxonomy_client.get_regions(),
        }
    
    def aggregate_ads_by_period(
        self,
        df: pd.DataFrame,
        period: str = "M"  # M=month, Q=quarter, Y=year
    ) -> pd.DataFrame:
        """Aggregate job ads by time period.
        
        Args:
            df: DataFrame with job ads
            period: Aggregation period (M, Q, Y)
            
        Returns:
            Aggregated DataFrame
        """
        if df.empty:
            return df
        
        # Convert to datetime
        df = df.copy()
        df["published_date"] = pd.to_datetime(df["published_date"])
        df["period"] = df["published_date"].dt.to_period(period)
        
        # Aggregate
        agg = df.groupby(["period", "ssyk_code", "region"]).agg({
            "id": "count",
            "number_of_vacancies": "sum",
            "description_length": "mean",
        }).reset_index()
        
        agg.columns = ["period", "ssyk_code", "region", "ad_count", "total_vacancies", "avg_description_length"]
        agg["period"] = agg["period"].astype(str)
        
        return agg
    
    def save_to_parquet(self, df: pd.DataFrame, filepath: Path) -> Path:
        """Save DataFrame to Parquet file.
        
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
        
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            temp_file = f.name
        
        try:
            df.to_parquet(temp_file, index=False, engine="pyarrow")
            
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(temp_file)
            
            logger.info(f"Successfully saved to GCS")
        finally:
            os.unlink(temp_file)
    
    def close(self):
        """Close all clients."""
        self.historical_client.close()
        self.taxonomy_client.close()
        if self.enrichments_client:
            self.enrichments_client.close()
    
    def enrich_ads_with_skills(
        self,
        ads_df: pd.DataFrame,
        threshold: float = 0.5,
    ) -> pd.DataFrame:
        """Enrich job ads DataFrame with skills extracted from descriptions.
        
        Args:
            ads_df: DataFrame with job ads (must have 'id' and 'description_text' columns)
            threshold: Minimum probability threshold for skill extraction (0-1)
            
        Returns:
            DataFrame with columns: ad_id, skill, skill_type, probability
        """
        if self.enrichments_client is None:
            logger.warning("Enrichments client not enabled. Initialize with enable_enrichments=True")
            return pd.DataFrame(columns=["ad_id", "skill", "skill_type", "probability"])
        
        if "description_text" not in ads_df.columns:
            logger.warning("No description_text column found in DataFrame")
            return pd.DataFrame(columns=["ad_id", "skill", "skill_type", "probability"])
        
        logger.info(f"Enriching {len(ads_df)} job ads with skills data")
        return self.enrichments_client.enrich_batch(
            ads_df,
            text_column="description_text",
            id_column="id",
            threshold=threshold,
        )
    
    def aggregate_skills(
        self,
        skills_df: pd.DataFrame,
        ads_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Aggregate skills by occupation and skill type.
        
        Args:
            skills_df: DataFrame from enrich_ads_with_skills()
            ads_df: Original ads DataFrame with ssyk_code
            
        Returns:
            DataFrame with skill counts by occupation
        """
        if skills_df.empty or ads_df.empty:
            return pd.DataFrame()
        
        # Join skills with ad occupation info
        merged = skills_df.merge(
            ads_df[["id", "ssyk_code", "occupation_label"]],
            left_on="ad_id",
            right_on="id",
            how="left",
        )
        
        # Aggregate skill counts
        agg = merged.groupby(["ssyk_code", "occupation_label", "skill", "skill_type"]).agg({
            "ad_id": "count",
            "probability": "mean",
        }).reset_index()
        
        agg.columns = ["ssyk_code", "occupation_label", "skill", "skill_type", "occurrence_count", "avg_probability"]
        agg = agg.sort_values(["ssyk_code", "occurrence_count"], ascending=[True, False])
        
        return agg
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
