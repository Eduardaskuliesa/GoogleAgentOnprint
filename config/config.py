import os
from dotenv import load_dotenv

print(f"Before load_dotenv: {os.getenv('EXPRESS_BASE_URL')}")

load_dotenv(override=True)

print(f"After load_dotenv: {os.getenv('EXPRESS_BASE_URL')}")
class Settings:
    # Server settings
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Express server settings
    EXPRESS_BASE_URL: str = os.getenv("EXPRESS_BASE_URL", "")
    EXPRESS_API_KEY: str = os.getenv("EXPRESS_API_KEY", "")
    
    # Google GenAI settings
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # SERVER API KEY for authentication
    SERVER_API_KEY: str = os.getenv("SERVER_API_KEY", "")

settings = Settings()