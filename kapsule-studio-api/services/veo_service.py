import logging
import time
import os
import requests
from google.auth import default
from google.auth.transport.requests import Request
from google.cloud import storage
import config

logger = logging.getLogger(__name__)


class VeoService:
    """Service for handling Google Veo 3.0 video generation via REST API."""
    
    def __init__(self):
        """Initialize credentials and API endpoint."""
        self.credentials, self.project_id = default()
        self.api_base = f"https://{config.VEO_LOCATION}-aiplatform.googleapis.com/v1"
        self.model_endpoint = f"{self.api_base}/projects/{config.GCP_PROJECT_ID}/locations/{config.VEO_LOCATION}/publishers/google/models/{config.VEO_MODEL}"
        logger.info(f"VeoService initialized with model: {config.VEO_MODEL}")
        logger.info(f"VeoService endpoint: {self.model_endpoint}")
    
    def _get_access_token(self) -> str:
        """Get a fresh access token."""
        if not self.credentials.valid:
            self.credentials.refresh(Request())
        return self.credentials.token
    
    def generate_video(self, prompt: str, duration: str, job_id: str) -> str:
        """
        Generate video using Veo 3.0 REST API.
        
        Args:
            prompt: Text prompt for video generation
            duration: Video duration ("8s" or "15s")
            job_id: Job ID for logging and temp file naming
            
        Returns:
            Local path to generated video file
        """
        logger.info(f"[Job {job_id}] Starting Veo video generation via REST API")
        logger.info(f"[Job {job_id}] Prompt: {prompt}")
        logger.info(f"[Job {job_id}] Duration: {duration}")
        
        try:
            # Parse duration to seconds
            duration_seconds = int(duration.replace("s", ""))
            
            # Step 1: Submit video generation request
            request_body = {
                "instances": [
                    {
                        "prompt": prompt
                    }
                ],
                "parameters": {
                    "durationSeconds": duration_seconds,
                    "storageUri": f"gs://{config.GCS_BUCKET_NAME}/veo-temp/",
                    "sampleCount": 1,
                    "aspectRatio": "9:16",  # Portrait mode for social media
                    "resolution": "720p",
                    "generateAudio": False  # We'll add our own audio
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self._get_access_token()}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"[Job {job_id}] Calling Veo API: {self.model_endpoint}:predictLongRunning")
            
            # Submit the request
            response = requests.post(
                f"{self.model_endpoint}:predictLongRunning",
                json=request_body,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                error_detail = response.json() if response.text else {"error": "Unknown error"}
                logger.error(f"[Job {job_id}] Veo API error: {response.status_code} - {error_detail}")
                raise Exception(f"Veo API request failed: {response.status_code} - {error_detail}")
            
            operation_data = response.json()
            operation_name = operation_data.get("name")
            
            if not operation_name:
                raise Exception("No operation name returned from Veo API")
            
            logger.info(f"[Job {job_id}] Veo operation started: {operation_name}")
            
            # Step 2: Poll for completion
            video_uri = self._poll_operation(operation_name, job_id)
            
            # Step 3: Download video from GCS
            temp_video_path = self._download_video_from_gcs(video_uri, job_id)
            
            logger.info(f"[Job {job_id}] Veo video downloaded to: {temp_video_path}")
            
            return temp_video_path
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[Job {job_id}] Veo API request failed: {str(e)}")
            raise Exception(f"Veo API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"[Job {job_id}] Veo generation failed: {str(e)}")
            raise
    
    def _poll_operation(self, operation_name: str, job_id: str, max_wait: int = 300) -> str:
        """
        Poll the Veo operation until completion.
        
        Args:
            operation_name: Full operation name from initial request
            job_id: Job ID for logging
            max_wait: Maximum seconds to wait (default 5 minutes)
            
        Returns:
            GCS URI of generated video
        """
        logger.info(f"[Job {job_id}] Polling operation status...")
        
        start_time = time.time()
        poll_interval = 10  # Poll every 10 seconds
        
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }
        
        # Extract model info from operation name for fetch endpoint
        # operation_name format: projects/PROJECT_ID/locations/LOCATION/publishers/google/models/MODEL_ID/operations/OPERATION_ID
        parts = operation_name.split("/")
        project_id = parts[1]
        location = parts[3]
        model_id = parts[7]
        operation_id = parts[9]
        
        fetch_url = f"{self.api_base}/projects/{project_id}/locations/{location}/publishers/google/models/{model_id}:fetchPredictOperation"
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.post(
                    fetch_url,
                    json={"operationName": operation_name},
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code != 200:
                    logger.warning(f"[Job {job_id}] Poll failed: {response.status_code}")
                    time.sleep(poll_interval)
                    continue
                
                result = response.json()
                
                # Check if operation is done
                if result.get("done"):
                    logger.info(f"[Job {job_id}] Veo operation completed!")
                    logger.info(f"[Job {job_id}] Full response: {result}")
                    
                    # Check for errors first
                    if "error" in result:
                        error_msg = result.get("error", {})
                        raise Exception(f"Veo operation failed: {error_msg}")
                    
                    # Extract video URI from response
                    response_data = result.get("response", {})
                    logger.info(f"[Job {job_id}] Response data keys: {response_data.keys()}")
                    
                    # Try different response structures
                    videos = response_data.get("videos", [])
                    
                    # Alternative: check for 'predictions' field
                    if not videos and "predictions" in response_data:
                        predictions = response_data.get("predictions", [])
                        if predictions and isinstance(predictions, list):
                            videos = predictions
                    
                    # Alternative: check for direct video data
                    if not videos and "video" in response_data:
                        videos = [response_data.get("video")]
                    
                    if not videos:
                        logger.error(f"[Job {job_id}] No videos found. Response structure: {response_data}")
                        raise Exception(f"No videos in completed operation response. Response keys: {list(response_data.keys())}")
                    
                    # Extract GCS URI
                    video_data = videos[0] if isinstance(videos, list) else videos
                    video_uri = video_data.get("gcsUri") or video_data.get("uri") or video_data.get("videoUri")
                    
                    if not video_uri:
                        logger.error(f"[Job {job_id}] No URI in video data. Video data: {video_data}")
                        raise Exception(f"No GCS URI in video response. Video data keys: {list(video_data.keys()) if isinstance(video_data, dict) else 'not a dict'}")
                    
                    logger.info(f"[Job {job_id}] Video generated at: {video_uri}")
                    return video_uri
                
                # Not done yet, continue polling
                logger.info(f"[Job {job_id}] Still processing... (elapsed: {int(time.time() - start_time)}s)")
                time.sleep(poll_interval)
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"[Job {job_id}] Poll request failed: {e}")
                time.sleep(poll_interval)
                continue
        
        raise Exception(f"Veo operation timed out after {max_wait} seconds")
    
    def _download_video_from_gcs(self, gcs_uri: str, job_id: str) -> str:
        """
        Download video from GCS to local temp file.
        
        Args:
            gcs_uri: GCS URI (gs://bucket/path)
            job_id: Job ID for naming
            
        Returns:
            Local path to downloaded video
        """
        logger.info(f"[Job {job_id}] Downloading video from: {gcs_uri}")
        
        # Parse GCS URI
        if not gcs_uri.startswith("gs://"):
            raise ValueError(f"Invalid GCS URI: {gcs_uri}")
        
        parts = gcs_uri.replace("gs://", "").split("/", 1)
        bucket_name = parts[0]
        blob_path = parts[1]
        
        # Download using GCS client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        temp_video_path = f"/tmp/veo_video_{job_id}.mp4"
        blob.download_to_filename(temp_video_path)
        
        logger.info(f"[Job {job_id}] Video downloaded to: {temp_video_path}")
        
        return temp_video_path

