"""
Azure Key Vault Integration with User Managed Identity (UMI)

This module provides password-less authentication to Azure Key Vault using
User Managed Identity. Secrets are loaded at application startup and cached
in the application settings.

Key Vault: kv-opsc-sre-74668
UMI Client ID: 9de1422a-8247-4986-b63d-bffe81f0d114

Secrets loaded:
- RedisKey: Redis cache password
- CosmosMongoDBConnectionString: Cosmos DB connection string
- CohereAPIKey: Cohere AI API key
- MQTTHost: MQTT broker hostname
- MQTTPort: MQTT broker port
- RabbitMQURL: RabbitMQ connection URL
"""

import os
from typing import Dict, Optional
from azure.identity import ManagedIdentityCredential, DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from loguru import logger


# Key Vault configuration
KEY_VAULT_NAME = "kv-opsc-sre-74668"
KEY_VAULT_URL = f"https://{KEY_VAULT_NAME}.vault.azure.net"

# User Managed Identity Client ID
UMI_CLIENT_ID = "9de1422a-8247-4986-b63d-bffe81f0d114"

# Global Key Vault client (initialized on first use)
_kv_client: Optional[SecretClient] = None
_secrets_cache: Dict[str, str] = {}


def get_keyvault_client() -> SecretClient:
    """
    Get or create the Azure Key Vault client with User Managed Identity.

    Authentication flow:
    1. Try ManagedIdentityCredential with UMI client ID (production Azure)
    2. Fallback to DefaultAzureCredential (local development with Azure CLI)

    Returns:
        SecretClient: Authenticated Key Vault client
    """
    global _kv_client

    if _kv_client is not None:
        return _kv_client

    try:
        # Production: Use User Managed Identity
        logger.info(f"Authenticating to Key Vault with UMI: {UMI_CLIENT_ID}")
        credential = ManagedIdentityCredential(client_id=UMI_CLIENT_ID)
        _kv_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)
        logger.success(f"✅ Connected to Key Vault: {KEY_VAULT_NAME} (UMI)")

    except Exception as umi_error:
        # Fallback: Local development with Azure CLI or environment credentials
        logger.warning(f"UMI authentication failed: {umi_error}")
        logger.info("Falling back to DefaultAzureCredential (local dev)")

        try:
            credential = DefaultAzureCredential()
            _kv_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)
            logger.success(f"✅ Connected to Key Vault: {KEY_VAULT_NAME} (DefaultCredential)")
        except Exception as fallback_error:
            logger.error(f"❌ Key Vault authentication failed: {fallback_error}")
            raise RuntimeError(
                f"Cannot authenticate to Azure Key Vault. "
                f"Ensure UMI is configured or run 'az login' for local dev."
            ) from fallback_error

    return _kv_client


async def get_secret(secret_name: str, use_cache: bool = True) -> Optional[str]:
    """
    Retrieve a secret from Azure Key Vault.

    Args:
        secret_name: Name of the secret in Key Vault
        use_cache: Whether to use cached value (default: True)

    Returns:
        Secret value as string, or None if not found

    Example:
        redis_password = await get_secret("RedisKey")
        cohere_key = await get_secret("CohereAPIKey")
    """
    # Check cache first
    if use_cache and secret_name in _secrets_cache:
        logger.debug(f"Using cached secret: {secret_name}")
        return _secrets_cache[secret_name]

    try:
        client = get_keyvault_client()
        secret = client.get_secret(secret_name)

        # Cache the secret value
        _secrets_cache[secret_name] = secret.value
        logger.debug(f"✅ Retrieved secret: {secret_name}")

        return secret.value

    except Exception as e:
        logger.error(f"❌ Failed to retrieve secret '{secret_name}': {e}")
        return None


async def load_all_secrets() -> Dict[str, Optional[str]]:
    """
    Load all required secrets from Azure Key Vault.

    This is called at application startup to populate settings.

    Returns:
        Dictionary mapping secret names to their values
    """
    secret_names = [
        "RedisKey",                        # Redis password
        "CosmosMongoDBConnectionString",   # Cosmos DB connection string
        "CohereAPIKey",                    # Cohere AI API key
        "MQTTHost",                        # MQTT broker host
        "MQTTPort",                        # MQTT broker port
        "RabbitMQURL",                     # RabbitMQ connection URL
    ]

    logger.info(f"Loading {len(secret_names)} secrets from Key Vault...")

    secrets = {}
    for name in secret_names:
        value = await get_secret(name, use_cache=False)
        secrets[name] = value

        if value:
            logger.success(f"  ✅ {name}")
        else:
            logger.warning(f"  ⚠️  {name} (not found or failed)")

    logger.info(f"Loaded {sum(1 for v in secrets.values() if v)} / {len(secret_names)} secrets")

    return secrets


def is_key_vault_available() -> bool:
    """
    Check if Key Vault is accessible.

    Returns:
        True if Key Vault can be reached, False otherwise
    """
    try:
        client = get_keyvault_client()
        # Try to list secrets (permissions check)
        list(client.list_properties_of_secrets())
        return True
    except Exception as e:
        logger.error(f"Key Vault health check failed: {e}")
        return False


def clear_cache():
    """Clear the secrets cache. Useful for testing or forcing refresh."""
    global _secrets_cache
    _secrets_cache.clear()
    logger.info("Secrets cache cleared")
