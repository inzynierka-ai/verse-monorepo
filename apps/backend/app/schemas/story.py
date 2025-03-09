from pydantic import BaseModel

class StoryBase(BaseModel):
    user_id: int
    title: str
    description: str
    prompt: str

class StoryCreate(StoryBase):
    pass

class Story(StoryBase):
    id: int

    class Config:
        from_attributes = True
