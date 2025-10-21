#!/bin/bash
set -e

PROJECT_ID="gen-lang-client-0915852466"
REGION="us-central1"
SERVICE_NAME="kapsule-studio-frontend"

# Get backend URL
BACKEND_URL=$(gcloud run services describe kapsule-studio-api --region ${REGION} --format="value(status.url)")

echo "Backend URL: ${BACKEND_URL}"
echo "Building and deploying frontend to Cloud Run..."

gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}

gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 512Mi \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars VITE_API_URL=${BACKEND_URL}

echo "Frontend deployed!"
gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format="value(status.url)"

