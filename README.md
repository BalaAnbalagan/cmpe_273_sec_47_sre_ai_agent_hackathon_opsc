# SRE AI Agent Hackathon - Team OPSC

This project is Team OPSC's submission for the CMPE 273 Section 47 SRE AI Agent Hackathon.

## Project Overview

A Tier-0 Enterprise Reliability Engineering application demonstrating 99.99999% (seven-nines) availability through:
- Real-time IoT telemetry monitoring (100,000 devices across 10 global sites)
- Active user session tracking and analytics
- AI-driven site image intelligence using Cohere embeddings
- Log diagnostics and RAG-based analysis
- Regional failover simulation (< 0.003 seconds)

## Team Members

- **Bala** - Azure Infrastructure & DevOps
- **Varad** - Backend Development (FastAPI)
- **Samip** - Frontend Development (Next.js + shadcn/ui)

## Architecture

### Technology Stack

**Frontend:**
- Next.js 14 (App Router)
- React + TypeScript
- shadcn/ui components
- Tailwind CSS

**Backend:**
- FastAPI (Python 3.11)
- Redis Cache (state management)
- Cosmos DB (MongoDB API)
- MQTT (device telemetry)
- RabbitMQ (user activity)

**Infrastructure:**
- Azure App Services (zone-redundant)
- Azure Cache for Redis Premium
- Azure Cosmos DB (MongoDB API)
- Azure Container Instances (MQTT + RabbitMQ)
- Azure Blob Storage

**AI/ML:**
- Cohere AI (embeddings + RAG)
- Vector search for image intelligence

## Quick Start

### 1. Deploy Infrastructure (Bala)

```bash
cd infra/scripts
./deploy-infra.sh
```

See [infra/README.md](infra/README.md) for detailed instructions.

### 2. Get Configuration

```bash
cd infra/scripts
./get-config.sh
```

This generates a `.env` file with all Azure connection details.

### 3. Local Development

Run infrastructure locally:

```bash
cd infra
docker-compose up -d
```

This starts MQTT, RabbitMQ, Redis, MongoDB, and PostgreSQL on localhost.

## Project Structure

```
cmpe_273_sec_47_sre_ai_agent_hackathon_opsc/
├── infra/                     # Infrastructure (Bala)
│   ├── scripts/               # Deployment scripts
│   ├── docs/                  # Infrastructure documentation
│   ├── docker-compose.yml     # Local development stack
│   └── README.md
│
├── backend/                   # Backend API (Varad)
│   ├── api/                   # FastAPI application
│   ├── simulators/            # Device & user simulators
│   ├── workers/               # MQTT/RabbitMQ consumers
│   └── requirements.txt
│
├── frontend/                  # Frontend UI (Samip)
│   ├── app/                   # Next.js pages
│   ├── components/            # React components
│   └── package.json
│
├── data/                      # Sample data
│   ├── images/                # Site camera images
│   └── logs/                  # System logs
│
└── docs/                      # Documentation
    ├── architecture.md
    └── api-contracts.md
```

## Infrastructure

### Azure Resources

All resources deployed in **West US** with **Availability Zone** redundancy:

- **Resource Group:** rg-cmpe273-sre-hackathon
- **App Services:**
  - `sre-frontend` - Next.js dashboard
  - `sre-backend-az1` - FastAPI (Zone 1)
  - `sre-backend-az2` - FastAPI (Zone 2)
- **Messaging:**
  - MQTT Broker (Container Instance)
  - RabbitMQ Broker (Container Instance)
- **Data:**
  - Redis Premium P1 (6GB, zone-redundant)
  - Cosmos DB (MongoDB API, zone-redundant)
  - Blob Storage (ZRS)

### Cost Estimate

- **Production (HA):** ~$200/week
- **Development:** ~$65/week

### Cleanup

When done:

```bash
cd infra/scripts
./cleanup.sh
```

This deletes all Azure resources.

## Documentation

- [Infrastructure Deployment Guide](infra/docs/DEPLOYMENT_GUIDE.md)
- [Infrastructure Architecture](infra/docs/ARCHITECTURE.md)
- [Infrastructure README](infra/README.md)

## Features

### SRE Dashboard (4 Main Sections)

1. **Deployment Version / Failover**
   - Current deployment version
   - Active region (AZ1 or AZ2)
   - Simulate failover button
   - Failover time measurement

2. **Site Active Users**
   - Number of active users per site
   - Active backend connections
   - User session details
   - Real-time latency metrics

3. **Active Connected Devices**
   - 100,000 IoT devices across 10 sites
   - Device types: Turbines, Thermal Engines, Electrical Rotors
   - Real-time telemetry via MQTT
   - Device health status

4. **Site Image Intelligence**
   - AI-powered image analysis
   - Natural language queries
   - Examples:
     - "Show turbine sites with workers without hard hats"
     - "Find sites with high safety compliance"
   - Word cloud generation
   - Semantic image search

### Device Telemetry

**MQTT Topics:** `og/field/{site_id}/{device_type}/{device_id}`

**Sites (10 global):**
- ND-RAVEN, TX-EAGLE, WY-ALPHA, NM-SAGE, SFO-WEB-01, etc.

**Device Types:**
- turbine
- thermal_engine
- electrical_rotor
- connected_device

**Data Volume:**
- 100,000 devices
- ~8,333 messages/second
- ~4.2 MB/sec throughput

### User Activity

**RabbitMQ Queue:** `webapp/active_users`

**Metrics:**
- Active users count
- Backend connections
- Session timestamps
- Regional distribution

### Image Intelligence

**Cohere AI Integration:**
- Image embeddings (1024-4096 dimensions)
- Vector search
- Semantic queries
- Safety compliance detection

**Storage:**
- Raw images in Azure Blob Storage
- Embeddings in Cosmos DB
- Cache in Redis

## Development Workflow

### Infrastructure Team (Bala)

1. Deploy Azure infrastructure
2. Configure networking and security
3. Set up monitoring and alerts
4. Provide `.env` configuration to team

### Backend Team (Varad)

1. Build FastAPI application
2. Implement device simulators
3. Create MQTT/RabbitMQ consumers
4. Integrate with Redis and Cosmos DB
5. Deploy to Azure App Services

### Frontend Team (Samip)

1. Build Next.js dashboard
2. Implement shadcn/ui components
3. Connect to FastAPI backend
4. Display real-time metrics
5. Deploy to Azure App Service

## Environment Variables

Required environment variables (auto-generated by `get-config.sh`):

```bash
# Application URLs
FRONTEND_URL=https://sre-frontend.azurewebsites.net
BACKEND_AZ1_URL=https://sre-backend-az1.azurewebsites.net
BACKEND_AZ2_URL=https://sre-backend-az2.azurewebsites.net

# MQTT
MQTT_HOST=<ip>
MQTT_PORT=1883

# RabbitMQ
RABBITMQ_HOST=<ip>
RABBITMQ_PORT=5672

# Redis
REDIS_HOST=redis-sre-ha.redis.cache.windows.net
REDIS_PORT=6380
REDIS_PASSWORD=<key>

# Cosmos DB
COSMOS_MONGODB_URI=mongodb://...

# Cohere AI (add your key)
COHERE_API_KEY=your-key-here
```

## License

Academic project for CMPE 273 - San José State University

## Acknowledgments

- Professor Chandrasekar Vuppalapati
- CMPE 273 Enterprise Distributed Systems
- San José State University
