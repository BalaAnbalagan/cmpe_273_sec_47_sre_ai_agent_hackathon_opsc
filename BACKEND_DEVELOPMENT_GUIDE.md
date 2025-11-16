# Backend Development Guide

## Project Structure

The backend is a FastAPI application deployed to Azure App Service with the following structure:

```
backend/
├── main.py                    # Entrypoint (imports from api.main)
├── requirements.txt           # Python dependencies
└── api/                       # Main application package
    ├── main.py               # FastAPI app definition
    ├── core/                 # Core configuration
    │   ├── __init__.py
    │   ├── config.py         # Settings and environment variables
    │   └── keyvault.py       # Azure Key Vault integration
    ├── models/               # Data models
    │   └── schemas.py        # Pydantic models
    ├── routers/              # API endpoints
    │   ├── __init__.py
    │   └── sre.py           # SRE endpoints
    └── services/             # Business logic
        ├── __init__.py
        ├── cohere_service.py
        ├── image_service.py
        ├── log_service.py
        ├── mongo_client.py
        ├── redis_client.py
        ├── telemetry_service.py
        └── user_service.py
```

## Critical Rules for Development

### 1. Import Paths

**ALWAYS use `api.*` prefix for imports, NEVER `backend.api.*`**

```python
# ✅ CORRECT
from api.core.config import settings
from api.services.redis_client import get_redis
from api.models.schemas import TelemetryEvent

# ❌ WRONG - Will break on Azure
from backend.api.core.config import settings
from backend.api.services.redis_client import get_redis
```

**Why?** Azure deploys to `/home/site/wwwroot/` so the Python path starts at `backend/`, making the package root `api/`.

### 2. File Structure Rules

- **backend/main.py** must remain a simple entrypoint only:
```python
import os
import sys
sys.path.append(os.path.dirname(__file__))
from api.main import app
__all__ = ["app"]
```

