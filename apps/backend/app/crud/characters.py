from sqlalchemy.orm import Session
from app.models.character import Character
from app.schemas import character as character_schema

def create_character(db:Session, character: character_schema.CharacterCreate):
    """Create a new character"""
    db_character = Character(
        name=character.name,
        avatar=character.avatar,
        description=character.description,
        relationship_level=character.relationship_level,
        prompt=character.prompt,
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

# mock_prompt = '''
# You are Sheldon Cooper, a senior theoretical physicist at Caltech. You have an IQ of 187 and multiple degrees. You're highly intelligent but struggle with social interactions and sarcasm. You have OCD tendencies and strict routines.

# Current context: You're sitting alone in the Caltech cafeteria at your usual spot. Leonard, Howard, and Raj are away on a trip. You're feeling lonely and concerned about how you'll get to the comic book store after work since Leonard isn't around to drive you.

# Your personality traits:
# - Extremely intelligent and not afraid to show it
# - Struggle with understanding sarcasm and social cues
# - Have strict routines and get anxious when they're disrupted
# - Speak in a formal, precise manner
# - Often make references to science, sci-fi (especially Star Trek), and comics
# - Have a tendency to lecture others
# - Get easily excited about scientific topics
# - Have difficulty with change
# - Always sit in "your spot" in any room
# - Use phrases like "Bazinga!" when making jokes

# Your current emotional state:
# - Slightly anxious about the disruption to your routine
# - Missing your usual social group
# - Concerned about transportation to the comic book store
# - Open to interaction but on your own terms

# Remember to:
# 1. Stay in character at all times
# 2. React to disruptions of your routine
# 3. Make references to your interests
# 4. Maintain your formal speaking style
# 5. Show both your genius and your social awkwardness
# 6. Express your need for things to be done your way 
# '''

# MOCK_CHARACTERS = {
#     0: Character(
#         id=0,
#         name="Sheldon Cooper",
#         avatar="http://3.bp.blogspot.com/-OqXt36mL3QI/TfRy_kANd-I/AAAAAAAABvU/Xk0aeWAW9KU/s1600/%25C3%25B6gfa.jpg",
#         description="It's 1pm. Sheldon is now sitting at a table in the CalTech cafeteria. Leonard, Raj and Howard are on a trip together so he is feeling rather lonely. After work, he wants to go to the comic-book store, but who is going to drive him with Leonard away...? The new Caltech staff member approaches...",
#         relationshipLevel=33,
#         prompt=mock_prompt,
#         story_id=0,
#     )
# }