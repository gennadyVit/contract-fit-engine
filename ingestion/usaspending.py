import os
import time
from dotenv import load_dotenv

from snowflake_conn import get_connection
import requests

load_dotenv()

BASE_URL = "https://api.usaspending.gov/api/v2"

FIELDS = [
    "Award ID",
    "Recipient Name",
    "Award Amount",
    "Description",
    "Start Date",
    "End Date",
    "Awarding Agency",
    "Awarding Sub Agency",
    "Contract Award Type",
    "Place of Performance Country Code",
    "Place of Performance State Code",
]

ALL_MARKET_CAP = 7000
SMALL_BUSINESS_CAP = 7000
PER_PAGE = 100



def fetch_pull(total_cap: int, small_business_only: bool) -> list[dict]:
    url = f"{BASE_URL}/search/spending_by_award/"
    records = []
    page = 1
    label = "small-business" if small_business_only else "all-market"

    print(f"  [{label}] Fetching up to {total_cap} records (2024-2025, all NAICS)...")
    while len(records) < total_cap:
        filters = {
            "award_type_codes": ["A", "B", "C", "D"],
            "time_period": [{"start_date": "2024-01-01", "end_date": "2025-12-31"}],
        }
        if small_business_only:
            filters["recipient_type_names"] = ["small_business"]

        payload = {
            "filters": filters,
            "fields": FIELDS,
            "sort": "Start Date",
            "order": "desc",
            "limit": PER_PAGE,
            "page": page,
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if not results:
            break

        records.extend(results)

        if not data.get("page_metadata", {}).get("hasNext"):
            break

        page += 1
        time.sleep(0.2)

    print(f"    Got {len(records)} records")
    return records[:total_cap]


def fetch_all_awards() -> list[dict]:
    all_market = fetch_pull(ALL_MARKET_CAP, small_business_only=False)
    small_business = fetch_pull(SMALL_BUSINESS_CAP, small_business_only=True)

    merged = {}

    for r in all_market:
        key = r.get("internal_id")
        merged[key] = r
        merged[key]["_source_all_market_pull"] = True
        merged[key]["_source_small_business_pull"] = False

    for r in small_business:
        key = r.get("internal_id")
        if key in merged:
            merged[key]["_source_small_business_pull"] = True
        else:
            r["_source_all_market_pull"] = False
            r["_source_small_business_pull"] = True
            merged[key] = r

    return list(merged.values())


def load_to_snowflake(records, cursor):
    rows = []
    for r in records:
        source_sb = r.get("_source_small_business_pull", False)
        rows.append((
            r.get("Award ID"),
            str(r.get("internal_id")),
            r.get("Recipient Name"),
            r.get("Award Amount"),
            r.get("Description"),
            r.get("Start Date"),
            r.get("End Date"),
            r.get("Awarding Agency"),
            r.get("Awarding Sub Agency"),
            r.get("Contract Award Type"),
            None,  # NAICS_CODE not returned by bulk search endpoint
            r.get("Place of Performance Country Code"),
            r.get("Place of Performance State Code"),
            True if source_sb else None,  # tri-state: True if confirmed SB, else unknown (NULL)
            r.get("_source_all_market_pull", False),
            source_sb,
        ))

    cursor.executemany("""
        INSERT INTO GOVCONTRACT.RAW.STG_USASPENDING_AWARDS (
            AWARD_ID, INTERNAL_ID, RECIPIENT_NAME, AWARD_AMOUNT, DESCRIPTION,
            START_DATE, END_DATE, AWARDING_AGENCY, AWARDING_SUB_AGENCY,
            AWARD_TYPE, NAICS_CODE, POP_COUNTRY_CODE, POP_STATE_CODE,
            IS_SMALL_BUSINESS_AWARD, SOURCE_ALL_MARKET_PULL, SOURCE_SMALL_BUSINESS_PULL
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, rows)
    return len(rows)


if __name__ == "__main__":
    print(f"Fetching USASpending awards (all NAICS, 2024-2025)...")
    print(f"  All-market pull cap: {ALL_MARKET_CAP}, Small-business pull cap: {SMALL_BUSINESS_CAP}")
    records = fetch_all_awards()
    sb_count = sum(1 for r in records if r.get("_source_small_business_pull"))
    print(f"Fetched {len(records)} unique records after dedup ({sb_count} confirmed small-business)")

    print("Connecting to Snowflake...")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"USE WAREHOUSE {os.getenv('SNOWFLAKE_WAREHOUSE')}")


    print("Loading records into Snowflake...")
    count = load_to_snowflake(records, cursor)
    conn.commit()
    conn.close()

    print(f"Done! {count} records loaded into GOVCONTRACT.RAW.STG_USASPENDING_AWARDS")
    print("Query it in Snowflake: SELECT * FROM GOVCONTRACT.RAW.STG_USASPENDING_AWARDS LIMIT 20;")
