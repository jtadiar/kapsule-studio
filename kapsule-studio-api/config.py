import os
from dotenv import load_dotenv
from google.cloud import secretmanager

# Load environment variables from .env file
load_dotenv()


def access_secret(secret_id: str, default: str = "") -> str:
    """Access secret from Secret Manager, fallback to env var or default."""
    try:
        client = secretmanager.SecretManagerServiceClient()
        project_id = os.getenv('GCP_PROJECT_ID', 'gen-lang-client-0915852466')
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception:
        # Fallback to environment variable or default
        return os.getenv(secret_id.upper().replace('-', '_'), default)


# Google Cloud Platform Configuration
GCP_PROJECT_ID = access_secret("gcp-project-id", os.getenv("GCP_PROJECT_ID", "gen-lang-client-0915852466"))
GCS_BUCKET_NAME = access_secret("gcs-bucket-name", os.getenv("GCS_BUCKET_NAME", "kapsule-stitch-public"))
GCP_REGION = os.getenv("GCP_REGION", "us-central1")

# Frontend CORS Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Server Configuration
PORT = int(os.getenv("PORT", 8000))

# File Upload Configuration
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB in bytes (increased for full audio files)
ALLOWED_AUDIO_TYPES = ["audio/mpeg", "audio/wav", "audio/m4a"]

# Veo Configuration
VEO_MODEL = "veo-3.0-generate-001"
VEO_LOCATION = GCP_REGION

# Gemini (Prompt Enhancer) Configuration  
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_LOCATION = os.getenv("GEMINI_LOCATION", GCP_REGION)
USE_GEMINI_PROMPT_ENHANCER = os.getenv("USE_GEMINI_PROMPT_ENHANCER", "false").lower() == "true"

# Storage Paths
AUDIO_FOLDER = "audio/"
VIDEO_FOLDER = "video/"

# Firestore Collections
JOBS_COLLECTION = "jobs"

