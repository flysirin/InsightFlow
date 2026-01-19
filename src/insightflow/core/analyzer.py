import time
import logging
import uuid
import mimetypes
import yaml
from pathlib import Path
from typing import Optional, List, TypeVar
from google import genai
from google.genai import types
from .config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")

class KeyExhaustedError(Exception):
    pass

class KeyManager:
    def __init__(self):
        self.free_keys = settings.GOOGLE_KEYS_FREE.copy()
        self.paid_keys = settings.GOOGLE_KEYS_PAID.copy()
        self.bad_keys = set()
        
    def get_next_key(self) -> Optional[str]:
        for key in self.free_keys:
            if key not in self.bad_keys: return key
        if self.bad_keys.issuperset(set(self.free_keys)):
            if self.free_keys and any(k not in self.bad_keys for k in self.paid_keys):
                 logger.info("Free tier keys exhausted. Switching to Paid tier.")
            for key in self.paid_keys:
                if key not in self.bad_keys: return key
        return None

    def mark_as_failed(self, key: str):
        if key:
            logger.warning(f"Marking API Key as exhausted/failed: ...{key[-4:]}")
            self.bad_keys.add(key)

class AudioAnalyzer:
    def __init__(self):
        self.key_manager = KeyManager()
        self.current_client: Optional[genai.Client] = None
        self.current_key: Optional[str] = None
        if not self._rotate_client():
            logger.warning("No valid API keys available on startup.")

    def _rotate_client(self) -> bool:
        new_key = self.key_manager.get_next_key()
        if not new_key: return False
        self.current_key = new_key
        try:
            self.current_client = genai.Client(api_key=new_key)
            logger.info(f"Switched to API Key ending in ...{new_key[-4:]}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize client: {e}")
            self.key_manager.mark_as_failed(new_key)
            return self._rotate_client()

    def _find_best_model(self) -> str:
        if settings.GOOGLE_MODEL:
            return settings.GOOGLE_MODEL
        try:
            all_models = list(self.current_client.models.list())
            priorities = [
                "gemini-2.0-flash-lite",
                "gemini-2.0-flash-lite-001",
                "gemini-2.0-flash",
                "gemini-2.5-flash",
                "gemini-1.5-flash"
            ]
            available_names = {m.name.replace("models/", "") for m in all_models}
            for p in priorities:
                if p in available_names: return p
            return "gemini-2.0-flash-lite"
        except Exception:
            return "gemini-2.0-flash-lite"

    def _load_prompt(self) -> str:
        """Loads the analysis prompt from prompts.yaml or falls back to default."""
        prompt_path = Path("prompts.yaml")
        if prompt_path.exists():
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and "default_prompt" in data:
                        return data["default_prompt"]
            except Exception as e:
                logger.warning(f"Failed to read prompts.yaml: {e}")
        return "Task 1: Transcript. Task 2: Summary. Keep original language."

    def _run_full_analysis_transaction(self, file_path: Path):
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            if file_path.suffix == '.mp3': mime_type = 'audio/mpeg'
            elif file_path.suffix == '.mp4': mime_type = 'video/mp4'
            else: mime_type = 'application/octet-stream'

        file_ref = None
        try:
            logger.info(f"Uploading {file_path.name}...")
            with open(file_path, "rb") as f:
                file_ref = self.current_client.files.upload(
                    file=f,
                    config=types.UploadFileConfig(display_name=file_path.name, mime_type=mime_type)
                )

            while file_ref.state.name == "PROCESSING":
                time.sleep(2)
                file_ref = self.current_client.files.get(name=file_ref.name)

            if file_ref.state.name != "ACTIVE":
                raise RuntimeError(f"File processing failed state: {file_ref.state.name}")

            model_name = self._find_best_model()
            prompt_text = self._load_prompt()
            
            logger.info(f"Requesting analysis from {model_name}...")
            response = self.current_client.models.generate_content(
                model=model_name,
                contents=[file_ref, prompt_text]
            )
            return response.text
        finally:
            if file_ref and self.current_client:
                try:
                    self.current_client.files.delete(name=file_ref.name)
                except Exception: pass

    def analyze(self, file_path: Path) -> str:
        while True:
            if not self.current_client:
                if not self._rotate_client(): raise KeyExhaustedError("All API keys exhausted.")
            try:
                return self._run_full_analysis_transaction(file_path)
            except Exception as e:
                error_str = str(e).lower()
                if any(x in error_str for x in ["429", "403", "exhausted", "quota"]):
                    logger.warning(f"Quota/Auth error: {e}")
                    self.key_manager.mark_as_failed(self.current_key)
                    self.current_client = None
                elif "disconnected" in error_str:
                    logger.warning(f"Network error: {e}. Retrying...")
                    time.sleep(2)
                else:
                    logger.error(f"Non-retriable error: {e}")
                    raise e
