#!/bin/bash

###############################################################################
# Azure Infrastructure Deployment Script
# CMPE273 SRE Hackathon - Team OPSC
# Option-1 Deployment Model: West US with Availability Zones
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration Variables
RESOURCE_GROUP="rg-cmpe273-sre-hackathon"
LOCATION="westus"
VNET_NAME="vnet-sre"
VNET_ADDRESS="10.0.0.0/16"

# Subnets
APP_SUBNET_NAME="app-subnet"
APP_SUBNET_PREFIX="10.0.1.0/24"
MQ_SUBNET_NAME="mq-subnet"
MQ_SUBNET_PREFIX="10.0.2.0/24"
DATA_SUBNET_NAME="data-subnet"
DATA_SUBNET_PREFIX="10.0.3.0/24"

# Public IPs
PIP_MQTT="pip-mqtt"
PIP_RABBITMQ="pip-rabbitmq"

# App Service
APP_SERVICE_PLAN="asp-sre-ha"
APP_SERVICE_SKU="P1v2"  # Change to "B1" for cost savings
BACKEND_AZ1="sre-backend-az1"
BACKEND_AZ2="sre-backend-az2"
FRONTEND="sre-frontend"

# Container Instances
MQTT_CONTAINER="mqtt-broker"
RABBITMQ_CONTAINER="rabbitmq-broker"

# Redis
REDIS_NAME="redis-sre-ha"
REDIS_SKU="Premium"
REDIS_FAMILY="P"
REDIS_CAPACITY="1"

# Cosmos DB
COSMOS_ACCOUNT="cosmos-sre-mongo"
COSMOS_DB_NAME="sre-database"

# Storage
STORAGE_ACCOUNT="storsreimages$(date +%s | tail -c 5)"  # Add suffix for uniqueness

# Tags
TAGS="Project=CMPE273-SRE-Hackathon Team=OPSC Environment=Production"

###############################################################################
# Helper Functions
###############################################################################

