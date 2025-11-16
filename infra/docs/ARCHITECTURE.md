# Infrastructure Architecture
## CMPE273 SRE Hackathon - Team OPSC

---

## Architecture Overview

This document describes the Azure infrastructure architecture for the Tier-0 SRE application with 99.99999% availability target.

---

## High-Level Architecture

```
Internet
    ↓
[Azure Front Door / DNS]
    ↓
┌─────────────────────────────────────────────────────────────┐
│                    Azure West US Region                      │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │   Zone 1     │   Zone 2     │   Zone 3     │            │
│  └──────────────┴──────────────┴──────────────┘            │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │          Application Tier (App Services)              │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │  │ Frontend │  │Backend   │  │Backend   │           │  │
│  │  │          │  │  AZ1     │  │  AZ2     │           │  │
│  │  └──────────┘  └──────────┘  └──────────┘           │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │          Messaging Tier (MQTT + RabbitMQ)            │  │
│  │  ┌──────────┐           ┌──────────┐                 │  │
│  │  │   MQTT   │           │ RabbitMQ │                 │  │
│  │  │  Broker  │           │  Broker  │                 │  │
│  │  └──────────┘           └──────────┘                 │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │          Data Tier (Redis + Cosmos DB)               │  │
│  │  ┌──────────┐           ┌──────────┐                 │  │
│  │  │  Redis   │           │ Cosmos   │                 │  │
│  │  │  Cache   │           │    DB    │                 │  │
│  │  │ Premium  │           │ MongoDB  │                 │  │
│  │  └──────────┘           └──────────┘                 │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │          Storage Tier (Blob Storage)                  │  │
│  │  ┌──────────┐           ┌──────────┐                 │  │
│  │  │  Images  │           │   Logs   │                 │  │
│  │  └──────────┘           └──────────┘                 │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘

External APIs
    ↓
[Cohere AI API]
```

---

## Network Architecture

### Virtual Network: vnet-sre (10.0.0.0/16)

```
vnet-sre (10.0.0.0/16)
│
├── app-subnet (10.0.1.0/24)
│   └── App Services (Frontend, Backend AZ1, Backend AZ2)
│
├── mq-subnet (10.0.2.0/24)
│   ├── MQTT Broker (Container Instance)
│   └── RabbitMQ Broker (Container Instance)
│
└── data-subnet (10.0.3.0/24)
    ├── Redis Cache (managed service)
    └── Cosmos DB (managed service)
```

### Network Security

- **Network Security Groups (NSG)** on each subnet
- **Service Endpoints** for Azure PaaS services
- **Public IPs** for MQTT and RabbitMQ (external device access)
- **HTTPS/TLS** for all App Service endpoints

---

## Component Details

### 1. Compute Layer

#### App Service Plan: asp-sre-ha
- **SKU:** P1v2 (Production) or B1 (Development)
- **Zones:** 1, 2 (zone-redundant)
- **OS:** Linux
- **Runtime:** Python 3.11 (backend), Node.js 18 (frontend)

#### Frontend App Service: sre-frontend
- **URL:** https://sre-frontend.azurewebsites.net
- **Framework:** Next.js + React + TypeScript
- **UI Library:** shadcn/ui
- **Purpose:** SRE Dashboard with 4 main sections
  1. Deployment Version / Failover
  2. Site Active Users
  3. Active Connected Devices
  4. Site Image Intelligence

#### Backend App Services
**sre-backend-az1** (Zone 1)
- **URL:** https://sre-backend-az1.azurewebsites.net
- **Framework:** FastAPI (Python)
- **Purpose:** Primary backend, region1 for failover simulation

**sre-backend-az2** (Zone 2)
- **URL:** https://sre-backend-az2.azurewebsites.net
- **Framework:** FastAPI (Python)
- **Purpose:** Secondary backend, region2 for failover simulation

#### Failover Mechanism
- Frontend can switch between AZ1 and AZ2 backends
- Simulates Tier-0 regional failover
- Target: < 0.003 seconds failover time

---

### 2. Messaging Layer

#### MQTT Broker (eclipse-mosquitto)
- **Protocol:** MQTT 3.1.1
- **Ports:** 1883 (MQTT), 8883 (MQTT over SSL), 9001 (WebSockets)
- **Topic Pattern:** `og/field/{site_id}/{device_type}/{device_id}`
- **Use Case:** 100,000 IoT devices publishing telemetry
- **Message Rate:** ~8,333 messages/second at peak
- **Persistence:** Enabled

Example Topics:
```
og/field/ND-RAVEN/turbine/TURB-00912
og/field/TX-EAGLE/thermal_engine/THRM-22177
og/field/WY-ALPHA/electrical_rotor/EROT-55031
og/field/NM-SAGE/connected_device/OGC-78402
```

