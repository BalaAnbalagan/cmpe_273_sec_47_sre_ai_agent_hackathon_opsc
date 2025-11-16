#!/bin/bash

###############################################################################
# Get Configuration Script
# Retrieves all URLs, connection strings, and credentials
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
RESOURCE_GROUP="rg-cmpe273-sre-hackathon"
BACKEND_AZ1="sre-backend-az1"
BACKEND_AZ2="sre-backend-az2"
FRONTEND="sre-frontend"
MQTT_CONTAINER="mqtt-broker"
RABBITMQ_CONTAINER="rabbitmq-broker"
REDIS_NAME="redis-sre-ha"
COSMOS_ACCOUNT="cosmos-sre-mongo"
STORAGE_ACCOUNT_PREFIX="storsreimages"

print_header() {
    echo -e "${BLUE}$1${NC}"
    echo "================================================================"
}

print_item() {
    echo -e "${GREEN}$1:${NC} $2"
}

echo ""
echo "###############################################################################"
echo "#  Azure Infrastructure Configuration - Team OPSC                            #"
echo "###############################################################################"
echo ""

# Get Storage Account Name (dynamic)
STORAGE_ACCOUNT=$(az storage account list \
    --resource-group "$RESOURCE_GROUP" \
    --query "[?starts_with(name, '$STORAGE_ACCOUNT_PREFIX')].name" -o tsv | head -n 1)

###############################################################################
# 1. Frontend & Backend URLs
###############################################################################

print_header "1. Application URLs"

FRONTEND_URL="https://${FRONTEND}.azurewebsites.net"
BACKEND_AZ1_URL="https://${BACKEND_AZ1}.azurewebsites.net"
BACKEND_AZ2_URL="https://${BACKEND_AZ2}.azurewebsites.net"

print_item "Frontend URL" "$FRONTEND_URL"
print_item "Backend AZ1 URL" "$BACKEND_AZ1_URL"
print_item "Backend AZ2 URL" "$BACKEND_AZ2_URL"
echo ""

###############################################################################
# 2. MQTT Broker
###############################################################################

print_header "2. MQTT Broker"

