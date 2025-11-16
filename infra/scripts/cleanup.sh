#!/bin/bash

###############################################################################
# Cleanup Script
# Deletes all Azure resources for CMPE273 SRE Hackathon
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
RESOURCE_GROUP="rg-cmpe273-sre-hackathon"

echo ""
echo "###############################################################################"
echo "#  Azure Infrastructure Cleanup - CMPE273 SRE Hackathon (Team OPSC)         #"
echo "###############################################################################"
echo ""

echo -e "${YELLOW}WARNING: This will DELETE ALL resources in resource group: $RESOURCE_GROUP${NC}"
echo ""
echo "This includes:"
echo "  - All App Services (frontend, backend-az1, backend-az2)"
echo "  - MQTT and RabbitMQ containers"
echo "  - Redis Cache"
echo "  - Cosmos DB"
echo "  - Storage Account"
echo "  - Virtual Network"
echo "  - All other resources in the resource group"
echo ""

read -p "Are you sure you want to delete everything? (type 'yes' to confirm): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${GREEN}Cleanup cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${RED}Starting deletion...${NC}"
echo ""

# Check if resource group exists
if az group exists --name "$RESOURCE_GROUP" --output tsv | grep -q "true"; then
    echo "Deleting resource group: $RESOURCE_GROUP"
    echo "This may take 5-10 minutes..."

    az group delete \
        --name "$RESOURCE_GROUP" \
        --yes \
        --no-wait

    echo ""
    echo -e "${GREEN}✓ Deletion initiated${NC}"
    echo ""
    echo "Resource group deletion is running in the background."
    echo "Run the following command to check status:"
    echo ""
    echo "  az group show --name $RESOURCE_GROUP"
    echo ""
    echo "Once deleted, you will see an error: 'ResourceGroupNotFound'"
    echo ""
else
    echo -e "${YELLOW}Resource group $RESOURCE_GROUP does not exist${NC}"
fi

echo "###############################################################################"
echo -e "${GREEN}Cleanup Complete!${NC}"
echo "###############################################################################"
echo ""
