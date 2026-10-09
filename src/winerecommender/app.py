from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.winerecommender.adapters.db import PostgresAdapter
from src.winerecommender.adapters.embedding_model import EmbeddingModel
from src.winerecommender.configs.setting import DB_URL, EMBEDDING_MODEL
from src.winerecommender.services.recommender import RecommenderService
from winerecommender.routers import health, recommender

@asynccontextmanager
async def lifespan(app: FastAPI):
    embedding_model = EmbeddingModel(EMBEDDING_MODEL)
    db_adapter = PostgresAdapter(DB_URL)

    app.state.recommender = RecommenderService(
        db_adapter=db_adapter,
        embedding_model=embedding_model,
        db_url=DB_URL,
    )

    yield

app = FastAPI(
    title="Wine Recommender API",
    description="A semantic wine recommendation service",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(recommender.router)
