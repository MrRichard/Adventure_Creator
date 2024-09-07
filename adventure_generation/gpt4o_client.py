import os
import openai
import json
import requests
import string
import random

# To prevent rate limit issues
import time

# Add logging to help track prompt issues
import logging

# Configure logging
logging.basicConfig(filename='llm_usage.log', level=logging.NOTSET, format='%(asctime)s - %(message)s')

class GPT4oClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        self.system_role = """
        You are a ttrpg game world creator and game designer assistant. 
        You help build the setting for amazing adventures and weave a story with opportunity for interaction.
        You want to avoid fantasy tropes and commonly used language.
        """
        self.system_role_msg = {"role": "system","content": [{"type": "text","text": f"{self.system_role}"}]}
        self.image_storage = "images"
        
        logging.info("OpenAI Client initiated")

    def _create_messages(self, prompt):
        msgs=[self.system_role_msg, {"role": "user", "content": [{"type": "text","text": f"{prompt}"}]}]
            
        return msgs
    
    def _parse_json(self, json_inputs):
        try:
            dict_output = json.loads(json_inputs)
        except json.decoder.JSONDecodeError as e:
            logging.warn(f"Failed to decode JSON. Error: {e}")
            abbreviated_json = self._fix_json_response(json_inputs)
            dict_output = json.loads(abbreviated_json)
            
        # Let's add a delay to stop hitting ratelimits
        time.sleep(15)
        
        logging.debug(f"<<< OUTPUT FROM LLM:\n{json_inputs}")
        
        return dict_output

    # this is the step 1 map review    
    def generate_landscape_description(self, base64_image):
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                self.system_role_msg,
                {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": """
                    Review this map carefully and create a json file that contains the names and brief descriptions of the regions. 
                    Specifically, look for big and small towns, and named natural features. 
                    For each item create a json object with this information:\n- LocationName, LocationType, ShortDescription\n\n* 
                    The LocationType should be one of these items [ bigTown, smallTown, NaturalFeature, other ]. 
                    The shortDescription should be minimal. One to two lines at most.
                    Example formatting: {\"regions\": [{\"LocationName\": \"\",\"LocationType\": \"\",\"ShortDescription\": \"\"},{\"LocationName\": \"\",\"LocationType\": \"\",\"ShortDescription\": \"\"}]}
                    """
                    },
                    {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
                }
            ],
            max_tokens=2000,
            temperature=1.25,
            response_format={
                "type": "json_object"
            }
        )
        logging.info("Map reading does not parse json. Sends directly to Worldbuilder.")
        return response.choices[0].message.content
    
    def generate_detailed_region_description(self, region, world_info='', style_input=''):
        if region =='':
            return {}
        
        prompt = """
        INSTRUCTIONS: Expand upon the simple description for this region:
        Region Name: {} - a {}.
        Region Short Description: {}
        World Info: {}
        Writing Style: {}
        Please return this information in JSON format. Please always provide correct json syntax. Use object notation, not arrays.
        This content should be in the "regionDetails" object. Use this template:
        Example JSON: 
        """.format(
            region['LocationName'],
            region['LocationType'],
            region['ShortDescription'],
            world_info,
            style_input
        )
        prompt+="{\'description\' : \'An example descriptive paragraph\',\'lore\' : \'Example history, mood or lore of this region in one paragraph\'}"
        
        if self._count_words_in_prompt(prompt) >= 1000:
            print(" - Shortening prompt")
            prompt = self._shorten_prompt(prompt)
            logging.warn(prompt)
        
        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=1000,
            temperature=1.1,
            response_format={
                "type": "json_object"
            }
        )
        return self._parse_json(response.choices[0].message.content)
        
    
    def generate_location(self, region, world_info='', style_input=''):
        prompt = """
        INSTRUCTIONS: Create a fictional signficant locations for the location of {}, a {}.
        Region Short Description: {}
        World Info: {}
        Writing Style: {}
        Write a brief but creative description of the physical description and appearance of a place.
        Please return this information in JSON format. Please always provide correct json syntax. Use object notation, not arrays.
        Example JSON:
        """.format(region['LocationName'], 
                   region['LocationType'],
                   region['ShortDescription'],
                   world_info,
                   style_input
        )
        
        prompt += "{\'name\' : \'location name\', \'description\' : \'An example descriptive paragraph\', \'lore\' : \'Example history, mood or lore of this region in one paragraph\' }"
        
        if self._count_words_in_prompt(prompt) >= 1000:
            print(" - Shortening prompt")
            prompt = self._shorten_prompt(prompt)
            logging.warn(prompt)
        
        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=1000,
            temperature=1.1,
            response_format={
                "type": "json_object"
            }
        )
        return self._parse_json(response.choices[0].message.content)
    
    
    def generate_character(self, region, world_info='', style_input=''):
        prompt = '''
        INSTRUCTIONS: Create a fictional signficant character for the location of {}, a {}. This person should randomly be either gender, any race allowed in the World Info, any age between 10 and 100, and randomly between 1-10 in attractiveness with most people being a 6. 
        Region Short Description: {}
        World Info: {}
        Writing Style: {}
        Please return this information in JSON format. Please always provide correct json syntax. Use object notation, not arrays. 
        The output should consist of three items: "name", "description" and "personality"
        Example JSON: 
        '''.format(
            region['LocationName'],
            region['LocationType'],
            region['ShortDescription'],
            world_info,
            style_input
        )
        prompt+="{\'name\' : \'Character name\',\'description\' : \'describe the visible appearance of this character in one paragraph\', \'personality\' : \'convey the personality, world view, occupation and quirks of this character in one paragraph\'}"
        
        if self._count_words_in_prompt(prompt) >= 1000:
            print(" - Shortening prompt")
            prompt = self._shorten_prompt(prompt)
            logging.warn(prompt)
        
        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=1000,
            temperature=1.1,
            response_format={
                "type": "json_object"
            }
        )
        return self._parse_json(response.choices[0].message.content)
    
    def generate_regional_drama(self, region, world_info='', style_input=''):
        prompt = """
        INSTRUCTIONS: Review all of the characteristics of the selected region and develop an interesting task, question or quest for the region.
        Please return a paragraph and be merely a prompt or suggestion used for direction.
        Please return this information in JSON format. Please always provide correct json syntax. Use object notation, not arrays. 
        This drama is occurring in {}, a {}. 
        Short description: {}\n
        World Info: {}
        Writing Style: {}
        Example JSON:
        """.format(
            region['LocationName'],
            region['LocationType'],
            region['ShortDescription'],
            world_info,
            style_input
        )
        prompt += "{\'title\' : \'A unique title to describe the situation\',\'description\' : \'brief prompt for a short local adventure or challenge.\'}"
        
        prompt+="The sitatuation may involve the following characters or locations:"
        prompt+="\nCharacters:\n"
        for i in region['characters']:
            if 'personality' in region['characters'][i]:
                prompt += f" - {region['characters'][i]['personality']}"
            
        prompt+="\nSignificant locations:\n"
        for i in region['locations']:
            if 'lore' in region['locations'][i]:
                prompt+=f" - {region['locations'][i]['lore']}"
    
        if self._count_words_in_prompt(prompt) >= 1000:
            print(" - Shortening prompt")
            prompt = self._shorten_prompt(prompt)
            logging.warn(prompt)
        
        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")         
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=1000,
            temperature=1.1,
            response_format={
                "type": "json_object"
            }
        )
        return self._parse_json(response.choices[0].message.content)
    
    def generate_random_encounter(self, region, world_info):
        prompt = """
        INSTRUCTIONS: Review all of the characteristics of the selected region and create a short but interesting random encounter.
        Please return a short paragraph describing a detail description of the situation or opportunity. Some can be good, some situations can be bad.
        Please return this information in JSON format. Please always provide correct json syntax. Use object notation, not arrays. 
        The output should consist of one object: "encounter"
        This drama is occurring in {}, a {}. 
        Short description: {}\n
        World Info: {}
        Example JSON:
        """.format(
            region['LocationName'],
            region['LocationType'],
            region['ShortDescription'],
            world_info
        )
        prompt += "{\'description\' : \'A short description of the event that is occurring at present.\',\'opportunity\' : \'A very short segway into why a person would get involved, if they have a choice at all.\'}"
        
        prompt += "Characters:\n"
        for character in region['characters']:
            if 'description' in character and 'personality' in character:
                prompt += f" - {character['description']}. {character['personality']}."
            else:
                logging.warn("missing important character elements")
            
        prompt += "Significant locations:\n"
        for location in region['locations']:
            if 'description' in location and 'lore' in location:
                prompt += f" - {location['description']}. {location['lore']}."
            else:
                logging.warn("missing important location  elements")
                
        if self._count_words_in_prompt(prompt) >= 1000:
            print(" - Shortening prompt")
            prompt = self._shorten_prompt(prompt)
            logging.warn(prompt)
        
        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")         
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=1000,
            temperature=1.1,
            response_format={
                "type": "json_object"
            }
        )
        return self._parse_json(response.choices[0].message.content)
    
    def _parse_url(self, image_url, image_storage):
        # Am I overwriting the basic image storage, probably.
        if image_storage:
            self.image_storage=image_storage
        
        # Does this folder exist? make it so.
        if not os.path.exists(self.image_storage):
            os.makedirs(self.image_storage)
        
        # Create a random short jpg file name
        # TODO: Get character names for image?
        filename = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '.jpg'
        file_path = os.path.join(self.image_storage, filename)
        
        # Download the image located at the generated URL and save it
        image_data = requests.get(image_url).content
        with open(file_path, 'wb') as handler:
            handler.write(image_data)
        
        # Return the relative path of the downloaded image
        return file_path
    
    def _summarize_context(self, input_prompt):
        prompt = "Please summarize the user's input text into a shortened and organized format optimized for use later as context for language models:\n"
        prompt += input_prompt
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=self._create_messages(prompt),
            max_tokens=1000,
        )
        time.sleep(5)
        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        logging.debug(f">> OUTPUT FROM LLM:\n{response.choices[0].message.content}\n")
        return response.choices[0].message.content
    
    def _shorten_prompt(self, input_prompt):
        prompt = """
        This prompt is too long. 
        Please optimize this prompt for comsumption by gpt-4o-mini.
        If JSON output is requested, please be sure that JSON output is specificed in the prompt. 
        Summarize stories to single sentences or cut unneeded details:\n"""
        prompt += input_prompt
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=self._create_messages(prompt),
            max_tokens=1000,
        )
        output_content = response.choices[0].message.content
        if 'JSON' not in response.choices[0].message.content:
            output_content=response.choices[0].message.content
            output_content += "\nReturn this information in JSON format." 
        
        time.sleep(5)
        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        logging.debug(f">> OUTPUT FROM LLM:\n{response.choices[0].message.content}\n")
        return output_content
    
    def _fix_json_response(self, input_response):
        prompt = "This json data is too long and not in properly formatted. Please make the content shorter and format in proper JSON. Input to be revised: \n"
        prompt += input_response
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=1000,
            response_format={
                "type": "json_object"
            }    
        )
        time.sleep(5)
        logging.warn(" --- Incomplete JSON data fix attempted.")
        return response.choices[0].message.content
    
    def _optimize_dalle_prompt(self, input_prompt):
        prompt = "Optimize the prompt below for DALL-E 3. Include wording to avoid using written text UNLESS it is the name of the location or person.\n"
        prompt += input_prompt
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=1000,
        )
        time.sleep(5)
        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        logging.debug(f">> OUTPUT FROM LLM:\n{response.choices[0].message.content}\n")
        return response.choices[0].message.content
    
    def _count_words_in_prompt(self, prompt_string):
        # Split the prompt string by whitespace and filter out any empty strings
        words = prompt_string.split()
        # Return the number of words
        return len(words)
    
    def generate_character_portrait(self, character_description, world_info, illustration_style='', image_storage='character_illustrations'):
        
        # Do not use promptless
        if not character_description:
            print("Warning: character_description cannot be empty. Operation aborted.")
            return None
        
        prompt = f"""
        Generate this person's portrait based on the following description: {character_description}
        Illustration style: {illustration_style}
        """.strip(' \t\n\r')
        
        prompt = self._optimize_dalle_prompt(prompt)
        logging.debug(f"<< INPUT TO DALLE:\n{prompt}\n")
        try:
            response = openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
        except openai.BadRequestError as e:
            error_message = f"BadRequestError: {str(e)}\nPrompt: {prompt}\n"
            logging.error(error_message)
            print("An error occurred while generating the image. Details have been logged.")
            return None
        
        # Get the generated image URL
        return self._parse_url(response.data[0].url, image_storage)
        
    def generate_location_maps(self, location_description, world_info, illustration_style='', image_storage='location_maps'):
        
        # Do not use promptless
        if not location_description:
            print("Warning: character_description cannot be empty. Operation aborted.")
            return None
        
        prompt = f"""
        Draw a stylized isometric map of this place: {location_description}
        Illustration style: {illustration_style}
        """
        
        prompt = self._optimize_dalle_prompt(prompt)
        logging.debug(f"<< INPUT TO DALLE:\n{prompt}\n")
        try:
            response = openai.images.generate(
                model="dall-e-3", # temporary
                prompt=prompt.strip(' \t\n\r'),
                size="1024x1024",
                quality="standard",
                n=1
            )
        except openai.BadRequestError as e:
            error_message = f"BadRequestError: {str(e)}\nPrompt: {prompt}\n"
            logging.error(error_message)
            print(" - An error occurred while generating the image. Details have been logged.")
            return None
        
        # Get the generated image URL
        return self._parse_url(response.data[0].url, image_storage)