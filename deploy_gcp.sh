#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# Function to check if a variable is set
check_var() {
    if [ -z "${!1}" ]; then
        echo "Error: Environment variable $1 is not set."
        echo "Please set it using: export $1=value"
        exit 1
    fi
}

echo "========================================================"
echo "      Swedish Labor Market Analytics Deployment       "
echo "========================================================"

# Load environment variables from .env if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    # Only export lines that are not comments and contain an equals sign
    export $(grep -v '^#' .env | grep '=' | xargs)
fi

# Check required environment variables
check_var "GCP_PROJECT_ID"
check_var "GCS_BUCKET_NAME"

REGION="europe-north1"

echo "Using Project ID: $GCP_PROJECT_ID"
echo "Using GCS Bucket: $GCS_BUCKET_NAME"
echo "Region:           $REGION"
echo "========================================================"

# Step 0: Sync Data
echo "Step 0: Syncing processed data to API build context..."
if ! make sync-data; then
    echo "Error: Data sync failed."
    exit 1
fi
echo "Data sync complete."

# Step 1: Build and Push Images
echo "Step 1: Building and pushing Docker images to Container Registry..."

echo "- Building Data Pipeline..."
gcloud builds submit data-pipeline --tag gcr.io/$GCP_PROJECT_ID/labor-market-pipeline

echo "- Building API..."
gcloud builds submit api --tag gcr.io/$GCP_PROJECT_ID/labor-market-api

echo "- Building Frontend..."
# Note: For production, we might need to inject env vars differently depending on React setup
gcloud builds submit frontend --tag gcr.io/$GCP_PROJECT_ID/labor-market-frontend

# Step 2: Deploy Services
echo "Step 2: Deploying services to Cloud Run..."

# Deploy Data Pipeline (Job)
echo "- Deploying Data Pipeline Job..."
# Try to create, if fails, assume it exists and ignore or update
gcloud run jobs create labor-market-pipeline \
  --image gcr.io/$GCP_PROJECT_ID/labor-market-pipeline \
  --region $REGION \
  --set-env-vars GCP_PROJECT_ID=$GCP_PROJECT_ID,GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
  --quiet 2>/dev/null || \
gcloud run jobs update labor-market-pipeline \
  --image gcr.io/$GCP_PROJECT_ID/labor-market-pipeline \
  --region $REGION \
  --set-env-vars GCP_PROJECT_ID=$GCP_PROJECT_ID,GCS_BUCKET_NAME=$GCS_BUCKET_NAME

# Deploy API Service
echo "- Deploying API Service..."
gcloud run deploy labor-market-api \
  --image gcr.io/$GCP_PROJECT_ID/labor-market-api \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=$GCP_PROJECT_ID,GCS_BUCKET_NAME=$GCS_BUCKET_NAME,BIGQUERY_DATASET=labor_market

# Retrieve API URL
API_URL=$(gcloud run services describe labor-market-api --region $REGION --format 'value(status.url)')
echo "API URL retrieved: $API_URL"

# Deploy Frontend Service
echo "- Deploying Frontend Service..."
gcloud run deploy labor-market-frontend \
  --image gcr.io/$GCP_PROJECT_ID/labor-market-frontend \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars REACT_APP_API_URL=$API_URL/api/v1,API_URL=$API_URL/api/v1

FRONTEND_URL=$(gcloud run services describe labor-market-frontend --region $REGION --format 'value(status.url)')

echo "========================================================"
echo "Deployment Complete!"
echo ""
echo "Frontend: $FRONTEND_URL"
echo "API:      $API_URL"
echo ""
echo "To schedule the pipeline daily, verify your Cloud Scheduler settings."
echo "========================================================"
