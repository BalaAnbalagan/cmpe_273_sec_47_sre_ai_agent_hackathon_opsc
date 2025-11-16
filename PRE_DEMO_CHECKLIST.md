# Pre-Demo Checklist - 5 PM Today

## ✅ Infrastructure Status

### Azure Backend Services
```bash
# Check AZ1
curl https://sre-backend-az1.azurewebsites.net/sre/status

# Check AZ2
curl https://sre-backend-az2.azurewebsites.net/sre/status
```

**Expected:** Both return HTTP 200 with deployment info

### Message Brokers
```bash
# Test MQTT connectivity
nc -zv opsc-mqtt-sjsu.westus2.azurecontainer.io 1883

# Test RabbitMQ connectivity
nc -zv opsc-rabbitmq-sjsu.westus2.azurecontainer.io 5672
```

**Expected:** Connection succeeded

---

## 🚀 Demo Setup (15 min before presentation)

### Terminal 1 - MQTT Simulator
```bash
cd ~/Projects/cmpe_273_sec_47_\ sre_ai_agent_hackathon_opsc/simulators
python mqtt_device_simulator.py
```

**Expected Output:**
```
🚀 MQTT Device Simulator Starting...
   Broker: opsc-mqtt-sjsu.westus2.azurecontainer.io:1883
   Devices: 100,000
   Sites: 10
```

### Terminal 2 - RabbitMQ Simulator
```bash
cd ~/Projects/cmpe_273_sec_47_\ sre_ai_agent_hackathon_opsc/simulators
python rabbitmq_user_simulator.py
```

**Expected Output:**
```
🐰 RabbitMQ User Activity Simulator
   Broker: opsc-rabbitmq-sjsu.westus2.azurecontainer.io:5672
   Max concurrent users: 5,000
```

### Terminal 3 - Frontend Dashboard
```bash
cd ~/Projects/cmpe_273_sec_47_\ sre_ai_agent_hackathon_opsc/frontend
npm run dev
```

**Open:** http://localhost:3000

**Expected:** Dashboard loads with real-time status from both AZ1 and AZ2

### Terminal 4 - Demo Script Ready
```bash
cd ~/Projects/cmpe_273_sec_47_\ sre_ai_agent_hackathon_opsc/scripts
python demo_queries.py
```

**DO NOT RUN YET** - Wait for professor to request AI demos

---

## 📋 Demo Flow (15 minutes)

### 1. Infrastructure Tour (2 min)

**Browser:** Azure Portal
- Show resource group: `rg-cmpe273-sre-hackathon`
- Point out all 12 resources running

**Terminal:**
```bash
curl https://sre-backend-az1.azurewebsites.net/sre/deployment-version
curl https://sre-backend-az2.azurewebsites.net/sre/deployment-version
```

**Talk Track:**
- "We have multi-zone deployment with AZ1 and AZ2 for high availability"
- "All 12 Azure resources operational"
- "Targeting 99.99999% availability (Tier-0)"

### 2. Frontend Dashboard (3 min)

**Browser:** http://localhost:3000

**Demonstrate:**
- Real-time status from both availability zones
- Zone switcher (show <3ms failover)
- Azure services monitoring (Redis, Cosmos DB, Key Vault)
- Cohere AI integration status
- Live uptime counter

**Talk Track:**
- "Enterprise-grade monitoring dashboard"
- "Real-time health checks from both zones"
- "Professional UI with Tailwind CSS v4"

### 3. Run Simulators (3 min)

**Show Terminal 1:**
- MQTT simulator running
- 100,000 devices publishing telemetry
- 10 global sites
- Realistic metrics (temperature, RPM, voltage, etc.)

**Talk Track:**
- "Simulating 100,000 IoT devices across 10 global sites"
- "MQTT topic convention: og/field/{site_id}/{device_type}/{device_id}"
- "4 device types: turbines, thermal engines, electrical rotors, connected devices"

**Show Terminal 2:**
- RabbitMQ user activity
- Active user sessions
- Real-time metrics

**Talk Track:**
- "Up to 5,000 concurrent users tracked via RabbitMQ"
- "User sessions with login/logout events"
- "Activity simulation for dashboard views, reports, diagnostics"

### 4. Cohere AI Demonstrations (5 min)

