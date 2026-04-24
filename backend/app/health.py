import os
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    database_path = os.getenv("DATABASE_PATH", str(Path(__file__).parents[2] / "data" / "products.db"))
    return {
        "status": "ok",
        "database_path": database_path,
    }
