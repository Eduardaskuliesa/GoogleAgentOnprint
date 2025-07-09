import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Server settings
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Express server settings
    EXPRESS_BASE_URL: str = os.getenv("EXPRESS_BASE_URL", "http://localhost:4080")
    EXPRESS_API_KEY: str = os.getenv("EXPRESS_API_KEY", "")

settings = Settings()