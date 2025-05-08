import logging
from typing import List, Optional, TypeVar, Type, Dict, Any

import uuid

from pydantic import BaseModel

from app.models.character import Character as CharacterOrmModel
from app.models.location import Location as LocationOrmModel
from app.models.scene import Scene as SceneOrmModel
from app.schemas.story_generation import Character as CharacterSchema
from app.schemas.story_generation import Location as LocationSchema
from app.schemas.story_generation import Scene as SceneSchema

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class ModelConverter:
    """
    Utility class for converting ORM models to Pydantic models
    with proper error handling and default value filling.
    """

    @staticmethod
    def orm_to_pydantic(
        orm_model: Any,
        pydantic_model: Type[T],
        defaults: Optional[Dict[str, Any]] = None
    ) -> T:
        """
        Generic converter from ORM model to Pydantic model with defaults.
        
        Args:
            orm_model: The database ORM model instance
            pydantic_model: The target Pydantic model class
            defaults: Optional dictionary of default values
            
        Returns:
            An instance of the target Pydantic model
        """
        if orm_model is None:
            raise ValueError("Cannot convert None to Pydantic model")
            
        # Create a base dictionary from ORM model
        try:
            # Use model_dict if available, otherwise fallback to __dict__
            if hasattr(orm_model, "__dict__"):
                orm_dict = orm_model.__dict__.copy()
                # Remove SQLAlchemy internal attributes
                orm_dict.pop("_sa_instance_state", None)
            else:
                orm_dict = dict(orm_model)
        except Exception as e:
            logger.error(f"Failed to convert ORM model to dict: {e}")
            orm_dict = {}
        # Apply any default values
        if defaults:
            for key, value in defaults.items():
                orm_dict[key] = value
        try:
            # Convert to Pydantic model
            return pydantic_model.model_validate(orm_dict)
        except Exception as e:
            logger.error(f"Failed to validate {pydantic_model.__name__} from ORM data: {e}")
            raise ValueError(f"Failed to convert to {pydantic_model.__name__}: {str(e)}")

    @staticmethod
    def character_orm_to_pydantic(
        character_orm: CharacterOrmModel,
    ) -> CharacterSchema:
        """
        Converts a Character ORM model to a Character Pydantic model.
        
        Args:
            character_orm: The Character ORM model
            ensure_uuid: If True, generates a UUID if missing
            default_image_url: Default URL for character image if missing
            
        Returns:
            CharacterSchema: The Pydantic model representation
        """
            
        # Prepare defaults
        defaults: Dict[str, Any] = {
            "image_dir": character_orm.image_dir
        }
        
            
        # Handle relationships conversion
        relationships = getattr(character_orm, "relationships", None)
        if relationships is None or (isinstance(relationships, str) and not relationships):
            defaults["relationships"] = []
        elif isinstance(relationships, str):
            try:
                # Try to parse relationships if they're a string
                # This depends on your actual format, adjust as needed
                # Example assumes comma-separated "name:level:type:backstory" format
                relationships_list = []
                for rel_str in relationships.split(","):
                    if rel_str.strip():
                        parts = rel_str.split(":")
                        if len(parts) >= 4:
                            rel = {
                                "name": parts[0].strip(),
                                "level": int(parts[1].strip()),
                                "type": parts[2].strip(),
                                "backstory": parts[3].strip()
                            }
                            relationships_list.append(rel)
                defaults["relationships"] = relationships_list
            except Exception as e:
                logger.warning(f"Failed to parse relationships string: {e}")
                defaults["relationships"] = []
        
        # Set default personality traits if missing
        if not getattr(character_orm, "personalityTraits", None):
            defaults["personalityTraits"] = []
            
        # Set default goals if missing
        if not getattr(character_orm, "goals", None):
            defaults["goals"] = []
        elif isinstance(getattr(character_orm, "goals", None), str):
            goals_str = getattr(character_orm, "goals", "")
            defaults["goals"] = [goal.strip() for goal in goals_str.split(",") if goal.strip()]
        # Ensure role is properly set
        if not getattr(character_orm, "role", None) or getattr(character_orm, "role", "") not in ["player", "npc"]:
            defaults["role"] = "npc"
            
        try:
            return ModelConverter.orm_to_pydantic(
                character_orm, 
                CharacterSchema, 
                defaults
            )
        except Exception as e:
            # Log detailed error info for debugging
            logger.error(f"Character conversion failed: {e}")
            logger.error(f"Character ORM data: {character_orm.__dict__ if hasattr(character_orm, '__dict__') else character_orm}")
            logger.error(f"Applied defaults: {defaults}")
            
            raise e
    @staticmethod
    def location_orm_to_pydantic(
        location_orm: LocationOrmModel,
        ensure_uuid: bool = True,
        default_image_url: str = "/placeholder.png"
    ) -> LocationSchema:
        """
        Converts a Location ORM model to a Location Pydantic model.
        
        Args:
            location_orm: The Location ORM model
            ensure_uuid: If True, generates a UUID if missing
            default_image_url: Default URL for location image if missing
            
        Returns:
            LocationSchema: The Pydantic model representation
        """
            
        # Prepare defaults
        defaults: Dict[str, Any] = {}
        
        # Ensure UUID exists
        if ensure_uuid and not getattr(location_orm, "uuid", None):
            defaults["uuid"] = str(uuid.uuid4())
            
        # Ensure image_dir exists
        if not getattr(location_orm, "image_dir", None):
            defaults["image_dir"] = default_image_url
            
        # Set default rules if missing
        if not getattr(location_orm, "rules", None):
            defaults["rules"] = []
        elif isinstance(getattr(location_orm, "rules", None), str):
            rules_str = getattr(location_orm, "rules", "")
            defaults["rules"] = [rule.strip() for rule in rules_str.split(",") if rule.strip()]
            
        try:
            return ModelConverter.orm_to_pydantic(
                location_orm, 
                LocationSchema, 
                defaults
            )
        except Exception as e:
            # Log detailed error info for debugging
            logger.error(f"Location conversion failed: {e}")
            logger.error(f"Location ORM data: {location_orm.__dict__ if hasattr(location_orm, '__dict__') else location_orm}")
            logger.error(f"Applied defaults: {defaults}")
            
            # Fall back to manual creation with minimal required fields
            return LocationSchema(
                name=getattr(location_orm, "name", "Unknown Location"),
                description=getattr(location_orm, "description", "No description available"),
                rules=defaults.get("rules", []),
                image_dir=defaults.get("image_dir", default_image_url),
                uuid=defaults.get("uuid", str(uuid.uuid4())),
                id=getattr(location_orm, "id", None)
            )


