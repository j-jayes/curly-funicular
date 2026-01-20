# Quick Start Guide

Welcome to the Swedish Labor Market Analytics Platform! This guide will help you get started quickly.

## Prerequisites

- Docker and Docker Compose installed
- (Optional) Node.js 18+, Python 3.11+ for local development without Docker

## Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/j-jayes/curly-funicular.git
   cd curly-funicular
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration (optional for local development)
   ```

3. **Start all services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

That's it! The platform is now running locally.

## Development Without Docker

### Data Pipeline

```bash
cd data-pipeline
pip install -r requirements.txt
python scripts/run_pipeline.py
```

### API

```bash
cd api
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Visit http://localhost:8000/docs to see the API documentation.

### Frontend

```bash
cd frontend
npm install
npm start
```

The frontend will open at http://localhost:3000

## Using the Platform

### 1. Filter Data

Use the filter panel at the top to select:
- **Occupation**: Choose from available Swedish occupations (SSYK codes)
- **Region**: Select a Swedish region (län)
- **Age Group**: Filter by age ranges
- **Gender**: Filter by gender

### 2. View Visualizations

The platform provides three main visualizations:

1. **Sweden Map**: Interactive map showing regional data
   - Click on regions to see details
   - Color-coded based on data values

2. **Income Spread Chart**: Bar chart showing income distribution
   - 10th percentile (lowest earners)
   - Median income
   - 90th percentile (highest earners)

3. **Jobs Chart**: Line chart showing job distribution
   - Number of job openings by region
   - Based on Arbetsförmedlingen data

### 3. Explore the API

Visit http://localhost:8000/docs to explore all available endpoints:

- `GET /api/v1/income` - Fetch income statistics
- `GET /api/v1/jobs` - Fetch job advertisements
- `GET /api/v1/occupations` - List all occupations
- `GET /api/v1/regions` - List all regions
- `GET /api/v1/stats` - Get aggregated statistics

## Common Tasks

### Run Tests

```bash
# Pipeline tests
cd data-pipeline && pytest tests/

# API tests
cd api && pytest tests/
```

### Update Dependencies

```bash
# Python (pipeline/api)
pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f data-pipeline
```

### Stop Services

```bash
docker-compose down
```

### Clean Up

```bash
# Stop services and remove volumes
docker-compose down -v

# Or use Makefile
make clean
```

## Next Steps

- Read the [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system design
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for GCP deployment instructions
- Explore the code in each service directory
- Customize the visualizations and filters to your needs

## Troubleshooting

### Port Already in Use

If ports 3000 or 8000 are already in use:

```bash
# Change ports in docker-compose.yml
# For example, change "3000:80" to "3001:80"
```

### API Connection Error

If the frontend can't connect to the API:

1. Check that the API is running: http://localhost:8000/health
2. Verify `REACT_APP_API_URL` in `.env` is correct
3. Check CORS settings in `api/src/api/main.py`

### Build Errors

```bash
# Clear Docker cache and rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## Getting Help

- Open an issue on GitHub
- Check the documentation in each service's README
- Review the logs for error messages

## Features Overview

### Data Pipeline
✅ Ingests data from SCB (Statistics Sweden)  
✅ Ingests job ads from Arbetsförmedlingen  
✅ Processes and cleans data  
✅ Stores in GCS and BigQuery  
✅ Cookie cutter data science structure  

### API
✅ RESTful endpoints for data access  
✅ Filter by occupation, region, age, gender  
✅ Automatic API documentation  
✅ Pydantic validation  
✅ GCP integration  

### Frontend
✅ Interactive Sweden map  
✅ Income distribution charts  
✅ Job statistics visualization  
✅ Real-time filtering  
✅ Responsive design  
✅ Material-UI components  

Enjoy exploring Swedish labor market data! 🇸🇪
