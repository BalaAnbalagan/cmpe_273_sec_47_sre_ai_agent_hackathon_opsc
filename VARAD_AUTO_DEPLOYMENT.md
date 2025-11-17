# Auto-Deployment Guide for Varad

**Last Updated:** November 17, 2025

---

## ✅ Auto-Deployment is ACTIVE!

Every commit pushed to the `main` branch will automatically deploy the frontend to Azure.

---

## 🚀 How It Works

When you push changes to `main`:

1. **GitHub Actions automatically triggers** ([.github/workflows/azure-frontend-deploy.yml](.github/workflows/azure-frontend-deploy.yml))
2. **Builds your Next.js app** with production optimizations
3. **Packages the deployment** (standalone build + static files)
4. **Deploys to Azure** at https://sre-frontend.azurewebsites.net
5. **Restarts the app** to apply changes

**Typical deployment time:** 1-2 minutes

---

## 📝 Your Workflow (Simple!)

```bash
# 1. Make your changes
# Edit files in frontend/ directory

# 2. Test locally
cd frontend
npm run dev
# Visit http://localhost:3000 (or 3001 if 3000 is busy)

# 3. Commit and push
git add .
git commit -m "Your commit message"
git push origin main

# 4. Wait for deployment (1-2 minutes)
# GitHub Actions handles everything automatically!

# 5. Verify deployment
# Visit https://sre-frontend.azurewebsites.net
```

---

## 🔍 Monitoring Deployments

### View Deployment Status

**Option 1: GitHub Website**
- Go to: https://github.com/BalaAnbalagan/cmpe_273_sec_47_sre_ai_agent_hackathon_opsc/actions
- Look for the latest "Deploy Frontend to Azure" workflow
- ✅ Green checkmark = Success
- ❌ Red X = Failed (check logs)

**Option 2: Command Line** (if you have `gh` CLI)
```bash
# View latest runs
gh run list --workflow=azure-frontend-deploy.yml

# View details of specific run
gh run view <run-id>

# Watch a run in real-time
gh run watch
```

---

## 🛠️ What Gets Deployed

The workflow deploys:
- ✅ All your React/Next.js components
- ✅ Static assets (CSS, images, fonts)
- ✅ Public files
- ✅ Server-side code (API routes, middleware)
- ✅ Environment variables (backend URLs)

**Environment Variables (Pre-configured):**
- `NEXT_PUBLIC_API_URL_AZ1`: https://sre-backend-az1.azurewebsites.net
- `NEXT_PUBLIC_API_URL_AZ2`: https://sre-backend-az2.azurewebsites.net

---

## ⚠️ Common Issues & Solutions

### Issue 1: Deployment Failed

**Check the logs:**
1. Go to https://github.com/BalaAnbalagan/cmpe_273_sec_47_sre_ai_agent_hackathon_opsc/actions
2. Click on the failed run
3. Click on "build-and-deploy" job
4. Review the error message

**Common causes:**
- Build errors (TypeScript, ESLint)
- Missing dependencies
- Syntax errors

**Fix:** Fix the error in your code, commit, and push again.

---

### Issue 2: Build Works Locally But Fails in GitHub Actions

**Cause:** Different dependencies or environment

**Solution:**
```bash
# Test production build locally
cd frontend
npm run build

# If it fails locally, fix the errors
# If it succeeds locally but fails in GitHub Actions, check:
# - package.json dependencies
# - TypeScript errors
# - Environment-specific code
```

---

### Issue 3: Deployment Succeeds But Site Shows Old Version

**Cause:** Browser cache or deployment still propagating

**Solution:**
1. Hard refresh browser: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
2. Clear browser cache
3. Wait 1-2 minutes for Azure to restart
4. Check deployment logs to confirm it completed

---

### Issue 4: Frontend Can't Connect to Backend

**Cause:** Backend might be down or CORS issue

**Check backend status:**
```bash
curl https://sre-backend-az1.azurewebsites.net/sre/status
curl https://sre-backend-az2.azurewebsites.net/sre/status
```

Both should return JSON with status information.

**CORS is already enabled** on both backends, so this shouldn't be an issue.

---

## 🎯 Best Practices

### Before Pushing:

1. **Test locally first**
   ```bash
   cd frontend
   npm run dev
   # Verify your changes work
   ```

2. **Run build test** (optional but recommended)
   ```bash
   npm run build
   # Ensures production build works
   ```

3. **Write clear commit messages**
   ```bash
   git commit -m "Add: Natural language search UI component"
   # Not: "fix stuff"
   ```

### During Development:

- **Make small, frequent commits** - easier to debug if something breaks
- **Test each feature** before committing
- **Check GitHub Actions status** after pushing

---

## 📊 Deployment Pipeline Details

The GitHub Actions workflow does this:

```yaml
1. Checkout code from main branch
2. Set up Node.js 20
3. Install dependencies (npm ci)
4. Build Next.js app (standalone mode)
   - Includes NEXT_PUBLIC_API_URL_AZ1 and AZ2
5. Copy static files to standalone build
6. Copy public folder to standalone build
7. Create deployment zip
8. Login to Azure (using service principal)
9. Deploy to sre-frontend app service
10. Restart app
```

**Total time:** ~1-2 minutes

---

## 🔐 Secrets & Credentials (Already Configured)

GitHub repository has these secrets configured:
- ✅ `AZURE_CREDENTIALS` - Service principal for Azure login
- ✅ `AZURE_FRONTEND_PUBLISH_PROFILE` - Legacy secret (not currently used)

**You don't need to worry about these** - they're already set up!

---

## 🆘 Getting Help

If deployment fails or you need help:

1. **Check the logs first** (see "Monitoring Deployments" above)
2. **Try the solutions** in "Common Issues" section
3. **Ask Bala** if issue persists

---

## 🎬 Demo Day Checklist

Before the 5 PM demo:

- [ ] Push all your final changes to main
- [ ] Wait for GitHub Actions to complete (check Actions tab)
- [ ] Verify deployment at https://sre-frontend.azurewebsites.net
- [ ] Test all features work (search, safety analysis, chat, logs)
- [ ] Verify backend connectivity to AZ1 and AZ2
- [ ] Hard refresh browser to clear cache
- [ ] Have a backup plan: Local dev at http://localhost:3000

---

## 📌 Quick Reference

| What | URL/Command |
|------|-------------|
| **Production Frontend** | https://sre-frontend.azurewebsites.net |
| **Backend AZ1** | https://sre-backend-az1.azurewebsites.net |
| **Backend AZ2** | https://sre-backend-az2.azurewebsites.net |
| **Local Development** | http://localhost:3000 or 3001 |
| **GitHub Actions** | https://github.com/BalaAnbalagan/cmpe_273_sec_47_sre_ai_agent_hackathon_opsc/actions |
| **Check Deployment** | `gh run list --workflow=azure-frontend-deploy.yml` |
| **View Logs** | Click on workflow run → "build-and-deploy" job |

---

## ✨ That's It!

Just push to main and let GitHub Actions handle the deployment. Focus on building great UI! 🚀

**Team OPSC - Demo Ready!**

---

**Questions?** Ask Bala or check the GitHub Actions logs.
