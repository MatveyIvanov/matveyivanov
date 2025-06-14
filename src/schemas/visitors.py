from pydantic import BaseModel, Field


class Visitors(BaseModel):
    count: int = Field(..., description="Number of current visitors")
