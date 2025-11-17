#!/usr/bin/env python3
"""
Script to set Cohere API Key in Azure Key Vault
"""
import os
import sys
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

KEY_VAULT_NAME = "kv-opsc-sre-74668"
KEY_VAULT_URL = f"https://{KEY_VAULT_NAME}.vault.azure.net"
COHERE_API_KEY = "ycGKLnvJcb3B7dOey5Dsw4o8oHiNLnihN6iFkHqc"

def main():
    print(f"Setting Cohere API Key in Key Vault: {KEY_VAULT_NAME}")

    try:
        # Authenticate using Azure CLI credentials
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)

        # Set the secret
        secret = client.set_secret("CohereAPIKey", COHERE_API_KEY)

        print(f"✅ Successfully set secret: CohereAPIKey")
        print(f"   Secret ID: {secret.id}")
        print(f"   Version: {secret.properties.version}")

        # Verify by retrieving it
        retrieved = client.get_secret("CohereAPIKey")
        if retrieved.value == COHERE_API_KEY:
            print(f"✅ Verified: Secret matches!")
        else:
            print(f"❌ Warning: Retrieved value doesn't match")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
