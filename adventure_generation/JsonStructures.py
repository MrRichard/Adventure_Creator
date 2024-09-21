import json


class JsonStructures:
    def __init__(self):
        pass

    def generate_quest(self):
        return json.dumps(
            {
                "name": "A short title of quest",
                "description": "1 paragraph description of the quest",
                "other": {},
            }
        )

    def generate_location(self):
        return json.dumps(
            {
                "name": "the name of the location",
                "description": "1 paragraph of detailed description of this place",
                "lore": "1 paragraph about the history, mood or unique quality of this place",
                "other": {},
            }
        )

    def regional_demographics(self):
        return json.dumps(
            {
                "races": {"human": 70, "orc": 20, "elf": 10},
                "genders": {"male": 50, "female": 50},
                "classes": {
                    "pauper": 40,
                    "merchant": 30,
                    "military": 20,
                    "noblity": 10,
                },
            }
        )

    def generate_character(self):
        return json.dumps(
            {
                "name": "the name of the character",
                "description": "1 paragraph description of the character's physical appearance and visible qualities",
                "personality": "1-2 sentences describing the character's demeanor, worldview or mood",
                "race": "Character's race chosen at random from those availabe in the world descrition",
                "class": "Choose from pauper, merchant, military, noblity, or other",
                "gender": "Choose from M, F, or unknown",
                "other": {},
            }
        )

    def generate_random_encounter(self):
        return json.dumps(
            {
                "encounter": {
                    "title": "A short title, possibly with rhetorical elements like irony, puns, or alliteration.",
                    "description": "1 paragraph description of a random encounter or event that requires the party to engage",
                    "opportunity": "1-2 sentences describing why the party should or should not get involved",
                    "other": {},
                }
            }
        )
