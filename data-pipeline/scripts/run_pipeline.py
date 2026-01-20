"""Main pipeline execution script.

Runs the complete data pipeline:
1. Fetch income data from SCB (Statistics Sweden)
2. Fetch historical job ads from Arbetsförmedlingen
3. Process and transform data
4. Save to local Parquet files (and optionally GCS)

Usage:
    python scripts/run_pipeline.py [--local-only] [--years 2022 2023 2024]
"""

import logging
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_pipeline.ingestion.scb_ingestion import SCBIngestion
from data_pipeline.ingestion.arbetsformedlingen_ingestion import ArbetsformedlingenIngestion
from data_pipeline.processing.data_processor import DataProcessor
from data_pipeline.utils.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Default SSYK codes to fetch
DEFAULT_SSYK_CODES = ["2511", "2512"]  # Systems analysts, Software developers


def run_pipeline(
    local_only: bool = True,
    years: list = None,
    ssyk_codes: list = None,
    max_job_ads: int = 2000,
):
    """Run the complete data pipeline.
    
    Args:
        local_only: If True, save only locally. If False, also upload to GCS.
        years: List of years to fetch (default: 2022-2024)
        ssyk_codes: List of SSYK codes (default: 2511, 2512)
        max_job_ads: Maximum job ads per occupation to fetch
    """
    logger.info("="*60)
    logger.info("Starting Swedish Labor Market Data Pipeline")
    logger.info("="*60)
    
    # Load settings
    settings = get_settings()
    
    # Set defaults
    if years is None:
        years = ["2022", "2023", "2024"]
    if ssyk_codes is None:
        ssyk_codes = DEFAULT_SSYK_CODES
    
    logger.info(f"Configuration:")
    logger.info(f"  SSYK codes: {ssyk_codes}")
    logger.info(f"  Years: {years}")
    logger.info(f"  Max job ads per occupation: {max_job_ads}")
    logger.info(f"  Local only: {local_only}")
    
    try:
        # Initialize processor
        processor = DataProcessor()
        
        # ===== STEP 1: Fetch income data from SCB =====
        logger.info("\n" + "="*40)
        logger.info("STEP 1: Fetching income data from SCB")
        logger.info("="*40)
        
        with SCBIngestion(api_key=settings.scb_api_key) as scb_client:
            income_raw = scb_client.fetch_income_data(
                occupation_codes=ssyk_codes,
                years=years,
            )
            
            # Save raw data
            scb_client.save_to_parquet(
                income_raw,
                processor.raw_dir / "scb_income_raw.parquet"
            )
        
        logger.info(f"Fetched {len(income_raw)} income records from SCB")
        
        # ===== STEP 2: Fetch job ads from Arbetsförmedlingen =====
        logger.info("\n" + "="*40)
        logger.info("STEP 2: Fetching job ads from Arbetsförmedlingen")
        logger.info("="*40)
        
        with ArbetsformedlingenIngestion() as af_client:
            jobs_raw = af_client.fetch_historical_ads(
                ssyk_codes=ssyk_codes,
                max_results_per_occupation=max_job_ads,
            )
            
            # Save raw data
            af_client.save_to_parquet(
                jobs_raw,
                processor.raw_dir / "af_jobs_raw.parquet"
            )
        
        logger.info(f"Fetched {len(jobs_raw)} job ads from Arbetsförmedlingen")
        
        # ===== STEP 3: Process data =====
        logger.info("\n" + "="*40)
        logger.info("STEP 3: Processing data")
        logger.info("="*40)
        
        # Process income data
        income_processed = processor.process_income_data(income_raw)
        logger.info(f"Processed income data: {len(income_processed)} records")
        
        # Process job ads
        jobs_processed = processor.process_jobs_data(jobs_raw)
        logger.info(f"Processed jobs data: {len(jobs_processed)} records")
        
        # Aggregate jobs by region and year
        jobs_aggregated = processor.aggregate_jobs_by_region(jobs_processed, period="year")
        logger.info(f"Aggregated jobs data: {len(jobs_aggregated)} records")
        
        # ===== STEP 4: Save processed data =====
        logger.info("\n" + "="*40)
        logger.info("STEP 4: Saving processed data")
        logger.info("="*40)
        
        paths = processor.save_processed_data(
            income_df=income_processed,
            jobs_df=jobs_processed,
            jobs_agg_df=jobs_aggregated,
        )
        
        for name, path in paths.items():
            logger.info(f"  Saved {name}: {path}")
        
        # Create summary stats
        stats = processor.create_summary_stats(income_processed, jobs_processed)
        logger.info(f"\nSummary Statistics:")
        logger.info(f"  Income records: {stats['income'].get('record_count', 0)}")
        logger.info(f"  Job ads: {stats['jobs'].get('total_ads', 0)}")
        logger.info(f"  Total vacancies: {stats['jobs'].get('total_vacancies', 0)}")
        
        # ===== STEP 5: Upload to GCS (optional) =====
        if not local_only and settings.gcs_bucket_name:
            logger.info("\n" + "="*40)
            logger.info("STEP 5: Uploading to GCS")
            logger.info("="*40)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            with SCBIngestion() as scb_client:
                for name, path in paths.items():
                    df = pd.read_parquet(path)
                    blob_name = f"processed/{name}_{timestamp}.parquet"
                    scb_client.save_to_gcs(df, settings.gcs_bucket_name, blob_name)
                    logger.info(f"  Uploaded {name} to gs://{settings.gcs_bucket_name}/{blob_name}")
        
        logger.info("\n" + "="*60)
        logger.info("Pipeline completed successfully!")
        logger.info("="*60)
        
        return paths
        
    except Exception as e:
        logger.error(f"\nPipeline failed: {e}", exc_info=True)
        raise


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Swedish Labor Market Data Pipeline"
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        default=True,
        help="Save data locally only (don't upload to GCS)"
    )
    parser.add_argument(
        "--upload-gcs",
        action="store_true",
        help="Upload processed data to GCS"
    )
    parser.add_argument(
        "--years",
        nargs="+",
        default=["2023", "2024"],  # Only these years available in SCB table
        help="Years to fetch data for"
    )
    parser.add_argument(
        "--ssyk-codes",
        nargs="+",
        default=DEFAULT_SSYK_CODES,
        help="SSYK occupation codes to fetch"
    )
    parser.add_argument(
        "--max-ads",
        type=int,
        default=2000,
        help="Maximum job ads per occupation"
    )
    
    args = parser.parse_args()
    
    run_pipeline(
        local_only=not args.upload_gcs,
        years=args.years,
        ssyk_codes=args.ssyk_codes,
        max_job_ads=args.max_ads,
    )


if __name__ == "__main__":
    main()
