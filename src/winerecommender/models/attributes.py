from pydantic import BaseModel


class WineAttribute(BaseModel):
    source_id: int
    title: str | None = None
    description: str | None = None
    region: str | None = None
    country: str | None = None
    designation: str | None = None
    points: int | None = None
    price: float | None = None
    variety: str | None = None
    winery: str | None = None
    distance: float | None = None
