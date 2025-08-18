"""Data persistence operations"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import shutil


class PersistenceHandler:
    """Handles file I/O operations for data management"""
    
    def __init__(self, data_dir: Path):
        """Initialize persistence handler
        
        Args:
            data_dir: Base directory for data storage
        """
        self.data_dir = data_dir
        self.history_file = data_dir / "history.json"
        self.settings_file = data_dir / "settings.json"
        
    def ensure_directories(self):
        """Ensure required directories exist"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        subdirs = ['profiles', 'reports', 'cache', 'logs']
        for subdir in subdirs:
            (self.data_dir / subdir).mkdir(exist_ok=True)
    
    def load_json(self, filepath: Path, default: Any = None) -> Any:
        """Safely load JSON file
        
        Args:
            filepath: Path to JSON file
            default: Default value if file doesn't exist
            
        Returns:
            Loaded data or default value
        """
        if not filepath.exists():
            return default
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            # Log error and return default
            print(f"Error loading {filepath}: {e}")
            return default
    
    def save_json(self, filepath: Path, data: Any, backup: bool = True):
        """Safely save JSON file
        
        Args:
            filepath: Path to JSON file
            data: Data to save
            backup: Whether to create backup before saving
        """
        try:
            # Create backup if requested
            if backup and filepath.exists():
                backup_path = filepath.with_suffix('.json.bak')
                shutil.copy2(filepath, backup_path)
            
            # Write to temporary file first
            temp_path = filepath.with_suffix('.json.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            # Move temp file to actual file
            temp_path.replace(filepath)
            
        except IOError as e:
            print(f"Error saving {filepath}: {e}")
            raise
    
    def load_history(self) -> Dict[str, Any]:
        """Load history data from file
        
        Returns:
            History data dictionary
        """
        default = {
            'version': '1.0',
            'entries': [],
            'last_updated': datetime.now().isoformat()
        }
        return self.load_json(self.history_file, default)
    
    def save_history(self, entries: List[Dict[str, Any]]):
        """Save history entries to file
        
        Args:
            entries: List of history entries
        """
        data = {
            'version': '1.0',
            'last_updated': datetime.now().isoformat(),
            'entries': entries
        }
        self.save_json(self.history_file, data)
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file
        
        Returns:
            Settings dictionary
        """
        return self.load_json(self.settings_file, {})
    
    def save_settings(self, settings: Dict[str, Any]):
        """Save settings to file
        
        Args:
            settings: Settings dictionary
        """
        self.save_json(self.settings_file, settings)