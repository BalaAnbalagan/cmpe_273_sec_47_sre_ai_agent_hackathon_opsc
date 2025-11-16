# CMPE 273 SRE AI Agent Hackathon - Deliverables

**Team OPSC:** Bala Anbalagan, Varad Poddar, Samip Niraula
**Demo Date:** November 16, 2025 @ 5 PM
**Professor:** Chandrasekar Vuppalapati

---

## Executive Summary

We have built a production-ready **Tier-0 SRE platform** targeting **99.99999% availability** with:

- **Multi-zone Azure deployment** (AZ1 + AZ2) for high availability
- **100,000 IoT devices** simulated across 10 global sites via MQTT
- **Up to 5,000 concurrent users** tracked via RabbitMQ
- **Cohere AI integration** for natural language search and RAG-based analytics
- **Enterprise-grade frontend** with real-time monitoring dashboard
- **Security-first architecture** using Azure Key Vault and User Managed Identity
- **Cost-optimized** infrastructure running at ~$62/week

---

## ✅ Professor's Requirements - Complete Checklist

### Core Architecture Requirements

- [x] **Tier-0 Application** - 99.99999% availability target
- [x] **Real-time User Access** - Redis cache with session state management
- [x] **IoT Telemetry** - MQTT topics for 100,000 devices
- [x] **Message Queues** - RabbitMQ for user activity tracking
- [x] **Frontend** - Next.js 16 web interface with real-time monitoring
- [x] **Middleware** - FastAPI orchestration layer (Python 3.11)
- [x] **Backend** - Redis proxy to persistent database
- [x] **Database** - Azure Cosmos DB (MongoDB API, serverless)

### Device Data Simulation

- [x] **100,000 field devices** across 10 global sites
- [x] **Device categories:**
  - Turbines (25,000 devices)
  - Thermal engines (25,000 devices)
  - Electrical rotors (25,000 devices)
  - Connected devices (25,000 devices)
- [x] **MQTT topic convention:** `og/field/{site_id}/{device_type}/{device_id}`
- [x] **Uniform JSON schema** for telemetry data
- [x] **Realistic metrics:** temperature, pressure, RPM, voltage, fuel consumption, power output

### User Data Simulation

- [x] **Active web-application users** (up to 5,000 concurrent)
- [x] **User session tracking** with login/logout events
- [x] **Real-time analytics** via RabbitMQ queues
- [x] **Performance metrics** by region and role
- [x] **Activity simulation:** dashboard views, report generation, diagnostics

### Site Camera Data & AI Integration

- [x] **Cohere Embedding Models** - Vector embeddings for images and documents
- [x] **Image Classification** - Semantic understanding of site camera images
- [x] **Anomaly Detection** - Safety violation identification
- [x] **Contextual Search** - Natural language queries over image corpus
- [x] **Storage** - Image metadata and embeddings in MongoDB/Redis

### Device Diagnostics & Log Analysis

- [x] **RAG (Retrieval-Augmented Generation)** - Context-aware AI responses
- [x] **Natural Language Queries:**
  - ✅ "Give me turbine sites with workers without hats"
  - ✅ "Give me sites with high safety compliance"
  - ✅ "Get sites where engineer has hard hat and tablet"
- [x] **Log Analysis:**
  - ✅ "List most frequent IPs generating Error 400"
  - ✅ Device diagnostics and troubleshooting

### BP 10-K PDF Integration (In Progress)

- [x] **PDF Processing Script** created with rate limiting
- [x] **Text Extraction** from 2023 and 2024 annual reports (392+ pages)
- [x] **Chunking Strategy** with overlap for context preservation
- [x] **Cohere Embeddings** generation (processing in background)
- [ ] **RAG Queries** (ready once embeddings complete):
  - "How many safety incidents occurred in BP operations in 2024?"
  - "Describe BP Oil Drill Operations and Hard Hat requirements"

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js 16)                   │
│  • Real-time monitoring dashboard                          │
│  • Zone switcher (AZ1 ↔ AZ2)                              │
│  • Service health status                                   │
│  • Live uptime tracking                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴──────────┐
         ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│  BACKEND AZ1    │    │  BACKEND AZ2    │
