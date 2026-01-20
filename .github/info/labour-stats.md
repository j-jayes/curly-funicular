This specification focuses exclusively on the extraction and processing of **Statistics Sweden (SCB)** salary data. As of 2026, SCB has transitioned to **PxWebApi v2**, though the legacy **v1** (POST-based) remains the standard for bulk historical retrieval.

### Project Specification: SCB Labor Market Data Ingestion

#### 1. Data Source Analysis

The target is the **Salary Structure Statistics** (Lönestrukturstatistik). To build the requested time series (2014–2025+), you must interface with the **SSYK 2012** (Standard for Swedish Classification of Occupations) tables.

**Core Tables:**

* **Table ID `AM0110A1` (Regional):** *Average monthly salary and salary dispersion by region, occupation (SSYK 2012), and sex.* This is your primary source for mapping.
* **Table ID `000000C5` & `000007AW` (Whole Economy):** Use these for national-level benchmarks if regional granularity is missing for specific niche occupations.

---

#### 2. Technical API Interface

SCB's API uses a "Selection" model. You do not "search"; you submit a JSON query defining the coordinates of the data cube you want to extract.

**Endpoint (v1):** `https://api.scb.se/OV0104/v1/doris/en/ssd/START/AM/AM0110/AM0110A/LonYrkeRegion4AN`

**Request Specification:**
Your pipeline must handle a `POST` request with the following schema:

```json
{
  "query": [
    { "code": "Region", "selection": { "filter": "item", "values": ["01", "03", "12"] } },
    { "code": "Yrke2012", "selection": { "filter": "item", "values": ["2512", "2513"] } },
    { "code": "Kon", "selection": { "filter": "item", "values": ["1", "2"] } },
    { "code": "ContentsCode", "selection": { "filter": "item", "values": ["000000NV"] } },
    { "code": "Tid", "selection": { "filter": "item", "values": ["2022", "2023", "2024"] } }
  ],
  "response": { "format": "json-stat2" }
}

```

* **Format Note:** Use `json-stat2`. It is a specialized JSON format for multi-dimensional data that significantly reduces payload size by separating metadata (labels) from the data vector.

---

#### 3. Data Dimensions & Classification

To ensure the "Map of Sweden" and "Gender/Age" filters work correctly, the data scientist must handle these specific dimensions:

| Dimension | Classification | Notes |
| --- | --- | --- |
| **Geography** | **NUTS-2 / County** | SCB uses numerical codes (e.g., `01` = Stockholm). You will need a lookup table to map these to ISO-codes or GeoJSON properties. |
| **Occupation** | **SSYK 2012** | Use the 4-digit level for maximum precision (e.g., `2512` for Software Developers). |
| **Gender** | **Sex (Kön)** | Coded as `1` (Men) and `2` (Women). |
| **Time** | **Annual** | Salary data is usually released annually in May/June for the previous year. |

---

#### 4. Pipeline ETL Requirements

**A. Extraction Logic**

* **Pagination:** The SCB API has a limit of **150,000 cells per request**. If you fetch all occupations for all regions, you must chunk the requests by `Yrke2012` (Occupation) to avoid 403/Payload Too Large errors.
* **Rate Limiting:** Implement a back-off strategy for the limit of **30 calls per 10 seconds**.

**B. Transformation (The "Long-Form" Pivot)**
The raw API response is a multi-dimensional array. Your pipeline must "melt" this into a tidy, long-form DataFrame:

1. **Map Labels:** Replace the integer codes (e.g., `1`) with human-readable strings (`Male`) using the metadata provided in the API's initial `GET` response.
2. **Handle Missing Data:** SCB uses ".." or "." for suppressed data (due to small sample sizes for privacy). These must be converted to `NaN`.
3. **Inflation Adjustment (Optional):** To make the time series meaningful, consider joining a CPI (Consumer Price Index) table to show "Real Salary" vs. "Nominal Salary."

---

#### 5. Storage Schema (BigQuery / PostgreSQL)

The final table should be partitioned by **Year** to optimize the FastAPI queries:

* `year`: INT
* `region_code`: STRING (e.g., "01")
* `ssyk_code`: STRING (e.g., "2512")
* `gender`: STRING
* `avg_monthly_salary`: FLOAT
* `standard_deviation`: FLOAT (available in certain tables for "spread" charts)

---


As of **January 2026**, SCB has streamlined bulk access via **PxWebApi 2.0**, but for a production-grade data science pipeline, you should treat the extraction as a **Distributed Chunking Task**.

Because SCB limits each request to approximately **150,000 cells**, a single query for "all occupations across all regions over 10 years" will trigger a `403 Forbidden` or `413 Payload Too Large` error.

### The Bulk Extraction Architecture

To "format the data to serve from your app," you shouldn't just download a single CSV; you should build a **sharded ingestion engine**.

#### 1. The Sharding Strategy (Horizontal Partitioning)

Instead of one massive request, partition your extraction by the **Occupation (SSYK)** dimension. This is the most stable dimension and ensures each "chunk" fits within the API's memory limits.

* **Step A:** Fetch the full list of SSYK codes for your target table using a `GET` request to the table's metadata endpoint.
* **Step B:** Group these codes into batches of ~50–100 occupations.
* **Step C:** Loop through these batches, requesting all `Regions`, `Genders`, and `Years` for that specific subset of jobs.

#### 2. Advanced Protocol: JSON-stat2 & Parquet

For bulk downloads, avoid standard JSON.

* **JSON-stat2:** This is the current gold standard for SCB data. It de-duplicates dimension labels, reducing the payload size by up to 80% compared to standard JSON.
* **Parquet:** Some newer SCB endpoints in 2025/2026 support direct stream-to-parquet. If available for your table, use it to preserve schema types (Int/Float) without manual casting.

#### 3. Handling Rate Limits (The "30/10" Rule)

SCB enforces a limit of **30 requests per 10 seconds**. A "skilled data scientist" approach uses a **Semaphore-controlled Asynchronous Worker**:

```python
import asyncio
from aiolimiter import AsyncLimiter
from pyaxis import parse_json_stat # Standard library for SCB formats

# Limit to 3 requests per second to stay safely under the 30/10 limit
limiter = AsyncLimiter(3, 1)

async def fetch_chunk(ssyk_batch):
    async with limiter:
        # POST request to SCB API
        response = await client.post(URL, json=build_query(ssyk_batch))
        return parse_json_stat(response.json())

# Master loop to gather all chunks
all_data = await asyncio.gather(*[fetch_chunk(batch) for batch in ssyk_batches])

```

#### 4. Post-Extraction: The "Tidy" Format

The SCB response will be "wide" or "nested." To serve an app, you must transform it into a **Tidy/Long Format**.

| Year | SSYK_Code | Region_ID | Gender | Salary_Avg |
| --- | --- | --- | --- | --- |
| 2024 | 2512 | 01 | Male | 55400 |
| 2024 | 2512 | 01 | Female | 53200 |

> **Critical Expert Tip:** In your ETL, create a **Surrogate Key** by hashing `year + ssyk + region + gender`. This allows you to perform **Idempotent Upserts** into your GCP BigQuery table, ensuring that if you run the bulk download twice, you don't get duplicate data.

#### 5. Verification: The Checksum Step

After a bulk download, always compare the **Cell Count** in the metadata of the API response against the number of rows in your final DataFrame. Missing rows usually indicate "suppressed data" (where SCB hides values for privacy), which your app needs to handle as `null` rather than `0`.

---

**Would you like me to generate the actual SSYK-to-NUTS2 mapping table query so you can start the bulk download for specific Swedish regions immediately?**