
import requests
import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "raw" / "taxonomy"
DATA_DIR.mkdir(parents=True, exist_ok=True)

URLS = {
    "all_concepts": "https://data.arbetsformedlingen.se/taxonomy/version/27/query/all-concepts/all-concepts.json",
    "ssyk4_skills": "https://data.arbetsformedlingen.se/taxonomy/version/27/query/ssyk-level-4-with-related-skills-and-occupations/ssyk-level-4-with-related-skills-and-occupations.json",
    "occupation_fields": "https://data.arbetsformedlingen.se/taxonomy/version/27/query/occupation-fields-with-related-ssyk-level-4-groups-and-occupations/occupation-fields-with-related-ssyk-level-4-groups-and-occupations.json"
}

def peek_json(data, name):
    print(f"\n{'='*20} {name} {'='*20}")
    if isinstance(data, list):
        print(f"Type: List, Length: {len(data)}")
        if len(data) > 0:
            print("First item sample:")
            print(json.dumps(data[0], indent=2)[:500] + "...")
    elif isinstance(data, dict):
        print(f"Type: Dict, Keys: {list(data.keys())}")
        for k, v in data.items():
            if isinstance(v, list):
                print(f"Key '{k}' is a list of length {len(v)}")
                if len(v) > 0:
                    print(f"Sample item from '{k}':")
                    print(json.dumps(v[0], indent=2)[:500] + "...")
            else:
                print(f"Key '{k}': {str(v)[:100]}")
    else:
        print(f"Type: {type(data)}")

def main():
    for name, url in URLS.items():
        print(f"Fetching {name}...")
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            data = resp.json()
            
            # Save to file
            filepath = DATA_DIR / f"{name}.json"
            with open(filepath, "w") as f:
                json.dump(data, f)
            
            peek_json(data, name)
            
        except Exception as e:
            print(f"Error fetching {name}: {e}")

if __name__ == "__main__":
    main()
