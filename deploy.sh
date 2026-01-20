#!/bin/bash
# Deploy Swedish Labor Market Analytics to Google Cloud Run
# 
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - Project set: gcloud config set project mcp-occupation-classifier
#   - Docker installed (for local builds) OR use Cloud Build
#
# Usage: ./deploy.sh [api|frontend|all]

set -e

PROJECT_ID="${GCP_PROJECT_ID:-mcp-occupation-classifier}"
REGION="${GCP_REGION:-europe-north1}"
API_SERVICE_NAME="labor-market-api"
FRONTEND_SERVICE_NAME="labor-market-frontend"

echo "=========================================="
echo "Swedish Labor Market Analytics Deployment"
echo "=========================================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Function to deploy API
deploy_api() {
    echo ">>> Deploying API service..."
    
    # First, copy the processed data into the API directory for deployment
    echo "    Copying data files..."
    mkdir -p api/data
    cp -r data-pipeline/data/processed/* api/data/ 2>/dev/null || echo "    No data files to copy"
    
    # Build and deploy using Cloud Build + Cloud Run
    echo "    Building and deploying API with Cloud Build..."
    gcloud builds submit api \
        --tag gcr.io/$PROJECT_ID/$API_SERVICE_NAME \
        --project $PROJECT_ID \
        --quiet
    
    # Deploy to Cloud Run
    gcloud run deploy $API_SERVICE_NAME \
        --image gcr.io/$PROJECT_ID/$API_SERVICE_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 512Mi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 3 \
        --set-env-vars "DATA_PATH=/app/data" \
        --project $PROJECT_ID
    
    # Get the API URL
    API_URL=$(gcloud run services describe $API_SERVICE_NAME \
        --platform managed \
        --region $REGION \
        --format 'value(status.url)' \
        --project $PROJECT_ID)
    
    echo "    API deployed at: $API_URL"
    echo "$API_URL" > .api_url
}

# Function to deploy frontend
deploy_frontend() {
    echo ">>> Deploying Frontend service..."
    
    # Get API URL if available
    API_URL=""
    if [ -f .api_url ]; then
        API_URL=$(cat .api_url)
    else
        # Try to get from Cloud Run
        API_URL=$(gcloud run services describe $API_SERVICE_NAME \
            --platform managed \
            --region $REGION \
            --format 'value(status.url)' \
            --project $PROJECT_ID 2>/dev/null || echo "")
    fi
    
    if [ -z "$API_URL" ]; then
        echo "    Warning: API URL not found. Using placeholder."
        API_URL="https://your-api-url"
    fi
    
    echo "    Using API URL: $API_URL"
    
    # Update frontend environment
    echo "REACT_APP_API_URL=$API_URL" > frontend/.env.production
    
    # Build and deploy using Cloud Build
    echo "    Building and deploying Frontend with Cloud Build..."
    gcloud builds submit frontend \
        --tag gcr.io/$PROJECT_ID/$FRONTEND_SERVICE_NAME \
        --project $PROJECT_ID \
        --quiet
    
    # Deploy to Cloud Run
    gcloud run deploy $FRONTEND_SERVICE_NAME \
        --image gcr.io/$PROJECT_ID/$FRONTEND_SERVICE_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 256Mi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 3 \
        --project $PROJECT_ID
    
    # Get the Frontend URL
    FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE_NAME \
        --platform managed \
        --region $REGION \
        --format 'value(status.url)' \
        --project $PROJECT_ID)
    
    echo "    Frontend deployed at: $FRONTEND_URL"
    echo "$FRONTEND_URL" > .frontend_url
}

# Main deployment logic
case "${1:-all}" in
    api)
        deploy_api
        ;;
    frontend)
        deploy_frontend
        ;;
    all)
        deploy_api
        echo ""
        deploy_frontend
        echo ""
        echo "=========================================="
        echo "Deployment Complete!"
        echo "=========================================="
        echo ""
        echo "API:      $(cat .api_url 2>/dev/null || echo 'See output above')"
        echo "Frontend: $(cat .frontend_url 2>/dev/null || echo 'See output above')"
        echo ""
        echo "To view logs:"
        echo "  gcloud run logs read $API_SERVICE_NAME --region $REGION"
        echo "  gcloud run logs read $FRONTEND_SERVICE_NAME --region $REGION"
        ;;
    *)
        echo "Usage: $0 [api|frontend|all]"
        exit 1
        ;;
esac
