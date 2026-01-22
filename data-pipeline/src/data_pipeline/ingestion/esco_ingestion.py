import logging
import pandas as pd
import requests
import io
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class EscoIngestion:
    """
    Handles ingestion and mapping of ESCO (European Skills, Competences, Qualifications and Occupations) data.
    
    Since there is no direct SSYK->ESCO mapping, this class implements a two-step bridge:
    1. SSYK 2012 -> ISCO-08 (via SCB translation key)
    2. ISCO-08 -> ESCO (via ESCO dataset)
    """
    
    SCB_KEY_URL = "https://www.scb.se/contentassets/0c0089cc085a45d49c1dc83923ad933a/webb_nyckel_ssyk2012_isco-08_20160905.xlsx"
    
    def __init__(self, raw_dir: Path):
        self.raw_dir = raw_dir / "esco"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.scb_file_path = self.raw_dir / "scb_ssyk_isco_key.xlsx"

    def fetch_scb_mapping(self) -> Path:
        """Downloads the official SSYK 2012 to ISCO-08 translation key from SCB."""
        if self.scb_file_path.exists():
            logger.info("SCB SSYK key already exists.")
            return self.scb_file_path
            
        logger.info(f"Downloading SCB SSYK-ISCO key from {self.SCB_KEY_URL}...")
        try:
            resp = requests.get(self.SCB_KEY_URL)
            resp.raise_for_status()
            
            with open(self.scb_file_path, "wb") as f:
                f.write(resp.content)
            logger.info("SCB key downloaded successfully.")
            
        except Exception as e:
            logger.error(f"Failed to download SCB key: {e}")
            raise
            
        return self.scb_file_path

    def load_mapping_table(self) -> pd.DataFrame:
        """Loads and cleans the SSYK -> ISCO mapping table."""
        if not self.scb_file_path.exists():
            self.fetch_scb_mapping()
            
        # SCB Excel has columns: 'SSYK 2012 kod', 'ISCO-08 ', 'Yrkesbenämning'
        df = pd.read_excel(self.scb_file_path, dtype=str)
        
        # Renaissance cleaning
        df = df.rename(columns={
            "SSYK 2012 kod": "ssyk_code_2012",
            "ISCO-08 ": "isco_08_code",
            "Yrkesbenämning": "occupation_name"
        })
        
        # Clean whitespace
        df["ssyk_code_2012"] = df["ssyk_code_2012"].str.strip()
        df["isco_08_code"] = df["isco_08_code"].str.strip()
        
        return df[["ssyk_code_2012", "isco_08_code"]]

    def process_esco_mapping(self, ssyk_taxonomy_df: pd.DataFrame) -> pd.DataFrame:
        """
        Enriches the local taxonomy dataframe with ESCO mappings if available.
        
        Requires manual download of ESCO CSVs to data/raw/esco/
        - occupations.csv
        - occupations_skills.csv
        - skills.csv (optional, for skill names)
        """
        
        # 1. Load SCB Key
        scb_key = self.load_mapping_table()
        
        # 2. Merge SCB Key to SSYK Data
        # We assume ssyk_taxonomy_df has 'ssyk_code'
        merged_df = ssyk_taxonomy_df.merge(
            scb_key, 
            left_on="ssyk_code", 
            right_on="ssyk_code_2012", 
            how="left"
        )
        
        # 3. Check for local ESCO files
        occupations_path = self.raw_dir / "occupations.csv"
        relations_path = self.raw_dir / "occupations_skills.csv"
        skills_path = self.raw_dir / "skills.csv"
        
        if not (occupations_path.exists() and relations_path.exists()):
            logger.warning("ESCO CSV files not found. Skipping ESCO enrichment. "
                           "Please download ESCO dataset v1.2.1 CSV and place 'occupations.csv' "
                           "and 'occupations_skills.csv' in data/raw/esco/")
            # Return with just the ISCO codes added
            return merged_df
            
        logger.info("Loading ESCO datasets...")
        
        # Load ESCO Occupations to link ISCO -> ESCO Occupation URI
        # Using specific columns to save memory
        esco_occ = pd.read_csv(occupations_path, usecols=["conceptUri", "iscoGroup"], dtype=str)
        
        # Filter where iscoGroup is not null
        esco_occ = esco_occ.dropna(subset=["iscoGroup"])
        
        # Load ESCO Skills Relationships
        esco_rels = pd.read_csv(relations_path, dtype=str)
        # Should have columns like: occupationUri, skillUri, relationType, ...
        # Standardize standard v1.2 columns checking might be needed if format varies
        
        # Filter for 'essential' skills if relationType exists
        if "relationType" in esco_rels.columns:
            esco_rels = esco_rels[esco_rels["relationType"] == "essential"]
            
        # Aggregate Skills per Occupation URI
        # occupationUri -> [skillUri, skillUri]
        occ_skills_map = esco_rels.groupby("occupationUri")["skillUri"].apply(list).reset_index()
        
        # Merge Skills map back to Occupations
        # iscoGroup -> [Skill URIs] (Note: One ISCO group has MANY ESCO occupations, so this is a 1-to-many explosion)
        # Strategy: We want to map SSYK -> ISCO -> [Aggregated ESCO Skills for that ISCO family]
        
        # Join ESCO Occupations with their Skills
        esco_full = esco_occ.merge(occ_skills_map, left_on="conceptUri", right_on="occupationUri", how="inner")
        
        # Aggregate ALL skills for an entire ISCO group
        # This is a broad approach: "If you are in this ISCO group, here is the universe of ESCO skills associated with it"
        # Since SSYK is roughly ISCO, this gives a "basket of likely skills"
        isco_skills_agg = esco_full.groupby("iscoGroup")["skillUri"].sum().reset_index()
        
        # Function to deduplicate list
        isco_skills_agg["esco_skill_uris"] = isco_skills_agg["skillUri"].apply(lambda x: list(set(x)))
        
        # 4. Merge ESCO Skills to SSYK Data
        final_df = merged_df.merge(
            isco_skills_agg[["iscoGroup", "esco_skill_uris"]],
            left_on="isco_08_code",
            right_on="iscoGroup",
            how="left"
        )
        
        logger.info(f"Enriched {final_df['esco_skill_uris'].notna().sum()} rows with ESCO skills mapping")
        
        return final_df

    def save_processed(self, df: pd.DataFrame, output_dir: Path) -> Path:
        output_path = output_dir / "taxonomy_esco_enriched.parquet"
        df.to_parquet(output_path, index=False)
        logger.info(f"Saved ESCO-enriched taxonomy to {output_path}")
        return output_path
