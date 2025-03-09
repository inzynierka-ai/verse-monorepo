from sqlalchemy.orm import Session
from app.models import *
from app.schemas import location as location_schema

def get_location(db: Session, location_id: int) -> Location | None:
    """Get location by ID"""
    return db.query(Location).filter(Location.id == location_id).first()

def get_all_locations(db: Session) -> list[Location]:
    """Get all available locations"""
    return db.query(Location).all()

def create_location(db: Session, location: location_schema.LocationCreate):
    """Create a new location"""
    db_location = Location(
        name=location.name,
        background=location.background,
        description=location.description,
        prompt=location.prompt,
        story_id=location.story_id
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

# MOCK_LOCATIONS = {
#     0: Location(
#         id=0,
#         background="/cafeteria.webp",
#         name="Caltech cafeteria",
#         description="The heart of social interaction at Caltech, where the gang regularly meets for lunch. This bustling cafeteria is where many of their scientific discussions, personal conversations, and comedic moments take place. The venue features standard cafeteria seating with distinctive red chairs and is frequented by students, professors, and researchers alike.",
#         prompt="The heart of social interaction at Caltech, where the gang regularly meets for lunch. This bustling cafeteria is where many of their scientific discussions, personal conversations, and comedic moments take place. The venue features standard cafeteria seating with distinctive red chairs and is frequented by students, professors, and researchers alike.",
#         story_id=0,
#     )
# }
