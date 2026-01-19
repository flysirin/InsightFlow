import logging
import re
from pathlib import Path
from typing import Optional
import yt_dlp

logger = logging.getLogger(__name__)

# Ported from YTConverter/ytconverter/utils/sanitize.py
_BAD_CHARS = re.compile(r'[\\/*?:\"<>|]')

def sanitize_filename(name: str) -> str:
    """Removes characters that are invalid for filenames."""
    return _BAD_CHARS.sub("", name)

class YTDownloader:
    """
    Handles downloading audio from YouTube using yt-dlp library directly.
    Replaces the external 'YTConverter' process.
    """

    def __init__(self):
        pass

    def download_audio(self, url: str, output_dir: Path) -> Optional[Path]:
        """
        Downloads audio from URL, converts to MP3, and saves to output_dir.
        Returns the path to the downloaded file if successful, else None.
        """
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        # Configuration mostly matching 'headless.py' logic
        # We use a hook to get the final filename
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'logger': logger,
            'quiet': True,
            'no_warnings': True,
            # 'progress_hooks': [my_hook], # Could add progress later
            'restrictfilenames': True, # Helps with strict sanitization too
        }

        final_path = None

        try:
            logger.info(f"Starting download for: {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 1. Extract info to get the filename *before* or *during* download
                info = ydl.extract_info(url, download=True)
                
                # Determine the final filename
                # Note: 'ext' might be 'webm' in info, but postprocessor changes it to 'mp3'
                if info:
                    # If it was a playlist, 'entries' would exist. Assuming single video for now.
                    if 'entries' in info:
                        # Handle playlist if needed, for now just take first or warn
                        info = info['entries'][0]
                    
                    # Sanitize title to match what yt-dlp likely did (or rely on prepare_filename)
                    # Ideally, we ask ydl what the filename is.
                    filename = ydl.prepare_filename(info)
                    p = Path(filename)
                    # We know post-processor changes extension to .mp3
                    final_path = p.with_suffix(".mp3")
                    
                    logger.info(f"Download success: {final_path.name}")
                    return final_path
                
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Download failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during download: {e}", exc_info=True)

        return None
