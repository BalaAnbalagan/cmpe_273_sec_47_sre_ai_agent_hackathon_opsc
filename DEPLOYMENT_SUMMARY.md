# Azure Infrastructure Deployment Summary
## CMPE273 SRE Hackathon - Team OPSC

**Deployment Date:** November 15, 2025  
**Region:** West US 2 (California - closest to SF Bay Area)  
**Resource Group:** rg-cmpe273-sre-hackathon

---

## ✅ Successfully Deployed Resources

### 1. Networking
- **Virtual Network:** vnet-sre (10.0.0.0/16)
  - app-subnet: 10.0.1.0/24
  - mq-subnet: 10.0.2.0/24
  - data-subnet: 10.0.3.0/24

### 2. Compute (App Services)
- **App Service Plan:** asp-sre-ha (Basic B1, Linux)
- **Frontend:**
  - Name: sre-frontend
  - Runtime: Node.js 20 LTS
  - URL: https://sre-frontend.azurewebsites.net
  
- **Backend AZ1:**
  - Name: sre-backend-az1
  - Runtime: Python 3.11
  - URL: https://sre-backend-az1.azurewebsites.net
  
- **Backend AZ2:**
  - Name: sre-backend-az2
  - Runtime: Python 3.11
  - URL: https://sre-backend-az2.azurewebsites.net

### 3. Data Layer

**Cosmos DB (MongoDB API):**
- Account: cosmos-sre-mongo
- Database: sre-database
- API: MongoDB 4.2
- Status: ✅ Ready
- Connection: Stored in Key Vault

**Storage Account:**
- Name: storsreimages4131
- SKU: Standard_LRS (Hot tier)
- Containers:
  - site-images
  - system-logs
- Status: ✅ Ready
- Keys: Stored in Key Vault

**Redis Cache:**
- Name: redis-sre-ha
- SKU: Standard C2 (2.5GB)
- Status: ⏳ Creating (15-20 min total, ~10 min remaining)
- Host: redis-sre-ha.redis.cache.windows.net
- Port: 6380 (SSL)

### 4. Security

**Azure Key Vault:**
- Name: kv-opsc-sre-74668
- Secrets Stored:
  - StorageAccountKey
  - StorageConnectionString
  - CosmosMongoDBConnectionString
  - FrontendURL
  - BackendAZ1URL
  - BackendAZ2URL
  - RedisKey (will be added when Redis completes)

---

## ⏳ In Progress

### Redis Cache
- Status: Creating
- Expected completion: ~10 minutes
- Once complete, key will be added to Key Vault

### MQTT & RabbitMQ Brokers (Azure Container Instances)
- Status: Blocked (Docker Hub registry issues)
- **Workaround:** Use local Docker Compose
- Can retry deployment later or keep using local

---

## 📋 Next Steps for Team

### For Bala (Infrastructure):
1. ⏳ Wait for Redis to complete (~10 min)
2. Add Redis key to Key Vault when ready
3. Retry MQTT/RabbitMQ ACI deployment (or use local Docker)
4. Update .env file with Redis credentials

### For Varad (Backend):
1. Clone repository
2. Use local Docker Compose for MQTT/RabbitMQ:
   ```bash
   cd infra
   docker-compose up -d
   ```
3. Get credentials from Key Vault or .env file
4. Build FastAPI backend
5. Deploy to:
   - https://sre-backend-az1.azurewebsites.net
   - https://sre-backend-az2.azurewebsites.net

### For Samip (Frontend):
1. Clone repository
2. Get backend URLs from .env
3. Build Next.js dashboard
4. Deploy to: https://sre-frontend.azurewebsites.net

---

## 🔑 Accessing Credentials

### Option 1: Azure Key Vault (Recommended)
```bash
# Get Cosmos DB connection string
az keyvault secret show \
  --vault-name kv-opsc-sre-74668 \
  --name CosmosMongoDBConnectionString \
  --query value -o tsv

# Get Storage key
az keyvault secret show \
  --vault-name kv-opsc-sre-74668 \
  --name StorageAccountKey \
  --query value -o tsv

# When Redis is ready:
az keyvault secret show \
  --vault-name kv-opsc-sre-74668 \
  --name RedisKey \
  --query value -o tsv
```

### Option 2: .env File
Located at project root: `/.env`
- Contains all configuration
- Redis password pending (will update when ready)

---

## 💰 Cost Estimate

### Current Deployment (~$65-80/week):
- App Service Plan B1: ~$13/week
- Redis Standard C2: ~$18/week
- Cosmos DB (serverless): ~$20/week
- Storage Account: ~$5/week
- Key Vault: ~$1/week
- Networking: ~$5/week

**Total: ~$62/week** (very cost-effective for hackathon!)

---

## 🧹 Cleanup (After Hackathon)

Delete all resources:
```bash
cd infra/scripts
./cleanup.sh
```

Or manually:
```bash
az group delete --name rg-cmpe273-sre-hackathon --yes
```

---

## 📞 Support

**Key Vault Name:** kv-opsc-sre-74668  
**Resource Group:** rg-cmpe273-sre-hackathon  
**Region:** West US 2  
**Subscription:** The Krishnan Group

**Check Redis Status:**
```bash
az redis show -n redis-sre-ha -g rg-cmpe273-sre-hackathon \
  --query "{Status:provisioningState}" -o table
```

**View All Resources:**
```bash
az resource list -g rg-cmpe273-sre-hackathon --output table
```

---

**Team OPSC** | Infrastructure by Bala | CMPE273 SRE Hackathon | Nov 2025
