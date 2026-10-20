from contextlib import asynccontextmanager
from fastapi import FastAPI
from winerecommender.adapters.extractor_model import ExtractorModel
from winerecommender.services.extractor import ExtractorService

from src.winerecommender.adapters.db import PostgresAdapter
from src.winerecommender.adapters.embedding_model import EmbeddingModel
from src.winerecommender.configs.setting import DB_URL, EMBEDDING_MODEL, EXTRACTOR_MODEL
from src.winerecommender.services.recommender import RecommenderService
from winerecommender.routers import health, recommender

@asynccontextmanager
async def lifespan(app: FastAPI):
    embedding_model = EmbeddingModel(EMBEDDING_MODEL)
    extractor_model = ExtractorModel(EXTRACTOR_MODEL)
    db_adapter = PostgresAdapter(DB_URL)
    
    app.state.extractor = ExtractorService(
        extractor_model=extractor_model
    )

    app.state.recommender = RecommenderService(
        db_adapter=db_adapter,
        embedding_model=embedding_model,
        db_url=DB_URL,
        extractor_service=app.state.extractor
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
