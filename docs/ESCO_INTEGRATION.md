# ESCO Integration

This project integrates the European Skills, Competences, Qualifications and Occupations (ESCO) classification to enrich the Swedish occupational data (SSYK) with standardized skills.

## Strategy

Since there is no direct mapping between SSYK (Swedish) and ESCO (European), we utilize a two-step bridge strategy:

1.  **SSYK 2012 $\rightarrow$ ISCO-08**:
    *   **Source**: Statistics Sweden (SCB).
    *   **Method**: Automated download of the official conversion key (`webb_nyckel_ssyk2012_isco-08.xlsx`).
    *   **Logic**: Every Swedish occupation code (SSYK) is mapped to its International standard equivalent (ISCO-08).

2.  **ISCO-08 $\rightarrow$ ESCO**:
    *   **Source**: ESCO Portal (European Commission).
    *   **Method**: Manual download of the ESCO Dataset (CSV format).
    *   **Logic**: ESCO occupations are hierarchically child elements of ISCO-08 groups. We aggregate all ESCO skills associated with an ISCO-08 group to provide a "basket of potential skills" for the corresponding SSYK occupation.

## Setup Instructions

Because the ESCO portal does not support automated non-interactive downloads, you must provide the data files manually.

1.  **Download Data**:
    *   Go to the [ESCO Download Portal](https://esco.ec.europa.eu/en/use-esco/download).
    *   Select the latest version (e.g., **v1.2.1**).
    *   Choose **CSV** format.
    *   Enter your email to receive the download link.

2.  **Extract Files**:
    *   Unzip the package.
    *   Locate the following files (names may vary slightly by language pack):
        *   `occupations.csv`
        *   `occupations_skills.csv` (or `relationships_occupations_skills.csv`)
        *   `skills.csv` (Optional, for human-readable skill labels)

3.  **Place in Raw Directory**:
    *   Move these files to: `data-pipeline/data/raw/esco/`
    *   Ensure filenames match or update `src/data_pipeline/ingestion/esco_ingestion.py` if needed.

## Pipeline Usage

The integration is run as a pipeline step:

```bash
python scripts/run_pipeline.py --steps esco
# or as part of the full flow
python scripts/run_pipeline.py --steps taxonomy esco process
```
