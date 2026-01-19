import logging
import shutil
import tempfile
from pathlib import Path
import subprocess
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

class LocalIngestor:
    """
    Scans a local 'Inbox' folder.
    - Audio files: Returns path directly.
    - Video files: Extracts audio to a temp file and returns that.
    """

    SUPPORTED_VIDEO = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    SUPPORTED_AUDIO = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}

    def __init__(self, inbox_path: Path):
        self.inbox_path = inbox_path
        if not self.inbox_path.exists():
            self.inbox_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created Inbox at: {self.inbox_path}")

    def scan_inbox(self) -> List[Path]:
        """Returns list of files in Inbox that are NOT marked as [DONE]."""
        files = []
        for p in self.inbox_path.iterdir():
            if p.is_file() and not p.name.startswith("[DONE]"):
                if p.suffix.lower() in self.SUPPORTED_VIDEO or p.suffix.lower() in self.SUPPORTED_AUDIO:
                    files.append(p)
        return files

    def prepare_for_analysis(self, file_path: Path) -> Tuple[Path, bool]:
        """
        Prepares a file for Gemini.
        Returns: (path_to_audio_file, is_temporary)
        - is_temporary=True means the caller should delete the file after use.
        """
        suffix = file_path.suffix.lower()

        # Case 1: Audio -> Use directly
        if suffix in self.SUPPORTED_AUDIO:
            logger.info(f"Audio detected: {file_path.name}. Using directly.")
            return file_path, False

        # Case 2: Video -> Extract Audio to Temp
        if suffix in self.SUPPORTED_VIDEO:
            return self._extract_audio_to_temp(file_path)
            
        raise ValueError(f"Unsupported format: {suffix}")

    def _extract_audio_to_temp(self, video_path: Path) -> Tuple[Path, bool]:
        """Extracts audio from video to a temporary MP3 file."""
        logger.info(f"Extracting audio from video: {video_path.name}...")
        
        # Create a temp file path
        fd, temp_path = tempfile.mkstemp(suffix=".mp3", prefix="insightflow_")
        # Close the file descriptor immediately, let ffmpeg open it
        import os
        os.close(fd)
        
        temp_audio_path = Path(temp_path)

        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vn",              # No video
            "-acodec", "libmp3lame",
            "-q:a", "4",        # VBR quality 4 (good balance)
            "-y",               # Overwrite
            str(temp_audio_path)
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Audio extracted to temp: {temp_audio_path}")
            return temp_audio_path, True
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed: {e}")
            # Clean up empty temp file if failed
            if temp_audio_path.exists():
                temp_audio_path.unlink()
            raise RuntimeError("Video processing failed.")