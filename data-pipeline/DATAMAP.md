# SCB Datamap

This document outlines the Statistics Sweden (SCB) tables used in the data pipeline to ingest labor market salary statistics. The pipeline focuses on the "Structure of Earnings" (Lönestrukturstatistik) by SSYK 2012 codes.

## Overview of Tables

| Table Alias | SCB Table ID | Description | Key Dimensions | Time Series | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Regional Salaries** | `LonYrkeRegion4AN` | Average monthly salary by region and occupation. | Region, SSYK 2012, Sex, Sector, Year | 2014–Present | Active |
| **Salary Dispersion** | `LoneSpridSektYrk4AN` | Wage dispersion (percentiles) by sector and occupation. | SSYK 2012, Sex, Sector, Year, Percentiles (10, 25, 50, 75, 90) | 2014–Present | Active |
| **Salaries by Age** | `LonYrkeAlder4AN` | Average monthly salary by age group and occupation. | **Age Class**, SSYK 2012, Sex, Sector, Year | 2014–Present | **New** |
| **Salaries by Education** | `LonYrkeUtb4AN` | Average monthly salary by level of education and occupation. | **Education Level**, SSYK 2012, Sex, Sector, Year | 2014–Present | **New** |

## Detailed Table Specifications

### 1. Regional Salaries (`LonYrkeRegion4AN`)
**Endpoint:** `/AM/AM0110/AM0110A/LonYrkeRegion4AN`
**Dimensions:**
- **Region:** NUTS-2 codes (e.g., SE11 Stockholm).
- **Sektor:** 0 (All), 1-3 (Public), 4-5 (Private).
- **Yrke2012:** SSYK 4-digit codes.
- **Kon:** 1 (Men), 2 (Women), 1+2 (Total).
- **ContentsCode:** 000007AS (Monthly Salary), 000007AP (Number of Employees).
- **Tid:** Years (YYYY).

### 2. Salary Dispersion (`LoneSpridSektYrk4AN`)
**Endpoint:** `/AM/AM0110/AM0110A/LoneSpridSektYrk4AN`
**Dimensions:**
- **Sektor:** Breakdown by sector.
- **Yrke2012:** SSYK 4-digit codes.
- **Kon:** Sex breakdown.
- **ContentsCode:** 000007CE (Median), 000007CF (P10), 000007CG (P25), 000007CH (P75), 000007CI (P90), 000007CD (Mean).
- **Tid:** Years (YYYY).

### 3. Salaries by Age (`LonYrkeAlder4AN`)
**Endpoint:** `/AM/AM0110/AM0110A/LonYrkeAlder4AN`
**Dimensions:**
- **Alder:** Age groups (e.g., "18-24", "25-29", ranges).
- **Sektor:** Sector.
- **Yrke2012:** SSYK 4-digit codes.
- **Kon:** Sex breakdown.
- **ContentsCode:** 000007AS (Monthly Salary).
- **Tid:** Years (YYYY).

### 4. Salaries by Education (`LonYrkeUtb4AN`)
**Endpoint:** `/AM/AM0110/AM0110A/LonYrkeUtb4AN`
**Dimensions:**
- **Utbildningsniva:** Education level (e.g., "Post-secondary <3 years", "PhD").
- **Sektor:** Sector.
- **Yrke2012:** SSYK 4-digit codes.
- **Kon:** Sex breakdown.
- **ContentsCode:** 000007AS (Monthly Salary).
- **Tid:** Years (YYYY).

## Data Processing Strategy
- **Format:** JSON-stat2 (for efficiency).
- **Chunking:** Requests are chunked by occupation lists to avoid 150k cell limit.
- **Rate Limit:** 1 request per second to ensure safety.
- **Surrogate Key:** A hash of `Year + SSYK + Region + Sex + ...` is created for idempotent storage.
