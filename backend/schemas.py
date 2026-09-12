from pydantic import BaseModel


class SourceUpdate(BaseModel):
    enabled: bool


class SourceCreate(BaseModel):
    name: str
    category: str
    country: str
    enabled: bool = True