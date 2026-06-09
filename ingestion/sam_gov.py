import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SAM_GOV_API_KEY")
BASE_URL = "https://api.sam.gov/opportunities/v2/search"


def fetch_opportunities(keyword: str, limit: int = 100) -> list[dict]:
    params = {
        "api_key": API_KEY,
        "q": keyword,
        "limit": limit,
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json().get("opportunitiesData", [])


if __name__ == "__main__":
    results = fetch_opportunities("software")
    print(f"Fetched {len(results)} opportunities")
