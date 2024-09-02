def create_character_images(self):
    
        
        # Generate character images
        characters = character_description.get('characters', [])
        for details in characters:
            character_name = details
            character_appearance = characters[details]['physicalDescription']
            prompt = self.context
            prompt +=f"\nCreate a protrait of the character {character_name}."
            prompt +=f"\nIMPORTANT: Character physical description: {character_appearance}"
            portrait_url = self.gpt4o_client.generate_character_portrait(prompt)
            
            # Define the directory and file path
            players_info_dir = 'players_info'
            os.makedirs(players_info_dir, exist_ok=True)
            prompt_filename = f"{details}_location_prompt.txt"
            prompt_filepath = os.path.join(players_info_dir, prompt_filename)
        
        # Save the prompt to a text file
        with open(prompt_filepath, 'w') as prompt_file:
            prompt_file.write(prompt)
            
            # Download the image
            character_portraits = 'character_portraits'
            os.makedirs(character_portraits, exist_ok=True)
            
            response = requests.get(portrait_url, stream=True)
            if response.status_code == 200:
                image_filename = os.path.join(character_portraits, f"{character_name}.jpg")
                
            with open(image_filename, 'wb') as image_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        image_file.write(chunk)
                        
            # Update the character information with the relative path to the image
            
        characters[details]['portrait'] = image_filename