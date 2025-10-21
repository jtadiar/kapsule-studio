import logging
from datetime import datetime
import config

logger = logging.getLogger(__name__)


class FirestoreService:
    """Service for handling Firestore job tracking operations."""
    
    def __init__(self):
        """Initialize Firestore client."""
        try:
            from google.cloud import firestore
            self.client = firestore.Client(project=config.GCP_PROJECT_ID)
            self.jobs_collection = self.client.collection(config.JOBS_COLLECTION)
            logger.info(f"FirestoreService initialized with collection: {config.JOBS_COLLECTION}")
        except Exception as e:
            logger.warning(f"FirestoreService initialization failed: {e}")
            logger.info("Running in mock mode for testing")
            self.client = None
            self.jobs_collection = None
            self._mock_jobs = {}  # In-memory storage for testing
    
    def create_job(self, request_data: dict) -> str:
        """
        Create a new job document in Firestore.
        
        Args:
            request_data: Dictionary containing job details (prompt, audio_url, etc.)
            
        Returns:
            Job ID (Firestore document ID)
        """
        job_data = {
            "status": "queued",
            "createdAt": datetime.utcnow(),
            "prompt": request_data.get("prompt"),
            "audio_url": request_data.get("audio_url"),
            "duration": request_data.get("duration"),
            "genre": request_data.get("genre"),
            "visualStyle": request_data.get("visualStyle"),
            "cameraMovement": request_data.get("cameraMovement"),
            "mood": request_data.get("mood"),
            "subject": request_data.get("subject"),
            "setting": request_data.get("setting"),
            "extra": request_data.get("extra", "")
        }
        
        if self.client is None:
            # Mock mode - use in-memory storage
            import uuid
            job_id = str(uuid.uuid4())
            self._mock_jobs[job_id] = job_data
            logger.info(f"MOCK: Created job: {job_id}")
            return job_id
        
        # Create document and get auto-generated ID
        _, doc_ref = self.jobs_collection.add(job_data)
        job_id = doc_ref.id
        
        logger.info(f"Created job: {job_id}")
        
        return job_id
    
    def update_job_status(
        self,
        job_id: str,
        status: str,
        video_url: str = None,
        error: str = None
    ) -> None:
        """
        Update job status and related fields.
        
        Args:
            job_id: Job ID to update
            status: New status (queued, processing, complete, error)
            video_url: Optional video URL for completed jobs
            error: Optional error message for failed jobs
        """
        if self.client is None:
            # Mock mode - update in-memory storage
            if job_id in self._mock_jobs:
                self._mock_jobs[job_id]["status"] = status
                self._mock_jobs[job_id]["updatedAt"] = datetime.utcnow()
                
                if status == "complete":
                    self._mock_jobs[job_id]["completedAt"] = datetime.utcnow()
                    if video_url:
                        self._mock_jobs[job_id]["video_url"] = video_url
                
                if status == "error" and error:
                    self._mock_jobs[job_id]["error"] = error
                    self._mock_jobs[job_id]["completedAt"] = datetime.utcnow()
                
                logger.info(f"MOCK: Updated job {job_id} to status: {status}")
            return
        
        doc_ref = self.jobs_collection.document(job_id)
        
        update_data = {
            "status": status,
            "updatedAt": datetime.utcnow()
        }
        
        # Add completion timestamp for completed jobs
        if status == "complete":
            update_data["completedAt"] = datetime.utcnow()
            if video_url:
                update_data["video_url"] = video_url
        
        # Add error message for failed jobs
        if status == "error" and error:
            update_data["error"] = error
            update_data["completedAt"] = datetime.utcnow()
        
        doc_ref.update(update_data)
        
        logger.info(f"Updated job {job_id} to status: {status}")
    
    def get_job(self, job_id: str) -> dict:
        """
        Retrieve job document by ID.
        
        Args:
            job_id: Job ID to retrieve
            
        Returns:
            Job data dictionary or None if not found
        """
        if self.client is None:
            # Mock mode - get from in-memory storage
            if job_id in self._mock_jobs:
                job_data = self._mock_jobs[job_id].copy()
                job_data["job_id"] = job_id
                logger.info(f"MOCK: Retrieved job: {job_id}, status: {job_data.get('status')}")
                return job_data
            else:
                logger.warning(f"MOCK: Job not found: {job_id}")
                return None
        
        doc_ref = self.jobs_collection.document(job_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            logger.warning(f"Job not found: {job_id}")
            return None
        
        job_data = doc.to_dict()
        job_data["job_id"] = job_id
        
        logger.info(f"Retrieved job: {job_id}, status: {job_data.get('status')}")
        
        return job_data

