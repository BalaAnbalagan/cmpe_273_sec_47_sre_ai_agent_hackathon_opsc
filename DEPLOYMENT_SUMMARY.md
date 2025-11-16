# Azure Infrastructure Deployment Summary
## CMPE273 SRE Hackathon - Team OPSC

**Deployment Date:** November 15-16, 2025
**Region:** West US 2 (California - closest to SF Bay Area)
**Subscription:** SJSU Project (3f6c1a1f-b1fa-4745-ab53-a4d9d1d348d7)
**Resource Group:** rg-cmpe273-sre-hackathon
**Status:** ✅ **ALL INFRASTRUCTURE DEPLOYED SUCCESSFULLY**

---

## ✅ Successfully Deployed Resources

### 1. Networking
- **Virtual Network:** vnet-sre (10.0.0.0/16)
  - app-subnet: 10.0.1.0/24
  - mq-subnet: 10.0.2.0/24
  - data-subnet: 10.0.3.0/24

### 2. Compute (App Services)
- **App Service Plan:** asp-sre-ha (Basic B1, Linux)
  - Cost: ~$13/week
  - 1 vCPU, 1.75GB RAM

- **Frontend:**
  - Name: sre-frontend
  - Runtime: Node.js 20 LTS
  - URL: https://sre-frontend.azurewebsites.net
  - Purpose: Next.js SRE Dashboard

- **Backend AZ1:**
  - Name: sre-backend-az1
  - Runtime: Python 3.11
  - URL: https://sre-backend-az1.azurewebsites.net
  - Purpose: FastAPI primary backend (Zone 1 simulation)

- **Backend AZ2:**
  - Name: sre-backend-az2
  - Runtime: Python 3.11
  - URL: https://sre-backend-az2.azurewebsites.net
  - Purpose: FastAPI secondary backend (Zone 2 simulation)

### 3. Messaging Layer

**MQTT Broker (Azure Container Instance):**
- Name: mqtt-broker
- Image: eclipse-mosquitto:2 (from Azure Container Registry)
- Host: opsc-mqtt-sjsu.westus2.azurecontainer.io
- IP: 20.72.232.216
- Ports:
  - 1883 (MQTT)
  - 9001 (WebSocket)
- Status: ✅ Running
- Topic Pattern: `og/field/{site_id}/{device_type}/{device_id}`

**RabbitMQ Broker (Azure Container Instance):**
- Name: rabbitmq-broker
- Image: rabbitmq:3-management (from Azure Container Registry)
- Host: opsc-rabbitmq-sjsu.westus2.azurecontainer.io
- IP: 4.242.119.173
- Ports:
  - 5672 (AMQP)
  - 15672 (Management UI)
- Status: ✅ Running
- Credentials:
  - Username: admin
  - Password: hackathon2024
- Management UI: http://4.242.119.173:15672
- Queue: webapp/active_users

**Azure Container Registry:**
- Name: acropscsre
- Server: acropscsre.azurecr.io
- Purpose: Hosts MQTT and RabbitMQ images (workaround for Docker Hub issues)
- Images:
  - mosquitto:2
  - rabbitmq:3-management

### 4. Data Layer

**Redis Cache (Azure Cache for Redis):**
- Name: redis-sre-ha
- SKU: Standard C2 (2.5GB)
- Host: redis-sre-ha.redis.cache.windows.net
- Port: 6380 (SSL required)
- Status: ✅ Ready
- Features:
  - High availability with automatic failover
  - Data persistence (RDB)
  - Replication enabled
- Cost: ~$18/week

**Cosmos DB (MongoDB API):**
- Account: cosmos-sre-mongo
- Database: sre-database
- API: MongoDB 4.2
- Consistency: Session
- Status: ✅ Ready
- Collections to create:
  - device_images
  - image_embeddings
  - device_logs (optional)
  - user_history (optional)
- Cost: ~$20/week (serverless)

**Storage Account:**
- Name: storsreimages4131
- SKU: Standard_LRS (Hot tier)
- Containers:
  - site-images (for camera images)
  - system-logs (for application logs)
- Status: ✅ Ready
- Cost: ~$5/week

### 5. Security

**User Managed Identity:**
- Name: umi-sre-opsc
- Client ID: Stored in Key Vault (secret: UMIClientID)
- Status: ✅ Configured
- Access Granted:
  - Key Vault: Get, List secrets
  - Storage Account: Blob Data Contributor
  - Cosmos DB: DocumentDB Account Contributor
  - Redis Cache: Redis Cache Contributor
- Assigned to:
  - sre-frontend App Service ✅
  - sre-backend-az1 App Service ✅
  - sre-backend-az2 App Service ✅

**Azure Key Vault:**
- Name: kv-opsc-sre-74668
- URL: https://kv-opsc-sre-74668.vault.azure.net/
- Secrets Stored:
  - StorageAccountKey ✅
  - StorageConnectionString ✅
  - CosmosMongoDBConnectionString ✅
  - FrontendURL ✅
  - BackendAZ1URL ✅
  - BackendAZ2URL ✅
  - RedisKey ✅
  - MqttHost ✅
  - MqttIP ✅
  - MqttPort ✅
  - RabbitMQHost ✅
  - RabbitMQIP ✅
  - RabbitMQPort ✅
  - RabbitMQManagementPort ✅
  - RabbitMQUsername ✅
  - RabbitMQPassword ✅
  - UMIClientID ✅
