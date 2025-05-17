from sqlalchemy import Table, Column, Integer, ForeignKey
from app.db.session import Base


# Define the association table for the many-to-many relationship
scene_character_association = Table(
    'scene_character_association', Base.metadata,
    Column('scene_id', Integer, ForeignKey('scenes.id'), primary_key=True),
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True)
)