#### RabbitMQ Broker
- **Protocol:** AMQP 1.0
- **Ports:** 5672 (AMQP), 15672 (Management UI)
- **Queue:** `webapp/active_users`
- **Use Case:** User activity metrics, session data
- **Message Rate:** ~1,000-5,000 messages/minute
- **Management UI:** http://<public-ip>:15672

---

### 3. Data Layer

#### Redis Cache: redis-sre-ha
- **SKU:** Premium P1 (6GB) with zone redundancy
- **Zones:** 1, 2
- **Port:** 6380 (SSL required)
- **Features:**
  - High availability with automatic failover
  - Data persistence (RDB + AOF)
  - Clustering support
  - Geo-replication capable

**Data Stored:**
- Active user sessions
- Device state cache
- Failover state (active_region, version)
- SRE dashboard metrics
- Optional: Image embeddings (vector data)

**Redis Keys Structure:**
```
users:active:<site_id>           → Set of active user IDs
users:sessions:<user_id>         → User session data (hash)
devices:active:<site_id>         → Set of active device IDs
devices:state:<device_id>        → Device telemetry (hash)
sre:deployment:version           → Current deployment version
sre:deployment:active_region     → Active region (az1 or az2)
sre:metrics:dashboard            → Cached dashboard data
```

#### Cosmos DB: cosmos-sre-mongo
- **API:** MongoDB 4.2
- **Consistency:** Session
- **Zone-Redundant:** Yes
- **Database:** sre-database

**Collections:**
- `device_images` - Site camera images metadata
- `image_embeddings` - Cohere embeddings (1024-4096 dimensions)
- `device_logs` - Optional device log history
- `user_history` - Optional user session history

**Document Structure:**
```javascript
// device_images collection
{
  "_id": ObjectId,
  "site_id": "ND-RAVEN",
  "image_id": "IMG-2025-11-15-001",
  "timestamp": ISODate,
  "blob_url": "https://...",
  "metadata": {
    "camera_id": "CAM-01",
    "resolution": "1920x1080"
  }
}

// image_embeddings collection
{
  "_id": ObjectId,
  "image_id": "IMG-2025-11-15-001",
  "embedding": [0.123, -0.456, ...], // 1024-4096 floats
  "model": "embed-english-v3.0",
  "tags": ["worker", "hard hat", "tablet"],
  "created_at": ISODate
}
```

---

### 4. Storage Layer

#### Storage Account: storsreimages*
- **SKU:** Standard_ZRS (Zone-Redundant Storage)
- **Tier:** Hot
- **Replication:** ZRS (3 copies across zones)

**Containers:**
- `site-images` - Site camera images (raw)
- `system-logs` - Application and system logs

**Access:**
- Public read access (optional)
- SAS tokens for secure access
- Connection string authentication

---

### 5. AI/ML Integration

#### Cohere AI API (External)
- **Models:**
  - `embed-english-v3.0` - Text/image embeddings
  - `command-r-plus` - Chat/RAG queries
- **Use Cases:**
  1. Image embedding generation
  2. Semantic image search
  3. Natural language log queries
  4. Word cloud generation

**Integration Flow:**
```
Site Image → Upload to Blob Storage
    ↓
Image Embedding Worker (backend/workers/image_embeddings.py)
    ↓
Call Cohere API → Generate embedding
    ↓
Store in Cosmos DB (image_embeddings collection)
    ↓
Redis Cache (for fast retrieval)
```

**RAG Flow (Retrieval-Augmented Generation):**
```
User Query: "Give me turbine sites with workers without hats"
    ↓
Embedding Worker → Generate query embedding
    ↓
Vector Search in Cosmos DB → Find similar images
    ↓
Retrieve relevant images + context
    ↓
Cohere Chat API → Generate natural language response
    ↓
Return results to frontend
```

---

## Data Flows

### 1. Device Telemetry Flow
```
[100,000 IoT Devices]
    ↓ publish (MQTT)
[MQTT Broker] (og/field/{site}/{type}/{id})
    ↓ subscribe
[MQTT Consumer Worker] (backend/workers/mqtt_consumer.py)
    ↓ process + write
[Redis Cache] (current device state)
[Cosmos DB] (historical telemetry)
    ↓ read
[FastAPI /sre/active-devices]
    ↓ HTTP GET
[Next.js Frontend] (SRE Dashboard)
```

### 2. User Activity Flow
```
[User Simulator] (backend/simulators/user_simulator/)
    ↓ publish
[RabbitMQ] (webapp/active_users queue)
    ↓ consume
[User Activity Consumer] (backend/workers/mq_user_consumer.py)
    ↓ process + write
[Redis Cache] (active users, sessions)
[Cosmos DB] (user history)
    ↓ read
[FastAPI /sre/active-users]
    ↓ HTTP GET
[Next.js Frontend] (SRE Dashboard)
```

