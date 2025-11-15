import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any
import time

@dataclass
class AppConfig:
    root: Path
    cache: Path
    thumbs: Path
    metadata_cache: Path
    output: Path
    hls_dir: Path
    m3u_dir: Path
    json_dir: Path
    user_root: Path

class ConfigManager:
    def __init__(self):
        self.root = Path(__file__).parent
        self.setup_paths()
        self.setup_logging()
        self.metadata = self.load_metadata()
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_steps = 50

    def setup_paths(self):
        self.paths = AppConfig(
            root=self.root,
            cache=self.root / "cache",
            thumbs=self.root / "cache" / "thumbs",
            metadata_cache=self.root / "cache" / "metadata.json",
            output=self.root / "output",
            hls_dir=self.root / "output" / "hls",
            m3u_dir=self.root / "output" / "m3u",
            json_dir=self.root / "output" / "json",
            user_root=self.root / "user_data"
        )
        
        # Create all directories
        for path in asdict(self.paths).values():
            if isinstance(path, Path):
                path.mkdir(parents=True, exist_ok=True)

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.paths.cache / 'app.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_metadata(self) -> Dict[str, Any]:
        if self.paths.metadata_cache.exists():
            try:
                with open(self.paths.metadata_cache, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading metadata: {e}")
                return {}
        return {}

    def save_metadata(self):
        try:
            with open(self.paths.metadata_cache, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving metadata: {e}")

    def push_undo_state(self, action: str, data: Any):
        """Push current state to undo stack"""
        state = {
            'action': action,
            'timestamp': time.time(),
            'metadata': self.metadata.copy(),
            'data': data
        }
        self.undo_stack.append(state)
        
        # Limit stack size
        if len(self.undo_stack) > self.max_undo_steps:
            self.undo_stack.pop(0)
        
        # Clear redo stack when new action is performed
        self.redo_stack.clear()

    def undo(self):
        """Undo last action"""
        if not self.undo_stack:
            return None
        
        current_state = {
            'metadata': self.metadata.copy(),
            'timestamp': time.time()
        }
        
        last_state = self.undo_stack.pop()
        self.metadata = last_state['metadata']
        self.save_metadata()
        
        # Push current state to redo stack
        self.redo_stack.append(current_state)
        
        return last_state['action']

    def redo(self):
        """Redo last undone action"""
        if not self.redo_stack:
            return None
        
        current_state = {
            'metadata': self.metadata.copy(),
            'timestamp': time.time()
        }
        
        next_state = self.redo_stack.pop()
        self.metadata = next_state['metadata']
        self.save_metadata()
        
        # Push current state to undo stack
        self.undo_stack.append(current_state)
        
        return "Redo"

# Global config instance
config = ConfigManager()