- Access Policies:
  - UMI (umi-sre-opsc): Get, List secrets
- Cost: ~$1/week

---

## 📊 Complete Infrastructure Endpoints

### Application URLs
```
Frontend:    https://sre-frontend.azurewebsites.net
Backend AZ1: https://sre-backend-az1.azurewebsites.net
Backend AZ2: https://sre-backend-az2.azurewebsites.net
```

### MQTT Broker
```
Host (DNS):  opsc-mqtt-sjsu.westus2.azurecontainer.io
IP Address:  20.72.232.216
MQTT Port:   1883
WebSocket:   9001
```

### RabbitMQ Broker
```
Host (DNS):      opsc-rabbitmq-sjsu.westus2.azurecontainer.io
IP Address:      4.242.119.173
AMQP Port:       5672
Management UI:   http://4.242.119.173:15672
Username:        admin
Password:        hackathon2024
```

### Redis Cache
```
Host:     redis-sre-ha.redis.cache.windows.net
Port:     6380 (SSL)
Password: Stored in Key Vault (secret: RedisKey)
```

### Cosmos DB
```
Connection String: Stored in Key Vault (secret: CosmosMongoDBConnectionString)
Database:          sre-database
```

### Storage Account
```
Account:       storsreimages4131
Key:           Stored in Key Vault (secret: StorageAccountKey)
Containers:    site-images, system-logs
```

---

## 📋 Next Steps for Team

### Using User Managed Identity (UMI) for Password-less Authentication

All App Services now have a User Managed Identity (UMI) assigned that can access Azure resources without passwords:

**UMI Details:**
- Name: umi-sre-opsc
- Client ID: Retrieve from Key Vault (secret: UMIClientID) or from .env file
- Can access: Key Vault, Storage Account, Cosmos DB, Redis Cache

**Get UMI Client ID:**
```bash
# From Key Vault
az keyvault secret show --vault-name kv-opsc-sre-74668 --name UMIClientID --query value -o tsv

# Or from Azure Portal
az identity show --name umi-sre-opsc -g rg-cmpe273-sre-hackathon --query clientId -o tsv
```

**Using UMI in Python (Backend):**
```python
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
import os

# Get UMI Client ID from environment variable
umi_client_id = os.getenv("AZURE_CLIENT_ID")

# Use UMI to access Key Vault
credential = ManagedIdentityCredential(client_id=umi_client_id)
client = SecretClient(vault_url="https://kv-opsc-sre-74668.vault.azure.net/", credential=credential)

# Get secrets without passwords
redis_key = client.get_secret("RedisKey").value
cosmos_uri = client.get_secret("CosmosMongoDBConnectionString").value
```

**Using UMI in Node.js (Frontend):**
```javascript
const { ManagedIdentityCredential } = require("@azure/identity");
const { SecretClient } = require("@azure/keyvault-secrets");

// Get UMI Client ID from environment variable
const umiClientId = process.env.AZURE_CLIENT_ID;

// Use UMI to access Key Vault
const credential = new ManagedIdentityCredential(umiClientId);
const client = new SecretClient("https://kv-opsc-sre-74668.vault.azure.net/", credential);

// Get secrets without passwords
const redisKey = await client.getSecret("RedisKey");
```

### For Varad (Backend):

**1. Clone Repository and Get Credentials:**
```bash
git clone <repo-url>
cd cmpe_273_sec_47_sre_ai_agent_hackathon_opsc
```

**2. Copy .env file:**
```bash
# The .env file at project root has all credentials
cp .env backend/.env
```

**3. Update Cohere API Key:**
- Get your API key from https://dashboard.cohere.com/
- Update `COHERE_API_KEY` in backend/.env

**4. (Optional) Use UMI for Production:**
- When deployed to Azure App Service, use ManagedIdentityCredential
- Avoids hardcoding credentials in .env for production

**5. Build FastAPI Backend:**
```bash
cd backend/api
pip install -r requirements.txt
python main.py  # Test locally
```

**6. Deploy to Azure App Services:**
```bash
# Deploy to Backend AZ1
az webapp up --name sre-backend-az1 --resource-group rg-cmpe273-sre-hackathon

# Deploy to Backend AZ2
az webapp up --name sre-backend-az2 --resource-group rg-cmpe273-sre-hackathon
```

**Tasks:**
- Build device simulator (publish to MQTT: 4.154.194.61:1883)
- Build user simulator (publish to RabbitMQ: 52.143.78.169:5672)
- Create MQTT consumer worker
- Create RabbitMQ consumer worker
- Implement FastAPI endpoints
- Integrate with Redis and Cosmos DB

### For Samip (Frontend):

**1. Clone Repository:**
```bash
git clone <repo-url>
cd cmpe_273_sec_47_sre_ai_agent_hackathon_opsc
```

