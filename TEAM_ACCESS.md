# Team Access Guide - Infrastructure Overview
## CMPE273 SRE Hackathon - Team OPSC

**For:** Varad (Backend) & Samip (Frontend)
**Prepared by:** Bala (Infrastructure)
**Date:** November 15, 2025

---

## 🏗️ Infrastructure Overview

### What Has Been Deployed

All resources are in **Azure West US 2** (California) under:
- **Resource Group:** `rg-cmpe273-sre-hackathon`
- **Subscription:** The Krishnan Group
- **Cost:** ~$62/week

---

## 📊 Complete Infrastructure Architecture

### 1. Networking Layer

**Virtual Network:** `vnet-sre` (10.0.0.0/16)

```
vnet-sre (10.0.0.0/16)
│
├── app-subnet (10.0.1.0/24)        # App Services
├── mq-subnet (10.0.2.0/24)         # MQTT + RabbitMQ
└── data-subnet (10.0.3.0/24)       # Redis + Cosmos DB
```

**Why 3 subnets?**
- Security isolation between layers
- Network segmentation for better control
- Service endpoints for Azure services

---

### 2. Compute Layer (App Services)

**App Service Plan:** `asp-sre-ha`
- SKU: B1 (Basic, 1 core, 1.75GB RAM)
- OS: Linux
- Cost: ~$13/week

**3 App Services Deployed:**

#### Frontend App Service
```yaml
Name: sre-frontend
Runtime: Node.js 20 LTS
URL: https://sre-frontend.azurewebsites.net
Purpose: Next.js dashboard (Samip's code)
```

#### Backend AZ1
```yaml
Name: sre-backend-az1
Runtime: Python 3.11
URL: https://sre-backend-az1.azurewebsites.net
Purpose: FastAPI primary backend (Varad's code)
Zone: Simulates Zone 1 for failover
```

#### Backend AZ2
```yaml
Name: sre-backend-az2
Runtime: Python 3.11
URL: https://sre-backend-az2.azurewebsites.net
Purpose: FastAPI secondary backend (Varad's code)
Zone: Simulates Zone 2 for failover
```

**Why 2 backends?**
- Tier-0 requirement: Regional failover simulation
- Frontend can switch between AZ1 ↔ AZ2
- Demonstrates high availability

---

### 3. Data Layer

#### A) Azure Cache for Redis

```yaml
Name: redis-sre-ha
SKU: Standard C2 (2.5GB)
Host: redis-sre-ha.redis.cache.windows.net
Port: 6380 (SSL required)
Cost: ~$18/week
Status: Deploying (15-20 min total)
```

**What it stores:**
- Active user sessions
- Device state cache
- Failover state (active_region, version)
- Dashboard metrics

**Redis Keys Structure:**
```
users:active:{site_id}              → Set of active user IDs
users:sessions:{user_id}            → User session data
devices:active:{site_id}            → Set of active device IDs
devices:state:{device_id}           → Device telemetry
sre:deployment:version              → Current version
sre:deployment:active_region        → az1 or az2
```

#### B) Cosmos DB (MongoDB API)

```yaml
Name: cosmos-sre-mongo
API: MongoDB 4.2
Database: sre-database
Cost: ~$20/week (serverless)
Status: ✅ Ready
```

**Collections to create:**
```javascript
// device_images
{
  _id: ObjectId,
  site_id: "ND-RAVEN",
  image_id: "IMG-2025-11-15-001",
  blob_url: "https://...",
  timestamp: ISODate,
  metadata: { camera_id, resolution }
}

// image_embeddings
{
  _id: ObjectId,
  image_id: "IMG-2025-11-15-001",
  embedding: [0.123, -0.456, ...],  // 1024-4096 floats
  model: "embed-english-v3.0",
  tags: ["worker", "hard hat", "tablet"]
}
```

**Why Cosmos DB?**
- Globally distributed (can scale)
- MongoDB API (familiar to team)
- Vector search capabilities
- Auto-scaling

#### C) Storage Account

```yaml
Name: storsreimages4131
SKU: Standard_LRS (Hot tier)
Containers:
  - site-images (for camera images)
  - system-logs (for application logs)
Cost: ~$5/week
```

**How to upload images:**
```python
from azure.storage.blob import BlobServiceClient

# Connection string from Key Vault or .env
conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
blob_service = BlobServiceClient.from_connection_string(conn_str)

# Upload image
container_client = blob_service.get_container_client("site-images")
blob_client = container_client.get_blob_client("IMG-001.jpg")
blob_client.upload_blob(image_data)
```

---

### 4. Messaging Layer

#### MQTT Broker (For IoT Devices)