MQTT_IP=$(az container show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$MQTT_CONTAINER" \
    --query "ipAddress.ip" -o tsv)

print_item "MQTT Host" "$MQTT_IP"
print_item "MQTT Port" "1883"
print_item "MQTT SSL Port" "8883"
print_item "MQTT Topic Pattern" "og/field/{site_id}/{device_type}/{device_id}"
echo ""

###############################################################################
# 3. RabbitMQ Broker
###############################################################################

print_header "3. RabbitMQ Broker"

RABBITMQ_IP=$(az container show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$RABBITMQ_CONTAINER" \
    --query "ipAddress.ip" -o tsv)

print_item "RabbitMQ Host" "$RABBITMQ_IP"
print_item "RabbitMQ AMQP Port" "5672"
print_item "RabbitMQ Management UI" "http://${RABBITMQ_IP}:15672"
print_item "RabbitMQ Username" "admin"
print_item "RabbitMQ Password" "hackathon2024"
echo ""

###############################################################################
# 4. Redis Cache
###############################################################################

print_header "4. Redis Cache"

REDIS_HOST="${REDIS_NAME}.redis.cache.windows.net"
REDIS_PORT="6380"
REDIS_KEY=$(az redis list-keys \
    --resource-group "$RESOURCE_GROUP" \
    --name "$REDIS_NAME" \
    --query "primaryKey" -o tsv)

print_item "Redis Host" "$REDIS_HOST"
print_item "Redis Port" "$REDIS_PORT (SSL)"
print_item "Redis SSL" "Required"
print_item "Redis Primary Key" "$REDIS_KEY"
echo ""

###############################################################################
# 5. Cosmos DB (MongoDB)
###############################################################################

print_header "5. Cosmos DB (MongoDB API)"

COSMOS_CONNECTION=$(az cosmosdb keys list \
    --resource-group "$RESOURCE_GROUP" \
    --name "$COSMOS_ACCOUNT" \
    --type connection-strings \
    --query "connectionStrings[0].connectionString" -o tsv)

print_item "Cosmos Account" "$COSMOS_ACCOUNT"
print_item "Database Name" "sre-database"
print_item "Connection String" "$COSMOS_CONNECTION"
echo ""

###############################################################################
# 6. Storage Account
###############################################################################

print_header "6. Storage Account"

STORAGE_KEY=$(az storage account keys list \
    --resource-group "$RESOURCE_GROUP" \
    --account-name "$STORAGE_ACCOUNT" \
    --query "[0].value" -o tsv)

STORAGE_CONNECTION=$(az storage account show-connection-string \
    --resource-group "$RESOURCE_GROUP" \
    --name "$STORAGE_ACCOUNT" \
    --query "connectionString" -o tsv)

print_item "Storage Account" "$STORAGE_ACCOUNT"
print_item "Blob Endpoint" "https://${STORAGE_ACCOUNT}.blob.core.windows.net"
print_item "Access Key" "$STORAGE_KEY"
print_item "Connection String" "$STORAGE_CONNECTION"
print_item "Containers" "site-images, system-logs"
echo ""

###############################################################################
# 7. Generate .env File
###############################################################################

print_header "7. Generating .env File"

ENV_FILE="../../.env"

cat > "$ENV_FILE" <<EOF
# CMPE273 SRE Hackathon - Team OPSC
# Generated: $(date)

# ================================================================
# APPLICATION URLs
# ================================================================
FRONTEND_URL=$FRONTEND_URL
BACKEND_AZ1_URL=$BACKEND_AZ1_URL
BACKEND_AZ2_URL=$BACKEND_AZ2_URL

# ================================================================
# MQTT BROKER
# ================================================================
MQTT_HOST=$MQTT_IP
MQTT_PORT=1883
MQTT_SSL_PORT=8883
MQTT_TOPIC_PREFIX=og/field

# ================================================================
# RABBITMQ BROKER
# ================================================================
RABBITMQ_HOST=$RABBITMQ_IP
RABBITMQ_PORT=5672
RABBITMQ_MANAGEMENT_PORT=15672
RABBITMQ_USERNAME=admin
RABBITMQ_PASSWORD=hackathon2024
RABBITMQ_VHOST=/

# ================================================================
# REDIS CACHE
# ================================================================
REDIS_HOST=$REDIS_HOST
REDIS_PORT=$REDIS_PORT
REDIS_PASSWORD=$REDIS_KEY
REDIS_SSL=true

# ================================================================
# COSMOS DB (MongoDB)
# ================================================================
COSMOS_MONGODB_URI=$COSMOS_CONNECTION
COSMOS_DATABASE=sre-database
COSMOS_COLLECTION_IMAGES=device_images
COSMOS_COLLECTION_EMBEDDINGS=image_embeddings

# ================================================================
# STORAGE ACCOUNT
# ================================================================
AZURE_STORAGE_ACCOUNT=$STORAGE_ACCOUNT
AZURE_STORAGE_KEY=$STORAGE_KEY
AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION
BLOB_CONTAINER_IMAGES=site-images
BLOB_CONTAINER_LOGS=system-logs

# ================================================================
# COHERE AI (Add your API key)
# ================================================================
COHERE_API_KEY=your-cohere-api-key-here
COHERE_MODEL_EMBED_TEXT=embed-english-v3.0
COHERE_MODEL_EMBED_IMAGE=vision-model-name
COHERE_MODEL_CHAT=command-r-plus

# ================================================================
# APPLICATION CONFIG
# ================================================================
ENVIRONMENT=production
LOG_LEVEL=info
ACTIVE_REGION=az1
FAILOVER_ENABLED=true
EOF

print_item ".env file created" "$ENV_FILE"
echo ""

echo "###############################################################################"
echo -e "${GREEN}✓ Configuration Retrieved Successfully!${NC}"
echo "###############################################################################"
echo ""
echo "Next steps:"
echo "1. Copy .env file to your backend/ and frontend/ directories"
echo "2. Update COHERE_API_KEY with your actual API key"
echo "3. Share URLs with Varad & Samip for application deployment"
echo ""
