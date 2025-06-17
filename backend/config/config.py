import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class."""
    
    #Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY') 
    # DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # Database configuration
    MONGODB_URI = os.getenv('MONGODB_URI')
    MONGODB_DB_NAME= os.getenv('MONGODB_DB_NAME')

    # AI configuration
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

    #JWT configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')