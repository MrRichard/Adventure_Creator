import json
import os

class MapAnalyzer:
    def __init__(self, map_image_path):
        self.map_image_path = map_image_path
        self.gpt4o_client = GPT4oClient()

    def identify_regions(self):
        with open(self.map_image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        landscape_description = self.gpt4o_client.generate_landscape_description(base64_image)
        
        # convert to dict
        landscape_description = json.loads(landscape_description)
        
        # save this to a file for review
        self._save_as_json(landscape_description)
        
        return landscape_description

    def _save_as_json(self, landscape_description):
        filename = 'map_description.json'
        output_path = os.path.join('json_outputs', filename)
        
        with open(output_path, 'w') as json_file:
            json.dump(landscape_description, json_file)
    

import base64
from .gpt4o_client import GPT4oClient