```yaml
Status: ⏸️ Pending (Docker Hub issues)
Workaround: Use local Docker Compose
Topic Pattern: og/field/{site_id}/{device_type}/{device_id}
```

**For local development:**
```bash
cd infra
docker-compose up -d mqtt
# MQTT available at localhost:1883
```

**Device Types:**
- turbine
- thermal_engine
- electrical_rotor
- connected_device

**Example MQTT Message:**
```json
{
  "device_id": "TURB-00912",
  "device_type": "turbine",
  "site_id": "WY-ALPHA",
  "timestamp_utc": "2025-11-15T23:10:05Z",
  "metrics": {
    "rpm": 3487,
    "inlet_temp_c": 412.6,
    "power_kw": 12850.4
  },
  "status": { "state": "OK" }
}
```

#### RabbitMQ Broker (For User Activity)

```yaml
Status: ⏸️ Pending (Docker Hub issues)
Workaround: Use local Docker Compose
Queue: webapp/active_users
```

**For local development:**
```bash
cd infra
docker-compose up -d rabbitmq
# RabbitMQ: localhost:5672
# Management UI: http://localhost:15672
# Username: admin / Password: hackathon2024
```

**User Activity Message:**
```json
{
  "message_id": "MSG-20251115-00123",
  "site_id": "SFO-WEB-01",
  "metrics": {
    "active_users": 324,
    "active_connections": 289
  },
  "active_users_list": [
    {
      "user_id": "USR-09421",
      "username": "alex_j",
      "session_id": "SESS-342AF1",
      "ip_address": "192.168.1.104",
      "region": "US-WEST"
    }
  ]
}
```

---

### 5. Security Layer

#### Azure Key Vault

```yaml
Name: kv-opsc-sre-74668
Purpose: Secure credential storage
Cost: ~$1/week
```

**Secrets Stored:**
- `StorageAccountKey`
- `StorageConnectionString`
- `CosmosMongoDBConnectionString`
- `FrontendURL`
- `BackendAZ1URL`
- `BackendAZ2URL`
- `RedisKey` (pending Redis completion)

**How to access secrets:**
```bash
# Using Azure CLI (Bala's login)
az keyvault secret show \
  --vault-name kv-opsc-sre-74668 \
  --name CosmosMongoDBConnectionString \
  --query value -o tsv
```

---

## 🔐 Access Methods for Team

### Option 1: Use .env File (Easiest)

The `.env` file at project root contains all connection strings.

**Varad (Backend):**
```bash
# Copy .env to backend directory
cp .env backend/.env

# Your FastAPI app can read:
import os
from dotenv import load_dotenv

load_dotenv()

redis_host = os.getenv("REDIS_HOST")
cosmos_uri = os.getenv("COSMOS_MONGODB_URI")
```

**Samip (Frontend):**
```bash
# Copy .env to frontend directory
cp .env frontend/.env

# Next.js reads from .env:
const backendURL = process.env.BACKEND_AZ1_URL
```

### Option 2: Azure CLI Access (For deployments)

**Install Azure CLI:**
```bash
# macOS
brew install azure-cli

# Login with Bala's account
az login
```

**Deploy your code:**
```bash
# Varad - Deploy FastAPI to backend
cd backend/api
az webapp up --name sre-backend-az1 --resource-group rg-cmpe273-sre-hackathon

# Samip - Deploy Next.js to frontend
cd frontend
az webapp up --name sre-frontend --resource-group rg-cmpe273-sre-hackathon
```

---

## 🛠️ How Infrastructure Was Built

### Step-by-Step Build Process

#### 1. Resource Group Creation
```bash
az group create \
  --name rg-cmpe273-sre-hackathon \
  --location westus2
```

#### 2. Virtual Network Setup
```bash
# Create VNet
az network vnet create \
  --name vnet-sre \
  --address-prefix 10.0.0.0/16

# Create subnets
az network vnet subnet create --name app-subnet --address-prefix 10.0.1.0/24
az network vnet subnet create --name mq-subnet --address-prefix 10.0.2.0/24
az network vnet subnet create --name data-subnet --address-prefix 10.0.3.0/24
```

#### 3. App Service Deployment
```bash
# Create App Service Plan
az appservice plan create \
  --name asp-sre-ha \
  --sku B1 \
  --is-linux

# Create 3 App Services
az webapp create --name sre-frontend --runtime "NODE:20-lts"
az webapp create --name sre-backend-az1 --runtime "PYTHON:3.11"
az webapp create --name sre-backend-az2 --runtime "PYTHON:3.11"
```

#### 4. Data Services
```bash
# Redis Cache (takes 15-20 min)
az redis create \
  --name redis-sre-ha \
  --sku Standard \
  --vm-size C2

# Cosmos DB
az cosmosdb create \
  --name cosmos-sre-mongo \
  --kind MongoDB

# Storage Account
az storage account create \
  --name storsreimages4131 \
  --sku Standard_LRS
```

