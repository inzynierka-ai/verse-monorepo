from sqlalchemy.orm import Session
from app.models import Location
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
        description=location.description,
        brief_description=location.brief_description,
        image_prompt=location.image_prompt,
        rules=location.rules,
        colors=location.colors,
        image_dir=location.image_dir,
        story_id=location.story_id
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location
