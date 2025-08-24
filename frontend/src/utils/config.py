"""
Configuration management for the application
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ThemeConfig:
    """Theme configuration"""
    name: str
    primary_color: str
    secondary_color: str
    background_color: str
    surface_color: str
    text_color: str
    accent_color: str
    border_color: str
    shadow_color: str

@dataclass
class LanguageConfig:
    """Language configuration"""
    code: str
    name: str
    native_name: str
    flag: str

class Config:
    """Application configuration manager"""
    
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "app_config.json"
        self.default_config = self._get_default_config()
        self.config = self._load_config()
    
    def _get_config_dir(self) -> Path:
        """Get configuration directory based on OS"""
        if os.name == 'nt':  # Windows
            config_dir = Path.home() / "AppData" / "Local" / "MultiAPIDriveManager"
        elif os.name == 'posix':  # macOS/Linux
            config_dir = Path.home() / ".config" / "MultiAPIDriveManager"
        else:
            config_dir = Path.home() / ".MultiAPIDriveManager"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "language": "en",
            "theme": "dark",
            "backend_url": "http://localhost:3000",
            "auto_refresh_interval": 30,
            "search_history_limit": 50,
            "file_preview_enabled": True,
            "notifications_enabled": True,
            "startup_minimize": False,
            "window_size": {"width": 1200, "height": 800},
            "sidebar_width": 300,
            "recent_searches": [],
            "favorite_folders": []
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with default config to ensure all keys exist
                    return {**self.default_config, **config}
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.default_config.copy()
        else:
            # Create default config file
            self._save_config(self.default_config)
            return self.default_config.copy()
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
        self._save_config(self.config)
    
    def get_language(self) -> str:
        """Get current language code"""
        return self.get("language", "en")
    
    def set_language(self, language: str):
        """Set language"""
        self.set("language", language)
    
    def get_theme(self) -> str:
        """Get current theme"""
        return self.get("theme", "dark")
    
    def set_theme(self, theme: str):
        """Set theme"""
        self.set("theme", theme)
    
    def get_backend_url(self) -> str:
        """Get backend URL"""
        return self.get("backend_url", "http://localhost:3000")
    
    def get_window_size(self) -> Dict[str, int]:
        """Get window size"""
        return self.get("window_size", {"width": 1200, "height": 800})
    
    def set_window_size(self, width: int, height: int):
        """Set window size"""
        self.set("window_size", {"width": width, "height": height})
    
    def get_sidebar_width(self) -> int:
        """Get sidebar width"""
        return self.get("sidebar_width", 300)
    
    def set_sidebar_width(self, width: int):
        """Set sidebar width"""
        self.set("sidebar_width", width)
    
    def add_recent_search(self, query: str):
        """Add search to recent searches"""
        recent = self.get("recent_searches", [])
        if query in recent:
            recent.remove(query)
        recent.insert(0, query)
        recent = recent[:self.get("search_history_limit", 50)]
        self.set("recent_searches", recent)
    
    def get_recent_searches(self) -> list:
        """Get recent searches"""
        return self.get("recent_searches", [])
    
    def clear_recent_searches(self):
        """Clear recent searches"""
        self.set("recent_searches", [])
    
    def add_favorite_folder(self, folder_id: str, name: str, account: str):
        """Add folder to favorites"""
        favorites = self.get("favorite_folders", [])
        # Remove if already exists
        favorites = [f for f in favorites if f.get("id") != folder_id]
        favorites.append({
            "id": folder_id,
            "name": name,
            "account": account,
            "added_at": str(Path().cwd())
        })
        self.set("favorite_folders", favorites)
    
    def get_favorite_folders(self) -> list:
        """Get favorite folders"""
        return self.get("favorite_folders", [])
    
    def remove_favorite_folder(self, folder_id: str):
        """Remove folder from favorites"""
        favorites = self.get("favorite_folders", [])
        favorites = [f for f in favorites if f.get("id") != folder_id]
        self.set("favorite_folders", favorites)

# Global configuration instance
config = Config()

# Available themes
THEMES = {
    "dark": ThemeConfig(
        name="Dark",
        primary_color="#6366f1",
        secondary_color="#8b5cf6",
        background_color="#0f172a",
        surface_color="#1e293b",
        text_color="#f8fafc",
        accent_color="#06b6d4",
        border_color="#334155",
        shadow_color="#00000040"
    ),
    "light": ThemeConfig(
        name="Light",
        primary_color="#3b82f6",
        secondary_color="#6366f1",
        background_color="#ffffff",
        surface_color="#f8fafc",
        text_color="#0f172a",
        accent_color="#0891b2",
        border_color="#e2e8f0",
        shadow_color="#00000020"
    ),
    "midnight": ThemeConfig(
        name="Midnight",
        primary_color="#8b5cf6",
        secondary_color="#ec4899",
        background_color="#0a0a0a",
        surface_color="#1a1a1a",
        text_color="#ffffff",
        accent_color="#f59e0b",
        border_color="#2a2a2a",
        shadow_color="#00000060"
    ),
    "ocean": ThemeConfig(
        name="Ocean",
        primary_color="#0891b2",
        secondary_color="#0ea5e9",
        background_color="#0c4a6e",
        surface_color="#0e7490",
        text_color="#f0f9ff",
        accent_color="#22d3ee",
        border_color="#0369a1",
        shadow_color="#00000040"
    )
}

# Available languages
LANGUAGES = {
    "en": LanguageConfig(
        code="en",
        name="English",
        native_name="English",
        flag="🇺🇸"
    ),
    "vi": LanguageConfig(
        code="vi",
        name="Vietnamese",
        native_name="Tiếng Việt",
        flag="🇻🇳"
    )
}
