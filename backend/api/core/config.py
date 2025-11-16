from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    MONGO_URL: str = Field(default="mongodb://localhost:27017")
    MONGO_DB: str = Field(default="sre_hackathon")

    # Sliding windows (seconds) for "active" calculations
    DEVICE_PRESENCE_WINDOW_SEC: int = 120
    USER_PRESENCE_WINDOW_SEC: int = 120

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }

settings = Settings()
