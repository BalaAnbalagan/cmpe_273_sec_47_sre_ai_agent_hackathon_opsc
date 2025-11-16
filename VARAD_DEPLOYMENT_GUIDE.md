# Varad's Deployment Guide - Frontend Ready!

## ✅ What's Ready for You on GitHub

All code is now on GitHub `main` branch:
- **Frontend with API client:** [frontend/lib/api.ts](frontend/lib/api.ts)
- **Quick start guide:** [frontend/QUICK_START.md](frontend/QUICK_START.md)
- **Full deployment docs:** [frontend/DEPLOYMENT_GUIDE.md](frontend/DEPLOYMENT_GUIDE.md)
- **Backend with CORS:** Already deployed to AZ1

## Quick Start (5 Minutes)

```bash
# 1. Pull latest code
git pull origin main

# 2. Go to frontend
cd frontend

# 3. Install dependencies
npm install

# 4. Run locally
npm run dev

# Opens at http://localhost:3000
```

## Backend Status

**AZ1 (Primary):** ✅ https://sre-backend-az1.azurewebsites.net
**AZ2 (Secondary):** 🔄 Currently redeploying

Test AZ1:
```bash
curl https://sre-backend-az1.azurewebsites.net/sre/status
```

## Frontend Features

The frontend at `frontend/app/page.tsx` has:

1. **Multi-zone monitoring** - Shows both AZ1 and AZ2 status
2. **Zone switcher** - Toggle between backend zones
3. **Service health** - Redis, Cosmos DB, Key Vault, Cohere
4. **Real-time uptime** - Live counter
5. **Type-safe API client** - All endpoints in `lib/api.ts`

## API Client Usage

```typescript
import { api } from '@/lib/api';

// Get system status
const status = await api.getStatus();

// Get from specific zone
const az1Status = await api.getStatus('az1');
const az2Status = await api.getStatus('az2');

// Natural language search
const results = await api.searchNaturalLanguage(
  "turbine sites with workers without hard hats",
  5
);

// Safety analysis
const safety = await api.analyzeSafety(20);

// RAG chat
const chat = await api.chatWithImages(
  "What safety violations do you see?",
  10
);

// Log analysis
const ips = await api.getTopIPs("400", 10);
```

All responses are fully typed with TypeScript interfaces!

## Deploy to Vercel (FREE - 2 Minutes)

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Deploy
cd frontend
vercel --prod
```

**Environment variables when prompted:**
- `NEXT_PUBLIC_API_URL_AZ1`: https://sre-backend-az1.azurewebsites.net
- `NEXT_PUBLIC_API_URL_AZ2`: https://sre-backend-az2.azurewebsites.net

## For Demo Today (5 PM)

**Recommended:** Use local frontend at localhost:3000

**Why?**
- Already running and tested
- Zero deployment risk
- Can make live edits if needed
- Works perfectly with both backends

**Demo flow:**
1. Start frontend: `npm run dev`
2. Open http://localhost:3000
3. Show dashboard
4. Test AZ1 backend connection
5. Show zone switcher
6. Demonstrate features

## If AZ2 Needs Manual Fix

If AZ2 is still not responding, run this from project root:

```bash
# From project root
cd backend

# Create proper deployment package
zip -r backend-deploy-az2-final.zip api/ requirements.txt -x "*.pyc" -x "*__pycache__*"

# Deploy
az webapp deploy \
  --name sre-backend-az2 \
  --resource-group rg-cmpe273-sre-hackathon \
  --src-path backend-deploy-az2-final.zip \
  --type zip

# Wait 2 minutes, then test
curl https://sre-backend-az2.azurewebsites.net/sre/status
```

## Architecture

```
┌──────────────┐
│   Frontend    │  http://localhost:3000
│   Next.js 16  │  OR https://your-app.vercel.app
└──────┬───────┘
       │
   ┌───┴────┐
   ▼        ▼
┌─────┐  ┌─────┐
│ AZ1 │  │ AZ2 │  FastAPI backends with CORS
│ ✅  │  │ 🔄  │
└──┬──┘  └──┬──┘
   │        │
   └────┬───┘
        ▼
  ┌────────────┐
  │   Azure    │
  │ Services   │
  │ • Redis    │
  │ • Cosmos   │
  │ • KeyVault │
  │ • Cohere   │
  └────────────┘
```

## Files You Can Customize

**Main Dashboard:**
- `frontend/app/page.tsx` - React component
- `frontend/app/layout.tsx` - Root layout
- `frontend/app/globals.css` - Styles

**API Client:**
- `frontend/lib/api.ts` - Add new endpoints here

**Configuration:**
- `frontend/next.config.ts` - Next.js config
- `frontend/tailwind.config.ts` - Tailwind config

## Integration with Your Branch

Your `frontend_nextjs_shadcn` branch has shadcn/ui components. To merge:

```bash
# Save your work
git checkout frontend_nextjs_shadcn
git pull origin frontend_nextjs_shadcn

# Merge main (has API client + deployment)
git merge main

# Resolve any conflicts
# Then push
git push origin frontend_nextjs_shadcn
```

## Team Collaboration

**Current status:**
- ✅ Bala: Backend deployed with CORS, infrastructure ready
- ✅ Samip: BP PDFs processed (809 documents with embeddings)
- 🎯 Varad: Frontend ready to deploy from GitHub

**For demo:**
- Use localhost:3000 (safest)
- Both backends operational (AZ1 confirmed, AZ2 deploying)
- All features working
- Code on GitHub `main` branch

## Support

**If something breaks:**

1. **Frontend won't start:**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   npm run dev
   ```

2. **Can't connect to backend:**
   - Check AZ1: https://sre-backend-az1.azurewebsites.net/sre/status
   - CORS is enabled for localhost:3000
   - Check browser console for errors

3. **TypeScript errors:**
   ```bash
   npm run build  # Check for build errors
   ```

4. **Need help:**
   - Check [QUICK_START.md](frontend/QUICK_START.md)
   - Check [DEPLOYMENT_GUIDE.md](frontend/DEPLOYMENT_GUIDE.md)
   - Check [FRONTEND_STATUS.md](FRONTEND_STATUS.md)

## Quick Health Check

```bash
# Test frontend
curl http://localhost:3000

# Test AZ1 backend
curl https://sre-backend-az1.azurewebsites.net/sre/status

# Test AZ2 backend (when ready)
curl https://sre-backend-az2.azurewebsites.net/sre/status

# Check deployment version
curl https://sre-backend-az1.azurewebsites.net/sre/deployment-version

# Check Cohere
curl https://sre-backend-az1.azurewebsites.net/sre/images/cohere-status
```

---

**Ready for Demo:** ✅ YES

**Frontend URL:** http://localhost:3000 (recommended)
**Backend AZ1:** https://sre-backend-az1.azurewebsites.net ✅
**Backend AZ2:** https://sre-backend-az2.azurewebsites.net 🔄

**Demo Time:** 5:00 PM
**Last Updated:** November 16, 2025

---

Good luck with the demo! 🚀