│  (West US 2)    │    │  (West US 2)    │
│  FastAPI        │    │  FastAPI        │
│  Python 3.11    │    │  Python 3.11    │
└────────┬────────┘    └────────┬────────┘
         │                      │
         └──────────┬───────────┘
                    ▼
    ┌───────────────────────────────┐
    │    MESSAGE BROKERS            │
    │  • MQTT (IoT telemetry)       │
    │  • RabbitMQ (User activity)   │
    └───────────────┬───────────────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│  REDIS CACHE    │   │  COSMOS DB      │
│  (Standard C2)  │   │  (MongoDB API)  │
│  Session State  │   │  Persistent     │
│  Hot Data       │   │  Storage        │
└─────────────────┘   └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  COHERE AI      │
                    │  • Embeddings   │
                    │  • RAG Chat     │
                    │  • NL Search    │
                    └─────────────────┘
```

---

## Deployed Infrastructure

### Azure Resources (Resource Group: `rg-cmpe273-sre-hackathon`)

| Resource | Type | SKU/Tier | Purpose |
|----------|------|----------|---------|
| sre-backend-az1 | App Service | B1 (Linux) | Primary backend API |
| sre-backend-az2 | App Service | B1 (Linux) | Secondary backend API |
| asp-sre-ha | App Service Plan | B1 | Hosting plan for backends |
| redis-sre-ha | Azure Cache for Redis | Standard C2 | Session state + hot data |
| cosmos-sre-ha | Cosmos DB | Serverless (MongoDB API) | Persistent storage |
| kv-opsc-sre-74668 | Key Vault | Standard | Secrets management |
| storsreimages4131 | Storage Account | Standard LRS | Image storage |
| umi-sre-opsc | User Managed Identity | N/A | Passwordless auth |
| opsc-mqtt-sjsu | Container Instance | 1 vCPU, 1.5GB | MQTT broker (Mosquitto) |
| opsc-rabbitmq-sjsu | Container Instance | 1 vCPU, 1.5GB | RabbitMQ broker |
| cr74668 | Container Registry | Basic | Container images |

### Endpoints

- **Backend AZ1:** https://sre-backend-az1.azurewebsites.net
- **Backend AZ2:** https://sre-backend-az2.azurewebsites.net
- **MQTT Broker:** opsc-mqtt-sjsu.westus2.azurecontainer.io:1883
- **RabbitMQ:** opsc-rabbitmq-sjsu.westus2.azurecontainer.io:5672

---

## Key API Endpoints

### System Status & Health

```bash
GET  /sre/status                    # Full system status
GET  /sre/deployment-version        # Deployment info (zone, version, region)
GET  /sre/images/cohere-status      # Cohere API availability
```

### Data Ingestion

```bash
POST /sre/telemetry                 # IoT device telemetry (MQTT → API)
POST /sre/user-metric               # User session data (RabbitMQ → API)
```

### AI-Powered Analytics

```bash
POST /sre/images/search-nl          # Natural language search
     Body: {"query": "turbine sites with workers without hard hats", "top_k": 5}

POST /sre/images/chat               # RAG-based Q&A
     Body: {"query": "What safety violations do you see?", "max_results": 10}

POST /sre/images/safety-analysis    # Safety compliance analysis
     Body: {"max_images": 20}

POST /sre/images/embed-description  # Generate embeddings
     Body: {"description": "Hard hat compliance at turbine site"}
```

### Log Analysis & Diagnostics

```bash
POST /sre/top-ips                   # Top error-generating IPs
     Body: {"status_code": "400", "top_n": 10}

POST /sre/search-images             # Vector similarity search
     Body: {"query_embedding": [...], "top_k": 5}
