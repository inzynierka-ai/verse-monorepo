from pydantic import BaseModel

class ChapterBase(BaseModel):
    title: str
    description: str
    prompt: str
    story_id: int

class ChapterCreate(ChapterBase):
    pass

class Chapter(ChapterBase):
    id: int

    class Config:
        from_attributes = True
