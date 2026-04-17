import sqlite3
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("DATABASE_PATH", db_path)

    conn = sqlite3.connect(db_path)
    conn.executescript("""
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
        INSERT INTO products VALUES
            ('B001','USB Cable Lightning','Computers&Accessories|Cables',399.0,1099.0,64.0,4.2,24269,'Fast charging lightning cable','','https://amazon.in/B001'),
            ('B002','USB-C Cable Android','Computers&Accessories|Cables',199.0,349.0,43.0,4.0,43994,'Nylon braided USB-C charging cable','','https://amazon.in/B002'),
            ('B003','Bluetooth Speaker','Electronics|Audio',1299.0,2499.0,48.0,4.5,8000,'Portable wireless speaker','','https://amazon.in/B003');
        INSERT INTO products_fts(product_id, product_name, about_product)
            SELECT product_id, product_name, about_product FROM products;
    """)
    conn.commit()
    conn.close()
    return db_path
