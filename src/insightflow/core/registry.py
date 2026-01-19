import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, Any
import datetime

logger = logging.getLogger(__name__)

class Registry:
    def __init__(self, registry_path: str = "data/registry.json"):
        # Resolve path relative to project root if it's relative
        # Assuming run from root, but we can make it robust
        self.path = Path(registry_path).resolve()
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Registry corrupted at {self.path}. Starting fresh.")
                self.data = {}
        else:
            self.data = {}

    def save(self):
        # Ensure directory exists
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def _compute_fast_hash(self, file_path: Path) -> str:
        """
        Computes a quick hash based on file size + first 8kb + last 8kb.
        Avoids reading full content of large files (O(1) complexity).
        """
        if not file_path.exists():
            return ""
        
        try:
            file_size = file_path.stat().st_size
            sha256 = hashlib.sha256()
            
            # Add file size to hash to distinguish empty/small files easily
            sha256.update(str(file_size).encode('utf-8'))

            with open(file_path, "rb") as f:
                # Read beginning
                chunk_start = f.read(8192)
                sha256.update(chunk_start)
                
                # Read end if file is large enough
                if file_size > 8192:
                    f.seek(max(0, file_size - 8192))
                    chunk_end = f.read(8192)
                    sha256.update(chunk_end)
                    
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error computing hash for {file_path}: {e}")
            return ""

    def is_processed(self, file_path: Path) -> bool:
        """Checks if a file has been successfully processed."""
        file_hash = self._compute_fast_hash(file_path)
        if not file_hash:
            return False
            
        record = self.data.get(file_hash)
        if record and record.get("status") == "completed":
            return True
        return False

    def register_start(self, file_path: Path):
        """Marks a file as currently processing."""
        file_hash = self._compute_fast_hash(file_path)
        if not file_hash:
             return None

        self.data[file_hash] = {
            "path": str(file_path),
            "status": "processing",
            "started_at": datetime.datetime.now().isoformat()
        }
        self.save()
        return file_hash

    def register_complete(self, file_path: Path, output_dir: Path) -> Path:
        """
        Marks processing as complete and renames the source file with [DONE] prefix.
        Returns the new path of the renamed file.
        """
        file_hash = self._compute_fast_hash(file_path)
        
        # Update registry
        if file_hash in self.data:
            self.data[file_hash]["status"] = "completed"
            self.data[file_hash]["output_dir"] = str(output_dir)
            self.data[file_hash]["completed_at"] = datetime.datetime.now().isoformat()
            self.save()
        
        # Rename file
        new_path = file_path
        try:
            if not file_path.name.startswith("[DONE] "):
                new_name = f"[DONE] {file_path.name}"
                new_path = file_path.with_name(new_name)
                file_path.rename(new_path)
                logger.info(f"Renamed source file to: {new_name}")
        except OSError as e:
            logger.error(f"Failed to rename file {file_path}: {e}")
            # Even if rename fails, the task is logically complete in registry
            
        return new_path
