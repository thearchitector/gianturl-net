import orjson
from pydantic import BaseModel, Field


class EnlargeResponse(BaseModel):
    original: str = Field(description="The original short URL.")
    enlarged: str = Field(description="The new embiggened GiantURL.")
    improvement: int = Field(
        description="The percent improvement (enlargement) of the new GiantURL."
    )

    class Config:
        json_loads = orjson.loads
