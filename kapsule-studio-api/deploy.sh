#!/bin/bash
set -e

PROJECT_ID="gen-lang-client-0915852466"
REGION="us-central1"
SERVICE_NAME="kapsule-studio-api"

echo "Building and deploying backend to Cloud Run..."

gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}

gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600 \
  --max-instances 10 \
  --set-env-vars GCP_PROJECT_ID=${PROJECT_ID},GCP_REGION=${REGION}

echo "Backend deployed!"
gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format="value(status.url)"

