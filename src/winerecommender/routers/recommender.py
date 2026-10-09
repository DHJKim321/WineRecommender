from fastapi import APIRouter
from pydantic import BaseModel, Field

from configs.setting import TOP_N
from services.recommender import recommend_wines, encode

router = APIRouter(tags=["recommender"])

class RecommendationRequest(BaseModel):
    query: str = Field(
        min_length=1,
        description="Natural-language wine preferences",
    )
    limit: int = Field(default=TOP_N, ge=1,)


@router.post("/")
def recommend(request: RecommendationRequest):
    recommendations = recommend_wines(request.query, request.limit)
    if recommendations == []:
        recommendations = "Could not find any relevant wines"
    return {
        "query": request.query,
        "recommendations": recommendations,
    }
    
@router.post("/encode")
def encode_query(request: RecommendationRequest):
    embedding = encode(request.query)
    return {
        "embedding": embedding
    }
