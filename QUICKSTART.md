# Quick Start Guide - Infrastructure Deployment
## CMPE273 SRE Hackathon - Team OPSC

---

## For Bala (Infrastructure Team)

### Step 1: Login to Azure

```bash
az login
```

### Step 2: Deploy Infrastructure

```bash
cd infra/scripts
./deploy-infra.sh
```

**Time:** 20-30 minutes
**What it does:**
- Creates resource group in West US
- Deploys virtual network with 3 subnets
- Creates 3 App Services (frontend + 2 backends)
- Deploys MQTT and RabbitMQ brokers
- Creates Redis Cache (Premium, zone-redundant) - **takes 15-20 min**
- Creates Cosmos DB (MongoDB API) - **takes 5-10 min**
- Creates Storage Account

### Step 3: Get Configuration

```bash
./get-config.sh
```

**What it does:**
- Retrieves all public URLs
- Gets connection strings and keys
- **Generates `.env` file at project root**
- Displays all configuration

### Step 4: Share with Team

1. Copy the generated `.env` file
2. Share with Varad (backend) and Samip (frontend)
3. Share the public URLs:
   - Frontend: `https://sre-frontend.azurewebsites.net`
   - Backend AZ1: `https://sre-backend-az1.azurewebsites.net`
   - Backend AZ2: `https://sre-backend-az2.azurewebsites.net`

---

## For Varad & Samip (Development Team)

### Local Development (Before Azure)

Start local infrastructure:

```bash
cd infra
docker-compose up -d
```

This gives you:
- MQTT on `localhost:1883`
- RabbitMQ on `localhost:5672` (UI: `localhost:15672`)
- Redis on `localhost:6379`
- MongoDB on `localhost:27017`
- PostgreSQL on `localhost:5432`

**Credentials:**
- RabbitMQ: admin / hackathon2024
- MongoDB: admin / hackathon2024
- Redis: password = hackathon2024

### After Infrastructure is Deployed

1. Get the `.env` file from Bala
2. Copy it to your `backend/` and `frontend/` directories
3. Update `COHERE_API_KEY` with your actual key
4. Start developing!

---

## When You're Done

### Cleanup All Resources

```bash
cd infra/scripts
./cleanup.sh
```

**WARNING:** This deletes everything! Only run when hackathon is over.

---

## Cost Monitoring

### Check Current Costs

```bash
az consumption usage list --output table
```

### Set Budget Alert

```bash
az consumption budget create \
  --resource-group rg-cmpe273-sre-hackathon \
  --budget-name hackathon-budget \
  --amount 300 \
  --time-grain Monthly
```

---

## Troubleshooting

### Check Resource Status

```bash
az resource list --resource-group rg-cmpe273-sre-hackathon --output table
```

### View Container Logs

```bash
# MQTT logs
az container logs --resource-group rg-cmpe273-sre-hackathon --name mqtt-broker

# RabbitMQ logs
az container logs --resource-group rg-cmpe273-sre-hackathon --name rabbitmq-broker
```

### Check App Service Status

```bash
az webapp list --resource-group rg-cmpe273-sre-hackathon --output table
```

### View App Service Logs

```bash
az webapp log tail --name sre-backend-az1 --resource-group rg-cmpe273-sre-hackathon
```

---

## Important URLs

Once deployed, these will be your main endpoints:

- **Frontend:** https://sre-frontend.azurewebsites.net
- **Backend AZ1:** https://sre-backend-az1.azurewebsites.net
- **Backend AZ2:** https://sre-backend-az2.azurewebsites.net
- **RabbitMQ UI:** http://`<public-ip>`:15672
- **MQTT:** `<public-ip>`:1883

---

## Next Steps

1. ✅ Deploy infrastructure
2. ✅ Get configuration
3. ⬜ Varad: Build FastAPI backend
4. ⬜ Samip: Build Next.js frontend
5. ⬜ Deploy code to App Services
6. ⬜ Test end-to-end
7. ⬜ Demo!
8. ⬜ Cleanup resources

---

**Team OPSC** | CMPE273 SRE Hackathon | November 2025
