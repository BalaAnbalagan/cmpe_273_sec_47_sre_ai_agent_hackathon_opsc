# SRE AI Agent Hackathon - Demo Guide

**Team OPSC:** Bala Anbalagan, Varad Poddar, Samip Niraula
**Date:** November 16, 2025 @ 5 PM
**Professor:** Chandrasekar Vuppalapati

---

## Quick Demo Flow (15 Minutes)

### 1. Show Infrastructure (2 min)

**Azure Portal:**
- Open resource group: `rg-cmpe273-sre-hackathon`
- Show all 12 resources running
- Point out: MQTT broker, RabbitMQ, Redis, Cosmos DB, Key Vault, App Services

**Terminal:**
```bash
# Show both backends online
curl https://sre-backend-az1.azurewebsites.net/sre/status
curl https://sre-backend-az2.azurewebsites.net/sre/status
```

### 2. Show Frontend Dashboard (3 min)

**Open:** http://localhost:3000 (or deployed URL)

**Demonstrate:**
- Real-time status from both availability zones
- Toggle between AZ1 and AZ2 (< 3ms failover)
- Live Azure services monitoring
- Cohere AI status check
- API endpoint list

### 3. Run Simulators (3 min)

**Terminal 1 - MQTT Devices:**
```bash
cd simulators
pip install -r requirements.txt
python mqtt_device_simulator.py
```

Show: 100,000 devices publishing telemetry across 10 sites

**Terminal 2 - User Activity:**
```bash
python rabbitmq_user_simulator.py
```

Show: Active user sessions, real-time metrics

### 4. Cohere AI Demos (5 min)

**Run Demo Script:**
```bash
cd scripts
python demo_queries.py
```

**Highlights:**
1. **Natural Language Search:**
   - "turbine sites with workers without hard hats"
   - "sites with high safety compliance"

2. **Safety Analysis:**
   - Overall safety score
   - Violation findings
   - Recommendations

3. **RAG Chat:**
   - "What safety violations do you see?"
   - Context-aware responses

4. **Log Analysis:**
   - Top IPs generating Error 400
   - Device diagnostics

### 5. Architecture Explanation (2 min)

**Show README.md diagram:**

```
Users/Devices → Frontend (Next.js) → Backend (FastAPI AZ1/AZ2)
                                         ↓
                              MQTT + RabbitMQ + Redis + Cosmos DB
                                         ↓
                                    Cohere AI (RAG)
```

**Key Points:**
- 99.99999% availability target (Tier-0)
- Multi-zone redundancy
- Message-driven architecture
- AI-powered site intelligence
- Secure credential management (Key Vault + UMI)

---

## Detailed Component Demos

### MQTT Device Simulation

**What it does:**
- Simulates 100,000 IoT devices
- 10 global sites (ND-RAVEN, TX-EAGLE, etc.)
- 4 device types: turbines, thermal engines, electrical rotors, connected devices
- Real-time telemetry: temperature, pressure, RPM, voltage, status

**Topic structure:** `og/field/{site_id}/{device_type}/{device_id}`

**Run:**
```bash
cd simulators
python mqtt_device_simulator.py
```

**Expected output:**
```
🚀 MQTT Device Simulator Starting...
   Broker: opsc-mqtt-sjsu.westus2.azurecontainer.io:1883
   Devices: 100,000
   Sites: 10

Round 1: Published 100,000 messages in 12.45s
Round 2: Published 100,000 messages in 11.89s
```

### RabbitMQ User Activity

**What it does:**
- Simulates active web users (up to 5,000 concurrent)
- User sessions with login/logout
- Activity tracking (dashboard views, reports, diagnostics)
- Real-time metrics by region and role

**Run:**
```bash
cd simulators
python rabbitmq_user_simulator.py
```

**Expected output:**
```
✅ 1,847 users logged in

Round 10: Active users: 1,923
Round 20: Active users: 2,104
```

### Cohere AI Integration

**Natural Language Search:**
```bash
curl -X POST https://sre-backend-az1.azurewebsites.net/sre/images/search-nl \
  -H "Content-Type: application/json" \
  -d '{"query": "turbine sites with workers without hard hats", "top_k": 5}'
```

**Safety Analysis:**
```bash
curl -X POST https://sre-backend-az1.azurewebsites.net/sre/images/safety-analysis \
  -H "Content-Type: application/json" \
  -d '{"max_images": 20}'
```

**Chat with Images:**
```bash
curl -X POST https://sre-backend-az1.azurewebsites.net/sre/images/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What safety violations do you see across our sites?"}'
```

---

## API Endpoints Reference

### System Status
```bash
GET  /sre/status                    # Full system status
GET  /sre/deployment-version        # Deployment info
GET  /sre/images/cohere-status      # Cohere availability
```

### IoT & User Data
```bash
POST /sre/telemetry                 # IoT device data
POST /sre/user-metric               # User session data
```