def convert_character(
    character_orm: CharacterOrmModel,
    default_image_url: str = "/placeholder.png"
) -> CharacterSchema:
    """
    Shorthand function to convert a Character ORM model to a Character Pydantic model.
    
    Args:
        character_orm: The Character ORM model
        default_image_url: Default URL for character image
        
    Returns:
        CharacterSchema: The Pydantic model representation
    """
    return ModelConverter.character_orm_to_pydantic(
        character_orm
    )


def convert_characters(
    character_orms: List[CharacterOrmModel],
    default_image_url: str = "/placeholder.png"
) -> List[CharacterSchema]:
    """
    Convert a list of Character ORM models to Character Pydantic models.
    
    Args:
        character_orms: List of Character ORM models
        default_image_url: Default URL for character images
        
    Returns:
        List[CharacterSchema]: List of converted Pydantic models
    """
    result: List[CharacterSchema] = []
    
    for character_orm in character_orms:
        try:
            character_schema = convert_character(
                character_orm,
                default_image_url=default_image_url
            )
            result.append(character_schema)
        except Exception as e:
            logger.error(f"Failed to convert character {getattr(character_orm, 'name', 'unknown')}: {e}")
            # Skip this character or handle the error as needed
            
    return result


def convert_location(
    location_orm: LocationOrmModel,
    default_image_url: str = "/placeholder.png"
) -> LocationSchema:
    """
    Shorthand function to convert a Location ORM model to a Location Pydantic model.
    
    Args:
        location_orm: The Location ORM model
        default_image_url: Default URL for location image
        
    Returns:
        LocationSchema: The Pydantic model representation
    """
    return ModelConverter.location_orm_to_pydantic(
        location_orm,
        default_image_url=default_image_url
    )


def convert_locations(
    location_orms: List[LocationOrmModel],
    default_image_url: str = "/placeholder.png"
) -> List[LocationSchema]:
    """
    Convert a list of Location ORM models to Location Pydantic models.
    
    Args:
        location_orms: List of Location ORM models
        default_image_url: Default URL for location images
        
    Returns:
        List[LocationSchema]: List of converted Pydantic models
    """
    result: List[LocationSchema] = []
    
    for location_orm in location_orms:
        try:
            location_schema = convert_location(
                location_orm,
                default_image_url=default_image_url
            )
            result.append(location_schema)
        except Exception as e:
            logger.error(f"Failed to convert location {getattr(location_orm, 'name', 'unknown')}: {e}")
            # Skip this location or handle the error as needed
            
    return result

def convert_scene(
    scene_orm: SceneOrmModel
) -> SceneSchema:
    """
    Convert a Scene ORM model to a Scene Pydantic model.
    
    Args:
        scene_orm: The Scene ORM model
        
    Returns:
        SceneSchema: The Pydantic model representation
    """
    if not scene_orm:
        raise ValueError("Cannot convert None to Scene model")
    
    try:
        
        location_schema = convert_location(scene_orm.location) 
        characters_schema = convert_characters(scene_orm.characters)
        
        # Create the Scene schema
        return SceneSchema(
            description=str(scene_orm.description),
            summary=str(getattr(scene_orm, 'summary', None) or ""),
            location=location_schema,
            characters=characters_schema
        )
    except Exception as e:
        # Log detailed error info for debugging
        logger.error(f"Scene conversion failed: {e}")
        logger.error(f"Scene ORM data: {scene_orm.__dict__ if hasattr(scene_orm, '__dict__') else scene_orm}")
        raise e
        