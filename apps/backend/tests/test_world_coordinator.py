import asyncio
import json
from app.services.world_generation.world_coordinator import coordinate_world
from app.schemas.world_wizard import (
    WorldCoordinatorInput,
    SettingInfo,
    DetailedCharacter,
    DetailedLocation,
    DetailedConflict,
    PersonalityTrait,
    InteractiveElement,
    Faction,
    Resolution,
    TurningPoint,
    EntityConnection
)

async def test_world_coordinator():
    # Create input data
    input_data = WorldCoordinatorInput(
        world_setting=SettingInfo(
            theme="Cyberpunk dystopia",
            atmosphere="Gritty and oppressive",
            description="A futuristic megacity where corporations rule and technology has advanced but society has regressed."
        ),
        detailed_characters=[
            DetailedCharacter(
                id="char1",
                name="Max Reynolds",
                role="Hacker",
                description="A skilled computer specialist who can break through any security system.",
                personality_traits=[
                    PersonalityTrait(
                        name="Intelligent",
                        description="Quick-thinking and knowledgeable about technology."
                    ),
                    PersonalityTrait(
                        name="Reckless",
                        description="Often takes dangerous risks without considering consequences."
                    )
                ],
                backstory="Grew up on the streets and taught himself how to hack. Now works freelance for whoever pays the most.",
                goals=["Find corporate secrets", "Expose corruption"],
                appearance="Wears a dark hoodie, has augmented eyes, and a neural implant visible at the base of his skull."
            ),
            DetailedCharacter(
                id="char2",
                name="Victoria Chen",
                role="Corporate Executive",
                description="A ruthless executive who will protect corporate interests at any cost.",
                personality_traits=[
                    PersonalityTrait(
                        name="Calculating",
                        description="Always plans several steps ahead and considers all angles."
                    ),
                    PersonalityTrait(
                        name="Ambitious",
                        description="Willing to do whatever it takes to climb the corporate ladder."
                    )
                ],
                backstory="Born to wealthy parents, Victoria has been groomed for corporate leadership since childhood. She's risen through the ranks by being more ruthless than her competitors.",
                goals=["Secure her position", "Eliminate threats to the corporation"],
                appearance="Pristine business attire, subtle cybernetic enhancements, and always perfectly composed."
            )
        ],
        detailed_locations=[
            DetailedLocation(
                id="loc1",
                name="Neon District",
                description="A bustling area full of bright neon signs, street vendors, and the constant hum of technology.",
                history="Once a thriving business district, it fell into disrepair after the economic collapse of 2087. Now it's a haven for those who want to disappear or find illegal goods.",
                atmosphere="Chaotic, vibrant, and dangerous. The air is thick with steam from food vendors and the smell of synthetic drugs.",
                interactive_elements=[
                    InteractiveElement(
                        name="Black Market Terminal",
                        description="A hidden terminal that connects to the illegal underground network.",
                        interaction="Can be hacked to access restricted information or purchase illegal goods."
                    ),
                    InteractiveElement(
                        name="Noodle Stand",
                        description="A popular food vendor that serves as a gathering spot for locals.",
                        interaction="A good place to overhear rumors or meet contacts."
                    )
                ]
            ),
            DetailedLocation(
                id="loc2",
                name="Corporate Plaza",
                description="A sterile, heavily monitored area where the corporate elites conduct business.",
                history="Built after the corporate wars of 2075, this fortress-like complex houses the headquarters of the largest corporations that now govern the city.",
                atmosphere="Cold, efficient, and oppressive. Every surface is polished chrome or glass, and security drones constantly patrol.",
                interactive_elements=[
                    InteractiveElement(
                        name="Security Checkpoint",
                        description="A heavily guarded entrance with advanced scanning technology.",
                        interaction="Must be bypassed with proper credentials or hacking skills."
                    ),
                    InteractiveElement(
                        name="Executive Lounge",
                        description="A luxurious area where corporate deals are made over synthetic cocktails.",
                        interaction="A place to gather intelligence or make high-level contacts."
                    )
                ]
            )
        ],
        detailed_conflict=DetailedConflict(
            title="The Glitch in the System",
            description="A mysterious hacker has discovered a way to manipulate corporate security systems, threatening the power structure of the entire city.",
            factions=[
                Faction(
                    name="The Corporations",
                    motivation="Maintain control and order; protect their assets and power.",
                    methods="Deploying security forces, hiring bounty hunters, launching counter-hacking operations."
                ),
                Faction(
                    name="The Hackers",
                    motivation="Disrupt the corporate power structure; expose their secrets; potentially redistribute resources.",
                    methods="Cyberattacks, data breaches, information leaks, manipulating city infrastructure."
                )
            ],
            possible_resolutions=[
                Resolution(
                    path="Corporate Victory",
                    description="The corporations successfully identify and neutralize the hackers, patching the vulnerability.",
                    consequences="Increased surveillance, stricter laws, and harsher punishments for dissent."
                ),
                Resolution(
                    path="Hacker Triumph",
                    description="The hackers successfully distribute the 'glitch' widely, causing widespread system failures.",
                    consequences="Chaos and anarchy erupt as systems fail. New power structures emerge."
                )
            ],
            turning_points=[
                TurningPoint(
                    trigger="A major data leak exposes corporate corruption.",
                    result="Public opinion turns against the corporations, leading to mass protests."
                )
            ],
            character_connections=[
                EntityConnection(
                    entity_id="char1",
                    connection="Max could be the mysterious hacker or an ally, his skills are crucial to the conflict."
                ),
                EntityConnection(
                    entity_id="char2",
                    connection="Victoria is leading the corporate response to hunt down the hackers."
                )
            ],
            location_connections=[
                EntityConnection(
                    entity_id="loc1",
                    connection="The Neon District is where the hackers operate from and recruit supporters."
                ),
                EntityConnection(
                    entity_id="loc2",
                    connection="The Corporate Plaza is the primary target for the hackers' attacks."
                )
            ],
            personal_stakes="For individuals like Max, involvement could mean great risk or great reward.",
            community_stakes="The Neon District could become a battleground or experience temporary liberation.",
            world_stakes="The conflict could inspire similar uprisings in other corporate-controlled cities."
        )
    )
    
    try:
        # Call the function
        result = await coordinate_world(input_data)
        
        # Print the result
        print("Success! Coordinated world:")
        print(json.dumps(result.model_dump(), indent=2))
        return result
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    asyncio.run(test_world_coordinator()) 