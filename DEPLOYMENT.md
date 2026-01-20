# Deploying to Google Cloud Platform

This guide covers deploying the Swedish Labor Market Analytics platform to GCP.

## Prerequisites

1. GCP account with billing enabled
2. `gcloud` CLI installed and authenticated
3. Docker installed locally

## Setup GCP Project

```bash
# Set your project ID
export GCP_PROJECT_ID="your-project-id"
gcloud config set project ${GCP_PROJECT_ID}

# Enable required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  storage.googleapis.com \
  bigquery.googleapis.com \
  cloudscheduler.googleapis.com
```

## Create GCS Bucket

```bash
export GCS_BUCKET_NAME="labor-market-data-${GCP_PROJECT_ID}"
gsutil mb -l europe-north1 gs://${GCS_BUCKET_NAME}
```

## Create BigQuery Dataset

```bash
bq --location=EU mk --dataset ${GCP_PROJECT_ID}:labor_market
```

## Build and Deploy Services

### 1. Data Pipeline

```bash
cd data-pipeline

# Build and push image
gcloud builds submit --tag gcr.io/${GCP_PROJECT_ID}/labor-market-pipeline

# Deploy as Cloud Run job
gcloud run jobs create labor-market-pipeline \
  --image gcr.io/${GCP_PROJECT_ID}/labor-market-pipeline \
  --region europe-north1 \
  --set-env-vars GCP_PROJECT_ID=${GCP_PROJECT_ID},GCS_BUCKET_NAME=${GCS_BUCKET_NAME}
```

### 2. API Service

```bash
cd api

# Build and push image
gcloud builds submit --tag gcr.io/${GCP_PROJECT_ID}/labor-market-api

# Deploy to Cloud Run
gcloud run deploy labor-market-api \
  --image gcr.io/${GCP_PROJECT_ID}/labor-market-api \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=${GCP_PROJECT_ID},GCS_BUCKET_NAME=${GCS_BUCKET_NAME},BIGQUERY_DATASET=labor_market
```

### 3. Frontend

```bash
cd frontend

# Build and push image
gcloud builds submit --tag gcr.io/${GCP_PROJECT_ID}/labor-market-frontend

# Get API URL
export API_URL=$(gcloud run services describe labor-market-api \
  --region europe-north1 \
  --format 'value(status.url)')

# Deploy to Cloud Run
gcloud run deploy labor-market-frontend \
  --image gcr.io/${GCP_PROJECT_ID}/labor-market-frontend \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated \
  --set-env-vars API_URL=${API_URL}
```

## Schedule Data Pipeline

Set up Cloud Scheduler to run the pipeline daily:

```bash
# Create service account for scheduler
gcloud iam service-accounts create pipeline-scheduler \
  --display-name="Pipeline Scheduler"

# Grant invoker role
gcloud run jobs add-iam-policy-binding labor-market-pipeline \
  --region=europe-north1 \
  --member=serviceAccount:pipeline-scheduler@${GCP_PROJECT_ID}.iam.gserviceaccount.com \
  --role=roles/run.invoker

# Create scheduler job
gcloud scheduler jobs create http labor-market-pipeline-daily \
  --location=europe-north1 \
  --schedule="0 2 * * *" \
  --uri="https://europe-north1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${GCP_PROJECT_ID}/jobs/labor-market-pipeline:run" \
  --http-method=POST \
  --oauth-service-account-email=pipeline-scheduler@${GCP_PROJECT_ID}.iam.gserviceaccount.com
```

## Access Your Application

```bash
# Get frontend URL
gcloud run services describe labor-market-frontend \
  --region europe-north1 \
  --format 'value(status.url)'

# Get API URL
gcloud run services describe labor-market-api \
  --region europe-north1 \
  --format 'value(status.url)'
```

## Monitoring

### View Logs

```bash
# API logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=labor-market-api" \
  --limit 50 \
  --format json

# Pipeline logs
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=labor-market-pipeline" \
  --limit 50 \
  --format json
```

### Set Up Alerts

Create alert policies in Cloud Monitoring for:
- API response time
- Error rates
- Pipeline failures

## Cost Optimization

1. **Cloud Run**: Uses pay-per-request pricing
2. **GCS**: Use lifecycle policies for old data
3. **BigQuery**: Partition tables by date
4. **Cloud Scheduler**: Minimal cost for scheduled jobs

### Example Lifecycle Policy for GCS

```bash
cat > lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 365}
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://${GCS_BUCKET_NAME}
```

## Security

### Set Up VPC Connector (Optional)

For private resources:

```bash
gcloud compute networks vpc-access connectors create labor-market-connector \
  --region=europe-north1 \
  --network=default \
  --range=10.8.0.0/28
```

### Use Secret Manager for API Keys

```bash
# Store SCB API key
echo -n "your-scb-api-key" | \
  gcloud secrets create scb-api-key --data-file=-

# Grant access to service
gcloud secrets add-iam-policy-binding scb-api-key \
  --member=serviceAccount:YOUR-SERVICE-ACCOUNT@${GCP_PROJECT_ID}.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

## Troubleshooting

### Check Service Status

```bash
gcloud run services list --region=europe-north1
```

### View Service Details

```bash
gcloud run services describe SERVICE-NAME --region=europe-north1
```

### Test API Locally with Cloud Run

```bash
# Build locally
docker build -t labor-market-api ./api

# Run with cloud credentials
docker run -p 8000:8000 \
  -v ~/.config/gcloud:/root/.config/gcloud \
  -e GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json \
  labor-market-api
```

## Clean Up

To delete all resources:

```bash
# Delete Cloud Run services
gcloud run services delete labor-market-api --region=europe-north1
gcloud run services delete labor-market-frontend --region=europe-north1
gcloud run jobs delete labor-market-pipeline --region=europe-north1

# Delete Cloud Scheduler job
gcloud scheduler jobs delete labor-market-pipeline-daily --location=europe-north1

# Delete GCS bucket
gsutil -m rm -r gs://${GCS_BUCKET_NAME}

# Delete BigQuery dataset
bq rm -r -f ${GCP_PROJECT_ID}:labor_market
```
