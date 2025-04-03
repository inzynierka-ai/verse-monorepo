from pydantic import BaseModel

class ChapterBase(BaseModel):
    title: str
    description: str
    story_id: int
    uuid: str

class ChapterCreate(ChapterBase):
    pass

class Chapter(ChapterBase):
    id: int

    class Config:
        from_attributes = True