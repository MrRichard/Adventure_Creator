import requests
import json
import base64
from PIL import Image
import io
import os
import random
import string


class Automatic1111ImageGenerator:
    def __init__(self, base_url="http://localhost:7860"):
        
        # Allow the user to specify and IP address for an AUTOMATIC1111 server
        if "AC_AUTO1111_SERVER" in os.environ:
            self.base_url="http://{}:7860".format(
                os.getenv("AUTO1111")
            )
        else:
            self.base_url = base_url
            
            
        self.base_url = base_url
        self.api_endpoint = f"{self.base_url}/sdapi/v1/txt2img"

    def _send_request(self, payload):
        """Send a POST request to the AUTOMATIC1111 server and return the response."""
        response = requests.post(self.api_endpoint, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

    def generate_character_portrait(self, prompt):
        prompt=f"Generate a character portrait based on the provided prompt. Must be safe for work:\n{prompt} "
        payload = {
            "prompt": prompt,
            "steps": 30,
            "width": 768,
            "height": 768,
            "sampler_name": "Euler a",
            "seed": -1,
            "cfg_scale": 7,
            "negative_prompt": self.mega_negative_prompt()
        }

        # Sending request
        response = self._send_request(payload)
        if response and "images" in response:
            output_dir = "character_illustrations"
            os.makedirs(output_dir, exist_ok=True)

            filename = (
                "".join(random.choices(string.ascii_letters + string.digits, k=8))
                + ".jpg"
            )
            file_path = os.path.join(output_dir, filename)

            for i, img_data in enumerate(response["images"]):
                image = Image.open(io.BytesIO(base64.b64decode(img_data)))
                image.save(file_path)
                print(f"Character portrait saved as {file_path}")

            return file_path

    def generate_location_maps(self, prompt):
        prompt=f"Generate a detailed isometric map based on the provided prompt:\n{prompt} "
        payload = {
            "prompt": prompt,
            "steps": 30,
            "width": 768,
            "height": 768,
            "sampler_name": "Euler a",
            "seed": -1,
            "cfg_scale": 7,
            "negative_prompt": self.mega_negative_prompt()
        }

        # Sending request
        response = self._send_request(payload)
        if response and "images" in response:
            output_dir = "location_maps"
            os.makedirs(output_dir, exist_ok=True)

            filename = (
                "".join(random.choices(string.ascii_letters + string.digits, k=8))
                + ".jpg"
            )
            file_path = os.path.join(output_dir, filename)

            for i, img_data in enumerate(response["images"]):
                image = Image.open(io.BytesIO(base64.b64decode(img_data)))
                image.save(file_path)
                print(f"Location Map saved as as {file_path}")

            return file_path

    def mega_negative_prompt(self):
        return """"""
