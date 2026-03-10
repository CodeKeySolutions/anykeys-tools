import json
import sqlite3
import re
import time
from datetime import datetime
from urllib.parse import urlparse
from typing import Optional
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class PriceRecord:
    item_name: str
    vendor: str
    url: str
    price: Optional[float]
    currency: str
    scraped_at: str


class PriceTracker:
    def __init__(self, db_path: str = "prices.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                vendor TEXT NOT NULL,
                url TEXT NOT NULL,
                price REAL,
                currency TEXT DEFAULT 'USD',
                scraped_at TEXT NOT NULL,
                UNIQUE(item_name, vendor, url, price, scraped_at)
            )
        """)
        conn.commit()
        conn.close()

    def add_price(self, record: PriceRecord):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO price_history (item_name, vendor, url, price, currency, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (record.item_name, record.vendor, record.url, record.price, 
                  record.currency, record.scraped_at))
            conn.commit()
            result = True
        except sqlite3.IntegrityError:
            result = False
        conn.close()
        return result

    def is_duplicate(self, item_name: str, vendor: str, url: str, price: Optional[float]) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM price_history 
            WHERE item_name = ? AND vendor = ? AND url = ? AND price = ?
            LIMIT 1
        """, (item_name, vendor, url, price))
        result = cursor.fetchone() is not None
        conn.close()
        return result

    def get_price_history(self, item_name: Optional[str] = None, limit: int = 10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if item_name:
            cursor.execute("""
                SELECT * FROM price_history 
                WHERE item_name = ? 
                ORDER BY scraped_at DESC 
                LIMIT ?
            """, (item_name, limit))
        else:
            cursor.execute("""
                SELECT * FROM price_history 
                ORDER BY scraped_at DESC 
                LIMIT ?
            """, (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

    def get_latest_prices(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT item_name, vendor, url, price, currency, MAX(scraped_at) as latest
            FROM price_history
            GROUP BY item_name, vendor
        """)
        results = cursor.fetchall()
        conn.close()
        return results


class PriceScraper:
    def __init__(self, items_config: list, tracker: PriceTracker, headers: Optional[dict] = None):
        self.items = items_config
        self.tracker = tracker
        self.session = requests.Session()
        self.session.headers.update(headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def extract_price(self, soup: BeautifulSoup, selectors: dict) -> tuple:
        price = None
        currency = "USD"

        price_selector = selectors.get("price")
        if price_selector:
            price_elem = soup.select_one(price_selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price, currency = self._parse_price(price_text)

        title = None
        title_selector = selectors.get("title")
        if title_selector:
            title_elem = soup.select_one(title_selector)
            if title_elem:
                title = title_elem.get_text(strip=True)

        return price, currency, title

    def _parse_price(self, price_text: str) -> tuple:
        price_patterns = [
            r"[\$\£\€]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
            r"(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*[\$\£\€]",
        ]

        for pattern in price_patterns:
            match = re.search(pattern, price_text)
            if match:
                price_str = match.group(1).replace(",", "")
                currency = "USD"
                try:
                    price = float(price_str)
                    if "$" in price_text or "USD" in price_text.upper():
                        currency = "USD"
                    elif "£" in price_text or "GBP" in price_text.upper():
                        currency = "GBP"
                    elif "€" in price_text or "EUR" in price_text.upper():
                        currency = "EUR"
                    return price, currency
                except ValueError:
                    continue
        return None, "USD"

    def scrape_item(self, item: dict, delay: float = 1.0) -> list:
        results = []
        url = item.get("url")
        name = item.get("name")
        selectors = item.get("selectors", {})

        if not url:
            return results

        vendor = self._extract_vendor(url)

        try:
            time.sleep(delay)
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            price, currency, title = self.extract_price(soup, selectors)

            record = PriceRecord(
                item_name=title or name or "Unknown",
                vendor=vendor,
                url=url,
                price=price,
                currency=currency,
                scraped_at=datetime.now().isoformat()
            )

            is_dup = self.tracker.is_duplicate(record.item_name, record.vendor, record.url, record.price)
            saved = self.tracker.add_price(record)

            results.append({
                "item": name,
                "title": record.item_name,
                "vendor": vendor,
                "url": url,
                "price": price,
                "currency": currency,
                "scraped_at": record.scraped_at,
                "is_duplicate": is_dup,
                "saved": saved
            })

        except Exception as e:
            results.append({
                "item": name,
                "url": url,
                "error": str(e)
            })

        return results

    def _extract_vendor(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed.netloc.replace("www.", "")

    def scrape_all(self, delay: float = 1.0) -> list:
        all_results = []
        for item in self.items:
            results = self.scrape_item(item, delay)
            all_results.extend(results)
        return all_results


def load_items(config_path: str = "items.json") -> list:
    with open(config_path, "r") as f:
        config = json.load(f)
    return config.get("items", [])


def print_results(results: list):
    print("\n" + "=" * 60)
    print("SCRAPING RESULTS")
    print("=" * 60)

    for r in results:
        if "error" in r:
            print(f"\n❌ {r['item']}: {r['error']}")
            continue

        status = "✓ NEW" if r.get("saved") else "⚠ DUPLICATE"
        price_str = f"{r['currency']} {r['price']}" if r.get("price") else "N/A"
        print(f"\n{status} | {r['item']}")
        print(f"   Title: {r.get('title', 'N/A')}")
        print(f"   Vendor: {r.get('vendor')}")
        print(f"   Price: {price_str}")
        print(f"   URL: {r['url']}")

    print("\n" + "=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Price Scraping Tool")
    parser.add_argument("-c", "--config", default="items.json", help="Config file path")
    parser.add_argument("-d", "--delay", type=float, default=1.0, help="Delay between requests")
    parser.add_argument("--history", action="store_true", help="Show price history")
    parser.add_argument("--latest", action="store_true", help="Show latest prices")
    args = parser.parse_args()

    tracker = PriceTracker()

    if args.history:
        print("\nPrice History:")
        for row in tracker.get_price_history(limit=20):
            print(f"  {row}")
        return

    if args.latest:
        print("\nLatest Prices:")
        for row in tracker.get_latest_prices():
            print(f"  {row[0]} | {row[1]} | {row[3]} {row[4]}")
        return

    items = load_items(args.config)
    print(f"Loaded {len(items)} items to track")

    scraper = PriceScraper(items, tracker)
    results = scraper.scrape_all(delay=args.delay)

    print_results(results)

    new_count = sum(1 for r in results if r.get("saved"))
    dup_count = sum(1 for r in results if r.get("is_duplicate"))
    print(f"\nSummary: {new_count} new prices, {dup_count} duplicates")


if __name__ == "__main__":
    main()