### 3. Image Intelligence Flow
```
[Site Cameras]
    ↓ upload
[Blob Storage] (site-images container)
    ↓ trigger
[Image Embedding Worker] (backend/workers/image_embeddings.py)
    ↓ call API
[Cohere Embedding API]
    ↓ return embedding
[Cosmos DB] (image_embeddings collection)
[Redis Cache] (cached embeddings)
    ↓ query
[FastAPI /sre/images/search] (vector search)
    ↓ HTTP POST
[Next.js Frontend] (Image Intelligence section)
```

### 4. Failover Simulation Flow
```
[Frontend] User clicks "Simulate Failover"
    ↓ HTTP POST
[FastAPI /sre/failover]
    ↓ update state
[Redis Cache]
    active_region: "az1" → "az2"
    version: "v1.0.0057_region1" → "v1.0.0057_region2"
    failover_time: 0.0023 seconds
    ↓ read
[Frontend] Updates dashboard:
    - Application status: Live → Stopped → Live
    - Active region: AZ1 → AZ2
    - Failover time: 0.0023s
```

---

## High Availability Design

### Zone Redundancy
- **App Service Plan:** Spans Zone 1 and Zone 2
- **Redis Cache:** Premium tier with zone replication
- **Cosmos DB:** Zone-redundant enabled
- **Storage:** ZRS (Zone-Redundant Storage)

### Failover Scenarios

#### Scenario 1: App Service Failure
- **Detection:** Health checks fail (10 seconds)
- **Action:** Traffic routes to healthy instance
- **RTO:** < 30 seconds
- **RPO:** 0 (no data loss, stateless app)

#### Scenario 2: Redis Cache Failure
- **Detection:** Automatic by Azure (5 seconds)
- **Action:** Failover to replica node
- **RTO:** < 10 seconds
- **RPO:** < 1 second (data persisted)

#### Scenario 3: Cosmos DB Failover
- **Detection:** Automatic by Azure
- **Action:** Promote secondary region
- **RTO:** < 5 minutes
- **RPO:** < 1 minute

#### Scenario 4: MQTT/RabbitMQ Failure
- **Detection:** Health check failure
- **Action:** Manual restart or redeploy container
- **RTO:** 2-5 minutes
- **RPO:** Last persisted message

---

## Monitoring & Observability

### Azure Monitor
- Application Insights for App Services
- Container Insights for ACI
- Redis metrics (CPU, memory, connections)
- Cosmos DB metrics (RU consumption, latency)

### Key Metrics
- **Availability:** Uptime percentage
- **Latency:** API response times
- **Throughput:** Requests/second
- **Error Rate:** HTTP 4xx, 5xx errors
- **Resource Usage:** CPU, memory, storage

### Alerts
- App Service down/unhealthy
- Redis cache high memory usage (> 80%)
- Cosmos DB high RU consumption
- Container instance failure

---

## Security

### Authentication & Authorization
- **App Services:** Azure AD integration (optional)
- **Redis:** Connection string with password
- **Cosmos DB:** Primary/secondary keys
- **Storage:** SAS tokens or connection strings

### Network Security
- **HTTPS/TLS:** All App Service traffic
- **NSG Rules:** Restrict traffic to necessary ports
- **Private Endpoints:** Option for Cosmos DB/Redis (not used in this setup)

### Secrets Management
- Environment variables in App Service configuration
- Connection strings stored securely
- No secrets in code or git repository

---

## Cost Optimization

### Production vs. Development

**Production (P1v2 + Premium Redis):**
- High availability with zone redundancy
- Better performance
- ~$200/week

**Development (B1 + Standard Redis):**
- No zone redundancy
- Lower performance limits
- ~$65/week

### Cost-Saving Tips
1. Use B1 App Service Plan for development
2. Use Standard Redis instead of Premium
3. Use Cosmos DB serverless mode
4. Delete resources when not in use
5. Set up budget alerts

---

## Capacity Planning

### Device Telemetry
- **Devices:** 100,000
- **Message Rate:** 5 msg/min/device = 8,333 msg/sec
- **Message Size:** ~500 bytes
- **Throughput:** ~4.2 MB/sec
- **Daily Volume:** ~360 GB/day (compressed)

### User Sessions
- **Concurrent Users:** 3,000-5,000
- **Session Size:** 1-2 KB
- **Cache Memory:** ~10 MB
- **Database:** ~50 MB/day

### Images
- **Daily Images:** 1,000-5,000
- **Image Size:** 2-5 MB (raw)
- **Embedding Size:** 16 KB
- **Storage:** ~10-25 GB/day (images + embeddings)

---

## Deployment Automation

All infrastructure is deployed via:
- **infra/scripts/deploy-infra.sh** - Main deployment
- **infra/scripts/get-config.sh** - Configuration retrieval
- **infra/scripts/cleanup.sh** - Resource cleanup

No manual Azure Portal steps required!

---

**Team OPSC** | CMPE273 SRE Hackathon | November 2025
