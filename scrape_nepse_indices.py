#!/usr/bin/env python3
"""Scrape datewise NEPSE index data from merolagani.com.

Default range:
    2015-01-01 through 2025-06-03

The merolagani Indices page is ASP.NET WebForms. Its date search can be brittle
when called outside the browser, so this scraper pages through the default
newest-to-oldest NEPSE table and filters the requested date range locally.
"""

from __future__ import annotations

import argparse
import csv
import html
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from pathlib import Path


BASE_URL = "https://merolagani.com/Indices.aspx"
INDEX_FIELD = "ctl00$ContentPlaceHolder1$ddlIndexFilter"
PAGER_CURRENT_FIELD = "ctl00$ContentPlaceHolder1$PagerControl1$hdnCurrentPage"
PAGER_BUTTON_FIELD = "ctl00$ContentPlaceHolder1$PagerControl1$btnPaging"


@dataclass(frozen=True)
class IndexRow:
    date_ad: date
    index_value: float
    absolute_change: float
    percentage_change: float


class MerolaganiParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.inputs: dict[str, str] = {}
        self.selects: dict[str, str] = {}
        self._current_select: str | None = None
        self._selected_option_value: str | None = None
        self._in_table = False
        self._in_tbody = False
        self._in_row = False
        self._in_cell = False
        self._cell_parts: list[str] = []
        self._row: list[str] = []
        self.rows: list[list[str]] = []
        self.total_pages: int = 1

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {k: v or "" for k, v in attrs}

        if tag == "input" and attr.get("name"):
            self.inputs[attr["name"]] = html.unescape(attr.get("value", ""))

        if tag == "select" and attr.get("name"):
            self._current_select = attr["name"]
            self._selected_option_value = None

        if tag == "option" and self._current_select and "selected" in attr:
            self._selected_option_value = attr.get("value", "")

        if tag == "table":
            classes = attr.get("class", "")
            if "sortable" in classes and "table" in classes:
                self._in_table = True

        if self._in_table and tag == "tbody":
            self._in_tbody = True

        if self._in_tbody and tag == "tr":
            self._in_row = True
            self._row = []

        if self._in_row and tag == "td":
            self._in_cell = True
            self._cell_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "select" and self._current_select:
            if self._selected_option_value is not None:
                self.selects[self._current_select] = self._selected_option_value
            self._current_select = None
            self._selected_option_value = None

        if self._in_cell and tag == "td":
            text = " ".join("".join(self._cell_parts).split())
            self._row.append(text)
            self._in_cell = False
            self._cell_parts = []

        if self._in_row and tag == "tr":
            if len(self._row) >= 5:
                self.rows.append(self._row[:5])
            self._in_row = False
            self._row = []

        if self._in_tbody and tag == "tbody":
            self._in_tbody = False

        if self._in_table and tag == "table":
            self._in_table = False

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell_parts.append(data)

        match = re.search(r"Total pages:\s*(\d+)", data)
        if match:
            self.total_pages = int(match.group(1))


def parse_page(body: str) -> MerolaganiParser:
    parser = MerolaganiParser()
    parser.feed(body)
    return parser


def parse_float(value: str) -> float:
    cleaned = value.replace(",", "").replace("%", "").strip()
    return float(cleaned)


def parse_rows(raw_rows: list[list[str]]) -> list[IndexRow]:
    parsed: list[IndexRow] = []
    for row in raw_rows:
        try:
            parsed.append(
                IndexRow(
                    date_ad=datetime.strptime(row[1], "%Y/%m/%d").date(),
                    index_value=parse_float(row[2]),
                    absolute_change=parse_float(row[3]),
                    percentage_change=parse_float(row[4]),
                )
            )
        except (ValueError, IndexError):
            continue
    return parsed


def make_opener() -> urllib.request.OpenerDirector:
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    opener.addheaders = [
        ("User-Agent", "Mozilla/5.0 (compatible; NEPSEIndexResearchScraper/1.0)"),
        ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
    ]
    return opener