**2. Copy .env file:**
```bash
cp .env frontend/.env
```

**3. Build Next.js Dashboard:**
```bash
cd frontend
npm install
npm run dev  # Test locally
```

**4. Deploy to Azure:**
```bash
az webapp up --name sre-frontend --resource-group rg-cmpe273-sre-hackathon
```

**Dashboard Sections:**
1. Deployment Version / Failover
2. Site Active Users
3. Active Connected Devices
4. Site Image Intelligence

---

## 🔑 Accessing Credentials

### Option 1: Use .env File (Easiest)
The complete `.env` file is at the project root with all credentials populated.

### Option 2: Azure Key Vault
```bash
# Get Cosmos DB connection string
az keyvault secret show \
  --vault-name kv-opsc-sre-74668 \
  --name CosmosMongoDBConnectionString \
  --query value -o tsv

# Get Redis key
az keyvault secret show \
  --vault-name kv-opsc-sre-74668 \
  --name RedisKey \
  --query value -o tsv

# Get Storage key
az keyvault secret show \
  --vault-name kv-opsc-sre-74668 \
  --name StorageAccountKey \
  --query value -o tsv

# List all secrets
az keyvault secret list --vault-name kv-opsc-sre-74668 --output table
```

### Option 3: Local Development with Docker Compose
```bash
cd infra
docker-compose up -d
```

This starts local versions of:
- MQTT: localhost:1883
- RabbitMQ: localhost:5672 (UI: localhost:15672)
- Redis: localhost:6379
- MongoDB: localhost:27017

---

## 💰 Cost Breakdown

### Current Deployment (~$62/week):

| Service | SKU/Tier | Weekly Cost |
|---------|----------|-------------|
| App Service Plan | B1 (1 vCPU, 1.75GB) | ~$13 |
| Redis Cache | Standard C2 (2.5GB) | ~$18 |
| Cosmos DB | Serverless (MongoDB) | ~$20 |
| Storage Account | Standard LRS (Hot) | ~$5 |
| Container Registry | Basic | ~$3 |
| Container Instances (2) | 1 vCPU, 1.5GB + 2GB | ~$2 |
| Key Vault | Standard | ~$1 |
| Networking | VNet, Public IPs | ~$0 |

**Total: ~$62/week** ✅

**Estimated Hackathon Cost (1 week):** ~$62
**If needed for 2 weeks:** ~$124

---

## 🎯 Deployment Achievements

✅ All infrastructure deployed to Azure West US 2
✅ MQTT and RabbitMQ running on Azure Container Instances
✅ Redis Cache ready with high availability
✅ Cosmos DB (MongoDB API) configured
✅ Storage Account with containers created
✅ All credentials stored in Azure Key Vault
✅ Complete .env file generated with actual values
✅ Zone-redundant architecture simulation (AZ1 + AZ2)
✅ Cost-optimized for hackathon (~$62/week)

---

## 🧹 Cleanup (After Hackathon)

**Delete all resources:**
```bash
cd infra/scripts
./cleanup.sh
```

**Or manually:**
```bash
az group delete --name rg-cmpe273-sre-hackathon --yes --no-wait
```

This deletes:
- All App Services
- Redis Cache
- Cosmos DB
- Storage Account
- Container Registry
- Container Instances
- Key Vault
- Virtual Network

---

## 📞 Support & Troubleshooting

### Check Resource Status
```bash
# View all resources
az resource list -g rg-cmpe273-sre-hackathon --output table

# Check Redis status
az redis show -n redis-sre-ha -g rg-cmpe273-sre-hackathon

# Check MQTT container
az container show -n mqtt-broker -g rg-cmpe273-sre-hackathon

# Check RabbitMQ container
az container show -n rabbitmq-broker -g rg-cmpe273-sre-hackathon

# View App Service logs
az webapp log tail --name sre-backend-az1 -g rg-cmpe273-sre-hackathon
```

### Test MQTT Connection
```bash
# Install mosquitto clients
brew install mosquitto

# Test MQTT connection
mosquitto_sub -h 20.72.232.216 -p 1883 -t "og/field/#" -v
```

### Test RabbitMQ Connection
- Management UI: http://4.242.119.173:15672
- Username: admin
- Password: hackathon2024

### Important Information
- **Resource Group:** rg-cmpe273-sre-hackathon
- **Region:** West US 2
- **Subscription:** SJSU Project (3f6c1a1f-b1fa-4745-ab53-a4d9d1d348d7)
- **Key Vault:** kv-opsc-sre-74668

---

## 📚 Documentation

- [TEAM_ACCESS.md](TEAM_ACCESS.md) - Complete infrastructure guide for team
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [README.md](README.md) - Project overview
- [infra/README.md](infra/README.md) - Infrastructure documentation
- [infra/docs/ARCHITECTURE.md](infra/docs/ARCHITECTURE.md) - Architecture details

---

**Team OPSC** | Infrastructure by Bala | CMPE273 SRE Hackathon | November 2025

🎉 **Infrastructure Deployment Complete - Ready for Development!** 🎉
