"""Main pipeline execution script."""

import logging
import sys
from datetime import datetime

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


def run_pipeline():
    """Run the complete data pipeline."""
    logger.info("Starting data pipeline")
    
    # Load settings
    settings = get_settings()
    
    try:
        # Initialize ingestion clients
        scb_client = SCBIngestion(api_key=settings.scb_api_key)
        af_client = ArbetsformedlingenIngestion()
        processor = DataProcessor()
        
        # Fetch income data from SCB
        logger.info("Fetching income data from SCB")
        income_df = scb_client.fetch_income_data()
        
        # Fetch job ads from Arbetsförmedlingen
        logger.info("Fetching job ads from Arbetsförmedlingen")
        jobs_df = af_client.fetch_all_job_ads(max_results=1000)
        
        # Process and merge data
        logger.info("Processing data")
        merged_df = processor.merge_income_and_jobs(income_df, jobs_df)
        cleaned_df = processor.clean_data(merged_df)
        final_df = processor.add_derived_features(cleaned_df)
        
        # Save to GCS
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        blob_name = f"processed/labor_market_data_{timestamp}.parquet"
        
        logger.info(f"Saving processed data to GCS")
        scb_client.save_to_gcs(
            final_df,
            settings.gcs_bucket_name,
            blob_name
        )
        
        logger.info("Pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run_pipeline()
