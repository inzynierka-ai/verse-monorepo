from pydantic import BaseModel

class LocationBase(BaseModel):
    background: str
    name: str
    description: str
    prompt: str
    story_id: int

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int

    class Config:
        from_attributes = True