def request_text(
    opener: urllib.request.OpenerDirector,
    data: dict[str, str] | None = None,
) -> str:
    encoded = None
    if data is not None:
        encoded = urllib.parse.urlencode(data).encode("utf-8")
    request = urllib.request.Request(BASE_URL, data=encoded, method="POST" if data else "GET")
    with opener.open(request, timeout=60) as response:
        return response.read().decode("utf-8", errors="replace")


def build_pager_form(parser: MerolaganiParser) -> dict[str, str]:
    hidden_names = {
        "__VIEWSTATE",
        "__VIEWSTATEGENERATOR",
        "__EVENTVALIDATION",
        "ctl00$ContentPlaceHolder1$PagerControl1$hdnPCID",
        "ctl00$ContentPlaceHolder1$PagerControl2$hdnPCID",
    }
    form = {
        name: value
        for name, value in parser.inputs.items()
        if name in hidden_names
    }
    form["__EVENTTARGET"] = ""
    form["__EVENTARGUMENT"] = ""
    form[INDEX_FIELD] = "58"
    return form


def fetch_page(
    opener: urllib.request.OpenerDirector,
    current: MerolaganiParser,
    page_number: int,
) -> MerolaganiParser:
    form = build_pager_form(current)
    form[PAGER_CURRENT_FIELD] = str(page_number)
    form[PAGER_BUTTON_FIELD] = ""
    return parse_page(request_text(opener, form))


def scrape(start_date: date, end_date: date, delay: float) -> list[IndexRow]:
    opener = make_opener()
    page = parse_page(request_text(opener))
    rows = [
        row
        for row in parse_rows(page.rows)
        if start_date <= row.date_ad <= end_date
    ]
    total_pages = page.total_pages
    print(f"Page 1/{total_pages}: {len(page.rows)} raw rows, {len(rows)} kept")

    for page_number in range(2, total_pages + 1):
        time.sleep(delay)
        page = fetch_page(opener, page, page_number)
        page_rows = parse_rows(page.rows)
        kept_rows = [
            row
            for row in page_rows
            if start_date <= row.date_ad <= end_date
        ]
        rows.extend(kept_rows)
        print(f"Page {page_number}/{total_pages}: {len(page_rows)} raw rows, {len(kept_rows)} kept")

        if page_rows and min(row.date_ad for row in page_rows) < start_date:
            break

    deduped = {row.date_ad: row for row in rows}
    filtered = [
        row
        for row in deduped.values()
        if start_date <= row.date_ad <= end_date
    ]
    return sorted(filtered, key=lambda row: row.date_ad)


def write_csv(rows: list[IndexRow], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "date_ad",
                "index_value",
                "absolute_change",
                "percentage_change",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "date_ad": row.date_ad.isoformat(),
                    "index_value": f"{row.index_value:.2f}",
                    "absolute_change": f"{row.absolute_change:.2f}",
                    "percentage_change": f"{row.percentage_change:.2f}",
                }
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape NEPSE index history from merolagani.com")
    parser.add_argument("--start", default="2015-01-01", help="Start date in YYYY-MM-DD")
    parser.add_argument("--end", default="2025-06-03", help="End date in YYYY-MM-DD")
    parser.add_argument("--delay", type=float, default=0.4, help="Seconds to pause between pages")
    parser.add_argument(
        "--output",
        default="nepse_index_2015-01-01_to_2025-06-03.csv",
        help="CSV output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start_date = date.fromisoformat(args.start)
    end_date = date.fromisoformat(args.end)
    if start_date > end_date:
        raise SystemExit("--start must be on or before --end")

    rows = scrape(start_date, end_date, args.delay)
    output = Path(args.output)
    write_csv(rows, output)

    if rows:
        print(f"Wrote {len(rows)} rows to {output}")
        print(f"Date range in CSV: {rows[0].date_ad} to {rows[-1].date_ad}")
    else:
        print(f"Wrote 0 rows to {output}")


if __name__ == "__main__":
    main()
