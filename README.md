# Swedish Labor Market Analytics Platform

A microservice architecture for analyzing Swedish labor market data, including income statistics and job advertisements.

## Architecture Overview

This project follows a cookie cutter data science style layout with three main microservices:

```
curly-funicular/
├── data-pipeline/          # Data ingestion and processing microservice
├── api/                    # FastAPI REST API microservice
├── frontend/               # React frontend microservice
├── docker-compose.yml      # Local development setup
└── README.md
```

### Components

#### 1. Data Pipeline (`data-pipeline/`)

Ingests and processes data from multiple sources:
- **SCB (Statistics Sweden)**: Income data by occupation and geography
- **Arbetsförmedlingen API**: Job advertisements from Swedish Public Employment Service

**Key Features:**
- Automated data ingestion
- Data processing and cleaning
- GCS storage integration
- Cookie cutter data science structure

**Tech Stack:** Python, Pandas, Google Cloud Storage, BigQuery

#### 2. API (`api/`)

FastAPI-based REST API providing endpoints for data access.

**Endpoints:**
- `GET /api/v1/income` - Income data with filters
- `GET /api/v1/jobs` - Job advertisements
- `GET /api/v1/occupations` - List of occupations
- `GET /api/v1/regions` - List of Swedish regions
- `GET /api/v1/stats` - Aggregated statistics

**Tech Stack:** FastAPI, Pydantic, Google Cloud SDK

#### 3. Frontend (`frontend/`)

React-based interactive dashboard.

**Features:**
- Interactive map of Sweden
- Income spread visualization
- Job statistics charts
- Filters: occupation, age, gender, location

**Tech Stack:** React, Material-UI, Recharts, D3.js

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local pipeline/API development)
- Google Cloud Project (for deployment)

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/j-jayes/curly-funicular.git
cd curly-funicular
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start all services with Docker Compose:
```bash
docker-compose up --build
```

Services will be available at:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Individual Service Setup

#### Data Pipeline

```bash
cd data-pipeline
pip install -r requirements.txt
python scripts/run_pipeline.py
```

#### API

```bash
cd api
pip install -r requirements.txt
uvicorn api.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

## GCP Deployment

### Prerequisites

1. GCP Project with billing enabled
2. Enable required APIs:
   - Cloud Storage
   - BigQuery
   - Cloud Run
   - Container Registry

### Deployment Steps

#### 1. Build and Push Docker Images

```bash
# Set project ID
export GCP_PROJECT_ID=your-project-id

# Data Pipeline
cd data-pipeline
gcloud builds submit --tag gcr.io/${GCP_PROJECT_ID}/labor-market-pipeline

# API
cd ../api
gcloud builds submit --tag gcr.io/${GCP_PROJECT_ID}/labor-market-api

# Frontend
cd ../frontend
gcloud builds submit --tag gcr.io/${GCP_PROJECT_ID}/labor-market-frontend
```

#### 2. Deploy to Cloud Run

```bash
# Deploy API
gcloud run deploy labor-market-api \
  --image gcr.io/${GCP_PROJECT_ID}/labor-market-api \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated

# Deploy Frontend
gcloud run deploy labor-market-frontend \
  --image gcr.io/${GCP_PROJECT_ID}/labor-market-frontend \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated
```

#### 3. Schedule Data Pipeline

Set up Cloud Scheduler to run the pipeline periodically:

```bash
gcloud scheduler jobs create http labor-market-pipeline-daily \
  --schedule="0 2 * * *" \
  --uri="https://your-pipeline-url/run" \
  --http-method=POST
```

## Project Structure Details

### Data Pipeline Structure

```
data-pipeline/
├── src/
│   └── data_pipeline/
│       ├── ingestion/          # Data ingestion modules
│       ├── processing/         # Data processing
│       └── utils/              # Utilities
├── tests/                      # Unit tests
├── configs/                    # Configuration files
├── data/                       # Data storage
│   ├── raw/                    # Raw data
│   └── processed/              # Processed data
├── notebooks/                  # Jupyter notebooks
├── scripts/                    # Execution scripts
└── requirements.txt
```

### API Structure

```
api/
├── src/
│   └── api/
│       ├── routes/             # API endpoints
│       ├── models/             # Data models
│       └── utils/              # Utilities
├── tests/                      # API tests
├── configs/                    # Configuration
└── requirements.txt
```

### Frontend Structure

```
frontend/
├── public/                     # Static files
├── src/
│   ├── components/
│   │   ├── Map/               # Map component
│   │   ├── Charts/            # Chart components
│   │   ├── Filters/           # Filter panel
│   │   └── Layout/            # Layout components
│   └── services/              # API service
└── package.json
```

## Data Sources

### SCB (Statistics Sweden)

- **Type:** Income statistics by occupation and geography
- **API:** https://api.scb.se/OV0104/v1/doris/en/ssd
- **Coverage:** Swedish occupations (SSYK codes), all regions
- **Update Frequency:** Annual

### Arbetsförmedlingen

- **Type:** Job advertisements
- **API:** https://jobsearch.api.jobtechdev.se
- **Coverage:** Current job openings in Sweden
- **Update Frequency:** Real-time

## Features

### Filters

- **Occupation:** SSYK occupation codes
- **Location:** Swedish regions (län)
- **Age Group:** 18-24, 25-34, 35-44, 45-54, 55-64, 65+
- **Gender:** Male, Female, All

### Visualizations

1. **Sweden Map:** Interactive regional visualization
2. **Income Spread Chart:** Bar chart showing income percentiles
3. **Jobs Chart:** Line chart showing job distribution

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the terms in the LICENSE file.

## Support

For questions or issues, please open an issue on GitHub.