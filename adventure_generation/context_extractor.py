import os
import json

class ContextExtractor:
    
    def __init__(self, input_context_file, input_image_file, input_settings_file):
        
        # Verify File paths
        if not os.path.isfile(input_image_file):
            raise FileNotFoundError(f"Input image file does not exist or is unreadable: {input_image_file}")
        if not os.path.isfile(input_context_file):
            raise FileNotFoundError(f"Input context file does not exist or is unreadable: {input_context_file}")
        if not os.path.isfile(input_settings_file):
            raise FileNotFoundError(f"Input settings file does not exist or is unreadable: {input_settings_file}")
        
        # Save File paths
        self.input_image_file = input_image_file
        self.input_context_file = input_context_file
        self.input_settings_file = input_settings_file
        
        # Parse File paths
        self.base_context = self._read_context() # this should be plain text .txt
        self.settings = self._read_settings() # this should be json
        
    def _read_context(self):
        with open(self.input_context_file, "r") as file:
            context = file.read()
        return context
    
    def _read_settings(self):
        try:
            if not os.path.isfile(self.input_settings_file):
                raise RuntimeError(f"Settings file does not exist: {self.input_settings_file}")
            
            with open(self.input_settings_file, "r") as file:
                settings = json.load(file)
            
            if not isinstance(settings, dict):
                raise RuntimeError(f"Expected JSON object but got {type(settings)}")
            
            return settings
        except Exception as e:
            raise RuntimeError(f"Failed to read settings file: {e}")
    
    
    def get_context(self):
        return self.base_context
    
    
    def get_input_imagepath(self):
        return self.input_image_file
    
    
    def get_visual_style(self):
        return self.settings['visual_style']
    
    
    def get_writing_style(self):
        return self.settings['writing_style']
    
    
    def get_cover_style(self):
        return self.settings['cover_style']
