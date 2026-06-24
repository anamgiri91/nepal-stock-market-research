"""
Scrape NEPSE Index History Data from ShareSansar.com
Uses curl subprocess for reliable HTTP requests.
Date range: 2010-01-01 to 2026-06-12
Output: nepse_index_history.csv
"""

import subprocess
import json
import csv
import time

API_URL = "https://www.sharesansar.com/index-history-data"
INDEX_ID = 12   # NEPSE Index
FROM_DATE = "2010-01-01"
TO_DATE = "2026-06-12"
PAGE_SIZE = 50  # Server max is 50
OUTPUT_FILE = "nepse_index_history.csv"


def fetch_page(start, length, draw=1):
    """Fetch a page of data using curl."""
    url = (
        f"{API_URL}?index_id={INDEX_ID}"
        f"&from={FROM_DATE}&to={TO_DATE}"
        f"&draw={draw}&start={start}&length={length}"
    )
    result = subprocess.run(
        ["curl", "-s", url,
         "-H", "X-Requested-With: XMLHttpRequest",
         "-H", "Accept: application/json",
         "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"],
        capture_output=True, text=True, timeout=60
    )
    return json.loads(result.stdout)


def main():
    print(f"Scraping NEPSE Index data: {FROM_DATE} → {TO_DATE}")
    print(f"Output: {OUTPUT_FILE}")
    print("-" * 60)

    # First request — get total count
    first = fetch_page(0, PAGE_SIZE, draw=1)
    total = first["recordsTotal"]
    all_data = list(first["data"])
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    print(f"Total: {total} records ({total_pages} pages of {PAGE_SIZE})")
    print(f"  Page 1/{total_pages}: {len(all_data)} records", flush=True)

    # Paginate through remaining records
    offset = len(all_data)
    page = 2
    while offset < total:
        time.sleep(0.3)
        result = fetch_page(offset, PAGE_SIZE, draw=page)
        batch = result.get("data", [])
        if not batch:
            print(f"  Page {page}/{total_pages}: empty, stopping")
            break
        all_data.extend(batch)
        if page % 10 == 0 or page == total_pages:
            print(f"  Page {page}/{total_pages}: {len(all_data)}/{total} records", flush=True)
        offset += len(batch)
        page += 1

    # Sort by date ascending
    all_data.sort(key=lambda x: x["published_date"])

    # Deduplicate by date
    seen = set()
    unique = []
    for row in all_data:
        d = row["published_date"]
        if d not in seen:
            seen.add(d)
            unique.append(row)

    # Write CSV
    fields = ["Date", "Open", "High", "Low", "Close", "Change", "Percent_Change", "Turnover"]
    with open(OUTPUT_FILE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in unique:
            w.writerow({
                "Date": r["published_date"],
                "Open": r["open"],
                "High": r["high"],
                "Low": r["low"],
                "Close": r["current"],
                "Change": r["change_"],
                "Percent_Change": r["per_change"],
                "Turnover": r["turnover"],
            })

    print("-" * 60)
    print(f"✅ {len(unique)} records saved to {OUTPUT_FILE}")
    if unique:
        print(f"   Range: {unique[0]['published_date']} → {unique[-1]['published_date']}")


if __name__ == "__main__":
    main()
