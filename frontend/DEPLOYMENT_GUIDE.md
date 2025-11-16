# Frontend Deployment Guide

## Azure App Service Deployment (Recommended)

### Prerequisites
- Azure CLI installed and logged in
- Resource group: `rg-cmpe273-sre-hackathon`
- App Service Plan: `asp-sre-ha` (already exists)

### Step 1: Create Frontend App Service

```bash
# Create the web app for frontend
az webapp create \
  --name sre-frontend \
  --resource-group rg-cmpe273-sre-hackathon \
  --plan asp-sre-ha \
  --runtime "NODE:20-lts"
```

**Frontend URL:** https://sre-frontend.azurewebsites.net

### Step 2: Configure App Settings

```bash
# Set Node.js version and environment variables
az webapp config appsettings set \
  --name sre-frontend \
  --resource-group rg-cmpe273-sre-hackathon \
  --settings \
    WEBSITE_NODE_DEFAULT_VERSION="20-lts" \
    NEXT_PUBLIC_API_URL_AZ1="https://sre-backend-az1.azurewebsites.net" \
    NEXT_PUBLIC_API_URL_AZ2="https://sre-backend-az2.azurewebsites.net" \
    NODE_ENV="production"
```

### Step 3: Build and Deploy

```bash
# From frontend directory
cd frontend

# Install dependencies
npm install

# Build the app
npm run build

# Create deployment package
zip -r frontend-deploy.zip .next package.json package-lock.json next.config.ts public node_modules

# Deploy to Azure
az webapp deploy \
  --name sre-frontend \
  --resource-group rg-cmpe273-sre-hackathon \
  --src-path frontend-deploy.zip \
  --type zip \
  --async false
```

### Step 4: Configure Startup Command

```bash
# Set the startup command
az webapp config set \
  --name sre-frontend \
  --resource-group rg-cmpe273-sre-hackathon \
  --startup-file "node_modules/.bin/next start"
```

### Step 5: Verify Deployment

```bash
# Check app status
az webapp show \
  --name sre-frontend \
  --resource-group rg-cmpe273-sre-hackathon \
  --query state

# View logs
az webapp log tail \
  --name sre-frontend \
  --resource-group rg-cmpe273-sre-hackathon
```

**Test:** https://sre-frontend.azurewebsites.net

---

## Alternative: Vercel Deployment (FREE & Faster)

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Login to Vercel

```bash
vercel login
```

### Step 3: Deploy

```bash
cd frontend

# First deployment (interactive)
vercel

# Production deployment
vercel --prod
```

### Step 4: Set Environment Variables

In Vercel Dashboard or CLI:

```bash
vercel env add NEXT_PUBLIC_API_URL_AZ1
# Enter: https://sre-backend-az1.azurewebsites.net

vercel env add NEXT_PUBLIC_API_URL_AZ2
# Enter: https://sre-backend-az2.azurewebsites.net
```

**Vercel URL:** Automatically generated (e.g., sre-dashboard.vercel.app)

---

## Backend CORS Configuration

The backend already has CORS enabled for:
- `http://localhost:3000` (local development)
- `https://*.azurewebsites.net` (Azure deployments)
- `https://*.vercel.app` (Vercel deployments)

No backend changes needed!

---

## Local Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

**Open:** http://localhost:3000

---

## Testing Backend Connectivity

Once deployed, test the connection:

```bash
# From browser console or terminal
curl https://sre-frontend.azurewebsites.net

# Check API connectivity
curl https://sre-backend-az1.azurewebsites.net/sre/status
curl https://sre-backend-az2.azurewebsites.net/sre/status
```

---

## Troubleshooting

### Frontend not starting?

```bash
# Check logs
az webapp log tail --name sre-frontend --resource-group rg-cmpe273-sre-hackathon

# Restart app
az webapp restart --name sre-frontend --resource-group rg-cmpe273-sre-hackathon
```

### CORS errors?

Backend already configured with wildcard support for:
- Local: `http://localhost:3000`
- Azure: `https://*.azurewebsites.net`
- Vercel: `https://*.vercel.app`

### Build failures?

```bash
# Clear cache and rebuild
rm -rf .next node_modules
npm install
npm run build
```

---

## Cost Breakdown

### Azure App Service
- Uses existing `asp-sre-ha` plan (B1)
- **Additional Cost:** $0 (already paying for plan)

### Vercel
- **Cost:** FREE for hobby projects
- Unlimited bandwidth
- Global CDN
- Automatic SSL

**Recommendation:** Use Vercel for free hosting with better performance!

---

## Quick Commands Reference

```bash
# Azure deployment
az webapp create --name sre-frontend --resource-group rg-cmpe273-sre-hackathon --plan asp-sre-ha --runtime "NODE:20-lts"
cd frontend && npm run build && zip -r frontend-deploy.zip .next package.json package-lock.json next.config.ts public node_modules
az webapp deploy --name sre-frontend --resource-group rg-cmpe273-sre-hackathon --src-path frontend-deploy.zip --type zip

# Vercel deployment
cd frontend && vercel --prod
```

---

**Ready to Deploy!** 🚀
