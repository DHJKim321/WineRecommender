from pydantic import BaseModel, ConfigDict


class WineAttribute(BaseModel):
    source_id: int
    title: str
    description: str
    region: str
    country: str
    designation: str
    points: int
    price: float
    variety: str
    winery: str
    
class WineEmbedding(WineAttribute):
    source_id: int
    embedding_config = ConfigDict(arbitrary_types_allowed=True)
    embedding: list[float]
    distance: float