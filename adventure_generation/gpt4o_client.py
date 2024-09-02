import os
import openai
import json

class GPT4oClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        self.system_role = """
        You are a ttrpg game world creator and game designer assistant. 
        You help build the setting for amazing adventures.
        You want to avoid fantasy tropes and commonly used language, and instead emulate the styles of historical travel writers.
        """
        self.system_role_msg = {"role": "system","content": [{"type": "text","text": f"{self.system_role}"}]}

    def _create_messages(self, prompt):
        msgs=[self.system_role_msg, {"role": "user", "content": [{"type": "text","text": f"{prompt}"}]}]
        return msgs
    
    def _parse_json(self, json_inputs):
        try:
            dict_output = json.loads(json_inputs)
        except json.decoder.JSONDecodeError as e:
            print(f"Failed to decode JSON. Error: {e}")
            return ''
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
                    Example formatting: {"regions": [{"LocationName": "","LocationType": "","ShortDescription": ""},{"LocationName": "","LocationType": "","ShortDescription": ""}]}
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
        return response.choices[0].message.content
    
    def generate_detailed_region_description(self, region=''):
        if region =='':
            return {}
        
        prompt = '''
        INSTRUCTIONS: Expand upon the simple description for this region:
        Region Name: {} - A {}.
        Region Short Description: {}
        Please return this information in JSON format. Please always provide correct json syntax. Use object notation, not arrays.
        This content should be in the "regionDetails" object. Use this template:
        
        The "description" should be used to describe the fictional setting (1-2 paragraphs).
        The "lore" should be used to convey a mood, history or uniqueness to this region (1-2 paragraphs).
        '''.format(
            region['LocationName'],
            region['LocationType'],
            region['ShortDescription']
        )
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
        
    
    def generate_location(self, region):
        prompt = """
        INSTRUCTIONS: Create a fictional signficant locations for the location of {}, a {}.
        Region Short Description: {}
        Write a brief but creative description of the physical description and appearance of a place.
        Please return this information in JSON format. Please always provide correct json syntax. Use object notation, not arrays. 
        The output should consist of two items: "description" and "lore"
        The "description" should be used to describe the fictional setting (1-2 paragraphs).
        The "lore" should be used to convey a mood, history or uniqueness to this site (1-2 paragraphs).
        """.format(
            region['LocationName'],
            region['LocationType'],
            region['ShortDescription']
        )
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
    
    
    def generate_character(self, region):
        prompt = """
        INSTRUCTIONS: Create a fictional signficant character for the location of {}, a {}.
        Region Short Description: {}
        Please return this information in JSON format. Please always provide correct json syntax. Use object notation, not arrays. 
        The output should consist of two items: "description" and "personality"
        The "description" should be used to describe the visible appearance of this character (1-2 paragraphs).
        The "personality" should be used to convey the personality, world view, occupation and quirks of this character (1-2 paragraphs).
        """.format(
            region['LocationName'],
            region['LocationType'],
            region['ShortDescription']
        )
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
    
    def generate_regional_drama(self, region):
        prompt = prompt = """
        INSTRUCTIONS: Review all of the characteristics of the selected region and develop an interesting task, question or quest for the region.
        Please return a paragraph and be merely a prompt or suggestion used for direction.
        Please return this information in JSON format. Please always provide correct json syntax. Use object notation, not arrays. 
        The output should consist of two objects: "title" and "description"
        
        This drama is occurring in {}, a {}. 
        Short description: {}\n
        """.format(
            region['LocationName'],
            region['LocationType'],
            region['ShortDescription']
        )
        
        prompt+="Characters:\n"
        for i in region['characters']:
            prompt+=f" - {region['characters'][i]['description']}. {region['characters'][i]['description']}."
            
        prompt+="Significant locationas:\n"
        for i in region['locations']:
            prompt+=f" - {region['locations'][i]['description']}. {region['locations'][i]['lore']}."
                 
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
    
    def generate_random_encounter(self, region):
        prompt = prompt = """
        INSTRUCTIONS: Review all of the characteristics of the selected region and create a short but interesting random encounter.
        Please return 1-2 paragraphs describing a detail description of the situation. Some can be good, some situations can be bad.
        Please return this information in JSON format. Please always provide correct json syntax. Use object notation, not arrays. 
        The output should consist of one object: "encounter"
        
        This drama is occurring in {}, a {}. 
        Short description: {}\n
        """.format(
            region['LocationName'],
            region['LocationType'],
            region['ShortDescription']
        )
        
        prompt+="Characters:\n"
        for i in region['characters']:
            prompt+=f" - {region['characters'][i]['description']}. {region['characters'][i]['description']}."
            
        prompt+="Significant locationas:\n"
        for i in region['locations']:
            prompt+=f" - {region['locations'][i]['description']}. {region['locations'][i]['lore']}."
                 
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
    
    def generate_character_portrait(self, prompt):
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        return response.data[0].url

    def generate_region_details(self, region):
        prompt = f"Region: {region}\nGenerate region details."
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=500
        )
        return response.choices[0].text.strip()

    def generate_quest_lines(self, region, details, plot_drama):
        prompt = f"Region: {region}\nDetails: {details}\nPlot Drama: {plot_drama}\nGenerate quest lines."
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=500
        )
        return response.choices[0].text.strip()

    def generate_random_encounters(self, region, details):
        prompt = f"Region: {region}\nDetails: {details}\nGenerate random encounters."
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=prompt,
            max_tokens=500
        )
        return response.choices[0].text.strip()
