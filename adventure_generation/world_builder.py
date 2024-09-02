import os
import json
import requests

class WorldBuilder:
    
    def __init__(self, context_extractor_object, region, llm_client):
        self.context_extractor = context_extractor_object
        if isinstance(region, dict):
            self.region = region
        else:
            raise ValueError("World must be either a dictionary or a JSON string.")
        self.llm_client = llm_client
        
    # This starts the region development chain. This looks like:
    # 1. Describe the region in generalized detail
    # 2. Create each new location and describe it in detail
    # 3. Create each new character and describe them in detail
    # 4. Create a custom encounter table of random events for this region
    # 5. Create a minor side quest that connect characters and locations.
    
    # 
    def region_development_chain(self):
        
        # Step 1 - Run Create Region Description
        print(f"{self.region['LocationName']} - Creating a regional description")
        regional_description = self.llm_client.generate_detailed_region_description(
            self.region,
            self.context_extractor.get_context(),
            self.context_extractor.get_writing_style()
        )
        self.region.update(regional_description)
        
        # Step 2 - Create the locations
        created_locations = {}
        print(f"{self.region['LocationName']} needs {self.region['num_locations']} locations")
        for i in range(self.region['num_locations']):
            loc=self.llm_client.generate_location(
                self.region,
                self.context_extractor.get_context(),
                self.context_extractor.get_writing_style()
            )
            created_locations[i] = loc
        self.region['locations'] = created_locations
            
        # Step 3 - Create the characters
        created_characters = {}
        print(f"{self.region['LocationName']} needs {self.region['num_characters']} characters")
        for i in range(self.region['num_characters']):
            char=self.llm_client.generate_character(
                self.region,
                self.context_extractor.get_context(),
                self.context_extractor.get_writing_style()
            )
            created_characters[i] = char
        self.region['characters'] = created_characters
        
        # Step 4 - Create a custom encounter table based on a d10
        print(f"{self.region['LocationName']} - Quest or plot prompts")
        created_quests = {}
        for i in range(1, 11):
            quest=self.llm_client.generate_regional_drama(
                self.region, 
                self.context_extractor.get_writing_style())
            created_quests[i] = quest
        self.region['quests'] =  created_quests
        
        # Step 5  - Create a random encounter table
        print(f"{self.region['LocationName']} - generating a random encounter table")
        created_encounters = {}
        for i in range(1, 11):
            encounter=self.llm_client.generate_random_encounter(
                self.region,
                self.context_extractor.get_context()
            )
            created_encounters[i] = encounter
        self.region['random_encounter_table'] =  created_encounters
        
        # Step 6 - Create character portraits
        print(f"{self.region['LocationName']} - generating character portraits")
        for i in range(self.region['num_characters']):
            portrait_file=self.llm_client.generate_character_portrait(
                character_description = self.region['characters'][i]['description'],
                illustration_style=self.context_extractor.get_visual_style()
            )
            self.region['characters'][i]['portrait'] =  portrait_file
        
        return self.region