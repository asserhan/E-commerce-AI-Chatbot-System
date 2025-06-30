import os
from dotenv import load_dotenv

load_dotenv()

class Config:
   SECRET_KEY = os.getenv('SECRET_KEY')
   MONGO_URI = os.getenv('MONGO_URI')
   GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
   CORS_ORIGINS = os.getenv('CORS_ORIGINS')
   
   # AI Model Configurations
   AI_MODELS = [
       {
           "name": "openai-gpt-4.1",
           "endpoint": "https://models.github.ai/inference",
           "model": "openai/gpt-4.1",
           "token_env": "GITHUB_TOKEN"
       },
       {
           "name": "openai-gpt-4.1-mini",
           "endpoint": "https://models.github.ai/inference",
           "model": "openai/gpt-4.1-mini",
           "token_env": "GITHUB_TOKEN"
       },
       # Add more models as needed
   ]

def get_config():
    return Config
