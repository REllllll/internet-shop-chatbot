from app import db


def test_search_returns_match(test_db):
    results = db.search_products("lightning cable")
    assert any(r["product_id"] == "B001" for r in results)


def test_search_returns_empty_for_no_match(test_db):
    assert db.search_products("nonexistent_xyz_123") == []


def test_search_handles_hyphenated_terms(test_db):
    results = db.search_products("USB-C cable")
    assert any(r["product_id"] == "B002" for r in results)


def test_filter_by_category(test_db):
    results = db.filter_products(category="Computers&Accessories")
    assert len(results) == 2
    assert all("Computers&Accessories" in r["category"] for r in results)


def test_filter_by_max_price(test_db):
    results = db.filter_products(max_price=300.0)
    assert all(r["discounted_price"] <= 300.0 for r in results)
    assert len(results) == 1  # Only B002 at 199.0


def test_filter_by_min_rating(test_db):
    results = db.filter_products(min_rating=4.3)
    assert len(results) == 1
    assert results[0]["product_id"] == "B003"


def test_filter_by_keywords(test_db):
    results = db.filter_products(keywords=["speaker"])
    assert len(results) == 1
    assert results[0]["product_id"] == "B003"


def test_filter_combined(test_db):
    results = db.filter_products(category="Computers&Accessories", max_price=250.0)
    assert len(results) == 1
    assert results[0]["product_id"] == "B002"
