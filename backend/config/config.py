import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class."""
    
    #Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY') 
  

    # Database configuration
    MONGO_URI = os.getenv('MONGODB_URI')  # Only this is needed for Flask-PyMongo

    # AI configuration
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

    #JWT configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
