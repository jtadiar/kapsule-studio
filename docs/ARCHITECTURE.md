# Kapsule Studio Architecture

## System Overview

Kapsule Studio is a serverless AI music video generator deployed on Google Cloud Run.

## Architecture Diagram


![Architecture Diagram](https://raw.githubusercontent.com/jtadiar/kapsule-studio/main/architecture-diagram.png)


## Technology Stack

- **Netlify**: Frontend hosting with CDN
- **Cloud Run**: Serverless backend API deployment
- **Web Audio API**: Browser-side audio segment extraction
- **Veo 3.0**: AI video generation
- **Gemini 2.5 Flash**: Prompt enhancement
- **Cloud Storage**: Audio/video file storage
- **Firestore**: Job status tracking
- **FFmpeg**: Audio/video processing and looping
- **Secret Manager**: Secure configuration

## Data Flow

1. User uploads audio file (any size, e.g., 50MB+) in browser
2. User selects 15-second segment with interactive timeline
3. Frontend extracts segment using Web Audio API (~2-5MB)
4. Frontend uploads only the segment via `POST /api/upload-audio`
5. Backend stores segment in GCS
6. Backend generates enhanced prompt (optionally using Gemini 2.5)
7. Backend calls Veo 3.0 for 9:16 video generation
8. Backend downloads generated video from GCS
9. Backend merges and loops video with audio using FFmpeg
10. Backend uploads final video to GCS
11. Frontend polls for completion via `/api/result/{job_id}`
12. User downloads final video

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
