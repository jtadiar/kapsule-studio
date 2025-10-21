# Deployment Guide for Developers

## For New Developers Deploying Their Own Instance

### Step 1: Prerequisites

1. Create a GCP project at https://console.cloud.google.com
2. Enable billing
3. Install gcloud CLI: https://cloud.google.com/sdk/docs/install
4. Authenticate: `gcloud auth login`

### Step 2: Clone and Setup

```bash
git clone https://github.com/YOUR_USERNAME/kapsule-studio.git
cd kapsule-studio
./setup-gcp.sh
```

Follow prompts to enter your project ID and bucket name.

### Step 3: Local Testing (Optional)

```bash
# Backend
cd kapsule-studio-api
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
gcloud auth application-default login
uvicorn main:app --reload

# Frontend (new terminal)
cd kapsule-studio-frontend
npm install
npm run dev
```

### Step 4: Deploy to Cloud Run

```bash
# Deploy backend first
cd kapsule-studio-api
./deploy.sh

# Then deploy frontend
cd ../kapsule-studio-frontend
./deploy.sh
```

### Step 5: Update Backend CORS

After frontend deployment, update backend to allow frontend URL:

```bash
FRONTEND_URL=$(gcloud run services describe kapsule-studio-frontend --region us-central1 --format="value(status.url)")

gcloud run services update kapsule-studio-api \
  --region us-central1 \
  --set-env-vars FRONTEND_URL=${FRONTEND_URL}
```

### Troubleshooting

**Build fails**: Ensure Docker is running and gcloud is authenticated

**403 errors**: Check IAM permissions for Cloud Run service account

**Veo quota**: Request quota increase at https://console.cloud.google.com/iam-admin/quotas

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for system architecture details.

## Security Notes

- Never commit credentials or API keys to git
- Use Secret Manager for sensitive configuration
- Service accounts should have minimal required permissions
- Review `.gitignore` files before committing

## Cost Management

Monitor your Cloud Run usage:
```bash
gcloud run services describe kapsule-studio-api --region us-central1
gcloud run services describe kapsule-studio-frontend --region us-central1
```

Set budget alerts in GCP Console to avoid unexpected charges.

## Updating Your Deployment

To update the backend:
```bash
cd kapsule-studio-api
./deploy.sh
```

To update the frontend:
```bash
cd kapsule-studio-frontend
./deploy.sh
```

Changes will be deployed automatically with zero downtime.

