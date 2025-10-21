import logging
import json
import time
from typing import Dict, Optional

import requests
from google.auth import default
from google.auth.transport.requests import Request

import config

logger = logging.getLogger(__name__)


SYSTEM_INSTRUCTIONS = (
    "Act as a senior music-video creative director. Compose a single coherent cinematic prompt for a video generation model. "
    "Always enforce vertical 9:16 orientation. Never include on-screen text, watermarks, phone UIs, or logos. "
    "Guarantee professional music-video quality: cinematic composition, dynamic motion, realistic lens depth, and engaging transitions. "
    "Ensure the camera is always moving, tracking, cutting, or panning; avoid static frames. "
    "Output MUST be a single paragraph of plain text (no markdown)."
)


class GeminiService:
    def __init__(self) -> None:
        self.credentials, _ = default()
        self.api_base = f"https://{config.GEMINI_LOCATION}-aiplatform.googleapis.com/v1"
        self.model_endpoint = (
            f"{self.api_base}/projects/{config.GCP_PROJECT_ID}/locations/{config.GEMINI_LOCATION}/publishers/google/models/{config.GEMINI_MODEL}:generateContent"
        )
        logger.info("GeminiService initialized with model %s", config.GEMINI_MODEL)

    def _get_access_token(self) -> str:
        if not self.credentials.valid:
            self.credentials.refresh(Request())
        return self.credentials.token

    def enhance(self, base_prompt: str, options: Dict[str, str], timeout_s: int = 20) -> Optional[str]:
        """Call Gemini to enhance the prompt. Returns enhanced string or None on failure."""
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": SYSTEM_INSTRUCTIONS},
                        {"text": "Base prompt:"},
                        {"text": base_prompt},
                        {"text": "Options JSON:"},
                        {"text": json.dumps(options, ensure_ascii=False)},
                        {"text": "Compose a final cinematic prompt now (single paragraph)."},
                    ],
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(self.model_endpoint, json=payload, headers=headers, timeout=timeout_s)
            if resp.status_code != 200:
                logger.warning("Gemini enhancer error %s: %s", resp.status_code, resp.text[:500])
                return None

            data = resp.json()
            # Vertex response structure varies; support common forms
            candidates = data.get("candidates") or []
            if not candidates:
                return None
            parts = candidates[0].get("content", {}).get("parts", [])
            texts = [p.get("text", "") for p in parts if isinstance(p, dict)]
            result = " ".join(t for t in texts if t).strip()
            return result or None
        except requests.RequestException as e:
            logger.warning("Gemini enhancer request failed: %s", e)
            return None


