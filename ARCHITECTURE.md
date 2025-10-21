# Kapsule Studio Architecture

## System Overview

Kapsule Studio is a serverless AI music video generator deployed on Google Cloud Run.

## Architecture Diagram

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│  Netlify: Frontend (Static)     │
│  (React + Vite)                 │
│  studio.kapsule.co              │
└────────┬────────────────────────┘
         │ HTTP/REST
         ▼
┌─────────────────────────────────┐
│  Cloud Run: Backend API Service │
│  (FastAPI + Python + FFmpeg)    │
│  Port: 8080                     │
└─────┬───────┬───────┬──────────┘
      │       │       │
      ▼       ▼       ▼
   ┌────┐  ┌────┐  ┌────────┐
   │GCS │  │Veo │  │Firestore│
   └────┘  └────┘  └────────┘
      ▲
      │ Direct Upload (Signed URL)
      │
   ┌──────┐
   │ User │
   └──────┘
```

## Technology Stack

- **Netlify**: Frontend hosting with CDN
- **Cloud Run**: Serverless backend API deployment
- **Veo 3.0**: AI video generation
- **Gemini 2.5 Flash**: Prompt enhancement
- **Cloud Storage**: Audio/video file storage (with signed URL uploads)
- **Firestore**: Job status tracking
- **FFmpeg**: Audio/video processing
- **Secret Manager**: Secure configuration

## Data Flow

1. User uploads audio via frontend
2. Frontend sends to backend API
3. Backend stores audio in GCS
4. Backend generates enhanced prompt using Gemini
5. Backend calls Veo 3.0 for video generation
6. Backend downloads video from GCS
7. Backend merges audio + video with FFmpeg
8. Backend uploads final video to GCS
9. Frontend polls for completion
10. User downloads final video

## Security

- Secrets stored in Google Secret Manager
- No credentials in git repository
- Service accounts with minimal permissions
- Public bucket for video delivery only

## Deployment

Both frontend and backend are deployed as separate Cloud Run services:
- **Backend**: FastAPI application with FFmpeg
- **Frontend**: Static React app served by Nginx

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for deployment instructions.
