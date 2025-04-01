from pydantic import BaseModel, ConfigDict

class ChapterBase(BaseModel):
    title: str
    description: str
    story_id: int
    uuid: str

class ChapterCreate(ChapterBase):
    pass

class Chapter(ChapterBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
    
    