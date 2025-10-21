# Kapsule Studio - Complete Setup Guide

## 🎯 What You Have

A production-ready full-stack application for AI-powered music video generation:

- **Backend API**: Standalone FastAPI serverless application (`kapsule-studio-api/`)
- **Frontend**: React TypeScript application (`kapsule-studio-frontend/`)
- **Integration**: Frontend seamlessly connects to backend API
- **Cloud Infrastructure**: Google Cloud Platform (Veo 3.0, Cloud Storage, Firestore)

## 📁 Complete Project Structure

```
kapsule-studio/
│
├── README.md                           # Main project documentation
├── SETUP_GUIDE.md                     # This file
│
├── kapsule-studio-api/                # Backend API (Standalone)
│   ├── main.py                        # FastAPI app with 3 endpoints
│   ├── config.py                      # Environment configuration
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile                     # Cloud Run deployment
│   ├── .dockerignore                  # Docker ignore rules
│   ├── .gitignore                     # Git ignore rules
│   ├── README.md                      # API-specific documentation
│   ├── start.sh                       # Quick start script (Unix/Mac)
│   ├── start.bat                      # Quick start script (Windows)
│   │
│   ├── services/                      # Business logic services
│   │   ├── __init__.py
│   │   ├── storage_service.py         # Google Cloud Storage operations
│   │   ├── firestore_service.py       # Job tracking with Firestore
│   │   └── veo_service.py            # Veo 3.0 video generation
│   │
│   └── utils/                         # Utility functions
│       ├── __init__.py
│       └── video_utils.py            # FFmpeg video/audio merging
│
└── kapsule-studio-frontend/          # Frontend Application
    ├── App.tsx                        # Main app (with API integration)
    ├── vite-env.d.ts                 # TypeScript env definitions
    ├── components/
    │   ├── UploadSection.tsx         # Audio upload (API integrated)
    │   ├── VideoPreview.tsx          # Video display (API integrated)
    │   ├── PromptForm.tsx
    │   └── Card.tsx
    └── (other frontend files...)
```

## 🚀 Quick Start (5 Minutes)

### Step 1: Backend API

```bash
cd kapsule-studio-api

# Easy method (uses startup script)
./start.sh

# Manual method
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your GCP settings
gcloud auth application-default login
uvicorn main:app --reload --port 8000
```

✅ Backend running at: `http://localhost:8000`  
📖 API docs at: `http://localhost:8000/docs`

### Step 2: Frontend

```bash
cd kapsule-studio-frontend

npm install
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

✅ Frontend running at: `http://localhost:5173`

## 🔧 Configuration

### Backend Environment Variables (.env in api/)

```bash
GCP_PROJECT_ID=gen-lang-client-0915852466
GCS_BUCKET_NAME=kapsule-stitch-public
GCP_REGION=us-central1
FRONTEND_URL=http://localhost:5173
PORT=8000
```

### Frontend Environment Variables (.env in frontend/)

```bash
VITE_API_URL=http://localhost:8000
```

## 🎬 How It Works

### 1️⃣ Audio Upload Flow
```
User → Frontend → POST /api/upload-audio → GCS
                ← {audio_url: "gs://..."}
```

### 2️⃣ Video Generation Flow
```
User → Frontend → POST /api/generate → Firestore (creates job)
                ← {job_id: "abc123"}
                
                → Background Task:
                  1. Veo 3.0 generates video (2-5 min)
                  2. Downloads user's audio from GCS
                  3. FFmpeg merges video + audio
                  4. Uploads final video to GCS
                  5. Updates Firestore job status
```

### 3️⃣ Status Polling Flow
```
Frontend → GET /api/result/{job_id} (every 3 seconds)
         ← {status: "processing"}
         ← {status: "processing"}
         ← {status: "complete", video_url: "https://..."}
```

## 📦 API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/upload-audio` | POST | Upload audio file to GCS |
| `/api/generate` | POST | Start video generation job |
| `/api/result/{job_id}` | GET | Get job status & video URL |
| `/` | GET | Health check |
| `/docs` | GET | Interactive API documentation |

## 🌐 Deployment

### Backend → Google Cloud Run

```bash
cd kapsule-studio-api

gcloud builds submit --tag gcr.io/gen-lang-client-0915852466/kapsule-studio-api

gcloud run deploy kapsule-studio-api \
  --image gcr.io/gen-lang-client-0915852466/kapsule-studio-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 900
```

### Frontend → Vercel/Netlify

```bash
cd kapsule-studio-frontend

# Update .env with production API URL
echo "VITE_API_URL=https://your-api.run.app" > .env

npm run build
# Deploy dist/ folder to your hosting provider
```

## 🔐 GCP Prerequisites Checklist

- ✅ GCP Project: `gen-lang-client-0915852466`
- ✅ Cloud Storage Bucket: `kapsule-stitch-public`
  - ✅ `/audio/` folder for uploads
  - ✅ `/video/` folder for final videos
  - ✅ Public access configured
- ✅ Firestore Database enabled
  - ✅ `jobs` collection (auto-created)
- ✅ Vertex AI API enabled
  - ✅ Veo 3.0 model access (`veo-3.0-generate-001`)
- ✅ Authentication configured
  - ✅ Service Account with proper roles
  - ✅ Application Default Credentials setup

## 🛠️ Development Tools

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000

# Upload audio
curl -X POST http://localhost:8000/api/upload-audio \
  -F "file=@/path/to/song.mp3"

# Start generation
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"genre":"Pop","duration":"8s",...}'

# Check status
curl http://localhost:8000/api/result/{job_id}
```

### View Logs

```bash
# Backend logs (during development)
# Logs appear in terminal where uvicorn is running

# Cloud Run logs (production)
gcloud run logs read kapsule-studio-api --region us-central1
```

## 📊 Expected Performance

| Operation | Duration |
|-----------|----------|
| Audio Upload | 2-5 seconds |
| Job Creation | < 1 second |
| Veo Generation (8s video) | 2-3 minutes |
| Veo Generation (15s video) | 3-5 minutes |
| FFmpeg Merge | 5-10 seconds |
| Total Workflow | 2-6 minutes |

## ❓ Troubleshooting

### "Requested entity was not found"
→ Vertex AI API not enabled or Veo model not accessible  
→ Run: `gcloud services enable aiplatform.googleapis.com`

### CORS Errors
→ Check `FRONTEND_URL` in backend `.env` matches your frontend URL  
→ Restart backend after changing CORS settings

### FFmpeg Errors
→ Install FFmpeg: `brew install ffmpeg` (Mac) or `apt install ffmpeg` (Linux)

### GCS Upload Fails
→ Check service account has `Storage Admin` role  
→ Verify bucket name in `.env` is correct

### Video Won't Play
→ Signed URLs expire after 1 hour  
→ Generate new video or refresh the status endpoint

## 🎉 Success Indicators

✅ Backend API docs load at `http://localhost:8000/docs`  
✅ Frontend loads at `http://localhost:5173`  
✅ Can upload an audio file successfully  
✅ Generate button becomes enabled after upload  
✅ Job status polls and shows "processing"  
✅ Video appears and plays after 2-5 minutes  
✅ Download button opens video in new tab

## 📞 Next Steps

1. Test the complete flow locally
2. Deploy backend to Cloud Run
3. Deploy frontend to hosting provider
4. Update CORS and API URL settings
5. Test production deployment
6. Share with users!

---

**Built with**: FastAPI, React, TypeScript, Google Veo 3.0, Cloud Storage, Firestore, FFmpeg

