# System Status Report - CMPE 273 SRE Hackathon

**Team OPSC** | **Last Updated:** November 17, 2025

---

## 🚀 Deployment Status

### Frontend
- **URL:** https://sre-frontend.azurewebsites.net
- **Status:** ✅ Running
- **Auto-Deployment:** ✅ Active (GitHub Actions)
- **Local Dev:** http://localhost:3001

### Backend - Multi-Zone
- **AZ1:** https://sre-backend-az1.azurewebsites.net ✅ Running
- **AZ2:** https://sre-backend-az2.azurewebsites.net ✅ Running
- **Failover:** ✅ Configured (automatic)

---

## 📊 Azure Services Status

### Core Services
| Service | Status | Details |
|---------|--------|---------|
| **Key Vault** | ✅ Available | `kv-opsc-sre-74668` (20 secrets) |
| **Redis Cache** | ✅ Connected | Caching layer operational |
| **Cosmos DB** | ✅ Connected | MongoDB API with 809 RAG documents |
| **Storage Account** | ✅ Active | `storsreimages4131` (blob: site-images) |
| **Cohere AI** | ✅ Configured | `embed-english-v3.0` + `command-r-plus` |

### Message Brokers

#### MQTT Broker
- **Container:** `mqtt-broker`
- **FQDN:** `opsc-mqtt-sjsu.westus2.azurecontainer.io`
- **Port:** `1883`
- **IP:** `20.72.232.216`
- **Status:** ✅ Running
- **Restart Count:** 0

**Health Check:**
```bash
# Test MQTT connectivity
nc -zv -w5 opsc-mqtt-sjsu.westus2.azurecontainer.io 1883

# Expected output:
# Connection to opsc-mqtt-sjsu.westus2.azurecontainer.io port 1883 [tcp/ibm-mqisdp] succeeded!
```

**Check Container Status:**
```bash
az container show --name mqtt-broker \
  --resource-group rg-cmpe273-sre-hackathon \
  --query "{Name:name, State:instanceView.state, RestartCount:containers[0].instanceView.restartCount}"
```

---

#### RabbitMQ Broker
- **Container:** `rabbitmq-broker`
- **FQDN:** `opsc-rabbitmq-sjsu.westus2.azurecontainer.io`
- **Port:** `5672` (AMQP)
- **Management:** `15672` (Web UI)
- **IP:** `4.242.119.173`
- **Status:** ✅ Running
- **Restart Count:** 0

**Health Check:**
```bash
# Test RabbitMQ connectivity
nc -zv -w5 opsc-rabbitmq-sjsu.westus2.azurecontainer.io 5672

# Expected output:
# Connection to opsc-rabbitmq-sjsu.westus2.azurecontainer.io port 5672 [tcp/amqp] succeeded!
```

**Check Container Status:**
```bash
az container show --name rabbitmq-broker \
  --resource-group rg-cmpe273-sre-hackathon \
  --query "{Name:name, State:instanceView.state, RestartCount:containers[0].instanceView.restartCount}"
```

**Access Management UI:**
```
URL: http://opsc-rabbitmq-sjsu.westus2.azurecontainer.io:15672
Default Credentials: guest/guest
```

---

## 🔐 Security & Authentication

### User Managed Identity (UMI)
- **Name:** `umi-sre-opsc`
- **Client ID:** `9de1422a-8247-4986-b63d-bffe81f0d114`
- **Assigned To:** Both AZ1 and AZ2 backend app services

### Key Vault Secrets (20 Total)
```
✅ CohereAPIKey
✅ CosmosDBConnectionString
✅ RedisConnectionString
✅ AzureStorageConnectionString
✅ MQTTHost
✅ MQTTPort
✅ MQTTUsername
✅ MQTTPassword
✅ RabbitMQHost
✅ RabbitMQPort
✅ RabbitMQUsername
✅ RabbitMQPassword
✅ RabbitMQURL (Complete connection string)
... and 7 more
```

---

## 🤖 RAG & AI System

### Document Processing
- **Documents Embedded:** 809
- **Source:** BP 10-K Annual Reports (392+ pages)
- **Embedding Model:** Cohere `embed-english-v3.0`
- **Chat Model:** Cohere `command-r-plus`
- **Storage:** Cosmos DB (MongoDB)

### AI Endpoints
| Endpoint | Purpose | Status |
|----------|---------|--------|
| `GET /sre/images/cohere-status` | Check AI availability | ✅ Working |
| `POST /sre/images/search-nl` | Natural language search | ✅ Working |
| `POST /sre/images/safety-analysis` | Safety violation detection | ✅ Working |
| `POST /sre/images/chat` | RAG-based Q&A with citations | ✅ Working |

---

## 📈 Quick Health Checks

### 1. Backend Status (Comprehensive)
```bash
# Check AZ1
curl -s https://sre-backend-az1.azurewebsites.net/sre/status | python3 -m json.tool

# Check AZ2
curl -s https://sre-backend-az2.azurewebsites.net/sre/status | python3 -m json.tool
```

### 2. Frontend Health
```bash
curl -I https://sre-frontend.azurewebsites.net
# Should return: HTTP/2 200
```

### 3. Cohere AI Status
```bash
curl -s https://sre-backend-az1.azurewebsites.net/sre/images/cohere-status | python3 -m json.tool
```

