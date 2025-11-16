# Frontend Quick Start Guide

## LOCAL DEVELOPMENT (Fastest - Use this for Demo!)

### Option 1: Run Locally (RECOMMENDED for Demo)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

**Why this works best:**
- Zero deployment issues
- Works immediately
- Full control during demo
- Can show live code editing

---

## DEPLOYMENT OPTIONS

### Option A: Vercel (FREE, 2 minutes, 99.99% reliable)

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Login to Vercel:**
```bash
vercel login
```

3. **Deploy from frontend directory:**
```bash
cd frontend
vercel
```

4. **Follow prompts:**
- Set up and deploy? **Y**
- Which scope? **Your account**
- Link to existing project? **N**
- Project name? **sre-opsc-hackathon**
- Directory? **./  (current directory)**
- Override settings? **N**

5. **Production deployment:**
```bash
vercel --prod
```

**Environment Variables (when prompted):**
- `NEXT_PUBLIC_API_URL_AZ1`: https://sre-backend-az1.azurewebsites.net
- `NEXT_PUBLIC_API_URL_AZ2`: https://sre-backend-az2.azurewebsites.net

**Result:** Frontend deployed to https://sre-opsc-hackathon.vercel.app (or similar)

**Cost:** $0 (FREE tier)

---

### Option B: Azure Static Web Apps (Alternative)

```bash
# Create static web app
az staticwebapp create \
  --name sre-frontend-static \
  --resource-group rg-cmpe273-sre-hackathon \
  --source https://github.com/BalaAnbalagan/cmpe_273_sec_47_sre_ai_agent_hackathon_opsc \
  --branch main \
  --app-location "/frontend" \
  --output-location ".next" \
  --location "westus2"
```

---

## DEMO PREPARATION

### Before Demo (Choose ONE):

**RECOMMENDED: Local Development**
```bash
cd frontend
npm install
npm run dev
# Frontend at http://localhost:3000
```

**OR: Vercel Deployment**
```bash
cd frontend
vercel --prod
# Frontend at https://your-app.vercel.app
```

### During Demo

1. **Show Dashboard:**
   - System status (both AZ1 & AZ2)
   - Zone switcher
   - Service health checks
   - Real-time monitoring

2. **Test Backend Connectivity:**
   - Click "Check AZ1" button
   - Click "Check AZ2" button
   - Show automatic failover

3. **Live Features:**
   - Cohere AI status
   - Redis connection
   - Cosmos DB status
   - MQTT/RabbitMQ brokers

---

## Frontend Architecture

- **Framework:** Next.js 16 + TypeScript
- **Styling:** Tailwind CSS v4
- **API Client:** [lib/api.ts](lib/api.ts) with automatic failover
- **Features:**
  - Multi-zone health monitoring
  - <3ms zone switching
  - Real-time status updates
  - Enterprise-grade UI

---

## Troubleshooting

### "Failed to fetch backend"
**Solution:** Backend CORS not deployed yet. Deploy backend with CORS:

```bash
cd backend/api
# Verify main.py has CORS middleware
grep -A 10 "CORSMiddleware" main.py

# If missing, backend needs CORS update
```

### "npm install fails"
**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install
```

### "Build fails"
**Solution:**
```bash
# Check Node version (needs 20+)
node --version

# Update Node if needed
nvm install 20
nvm use 20
```

---

## Backend Endpoints Used

```
GET  /sre/status                    # System status
GET  /sre/deployment-version        # Deployment info
GET  /sre/images/cohere-status      # Cohere availability
POST /sre/images/search-nl          # Natural language search
POST /sre/images/safety-analysis    # Safety analysis
POST /sre/images/chat               # RAG chat
POST /sre/top-ips                   # Log analysis
```

---

## For Varad

**To continue development:**

1. **Pull latest code:**
```bash
git checkout main
git pull origin main
```

2. **Install dependencies:**
```bash
cd frontend
npm install
```

3. **Run locally:**
```bash
npm run dev
```

4. **Deploy to Vercel (when ready):**
```bash
vercel --prod
```

**Files to review:**
- [app/page.tsx](app/page.tsx) - Main dashboard
- [lib/api.ts](lib/api.ts) - Backend API client
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Full deployment docs

---

**Last Updated:** November 16, 2025 (Demo Day!)