**Run in Terminal 4:**
```bash
python demo_queries.py
```

**Highlights:**

1. **System Status** - Both backends online
2. **Natural Language Search:**
   - "turbine sites with workers without hard hats"
   - "sites with high safety compliance"
   - "engineer with hard hat and tablet"

3. **Safety Analysis:**
   - Overall safety score
   - Violation findings
   - Recommendations

4. **RAG Chat:**
   - "What safety violations do you see across our sites?"
   - Context-aware responses

5. **Log Analysis:**
   - Top IPs generating Error 400
   - Device diagnostics

**Talk Track:**
- "Cohere AI enables natural language search - no SQL needed"
- "RAG (Retrieval-Augmented Generation) provides context-aware responses"
- "Vector embeddings for semantic similarity search"

### 5. Architecture Explanation (2 min)

**Show:** README.md architecture diagram

**Talk Through:**
```
Users/Devices → Frontend (Next.js)
                    ↓
           Backend AZ1 / AZ2 (FastAPI)
                    ↓
      MQTT + RabbitMQ + Redis + Cosmos DB
                    ↓
              Cohere AI (RAG)
```

**Talk Track:**
- "Multi-zone redundancy for high availability"
- "Message-driven architecture for scalability"
- "Security-first: Azure Key Vault + User Managed Identity"
- "Cost-optimized at ~$62/week"

---

## 🎯 Key Talking Points

1. **Production-Ready Architecture**
   - "We built a Tier-0 system targeting 99.99999% availability"
   - "Multi-zone deployment for redundancy"
   - "Fully operational and deployed to Azure"

2. **Scale**
   - "100,000 IoT devices across 10 global sites"
   - "Up to 5,000 concurrent users"
   - "Real-time telemetry and session tracking"

3. **AI Innovation**
   - "Cohere embeddings for natural language search"
   - "RAG enables context-aware Q&A"
   - "Safety compliance analysis with AI"

4. **Security**
   - "Zero hardcoded secrets - all in Azure Key Vault"
   - "User Managed Identity for passwordless authentication"
   - "Production-grade security practices"

5. **Practical SRE**
   - "Real-time monitoring and alerting"
   - "Log analysis and diagnostics"
   - "Message-driven architecture"

---

## ⚠️ Troubleshooting

### Backend not responding?
```bash
az webapp restart --name sre-backend-az1 --resource-group rg-cmpe273-sre-hackathon
az webapp restart --name sre-backend-az2 --resource-group rg-cmpe273-sre-hackathon
```

### Simulators can't connect?
Check environment variables:
```bash
cat .env | grep MQTT
cat .env | grep RABBITMQ
```

### Frontend not loading?
```bash
cd frontend
rm -rf .next
npm run build
npm run dev
```

### Cohere API errors?
Check Key Vault:
```bash
az keyvault secret show --vault-name kv-opsc-sre-74668 --name CohereAPIKey
```

---

## 📊 Expected Demo Outcome

**Professor will see:**
- ✅ All architecture requirements met
- ✅ 100,000 device simulation running
- ✅ User activity tracking operational
- ✅ Natural language queries working
- ✅ Professional frontend dashboard
- ✅ Multi-zone high availability
- ✅ Security-first implementation

**Questions to Anticipate:**
1. "How do you handle failover between zones?" → Show zone switcher
2. "What's the cost of running this?" → ~$62/week
3. "How does RAG work?" → Explain Cohere embeddings + vector search
4. "Is this production-ready?" → Yes, fully deployed and operational
5. "How do you secure secrets?" → Azure Key Vault + UMI

---

## ✅ Final Checks (5 min before demo)

- [ ] Both backends returning HTTP 200
- [ ] MQTT simulator publishing (Terminal 1)
- [ ] RabbitMQ simulator active (Terminal 2)
- [ ] Frontend dashboard loaded (Browser)
- [ ] Demo script ready in Terminal 4
- [ ] Azure Portal open to resource group
- [ ] README.md architecture diagram visible
- [ ] Team members ready (Bala, Varad, Samip)

---

**Ready? Let's go! 🚀**

**Demo Time:** 5:00 PM
**Duration:** 15 minutes
**Team OPSC:** Bala Anbalagan, Varad Poddar, Samip Niraula
