import os
import sys
from ollama import Client
import json
import requests
import string
import random
from adventure_generation.JsonStructures import JsonStructures

# To prevent rate limit issues
import time

# Add logging to help track prompt issues
import logging

# Configure logging
logging.basicConfig(
    filename="llm_usage.log", level=logging.NOTSET, format="%(asctime)s - %(message)s"
)


class ollamaClient:

    def __init__(self):
        self.api_key = "ollama"
        self.base_url = "http://192.168.1.115:11434"
        self.client = Client(host=self.base_url)
        self.jstructs = JsonStructures()
        self.general_use_model = "gemma2:9b"

        logging.info("Ollama NATIVE Client initiated")

        self.system_role = """
        You are a ttrpg game world creator and game designer assistant. 
        You help build the setting for amazing adventures and weave a story with opportunity for interaction.
        """
        self.system_role_msg = {"role": "system", "content": f"{self.system_role}"}
        self.image_storage = "images"

    # This service function helps create a "messages" variable for LLM APIs
    def _create_messages(self, prompt):
        msgs = [self.system_role_msg, {"role": "user", "content": f"{prompt}"}]

        return msgs

    # This service function parses the JSON output from the LLM
    def _parse_json(self, json_inputs):
        try:
            dict_output = json.loads(json_inputs)
        except json.decoder.JSONDecodeError as e:
            logging.warning(f"Failed to decode JSON. Error: {e}")
            abbreviated_json = self._fix_json_response(json_inputs)
            dict_output = json.loads(abbreviated_json)

        # Let's add a delay to stop hitting ratelimits
        time.sleep(1)

        logging.debug(f"<<< OUTPUT FROM LLM:\n{json_inputs}")

        return dict_output

    # This service function hands the download and storing of DALL-E Image URL responses
    def _parse_url(self, image_url, image_storage):
        # Am I overwriting the basic image storage, probably.
        if image_storage:
            self.image_storage = image_storage

        # Does this folder exist? make it so.
        if not os.path.exists(self.image_storage):
            os.makedirs(self.image_storage)

        # Create a random short jpg file name
        # TODO: Get character names for image?
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

    # This service function organizes and summarizes the users initial input txt
    def _summarize_context(self, input_prompt):
        prompt = "Please summarize the user's input text into a shortened and organized format optimized for use later as context for language models:\n"
        prompt += input_prompt
        response = self.client.chat(
            model=self.general_use_model,
            messages=self._create_messages(prompt),
        )
        time.sleep(1)
        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")

        return response["message"]["content"]

    # This service function shorten generated prompts that are too long
    def _shorten_prompt(self, input_prompt):
        prompt = """
        This prompt is too long. 
        Please optimize this prompt for comsumption by an Open Source large Language model.
        If JSON output is requested, please be sure that JSON output is specificed in the prompt. 
        Summarize stories to single sentences or cut unneeded details:\n"""
        prompt += input_prompt
        response = self.client.chat(
            model=self.general_use_model,
            messages=self._create_messages(prompt),
        )
        output_content = response["message"]["content"]
        if "JSON" not in response["message"]["content"]:
            output_content = response["message"]["content"]
            output_content += "\nReturn this information in JSON format."

        time.sleep(1)
        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        logging.debug(f">> OUTPUT FROM LLM:\n{response['message']['content']}\n")
        return output_content

    # This service function attempts to fix any JSON that cannot be loaded,
    # Possibly due to LLM error
    def _fix_json_response(self, input_response):
        prompt = "This json data is not in properly formatted. Please format output in proper JSON. Input to be revised: \n"
        prompt += input_response
        response = self.client.chat(
            model=self.general_use_model,  # this might be sketchy.
            messages=self._create_messages(prompt),
            format="json",
        )
        time.sleep(1)
        logging.warning(" --- Incomplete JSON data fix attempted.")
        return response["message"]["content"]

    # This service function gets the size of the string
    # This is how we determine if a prompt is too large for a model
    def _get_size_of_string(self, string_var):
        # Get the number of bytes of the string
        byte_size = sys.getsizeof(string_var)
        # Convert bytes to kilobytes
        kb_size = byte_size / 1024
        return kb_size
    
    # This service function strips a descriptive prompt down to keywords for opensource sd models
    def optimize_for_stable_diffusion(self, input_prompt, visual_style):
        prompt = (
            "Optimize the following prompt for Stable Diffusion by reducing it to a single line of comma-separated keywords. "
            "The keywords should focus on description, styling, texture, and lighting.\n"
            f"Input prompt: {input_prompt}\n"
            f"Visual Style: {visual_style}\n"
        )

        response = self.client.chat(
            model=self.general_use_model,
            messages=self._create_messages(prompt),
        )

        # Adding a delay to prevent hitting rate limits
        time.sleep(1)
        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        logging.debug(f">> OUTPUT FROM LLM:\n{response['message']['content']}\n")
        return response["message"]["content"].strip()


    def generate_detailed_region_description(self, region, world_info="", style_input=""):
        if region == "":
            return {}

        prompt = """
        INSTRUCTIONS: Expand upon the simple description for this region:
        Region Name: {} - a {}.
        Region Short Description: {}
        World Info: {}
        Writing Style: {}
        Please return this information in JSON format. Please always provide correct json syntax.
        If data doesn't fit predefined fields within a section, use the "other" field for that section.
        Use object notation, not arrays. Store these under "regionDetails".
        Example JSON: 
        """.format(
            region["LocationName"],
            region["LocationType"],
            region["ShortDescription"],
            world_info,
            style_input,
        )
        prompt += "{'description' : 'An example descriptive paragraph','lore' : 'Example history, mood or lore of this region in one paragraph'}"

        if self._get_size_of_string(prompt) >= 90:
            print(" - Shortening prompt")
            prompt = self._shorten_prompt(prompt)
            logging.warning(prompt)

        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        logging.debug(self._create_messages(prompt))

        response = self.client.chat(
            model=self.general_use_model, messages=self._create_messages(prompt), format="json"
        )
        return self._parse_json(response["message"]["content"])


    def generate_location(self, region, world_info="", style_input=""):
        prompt = """
        INSTRUCTIONS: Create a fictional signficant locations for the location of {}, a {}.
        Region Short Description: {}
        World Info: {}
        Writing Style: {}
        Write a brief but creative description of the physical description and appearance of a place.
        Please return this information in JSON format. Please always provide correct json syntax. 
        If data doesn't fit predefined fields within a section, use the "other" field for that section.
        Use object notation, not arrays.
        Example JSON:
        """.format(
            region["LocationName"],
            region["LocationType"],
            region["ShortDescription"],
            world_info,
            style_input,
        )
        prompt += self.jstructs.generate_location()

        if self._get_size_of_string(prompt) >= 90:
            print(" - Shortening prompt")
            prompt = self._shorten_prompt(prompt)
            logging.warning(prompt)

        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        response = self.client.chat(
            model=self.general_use_model, messages=self._create_messages(prompt), format="json"
        )
        return self._parse_json(response["message"]["content"])

    def generate_character(self, region, world_info="", style_input=""):
        prompt = """
        INSTRUCTIONS: Create a fictional signficant character for the location of {}, a {}.
        Region Short Description: {}
        World Info: {}
        Writing Style: {}
        Please return this information in JSON format. Please always provide correct json syntax.
        If data doesn't fit predefined fields within a section, use the "other" field for that section.
        Use object notation, not arrays.
        Example JSON: 
        """.format(
            region["LocationName"],
            region["LocationType"],
            region["ShortDescription"],
            world_info,
            style_input,
        )
        prompt += self.jstructs.generate_character()

        if self._get_size_of_string(prompt) >= 90:
            print(" - Shortening prompt")
            prompt = self._shorten_prompt(prompt)
            logging.warning(prompt)

        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        response = self.client.chat(
            model=self.general_use_model, messages=self._create_messages(prompt), format="json"
        )
        return self._parse_json(response["message"]["content"])

    def generate_regional_drama(self, region, world_info="", style_input=""):
        prompt = """
        INSTRUCTIONS: Review all of the characteristics of the selected region and develop an interesting task, question or quest for the region.
        Please return a paragraph and be merely a prompt or suggestion used for direction.
        Please return this information in JSON format. Please always provide correct json syntax.
        Use object notation, not arrays.
        If data doesn't fit predefined fields within a section, use the "other" field for that section.
        This drama is occurring in {}, a {}. 
        Short description: {}\n
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
        prompt += self.jstructs.generate_quest()
        prompt += "\nThe situation may involve the following characters or locations:"
        prompt += "\nCharacters:\n"
        for i in region["characters"]:
            if "personality" in region["characters"][i]:
                prompt += f" - {region['characters'][i]['personality']}"

        prompt += "\nSignificant locations:\n"
        for i in region["locations"]:
            if "lore" in region["locations"][i]:
                prompt += f" - {region['locations'][i]['lore']}"

        if self._get_size_of_string(prompt) >= 90:
            print(" - Shortening prompt")
            prompt = self._shorten_prompt(prompt)
            logging.warning(prompt)

        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        response = self.client.chat(
            model=self.general_use_model, messages=self._create_messages(prompt), format="json"
        )
        return self._parse_json(response["message"]["content"])

    def generate_random_encounter(self, region, world_info):
        prompt = """
        INSTRUCTIONS: Review all of the characteristics of the selected region and create a short but interesting random encounter.
        Please return a short paragraph describing a detail description of the situation or opportunity. Some can be good, some situations can be bad.
        Please return this information in JSON format. Please always provide correct json syntax.
        Use object notation, not arrays.
        If data doesn't fit predefined fields within a section, use the "other" field for that section.
        This drama is occurring in {}, a {}. 
        Short description: {}\n
        World Info: {}
        Example JSON:
        """.format(
            region["LocationName"],
            region["LocationType"],
            region["ShortDescription"],
            world_info,
        )
        prompt += self.jstructs.generate_random_encounter()
        prompt += "\nThe situation may involve the following characters or locations:"
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

        if self._get_size_of_string(prompt) >= 90:
            print(" - Shortening prompt")
            prompt = self._shorten_prompt(prompt)
            logging.warning(prompt)

        logging.debug(f"<< INPUT TO LLM:\n{prompt}\n")
        response = self.client.chat(
            model=self.general_use_model, messages=self._create_messages(prompt), format="json"
        )
        return self._parse_json(response["message"]["content"])
    
