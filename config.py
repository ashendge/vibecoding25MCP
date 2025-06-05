import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the application."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_URL: str = "https://api.openai.com/v1/chat/completions"
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = 0.3
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "vibe.db")
    
    # API Configuration
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    
    @classmethod
    def validate(cls) -> None:
        """Validate that all required configuration values are set."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    @classmethod
    def get_openai_config(cls) -> Dict[str, Any]:
        """Get OpenAI API configuration."""
        return {
            "model": cls.OPENAI_MODEL,
            "temperature": cls.OPENAI_TEMPERATURE,
            "response_format": {"type": "json_object"}
        } 