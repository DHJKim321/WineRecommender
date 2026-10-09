from pydantic import BaseModel, Field

from winerecommender.configs.setting import TOP_N

class EncodeQueryRequest(BaseModel):
    query: str = Field(
        min_length=1,
        description="Natural-language wine preferences",
    )
    
class RecommendationRequest(EncodeQueryRequest):
    limit: int = Field(default=TOP_N, ge=1, le=50, description="Maximum number of recommendations")#
