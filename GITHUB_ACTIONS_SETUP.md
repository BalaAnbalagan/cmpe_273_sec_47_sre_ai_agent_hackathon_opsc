# GitHub Actions Deployment Setup

## Frontend Deployment to Azure via GitHub Actions

The GitHub Actions workflow is already configured at [.github/workflows/azure-frontend-deploy.yml](.github/workflows/azure-frontend-deploy.yml).

**Status:** Ready to use, just needs one secret!

---

## Quick Setup (2 Steps)

### Step 1: Get the Publish Profile

Run this command to get the Azure publish profile:

```bash
az webapp deployment list-publishing-profiles \
  --name sre-frontend \
  --resource-group rg-cmpe273-sre-hackathon \
  --xml
```

**Copy the entire XML output** (from `<publishData>` to `</publishData>`)

---

### Step 2: Add GitHub Secret

1. Go to your GitHub repository:
   https://github.com/BalaAnbalagan/cmpe_273_sec_47_sre_ai_agent_hackathon_opsc/settings/secrets/actions

2. Click **"New repository secret"**

3. Name: `AZURE_FRONTEND_PUBLISH_PROFILE`

4. Value: **Paste the XML from Step 1**

5. Click **"Add secret"**

---

## How It Works

The workflow automatically deploys when:
- You push to `main` branch
- Files in `frontend/` directory change
- Or you manually trigger it from GitHub Actions tab

**Workflow Steps:**
1. ✅ Checkout code
2. ✅ Set up Node.js 20
3. ✅ Install dependencies (`npm ci`)
4. ✅ Build Next.js app (`npm run build`)
   - Uses standalone output mode
   - Sets environment variables for AZ1/AZ2 backend URLs
5. ✅ Deploy to Azure App Service (sre-frontend)
   - Uses publish profile for authentication
   - Deploys `.next/standalone` folder

---

## Manual Trigger (If Needed)

If you want to deploy without pushing changes:

1. Go to: https://github.com/BalaAnbalagan/cmpe_273_sec_47_sre_ai_agent_hackathon_opsc/actions/workflows/azure-frontend-deploy.yml

2. Click **"Run workflow"**

3. Select `main` branch

4. Click **"Run workflow"** button

---

## Frontend URL

Once deployed: **https://sre-frontend.azurewebsites.net**

---

## Current Infrastructure

**Azure App Service:**
- Name: `sre-frontend`
- Resource Group: `rg-cmpe273-sre-hackathon`
- Tier: PremiumV2 P1v2
- Runtime: Node.js 20 LTS
- Region: West US 2

**Environment Variables (already configured):**
- `WEBSITE_NODE_DEFAULT_VERSION`: 20-lts
- `NEXT_PUBLIC_API_URL_AZ1`: https://sre-backend-az1.azurewebsites.net
- `NEXT_PUBLIC_API_URL_AZ2`: https://sre-backend-az2.azurewebsites.net
- `NODE_ENV`: production
- `SCM_DO_BUILD_DURING_DEPLOYMENT`: true

---

## Testing the Deployment

After the GitHub Action completes:

1. **Check deployment status:**
   - GitHub Actions tab will show green checkmark ✅

2. **Visit frontend:**
   - URL: https://sre-frontend.azurewebsites.net
   - Should see login page or dashboard

3. **Test backend connectivity:**
   - Frontend should connect to both AZ1 and AZ2 backends
   - CORS is already enabled on backends

---

## Troubleshooting

### If workflow fails:

1. **Check the logs:**
   - Go to Actions tab → Click on failed run → Click on job → Expand steps

2. **Common issues:**
   - Secret not added: Add `AZURE_FRONTEND_PUBLISH_PROFILE`
   - Build fails: Check `npm run build` works locally
   - Deployment fails: Verify app service exists

### If deployed but not working:

1. **Check Azure logs:**
   ```bash
   az webapp log tail --name sre-frontend --resource-group rg-cmpe273-sre-hackathon
   ```

2. **Restart app service:**
   ```bash
   az webapp restart --name sre-frontend --resource-group rg-cmpe273-sre-hackathon
   ```

3. **Check app service status:**
   ```bash
   az webapp show --name sre-frontend --resource-group rg-cmpe273-sre-hackathon --query "state"
   ```

---

## Alternative: Manual Deployment (Backup Method)

If GitHub Actions doesn't work, you can deploy manually:

```bash
# Build locally
cd frontend
npm run build

# Create deployment package
cd .next/standalone
zip -r ../../../frontend-deploy.zip .

# Deploy to Azure
cd ../../..
az webapp deploy \
  --name sre-frontend \
  --resource-group rg-cmpe273-sre-hackathon \
  --src-path frontend-deploy.zip \
  --type zip
```

---

## Summary

✅ **What's Ready:**
- GitHub Actions workflow configured
- Azure App Service created (sre-frontend)
- Next.js standalone build configured
- Environment variables set
- CORS enabled on backends

🔧 **What You Need to Do:**
1. Get publish profile (Step 1 above)
2. Add as GitHub secret (Step 2 above)
3. Push to main or manually trigger workflow

⏱️ **Time:** 2 minutes to set up secret, 3-5 minutes for deployment

🎯 **Result:** Frontend automatically deploys to https://sre-frontend.azurewebsites.net

---

**Team OPSC - Demo Ready!** 🚀
