from fastapi import FastAPI

from winerecommender.routers import health, recommender

app = FastAPI(
    title="Wine Recommender API",
    description="A semantic wine recommendation service",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(recommender.router)