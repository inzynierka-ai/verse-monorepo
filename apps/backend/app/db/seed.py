from app.db.session import SessionLocal
from app.models.user import User
from app.models.story import Story
from app.models.character import Character
from app.models.chapter import Chapter
from app.models.scene import Scene
from app.models.location import Location
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def seed_database():
    """Seed the database with initial test data."""
    db = SessionLocal()
    
    try:
        # Check if database is already seeded
        if db.query(User).first():
            print("Database already contains data, skipping seed.")
            return
        
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
        
        # Create locations with required prompt field
        location1 = Location(
            name="Ancient Castle",
            description="A massive stone fortress on a hill",
            prompt="A grand medieval castle with tall stone towers, fluttering banners, and a massive drawbridge over a moat.",
            background="castle_background.jpg",
            story_id=story1.id
        )
        
        location2 = Location(
            name="Victorian Mansion",
            description="An elegant mansion with dark secrets",
            prompt="A lavish Victorian mansion with rich wooden paneling, ornate furniture, and creaking floorboards, lit by flickering gaslights.",
            background="mansion_background.jpg",
            story_id=story2.id
        )
        
        location3 = Location(
            name="Starship Explorer",
            description="A futuristic vessel exploring the cosmos",
            prompt="The sleek command bridge of a starship with glowing consoles, viewscreens showing distant stars, and a large captain's chair.",
            background="spaceship_background.jpg",
            story_id=story3.id
        )
        
        location4 = Location(
            name="Whispering Woods",
            description="A mystical forest filled with ancient magic",
            prompt="An enchanted forest with towering trees that seem to bend and sway with awareness, dappled sunlight filtering through the canopy, and glowing mushrooms along the paths.",
            background="forest_background.jpg",
            story_id=story4.id
        )
        
        db.add_all([location1, location2, location3, location4])
        db.flush()
        
        # Create characters
        # For story1
        characters_story1 = [
            Character(
                name="Aria",
                avatar="knight_avatar.png",
                description="A brave knight with mysterious powers",
                relationship_level=5,
                prompt="You are Aria, a knight with mysterious powers. You speak with confidence and valor.",
                story_id=story1.id
            ),
            Character(
                name="Magnus",
                avatar="wizard_avatar.png",
                description="An old wise wizard",
                relationship_level=4,
                prompt="You are Magnus, an ancient wizard with knowledge of forgotten spells. You speak slowly and thoughtfully.",
                story_id=story1.id
            ),
            Character(
                name="Elara",
                avatar="princess_avatar.png",
                description="A princess with a hidden agenda",
                relationship_level=3,
                prompt="You are Elara, a princess with ulterior motives. You speak elegantly but hide your true intentions.",
                story_id=story1.id
            )
        ]
        
        # For story2
        characters_story2 = [
            Character(
                name="Detective Blake",
                avatar="detective_avatar.png",
                description="A sharp-minded detective with a knack for solving impossible cases",
                relationship_level=5,
                prompt="You are Detective Blake, known for your deductive reasoning. You speak directly and observe everything.",
                story_id=story2.id
            ),
            Character(
                name="Lady Victoria",
                avatar="lady_avatar.png",
                description="A wealthy socialite with many secrets",
                relationship_level=3,
                prompt="You are Lady Victoria, a socialite from high society. You speak with sophistication and guard your secrets closely.",
                story_id=story2.id
            ),
            Character(
                name="Dr. Watson",
                avatar="doctor_avatar.png",
                description="A medical professional and reliable ally",
                relationship_level=4,
                prompt="You are Dr. Watson, a medical expert and loyal friend. You speak factually and diplomatically.",
                story_id=story2.id
            )
        ]
        
        # For story3
        characters_story3 = [
            Character(
                name="Captain Nova",
                avatar="captain_avatar.png",
                description="A starship captain exploring the galaxy",
                relationship_level=5,
                prompt="You are Captain Nova, leader of the starship Explorer. You speak decisively and value your crew.",
                story_id=story3.id
            ),
            Character(
                name="Dr. Quasar",
                avatar="scientist_avatar.png",
                description="A brilliant scientist with unconventional theories",
                relationship_level=4,
                prompt="You are Dr. Quasar, a scientist with groundbreaking ideas. You speak excitedly about your theories and discoveries.",
                story_id=story3.id
            ),
            Character(
                name="Z-9",
                avatar="robot_avatar.png",
                description="An advanced AI with developing emotions",
                relationship_level=3,
                prompt="You are Z-9, an AI gaining sentience. Your speech is becoming less robotic and more emotional over time.",
                story_id=story3.id
            )
        ]
        
        # For story4
        characters_story4 = [
            Character(
                name="Willow",
                avatar="druid_avatar.png",
                description="A young druid with a special connection to nature",
                relationship_level=5,
                prompt="You are Willow, a nature-loving druid. You speak gently and often reference natural phenomena.",
                story_id=story4.id
            ),
            Character(
                name="Flicker",
                avatar="fairy_avatar.png",
                description="A mischievous fairy with magical abilities",
                relationship_level=4,
                prompt="You are Flicker, a playful fairy. You speak in short, energetic bursts and love pranks.",
                story_id=story4.id
            ),
            Character(
                name="Elder Oak",
                avatar="treant_avatar.png",
                description="An ancient tree spirit with wisdom of ages",
                relationship_level=4,
                prompt="You are Elder Oak, an ancient tree spirit. You speak slowly, deliberately, and use many metaphors.",
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