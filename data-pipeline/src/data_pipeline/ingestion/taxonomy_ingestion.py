
import requests
import json
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class TaxonomyIngestion:
    """Handles fetching and processing of Arbetsförmedlingen Taxonomy data."""
    
    URLS = {
        "ssyk4_skills": "https://data.arbetsformedlingen.se/taxonomy/version/27/query/ssyk-level-4-with-related-skills-and-occupations/ssyk-level-4-with-related-skills-and-occupations.json",
        "occupation_fields": "https://data.arbetsformedlingen.se/taxonomy/version/27/query/occupation-fields-with-related-ssyk-level-4-groups-and-occupations/occupation-fields-with-related-ssyk-level-4-groups-and-occupations.json",
        "ssyk_hierarchy": "https://data.arbetsformedlingen.se/taxonomy/version/27/query/the-ssyk-hierarchy-with-occupations/the-ssyk-hierarchy-with-occupations.json"
    }
    
    def __init__(self, raw_dir: Path):
        self.raw_dir = raw_dir / "taxonomy"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        
    def fetch_files(self):
        """Downloads the required taxonomy files."""
        for name, url in self.URLS.items():
            filepath = self.raw_dir / f"{name}.json"
            if filepath.exists():
                logger.info(f"Taxonomy file {name} already exists.")
                continue
                
            logger.info(f"Fetching taxonomy file {name}...")
            try:
                resp = requests.get(url)
                resp.raise_for_status()
                with open(filepath, "w") as f:
                    json.dump(resp.json(), f)
            except Exception as e:
                logger.error(f"Failed to fetch {name}: {e}")
                raise

    def load_json(self, name: str) -> Dict:
        with open(self.raw_dir / f"{name}.json", "r") as f:
            return json.load(f)

    def _extract_occupations_from_hierarchy(self, concepts: List[Dict]) -> Dict[str, List[str]]:
        """Recursively traverses the hierarchy to find SSYK Level 4 to Occupation mappings."""
        mapping = {}
        
        for item in concepts:
            item_type = item.get("type")
            
            # If we hit Level 4, extract its occupations
            if item_type == "ssyk-level-4":
                ssyk_code = item.get("ssyk_code_2012")
                occupations = []
                for child in item.get("narrower", []):
                    if child.get("type") == "occupation-name":
                        occupations.append(child.get("preferred_label"))
                
                if ssyk_code:
                    mapping[ssyk_code] = occupations
            
            # Recurse if there are children (regardless of current type, as long as it's not the leaf)
            if "narrower" in item:
                 # Recursive merge
                 child_map = self._extract_occupations_from_hierarchy(item.get("narrower", []))
                 mapping.update(child_map)
                 
        return mapping

    def process_taxonomy(self) -> pd.DataFrame:
        """Joins occupation fields, skills, and hierarchy data into a unified DataFrame."""
        
        # 1. Parse Occupation Fields to get SSYK Code properties (Label, Definition, Field)
        fields_data = self.load_json("occupation_fields")
        ssyk_map = {} # taxonomy_id -> {code, label, definition, field}
        
        for field in fields_data["data"]["concepts"]:
            field_label = field.get("preferred_label")
            for group in field.get("narrower", []):
                tid = group.get("id")
                # Extract SSYK Code 2012
                ssyk_code = group.get("ssyk_code_2012")
                
                if tid and ssyk_code:
                    ssyk_map[tid] = {
                        "ssyk_code": ssyk_code,
                        "ssyk_name": group.get("preferred_label"),
                        "ssyk_definition": group.get("definition"),
                        "occupation_field": field_label,
                        "taxonomy_id": tid
                    }
        
        logger.info(f"Found {len(ssyk_map)} SSYK Level 4 groups in occupation fields")
        
        # 2. Parse Hierarchy to get comprehensive Occupation Name list
        hierarchy_data = self.load_json("ssyk_hierarchy")
        hierarchy_occupations_map = self._extract_occupations_from_hierarchy(hierarchy_data["data"]["concepts"])
        logger.info(f"Extracted occupation lists for {len(hierarchy_occupations_map)} SSYK codes from hierarchy")

        # 3. Parse Skills to get related skills (and potentially other occupations, but we prioritize hierarchy)
        skills_data = self.load_json("ssyk4_skills")
        records = []
        
        for group in skills_data["data"]["concepts"]:
            tid = group.get("id")
            
            # Base info
            base_info = ssyk_map.get(tid)
            if not base_info:
                continue
            
            ssyk_code = base_info["ssyk_code"]
                
            # Extract Skills
            skills = [
                item["preferred_label"] 
                for item in group.get("related", []) 
                if item.get("type") == "skill"
            ]
            
            # Extract Occupations from Skills file (as fallback or supplement)
            occupations_from_skills = [
                item["preferred_label"]
                for item in group.get("narrower", [])
                if item.get("type") == "occupation-name"
            ]
            
            # Get Occupations from Hierarchy (Official List)
            occupations_from_hierarchy = hierarchy_occupations_map.get(ssyk_code, [])
            
            # Combine unique occupations
            all_occupations = list(set(occupations_from_skills + occupations_from_hierarchy))
            
            record = base_info.copy()
            record["skills"] = skills
            record["related_occupations"] = all_occupations
            records.append(record)
            
        df = pd.DataFrame(records)
        logger.info(f"Processed {len(df)} enriched SSYK records")
        
        return df

    def save_processed(self, df: pd.DataFrame, output_dir: Path) -> Path:
        output_path = output_dir / "taxonomy_enriched.parquet"
        
        # Ensure list columns are handled correctly for Parquet
        # PyArrow handles lists fine, but let's be explicit if needed.
        # Actually pandas to_parquet handles basic lists.
        
        df.to_parquet(output_path, index=False)
        logger.info(f"Saved enriched taxonomy to {output_path}")
        return output_path
