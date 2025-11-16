"""
Application Configuration with Azure Key Vault Integration

This module provides application settings that can be loaded from:
1. Environment variables (.env file for local development)
2. Azure Key Vault (production deployment with UMI)

Settings are loaded in this order (later overrides earlier):
1. Default values
2. .env file
3. Azure Key Vault (if load_from_keyvault() is called)
"""

import os
from typing import Dict, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from loguru import logger


class Settings(BaseSettings):
    """
    Application settings with Azure Key Vault support.

    Local Development:
        Uses .env file with defaults for Redis, MongoDB, etc.

    Production (Azure):
        Calls load_from_keyvault() at startup to override with Key Vault secrets.
    """

    # ================================================================
    # AZURE CONFIGURATION
    # ================================================================
    AZURE_CLIENT_ID: str = Field(default="9de1422a-8247-4986-b63d-bffe81f0d114")
    KEY_VAULT_NAME: str = Field(default="kv-opsc-sre-74668")
    USE_KEY_VAULT: bool = Field(default=True)  # Set to False to disable Key Vault

    # Deployment metadata
    REGION_NAME: str = Field(default="West US 2")
    ACTIVE_REGION: str = Field(default="az1")
    DEPLOYMENT_VERSION: str = Field(default="v1.0.0001_region1")
    ENVIRONMENT: str = Field(default="production")

    # ================================================================
    # REDIS CONFIGURATION
    # ================================================================
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_PASSWORD: str = Field(default="")
    REDIS_SSL: bool = Field(default=False)
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # ================================================================
    # MONGODB CONFIGURATION
    # ================================================================
    MONGO_URL: str = Field(default="mongodb://localhost:27017")
    MONGO_DB: str = Field(default="sre_hackathon")
    COSMOS_MONGODB_URI: str = Field(default="")  # Overridden by Key Vault

    # ================================================================
    # COHERE AI CONFIGURATION
    # ================================================================
    COHERE_API_KEY: str = Field(default="")
    COHERE_MODEL_EMBED: str = Field(default="embed-english-v3.0")
    COHERE_MODEL_CHAT: str = Field(default="command-r-plus")

    # ================================================================
    # MQTT CONFIGURATION
    # ================================================================
    MQTT_HOST: str = Field(default="localhost")
    MQTT_PORT: int = Field(default=1883)

    # ================================================================
    # RABBITMQ CONFIGURATION
    # ================================================================
    RABBITMQ_HOST: str = Field(default="localhost")
    RABBITMQ_PORT: int = Field(default=5672)
    RABBITMQ_URL: str = Field(default="amqp://guest:guest@localhost:5672/")

    # ================================================================
    # AZURE STORAGE CONFIGURATION
    # ================================================================
    AZURE_STORAGE_ACCOUNT: str = Field(default="storsreimages4131")
    BLOB_CONTAINER_IMAGES: str = Field(default="site-images")

    # ================================================================
    # APPLICATION CONFIGURATION
    # ================================================================
    DEVICE_PRESENCE_WINDOW_SEC: int = 120
    USER_PRESENCE_WINDOW_SEC: int = 120
    LOG_LEVEL: str = Field(default="info")

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }

    async def load_from_keyvault(self) -> bool:
        """
        Load secrets from Azure Key Vault and override current settings.

        This is called at application startup in production environments.
        Falls back gracefully if Key Vault is unavailable (uses .env values).

        Returns:
            True if secrets were loaded successfully, False otherwise
        """
        if not self.USE_KEY_VAULT:
            logger.info("Key Vault disabled (USE_KEY_VAULT=False)")
            return False

        try:
            # Import here to avoid circular dependency
            from api.core.keyvault import load_all_secrets

            logger.info("Loading secrets from Azure Key Vault...")
            secrets = await load_all_secrets()

            # Map Key Vault secret names to settings attributes
            secret_mapping: Dict[str, str] = {
                "RedisKey": "REDIS_PASSWORD",
                "CosmosMongoDBConnectionString": "COSMOS_MONGODB_URI",
                "CohereAPIKey": "COHERE_API_KEY",
                "MQTTHost": "MQTT_HOST",
                "MQTTPort": "MQTT_PORT",
                "RabbitMQURL": "RABBITMQ_URL",
            }

            loaded_count = 0
            for kv_name, settings_attr in secret_mapping.items():
                value = secrets.get(kv_name)
                if value:
                    setattr(self, settings_attr, value)
                    loaded_count += 1
                    logger.debug(f"  ✅ {settings_attr} ← {kv_name}")

            # Build Redis URL from components
            if self.REDIS_PASSWORD:
                protocol = "rediss" if self.REDIS_SSL else "redis"
                self.REDIS_URL = f"{protocol}://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
                logger.success(f"✅ Redis URL configured (SSL={self.REDIS_SSL})")

            # Use Cosmos DB URI if available
            if self.COSMOS_MONGODB_URI:
                self.MONGO_URL = self.COSMOS_MONGODB_URI
                logger.success("✅ Cosmos DB URI configured")

            logger.success(f"✅ Loaded {loaded_count}/{len(secret_mapping)} secrets from Key Vault")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to load Key Vault secrets: {e}")
            logger.warning("Falling back to .env configuration")
            return False


# Global settings instance
# In production, call settings.load_from_keyvault() at app startup
settings = Settings()
