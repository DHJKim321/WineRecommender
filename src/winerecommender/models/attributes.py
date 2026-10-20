from pydantic import BaseModel, ConfigDict, Field


class WineAttribute(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
    
class NumericRange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min: float | None = None
    max: float | None = None

class PointsRange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min: int | None = None
    max: int | None = None

class WineQueryFilter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    region: list[str] = Field(default_factory=list)
    country: list[str] = Field(default_factory=list)
    designation: list[str] = Field(default_factory=list)
    points: PointsRange
    price: NumericRange
    variety: list[str] = Field(default_factory=list)
    winery: list[str] = Field(default_factory=list)
