#!/bin/bash
set -e

echo "Kapsule Studio - GCP Setup Script"
echo "=================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI not found. Install from https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Prompt for project ID
read -p "Enter your GCP Project ID: " PROJECT_ID
read -p "Enter your GCS Bucket Name: " BUCKET_NAME
read -p "Enter region (default: us-central1): " REGION
REGION=${REGION:-us-central1}

echo ""
echo "Setting up project: ${PROJECT_ID}"

# Set project
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  firestore.googleapis.com

# Create secrets
echo "Creating secrets in Secret Manager..."
echo -n "${PROJECT_ID}" | gcloud secrets create gcp-project-id --data-file=- --replication-policy=automatic || echo "Secret gcp-project-id already exists"
echo -n "${BUCKET_NAME}" | gcloud secrets create gcs-bucket-name --data-file=- --replication-policy=automatic || echo "Secret gcs-bucket-name already exists"

# Grant Cloud Run access to secrets
echo "Granting Cloud Run access to secrets..."
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud secrets add-iam-policy-binding gcp-project-id \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" || true

gcloud secrets add-iam-policy-binding gcs-bucket-name \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" || true

# Create .env file for local development
echo "Creating .env file for local development..."
cat > kapsule-studio-api/.env <<EOF
GCP_PROJECT_ID=${PROJECT_ID}
GCS_BUCKET_NAME=${BUCKET_NAME}
GCP_REGION=${REGION}
FRONTEND_URL=http://localhost:3000
GEMINI_MODEL=gemini-2.5-flash
USE_GEMINI_PROMPT_ENHANCER=false
EOF

echo ""
echo "Setup complete!"
echo "Next steps:"
echo "1. cd kapsule-studio-api && ./deploy.sh"
echo "2. cd kapsule-studio-frontend && ./deploy.sh"

