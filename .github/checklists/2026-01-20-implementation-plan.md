# Implementation Plan - Swedish Labor Market Analytics

**Date:** 2026-01-20  
**Project:** curly-funicular  
**GCP Project:** mcp-occupation-classifier  
**Status:** ✅ COMPLETED

## Project Notes

### Data Storage Strategy
- Using **Parquet files** initially (stored locally in `data-pipeline/data/processed/`)
- Can migrate to BigQuery later when data volume grows
- This simplifies development and reduces costs for demo

### Scope
- Focus on SSYK codes **2511** (Systems analysts and IT architects) and **2512** (Software and systems developers)
- Swedish regions (NUTS-2 level: 8 regions + national total)

### GeoJSON Source
- Sweden regions: `https://raw.githubusercontent.com/okfse/sweden-geojson/master/swedish_regions.geojson`

---

## Sprint 1: Data Pipeline Foundation ✅

### SCB Ingestion
- [x] Read documentation carefully (labour-stats.md)
- [x] Implement HTTP client with rate limiting (30 req/10 sec → 3/sec safe limit)
- [x] Add JSON-stat2 parsing support via pyjstat
- [x] Handle missing data (NaN values)
- [x] Add surrogate key generation for idempotent updates
- [x] Save to Parquet format

### API Endpoint Used (SCB)
- Table: `LonYrkeRegion4AN` (Regional salary by occupation/sex)
- Endpoint: `https://api.scb.se/OV0104/v1/doris/en/ssd/AM/AM0110/AM0110A/LonYrkeRegion4AN`
- Method: POST with JSON query
- Format: json-stat2
- **Region codes:** Uses NUTS format (SE11=Stockholm, SE12=East-Central, etc.)
- **Available years:** 2023, 2024

---

## Sprint 2: Job Ads Pipeline ✅

### Arbetsförmedlingen APIs
- [x] Verified Historical Ads API works without key
- [x] Implemented Historical Ads ingestion (`https://historical.api.jobtechdev.se/search`)
- [x] Use `occupation-group` parameter with SSYK codes directly (not concept IDs)
- [x] Handle pagination (offset/limit)
- [x] Save to Parquet format

### API Endpoint Used (AF)
- Historical: `https://historical.api.jobtechdev.se/search?occupation-group=2512`
- No API key required
- Parameter: `occupation-group` accepts SSYK codes directly

---

## Sprint 3: Data Processing ✅

- [x] Transform SCB data to tidy/long format
- [x] Add SSYK code to occupation name mapping
- [x] Create aggregated job statistics by region
- [x] Processor saves to Parquet files

---

## Sprint 4: API Backend ✅

- [x] Update database.py to read from Parquet files (no GCS/BigQuery needed yet)
- [x] Connect income routes to real data
- [x] Connect jobs routes to real data
- [x] Add /jobs/aggregated endpoint for regional stats

---

## Sprint 5: Frontend ✅

- [x] Add Sweden GeoJSON for map choropleth (from okfse repo)
- [x] Connect map to real regional income data
- [x] Update charts to work with actual data structure (monthly_salary, gender)
- [x] Add loading states
- [x] Update filters to match available data (year, gender, occupation, region)

---

## Sprint 6: Testing & Deployment (Pending)

- [ ] Add pytest tests with mocked API responses
- [ ] Create .env.example
- [ ] Test Docker Compose locally
- [ ] Document deployment steps

---

## GCP APIs Enabled
- [x] Cloud Storage
- [x] BigQuery
- [x] Cloud Run
- [x] Cloud Scheduler
- [x] Cloud Build

---

## Dependencies Added

### Data Pipeline (requirements.txt)
- `httpx>=0.25.0` - HTTP client
- `pyjstat>=2.4.0` - JSON-stat2 parsing
- `pyarrow>=14.0.0` - Parquet support
- `tenacity>=8.2.0` - Retry logic

### API (requirements.txt)
- `pyarrow>=14.0.0` - Parquet reading

---

## Data Files Generated

| File | Records | Description |
|------|---------|-------------|
| `data/processed/income.parquet` | 144 | SCB salary data (2 occupations × 9 regions × 2 years × 2 genders × 2 measures) |
| `data/processed/jobs_detail.parquet` | 200 | Individual job ads from AF |
| `data/processed/jobs_aggregated.parquet` | 29 | Aggregated by region/occupation/year |

---

## Region Code Mapping (SCB NUTS-2)
| Code | Region |
|------|--------|
| SE | Sweden (national) |
| SE11 | Stockholm |
| SE12 | East-Central Sweden |
| SE21 | Småland and islands |
| SE22 | South Sweden |
| SE23 | West Sweden |
| SE31 | North-Central Sweden |
| SE32 | Central Norrland |
| SE33 | Upper Norrland |
