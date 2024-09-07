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
        self.optimized_context = self._optimize_user_input(
            self.context_extractor.get_context())
        self.optimized_style = self._optimize_user_input(
            self.context_extractor.get_writing_style())
            
    def _optimize_user_input(self, input_copy):
        print(" - Optimizing input copy")
        optimized_copy = self.llm_client._summarize_context(input_copy)
        return optimized_copy
    # This starts the region development chain. This looks like:
    # 1. Describe the region in generalized detail
    # 2. Create each new location and describe it in detail
    # 3. Create each new character and describe them in detail
    # 4. Create a custom encounter table of random events for this region
    # 5. Create a minor side quest that connect characters and locations.
    
    def region_development_chain(self):
        
        # Step 1 - Run Create Region Description
        print(f"{self.region['LocationName']} - Creating a regional description")
        regional_description = self.llm_client.generate_detailed_region_description(
            self.region,
            self.optimized_context,
            self.optimized_style
        )
        self.region.update(regional_description)
        
        # Step 2 - Create the locations
        created_locations = {}
        print(f"{self.region['LocationName']} needs {self.region['num_locations']} locations")
        for i in range(self.region['num_locations']):
            loc=self.llm_client.generate_location(
                self.region,
                self.optimized_context,
                self.optimized_style
            )
            location_name=loc['name']
            created_locations[location_name] = loc
        self.region['locations'] = created_locations
            
        # Step 3 - Create the characters
        created_characters = {}
        print(f"{self.region['LocationName']} needs {self.region['num_characters']} characters")
        for i in range(self.region['num_characters']):
            char=self.llm_client.generate_character(
                self.region,
                self.optimized_context,
                self.optimized_style
            )
            character_name=char['name']
            created_characters[character_name] = char
        self.region['characters'] = created_characters
        
        # Step 4 - Create a custom encounter table based on a d10
        print(f"{self.region['LocationName']} - Quest or plot prompts")
        created_quests = {}
        for i in range(1, 7):
            quest=self.llm_client.generate_regional_drama(
                self.region, 
                self.optimized_style
            )
            created_quests[i] = quest
        self.region['quests'] =  created_quests
        
        # Step 5  - Create a random encounter table
        print(f"{self.region['LocationName']} - Generating a random encounter table")
        created_encounters = {}
        for i in range(1, 11):
            encounter=self.llm_client.generate_random_encounter(
                self.region,
                self.optimized_context
            )
            created_encounters[i] = encounter
        self.region['random_encounter_table'] =  created_encounters
        
        # Step 6 - Create character portraits
        print(f"{self.region['LocationName']} - Generating character portraits")
        for character in self.region['characters']:
            portrait_file=self.llm_client.generate_character_portrait(
                character_description = self.region['characters'][character]['description'],
                world_info=self.optimized_context,
                illustration_style=self.optimized_style
            )
            self.region['characters'][character]['portrait'] =  portrait_file
            
        # Step 7 - Create location maps 
        print(f"{self.region['LocationName']} - Generating location maps")
        for loc in self.region['locations']:
            location_map=self.llm_client.generate_location_maps(
                location_description = self.region['locations'][loc]['description'],
                world_info=self.optimized_context,
                illustration_style=self.optimized_style
            )
            self.region['locations'][loc]['illustration'] =  location_map
        
        return self.region