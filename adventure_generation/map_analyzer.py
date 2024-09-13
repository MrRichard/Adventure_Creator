import json
import os
import base64

class MapAnalyzer:
    def __init__(self, map_image_path, llm_client):
        self.map_image_path = map_image_path
        self.llm_client = llm_client

    def identify_regions(self):
        with open(self.map_image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        landscape_description = self.llm_client.generate_landscape_description(base64_image)
        
        # convert to dict
        # landscape_description = json.loads(landscape_description)
        
        # save this to a file for review
        self._save_as_json(landscape_description)
        
        return landscape_description

    def _save_as_json(self, landscape_description):
        filename = 'map_description.json'
        output_path = os.path.join('output','json_outputs', filename)
        
        with open(output_path, 'w') as json_file:
            json.dump(landscape_description, json_file)

