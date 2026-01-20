# FastAPI Microservice

This microservice provides REST API endpoints for accessing Swedish labor market data.

## Features

- RESTful API for income and job advertisement data
- Filter by occupation, location, age, gender
- GCP-ready deployment with Docker
- Automatic API documentation (Swagger/OpenAPI)

## Project Structure

```
api/
├── src/
│   └── api/
│       ├── __init__.py
│       ├── main.py
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── income.py
│       │   └── jobs.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── schemas.py
│       └── utils/
│           ├── __init__.py
│           └── database.py
├── tests/
├── configs/
│   └── config.yaml
├── requirements.txt
├── Dockerfile
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

## Run Locally

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

- `GET /api/v1/income`: Get income data with filters
- `GET /api/v1/jobs`: Get job advertisements with filters
- `GET /api/v1/occupations`: List available occupations
- `GET /api/v1/regions`: List available regions
- `GET /api/v1/stats`: Get aggregated statistics

## Environment Variables

- `GCP_PROJECT_ID`: Google Cloud Project ID
- `GCS_BUCKET_NAME`: Google Cloud Storage bucket name
- `BIGQUERY_DATASET`: BigQuery dataset name
