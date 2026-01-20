# Data Pipeline Microservice

This microservice handles data ingestion from multiple sources for the Swedish labor market analytics platform.

## Data Sources

1. **SCB (Statistics Sweden)**: Income data by occupation and geography
2. **Arbetsförmedlingen API**: Job advertisements from Swedish Public Employment Service

## Project Structure

```
data-pipeline/
├── src/
│   └── data_pipeline/
│       ├── __init__.py
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── scb_ingestion.py
│       │   └── arbetsformedlingen_ingestion.py
│       ├── processing/
│       │   ├── __init__.py
│       │   └── data_processor.py
│       └── utils/
│           ├── __init__.py
│           └── config.py
├── tests/
├── configs/
│   └── config.yaml
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── scripts/
│   └── run_pipeline.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python scripts/run_pipeline.py
```

## Environment Variables

- `SCB_API_KEY`: API key for SCB
- `GCP_PROJECT_ID`: Google Cloud Project ID
- `GCS_BUCKET_NAME`: Google Cloud Storage bucket name