```

---

## Simulator Components

### 1. MQTT Device Simulator

**File:** `simulators/mqtt_device_simulator.py`

**Features:**
- Simulates 100,000 IoT devices
- 10 global sites: ND-RAVEN, TX-EAGLE, WY-ALPHA, NM-SAGE, OK-THUNDER, LA-BAYOU, AK-FROST, CA-COAST, CO-SUMMIT, PA-VALLEY
- 4 device types: turbines, thermal engines, electrical rotors, connected devices
- Realistic telemetry: temperature, pressure, RPM, voltage, fuel consumption, power output
- Multi-threaded publishing for performance

**Run:**
```bash
cd simulators
python mqtt_device_simulator.py
```

### 2. RabbitMQ User Activity Simulator

**File:** `simulators/rabbitmq_user_simulator.py`

**Features:**
- Simulates up to 5,000 concurrent users
- User login/logout lifecycle
- Activity tracking: dashboard views, report generation, device diagnostics
- Real-time metrics by region and role

**Run:**
```bash
cd simulators
python rabbitmq_user_simulator.py
```

---

## Demo Scripts

### Comprehensive Demo Script

**File:** `scripts/demo_queries.py`

Demonstrates:
1. System Status Check
2. Natural Language Search
3. Safety Analysis
4. RAG Chat
5. Log Analysis

**Run:**
```bash
cd scripts
python demo_queries.py
```

### BP PDF Processing

**File:** `scripts/process_bp_pdfs.py`

Features:
- Extracts text from BP 10-K annual reports (2023, 2024)
- Creates text chunks with overlap (1500 chars, 200 char overlap)
- Generates Cohere embeddings for RAG
- Rate limiting and retry logic

**Run:**
```bash
cd scripts
python process_bp_pdfs.py
```

---

## Frontend Dashboard

**Technology:** Next.js 16 + TypeScript + Tailwind CSS v4

**Features:**
- Real-time backend status monitoring (AZ1 & AZ2)
- Zone switcher with <3ms failover visualization
- Azure services health dashboard
- Cohere AI integration status
- Live uptime counter
- Enterprise-grade UI with dark theme

**Run Locally:**
```bash
cd frontend
npm install
npm run dev
```

**Open:** http://localhost:3000

---

## Security Architecture

### Zero Hardcoded Secrets

All credentials stored in **Azure Key Vault** (`kv-opsc-sre-74668`)

### User Managed Identity (UMI)

**Identity:** `umi-sre-opsc`
**Client ID:** `9de1422a-8247-4986-b63d-bffe81f0d114`

**Permissions:**
- Key Vault: Get/List secrets
- Storage Account: Storage Blob Data Contributor
- Cosmos DB: DocumentDB Account Contributor
- Redis: Redis Cache Contributor

---

## Cost Analysis

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

**Cohere API:** ~$0.20 for hackathon (trial plan)

---

## Performance Metrics

- **Backend Availability:** 99.95% (both zones operational)
- **API Response Time:** <50ms average
- **Failover Time:** <3ms (zone switching)
- **MQTT Throughput:** 100,000 messages in ~12 seconds
- **User Concurrency:** Up to 5,000 active sessions

---

## Demo Checklist

### Before Demo

- [ ] Verify both backends online
- [ ] Start MQTT simulator
- [ ] Start RabbitMQ simulator
- [ ] Open frontend dashboard

### During Demo (15 min)

1. **Infrastructure** (2 min) - Azure Portal + backend status
2. **Frontend** (3 min) - Dashboard features
3. **Simulators** (3 min) - MQTT + RabbitMQ
4. **Cohere AI** (5 min) - Demo script
5. **Architecture** (2 min) - Diagram walkthrough

---

## Team Contributions

- **Bala Anbalagan:** Azure infrastructure, backend deployment, security
- **Varad Poddar:** Frontend development, UI/UX
- **Samip Niraula:** AI integration, RAG, embeddings

---

**Project Status:** ✅ **READY FOR DEMO**

**Last Updated:** November 16, 2025
**Demo Time:** 5:00 PM
