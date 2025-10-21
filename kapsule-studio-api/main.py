import logging
import os
from uuid import uuid4
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import config
from services.storage_service import StorageService
from services.firestore_service import FirestoreService
from services.veo_service import VeoService
from services.prompt_enhancer import build_enhanced_prompt
from services.gemini_service import GeminiService
from utils.video_utils import merge_audio_video, cleanup_temp_files

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Kapsule Studio API",
    description="API for generating music videos using Google Veo 3.0",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Initialize services
storage_service = StorageService()
firestore_service = FirestoreService()
veo_service = VeoService()
gemini_service = GeminiService()


# Request/Response Models
class GenerateRequest(BaseModel):
    """
    Request model for video generation.
    
    Supports two formats:
    1. Direct prompt: Provide 'prompt' field with custom text
    2. Structured options: Omit 'prompt', backend builds enhanced prompt
    """
    genre: str
    visualStyle: str
    cameraMovement: str
    mood: str
    subject: str
    setting: str
    lighting: str
    cameraType: str
    duration: str
    creativeIntensity: str
    extra: str
    audio_url: str
    prompt: Optional[str] = None  # Optional: if not provided, built from options


class AudioUploadResponse(BaseModel):
    """Response model for audio upload."""
    audio_url: str


class GenerateResponse(BaseModel):
    """Response model for generate endpoint."""
    job_id: str


class PromptPreviewRequest(BaseModel):
    """Request for prompt preview (same as GenerateRequest without audio)."""
    genre: str
    visualStyle: str
    cameraMovement: str
    mood: str
    subject: str
    setting: str
    lighting: str
    cameraType: str
    duration: str
    creativeIntensity: str
    extra: str
    force_gemini: Optional[bool] = False  # Force Gemini enhancement even if disabled in config


class PromptPreviewResponse(BaseModel):
    enhanced_prompt: str
    source: str  # 'gemini' | 'rule_fallback'


class JobStatusResponse(BaseModel):
    """Response model for job status."""
    status: str
    video_url: Optional[str] = None
    error: Optional[str] = None


# Background task for video generation workflow
async def process_video_generation(job_id: str, request_data: dict):
    """
    Background task that handles the complete video generation workflow.
    
    Steps:
    1. Update job status to "processing"
    2. Generate video with Veo
    3. Download audio from GCS
    4. Merge video and audio with FFmpeg
    5. Upload final video to GCS
    6. Update job status to "complete" with video URL
    """
    temp_files = []
    
    try:
        logger.info(f"[Job {job_id}] Starting video generation workflow")
        
        # Step 1: Update status to processing
        firestore_service.update_job_status(job_id, "processing")
        
        # Step 2: Generate video with Veo
        logger.info(f"[Job {job_id}] Calling Veo service...")
        veo_video_path = veo_service.generate_video(
            prompt=request_data["prompt"],
            duration=request_data["duration"],
            job_id=job_id
        )
        temp_files.append(veo_video_path)
        
        # Step 3: Download audio from GCS
        logger.info(f"[Job {job_id}] Downloading audio from GCS...")
        audio_path = f"/tmp/audio_{job_id}.mp3"
        storage_service.download_file(request_data["audio_url"], audio_path)
        temp_files.append(audio_path)
        
        # Step 4: Merge video and audio
        logger.info(f"[Job {job_id}] Merging video and audio with FFmpeg...")
        final_video_path = f"/tmp/final_{job_id}.mp4"
        merge_success = merge_audio_video(veo_video_path, audio_path, final_video_path)
        
        if not merge_success:
            raise Exception("Failed to merge video and audio")
        
        temp_files.append(final_video_path)
        
        # Step 5: Upload final video to GCS
        logger.info(f"[Job {job_id}] Uploading final video to GCS...")
        final_filename = f"final_{job_id}.mp4"
        video_gcs_uri = storage_service.upload_video(final_video_path, final_filename)
        
        # Step 6: Generate signed URL
        logger.info(f"[Job {job_id}] Generating signed URL...")
        video_url = storage_service.get_signed_url(video_gcs_uri, expiration=3600)
        
        # Step 7: Update job status to complete
        firestore_service.update_job_status(
            job_id,
            "complete",
            video_url=video_url
        )
        
        logger.info(f"[Job {job_id}] Video generation workflow completed successfully!")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[Job {job_id}] Workflow failed: {error_msg}", exc_info=True)
        
        # Update job status to error
        firestore_service.update_job_status(
            job_id,
            "error",
            error=error_msg
        )
    
    finally:
        # Clean up temporary files
        logger.info(f"[Job {job_id}] Cleaning up temporary files...")
        cleanup_temp_files(*temp_files)


# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Kapsule Studio API",
        "version": "1.0.0"
    }


# Simple in-memory rate limit for preview (per-process, per-IP)
_preview_hits = {}


