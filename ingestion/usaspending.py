import requests

BASE_URL = "https://api.usaspending.gov/api/v2"


def fetch_awards(keyword: str, limit: int = 100) -> list[dict]:
    url = f"{BASE_URL}/search/spending_by_award/"
    payload = {
        "filters": {
            "keywords": [keyword],
            "award_type_codes": ["A", "B", "C", "D"],
        },
        "fields": ["Award ID", "Recipient Name", "Award Amount", "Description"],
        "limit": limit,
        "page": 1,
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json().get("results", [])


if __name__ == "__main__":
    results = fetch_awards("software")
    print(f"Fetched {len(results)} awards")
