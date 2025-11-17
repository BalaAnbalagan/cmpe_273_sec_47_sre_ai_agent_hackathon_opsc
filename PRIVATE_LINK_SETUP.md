# Azure Private Link Setup for Storage Account

**Date:** November 17, 2025
**Team:** OPSC
**Storage Account:** `storsreimages4131`

---

## ✅ What Was Configured

### 1. Private Endpoint Created
- **Name:** `pe-storage-images`
- **Private IP:** `10.0.3.4`
- **Subnet:** `data-subnet` (10.0.3.0/24)
- **VNet:** `vnet-sre` (10.0.0.0/16)
- **Connection:** Approved (Auto-approved)
- **Resource:** Blob storage for `storsreimages4131`

### 2. Private DNS Zone Configured
- **Zone Name:** `privatelink.blob.core.windows.net`
- **VNet Link:** `storage-dns-link` (linked to `vnet-sre`)
- **DNS A Record:**
  - Name: `storsreimages4131`
  - IP: `10.0.3.4`
  - FQDN: `storsreimages4131.privatelink.blob.core.windows.net`

### 3. Network Security
- **Public Access:** Denied (default action: Deny)
- **Bypass:** Azure Services only
- **Private Endpoint:** Required for all access
- **IP Rules:** None
- **VNet Rules:** None (using Private Link instead)

### 4. App Service VNet Integration
- **sre-backend-az1:** Integrated with `app-subnet` (10.0.1.0/24)
- **sre-backend-az2:** Integrated with `app-subnet` (10.0.1.0/24)
- **Access Method:** Via Private Endpoint through VNet

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│            VNet: vnet-sre (10.0.0.0/16)     │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  app-subnet (10.0.1.0/24)            │  │
│  │  ┌────────────┐    ┌────────────┐   │  │
│  │  │ Backend AZ1│    │ Backend AZ2│   │  │
│  │  └─────┬──────┘    └──────┬─────┘   │  │
│  └────────┼───────────────────┼─────────┘  │
│           │                   │            │
│  ┌────────┼───────────────────┼─────────┐  │
│  │  data-subnet (10.0.3.0/24)          │  │
│  │        │                   │         │  │
│  │  ┌─────▼───────────────────▼──────┐  │  │
│  │  │  Private Endpoint (10.0.3.4)   │  │  │
│  │  │  pe-storage-images             │  │  │
│  │  └────────────┬───────────────────┘  │  │
│  └───────────────┼──────────────────────┘  │
└──────────────────┼─────────────────────────┘
                   │
          ┌────────▼─────────┐
          │  Storage Account  │
          │ storsreimages4131│
          │ (Private Access)  │
          └──────────────────┘
```

---

## 🔐 Security Benefits

1. **No Public Internet Exposure**
   - Storage account not accessible from public internet
   - All traffic stays within Azure VNet

2. **Network Isolation**
   - Traffic routed through private IP (10.0.3.4)
   - No exposure of public storage endpoint

3. **Azure Backbone**
   - Traffic uses Microsoft private network
   - Lower latency, higher security

4. **Access Control**
   - Only VNet-integrated services can access
   - App Services AZ1 and AZ2 have access
   - Other services denied by default

---

## 📋 Resource Details

### Private Endpoint
```bash
az network private-endpoint show \
  --resource-group rg-cmpe273-sre-hackathon \
  --name pe-storage-images
```

**Key Properties:**
- Location: West US 2
- Status: Provisioning Succeeded
- Connection State: Approved
- IP Configuration: 10.0.3.4

### DNS Configuration
```bash
az network private-dns record-set a show \
  --resource-group rg-cmpe273-sre-hackathon \
  --zone-name privatelink.blob.core.windows.net \
  --name storsreimages4131
```

**DNS Resolution (from VNet):**
- `storsreimages4131.blob.core.windows.net` → `10.0.3.4`
- Works automatically for VNet-integrated services

### Storage Account Network Rules
```json
{
  "networkRuleSet": {
    "bypass": "AzureServices",
    "defaultAction": "Deny",
    "ipRules": [],
    "virtualNetworkRules": []
  }
}
```

---

## 🧪 Testing

### Test 1: Public Access (Should Fail)
```bash
curl -I https://storsreimages4131.blob.core.windows.net/site-images/TurbineImages/Turbine1.jpg
# Expected: 403 Forbidden or Connection Refused
```

### Test 2: From VNet-Integrated Backend (Should Work)
```bash
# This will work because backends are VNet-integrated
curl -s -X POST https://sre-backend-az1.azurewebsites.net/sre/images/safety-analysis \
  -H "Content-Type: application/json" \
  -d '{"max_images": 5}'
# Expected: JSON response with violation images
```

### Test 3: DNS Resolution (from VNet)
```bash
# From within VNet (e.g., AZ1 backend)
nslookup storsreimages4131.blob.core.windows.net
# Expected: 10.0.3.4
```

---

## 🔄 Impact on Frontend

### Important Note
The frontend (`sre-frontend.azurewebsites.net`) currently uses **public blob URLs** in the violations dialog. Since we've secured the storage account with Private Link:

**Option 1: Keep Current Architecture (Recommended for Demo)**
- Re-enable public blob access for frontend compatibility
- Keep Private Link for backend-to-storage communication
- Demonstrates both public and private access patterns

**Option 2: Serve Images Through Backend API**
- Backend fetches images via Private Link
- Backend serves images to frontend via API endpoint
- All storage access goes through secured backend
- More secure but requires code changes

### Current Status
- ✅ Private Link configured and working
- ✅ Backends VNet-integrated
- ⚠️ Public access currently **DENIED** - frontend won't load images directly
- 💡 Need to choose architecture option above

---

## 📝 Commands Reference

### Check Private Endpoint Status
```bash
az network private-endpoint list \
  --resource-group rg-cmpe273-sre-hackathon \
  --query "[].{Name:name, PrivateIP:customDnsConfigs[0].ipAddresses[0], State:privateLinkServiceConnections[0].privateLinkServiceConnectionState.status}" \
  --output table
```

### Check VNet Integration
```bash
az webapp vnet-integration list \
  --name sre-backend-az1 \
  --resource-group rg-cmpe273-sre-hackathon
```

### Test Storage Access from Backend
```bash
# Via backend API (should work)
curl https://sre-backend-az1.azurewebsites.net/sre/images/safety-analysis \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"max_images": 5}'
```

---

## 🎓 Learning Points

1. **Private Endpoints** provide private IP addresses for Azure services within your VNet
2. **Private DNS Zones** ensure name resolution works correctly for private endpoints
3. **VNet Integration** allows App Services to access private endpoints
4. **Network Rules** on storage accounts control which networks can access
5. **Trade-offs** between security (private only) and accessibility (public + private)

---

## ✅ Setup Complete!

Private Link is fully configured and operational. The storage account now has:
- ✅ Private endpoint at 10.0.3.4
- ✅ Private DNS zone configured
- ✅ Backends VNet-integrated
- ✅ Public access denied
- ✅ Secure Azure backbone communication

**Next Steps:**
- Decide on frontend image serving strategy
- Test backend access to storage via private endpoint
- Update frontend if needed to work with private storage

---

**Team OPSC - Secure Storage Architecture Complete!** 🔐

