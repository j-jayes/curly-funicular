"""Main pipeline execution script.

Runs the complete data pipeline:
1. Fetch income data from SCB (Statistics Sweden)
2. Fetch taxonomy data
3. Fetch historical job ads from Arbetsförmedlingen
4. Process and transform data
5. Save to local Parquet files (and optionally GCS)

Usage:
    python scripts/run_pipeline.py --steps scb taxonomy jobs process
"""

import logging
import sys
import argparse
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_pipeline.ingestion.scb_ingestion import SCBIngestion, DEFAULT_SSYK_CODES
from data_pipeline.ingestion.arbetsformedlingen_ingestion import ArbetsformedlingenIngestion
from data_pipeline.ingestion.taxonomy_ingestion import TaxonomyIngestion
from data_pipeline.ingestion.esco_ingestion import EscoIngestion
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


def run_pipeline(
    steps: list,
    local_only: bool = True,
    years: list = None,
    ssyk_codes: list = None,
    max_job_ads: int = 2000,
):
    """Run the complete data pipeline.
    
    Args:
        steps: List of steps to run ['scb', 'taxonomy', 'jobs', 'process']
        local_only: If True, save only locally. If False, also upload to GCS.
        years: List of years to fetch (default: 2014-2025)
        ssyk_codes: List of SSYK codes (default: All)
        max_job_ads: Maximum job ads per occupation to fetch
    """
    logger.info("="*60)
    logger.info("Starting Swedish Labor Market Data Pipeline")
    logger.info(f"Steps to run: {steps}")
    logger.info("="*60)
    
    # Load settings
    settings = get_settings()
    processor = DataProcessor()
    
    # Initialize data containers
    income_raw = None
    dispersion_raw = None
    age_raw = None
    education_raw = None
    jobs_raw = None
    skills_processed = None
    taxonomy_path = None
    
    try:
        # ===== STEP 1: Fetch income data from SCB =====
        if 'scb' in steps:
            logger.info("\n" + "="*40)
            logger.info("STEP 1: Fetching income data from SCB")
            logger.info("="*40)
            
            with SCBIngestion(api_key=settings.scb_api_key) as scb_client:
                # 1. Regional Income
                logger.info("Fetching regional income data...")
                income_raw = scb_client.fetch_income_data(
                    occupation_codes=ssyk_codes,
                    years=years,
                )
                scb_client.save_to_parquet(
                    income_raw,
                    processor.raw_dir / "scb_income_raw.parquet"
                )
                
                # 2. Salary Dispersion
                logger.info("Fetching salary dispersion data (percentiles)...")
                try:
                    dispersion_raw = scb_client.fetch_salary_dispersion(
                        occupation_codes=ssyk_codes,
                        years=years,
                    )
                    scb_client.save_to_parquet(
                        dispersion_raw,
                        processor.raw_dir / "scb_dispersion_raw.parquet"
                    )
                    logger.info(f"Fetched {len(dispersion_raw)} dispersion records")
                except Exception as e:
                    logger.warning(f"Could not fetch dispersion data: {e}")
                    
                # 3. Income by Age
                logger.info("Fetching income by age data...")
                try:
                    age_raw = scb_client.fetch_income_by_age(
                        occupation_codes=ssyk_codes,
                        years=years,
                    )
                    scb_client.save_to_parquet(
                        age_raw,
                        processor.raw_dir / "scb_age_raw.parquet"
                    )
                    logger.info(f"Fetched {len(age_raw)} age records")
                except Exception as e:
                    logger.warning(f"Could not fetch age data: {e}")

                # 4. Income by Education
                logger.info("Fetching income by education data...")
                try:
                    education_raw = scb_client.fetch_income_by_education(
                        occupation_codes=ssyk_codes,
                        years=years,
                    )
                    scb_client.save_to_parquet(
                        education_raw,
                        processor.raw_dir / "scb_education_raw.parquet"
                    )
                    logger.info(f"Fetched {len(education_raw)} education records")
                except Exception as e:
                    logger.warning(f"Could not fetch education data: {e}")
            
            logger.info(f"Fetched {len(income_raw)} income records from SCB")
        
        # ===== STEP 2: Fetch Taxonomy Data =====
        if 'taxonomy' in steps:
            logger.info("\n" + "="*40)
            logger.info("STEP 2: Fetching Taxonomy Data")
            logger.info("="*40)
            
            try:
                taxonomy_client = TaxonomyIngestion(raw_dir=processor.raw_dir)
                taxonomy_client.fetch_files()
                taxonomy_processed = taxonomy_client.process_taxonomy()
                
                # Enrichen with ESCO if requested or by default if taxonomy is run
                logger.info("Enriching taxonomy with ESCO skills...")
                esco_client = EscoIngestion(raw_dir=processor.raw_dir)
                esco_client.fetch_scb_mapping()
                taxonomy_processed = esco_client.process_esco_mapping(taxonomy_processed)
                
                if not taxonomy_processed.empty:
                    taxonomy_path = taxonomy_client.save_processed(
                        taxonomy_processed, 
                        processor.processed_dir
                    )
            except Exception as e:
                logger.warning(f"Taxonomy step failed: {e}")

        # ===== STEP 3: Fetch job ads from Arbetsförmedlingen =====
        if 'jobs' in steps:
            logger.info("\n" + "="*40)
            logger.info("STEP 3: Fetching job ads from Arbetsförmedlingen")
            logger.info("="*40)
            
            with ArbetsformedlingenIngestion(enable_enrichments=True) as af_client:
                # determine ssyk codes to fetch
                af_ssyk_codes = ssyk_codes
                
                # If no specific codes requested, try to load ALL from taxonomy
                if not af_ssyk_codes:
                    taxonomy_file = processor.processed_dir / "taxonomy_enriched.parquet"
                    if taxonomy_file.exists():
                        logger.info(f"Loading SSYK codes from {taxonomy_file}")
                        tax_df = pd.read_parquet(taxonomy_file)
                        if "ssyk_code" in tax_df.columns:
                            af_ssyk_codes = sorted(tax_df["ssyk_code"].astype(str).unique().tolist())
                            logger.info(f"Found {len(af_ssyk_codes)} unique SSYK codes in taxonomy")
                    
                # Fallback to default if still empty
                if not af_ssyk_codes:
                    logger.warning("No taxonomy file found and no codes provided. Using default list.")
                    af_ssyk_codes = DEFAULT_SSYK_CODES

                # Expand time window to ensure we get enough ads (last 2 years)
                start_date = (datetime.now() - pd.Timedelta(days=365*2)).strftime("%Y-%m-%dT00:00:00")
                
                jobs_raw = af_client.fetch_historical_ads(
                    ssyk_codes=af_ssyk_codes,
                    start_date=start_date,
                    max_results_per_occupation=max_job_ads,
                )
                
                # Save raw data
                af_client.save_to_parquet(
                    jobs_raw,
                    processor.raw_dir / "af_jobs_raw.parquet"
                )
                
                # Enrich with skills
                if not jobs_raw.empty:
                    logger.info("Enriching job ads with skills (this may take a while)...")
                    skills_raw = af_client.enrich_ads_with_skills(jobs_raw)
                    
                    if not skills_raw.empty:
                        skills_processed = af_client.aggregate_skills(skills_raw, jobs_raw)
                        logger.info(f"Aggregated {len(skills_processed)} skill records")
                        
                        af_client.save_to_parquet(
                            skills_raw,
                            processor.raw_dir / "af_skills_raw.parquet"
                        )
            logger.info(f"Fetched {len(jobs_raw)} job ads")
        
        # ===== STEP 4: Process data =====
        if 'process' in steps:
            logger.info("\n" + "="*40)
            logger.info("STEP 4: Processing data")
            logger.info("="*40)
            
            # Load raw data if missing (skipped steps)
            if income_raw is None:
                p = processor.raw_dir / "scb_income_raw.parquet"
                if p.exists(): income_raw = pd.read_parquet(p)
            
            if jobs_raw is None:
                p = processor.raw_dir / "af_jobs_raw.parquet"
                if p.exists(): jobs_raw = pd.read_parquet(p)
                
            if dispersion_raw is None:
                p = processor.raw_dir / "scb_dispersion_raw.parquet"
                if p.exists(): dispersion_raw = pd.read_parquet(p)
            
            # Process income data
            income_processed = pd.DataFrame()
            if income_raw is not None:
                income_processed = processor.process_income_data(income_raw)
                logger.info(f"Processed income data: {len(income_processed)} records")
            
            # Process job ads
            jobs_processed = pd.DataFrame()
            jobs_aggregated = pd.DataFrame()
            if jobs_raw is not None:
                jobs_processed = processor.process_jobs_data(jobs_raw)
                logger.info(f"Processed jobs data: {len(jobs_processed)} records")
                jobs_aggregated = processor.aggregate_jobs_by_region(jobs_processed, period="year")
                logger.info(f"Aggregated jobs data: {len(jobs_aggregated)} records")
            
            # Process dispersion
            dispersion_processed = None
            if dispersion_raw is not None:
                dispersion_processed = processor.process_dispersion_data(dispersion_raw)
            
            # Process age/education (Attempt load if None)
            if age_raw is None:
                p = processor.raw_dir / "scb_age_raw.parquet"
                if p.exists(): age_raw = pd.read_parquet(p)
            age_processed = processor.process_income_by_age_data(age_raw) if age_raw is not None else None

            if education_raw is None:
                p = processor.raw_dir / "scb_education_raw.parquet"
                if p.exists(): education_raw = pd.read_parquet(p)
            education_processed = processor.process_income_by_education_data(education_raw) if education_raw is not None else None
            
            # Load skills if available and not in memory
            if skills_processed is None:
                p = processor.processed_dir / "skills.parquet" # Or logic to process from raw? 
                # Actually pipeline saves skills in step 2 to raw? No, to processed dir in Step 4.
                # In Step 2 it is aggregated.
                # If we skip Step 2, we don't have new skills.
                # But Step 4 saves all processed data.
                pass

            # Save processed data
            paths = processor.save_processed_data(
                income_df=income_processed,
                jobs_df=jobs_processed,
                jobs_agg_df=jobs_aggregated,
                dispersion_df=dispersion_processed,
                skills_df=skills_processed,
                age_df=age_processed,
                education_df=education_processed,
            )
            
            if taxonomy_path:
                paths["taxonomy"] = taxonomy_path
            elif (processor.processed_dir / "taxonomy_enriched.parquet").exists():
                 paths["taxonomy"] = processor.processed_dir / "taxonomy_enriched.parquet"

            
            for name, path in paths.items():
                logger.info(f"  Saved {name}: {path}")
                
            # Create summary stats
            stats = processor.create_summary_stats(income_processed, jobs_processed)
            logger.info(f"\nSummary Statistics:")
            logger.info(f"  Income records: {stats['income'].get('record_count', 0)}")
            logger.info(f"  Job ads: {stats['jobs'].get('total_ads', 0)}")
        
        # ===== STEP 5: Upload =====
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
        
    except Exception as e:
        logger.error(f"\nPipeline failed: {e}", exc_info=True)
        raise


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Swedish Labor Market Data Pipeline"
    )
    parser.add_argument(
        "--steps",
        nargs="+",
        choices=["scb", "taxonomy", "jobs", "process", "all"],
        default=["all"],
        help="Pipeline steps to run. 'all' runs everything."
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
        default=None,  # Fetch all available years (start 2014)
        help="Years to fetch data for"
    )
    parser.add_argument(
        "--ssyk-codes",
        nargs="+",
        default=None,  # Fetch all SSYK codes by default
        help="SSYK occupation codes to fetch"
    )
    parser.add_argument(
        "--max-ads",
        type=int,
        default=500,  # Increased default to 500
        help="Maximum job ads per occupation"
    )
    
    args = parser.parse_args()
    
    steps = ["scb", "taxonomy", "jobs", "process"] if "all" in args.steps else args.steps
    
    run_pipeline(
        steps=steps,
        local_only=not args.upload_gcs,
        years=args.years,
        ssyk_codes=args.ssyk_codes,
        max_job_ads=args.max_ads,
    )


if __name__ == "__main__":
    main()
