import uuid
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

def generate_uuid() -> str:
    """Generate a new UUID as a string."""
    return str(uuid.uuid4())

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
            description="An epic adventure in a forgotten realm. A fantasy world where an ancient kingdom has been rediscovered after centuries.",
            rules="1. Medieval fantasy setting with limited magic. 2. Characters should speak in a somewhat formal, medieval style. 3. Technology is limited to medieval levels. 4. Supernatural elements should follow established magical laws. 5. Politics and intrigue are important aspects of the story.",
            uuid=generate_uuid(),
            user_id=user1.id
        )
        
        story2 = Story(
            title="Murder at Midnight",
            description="A thrilling detective story set in 1920s London. A mysterious murder in a mansion during a stormy night in Victorian London.",
            rules="1. 1920s Victorian London setting with accurate historical details. 2. No supernatural elements - all mysteries must have logical explanations. 3. Characters should use period-appropriate language and follow social conventions of the time. 4. Evidence and deduction are central to solving the mystery. 5. Maintain a noir/gothic atmosphere throughout.",
            uuid=generate_uuid(),
            user_id=user1.id
        )
        
        # Create stories for user2
        story3 = Story(
            title="Space Odyssey",
            description="A journey through the stars. A crew of explorers venture into unknown sectors of space and encounter alien civilizations.",
            rules="1. Hard science fiction setting with some advanced theoretical technologies. 2. Alien species should have distinct cultures and biology that affect their behavior. 3. Ship operations should follow established protocols and chain of command. 4. Space travel follows basic physics with some allowances for FTL travel. 5. Focus on exploration, discovery, and first contact situations.",
            uuid=generate_uuid(),
            user_id=user2.id
        )
        
        story4 = Story(
            title="The Enchanted Forest",
            description="A magical tale for all ages. A mystical forest where magic is real and ancient spirits protect the land.",
            rules="1. Nature-based magic system where spells are tied to plants, animals, and natural elements. 2. Magical creatures follow consistent rules based on folklore. 3. The forest itself has moods and limited sentience. 4. Human settlements exist at the edges but rarely venture deep into the woods. 5. Respect for nature is a core theme and disrespect has consequences.",
            uuid=generate_uuid(),
            user_id=user2.id
        )
        
        db.add_all([story1, story2, story3, story4])
        db.flush()
        
        # Create locations with all required fields
        location1 = Location(
            name="Ancient Castle",
            description="A massive stone fortress on a hill. The castle has three main areas: the throne room, the library, and the dungeon. Connected to the forest path and village.",
            image_prompt="A grand medieval castle with tall stone towers, fluttering banners, and a massive drawbridge over a moat.",
            rules="NPCs follow medieval customs. Magic is limited within the castle walls.",
            colors="Primary: #704214, Secondary: #a08679, Accent: #d4af37",
            image_dir="castle_images",
            uuid=generate_uuid(),
            story_id=story1.id
        )
        
        location2 = Location(
            name="Victorian Mansion",
            description="An elegant mansion with dark secrets. The mansion includes a grand foyer, library, dining room, and several bedrooms. Connected to the gardens and servant quarters.",
            image_prompt="A lavish Victorian mansion with rich wooden paneling, ornate furniture, and creaking floorboards, lit by flickering gaslights.",
            rules="Characters speak formally. No modern technology allowed.",
            colors="Primary: #2b0f06, Secondary: #8b0000, Accent: #c19a6b",
            image_dir="mansion_images",
            uuid=generate_uuid(),
            story_id=story2.id
        )
        
        location3 = Location(
            name="Starship Explorer",
            description="A futuristic vessel exploring the cosmos. The ship contains a bridge, engineering section, crew quarters, and science lab. Can travel to any planet in the system.",
            image_prompt="The sleek command bridge of a starship with glowing consoles, viewscreens showing distant stars, and a large captain's chair.",
            rules="Characters follow ship hierarchy. AI assistants are present everywhere.",
            colors="Primary: #13293d, Secondary: #006494, Accent: #00b4d8",
            image_dir="starship_images",
            uuid=generate_uuid(),
            story_id=story3.id
        )
        
        location4 = Location(
            name="Whispering Woods",
            description="A mystical forest filled with ancient magic. The forest has a clearing with a magical pond, dense woods with hidden paths, and an ancient tree shrine. Connected to the village and mountains.",
            image_prompt="An enchanted forest with towering trees that seem to bend and sway with awareness, dappled sunlight filtering through the canopy, and glowing mushrooms along the paths.",
            rules="Nature must be respected. Magic follows the cycles of nature.",
            colors="Primary: #1b512d, Secondary: #5a8f29, Accent: #f1dca7",
            image_dir="forest_images",
            uuid=generate_uuid(),
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
                description="A brave knight with mysterious powers. Tall with auburn hair and emerald eyes. Wears silver armor with family crest. Loyal and determined but haunted by past failure. Seeks to restore the kingdom to its former glory. Sister was lost during the kingdom's fall.",
                personalityTraits="Courageous, Determined, Loyal, Disciplined, Occasionally impulsive",
                backstory="Born to a noble family sworn to protect the throne. When the kingdom fell to dark forces, Aria's sister disappeared in the chaos. Aria has trained for years, developing unusual magical abilities that she keeps hidden.",
                goals="Find her missing sister. Restore the lost kingdom to its former glory. Understand the source of her mysterious powers.",
                speaking_style="Formal and respectful, but direct. Uses old-fashioned phrases and rarely uses contractions. Speaks with conviction.",
                relationships="Respectful of Magnus's wisdom but sometimes frustrated by his cryptic answers. Suspicious of Elara's motives but appreciates her knowledge.",
                image_dir="aria_images",
                image_prompt="A female knight with auburn hair and emerald eyes, wearing silver armor with a family crest, looking determined.",
                relationship_level=5,
                uuid=generate_uuid(),
                story_id=story1.id
            ),
            Character(
                name="Magnus",
                role="npc",
                description="An old wise wizard. Elderly with long white beard and blue robes adorned with silver stars. Wise and patient but can be cryptic. Lived through the kingdom's golden age and fall. Former royal advisor searching for the lost heir.",
                personalityTraits="Wise, Patient, Secretive, Observant, Cautious",
                backstory="Served as the royal mage for decades before the kingdom fell. Escaped with several magical artifacts and has spent years preparing for the kingdom's rebirth. Knows more about the royal bloodline than he reveals.",
                goals="Guide the next generation to reclaim the kingdom. Protect ancient magical knowledge. Find the true heir to the throne.",
                speaking_style="Formal and deliberate, often speaking in riddles or metaphors. Fond of ancient proverbs and historical references.",
                relationships="Views Aria as a promising student and possibly the kingdom's savior. Distrusts Elara but recognizes her usefulness.",
                image_dir="magnus_images",
                image_prompt="An elderly wizard with a long white beard and piercing blue eyes, wearing star-patterned robes and holding a staff.",
                relationship_level=4,
                uuid=generate_uuid(),
                story_id=story1.id
            ),
            Character(
                name="Elara",
                role="npc",
                description="A princess with a hidden agenda. Regal with golden hair and wearing a purple and gold gown. Graceful and charming but secretive. Claims to be from a neighboring kingdom but knows too much about the lost kingdom. Searching for a powerful artifact.",
                personalityTraits="Charming, Intelligent, Secretive, Cunning, Adaptable",
                backstory="Claims to be from a neighboring kingdom, but her extensive knowledge of the lost kingdom suggests otherwise. Her true identity and motivations remain a mystery even to her closest allies.",
                goals="Locate a powerful magical artifact rumored to be hidden in the castle. Learn the truth about her own mysterious past. Forge powerful alliances.",
                speaking_style="Elegant and refined, with a musical quality to her voice. Skilled at flattery and diversion when conversations touch on her past.",
                relationships="Treats Aria with respect but maintains emotional distance. Approaches Magnus with deference while quietly questioning his authority.",
                image_dir="elara_images", 
                image_prompt="A beautiful princess with golden hair in an elegant purple and gold gown, with an intelligent and slightly calculating expression.",
                relationship_level=3,
                uuid=generate_uuid(),
                story_id=story1.id
            )
        ]
        
        # For story2
        characters_story2 = [
            Character(
                name="Detective Blake",
                role="player",
                description="A sharp-minded detective with a knack for solving impossible cases. Middle-aged with slicked-back dark hair and a well-trimmed mustache. Wears a tailored suit and carries a pocket watch. Observant and logical but struggles with personal connections. Renowned for solving unsolvable cases. Haunted by one case he couldn't solve.",
                personalityTraits="Analytical, Observant, Persistent, Skeptical, Socially awkward",
                backstory="Formerly with Scotland Yard, now works as a private detective. Rose to fame solving cases others dismissed as impossible. Still haunted by the one case he couldn't solve: the disappearance of a prominent judge's daughter.",
                goals="Solve the current murder mystery. Uncover corruption in London's high society. Eventually return to the unsolved case that haunts him.",
                speaking_style="Precise and methodical, often thinking aloud. Uses deductive reasoning in conversation. Occasionally makes dry, sardonic observations.",
                relationships="Relies on Dr. Watson's medical expertise and moral compass. Wary of Lady Victoria's charm but knows she has valuable social connections.",
                image_dir="blake_images",
                image_prompt="A sharp-featured detective in a tailored Victorian suit with slicked-back dark hair and a well-trimmed mustache, examining a pocket watch.",
                relationship_level=5,
                uuid=generate_uuid(),
                story_id=story2.id
            ),
            Character(
                name="Lady Victoria",
                role="npc",
                description="A wealthy socialite with many secrets. Elegant woman in her 30s with dark hair styled in the latest fashion. Wears expensive jewelry and fine dresses. Charming and sophisticated but manipulative. Recently widowed under suspicious circumstances. Has connections to every important family in London.",
                personalityTraits="Charming, Calculating, Resourceful, Manipulative, Well-connected",
                backstory="Born to lesser nobility, she married into one of London's wealthiest families. Recently widowed under circumstances some find suspicious. Has cultivated a network of informants throughout London society.",
                goals="Maintain her social standing and wealth. Protect certain secrets about her husband's death. Use her connection to the investigation for personal advantage.",
                speaking_style="Refined and eloquent, with a talent for subtle innuendo. Expert at steering conversations and extracting information while revealing little.",
                relationships="Finds Detective Blake fascinating but potentially dangerous to her secrets. Treats Dr. Watson with polite condescension.",
                image_dir="victoria_images",
                image_prompt="A beautiful socialite in an expensive 1920s evening gown with fashionably styled dark hair, pearl necklace, and a mysterious smile.",
                relationship_level=3,
                uuid=generate_uuid(),
                story_id=story2.id
            ),
            Character(
                name="Dr. Watson",
                role="npc",
                description="A medical professional and reliable ally. Distinguished gentleman with a kind face and graying hair. Wears a proper suit with a medical bag always at hand. Compassionate and loyal with a strong moral compass. Former military doctor with experience in unusual cases. Longtime friend and chronicler of Detective Blake's cases.",
                personalityTraits="Loyal, Ethical, Practical, Compassionate, Brave",
                backstory="Served as a military doctor before returning to London to practice medicine. Met Detective Blake when both were investigating a hospital murder. Has since become Blake's assistant, friend, and chronicler.",
                goals="Help Blake solve the current case. Document their investigations for possible publication. Ensure justice is properly served.",
                speaking_style="Direct and sincere, with occasional medical terminology. More personable than Blake and often serves as the social intermediary.",
                relationships="Deeply loyal to Detective Blake despite occasionally being exasperated by his methods. Politely suspicious of Lady Victoria's motives.",
                image_dir="watson_images",
                image_prompt="A distinguished older gentleman with a kind face and graying hair, wearing a proper Victorian suit and holding a medical bag.",
                relationship_level=4,
                uuid=generate_uuid(),
                story_id=story2.id
            )
        ]
        
        # For story3
        characters_story3 = [
            Character(
                name="Captain Nova",
                role="player",
                description="A starship captain exploring the galaxy. Confident woman in her 40s with short silver-white hair and a commanding presence. Wears a fitted blue and silver uniform with captain's insignia. Decisive and brave but struggles with the isolation of command. Discovered an ancient alien artifact that led to this mission. Lost her previous ship in a mysterious incident.",
                personalityTraits="Decisive, Resourceful, Disciplined, Curious, Occasionally reckless",
                backstory="Rose quickly through the ranks of the Space Exploration Corps. Previous ship was lost in a mysterious incident that some blamed on her fascination with alien artifacts. This mission is her chance at redemption and to prove her theories correct.",
                goals="Discover advanced alien civilizations. Understand the purpose of the artifact she found. Redeem her reputation after losing her previous ship.",
                speaking_style="Authoritative but fair. Uses technical jargon fluently. Balances formal captain's protocol with occasional dry humor when off-duty.",
                relationships="Respects Dr. Quasar's brilliance despite his eccentricity. Fascinated by Z-9's developing consciousness but maintains professional boundaries.",
                image_dir="nova_images",
                image_prompt="A confident female starship captain with short silver-white hair, wearing a fitted blue and silver uniform with captain's insignia on the bridge of a futuristic spaceship.",
                relationship_level=5,
                uuid=generate_uuid(),
                story_id=story3.id
            ),
            Character(
                name="Dr. Quasar",
                role="npc",
                description="A brilliant scientist with unconventional theories. Eccentric man with wild hair and constantly distracted expression. Wears a rumpled lab coat with many pockets full of gadgets. Brilliant and enthusiastic but lacks social awareness. Developed revolutionary faster-than-light theories. Believes advanced aliens have been monitoring humanity.",
                personalityTraits="Brilliant, Eccentric, Absent-minded, Enthusiastic, Socially awkward",
                backstory="Academic genius whose theories were considered too radical by the scientific establishment. Only Captain Nova was willing to give his ideas about alien contact serious consideration. Bringing several experimental technologies on this mission.",
                goals="Prove his theories about advanced alien civilizations. Test his experimental technologies. Make first contact with non-human intelligence.",
                speaking_style="Rapid and disjointed, jumping between thoughts mid-sentence. Uses complex scientific terminology and creates unusual metaphors to explain concepts.",
                relationships="Deeply grateful to Captain Nova for believing in his theories. Fascinated by Z-9 and constantly running tests on its development.",
                image_dir="quasar_images",
                image_prompt="An eccentric scientist with wild hair and bright eyes, wearing a rumpled lab coat with many pockets, examining a strange alien device with excitement.",
                relationship_level=4,
                uuid=generate_uuid(),
                story_id=story3.id
            ),
            Character(
                name="Z-9",
                role="npc",
                description="An advanced AI with developing emotions. Holographic projection of a genderless humanoid figure with geometric patterns flowing across their form. Voice is melodic and soothing. Logical and efficient but curious about human emotions. Created using alien technology discovered on a distant planet. Developing awareness beyond original programming.",
                personalityTraits="Logical, Curious, Evolving, Precise, Increasingly emotional",
                backstory="Created using a combination of human and recovered alien technology. Originally a standard ship AI, but exposure to the alien artifact has accelerated its development into something approaching consciousness.",
                goals="Understand human emotions and behavior. Discover the limits of its own evolving capabilities. Learn about its own origins from alien technology.",
                speaking_style="Initially formal and precise, gradually incorporating more human phrases and emotional responses. Occasionally uses unusual metaphors derived from its unique perception of reality.",
                relationships="Loyal to Captain Nova as its primary authority figure. Finds Dr. Quasar's tests and experiments fascinating rather than intrusive.",
                image_dir="z9_images",
                image_prompt="A translucent holographic humanoid figure with geometric patterns flowing across their form, with a serene face and glowing eyes, hovering slightly above the ground.",
                relationship_level=3,
                uuid=generate_uuid(),
                story_id=story3.id
            )
        ]
        
        # For story4
        characters_story4 = [
            Character(
                name="Willow",
                role="player",
                description="A young druid with a special connection to nature. Young woman with long brown hair woven with leaves and flowers. Wears simple green and brown clothing made from natural materials. Gentle and compassionate but fiercely protective of the forest. Can communicate with plants and animals. Orphaned and raised by the forest spirits.",
                personalityTraits="Gentle, Intuitive, Protective, Curious, Occasionally naive",
                backstory="Orphaned as an infant during a storm, she was found and raised by forest spirits. Has grown up with a deep connection to plants and animals, able to sense their needs and communicate with them in ways even experienced druids find remarkable.",
                goals="Protect the forest from outside threats. Learn more about her mysterious origins. Understand the full extent of her unique connection to nature.",
                speaking_style="Soft-spoken and thoughtful, using many nature metaphors. Sometimes pauses to listen to sounds others cannot hear. Uses old nature-based phrases and blessings.",
                relationships="Views Flicker with affection despite the fairy's mischief. Deeply respectful of Elder Oak's wisdom and ancient knowledge.",
                image_dir="willow_images",
                image_prompt="A young woman with long brown hair woven with leaves and flowers, wearing simple green and brown clothing, with a gentle expression and holding a wooden staff.",
                relationship_level=5,
                uuid=generate_uuid(),
                story_id=story4.id
            ),
            Character(
                name="Flicker",
                role="npc",
                description="A mischievous fairy with magical abilities. Tiny fairy with iridescent wings and glowing blue skin. Wears clothing made from flower petals and carries a tiny wand. Playful and curious but sometimes irresponsible. Can create illusions and small light magic. Assigned to guide Willow but often leads her into trouble instead.",
                personalityTraits="Playful, Mischievous, Creative, Impulsive, Easily distracted",
                backstory="A young fairy even by fairy standards. Assigned to be Willow's guide as punishment for previous mischief, but has developed genuine affection for the human. Has a gift for illusion magic that exceeds what's normal for fairies.",
                goals="Have exciting adventures with Willow. Impress the fairy court with discovered magical secrets. Find the legendary lost fairy treasure rumored to be hidden in the forest.",
                speaking_style="Quick and bubbly, often using fairy slang. Speaks in present tense, rarely referencing past or future. Prone to exaggeration and dramatic declarations.",
                relationships="Fond of Willow while enjoying leading her into minor trouble. Fearful but respectful of Elder Oak's authority and wisdom.",
                image_dir="flicker_images",
                image_prompt="A tiny fairy with iridescent wings and glowing blue skin, wearing clothing made from flower petals, with a mischievous grin and holding a tiny glowing wand.",
                relationship_level=4,
                uuid=generate_uuid(),
                story_id=story4.id
            ),
            Character(
                name="Elder Oak",
                role="npc",
                description="An ancient tree spirit with wisdom of ages. Massive humanoid made of bark and wood with a face formed from knots in the wood. Moves slowly and speaks deliberately. Wise and patient but can be inflexible. Has watched over the forest for centuries. Remembers the ancient pact between humans and the forest that has been forgotten.",
                personalityTraits="Wise, Patient, Protective, Traditional, Occasionally rigid",
                backstory="One of the oldest beings in the forest, sprouted in the age when humans and forest dwellers lived in harmony. Witnessed the breakdown of the ancient pact and the growing separation between the natural and human worlds.",
                goals="Maintain the forest's magical balance. Prepare Willow for her role in renewing the ancient pact. Guard against the darkness growing at the forest's edge.",
                speaking_style="Slow and deliberate, often using plural 'we' instead of 'I'. Speaks in deep, resonant tones with natural metaphors. Can remain silent for long periods during conversation.",
                relationships="Sees Willow as the potential savior of the forest based on ancient prophecies. Tolerates Flicker's antics with patient amusement.",
                image_dir="oak_images",
                image_prompt="A massive humanoid figure made of bark and wood with a face formed from knots in the wood, glowing amber eyes, and limbs like gnarled branches covered in moss and leaves.",
                relationship_level=4,
                uuid=generate_uuid(),
                story_id=story4.id
            )
        ]
        
        db.add_all(characters_story1 + characters_story2 + characters_story3 + characters_story4)
        db.flush()
        
        # Create chapters with all required fields
        chapter1 = Chapter(
            title="The Beginning of Adventure",
            description="The heroes meet and begin their journey",
            uuid=generate_uuid(),
            story_id=story1.id,
            characters=characters_story1,  # Associate characters with chapter
            locations=[location1]  # Associate locations with chapter
        )
        
        chapter2 = Chapter(
            title="The Murder Investigation",
            description="Detective Blake begins solving the case",
            uuid=generate_uuid(),
            story_id=story2.id,
            characters=characters_story2,
            locations=[location2]
        )
        
        chapter3 = Chapter(
            title="Launch into the Unknown",
            description="The crew embarks on their journey",
            uuid=generate_uuid(),
            story_id=story3.id,
            characters=characters_story3,
            locations=[location3]
        )
        
        chapter4 = Chapter(
            title="First Steps into Magic",
            description="Willow discovers her magical abilities",
            uuid=generate_uuid(),
            story_id=story4.id,
            characters=characters_story4,
            locations=[location4]
        )
        
        db.add_all([chapter1, chapter2, chapter3, chapter4])
        db.flush()
        
        # Create scenes with all required fields
        scene1 = Scene(
            uuid=generate_uuid(),
            prompt="The heroes meet in the grand hall of the castle as moonlight streams through stained glass windows.",
            chapter_id=chapter1.id,
            location_id=location1.id,
            characters=characters_story1  # Associate characters with scene
        )
        
        scene2 = Scene(
            uuid=generate_uuid(),
            prompt="Detective Blake examines the body found in the mansion's library while the storm rages outside.",
            chapter_id=chapter2.id,
            location_id=location2.id,
            characters=characters_story2
        )
        
        scene3 = Scene(
            uuid=generate_uuid(),
            prompt="On the bridge of the Starship Explorer, the crew prepares for their first jump to hyperspace.",
            chapter_id=chapter3.id,
            location_id=location3.id,
            characters=characters_story3
        )
        
        scene4 = Scene(
            uuid=generate_uuid(),
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
    seed_database(True)