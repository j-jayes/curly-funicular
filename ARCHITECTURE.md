# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Swedish Labor Market Analytics                │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│   Data Sources       │
├──────────────────────┤
│  • SCB API           │  Income data by occupation/geography
│  • Arbetsförmedlingen│  Job advertisements
└──────┬───────────────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│            Data Pipeline (Python)                 │
├──────────────────────────────────────────────────┤
│  • Ingestion modules (scb_ingestion.py,          │
│    arbetsformedlingen_ingestion.py)               │
│  • Data processing & cleaning                     │
│  • Cookie cutter data science structure           │
└──────┬───────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│         Google Cloud Storage (GCS)                │
│         & BigQuery                                │
├──────────────────────────────────────────────────┤
│  • Parquet files in GCS                           │
│  • Structured tables in BigQuery                  │
└──────┬───────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│              FastAPI Backend                      │
├──────────────────────────────────────────────────┤
│  Endpoints:                                       │
│  • GET /api/v1/income                            │
│  • GET /api/v1/jobs                              │
│  • GET /api/v1/occupations                       │
│  • GET /api/v1/regions                           │
│  • GET /api/v1/stats                             │
└──────┬───────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│              React Frontend                       │
├──────────────────────────────────────────────────┤
│  Components:                                      │
│  • Sweden Map (D3.js)                            │
│  • Income Charts (Recharts)                      │
│  • Jobs Charts (Recharts)                        │
│  • Filter Panel (MUI)                            │
│    - Occupation dropdown                          │
│    - Region dropdown                              │
│    - Age group dropdown                           │
│    - Gender dropdown                              │
└──────────────────────────────────────────────────┘
```

## Deployment Architecture (GCP)

```
┌─────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                     │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐
│ Cloud Scheduler  │  (Daily pipeline execution)
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Cloud Run Job: Data Pipeline                               │
│  • Scheduled execution                                       │
│  • Ingests data from external APIs                          │
│  • Processes and stores in GCS/BigQuery                     │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Cloud Storage (GCS)          BigQuery                      │
│  • Raw data (Parquet)         • Processed tables            │
│  • Processed data             • Optimized for queries       │
└────────┬────────────────────────────┬───────────────────────┘
         │                            │
         └────────────┬───────────────┘
                      ▼
         ┌────────────────────────────┐
         │  Cloud Run: FastAPI        │
         │  • Serverless deployment   │
         │  • Auto-scaling            │
         │  • REST API endpoints      │
         └────────────┬───────────────┘
                      │
                      ▼
         ┌────────────────────────────┐
         │  Cloud Run: Frontend       │
         │  • Static React app        │
         │  • Nginx server            │
         │  • Auto-scaling            │
         └────────────────────────────┘
```

## Data Flow

1. **Ingestion**: Cloud Scheduler triggers the data pipeline daily
2. **Processing**: Pipeline fetches data from SCB and Arbetsförmedlingen APIs
3. **Storage**: Processed data stored in GCS (Parquet) and BigQuery (tables)
4. **API**: FastAPI queries BigQuery and serves data via REST endpoints
5. **Frontend**: React app fetches data from API and displays visualizations
6. **User Interaction**: Filters update visualizations in real-time

## Technology Stack

### Data Pipeline
- **Language**: Python 3.11
- **Libraries**: Pandas, Requests, Google Cloud SDK
- **Storage**: Google Cloud Storage, BigQuery
- **Deployment**: Cloud Run Jobs

### API
- **Framework**: FastAPI
- **Validation**: Pydantic
- **Database**: BigQuery (via Google Cloud SDK)
- **Documentation**: OpenAPI/Swagger
- **Deployment**: Cloud Run

### Frontend
- **Framework**: React 18
- **UI**: Material-UI
- **Charts**: Recharts
- **Maps**: D3.js
- **HTTP Client**: Axios
- **Deployment**: Cloud Run (Nginx)

## Security

- **Authentication**: Cloud IAM for service-to-service
- **API Keys**: Secret Manager for external API keys
- **CORS**: Configured in FastAPI
- **HTTPS**: Automatic SSL via Cloud Run

## Scalability

- **Auto-scaling**: Cloud Run handles traffic automatically
- **Caching**: Can add Cloud CDN for frontend
- **Database**: BigQuery scales automatically
- **Cost**: Pay-per-request pricing model
