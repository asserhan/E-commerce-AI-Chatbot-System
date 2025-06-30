from config import Config
import os

class ModelSelector:
    def __init__(self):
        self.models = Config.AI_MODELS
        self.current_index = 0

    def get_current_model(self):
        model = self.models[self.current_index]
        # Get the token from env
        model['token'] = os.getenv(model['token_env'])
        return model

    def switch_to_next_model(self):
        self.current_index = (self.current_index + 1) % len(self.models)
        return self.get_current_model()
