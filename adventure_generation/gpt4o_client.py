import os
import openai

class GPT4oClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        self.system_role = "You are a ttrpg game world creator and game designer assistant. You help build the setting for amazing adventures."
        self.system_role_msg = {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": f"{self.system_role }"
                    }
                ]
                }

    def _create_messages(self, prompt):
        msgs=[self.system_role_msg, {"role": "user", "content": [{"type": "text","text": f"{prompt}"}]}]
        return msgs

    # this is the step 1 map review    
    def generate_landscape_description(self, base64_image):
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                self.system_role_msg,
                {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": "Review this map carefully and create a json file that contains the names and brief descriptions of the locations. Specifically, look for big and small towns, and named natural features. For each item create a json object with this information:\n- LocationName, LocationType, ShortDescription\n\n* The LocationType should be one of these items [ bigTown, smallTown, NaturalFeature, other ]. The shortDescription should be minimal. One to two lines at most."
                    },
                    {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
                }
            ],
            max_tokens=1000,
            temperature=1.25,
            response_format={
                "type": "json_object"
            }
        )
        return response.choices[0].message.content

    def embellish_context(self, context):
        prompt = f"The user has provided this description of the world: {context}. Please expand upon this description by adding new details, simple fictional history and world context."
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=750
        )
        return response.choices[0].text.strip()
    
    def generate_region_description(self, prompt):
        prompt += """INSTRUCTIONS: Create a creatively written paragraph that embellishes on the shortDescription. 
        Create several NPC characters appropriate for the context that dwell in this location. Write a brief bio for each character as well as a physical description or appearance.
        Create several signficant locations appropriate for existing at this location. Write a brief description of the physical description and appearance of the place.
        Please return this information in JSON format. Utilize the elements: "description", "locations" and "characters". The characters object should have sub elements for "physicalDescription" and "personality". Use object notation, not arrays.
        Locations should only have "description" elements. Please always provide correct json syntax, even if that means reducing the amount of locations or characters.
        """
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=1000,
            response_format={
                "type": "json_object"
            }
        )
        return response.choices[0].message.content

    def generate_plot_drama(self, world_description):
        prompt = f"World Description: {world_description}\nGenerate plot drama."
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._create_messages(prompt),
            max_tokens=500
        )
        return response.choices[0].text.strip()

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