#### 5. Key Vault & Security
```bash
# Create Key Vault
az keyvault create --name kv-opsc-sre-74668

# Store secrets
az keyvault secret set --name StorageAccountKey --value "..."
az keyvault secret set --name CosmosMongoDBConnectionString --value "..."
```

---

## 📚 Understanding Each Component

### Why App Services (Not VMs)?

**Pros:**
- ✅ Fully managed (no OS updates)
- ✅ Auto-scaling built-in
- ✅ Easy deployment (git push or zip)
- ✅ HTTPS by default
- ✅ Built-in monitoring

**Cons:**
- ❌ Less control than VMs
- ❌ Cold start delays (B1 tier)

### Why Redis for Caching?

**Benefits:**
- ⚡ In-memory = super fast (microsecond latency)
- 🔄 Supports data structures (hash, set, sorted set)
- 📊 Perfect for session storage
- 🎯 Pub/sub for real-time updates

**Alternative:** Could use Cosmos DB cache, but slower

### Why Cosmos DB (Not Azure SQL)?

**For this project:**
- ✅ MongoDB API = familiar + flexible schema
- ✅ Vector search for image embeddings
- ✅ Auto-scaling (serverless mode)
- ✅ Globally distributed (can scale later)

**SQL would work too** - but JSON documents are easier for IoT data

### Why MQTT for Devices?

**Industry Standard:**
- 📡 Lightweight protocol for IoT
- 🔋 Low bandwidth usage
- 📲 Pub/sub pattern
- 🌐 100,000 devices can connect

---

## 🚀 Local Development Setup

### Run All Infrastructure Locally

```bash
cd infra
docker-compose up -d
```

**What this starts:**
```
✅ MQTT (mosquitto) → localhost:1883
✅ RabbitMQ → localhost:5672 (UI: localhost:15672)
✅ Redis → localhost:6379
✅ MongoDB → localhost:27017
✅ PostgreSQL → localhost:5432
```

**Connect to local services:**
```python
# Redis
import redis
r = redis.Redis(host='localhost', port=6379, password='hackathon2024')

# MongoDB
from pymongo import MongoClient
client = MongoClient('mongodb://admin:hackathon2024@localhost:27017/')

# MQTT
import paho.mqtt.client as mqtt
client = mqtt.Client()
client.connect("localhost", 1883)
```

---

## 📖 Learning Resources

### Understanding Azure Services

**App Services:**
- https://learn.microsoft.com/en-us/azure/app-service/

**Redis Cache:**
- https://learn.microsoft.com/en-us/azure/azure-cache-for-redis/

**Cosmos DB:**
- https://learn.microsoft.com/en-us/azure/cosmos-db/

**Key Vault:**
- https://learn.microsoft.com/en-us/azure/key-vault/

### MQTT & IoT

**MQTT Protocol:**
- https://mqtt.org/
- https://www.hivemq.com/mqtt-essentials/

**RabbitMQ:**
- https://www.rabbitmq.com/tutorials

---

## 🎯 Your Tasks

### Varad (Backend):

1. **Understand the data flow:**
   - MQTT → Your consumer → Redis/Cosmos
   - RabbitMQ → Your consumer → Redis/Cosmos
   - FastAPI → Read from Redis/Cosmos → Return JSON

2. **Build:**
   - Device simulator (publish MQTT)
   - User simulator (publish RabbitMQ)
   - MQTT consumer worker
   - RabbitMQ consumer worker
   - FastAPI endpoints

3. **Deploy:**
   - Deploy to `sre-backend-az1` and `sre-backend-az2`

### Samip (Frontend):

1. **Understand the dashboard:**
   - 4 main sections (deployment, users, devices, images)
   - Calls FastAPI endpoints
   - Displays real-time data

2. **Build:**
   - Next.js pages
   - shadcn/ui components
   - API client (fetch/axios)

3. **Deploy:**
   - Deploy to `sre-frontend`

---

## 🆘 Getting Help

**If you need:**
- Credentials → Check `.env` file or ask Bala
- Azure access → Use Bala's login for now
- Deploy help → See deployment guides
- Infrastructure questions → Ask Bala

**Useful Commands:**
```bash
# Check Redis status
az redis show -n redis-sre-ha -g rg-cmpe273-sre-hackathon

# View all resources
az resource list -g rg-cmpe273-sre-hackathon --output table

# Get app service logs
az webapp log tail --name sre-backend-az1 -g rg-cmpe273-sre-hackathon
```

---

**Team OPSC** | Infrastructure by Bala | CMPE273 SRE Hackathon | November 2025
