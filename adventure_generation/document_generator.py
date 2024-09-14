import sys
import os
import json
from jinja2 import Template, Environment, FileSystemLoader

class DocumentGenerator:
    def __init__(self, json_path: str, template_dir: str, output_dir: str):
        self.json_path = json_path
        self.output_dir = output_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def load_json(self):
        with open(self.json_path, 'r') as file:
            return json.load(file)
    
    def generate_html(self):
        data = self.load_json()
        for region in data.get('regions', []):
            region_template = self.env.get_template('region_template.html')
            rendered_html = region_template.render(region=region)
            file_name = f"{region['LocationName'].replace(' ', '_')}.html"
            with open(os.path.join(self.output_dir, file_name), 'w') as file:
                file.write(rendered_html)
    
def main(json_path, template_dir, output_dir):
    generator = DocumentGenerator(json_path, template_dir, output_dir)
    generator.generate_html()
