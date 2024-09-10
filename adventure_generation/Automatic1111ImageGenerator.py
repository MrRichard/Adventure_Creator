import requests
import json
import base64
from PIL import Image
import io
import os
import random
import string


class Automatic1111ImageGenerator:
    def __init__(self, base_url="http://192.168.1.115:7860"):
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
        prompt=f"Generate a character portrait based on the provided prompt.:\n{prompt} "
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
        return """
            ai-generated, artifact, artifacts, bad quality, bad scan, blurred, 
            blurry, compressed, compression artifacts, corrupted, dirty art scan, 
            dirty scan, dithering, downsampling, faded lines, frameborder, grainy, 
            heavily compressed, heavily pixelated, high noise, image noise, low dpi, 
            low fidelity, low resolution, lowres, moire pattern, moiré pattern, 
            motion blur, muddy colors, noise, noisy background, overcompressed, 
            pixelation, pixels, poor quality, poor lineart, scanned with errors,
            scan artifact, scan errors, very low quality, visible pixels BREAK amateur, 
            amateur drawing, bad anatomy, bad art, bad aspect ratio, bad color, bad coloring, 
            bad composition, bad contrast, bad crop, bad drawing, bad image, bad lighting, 
            bad lineart, bad perspective, bad photoshop, bad pose, bad proportions, bad shading, 
            bad sketch, bad trace, bad typesetting, bad vector, beginner, black and white, 
            broken anatomy, broken pose, cartoon, clashing styles, color error, color issues, 
            color mismatch, deformed, dirty art, disfigured, displeasing, distorted, 
            distorted proportions, drawing, dubious anatomy, duplicate, early, 
            exaggerated limbs, exaggerated pose, flat colors, gross proportions, 
            incomplete, inconsistent proportions, inconsistent shading, inconsistent style, 
            incorrect anatomy, lazy art, long neck, low contrast, low detail, low detail background, 
            low effort, low quality background, malformed limbs, messy, messy drawing, messy lineart, 
            misaligned, mutated hands, mutation, mutilated, no shading, off center, off model, 
            off model errors, off-model, poor background, poor color, poor coloring, 
            poorly colored, poorly drawn, poorly drawn face, poorly drawn hands, 
            poorly proportioned, poorly scaled, poorly shaded, quality control, 
            questionable anatomy, questionable quality, random background, rough, rough drawing, 
            rough edges, rough sketch, rushed, shading error, sketch, sketchy, smudged, smudged lines, 
            symmetrical, terrible quality, too many fingers, twisted, ugly, unclear, uncolored, 
            uncoloured, under saturated, underexposed, uneven lines, unfinished, unfinished lineart, 
            unpolished, worst quality, wrong anatomy, wrong proportions BREAK bar censor, censor, 
            censor mosaic, censored, filter abuse, instagram filter, mosaic censoring, over filter, 
            over saturated, over sharpened, overbrightened, overdarkened, overexposed, overfiltered, 
            oversaturated BREAK aliasing, anatomy error, anatomy mistake, camera aberration, chromatic 
            aberration, cloned face, color banding, cribbed from, cropped, draft, emoji, error, 
            extra arms, extra digits, extra fingers, extra legs, extra limbs, fused fingers, gradient background, 
            improper cropping, jagged edges, jpeg artifacts, missing, missing arms, missing legs, needs retage, 
            no background, obstructed view, overlay text, placeholder, style mismatch, stylistic clash, 
            tagme BREAK empty background, simple background, white background BREAK artist name, artist signature, 
            artist unknown, signature, stolen artwork, username, watermark, watermark text, watermarked, 
            web address, logo, patreon logo, sample watermark, sticker, sticker overlay, abstract, 
            icon overlay, meme, monochrome, ms paint, pixel art, screencap, symetrical"""