- **backend/requirements.txt** must be at the root level
- **backend/api/** contains all application code
- All subdirectories under `api/` must have `__init__.py` files

### 3. Adding New Dependencies

1. Add to `backend/requirements.txt`
2. Test locally:
```bash
cd backend
pip3 install -r requirements.txt
python3 -c "from api.main import app"
```
3. Deploy (see deployment section)

### 4. Adding New Routes

1. Add endpoint to `backend/api/routers/sre.py` or create new router file
2. Use correct imports:
```python
from fastapi import APIRouter
from api.models.schemas import YourModel
from api.services.your_service import your_function
```
3. Register router in `backend/api/main.py`:
```python
from api.routers.sre import router as sre_router
app.include_router(sre_router)
```

### 5. Adding New Services

1. Create file in `backend/api/services/`
2. Use correct imports:
```python
from api.core.config import settings
from api.services.redis_client import get_redis
```
3. Import in routers:
```python
from api.services.your_service import your_function
```

### 6. Environment Variables

Configuration is managed through:
- Azure Key Vault (production secrets)
- App Settings in Azure App Service
- `.env` file (local development only - never commit)

Access config:
```python
from api.core.config import settings
print(settings.REDIS_HOST)
```

## Local Development

### Setup

```bash
cd backend
pip3 install -r requirements.txt

# Create .env file (do not commit)
cat > .env << EOF
USE_KEY_VAULT=false
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-password
COSMOS_MONGODB_URI=mongodb://localhost:27017
COSMOS_DATABASE=sre-database
COHERE_API_KEY=your-api-key
# ... other settings
EOF
```

### Test Imports

```bash
cd backend
python3 -c "from api.main import app; print('✅ Imports working')"
```

### Run Locally

```bash
cd backend
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 120
```

Access at: http://localhost:8000/sre/status

## Deployment to Azure

### Deployment Structure

Azure expects this at `/home/site/wwwroot/`:
```
main.py
requirements.txt
api/
  ├── main.py
  ├── core/
  ├── models/
  ├── routers/
  └── services/
```

### Deploy to Both Zones

```bash
cd backend

# Create deployment package
zip -r backend-deploy.zip main.py requirements.txt api/ -x "*.pyc" -x "*__pycache__*"

# Verify package contents
unzip -l backend-deploy.zip

# Deploy to AZ1
az webapp deploy \
  --name sre-backend-az1 \
  --resource-group rg-cmpe273-sre-hackathon \
  --src-path backend-deploy.zip \
  --type zip \
  --async false

# Deploy to AZ2
az webapp deploy \
  --name sre-backend-az2 \
  --resource-group rg-cmpe273-sre-hackathon \
  --src-path backend-deploy.zip \
  --type zip \
  --async false
```

### Verify Deployment

```bash
# Check AZ1
curl https://sre-backend-az1.azurewebsites.net/sre/status

# Check AZ2
curl https://sre-backend-az2.azurewebsites.net/sre/status
```

## Azure App Service Configuration

### Startup Command
```bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 120
```

### App Settings (Environment Variables)

Set via Azure CLI:
```bash
az webapp config appsettings set \
  --name sre-backend-az1 \
  --resource-group rg-cmpe273-sre-hackathon \
  --settings \
    USE_KEY_VAULT=true \
    AZURE_CLIENT_ID="@Microsoft.KeyVault(...)" \
    REDIS_HOST="redis-sre-ha.redis.cache.windows.net" \
    # ... more settings
```

### Managed Identity

Both App Services use User Managed Identity:
- Client ID: `9de1422a-8247-4986-b63d-bffe81f0d114`
- Has access to: Key Vault, Storage Account, Cosmos DB, Redis

## Common Issues and Solutions

### Issue: `ModuleNotFoundError: No module named 'backend'`

**Cause:** Using `from backend.api.*` imports

**Solution:** Change to `from api.*` imports

```python
# Fix all files
find backend/api -name "*.py" -exec sed -i '' 's/from backend\.api\./from api./g' {} +
```

### Issue: `ModuleNotFoundError: No module named 'motor'`

**Cause:** Missing dependency

**Solution:** Add to `requirements.txt` and redeploy

### Issue: Application Error on Azure

**Cause:** Missing api/ directory in deployment package

**Solution:** Ensure zip command includes `api/`:
```bash
zip -r backend-deploy.zip main.py requirements.txt api/
```

### Issue: App starts locally but fails on Azure

**Cause:** Import paths or missing dependencies

**Solution:**
1. Test imports: `python3 -c "from api.main import app"`
2. Check all imports use `api.*` prefix
3. Verify all dependencies in `requirements.txt`

## Development Workflow

### 1. Make Changes

```bash
# Edit files in backend/api/
vim backend/api/routers/sre.py
```

### 2. Test Locally

```bash
cd backend
python3 -c "from api.main import app"
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000
```

### 3. Commit Changes

```bash
git add backend/
git commit -m "Feature: Add new endpoint"
git push origin main
```

### 4. Deploy to Azure

```bash
cd backend
zip -r backend-deploy.zip main.py requirements.txt api/ -x "*.pyc" -x "*__pycache__*"

# Deploy to both zones
az webapp deploy --name sre-backend-az1 --resource-group rg-cmpe273-sre-hackathon --src-path backend-deploy.zip --type zip --async false
az webapp deploy --name sre-backend-az2 --resource-group rg-cmpe273-sre-hackathon --src-path backend-deploy.zip --type zip --async false
```

### 5. Verify

```bash
curl https://sre-backend-az1.azurewebsites.net/sre/status
curl https://sre-backend-az2.azurewebsites.net/sre/status
```

## Endpoints

### Health Check
```bash
GET /sre/status
```

### Deployment Version
```bash
GET /sre/deployment-version
```

### Telemetry
```bash
POST /sre/telemetry
```

### User Metrics
```bash
POST /sre/user-metric
```

### Image Search
```bash
POST /sre/search-images
```

### Logs
```bash
POST /sre/top-ips
```

## Key Vault Integration

Secrets are loaded on startup via `api.core.config.Settings.load_from_keyvault()`:

```python
# In api/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting SRE Hackathon API")
    ok = await settings.load_from_keyvault()
    logger.info(f"Key Vault Loaded: {ok}")
    yield
    await close_redis()
    await close_mongo()
```

Secrets loaded from Key Vault:
- `CohereAPIKey`
- `RedisKey`
- `CosmosMongoDBConnectionString`

## Production URLs

- **AZ1:** https://sre-backend-az1.azurewebsites.net
- **AZ2:** https://sre-backend-az2.azurewebsites.net

## Team Best Practices

1. **Always test imports before deploying:**
   ```bash
   cd backend && python3 -c "from api.main import app"
   ```

2. **Never commit secrets** - use Key Vault or app settings

3. **Deploy to both zones** after changes

4. **Use relative imports** with `api.*` prefix

5. **Add `__init__.py`** to all new packages

6. **Update requirements.txt** when adding dependencies

7. **Test locally first** before deploying to Azure

## Quick Reference

```bash
# Test imports
cd backend && python3 -c "from api.main import app"

# Run locally
cd backend && gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 120

# Create deployment package
cd backend && zip -r backend-deploy.zip main.py requirements.txt api/ -x "*.pyc" -x "*__pycache__*"

# Deploy to AZ1
az webapp deploy --name sre-backend-az1 --resource-group rg-cmpe273-sre-hackathon --src-path backend/backend-deploy.zip --type zip --async false

# Deploy to AZ2
az webapp deploy --name sre-backend-az2 --resource-group rg-cmpe273-sre-hackathon --src-path backend/backend-deploy.zip --type zip --async false

# Check status
curl https://sre-backend-az1.azurewebsites.net/sre/status
curl https://sre-backend-az2.azurewebsites.net/sre/status
```
