import httpx
import json

url = "https://jobad-enrichments-api.jobtechdev.se/enrichtextdocumentsbinary"

def test_payload(payload, name):
    print(f"Testing {name}...")
    try:
        response = httpx.post(url, json=payload, headers={"Content-Type": "application/json"})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
            print(response.json())
        else:
            print(f"Error: {response.text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 20)

# 1. Matches my current code
payload1 = {
    "documents_input": [
        {"doc_id": "1", "text": "Vi söker en duktig Python utvecklare med erfarenhet av data science."}
    ],
    "include_terms_info": True
}

# 2. Try doc_id instead of id
payload2 = {
    "documents_input": [
        {"doc_id": "1", "text": "Vi söker en duktig Python utvecklare med erfarenhet av data science."}
    ],
    "include_terms_info": True
}

# 3. Correct doc_id implementation?
# The error was 422. Maybe the field name is just 'documents'?

payload3 = {
    "documents": [
        {"doc_id": "1", "text": "Vi söker en duktig Python utvecklare med erfarenhet av data science."}
    ], 
    "include_terms_info": True
}

test_payload(payload1, "Current impl (with doc_id?) No wait, current used id")

payload_current = {
    "documents_input": [
        {"id": "1", "text": "Vi söker en duktig Python utvecklare med erfarenhet av data science."}
    ],
    "include_terms_info": True
}
test_payload(payload_current, "Actually Current implementation (id)")

test_payload(payload2, "With doc_id")
payload5 = {
    "documents_input": [
        {"doc_id": "1", "doc_text": "Vi söker en duktig Python utvecklare med erfarenhet av data science."}
    ],
    "include_terms_info": True
}

test_payload(payload5, "With doc_id and doc_text")
