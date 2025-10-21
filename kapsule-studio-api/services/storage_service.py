import logging
import uuid
import os
from typing import BinaryIO
import config

logger = logging.getLogger(__name__)


class StorageService:
    """Service for handling Google Cloud Storage operations."""
    
    def __init__(self):
        """Initialize GCS client."""
        try:
            from google.cloud import storage
            self.client = storage.Client(project=config.GCP_PROJECT_ID)
            self.bucket = self.client.bucket(config.GCS_BUCKET_NAME)
            logger.info(f"StorageService initialized with bucket: {config.GCS_BUCKET_NAME}")
        except Exception as e:
            logger.warning(f"StorageService initialization failed: {e}")
            logger.info("Running in mock mode for testing")
            self.client = None
            self.bucket = None
    
    def upload_audio(self, file: BinaryIO, original_filename: str) -> str:
        """
        Upload audio file to GCS audio folder.
        
        Args:
            file: File-like object to upload
            original_filename: Original filename from user
            
        Returns:
            GCS URI (gs://bucket/audio/filename)
        """
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        filename = f"{unique_id}_{original_filename}"
        blob_path = f"{config.AUDIO_FOLDER}{filename}"
        
        if self.client is None:
            # Mock mode - just return a mock URL
            gcs_uri = f"gs://{config.GCS_BUCKET_NAME}/{blob_path}"
            logger.info(f"MOCK: Would upload audio file to: {gcs_uri}")
            return gcs_uri
        
        blob = self.bucket.blob(blob_path)
        
        # Reset file pointer to beginning
        file.seek(0)
        
        # Upload file
        blob.upload_from_file(file)
        
        gcs_uri = f"gs://{config.GCS_BUCKET_NAME}/{blob_path}"
        logger.info(f"Uploaded audio file to: {gcs_uri}")
        
        return gcs_uri
    
    def upload_video(self, local_path: str, filename: str) -> str:
        """
        Upload video file to GCS video folder.
        
        Args:
            local_path: Local path to video file
            filename: Filename to use in GCS
            
        Returns:
            GCS URI (gs://bucket/video/filename)
        """
        blob_path = f"{config.VIDEO_FOLDER}{filename}"
        
        if self.client is None:
            # Mock mode - just return a mock URL
            gcs_uri = f"gs://{config.GCS_BUCKET_NAME}/{blob_path}"
            logger.info(f"MOCK: Would upload video file to: {gcs_uri}")
            return gcs_uri
        
        blob = self.bucket.blob(blob_path)
        
        # Upload file
        blob.upload_from_filename(local_path)
        
        gcs_uri = f"gs://{config.GCS_BUCKET_NAME}/{blob_path}"
        logger.info(f"Uploaded video file to: {gcs_uri}")
        
        return gcs_uri
    
    def download_file(self, gcs_url: str, local_path: str) -> None:
        """
        Download file from GCS to local filesystem.
        
        Args:
            gcs_url: GCS URI (gs://bucket/path/to/file)
            local_path: Local path where file should be saved
        """
        if self.client is None:
            # Mock mode - create a dummy file
            logger.info(f"MOCK: Would download {gcs_url} to {local_path}")
            with open(local_path, "wb") as f:
                f.write(b"mock audio data")
            return
        
        # Parse GCS URL
        if not gcs_url.startswith("gs://"):
            raise ValueError(f"Invalid GCS URL: {gcs_url}")
        
        # Extract bucket and blob path
        parts = gcs_url.replace("gs://", "").split("/", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid GCS URL format: {gcs_url}")
        
        bucket_name, blob_path = parts
        
        # Download file
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        blob.download_to_filename(local_path)
        
        logger.info(f"Downloaded {gcs_url} to {local_path}")
    
    def generate_signed_upload_url(self, filename: str, content_type: str) -> tuple:
        """
        Generate a signed URL for direct upload to GCS.
        
        Args:
            filename: Original filename
            content_type: MIME type of the file
            
        Returns:
            Tuple of (signed_upload_url, gcs_uri)
        """
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        safe_filename = f"{unique_id}_{filename}"
        blob_path = f"{config.AUDIO_FOLDER}{safe_filename}"
        
        if self.client is None:
            # Mock mode
            mock_url = f"https://storage.googleapis.com/{config.GCS_BUCKET_NAME}/{blob_path}"
            gcs_uri = f"gs://{config.GCS_BUCKET_NAME}/{blob_path}"
            logger.info(f"MOCK: Would generate signed upload URL for: {gcs_uri}")
            return mock_url, gcs_uri
        
        blob = self.bucket.blob(blob_path)
        
        # Generate signed URL for upload (PUT method)
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=900,  # 15 minutes
            method="PUT",
            content_type=content_type
        )
        
        gcs_uri = f"gs://{config.GCS_BUCKET_NAME}/{blob_path}"
        logger.info(f"Generated signed upload URL for: {gcs_uri}")
        
        return signed_url, gcs_uri
    
    def get_signed_url(self, gcs_url: str, expiration: int = 3600) -> str:
        """
        Generate a public URL for accessing a GCS object.
        
        Args:
            gcs_url: GCS URI (gs://bucket/path/to/file)
            expiration: URL expiration time in seconds (not used for public URLs)
            
        Returns:
            Publicly accessible URL
        """
        if self.client is None:
            # Mock mode - return a mock URL
            mock_url = f"https://storage.googleapis.com/{config.GCS_BUCKET_NAME}/video/mock_video.mp4"
            logger.info(f"MOCK: Would generate public URL: {mock_url}")
            return mock_url
        
        # Parse GCS URL
        if not gcs_url.startswith("gs://"):
            raise ValueError(f"Invalid GCS URL: {gcs_url}")
        
        # Extract bucket and blob path
        parts = gcs_url.replace("gs://", "").split("/", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid GCS URL format: {gcs_url}")
        
        bucket_name, blob_path = parts
        
        # Since the bucket has public access, use the public URL
        # This works with user credentials (no private key needed)
        public_url = f"https://storage.googleapis.com/{bucket_name}/{blob_path}"
        
        logger.info(f"Generated public URL for {blob_path}")
        
        return public_url

