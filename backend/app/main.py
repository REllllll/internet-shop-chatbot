import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_path = os.getenv("DATABASE_PATH", str(Path(__file__).parents[2] / "data" / "products.db"))
    if not Path(db_path).exists():
        raise RuntimeError(
            f"Database not found at {db_path}\n"
            "Run: python data/seed.py"
        )
    yield


app = FastAPI(title="ShopBot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .internal import router as internal_router  # noqa: E402
from .chat import router as chat_router          # noqa: E402

app.include_router(internal_router)
app.include_router(chat_router)
