from typing import Optional
from sqlalchemy.orm import Session
from app.models.character import Character
from app.schemas import character as character_schema

def create_character(db:Session, character: character_schema.CharacterCreate):
    """Create a new character"""
    db_character = Character(
        name=character.name,
        image_dir=character.image_dir,
        description=character.description,
        relationship_level=character.relationship_level,
        story_id=character.story_id
    )
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character 

def get_character(db: Session, character_id: int) -> Character | None:
    """Get character by ID"""
    return db.query(Character).filter(Character.id == character_id).first()

def get_characters(db: Session) -> list[Character]:
    """Get all available characters"""
    return db.query(Character).all()

def get_player_character_for_story(db: Session, story_id: int) -> Character | None:
    """Get the player character associated with a specific story."""
    return db.query(Character).filter(
        Character.story_id == story_id, 
        Character.role == 'player'  # Assuming 'player' is the role identifier
    ).first()

def get_character_by_uuid(db: Session, character_uuid: str) -> Optional[Character]:
    """Get a character by its UUID"""
    return db.query(Character).filter(Character.uuid == character_uuid).first()
