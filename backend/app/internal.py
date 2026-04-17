from fastapi import APIRouter, Query
from pydantic import BaseModel
from . import db

router = APIRouter(prefix="/internal")


class ProductSearchRequest(BaseModel):
    query: str | None = None
    category: str | None = None
    budget: float | None = None


@router.get("/products")
def get_products(
    category: str | None = Query(None),
    max_price: float | None = Query(None),
    min_rating: float | None = Query(None),
    keywords: str | None = Query(default=None),  # comma-separated, e.g. "cable,nylon"
    limit: int = Query(50, le=100),
) -> list[dict]:
    kw_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else None
    return db.filter_products(
        category=category,
        max_price=max_price,
        min_rating=min_rating,
        keywords=kw_list,
        limit=limit,
    )


@router.post("/products/search")
def search_products(request: ProductSearchRequest) -> list[dict]:
    """Search products for n8n workflow integration."""
    keywords = [request.query] if request.query else None
    return db.filter_products(
        category=request.category,
        max_price=request.budget,
        keywords=keywords,
        limit=5,
    )
