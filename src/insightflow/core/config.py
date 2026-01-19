import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# 1. Load environment variables from .env file
load_dotenv()

class Settings:
    """
    Simple configuration loader using standard os.getenv.
    No validation magic, just works.
    """
    
    def __init__(self):
        # --- API Keys ---
        # Read raw string, split by comma, remove whitespace
        raw_free = os.getenv("GOOGLE_KEYS_FREE", "")
        self.GOOGLE_KEYS_FREE: List[str] = [k.strip() for k in raw_free.split(",") if k.strip()]
        
        raw_paid = os.getenv("GOOGLE_KEYS_PAID", "")
        self.GOOGLE_KEYS_PAID: List[str] = [k.strip() for k in raw_paid.split(",") if k.strip()]

        # Model Selection
        self.GOOGLE_MODEL = os.getenv("GOOGLE_MODEL")

        # --- Directories ---
        # Default to Downloads/InsightFlowInbox if not set
        default_inbox = Path.home() / "Downloads" / "InsightFlowInbox"
        env_inbox = os.getenv("INSIGHTFLOW_INBOX")
        self.INSIGHTFLOW_INBOX = Path(env_inbox) if env_inbox else default_inbox

        # Internal paths
        # We process files directly in Inbox, or use system temp for intermediate steps.
        # OUTPUT now defaults to INBOX to keep everything together.
        self.INSIGHTFLOW_OUTPUT = self.INSIGHTFLOW_INBOX
        
        # --- Logging ---
        self.LOG_DIR = Path(os.getenv("INSIGHTFLOW_LOG_DIR", "logs"))
        self.LOG_FILE = self.LOG_DIR / "insightflow.log"
        self.LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 512 * 1024))  # 0.5 MB
        self.LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 3))

        # --- Audio Processing ---
        self.AUDIO_BITRATE = os.getenv("INSIGHTFLOW_AUDIO_BITRATE", "64k")
        self.AUDIO_CHANNELS = os.getenv("INSIGHTFLOW_AUDIO_CHANNELS", "1")  # 1=Mono, 2=Stereo

# Create the singleton instance
settings = Settings()

# Optional: Print warning if no keys found (but don't crash)
if not settings.GOOGLE_KEYS_FREE and not settings.GOOGLE_KEYS_PAID:
    print("⚠️  WARNING: No Google API Keys found in .env. Analysis will fail.")