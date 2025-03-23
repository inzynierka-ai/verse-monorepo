from app.db.session import SessionLocal
from app.models.user import User
from app.models.story import Story
from app.models.character import Character
from app.models.chapter import Chapter
from app.models.scene import Scene
from app.models.message import Message
from app.models.location import Location
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def clear_database():
    """Clear all data from the database tables."""
    db = SessionLocal()
    try:
        print("Clearing existing database data...")
        # Delete in reverse order of dependencies
        db.query(Message).delete()
        db.query(Scene).delete()
        db.query(Chapter).delete()
        db.query(Character).delete()
        db.query(Location).delete()
        db.query(Story).delete()
        db.query(User).delete()
        
        # Commit the deletions
        db.commit()
        print("Database cleared successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error clearing database: {e}")
        raise
    finally:
        db.close()

def seed_database(force_reseed=False):
    """Seed the database with initial test data.
    
    Args:
        force_reseed: If True, clear all existing data before seeding
    """
    db = SessionLocal()
    
    try:
        # Check if database needs seeding
        if not force_reseed and db.query(User).first():
            print("Database already contains data, skipping seed.")
            db.close()
            return
        
        # Clear database if forced reseeding
        if force_reseed:
            db.close()
            clear_database()
            db = SessionLocal()
        
        print("Starting database seeding...")
        
        # Create test users
        user1 = User(
            email="test1@example.com",
            username="tester1",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        
        user2 = User(
            email="test2@example.com", 
            username="tester2",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        
        db.add_all([user1, user2])
        db.flush()  # Get IDs without committing
        
        # Create stories for user1
        story1 = Story(
            title="The Lost Kingdom",
            description="An epic adventure in a forgotten realm",
            prompt="A fantasy world where an ancient kingdom has been rediscovered after centuries.",
            user_id=user1.id
        )
        
        story2 = Story(
            title="Murder at Midnight",
            description="A thrilling detective story set in 1920s London",
            prompt="A mysterious murder in a mansion during a stormy night in Victorian London.",
            user_id=user1.id
        )
        
        # Create stories for user2
        story3 = Story(
            title="Space Odyssey",
            description="A journey through the stars",
            prompt="A crew of explorers venture into unknown sectors of space and encounter alien civilizations.",
            user_id=user2.id
        )
        
        story4 = Story(
            title="The Enchanted Forest",
            description="A magical tale for all ages",
            prompt="A mystical forest where magic is real and ancient spirits protect the land.",
            user_id=user2.id
        )
        
        db.add_all([story1, story2, story3, story4])
        db.flush()
        
        # Create locations with all required fields
        location1 = Location(
            name="Ancient Castle",
            description="A massive stone fortress on a hill",
            details="The castle has three main areas: the throne room, the library, and the dungeon. Connected to the forest path and village.",
            image_prompt="A grand medieval castle with tall stone towers, fluttering banners, and a massive drawbridge over a moat.",
            story_id=story1.id
        )
        
        location2 = Location(
            name="Victorian Mansion",
            description="An elegant mansion with dark secrets",
            details="The mansion includes a grand foyer, library, dining room, and several bedrooms. Connected to the gardens and servant quarters.",
            image_prompt="A lavish Victorian mansion with rich wooden paneling, ornate furniture, and creaking floorboards, lit by flickering gaslights.",
            story_id=story2.id
        )
        
        location3 = Location(
            name="Starship Explorer",
            description="A futuristic vessel exploring the cosmos",
            details="The ship contains a bridge, engineering section, crew quarters, and science lab. Can travel to any planet in the system.",
            image_prompt="The sleek command bridge of a starship with glowing consoles, viewscreens showing distant stars, and a large captain's chair.",
            story_id=story3.id
        )
        
        location4 = Location(
            name="Whispering Woods",
            description="A mystical forest filled with ancient magic",
            details="The forest has a clearing with a magical pond, dense woods with hidden paths, and an ancient tree shrine. Connected to the village and mountains.",
            image_prompt="An enchanted forest with towering trees that seem to bend and sway with awareness, dappled sunlight filtering through the canopy, and glowing mushrooms along the paths.",
            story_id=story4.id
        )
        
        db.add_all([location1, location2, location3, location4])
        db.flush()
        
        # Create characters with all required fields
        # For story1
        characters_story1 = [
            Character(
                name="Aria",
                role="player",
                description="A brave knight with mysterious powers",
                details="Tall with auburn hair and emerald eyes. Wears silver armor with family crest. Loyal and determined but haunted by past failure. Seeks to restore the kingdom to its former glory. Sister was lost during the kingdom's fall.",
                image_dir="aria_images",
                image_prompt="A female knight with auburn hair and emerald eyes, wearing silver armor with a family crest, looking determined.",
                relationship_level=5,
                story_id=story1.id
            ),
            Character(
                name="Magnus",
                role="npc",
                description="An old wise wizard",
                details="Elderly with long white beard and blue robes adorned with silver stars. Wise and patient but can be cryptic. Lived through the kingdom's golden age and fall. Former royal advisor searching for the lost heir.",
                image_dir="magnus_images",
                image_prompt="An elderly wizard with a long white beard and piercing blue eyes, wearing star-patterned robes and holding a staff.",
                relationship_level=4,
                story_id=story1.id
            ),
            Character(
                name="Elara",
                role="npc",
                description="A princess with a hidden agenda",
                details="Regal with golden hair and wearing a purple and gold gown. Graceful and charming but secretive. Claims to be from a neighboring kingdom but knows too much about the lost kingdom. Searching for a powerful artifact.",
                image_dir="elara_images", 
                image_prompt="A beautiful princess with golden hair in an elegant purple and gold gown, with an intelligent and slightly calculating expression.",
                relationship_level=3,
                story_id=story1.id
            )
        ]
        
        # For story2
        characters_story2 = [
            Character(
                name="Detective Blake",
                role="player",
                description="A sharp-minded detective with a knack for solving impossible cases",
                details="Middle-aged with slicked-back dark hair and a well-trimmed mustache. Wears a tailored suit and carries a pocket watch. Observant and logical but struggles with personal connections. Renowned for solving unsolvable cases. Haunted by one case he couldn't solve.",
                image_dir="blake_images",
                image_prompt="A sharp-featured detective in a tailored Victorian suit with slicked-back dark hair and a well-trimmed mustache, examining a pocket watch.",
                relationship_level=5,
                story_id=story2.id
            ),
            Character(
                name="Lady Victoria",
                role="npc",
                description="A wealthy socialite with many secrets",
                details="Elegant woman in her 30s with dark hair styled in the latest fashion. Wears expensive jewelry and fine dresses. Charming and sophisticated but manipulative. Recently widowed under suspicious circumstances. Has connections to every important family in London.",
                image_dir="victoria_images",
                image_prompt="A beautiful socialite in an expensive 1920s evening gown with fashionably styled dark hair, pearl necklace, and a mysterious smile.",
                relationship_level=3,
                story_id=story2.id
            ),
            Character(
                name="Dr. Watson",
                role="npc",
                description="A medical professional and reliable ally",
                details="Distinguished gentleman with a kind face and graying hair. Wears a proper suit with a medical bag always at hand. Compassionate and loyal with a strong moral compass. Former military doctor with experience in unusual cases. Longtime friend and chronicler of Detective Blake's cases.",
                image_dir="watson_images",
                image_prompt="A distinguished older gentleman with a kind face and graying hair, wearing a proper Victorian suit and holding a medical bag.",
                relationship_level=4,
                story_id=story2.id
            )
        ]
        
        # For story3
        characters_story3 = [
            Character(
                name="Captain Nova",
                role="player",
                description="A starship captain exploring the galaxy",
                details="Confident woman in her 40s with short silver-white hair and a commanding presence. Wears a fitted blue and silver uniform with captain's insignia. Decisive and brave but struggles with the isolation of command. Discovered an ancient alien artifact that led to this mission. Lost her previous ship in a mysterious incident.",
                image_dir="nova_images",
                image_prompt="A confident female starship captain with short silver-white hair, wearing a fitted blue and silver uniform with captain's insignia on the bridge of a futuristic spaceship.",
                relationship_level=5,
                story_id=story3.id
            ),
            Character(
                name="Dr. Quasar",
                role="npc",
                description="A brilliant scientist with unconventional theories",
                details="Eccentric man with wild hair and constantly distracted expression. Wears a rumpled lab coat with many pockets full of gadgets. Brilliant and enthusiastic but lacks social awareness. Developed revolutionary faster-than-light theories. Believes advanced aliens have been monitoring humanity.",
                image_dir="quasar_images",
                image_prompt="An eccentric scientist with wild hair and bright eyes, wearing a rumpled lab coat with many pockets, examining a strange alien device with excitement.",
                relationship_level=4,
                story_id=story3.id
            ),
            Character(
                name="Z-9",
                role="npc",
                description="An advanced AI with developing emotions",
                details="Holographic projection of a genderless humanoid figure with geometric patterns flowing across their form. Voice is melodic and soothing. Logical and efficient but curious about human emotions. Created using alien technology discovered on a distant planet. Developing awareness beyond original programming.",
                image_dir="z9_images",
                image_prompt="A translucent holographic humanoid figure with geometric patterns flowing across their form, with a serene face and glowing eyes, hovering slightly above the ground.",
                relationship_level=3,
                story_id=story3.id
            )
        ]
        
        # For story4
        characters_story4 = [
            Character(
                name="Willow",
                role="player",
                description="A young druid with a special connection to nature",
                details="Young woman with long brown hair woven with leaves and flowers. Wears simple green and brown clothing made from natural materials. Gentle and compassionate but fiercely protective of the forest. Can communicate with plants and animals. Orphaned and raised by the forest spirits.",
                image_dir="willow_images",
                image_prompt="A young woman with long brown hair woven with leaves and flowers, wearing simple green and brown clothing, with a gentle expression and holding a wooden staff.",
                relationship_level=5,
                story_id=story4.id
            ),
            Character(
                name="Flicker",
                role="npc",
                description="A mischievous fairy with magical abilities",
                details="Tiny fairy with iridescent wings and glowing blue skin. Wears clothing made from flower petals and carries a tiny wand. Playful and curious but sometimes irresponsible. Can create illusions and small light magic. Assigned to guide Willow but often leads her into trouble instead.",
                image_dir="flicker_images",
                image_prompt="A tiny fairy with iridescent wings and glowing blue skin, wearing clothing made from flower petals, with a mischievous grin and holding a tiny glowing wand.",
                relationship_level=4,
                story_id=story4.id
            ),
            Character(
                name="Elder Oak",
                role="npc",
                description="An ancient tree spirit with wisdom of ages",
                details="Massive humanoid made of bark and wood with a face formed from knots in the wood. Moves slowly and speaks deliberately. Wise and patient but can be inflexible. Has watched over the forest for centuries. Remembers the ancient pact between humans and the forest that has been forgotten.",
                image_dir="oak_images",
                image_prompt="A massive humanoid figure made of bark and wood with a face formed from knots in the wood, glowing amber eyes, and limbs like gnarled branches covered in moss and leaves.",
                relationship_level=4,
                story_id=story4.id
            )
        ]
        
        db.add_all(characters_story1 + characters_story2 + characters_story3 + characters_story4)
        db.flush()
        
        # Create chapters with all required fields
        chapter1 = Chapter(
            title="The Beginning of Adventure",
            description="The heroes meet and begin their journey",
            prompt="The unlikely heroes gather at the ancient castle, each with their own reasons for being there.",
            story_id=story1.id,
            characters=characters_story1,  # Associate characters with chapter
            locations=[location1]  # Associate locations with chapter
        )
        
        chapter2 = Chapter(
            title="The Murder Investigation",
            description="Detective Blake begins solving the case",
            prompt="A murder has been committed in the mansion and Detective Blake must solve the case before the killer strikes again.",
            story_id=story2.id,
            characters=characters_story2,
            locations=[location2]
        )
        
        chapter3 = Chapter(
            title="Launch into the Unknown",
            description="The crew embarks on their journey",
            prompt="The starship Explorer prepares to venture into uncharted territories of space.",
            story_id=story3.id,
            characters=characters_story3,
            locations=[location3]
        )
        
        chapter4 = Chapter(
            title="First Steps into Magic",
            description="Willow discovers her magical abilities",
            prompt="Willow enters the Whispering Woods for the first time and encounters magical creatures.",
            story_id=story4.id,
            characters=characters_story4,
            locations=[location4]
        )
        
        db.add_all([chapter1, chapter2, chapter3, chapter4])
        db.flush()
        
        # Create scenes with all required fields
        scene1 = Scene(
            prompt="The heroes meet in the grand hall of the castle as moonlight streams through stained glass windows.",
            chapter_id=chapter1.id,
            location_id=location1.id,
            characters=characters_story1  # Associate characters with scene
        )
        
        scene2 = Scene(
            prompt="Detective Blake examines the body found in the mansion's library while the storm rages outside.",
            chapter_id=chapter2.id,
            location_id=location2.id,
            characters=characters_story2
        )
        
        scene3 = Scene(
            prompt="On the bridge of the Starship Explorer, the crew prepares for their first jump to hyperspace.",
            chapter_id=chapter3.id,
            location_id=location3.id,
            characters=characters_story3
        )
        
        scene4 = Scene(
            prompt="In a sunlit clearing of the Whispering Woods, Willow discovers she can communicate with the forest spirits.",
            chapter_id=chapter4.id,
            location_id=location4.id,
            characters=characters_story4
        )
        
        db.add_all([scene1, scene2, scene3, scene4])
        db.commit()
        
        print("Database seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()