import os
from ollama import Client

# TODO: This file needs some massive refactoring. Don't use this! Yet. 

class ollamaClient:
    def __init__(self):
        
        # TODO: put the ollama server into another folder. 
        self.client = Client(host="http://192.168.1.115:11434") # This is my home ollama server IP address. Don't get wierd on this. 
        self.system_role = "You are a ttrpg game world creator and game designer assistant. You help build the setting for amazing adventures."

    
    def generate_locations(self, prompt):
        prompt += """INSTRUCTIONS: Create the specificed number of signficant locations for existing at this location. 
        Write a brief but creative description of the physical description and appearance of the place.
        Please return this information in JSON format. All locations should be listed in the "locations" object.
        The locations should ONLY have a "description" element.
        Please always provide correct json syntax. Use object notation, not arrays. 
        """
        response = self.client.generate(
            model="llama3.1",
            prompt=prompt,
            format="json",
            #context=self.system_role
        )
        return response['response']
    
    
    def generate_characters(self, prompt):
        prompt += """INSTRUCTIONS: Create the specified number of characters for existing at this location. 
        Write a brief but creative physical description of the character and their personality.
        The physical description should be a short paragraph describing their visible traits and any items or observable features.
        The personality description should be a short paragraph describing the characters alignment, world-view, any backstory or interesting behavior.
        Please return this information in JSON format. All characters should be listed in the "characters" object.
        The characters object should have ONLY sub-objects for "physicalDescription" and "personality". 
        Please always provide correct json syntax. Use object notation, not arrays. 
        """
        response = self.client.generate(
            model="llama3.1",
            prompt=prompt,
            format="json",
            #context=self.system_role
        )
        return response['response']
