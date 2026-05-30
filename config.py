import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load env file if it exists
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

class Settings(BaseSettings):
    # OpenRouter API Key
    OPENROUTER_API_KEY: str = ""
    # Moonshot Kimi LLM via OpenRouter by default
    OPENROUTER_MODEL: str = "moonshotai/kimi-k2.5"
    # Base URL for OpenRouter
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Gemini Defaults
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    
    # Clone configurations
    TEMP_CLONE_DIR: str = "./temp_clones"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def is_api_key_configured(self) -> bool:
        return bool(self.OPENROUTER_API_KEY and not self.OPENROUTER_API_KEY.startswith("your_"))

# Create config instance
settings = Settings()
