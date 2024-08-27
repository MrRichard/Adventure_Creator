import os
import json

class WorldBuilder:
    def __init__(self, context, world, gpt4o_client):
        self.context = context
        
        if isinstance(world, str):
            self.world = json.loads(world)
        elif isinstance(world, dict):
            self.world = world
        else:
            raise ValueError("World must be either a dictionary or a JSON string.")
        
        self.world = world
        self.gpt4o_client = gpt4o_client
    
    # define a prompt for each region
    def build_world(self):
        prompt = self.context
        for region in self.world['locations']:
            print(f" > Creating the {region['LocationName']} region.")
            prompt += f"\n\nLocation Name: {region['LocationName']}\nLocation Type: {region['LocationType']}\nShort Description: {region['ShortDescription']}\n"
            
            # Request new copy
            json_output # humor me and ensure it's clear
            json_output=self._build_world(prompt)
            
            # Try to load copy. Error if incomplete or error'd json.
            try:
                region_description = json.loads(json_output)
            except json.decoder.JSONDecodeError as e:
                print(f"Failed to decode JSON for region: {region['LocationName']}. Error: {e}")
                error_filename = f"{region['LocationName']}_error.txt"
                error_filepath = os.path.join('json_outputs', error_filename)
                with open(error_filepath, 'w') as error_file:
                    error_file.write(prompt)
                    error_file.write(json_output)
            
            region.update(region_description)
        
        self._save_as_json()
        return self.world
            
    def _build_world(self, prompt):
        # Use GPT-4o to build a detailed world description
        world_description = self.gpt4o_client.generate_region_description(prompt)
        return world_description
    
    def _save_as_json(self): 
        filename = 'expanded_world.json'
        output_path = os.path.join('json_outputs', filename)
        
        with open(output_path, 'w') as json_file:
            json.dump(self.world, json_file)
