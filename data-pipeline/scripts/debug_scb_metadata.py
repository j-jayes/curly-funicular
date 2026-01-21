
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from data_pipeline.ingestion.scb_ingestion import SCBIngestion
import json

def fetch_metadata():
    client = SCBIngestion()
    meta = client.get_table_metadata()
    print(json.dumps(meta, indent=2))

if __name__ == "__main__":
    fetch_metadata()
