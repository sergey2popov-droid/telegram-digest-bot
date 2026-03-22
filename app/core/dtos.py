from datetime import datetime

from pydantic import BaseModel


class SourceDTO(BaseModel):
    id: int
    url: str
    name: str
    type: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ItemDTO(BaseModel):
    id: int
    source_id: int
    guid: str
    title: str
    url: str
    published_at: datetime | None
    raw_score: float
    final_score: float
    fetched_at: datetime

    model_config = {"from_attributes": True}


class DigestDTO(BaseModel):
    id: int
    created_at: datetime
    sent_at: datetime | None
    item_count: int

    model_config = {"from_attributes": True}
