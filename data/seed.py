import csv
import re
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "products.db"
CSV_PATH = Path(__file__).parent / "raw" / "amazon.csv"


def _price(v: str) -> float | None:
    try:
        return float(re.sub(r"[₹,\s]", "", v))
    except (ValueError, AttributeError):
        return None


def _float(v: str) -> float | None:
    try:
        return float(re.sub(r"[%,\s]", "", v))
    except (ValueError, AttributeError):
        return None


def _int(v: str) -> int | None:
    try:
        return int(re.sub(r"[,\s]", "", v))
    except (ValueError, AttributeError):
        return None


def seed():
    if not CSV_PATH.exists():
        print(
            f"ERROR: {CSV_PATH} not found.\n"
            "Download from https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset",
            file=sys.stderr,
        )
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        DROP TABLE IF EXISTS products_fts;
        DROP TABLE IF EXISTS products;
        CREATE TABLE products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT,
            discounted_price REAL,
            actual_price REAL,
            discount_percentage REAL,
            rating REAL,
            rating_count INTEGER,
            about_product TEXT,
            img_link TEXT,
            product_link TEXT
        );
        CREATE VIRTUAL TABLE products_fts USING fts5(
            product_id UNINDEXED,
            product_name,
            about_product,
            content='products',
            content_rowid='rowid'
        );
    """)

    seen, rows = set(), []
    with open(CSV_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pid = row["product_id"].strip()
            if pid in seen:
                continue
            seen.add(pid)
            rows.append((
                pid,
                row["product_name"].strip(),
                row["category"].strip(),
                _price(row["discounted_price"]),
                _price(row["actual_price"]),
                _float(row["discount_percentage"]),
                _float(row["rating"]),
                _int(row["rating_count"]),
                row["about_product"].strip(),
                row["img_link"].strip(),
                row["product_link"].strip(),
            ))

    conn.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?)", rows)
    conn.execute("""
        INSERT INTO products_fts(product_id, product_name, about_product)
        SELECT product_id, product_name, about_product FROM products
    """)
    conn.commit()
    conn.close()
    print(f"Seeded {len(rows)} products into {DB_PATH}")


if __name__ == "__main__":
    seed()
