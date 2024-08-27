class ContextExtractor:
    def __init__(self, prompt_file_path):
        self.prompt_file_path = prompt_file_path

    def extract_context(self):
        with open(self.prompt_file_path, "r") as file:
            context = file.read()
        return context
