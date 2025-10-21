# Netlify Deployment Guide for Kapsule Studio

## ✅ Build Complete!

Your frontend is built and ready to deploy at:
```
/Users/jt/Documents/apps/kapsule-studio/kapsule-studio-frontend/dist/
```

Backend API URL configured: `https://kapsule-studio-api-qgkw6ysw4a-uc.a.run.app`

---

## Option 1: Deploy via Netlify CLI (Recommended)

### Install Netlify CLI
```bash
npm install -g netlify-cli
```

### Login to Netlify
```bash
netlify login
```
This will open your browser for authentication.

### Deploy
```bash
cd /Users/jt/Documents/apps/kapsule-studio/kapsule-studio-frontend
netlify deploy --prod --dir=dist
```

Follow the prompts:
- **Create & configure a new site?** → Yes
- **Team** → Select your team
- **Site name** → kapsule-studio (or leave blank)
- **Deploy path** → dist (pre-filled)

**Save the deployed URL** (e.g., `https://kapsule-studio-abc123.netlify.app`)

---

## Option 2: Deploy via Netlify Web UI (Drag & Drop)

1. Go to https://app.netlify.com
2. Click **"Add new site"** → **"Deploy manually"**
3. Drag the `dist/` folder into the deploy zone:
   ```
   /Users/jt/Documents/apps/kapsule-studio/kapsule-studio-frontend/dist/
   ```
4. Wait ~30 seconds for deployment
5. **Save your site URL** (e.g., `https://kapsule-studio-abc123.netlify.app`)

---

## Configure Custom Domain: studio.kapsule.co

### In Netlify Dashboard:

1. Go to your deployed site
2. Click **"Domain settings"** or **"Set up a custom domain"**
3. Click **"Add custom domain"**
4. Enter: `studio.kapsule.co`
5. Click **"Verify"** → **"Add domain"**
6. Netlify will show DNS configuration instructions

### In Your Domain Registrar (where kapsule.co is hosted):

Add a **CNAME record**:

| Type  | Name   | Value                                    | TTL  |
|-------|--------|------------------------------------------|------|
| CNAME | studio | [your-netlify-site].netlify.app         | 3600 |

**Example:**
```
studio  →  kapsule-studio-abc123.netlify.app
```

**DNS propagation:** 5-60 minutes. Netlify will auto-provision SSL/HTTPS.

---

## Update Backend CORS

Your backend needs to allow requests from your Netlify domain.

### Quick Update (Single Domain):
```bash
gcloud run services update kapsule-studio-api \
  --region us-central1 \
  --set-env-vars FRONTEND_URL=https://studio.kapsule.co
```

### Better: Support Multiple Origins

**Edit:** `/Users/jt/Documents/apps/kapsule-studio/kapsule-studio-api/main.py`

Find this section (around line 30):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Replace with:
```python
# Support multiple frontend origins
allowed_origins = [
    "https://studio.kapsule.co",
    "https://kapsule-studio-abc123.netlify.app",  # Replace with YOUR actual Netlify URL
    "http://localhost:3000",  # For local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy the backend:
```bash
cd /Users/jt/Documents/apps/kapsule-studio/kapsule-studio-api
./deploy.sh
```

---

## Test Your Deployment

### Before DNS Propagates (Immediate):
Use the default Netlify URL:
```
https://kapsule-studio-abc123.netlify.app
```

### After DNS Propagates (5-60 minutes):
```
https://studio.kapsule.co
```

### Test Workflow:
1. Visit your site
2. Upload an audio file (at least 15 seconds)
3. Select a 15-second segment
4. Customize video options
5. Click "Preview Enhanced Prompt" (optional)
6. Click "Generate Video"
7. Wait for processing (2-5 minutes)
8. Download the result

---

## Troubleshooting

### CORS Errors in Browser Console
**Solution:** Update backend CORS settings (see above)

### DNS Not Resolving
**Solution:** 
- Check propagation: https://dnschecker.org/#CNAME/studio.kapsule.co
- Verify CNAME record in domain registrar
- Wait up to 60 minutes

### Build Errors
**Solution:** 
```bash
cd /Users/jt/Documents/apps/kapsule-studio/kapsule-studio-frontend
rm -rf node_modules dist
npm install
npm run build
```

### Video Generation Fails
**Solution:**
- Check browser console for errors
- Verify backend is running: `curl https://kapsule-studio-api-qgkw6ysw4a-uc.a.run.app/`
- Check backend logs:
  ```bash
  gcloud run services logs read kapsule-studio-api --region us-central1 --limit 50
  ```

---

## Quick Redeploy (After Changes)

```bash
cd /Users/jt/Documents/apps/kapsule-studio/kapsule-studio-frontend
npm run build
netlify deploy --prod --dir=dist
```

---

## Netlify CLI Useful Commands

```bash
# Check deployment status
netlify status

# View site in browser
netlify open:site

# View deployment logs
netlify logs

# List all sites
netlify sites:list
```

---

## Summary Checklist

- [x] Frontend built with production API URL
- [ ] Deploy to Netlify (CLI or web UI)
- [ ] Note your Netlify URL
- [ ] Add custom domain `studio.kapsule.co` in Netlify
- [ ] Configure CNAME record in DNS
- [ ] Update backend CORS settings
- [ ] Wait for DNS propagation (5-60 min)
- [ ] Test at `https://studio.kapsule.co`
- [ ] Share demo link for hackathon! 🚀

---

## Your Deployment URLs

**Backend API:** https://kapsule-studio-api-qgkw6ysw4a-uc.a.run.app

**Frontend (Netlify):** [Fill in after deployment]

**Custom Domain:** https://studio.kapsule.co (after DNS setup)

---

## Cost

**Netlify Free Tier:**
- 100GB bandwidth/month
- Unlimited sites
- Automatic SSL
- Global CDN
- **Cost: $0**

Perfect for hackathons and demos! 🎉

