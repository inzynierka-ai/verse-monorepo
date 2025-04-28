from sqlalchemy import Table, Column, Integer, ForeignKey
from app.db.session import Base


# Define the association table for the many-to-many relationship
scene_character_association = Table(
    'scene_character_association', Base.metadata,
    Column('scene_id', Integer, ForeignKey('scenes.id'), primary_key=True),
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True)
)

# Define the association table for the many-to-many relationship
location_character_association = Table(
    'location_character_association', Base.metadata,
    Column('location_id', Integer, ForeignKey('locations.id'), primary_key=True),
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True)
)

location_connections = Table(
    'location_connections', Base.metadata,
    Column('from_location_id', Integer, ForeignKey('locations.id'), primary_key=True),
    Column('to_location_id', Integer, ForeignKey('locations.id'), primary_key=True)
)