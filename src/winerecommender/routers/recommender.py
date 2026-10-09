from fastapi import Request, APIRouter

from src.winerecommender.models.requests import RecommendationRequest, EncodeQueryRequest

router = APIRouter(prefix="/recommender", tags=["recommender"])

@router.post("/recommend")
def recommend(
        body: RecommendationRequest,
        request: Request
    ):
    service = request.app.state.recommender
    recommendations = service.recommend_wines(body.query, body.limit)
    return {
        "query": body.query,
        "recommendations": recommendations,
    }

@router.post("/encode")
def encode_query(
        body: EncodeQueryRequest,
        request: Request
        ):
    service = request.app.state.recommender
    embedding = service.encode(body.query)
    return {
        "embedding": embedding
    }