@app.post("/api/prompt/preview", response_model=PromptPreviewResponse)
async def preview_prompt(request: PromptPreviewRequest, x_forwarded_for: Optional[str] = None):
    # Rate limit: 20/min per IP
    from time import time
    now = int(time())
    window = now // 60
    ip = (x_forwarded_for or "local").split(",")[0].strip()
    key = f"{ip}:{window}"
    _preview_hits[key] = _preview_hits.get(key, 0) + 1
    if _preview_hits[key] > 20:
        raise HTTPException(status_code=429, detail="Too many preview requests. Please wait a minute and try again.")

    # Build base prompt using our rule-based builder
    base_prompt = build_enhanced_prompt(
        genre=request.genre,
        mood=request.mood,
        visual_style=request.visualStyle,
        camera_movement=request.cameraMovement,
        duration=request.duration,
        lighting=request.lighting,
        camera_type=request.cameraType,
        creative_intensity=request.creativeIntensity,
        subject=request.subject,
        setting=request.setting,
        extra=request.extra
    )

    # Optionally call Gemini enhancer (if enabled in config OR force_gemini is True)
    if config.USE_GEMINI_PROMPT_ENHANCER or request.force_gemini:
        try:
            logger.info(f"Calling Gemini enhancer (force_gemini={request.force_gemini}, model={config.GEMINI_MODEL})")
            options = request.model_dump()
            enhanced = gemini_service.enhance(base_prompt, options)
            if enhanced:
                logger.info(f"Gemini enhancement successful, length={len(enhanced)}")
                return PromptPreviewResponse(enhanced_prompt=enhanced, source="gemini")
            else:
                logger.warning("Gemini returned None/empty response")
        except Exception as e:
            logger.error(f"Gemini preview failed with exception: {e}", exc_info=True)

    return PromptPreviewResponse(enhanced_prompt=base_prompt, source="rule_fallback")


@app.post("/api/upload-audio", response_model=AudioUploadResponse)
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload an audio segment to Google Cloud Storage.
    
    The frontend extracts the 15-second segment before uploading,
    so this endpoint just receives and stores the pre-extracted audio.
    Validates file type and size, then uploads to GCS audio folder.
    Returns the GCS URI of the uploaded file.
    """
    try:
        # Validate file type (accept WAV since frontend extracts to WAV)
        allowed_types = config.ALLOWED_AUDIO_TYPES + ["audio/wav", "audio/x-wav"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Read file contents to check size
        file_contents = await file.read()
        file_size = len(file_contents)
        
        logger.info(f"Uploading audio segment: {file.filename} ({file_size} bytes)")
        
        # Validate file size (should be small since it's only 15 seconds)
        if file_size > config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {config.MAX_FILE_SIZE / (1024*1024):.0f}MB"
            )
        
        # Upload to GCS
        from io import BytesIO
        file_obj = BytesIO(file_contents)
        audio_url = storage_service.upload_audio(file_obj, file.filename)
        
        logger.info(f"Successfully uploaded audio segment to: {audio_url}")
        
        return AudioUploadResponse(audio_url=audio_url)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading audio: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_video(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Start video generation job.
    
    Creates a job in Firestore and triggers background task for video generation.
    Returns the job ID for status polling.
    """
    try:
        logger.info(f"Received video generation request")
        logger.info(f"  Genre: {request.genre}, Duration: {request.duration}")
        logger.info(f"  Audio URL: {request.audio_url}")
        
        # Build enhanced prompt if not provided
        if not request.prompt:
            logger.info("No custom prompt provided, building enhanced prompt from options")
            enhanced_prompt = build_enhanced_prompt(
                genre=request.genre,
                mood=request.mood,
                visual_style=request.visualStyle,
                camera_movement=request.cameraMovement,
                duration=request.duration,
                lighting=request.lighting,
                camera_type=request.cameraType,
                creative_intensity=request.creativeIntensity,
                subject=request.subject,
                setting=request.setting,
                extra=request.extra
            )
            request.prompt = enhanced_prompt
            logger.info(f"  Enhanced Prompt: {enhanced_prompt[:150]}...")
        else:
            logger.info(f"  Using custom prompt: {request.prompt[:150]}...")
        
        # Create job in Firestore
        request_dict = request.model_dump()
        job_id = firestore_service.create_job(request_dict)
        
        logger.info(f"Created job: {job_id}")
        
        # Trigger background task
        background_tasks.add_task(process_video_generation, job_id, request_dict)
        
        return GenerateResponse(job_id=job_id)
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error creating generation job: {error_msg}", exc_info=True)
        
        # Check if it's a Veo API authentication error
        if "Requested entity was not found" in error_msg:
            raise HTTPException(
                status_code=500,
                detail="Requested entity was not found."
            )
        
        raise HTTPException(status_code=500, detail=f"Failed to create job: {error_msg}")


@app.get("/api/result/{job_id}", response_model=JobStatusResponse)
async def get_result(job_id: str):
    """
    Get the status of a video generation job.
    
    Returns job status: queued, processing, complete (with video URL), or error (with error message).
    """
    try:
        logger.info(f"Status check for job: {job_id}")
        
        # Get job from Firestore
        job_data = firestore_service.get_job(job_id)
        
        if not job_data:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
        
        status = job_data.get("status")
        
        # Build response based on status
        response = JobStatusResponse(status=status)
        
        if status == "complete":
            response.video_url = job_data.get("video_url")
        elif status == "error":
            response.error = job_data.get("error", "Unknown error occurred")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving job status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


# Run with: uvicorn main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.PORT)