### 4. All Container Instances
```bash
az container list \
  --resource-group rg-cmpe273-sre-hackathon \
  --query "[].{Name:name, State:instanceView.state, IP:ipAddress.ip, FQDN:ipAddress.fqdn}" \
  --output table
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions - Frontend Deployment
- **Workflow:** [azure-frontend-deploy.yml](.github/workflows/azure-frontend-deploy.yml)
- **Trigger:** Every push to `main` branch
- **Status:** ✅ Active
- **Last Run:** Success (1m36s)
- **View Runs:** https://github.com/BalaAnbalagan/cmpe_273_sec_47_sre_ai_agent_hackathon_opsc/actions

**What Happens:**
1. Checkout code
2. Install Node.js 20
3. Build Next.js app (standalone)
4. Package deployment (+ static files)
5. Login to Azure
6. Deploy to App Service
7. Restart app

**Typical Duration:** 1-2 minutes

---

## 🌐 Network & Connectivity

### Frontend → Backend Communication
- **Environment Variables:**
  - `NEXT_PUBLIC_API_URL_AZ1`: https://sre-backend-az1.azurewebsites.net
  - `NEXT_PUBLIC_API_URL_AZ2`: https://sre-backend-az2.azurewebsites.net
- **CORS:** ✅ Enabled on both backends (`allow_origins=["*"]`)
- **Failover:** ✅ Automatic (frontend switches if AZ1 down)

### Backend → Azure Services
- **UMI Authentication:** ✅ All services use managed identity
- **Key Vault Access:** ✅ Secrets loaded at startup
- **Network:** All services in West US 2 region

---

## 📋 Demo Checklist

### Pre-Demo Verification (5 minutes before)

```bash
# 1. Check all backends
curl https://sre-backend-az1.azurewebsites.net/sre/status
curl https://sre-backend-az2.azurewebsites.net/sre/status

# 2. Check frontend
curl -I https://sre-frontend.azurewebsites.net

# 3. Check MQTT broker
nc -zv opsc-mqtt-sjsu.westus2.azurecontainer.io 1883

# 4. Check RabbitMQ broker
nc -zv opsc-rabbitmq-sjsu.westus2.azurecontainer.io 5672

# 5. Check container health
az container list --resource-group rg-cmpe273-sre-hackathon --query "[].{Name:name, State:instanceView.state}" -o table

# 6. Test AI search
curl -X POST https://sre-backend-az1.azurewebsites.net/sre/images/search-nl \
  -H "Content-Type: application/json" \
  -d '{"query": "safety violations", "top_k": 3}'
```

### Expected Results
- ✅ All HTTP requests return 200 OK
- ✅ Both MQTT and RabbitMQ connections succeed
- ✅ All containers show "Running" state
- ✅ AI search returns results with similarity scores

---

## 🛠️ Troubleshooting

### Issue: MQTT/RabbitMQ Shows as "Offline" in Frontend

**Cause:** Backend `/sre/status` endpoint only shows addresses, not health status

**Current Behavior:**
```json
{
  "mqtt_broker": "opsc-mqtt-sjsu.westus2.azurecontainer.io:1883",
  "rabbitmq_broker": "opsc-rabbitmq-sjsu.westus2.azurecontainer.io:5672"
}
```

**Actual Status:** Both are running fine (verified via `nc` and Azure CLI)

**For Demo:**
- Use Azure CLI to show container status
- Use `nc` command to demonstrate connectivity
- Mention that brokers are operational but status reporting is informational only

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────┐
│          Frontend (sre-frontend)            │
│     https://sre-frontend.azurewebsites.net  │
│         (Next.js + shadcn/ui)               │
└───────────────┬─────────────────────────────┘
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
┌───────────────┐  ┌───────────────┐
│ Backend AZ1   │  │ Backend AZ2   │
│ (FastAPI)     │  │ (FastAPI)     │
└───────┬───────┘  └───────┬───────┘
        │                  │
        └────────┬─────────┘
                 │
    ┌────────────┼───────────────┐
    │            │               │
    ▼            ▼               ▼
┌────────┐  ┌─────────┐  ┌──────────────┐
│ Redis  │  │ Cosmos  │  │  Key Vault   │
│ Cache  │  │   DB    │  │  (Secrets)   │
└────────┘  └─────────┘  └──────────────┘
    │            │               │
    └────────────┼───────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌──────────┐
│  MQTT  │  │RabbitMQ│  │ Cohere   │
│ Broker │  │ Broker │  │   AI     │
└────────┘  └────────┘  └──────────┘
```

---

## 📞 Support Contacts

**Team OPSC:**
- Bala Anbalagan: Backend, Infrastructure, RAG
- Varad Poddar: Frontend UI
- Samip Niraula: PDF Processing

**Repository:** https://github.com/BalaAnbalagan/cmpe_273_sec_47_sre_ai_agent_hackathon_opsc

---

## ✅ System Health Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Frontend | ✅ Operational | Auto-deploy enabled |
| Backend AZ1 | ✅ Operational | All services connected |
| Backend AZ2 | ✅ Operational | All services connected |
| MQTT Broker | ✅ Running | Container healthy |
| RabbitMQ Broker | ✅ Running | Container healthy |
| Redis Cache | ✅ Connected | Caching active |
| Cosmos DB | ✅ Connected | 809 RAG documents |
| Cohere AI | ✅ Configured | Embeddings + Chat |
| Key Vault | ✅ Available | 20 secrets |
| CI/CD | ✅ Active | GitHub Actions |

**Overall System Status:** ✅ **FULLY OPERATIONAL**

**Demo Readiness:** ✅ **READY**

---

**Last Verified:** November 17, 2025 - All systems operational for 5 PM demo