### AI-Powered Analytics
```bash
POST /sre/images/search-nl          # Natural language search
POST /sre/images/chat               # RAG-based Q&A
POST /sre/images/safety-analysis    # Safety compliance
POST /sre/images/embed-description  # Generate embeddings
```

### Log Analysis
```bash
POST /sre/top-ips                   # Top error-generating IPs
POST /sre/search-images             # Vector similarity search
```

---

## Professor's Requirements Checklist

### ✅ Core Requirements

- [x] **Tier-0 Application** - 99.99999% availability target
- [x] **Real-time User Access** - Redis cache with session state
- [x] **IoT Telemetry** - MQTT topics for 100K devices
- [x] **Message Queues** - RabbitMQ for user activity
- [x] **Frontend** - Next.js web interface
- [x] **Middleware** - FastAPI orchestration
- [x] **Backend** - Redis proxy to persistent DB
- [x] **Database** - Cosmos DB (MongoDB API)

### ✅ Device Data Simulation

- [x] 100,000 field devices across 10 sites
- [x] Device types: turbines, thermal engines, electrical rotors, connected devices
- [x] MQTT topic convention: `og/field/{site_id}/{device_type}/{device_id}`
- [x] Uniform JSON schema for telemetry

### ✅ User Data Simulation

- [x] Active web-application users
- [x] User session tracking with timestamps
- [x] Real-time analytics via RabbitMQ
- [x] Performance monitoring metrics

### ✅ Site Camera Data & AI

- [x] **Cohere Embedding Models** - Vector embeddings for images
- [x] **Image Classification** - Semantic understanding
- [x] **Anomaly Detection** - Safety violation identification
- [x] **Contextual Search** - Natural language queries
- [x] **MongoDB/Redis Storage** - Image metadata and embeddings

### ✅ Device Diagnostics & Log Analysis

- [x] **RAG (Retrieval-Augmented Generation)** - Context-aware responses
- [x] **Natural Language Queries:**
  - "Give me turbine sites with workers without hats"
  - "Give me sites with high safety compliance"
  - "Get sites where engineer has hard hat and tablet"
- [x] **IP Analysis** - "List most frequent IPs generating Error 400"

### ✅ Additional Achievements

- [x] **Security-First** - Azure Key Vault + User Managed Identity
- [x] **Multi-Zone Deployment** - AZ1 + AZ2 with failover
- [x] **Cost-Optimized** - ~$62/week infrastructure
- [x] **Production-Ready** - Deployed and operational
- [x] **Well-Documented** - README, guides, inline comments

---

## Troubleshooting

### Simulators not connecting?

**Check environment variables:**
```bash
cd simulators
cat ../.env | grep MQTT
cat ../.env | grep RABBITMQ
```

**Test connectivity:**
```bash
# MQTT
nc -zv opsc-mqtt-sjsu.westus2.azurecontainer.io 1883

# RabbitMQ
nc -zv opsc-rabbitmq-sjsu.westus2.azurecontainer.io 5672
```

### Backend not responding?

**Check Azure App Service status:**
```bash
az webapp show --name sre-backend-az1 --resource-group rg-cmpe273-sre-hackathon --query state
```

**View logs:**
```bash
az webapp log tail --name sre-backend-az1 --resource-group rg-cmpe273-sre-hackathon
```

### Cohere API errors?

**Verify API key in Key Vault:**
```bash
az keyvault secret show --vault-name kv-opsc-sre-74668 --name CohereAPIKey
```

---

## Cost Breakdown

| Component | Weekly Cost |
|-----------|-------------|
| App Service Plan (B1) | ~$13 |
| Redis Cache (Standard C2) | ~$18 |
| Cosmos DB (Serverless) | ~$20 |
| Storage Account | ~$5 |
| Container Registry | ~$3 |
| Container Instances (2) | ~$2 |
| Key Vault | ~$1 |
| **Total** | **~$62/week** |

**Cohere API:** ~$0.20 for hackathon (very cost-effective!)

---

## Team Roles

- **Bala Anbalagan:** Azure infrastructure, backend deployment, Key Vault integration
- **Varad Poddar:** Frontend development, UI/UX, dashboard features
- **Samip Niraula:** AI integration, Cohere embeddings, RAG implementation

---

## Demo Talking Points

1. **Enterprise-Grade Architecture**
   - "We built a production-ready Tier-0 system targeting 99.99999% availability"
   - Multi-zone deployment for redundancy

2. **Scale**
   - "Simulating 100,000 IoT devices across 10 global sites"
   - Up to 5,000 concurrent users

3. **AI Innovation**
   - "Cohere embeddings enable natural language search over site images"
   - RAG provides context-aware answers about safety compliance

4. **Security**
   - "Zero hardcoded secrets - everything in Azure Key Vault"
   - User Managed Identity for passwordless authentication

5. **Practical SRE**
   - "Real-time monitoring, log analysis, and predictive insights"
   - Message-driven architecture for scalability

---

**Ready to Demo!** 🚀
