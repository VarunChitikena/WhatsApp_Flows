# config.py - Configuration
# Centralized configuration for credentials and settings

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    # WhatsApp API credentials
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    APP_ID = os.getenv('APP_ID')
    APP_SECRET = os.getenv('APP_SECRET')
    PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
    VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
    
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME', 'ttd_survey')
    
    # Server configuration
    SERVER_URL = os.getenv('SERVER_URL')
    
    # Categories for the survey
    CATEGORIES = [
        "CLEANLINESS",
        "KALYANAKATTA",
        "LADDUPRASADAM",
        "QLINE",
        "ANNAPRASADAM",
        "OVERALL",
        "ROOMS"
    ]
    
    # Path to key files
    PRIVATE_KEY_PATH = os.getenv('PRIVATE_KEY_PATH', 'private.pem')
    PUBLIC_KEY_PATH = os.getenv('PUBLIC_KEY_PATH', 'public.pem')