print_step() {
    echo -e "${BLUE}==>${NC} ${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

check_prerequisites() {
    print_step "Checking prerequisites..."

    # Check if Azure CLI is installed
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI is not installed. Please install it first."
        exit 1
    fi

    # Check if logged in
    if ! az account show &> /dev/null; then
        print_error "Not logged in to Azure. Please run 'az login' first."
        exit 1
    fi

    print_success "Prerequisites checked"

    # Show current subscription
    SUBSCRIPTION=$(az account show --query name -o tsv)
    print_warning "Deploying to subscription: $SUBSCRIPTION"
    echo ""
    read -p "Continue with this subscription? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Deployment cancelled"
        exit 1
    fi
}

###############################################################################
# Deployment Steps
###############################################################################

deploy_resource_group() {
    print_step "Creating Resource Group..."
    az group create \
        --name "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --tags $TAGS \
        --output none
    print_success "Resource Group created: $RESOURCE_GROUP"
}

deploy_networking() {
    print_step "Creating Virtual Network and Subnets..."

    # Create VNet
    az network vnet create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$VNET_NAME" \
        --address-prefix "$VNET_ADDRESS" \
        --location "$LOCATION" \
        --tags $TAGS \
        --output none

    # Create App Subnet
    az network vnet subnet create \
        --resource-group "$RESOURCE_GROUP" \
        --vnet-name "$VNET_NAME" \
        --name "$APP_SUBNET_NAME" \
        --address-prefix "$APP_SUBNET_PREFIX" \
        --output none

    # Create MQ Subnet
    az network vnet subnet create \
        --resource-group "$RESOURCE_GROUP" \
        --vnet-name "$VNET_NAME" \
        --name "$MQ_SUBNET_NAME" \
        --address-prefix "$MQ_SUBNET_PREFIX" \
        --output none

    # Create Data Subnet with service endpoints
    az network vnet subnet create \
        --resource-group "$RESOURCE_GROUP" \
        --vnet-name "$VNET_NAME" \
        --name "$DATA_SUBNET_NAME" \
        --address-prefix "$DATA_SUBNET_PREFIX" \
        --service-endpoints Microsoft.Storage Microsoft.AzureCosmosDB \
        --output none

    print_success "Virtual Network created with 3 subnets"

    # Create Public IPs
    print_step "Creating Public IPs..."

    az network public-ip create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$PIP_MQTT" \
        --location "$LOCATION" \
        --allocation-method Static \
        --sku Standard \
        --zone 1 2 \
        --tags $TAGS \
        --output none

    az network public-ip create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$PIP_RABBITMQ" \
        --location "$LOCATION" \
        --allocation-method Static \
        --sku Standard \
        --zone 1 2 \
        --tags $TAGS \
        --output none

    print_success "Public IPs created"
}

deploy_app_services() {
    print_step "Creating App Service Plan (Zone-Redundant)..."

    az appservice plan create \
        --name "$APP_SERVICE_PLAN" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --sku "$APP_SERVICE_SKU" \
        --is-linux \
        --zone-redundant \
        --tags $TAGS \
        --output none

    print_success "App Service Plan created: $APP_SERVICE_PLAN"

    print_step "Creating Backend App Service (AZ1)..."
    az webapp create \
        --name "$BACKEND_AZ1" \
        --resource-group "$RESOURCE_GROUP" \
        --plan "$APP_SERVICE_PLAN" \
        --runtime "PYTHON:3.11" \
        --tags $TAGS Region=AZ1 \
        --output none

    print_success "Backend AZ1 created: https://${BACKEND_AZ1}.azurewebsites.net"

    print_step "Creating Backend App Service (AZ2)..."
    az webapp create \
        --name "$BACKEND_AZ2" \
        --resource-group "$RESOURCE_GROUP" \
        --plan "$APP_SERVICE_PLAN" \
        --runtime "PYTHON:3.11" \
        --tags $TAGS Region=AZ2 \
        --output none

    print_success "Backend AZ2 created: https://${BACKEND_AZ2}.azurewebsites.net"

    print_step "Creating Frontend App Service..."
    az webapp create \
        --name "$FRONTEND" \
        --resource-group "$RESOURCE_GROUP" \
        --plan "$APP_SERVICE_PLAN" \
        --runtime "NODE:18-lts" \
        --tags $TAGS \
        --output none

    print_success "Frontend created: https://${FRONTEND}.azurewebsites.net"
}

deploy_messaging() {
    print_step "Creating MQTT Broker (Container Instance)..."

    # Get subnet ID for MQ subnet
    MQ_SUBNET_ID=$(az network vnet subnet show \
        --resource-group "$RESOURCE_GROUP" \
        --vnet-name "$VNET_NAME" \
        --name "$MQ_SUBNET_NAME" \
        --query id -o tsv)

    # Get public IP ID
    MQTT_IP_ID=$(az network public-ip show \
        --resource-group "$RESOURCE_GROUP" \
        --name "$PIP_MQTT" \
        --query id -o tsv)

    az container create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$MQTT_CONTAINER" \
        --image eclipse-mosquitto:latest \
        --cpu 1 \
        --memory 1 \
        --ports 1883 8883 \
        --ip-address Public \
        --location "$LOCATION" \
        --tags $TAGS \
        --output none

    print_success "MQTT Broker created"

    print_step "Creating RabbitMQ Broker (Container Instance)..."

    az container create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$RABBITMQ_CONTAINER" \
        --image rabbitmq:3-management \
        --cpu 1 \
        --memory 2 \
        --ports 5672 15672 \
        --environment-variables RABBITMQ_DEFAULT_USER=admin RABBITMQ_DEFAULT_PASS=hackathon2024 \
        --ip-address Public \
        --location "$LOCATION" \
        --tags $TAGS \
        --output none

    print_success "RabbitMQ Broker created"
}

deploy_redis() {
    print_step "Creating Redis Cache (Premium, Zone-Redundant)..."
    print_warning "This may take 15-20 minutes..."

    az redis create \
        --name "$REDIS_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --sku "$REDIS_SKU" \
        --vm-size "$REDIS_FAMILY$REDIS_CAPACITY" \
        --zones 1 2 \
        --redis-version 6 \
        --tags $TAGS \
        --output none

    print_success "Redis Cache created: $REDIS_NAME.redis.cache.windows.net"

    # Enable Redis modules (JSON, Search, TimeSeries)
    print_step "Configuring Redis modules..."
    print_warning "Note: RedisJSON, RedisSearch, RedisTimeSeries require Enterprise tier"
    print_warning "Premium tier supports standard Redis commands. Upgrade to Enterprise if needed."
}

deploy_cosmos_db() {
    print_step "Creating Cosmos DB (MongoDB API, Zone-Redundant)..."
    print_warning "This may take 5-10 minutes..."

    az cosmosdb create \
        --name "$COSMOS_ACCOUNT" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --kind MongoDB \
        --server-version 4.2 \
        --enable-automatic-failover true \
        --locations regionName="$LOCATION" failoverPriority=0 isZoneRedundant=true \
        --tags $TAGS \
        --output none

    print_success "Cosmos DB account created: $COSMOS_ACCOUNT"

    # Create database
    az cosmosdb mongodb database create \
        --account-name "$COSMOS_ACCOUNT" \
        --resource-group "$RESOURCE_GROUP" \
        --name "$COSMOS_DB_NAME" \
        --output none

    print_success "Database created: $COSMOS_DB_NAME"
}

deploy_storage() {
    print_step "Creating Storage Account..."

    az storage account create \
        --name "$STORAGE_ACCOUNT" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --sku Standard_ZRS \
        --kind StorageV2 \
        --access-tier Hot \
        --tags $TAGS \
        --output none

    print_success "Storage Account created: $STORAGE_ACCOUNT"

    # Create blob containers
    STORAGE_KEY=$(az storage account keys list \
        --resource-group "$RESOURCE_GROUP" \
        --account-name "$STORAGE_ACCOUNT" \
        --query "[0].value" -o tsv)

    az storage container create \
        --name "site-images" \
        --account-name "$STORAGE_ACCOUNT" \
        --account-key "$STORAGE_KEY" \
        --output none

    az storage container create \
        --name "system-logs" \
        --account-name "$STORAGE_ACCOUNT" \
        --account-key "$STORAGE_KEY" \
        --output none

    print_success "Blob containers created: site-images, system-logs"
}

###############################################################################
# Main Execution
###############################################################################

main() {
    echo ""
    echo "###############################################################################"
    echo "#  Azure Infrastructure Deployment - CMPE273 SRE Hackathon (Team OPSC)      #"
    echo "###############################################################################"
    echo ""

    check_prerequisites

    echo ""
    print_step "Starting deployment to $LOCATION..."
    echo ""

    deploy_resource_group
    deploy_networking
    deploy_app_services
    deploy_messaging
    deploy_redis
    deploy_cosmos_db
    deploy_storage

    echo ""
    echo "###############################################################################"
    echo -e "${GREEN}✓ Deployment Complete!${NC}"
    echo "###############################################################################"
    echo ""
    echo "Run './get-config.sh' to retrieve all connection strings and URLs"
    echo "Run './cleanup.sh' to delete all resources when done"
    echo ""
}

# Run main function
main
