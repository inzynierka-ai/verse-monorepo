import logging
import uuid
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, cast, Optional
from app.schemas.story import StoryCreate, StoryRead, StoryWithPlayerCharacterRead
from app.schemas import scene as scene_schema
from app.schemas.character import PlayerCharacterRead
from app.db.session import get_db
from app.crud.stories import get_story, create_story as create_story_service, get_user_stories
from app.schemas.user import User
from app.services.auth import get_current_user
from app.services.scene_service import SceneService

router = APIRouter(
    prefix="/stories",
    tags=["stories"]
)
@router.get("/", response_model=List[StoryWithPlayerCharacterRead])
async def list_stories(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all available stories with player character info"""
    db_stories = get_user_stories(db, current_user.id)
    stories_with_player_char_response: List[StoryWithPlayerCharacterRead] = []

    for db_story in db_stories:
        player_character_data: Optional[PlayerCharacterRead] = None
        
        # db_story.characters should now be a list containing at most one character (the player)
        # due to the modified get_user_stories query.
        if db_story.characters: # Check if the list is not empty
            player_char_model = db_story.characters[0] # Get the first (and only) character
            # player_char_model should always exist if db_story.characters is not empty
            player_character_data = PlayerCharacterRead(
                name=player_char_model.name,
                image_dir=player_char_model.image_dir
            )

        story_read_data = StoryRead.model_validate(db_story)

        stories_with_player_char_response.append(
            StoryWithPlayerCharacterRead(
                **story_read_data.model_dump(),
                player_character=player_character_data
            )
        )
    
    logging.info(f"Stories with player character info: {stories_with_player_char_response}")
    return stories_with_player_char_response

@router.get("/{story_id}", response_model=StoryRead)
def get_story_by_id(story_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a specific story by ID"""
    story = get_story(db, story_id, current_user.id)
    return story

@router.post("/", response_model=StoryRead)
def create_story(
    story: StoryCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new story"""
    # Create a copy of the story data and inject the user_id
    story_data = story.dict()
    story_data["user_id"] = current_user.id
    
    # Create a new StoryCreate instance with the updated data
    story_with_user = StoryCreate(**story_data)
    
    return create_story_service(db, story_with_user)

@router.get("/{story_id}/characters", response_model=List[scene_schema.Character])
def list_characters(story_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all characters for a specific story"""
    story = get_story(db, story_id, current_user.id)
    characters = story.characters
    return characters


@router.get("/{story_uuid}/scene/latest", response_model=scene_schema.Scene)
def get_latest_scene(
    story_uuid: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the latest active scene for a story"""
    # Verify user owns the story
    story = get_story(db, story_uuid, current_user.id)
    
    # Get the story ID as an integer
    story_id = cast(int, story.id)
    
    # Instantiate the service and call the method
    scene_service = SceneService()
    latest_scene = scene_service.fetch_latest_active_scene(db, story_id)
    
    # Handle not found cases
    if not latest_scene:
        raise HTTPException(status_code=404, detail="No active scene found for this story")
    
    return latest_scene

@router.patch("/{story_uuid}/scenes/{scene_uuid}/complete", response_model=scene_schema.Scene)
def complete_scene(
    story_uuid: uuid.UUID,
    scene_uuid: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a scene as completed"""
    # Verify user owns the story
    story = get_story(db, story_uuid, current_user.id)
    
    # Get the story ID as an integer
    story_id = cast(int, story.id)
    
    # Mark the scene as completed
    scene_service = SceneService()
    completed_scene = scene_service.mark_scene_completed(db, scene_uuid, story_id)
    
    # Handle not found cases
    if not completed_scene:
        raise HTTPException(status_code=404, detail="Scene not found or already completed")
    
    return completed_scene