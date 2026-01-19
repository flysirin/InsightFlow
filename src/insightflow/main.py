import logging
import sys
import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from insightflow.core.config import settings
from insightflow.core.downloader import YTDownloader
from insightflow.core.ingestor import LocalIngestor
from insightflow.core.analyzer import AudioAnalyzer
from insightflow.core.registry import Registry

# Setup logging with Rotation
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)

file_handler = RotatingFileHandler(
    settings.LOG_FILE,
    maxBytes=settings.LOG_MAX_BYTES,
    backupCount=settings.LOG_BACKUP_COUNT,
    encoding="utf-8"
)
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, stream_handler]
)
logger = logging.getLogger("InsightFlow.App")

def save_result_in_inbox(source_original_path: Path, text_content: str):
    """Saves the MD file directly next to the source file."""
    # Logic: /Inbox/Video.mp4 -> /Inbox/Video.md
    
    clean_stem = source_original_path.stem.replace("[DONE] ", "").strip()
    # Ensure we use the Inbox path for output, or wherever the source is
    # In 'inbox' mode, source is in Inbox. In 'url' mode, source is in INPUT (which is now also staging).
    
    # If source is in Inbox, save there.
    # If source is elsewhere (e.g. YT download), save in configured Output/Inbox.
    parent_dir = source_original_path.parent
    
    report_path = parent_dir / f"{clean_stem}.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(text_content)
    
    logger.info(f"📝 Report saved: {report_path.name}")
    return report_path

def process_file_item(original_file: Path, ingestor: LocalIngestor, analyzer: AudioAnalyzer, registry: Registry):
    """
    Handles lifecycle of one item:
    1. Prepare (Get audio path, potentially temp)
    2. Analyze
    3. Save MD
    4. Cleanup Temp
    5. Mark Done
    """
    if registry.is_processed(original_file):
        logger.info(f"Skipping {original_file.name} (Already processed).")
        return

    logger.info(f"--- 🚀 Processing: {original_file.name} ---")
    registry.register_start(original_file)

    temp_audio_path = None
    is_temp = False

    try:
        # 1. Prepare Audio
        # This returns either the file itself (if audio) or a temp mp3 (if video)
        audio_path_to_upload, is_temp = ingestor.prepare_for_analysis(original_file)
        
        # 2. Analyze
        result_text = analyzer.analyze(audio_path_to_upload)

        if result_text:
            # 3. Save Report (Next to original)
            save_result_in_inbox(original_file, result_text)
            
            # 4. Finalize
            new_path = registry.register_complete(original_file, original_file.parent)
            logger.info(f"✅ Done! Renamed to: {new_path.name}")
        else:
            logger.warning("Analysis returned empty result.")

    except Exception as e:
        logger.error(f"❌ Processing failed for {original_file.name}: {e}")
    
    finally:
        # 5. Cleanup Temp
        if is_temp and temp_audio_path and temp_audio_path.exists():
            try:
                temp_audio_path.unlink()
                logger.debug("Cleaned up temporary audio file.")
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")
        
        # If we assigned it to a variable, clean it
        if is_temp and 'audio_path_to_upload' in locals() and audio_path_to_upload.exists():
             try:
                audio_path_to_upload.unlink()
             except: pass

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m insightflow.main <command>")
        return

    command = sys.argv[1].lower()
    registry = Registry()
    
    # Initialize Core Components
    try:
        analyzer = AudioAnalyzer()
    except Exception:
        logger.error("Failed to initialize Analyzer. Check keys.")
        return

    if command == "url":
        if len(sys.argv) < 3:
            logger.error("Missing URL.")
            return
        
        url = sys.argv[2]
        # For URL, we still need a place to put the download.
        # Let's put it in Inbox so the user sees it!
        download_dest = settings.INSIGHTFLOW_INBOX
        downloader = YTDownloader()
        
        logger.info(f"Downloading {url} to {download_dest}...")
        downloaded_file = downloader.download_audio(url, download_dest)
        
        if downloaded_file and downloaded_file.exists():
            # Process the specific file we just downloaded
            ingestor = LocalIngestor(inbox_path=settings.INSIGHTFLOW_INBOX)
            process_file_item(downloaded_file, ingestor, analyzer, registry)
        else:
            logger.warning("Download failed or file not found.")

    elif command == "inbox":
        ingestor = LocalIngestor(inbox_path=settings.INSIGHTFLOW_INBOX)
        files = ingestor.scan_inbox()
        
        if not files:
            logger.info("Inbox empty.")
            return

        logger.info(f"Found {len(files)} files.")
        for file in files:
            process_file_item(file, ingestor, analyzer, registry)

if __name__ == "__main__":
    main()