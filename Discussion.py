import json
from litellm import completion


class ChatbotMemory:
    def __init__(self, file_path=None, load=False):
        self.context = []
        self.file_path = file_path
        if file_path and load:
            try:
                self.load_from_file(file_path)
            except FileNotFoundError:
                pass

    def add_message(self, participant, message):
        self.context.append({'participant': participant, 'message': message})

    def get_context(self):
        return self.context

    def get_context_as_string(self):
        return "\n".join([f"{entry['participant']}: {entry['message']}" for entry in self.context])

    def remove_message(self, participant, message):
        self.context = [entry for entry in self.context if not (entry['participant'] == participant and entry['message'] == message)]

    def save_to_file(self, file_path=None):
        with open(file_path, 'w') as file:
            json.dump(self.context, file)

    def load_from_file(self, file_path=None):
        with open(file_path, 'r') as file:
            self.context = json.load(file)

    

class ChatAgent:
    def __init__(self, name, 
                 task="Please contribute to the discussion provided in the context in the mpst helpful way.", 
                 model="ollama/qwen2.5:14b-instruct-q8_0", 
                 memory=None):
        self.name = name
        self.model=model
        self.memory = memory or ChatbotMemory()

    def system_prompt(self):
        return "You are a "