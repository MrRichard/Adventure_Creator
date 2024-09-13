import os
import openai
import json
import requests
import string
import random
import sys

from adventure_generation.JsonStructures import JsonStructures

# To prevent rate limit issues
import time

# Add logging to help track prompt issues
import logging

# Configure logging
logging.basicConfig(
    filename="llm_usage.log", level=logging.DEBUG, format="%(asctime)s - %(message)s"
)


class GPT4oClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        self.system_role = """
        You are a ttrpg game world creator and game designer assistant. 
        You help build the setting for amazing adventures and weave a story with opportunity for interaction.
        """
        self.system_role_msg = {
            "role": "system",
            "content": [{"type": "text", "text": f"{self.system_role}"}],
        }
        self.image_storage = "images"
        self.jstructs = JsonStructures()
        logging.info("OpenAI Client initiated")

    # Service function to create messages for API calls
    def _create_messages(self, prompt):
        msgs = [
            self.system_role_msg,
            {"role": "user", "content": [{"type": "text", "text": f"{prompt}"}]},
        ]
        return msgs

    # Service function to parse output json from API
    def _parse_json(self, json_inputs):
        try:
            dict_output = json.loads(json_inputs)
        except json.decoder.JSONDecodeError as e:
            logging.warning(f"Failed to decode JSON. Error: {e}")
            abbreviated_json = self._fix_json_response(json_inputs)
            dict_output = json.loads(abbreviated_json)

        # Let's add a delay to stop hitting ratelimits
        time.sleep(5)

        # Log EVERY output from LLM to DEBUG
        logging.debug(f"<<< OUTPUT FROM LLM:\n{json_inputs}")

        return dict_output
    
    # Service function for downloading and saving DALL-E images
    def _parse_url(self, image_url, image_storage):
        # Am I overwriting the basic image storage, probably.
        if image_storage:
            self.image_storage = image_storage

        # Does this folder exist? make it so.
        if not os.path.exists(self.image_storage):
            os.makedirs(self.image_storage)

        # Create a random short jpg file name
        # TODO: Get character names for image? Not a high priority.
        filename = (
            "".join(random.choices(string.ascii_letters + string.digits, k=8)) + ".jpg"
        )
        file_path = os.path.join(self.image_storage, filename)

        # Download the image located at the generated URL and save it
        image_data = requests.get(image_url).content
        with open(file_path, "wb") as handler:
            handler.write(image_data)

        # Return the relative path of the downloaded image
        return file_path

    # Service function for summarizing the user's input content 
    def _summarize_context(self, input_prompt):
        prompt = "Please summarize the user's input text into a shortened and organized format optimized for use later as context for language models:\n"
        prompt += input_prompt
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=self._create_messages(prompt),
            max_tokens=1000,
        )
        time.sleep(10)
        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        logging.debug(f">> OUTPUT FROM LLM:\n{response.choices[0].message.content}\n")
        return response.choices[0].message.content

    # Service function for summarizing really long content
    def _shorten_prompt(self, input_prompt):
        prompt = """
        This prompt is too long. 
        Please optimize this prompt for comsumption by gpt-4o-mini.
        If JSON output is requested, please be sure that JSON output is specified in the prompt. 
        Summarize stories to single sentences or cut unneeded details. Be brief. Do not include any headers or unneccessary text. Just the summay text, please:\n"""
        prompt += input_prompt
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=self._create_messages(prompt),
            max_tokens=1000,
        )
        output_content = response.choices[0].message.content
        if "JSON" not in response.choices[0].message.content:
            output_content = response.choices[0].message.content
            output_content += "\nReturn this information in JSON format."

        time.sleep(5)
        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        logging.debug(f">> OUTPUT FROM LLM:\n{response.choices[0].message.content}\n")
        return output_content

    # Service function for attempting to repair broken or incomplete json
    def _fix_json_response(self, input_response):
        prompt = "This json data is too long and not in properly formatted. Please make the content shorter and format in proper JSON. Input to be revised: \n"
        prompt += input_response
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=1000,
            response_format={"type": "json_object"},
        )
        time.sleep(5)
        logging.warning(" --- Incomplete JSON data fix attempted.")
        return response.choices[0].message.content

    # This service function is for making good DALL-E 3 prompts
    def _optimize_dalle_prompt(self, input_prompt):
        prompt = """
        Optimize the prompt below for DALL-E 3. 
        Be sure to carefully select wording to best fit the visual style specified by the user.
        Think of the artist medium and color palette when considering how to best render the lighting.
        Good composition will be greatly prized by the audience.
        Include wording to avoid using written text UNLESS it is the name of the location or person.\n
        """
        prompt += f"PROMPT: {input_prompt}"
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=1000,
        )
        time.sleep(5)
        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        logging.debug(f">> OUTPUT FROM LLM:\n{response.choices[0].message.content}\n")
        return response.choices[0].message.content
    
    # This service function is used to count the words in a prompt [ DEPRECATED ]
    def _count_words_in_prompt(self, prompt_string):
        # Split the prompt string by whitespace and filter out any empty strings
        words = prompt_string.split()
        # Return the number of words
        return len(words)

    # This service function is used to estimate the size of a prompt
    def _get_size_of_string(self, string_var):
        # Get the number of bytes of the string
        byte_size = sys.getsizeof(string_var)
        # Convert bytes to kilobytes
        kb_size = byte_size / 1024
        return kb_size

    # This is the step 1 map review
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
                    Specifically, look for big and small towns, and named natural features. Pay attention to each towns position relative to natural features like mountains, forests, or the coast. 
                    For each item create a json object with this information:\n- LocationName, LocationType, ShortDescription\n\n* 
                    The LocationType should be one of these items [ bigTown, smallTown, NaturalFeature, other ]. 
                    The shortDescription should be one to two lines at most.
                    Please pay detailed attention to the JSON formatting and using the correct key as described in the example. Incorrect key names breaks the program.
                    Example formatting: {\"regions\": [{\"LocationName\": \"\",\"LocationType\": \"\",\"ShortDescription\": \"\"},{\"LocationName\": \"\",\"LocationType\": \"\",\"ShortDescription\": \"\"}]}
                    """,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                },
            ],
            max_tokens=2000,
            temperature=1.25,
            response_format={"type": "json_object"},
        )
        return self._parse_json(response.choices[0].message.content)

    # For each region, we generate a detailed description and some lore
    def generate_detailed_region_description(
        self, region, world_info="", style_input=""
    ):
        if region == "":
            return {}

        prompt = """
        INSTRUCTIONS: Expand upon the simple description for this region. 
        Be sure to refer to the user-provided World Info and utilize the Writing Style.
        Region Name: {} - a {}.
        Region Short Description: {}
        World Info: {}
        Writing Style: {}
        Please return this information in JSON format. Please always provide correct json syntax. Use object notation, not arrays.
        This content should be in the "regionDetails" object. Use this template:
        Example JSON: 
        """.format(
            region["LocationName"],
            region["LocationType"],
            region["ShortDescription"],
            world_info,
            style_input,
        )
        prompt += "{'description' : 'An example descriptive paragraph','lore' : 'Example history, mood or lore of this region in one paragraph'}"

        if self._get_size_of_string(prompt) >= 15:
            print(" - Shortening prompt")
            prompt = self._shorten_prompt(prompt)
            logging.warning(prompt)

        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=1000,
            temperature=1.1,
            response_format={"type": "json_object"},
        )
        return self._parse_json(response.choices[0].message.content)

    # Generate sublocations in the region
    def generate_location(self, region, world_info="", style_input=""):
        prompt = """
        INSTRUCTIONS: Create a fictional signficant locations for the location of {}, a {}.
        Write a brief but creative description of the physical description and appearance of a place.
        This place maybe any location found in the region such as a farm, an inn or a famous building.
        Be creative and please pay attention to the World Info and Region description. 
        Well-written content that feels well placed in the world will be greatly appreciated by the reader.
        Please return this information in JSON format. Please always provide correct json syntax. Use object notation, not arrays.
        If data doesn't fit predefined fields within a section, use the "other" field for that section.
        Region Short Description: {}
        World Info: {}
        Writing Style: {}
        Example JSON:
        """.format(
            region["LocationName"],
            region["LocationType"],
            region["ShortDescription"],
            world_info,
            style_input,
        )
        prompt += self.jstructs.generate_location()

        if self._get_size_of_string(prompt) >= 15:
            print(" - Shortening prompt")
            prompt = self._shorten_prompt(prompt)
            logging.warning(prompt)

        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=1000,
            temperature=1.1,
            response_format={"type": "json_object"},
        )
        return self._parse_json(response.choices[0].message.content)

    # Write character 
    def generate_character(self, region, world_info="", style_input=""):
        prompt = """
        INSTRUCTIONS: Create a fictional signficant character for the location of {}, a {}. 
        Please randomly choose a gender for this person. Then, based on the World Info, determine a probability for each race and roll randomly. 
        You can also randomly roll some standard attributes such as "Strength, Charisma, Wisdom, Dexterity, Constituion", but you don't need to report those numbers. Just use them to inform your character development.
        You can also randomly choose if you want this to be a good, bad, or indifferent opportunistic character.
        Interesting characters that seem to belong to their location or have a tie to the region will be valued by the audience. 
        Please return this information in JSON format. Please always provide correct json syntax. Use object notation, not arrays.
        The output should consist of three items: "name", "description" and "personality"
        If data doesn't fit predefined fields within a section, use the "other" field for that section.
        Region Short Description: {}
        World Info: {}
        Writing Style: {}
        Example JSON: 
        """.format(
            region["LocationName"],
            region["LocationType"],
            region["ShortDescription"],
            world_info,
            style_input,
        )
        prompt += self.jstructs.generate_character()

        if self._get_size_of_string(prompt) >= 15:
            print(" - Shortening prompt")
            prompt = self._shorten_prompt(prompt)
            logging.warning(prompt)

        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=1000,
            temperature=1.1,
            response_format={"type": "json_object"},
        )
        return self._parse_json(response.choices[0].message.content)

    # Generate quest drama
    def generate_regional_drama(self, region, world_info="", style_input=""):
        prompt = """
        INSTRUCTIONS: Review all of the characteristics of the selected region and develop an interesting dilemma or quest for the region.
        These can be serious things like solving a crime, or mundane things like getting two old friends to forgive each other.
        The generated description should really just be an introduction with limited details. The players and GM can make up the rest, but you are welcome to add a plot-twist or a creative secret the players will uncover. 
        Please return this information in JSON format. Please always provide correct json syntax. Use object notation, not arrays.
        If data doesn't fit predefined fields within a section, use the "other" field for that section.
        This drama is occurring in {}, a {}.\n
        Short description: {}\n
        World Info: {}\n
        Writing Style: {}\n
        Example JSON:
        """.format(
            region["LocationName"],
            region["LocationType"],
            region["ShortDescription"],
            world_info,
            style_input,
        )
        prompt += self.jstructs.generate_quest()
        
        prompt += "The sitatuation may involve the following characters or locations:"
        prompt += "\nCharacters:\n"
        for i in region["characters"]:
            if "personality" in region["characters"][i]:
                prompt += f" - {region['characters'][i]['personality']}"

        prompt += "\nSignificant locations:\n"
        for i in region["locations"]:
            if "lore" in region["locations"][i]:
                prompt += f" - {region['locations'][i]['lore']}"

        if self._get_size_of_string(prompt) >= 15:
            print(" - Shortening prompt")
            prompt = self._shorten_prompt(prompt)
            logging.warning(prompt)

        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=1000,
            temperature=1.1,
            response_format={"type": "json_object"},
        )
        return self._parse_json(response.choices[0].message.content)

    def generate_random_encounter(self, region, world_info):
        prompt = """
        INSTRUCTIONS: Review all of the characteristics of the selected region and create a short but interesting random encounter.
        Unlike a question prompt, this a description of an immediate situation that occurs and the players must react. These can be good or bad.
        For example, the players can stumble across and old beggar who swears to know a dark secret. The players could be ambused by the bandits in a back alley. The players could stumble across a lively festival. 
        I suggest rolling a d10, with 1 being bad or troublesome random encounters, and 10 being pleasant surprises or a golden opportunity. 
        Pay attention to the World Info and Region Description. Events should be relevant to the region that they are in. The audience will enjoy a random enounter that seems probably considering local characters and locations.
        Please return this information in JSON format. Please always provide correct json syntax. Use object notation, not arrays. 
        If data doesn't fit predefined fields within a section, use the "other" field for that section.
        The output should consist of one object: "encounter"
        This drama is occurring in {}, a {}.\n
        Short description: {}\n
        World Info: {}\n
        Example JSON:
        """.format(
            region["LocationName"],
            region["LocationType"],
            region["ShortDescription"],
            world_info,
        )
        prompt += self.jstructs.generate_random_encounter()

        prompt += "Characters:\n"
        for character in region["characters"]:
            if "description" in character and "personality" in character:
                prompt += f" - {character['description']}. {character['personality']}."
            else:
                logging.warning("missing important character elements")

        prompt += "Significant locations:\n"
        for location in region["locations"]:
            if "description" in location and "lore" in location:
                prompt += f" - {location['description']}. {location['lore']}."
            else:
                logging.warning("missing important location  elements")

        if self._get_size_of_string(prompt) >= 15:
            print(" - Shortening prompt")
            prompt = self._shorten_prompt(prompt)
            logging.warning(prompt)

        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=1000,
            temperature=1.1,
            response_format={"type": "json_object"},
        )
        return self._parse_json(response.choices[0].message.content)

    def generate_character_portrait(
        self,
        character_description,
        world_info,
        illustration_style,
        image_storage="character_illustrations",
    ):

        # Do not use promptless
        if not character_description:
            print("Warning: character_description cannot be empty. Operation aborted.")
            return None

        prompt = f"""
        Generate a detailed portrait of face and torso based on the following description: {character_description}
        Single frame. No split frames or mosaics. No text or illumination.\n
        Illustration style: {illustration_style}
        """.strip(
            " \t\n\r"
        )

        prompt = self._optimize_dalle_prompt(prompt)
        logging.debug(f"<< INPUT TO DALLE:\n{prompt}\n")
        try:
            response = openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
        except openai.BadRequestError as e:
            error_message = f"BadRequestError: {str(e)}\nPrompt: {prompt}\n"
            logging.error(error_message)
            print(
                "An error occurred while generating the image. Details have been logged."
            )
            return None

        # Get the generated image URL
        return self._parse_url(response.data[0].url, image_storage)

    def generate_location_maps(
        self,
        location_description,
        world_info,
        illustration_style,
        image_storage="location_maps",
    ):

        # Do not use promptless
        if not location_description:
            print("Warning: character_description cannot be empty. Operation aborted.")
            return None

        prompt = f"""
        Draw a stylized map of this place: {location_description}\n
        Illustration style: {illustration_style}
        """

        prompt = self._optimize_dalle_prompt(prompt)
        logging.debug(f"<< INPUT TO DALLE:\n{prompt}\n")
        try:
            response = openai.images.generate(
                model="dall-e-3", 
                prompt=prompt.strip(" \t\n\r"),
                size="1024x1024",
                quality="standard",
                n=1,
            )
        except openai.BadRequestError as e:
            error_message = f"BadRequestError: {str(e)}\nPrompt: {prompt}\n"
            logging.error(error_message)
            print(
                " - An error occurred while generating the image. Details have been logged."
            )
            return None

        # Get the generated image URL
        return self._parse_url(response.data[0].url, image_storage)
