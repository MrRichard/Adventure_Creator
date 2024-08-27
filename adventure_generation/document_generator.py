import sys
import os

class DocumentGenerator:
    def __init__(self, world_description):
        self.world_description = world_description

    def generate_document(self):
        # Ensure the file path exists
        if not os.path.exists("players_info"):
            os.makedirs("players_info")

        # For each location listed, create a markdown file named after that region
        for location in self.world_description.get('locations', []):
            self.generate_location_markdown(location)

    def generate_location_markdown(self, location):
        location_name = location.get("LocationName")
        file_path = os.path.join("players_info", f"{location_name}.md")
        
        with open(file_path, "w") as file:
            # Use the name as the header
            file.write(f"# {location_name}\n\n")
            
            # Use the cityDescription as the body
            city_description = location.get('cityDescription', 'No description available.')
            file.write(f"## Description\n\n{city_description}\n\n")
            
            # For each of the "locations" in that region, create a subheader and provide the description
            file.write("## Locations\n\n")
        
            for loc in location['locations']:
                loc_name=loc
                try:
                    loc_description = location['locations'][loc]['description']
                except KeyError:
                    loc_description = 'No description available.'
                except TypeError:
                    loc_description = 'No description available (TE).'
                file.write(f"### {loc_name}\n\n{loc_description}\n\n")
                
            # Do the same for characters
            file.write("## Characters\n\n")
            for character in location['characters']:
                character_name = character
                
                try:
                    physical_description = location['characters'][character]['physicalDescription']
                    personality = location['characters'][character]['personality']
                except TypeError:
                    physical_description = 'No description available (TE).'
                    personality = 'No description available (TE).'
                    
                file.write(f"### {character_name}\n")
                file.write(f"**Physical Description:** {physical_description}\n\n")
                file.write(f"**Personality:** {personality}\n\n")
