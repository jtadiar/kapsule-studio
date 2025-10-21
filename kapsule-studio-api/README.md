# Kapsule Studio API

A production-ready FastAPI backend for Kapsule Studio that handles audio uploads, video generation using Google's Veo 3.0 model, and video stitching with FFmpeg.

## Features

- **Audio Upload**: Upload audio tracks (MP3, WAV, M4A) to Google Cloud Storage
- **Video Generation**: Generate cinematic videos using Google's Veo 3.0 AI model
- **Video Stitching**: Merge generated video with user's audio using FFmpeg
- **Job Tracking**: Async job processing with real-time status updates via Firestore
- **Cloud Native**: Designed for Google Cloud Run deployment

## Prerequisites

- Python 3.11+
- Google Cloud Platform account with:
  - Cloud Storage bucket configured
  - Firestore database enabled
  - Vertex AI API enabled
  - Application Default Credentials configured

## Local Development Setup

1. **Clone and navigate to the API directory**
   ```bash
   cd kapsule-studio-api
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg** (if not already installed)
   - macOS: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your GCP project details
   ```

6. **Authenticate with Google Cloud**
   ```bash
   gcloud auth application-default login
   ```

7. **Run the development server**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`

## API Endpoints

### `POST /api/upload-audio`
Upload an audio file to Google Cloud Storage.

**Request**: `multipart/form-data` with `file` field  
**Response**: `{"audio_url": "gs://bucket-name/audio/filename"}`

### `POST /api/generate`
Start video generation job.

**Request**:
```json
{
  "genre": "Pop",
  "visualStyle": "Cinematic",
  "cameraMovement": "Slow Pan",
  "mood": "Uplifting",
  "subject": "Solo Dancer",
  "setting": "City Rooftop",
  "duration": "8s",
  "extra": "Additional prompt details...",
  "audio_url": "gs://bucket-name/audio/filename",
  "prompt": "Full prompt string"
}
```

**Response**: `{"job_id": "unique-job-id"}`

### `GET /api/result/{job_id}`
Get the status of a video generation job.

**Response**:
- Queued: `{"status": "queued"}`
- Processing: `{"status": "processing"}`
- Complete: `{"status": "complete", "video_url": "https://..."}`
- Error: `{"status": "error", "error": "Error message"}`

## Deployment to Google Cloud Run

1. **Build and push Docker image**
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/kapsule-studio-api
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy kapsule-studio-api \
     --image gcr.io/YOUR_PROJECT_ID/kapsule-studio-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT_ID,GCS_BUCKET_NAME=YOUR_BUCKET,FRONTEND_URL=https://your-frontend.com
   ```

## Project Structure

```
kapsule-studio-api/
├── main.py                    # FastAPI application and routes
├── config.py                  # Configuration and environment variables
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container configuration
├── services/
│   ├── storage_service.py    # Google Cloud Storage operations
│   ├── firestore_service.py  # Firestore job tracking
│   └── veo_service.py        # Veo 3.0 video generation
└── utils/
    └── video_utils.py        # FFmpeg video processing
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GCP_PROJECT_ID` | Google Cloud project ID | gen-lang-client-0915852466 |
| `GCS_BUCKET_NAME` | Cloud Storage bucket name | kapsule-stitch-public |
| `GCP_REGION` | GCP region | us-central1 |
| `FRONTEND_URL` | Frontend URL for CORS | http://localhost:5173 |
| `PORT` | Server port | 8000 |

## License

MIT

