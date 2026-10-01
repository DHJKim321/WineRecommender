from pydantic import BaseModel, PositiveFloat, PositiveInt

class WineAttribute(BaseModel):
    id: int
    title: str
    description: str
    region: str
    designation: str
    country: str
    variety: str
    winery: str
    price: PositiveFloat
    points: PositiveInt
