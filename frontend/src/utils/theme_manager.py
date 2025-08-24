"""
Theme management for the application
"""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal
from .config import THEMES, config

class ThemeManager(QObject):
    """Theme manager for the application"""
    
    theme_changed = Signal(str)  # Emitted when theme changes
    
    def __init__(self):
        super().__init__()
        self.current_theme = config.get_theme()
        # Don't apply theme immediately - wait for QApplication to exist
    
    def get_theme(self, theme_name: str) -> Optional[Dict[str, str]]:
        """Get theme configuration by name"""
        theme = THEMES.get(theme_name)
        if theme:
            return {
                "name": theme.name,
                "primary_color": theme.primary_color,
                "secondary_color": theme.secondary_color,
                "background_color": theme.background_color,
                "surface_color": theme.surface_color,
                "text_color": theme.text_color,
                "accent_color": theme.accent_color,
                "border_color": theme.border_color,
                "shadow_color": theme.shadow_color
            }
        return None
    
    def get_current_theme(self) -> str:
        """Get current theme name"""
        return self.current_theme
    
    def get_current_theme_config(self) -> Optional[Dict[str, str]]:
        """Get current theme configuration"""
        return self.get_theme(self.current_theme)
    
    def apply_theme(self, theme_name: str):
        """Apply theme to the application"""
        if theme_name not in THEMES:
            return
        
        self.current_theme = theme_name
        config.set_theme(theme_name)
        
        # Apply theme to QApplication only if it exists
        theme_config = self.get_theme(theme_name)
        if theme_config:
            self._apply_stylesheet(theme_config)
            self.theme_changed.emit(theme_name)
    
    def _apply_stylesheet(self, theme_config: Dict[str, str]):
        """Apply theme stylesheet to QApplication"""
        # Check if QApplication exists before applying stylesheet
        app = QApplication.instance()
        if app is not None:
            stylesheet = self._generate_stylesheet(theme_config)
            app.setStyleSheet(stylesheet)
    
    def _generate_stylesheet(self, theme_config: Dict[str, str]) -> str:
        """Generate QSS stylesheet from theme configuration"""
        return f"""
        /* Global Application Styles */
        QApplication {{
            background-color: {theme_config['background_color']};
            color: {theme_config['text_color']};
        }}
        
        /* Main Window */
        QMainWindow {{
            background-color: {theme_config['background_color']};
            color: {theme_config['text_color']};
        }}
        
        /* Widgets */
        QWidget {{
            background-color: {theme_config['background_color']};
            color: {theme_config['text_color']};
            border: none;
        }}
        
        /* Sidebar */
        QFrame#sidebar {{
            background-color: {theme_config['surface_color']};
            border-right: 1px solid {theme_config['border_color']};
        }}
        
        QLabel#sidebar-title {{
            color: {theme_config['primary_color']};
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {theme_config['primary_color']};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {theme_config['secondary_color']};
        }}
        
        QPushButton:pressed {{
            background-color: {theme_config['accent_color']};
        }}
        
        QPushButton:disabled {{
            background-color: {theme_config['border_color']};
            color: {theme_config['text_color']};
        }}
        
        /* Add Account Button */
        QPushButton#add-account-btn {{
            background-color: {theme_config['accent_color']};
            font-size: 14px;
            padding: 12px 20px;
        }}
        
        QPushButton#add-account-btn:hover {{
            background-color: {theme_config['secondary_color']};
        }}
        
        /* Input Fields */
        QLineEdit {{
            background-color: {theme_config['surface_color']};
            color: {theme_config['text_color']};
            border: 1px solid {theme_config['border_color']};
            border-radius: 4px;
            padding: 8px 12px;
        }}
        
        QLineEdit:focus {{
            border-color: {theme_config['primary_color']};
            outline: none;
        }}
        
        /* Combo Boxes */
        QComboBox {{
            background-color: {theme_config['surface_color']};
            color: {theme_config['text_color']};
            border: 1px solid {theme_config['border_color']};
            border-radius: 4px;
            padding: 8px 12px;
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {theme_config['text_color']};
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {theme_config['surface_color']};
            color: {theme_config['text_color']};
            border: 1px solid {theme_config['border_color']};
            selection-background-color: {theme_config['primary_color']};
        }}
        
        /* Checkboxes */
        QCheckBox {{
            color: {theme_config['text_color']};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {theme_config['border_color']};
            border-radius: 3px;
            background-color: {theme_config['surface_color']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {theme_config['primary_color']};
            border-color: {theme_config['primary_color']};
        }}
        
        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {theme_config['border_color']};
            background-color: {theme_config['background_color']};
        }}
        
        QTabBar::tab {{
            background-color: {theme_config['surface_color']};
            color: {theme_config['text_color']};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {theme_config['primary_color']};
            color: white;
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {theme_config['secondary_color']};
        }}
        
        /* Tables */
        QTableWidget {{
            background-color: {theme_config['surface_color']};
            alternate-background-color: {theme_config['background_color']};
            gridline-color: {theme_config['border_color']};
        }}
        
        QTableWidget::item {{
            padding: 8px;
            border: none;
        }}
        
        QTableWidget::item:selected {{
            background-color: {theme_config['primary_color']};
            color: white;
        }}
        
        QHeaderView::section {{
            background-color: {theme_config['surface_color']};
            color: {theme_config['text_color']};
            padding: 8px;
            border: none;
            border-bottom: 1px solid {theme_config['border_color']};
        }}
        
        /* Scrollbars */
        QScrollBar:vertical {{
            background-color: {theme_config['surface_color']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {theme_config['border_color']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {theme_config['primary_color']};
        }}
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        /* Status Bar */
        QStatusBar {{
            background-color: {theme_config['surface_color']};
            color: {theme_config['text_color']};
            border-top: 1px solid {theme_config['border_color']};
        }}
        
        QStatusBar QLabel {{
            padding: 4px 8px;
        }}
        
        /* Toolbar */
        QToolBar {{
            background-color: {theme_config['surface_color']};
            border: none;
            border-bottom: 1px solid {theme_config['border_color']};
            spacing: 8px;
            padding: 8px;
        }}
        
        /* Group Boxes */
        QGroupBox {{
            font-weight: bold;
            border: 1px solid {theme_config['border_color']};
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 8px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            color: {theme_config['primary_color']};
        }}
        
        /* Progress Bar */
        QProgressBar {{
            border: 1px solid {theme_config['border_color']};
            border-radius: 4px;
            text-align: center;
            background-color: {theme_config['surface_color']};
        }}
        
        QProgressBar::chunk {{
            background-color: {theme_config['primary_color']};
            border-radius: 3px;
        }}
        
        /* Message Boxes */
        QMessageBox {{
            background-color: {theme_config['surface_color']};
            color: {theme_config['text_color']};
        }}
        
        QMessageBox QPushButton {{
            min-width: 80px;
        }}
        
        /* Custom Account Item */
        QFrame.account-item {{
            background-color: {theme_config['surface_color']};
            border: 1px solid {theme_config['border_color']};
            border-radius: 6px;
            margin: 4px;
            padding: 8px;
        }}
        
        QFrame.account-item:hover {{
            border-color: {theme_config['primary_color']};
            background-color: {theme_config['background_color']};
        }}
        
        /* Account Status Indicators */
        QLabel.status-idle {{
            color: {theme_config['accent_color']};
        }}
        
        QLabel.status-crawling {{
            color: {theme_config['secondary_color']};
        }}
        
        QLabel.status-syncing {{
            color: {theme_config['primary_color']};
        }}
        
        QLabel.status-error {{
            color: #ef4444;
        }}
        
        /* Connection Status */
        QLabel.connected {{
            color: #10b981;
            font-weight: bold;
        }}
        
        QLabel.disconnected {{
            color: #ef4444;
            font-weight: bold;
        }}
        """
    
    def get_available_themes(self) -> Dict[str, str]:
        """Get available theme names"""
        return {code: theme.name for code, theme in THEMES.items()}
    
    def get_theme_preview_colors(self, theme_name: str) -> Dict[str, str]:
        """Get theme colors for preview"""
        theme = THEMES.get(theme_name)
        if theme:
            return {
                "primary": theme.primary_color,
                "secondary": theme.secondary_color,
                "background": theme.background_color,
                "surface": theme.surface_color,
                "text": theme.text_color,
                "accent": theme.accent_color
            }
        return {}

# Global theme manager instance
theme_manager = ThemeManager()
