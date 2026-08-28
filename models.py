from pydantic import BaseModel, Field


class GameSearchResult(BaseModel):
    id: int
    name: str
    type: str
    year_published: int | None = None

class GameDetail(GameSearchResult):
    image_url: str | None = None
    min_players: int | None = None
    max_players: int | None = None
    playing_time: int | None = None
    min_age: int | None = None
    description: str | None = None

    designers: list[str] = Field(default_factory=list)
    publishers: list[str] = Field(default_factory=list)
    mechanics: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)

    rating: float | None = None
    weight: float | None = None