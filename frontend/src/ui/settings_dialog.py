"""
Settings dialog for the application
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QPushButton, QComboBox, QCheckBox, QSpinBox,
    QGroupBox, QFormLayout, QSlider, QFrame, QScrollArea,
    QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QPalette

from utils.config import config, THEMES, LANGUAGES
from utils.i18n import i18n
from utils.theme_manager import theme_manager

class ThemePreviewWidget(QFrame):
    """Widget to preview theme colors"""
    
    def __init__(self, theme_name: str):
        super().__init__()
        self.theme_name = theme_name
        self.setFixedSize(120, 80)
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)
        
        # Get theme colors
        theme = THEMES.get(theme_name)
        if theme:
            self.colors = [
                theme.primary_color,
                theme.secondary_color,
                theme.accent_color,
                theme.surface_color,
                theme.background_color
            ]
        else:
            self.colors = ["#000000"] * 5
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw color bars
        bar_width = self.width() // len(self.colors)
        for i, color in enumerate(self.colors):
            painter.fillRect(
                i * bar_width, 0, bar_width, self.height(),
                QColor(color)
            )
        
        # Draw theme name
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(
            self.rect(), Qt.AlignCenter | Qt.AlignBottom,
            self.theme_name
        )

class SettingsDialog(QDialog):
    """Modern settings dialog"""
    
    settings_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_current_settings()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle(i18n.get("settings"))
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.tab_widget.addTab(self._create_appearance_tab(), i18n.get("appearance"))
        self.tab_widget.addTab(self._create_language_tab(), i18n.get("language"))
        self.tab_widget.addTab(self._create_general_tab(), "General")
        self.tab_widget.addTab(self._create_about_tab(), i18n.get("about"))
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton(i18n.get("cancel"))
        self.save_button = QPushButton(i18n.get("save"))
        self.save_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
    
    def _create_appearance_tab(self) -> QWidget:
        """Create appearance settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # Theme selection
        theme_group = QGroupBox("Theme Selection")
        theme_layout = QVBoxLayout(theme_group)
        
        # Theme grid
        theme_grid = QGridLayout()
        theme_grid.setSpacing(15)
        
        self.theme_buttons = {}
        row, col = 0, 0
        max_cols = 3
        
        for theme_code, theme in THEMES.items():
            # Theme preview
            preview = ThemePreviewWidget(theme_code)
            theme_grid.addWidget(preview, row, col)
            
            # Theme radio button
            theme_btn = QPushButton(theme.name)
            theme_btn.setCheckable(True)
            theme_btn.setProperty("theme_code", theme_code)
            theme_btn.clicked.connect(self._on_theme_selected)
            theme_grid.addWidget(theme_btn, row + 1, col)
            
            self.theme_buttons[theme_code] = theme_btn
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 2
        
        theme_layout.addLayout(theme_grid)
        layout.addWidget(theme_group)
        
        # Customization options
        custom_group = QGroupBox("Customization")
        custom_layout = QFormLayout(custom_group)
        
        self.auto_theme_checkbox = QCheckBox("Auto-detect system theme")
        self.compact_mode_checkbox = QCheckBox("Compact mode")
        self.show_animations_checkbox = QCheckBox("Show animations")
        
        custom_layout.addRow("Theme Mode:", self.auto_theme_checkbox)
        custom_layout.addRow("Display:", self.compact_mode_checkbox)
        custom_layout.addRow("Effects:", self.show_animations_checkbox)
        
        layout.addWidget(custom_group)
        layout.addStretch()
        
        return widget
    
    def _create_language_tab(self) -> QWidget:
        """Create language settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # Language selection
        lang_group = QGroupBox("Language Selection")
        lang_layout = QVBoxLayout(lang_group)
        
        # Current language info
        current_lang = i18n.get_current_language_info()
        if current_lang:
            current_info = QLabel(f"Current: {current_lang.flag} {current_lang.native_name}")
        else:
            current_info = QLabel("Current: Unknown")
        current_info.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        lang_layout.addWidget(current_info)
        
        # Language grid
        lang_grid = QGridLayout()
        lang_grid.setSpacing(15)
        
        self.language_buttons = {}
        row, col = 0, 0
        max_cols = 2
        
        for lang_code, lang in LANGUAGES.items():
            # Language button
            lang_btn = QPushButton(f"{lang.flag} {lang.native_name}")
            lang_btn.setCheckable(True)
            lang_btn.setProperty("lang_code", lang_code)
            lang_btn.clicked.connect(self._on_language_selected)
            lang_btn.setMinimumHeight(50)
            lang_btn.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 8px;
                }
                QPushButton:checked {
                    background-color: #3b82f6;
                    color: white;
                }
            """)
            
            lang_grid.addWidget(lang_btn, row, col)
            self.language_buttons[lang_code] = lang_btn
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        lang_layout.addLayout(lang_grid)
        layout.addWidget(lang_group)
        
        # Language features
        features_group = QGroupBox("Language Features")
        features_layout = QFormLayout(features_group)
        
        self.auto_translate_checkbox = QCheckBox("Auto-translate missing strings")
        self.show_original_checkbox = QCheckBox("Show original text on hover")
        
        features_layout.addRow("Translation:", self.auto_translate_checkbox)
        features_layout.addRow("Display:", self.show_original_checkbox)
        
        layout.addWidget(features_group)
        layout.addStretch()
        
        return widget
    
    def _create_general_tab(self) -> QWidget:
        """Create general settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # Interface settings
        interface_group = QGroupBox("Interface")
        interface_layout = QFormLayout(interface_group)
        
        self.startup_minimize_checkbox = QCheckBox("Start minimized")
        self.auto_refresh_spinbox = QSpinBox()
        self.auto_refresh_spinbox.setRange(10, 300)
        self.auto_refresh_spinbox.setSuffix(" seconds")
        
        interface_layout.addRow("Startup:", self.startup_minimize_checkbox)
        interface_layout.addRow("Auto-refresh:", self.auto_refresh_spinbox)
        
        layout.addWidget(interface_group)
        
        # Search settings
        search_group = QGroupBox("Search")
        search_layout = QFormLayout(search_group)
        
        self.search_history_limit_spinbox = QSpinBox()
        self.search_history_limit_spinbox.setRange(10, 200)
        self.search_history_limit_spinbox.setSuffix(" items")
        
        self.file_preview_checkbox = QCheckBox("Enable file previews")
        self.notifications_checkbox = QCheckBox("Show notifications")
        
        search_layout.addRow("History limit:", self.search_history_limit_spinbox)
        search_layout.addRow("Preview:", self.file_preview_checkbox)
        search_layout.addRow("Notifications:", self.notifications_checkbox)
        
        layout.addWidget(search_group)
        
        # Sidebar settings
        sidebar_group = QGroupBox("Sidebar")
        sidebar_layout = QFormLayout(sidebar_group)
        
        self.sidebar_width_slider = QSlider(Qt.Horizontal)
        self.sidebar_width_slider.setRange(200, 500)
        self.sidebar_width_slider.setSuffix(" px")
        
        sidebar_layout.addRow("Width:", self.sidebar_width_slider)
        
        layout.addWidget(sidebar_group)
        layout.addStretch()
        
        return widget
    
    def _create_about_tab(self) -> QWidget:
        """Create about tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # App info
        info_group = QGroupBox("Application Information")
        info_layout = QFormLayout(info_group)
        
        app_name = QLabel("Multi Driver Made With ♥️ By Truong Phuc")
        app_name.setStyleSheet("font-size: 18px; font-weight: bold; color: #3b82f6;")
        
        version = QLabel("Version 1.0.0")
        version.setStyleSheet("font-size: 14px; color: #6b7280;")
        
        description = QLabel("Advanced Google Drive management with multi-account support, powerful search, and intelligent sync capabilities.")
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 12px; line-height: 1.5;")
        
        info_layout.addRow("Name:", app_name)
        info_layout.addRow("Version:", version)
        info_layout.addRow("Description:", description)
        
        layout.addWidget(info_group)
        
        # Features
        features_group = QGroupBox("Key Features")
        features_layout = QVBoxLayout(features_group)
        
        features = [
            "🔐 Multi-account Google Drive management",
            "🔍 Advanced full-text search with filters",
            "🔄 Intelligent sync and backup",
            "📊 Comprehensive reports and analytics",
            "🎨 Modern, customizable interface",
            "🌍 Multi-language support",
            "🔒 Secure OAuth and Service Account support"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setStyleSheet("font-size: 12px; padding: 4px;")
            features_layout.addWidget(feature_label)
        
        layout.addWidget(features_group)
        
        # Credits
        credits_group = QGroupBox("Credits")
        credits_layout = QVBoxLayout(credits_group)
        
        credits_text = """
        Built with PySide6 and modern Python technologies.
        
        Icons and design inspired by Material Design principles.
        Google Drive API integration for seamless file management.
        """
        
        credits_label = QLabel(credits_text.strip())
        credits_label.setWordWrap(True)
        credits_label.setStyleSheet("font-size: 11px; color: #6b7280; line-height: 1.4;")
        
        credits_layout.addWidget(credits_label)
        layout.addWidget(credits_group)
        
        layout.addStretch()
        
        return widget
    
    def setup_connections(self):
        """Setup signal connections"""
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.save_settings)
        
        # Theme manager connection
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def load_current_settings(self):
        """Load current settings into UI"""
        # Theme
        current_theme = config.get_theme()
        if current_theme in self.theme_buttons:
            self.theme_buttons[current_theme].setChecked(True)
        
        # Language
        current_lang = config.get_language()
        if current_lang in self.language_buttons:
            self.language_buttons[current_lang].setChecked(True)
        
        # General settings
        self.startup_minimize_checkbox.setChecked(config.get("startup_minimize", False))
        self.auto_refresh_spinbox.setValue(config.get("auto_refresh_interval", 30))
        self.search_history_limit_spinbox.setValue(config.get("search_history_limit", 50))
        self.file_preview_checkbox.setChecked(config.get("file_preview_enabled", True))
        self.notifications_checkbox.setChecked(config.get("notifications_enabled", True))
        self.sidebar_width_slider.setValue(config.get_sidebar_width())
    
    def _on_theme_selected(self):
        """Handle theme selection"""
        sender = self.sender()
        theme_code = sender.property("theme_code")
        
        # Uncheck other buttons
        for btn in self.theme_buttons.values():
            if btn != sender:
                btn.setChecked(False)
        
        # Apply theme
        theme_manager.apply_theme(theme_code)
    
    def _on_language_selected(self):
        """Handle language selection"""
        sender = self.sender()
        lang_code = sender.property("lang_code")
        
        # Uncheck other buttons
        for btn in self.language_buttons.values():
            if btn != sender:
                btn.setChecked(False)
        
        # Set language
        i18n.set_language(lang_code)
        config.set_language(lang_code)
    
    def _on_theme_changed(self, theme_name: str):
        """Handle theme change from theme manager"""
        # Update button states
        for theme_code, btn in self.theme_buttons.items():
            btn.setChecked(theme_code == theme_name)
    
    def save_settings(self):
        """Save all settings"""
        # Save general settings
        config.set("startup_minimize", self.startup_minimize_checkbox.isChecked())
        config.set("auto_refresh_interval", self.auto_refresh_spinbox.value())
        config.set("search_history_limit", self.search_history_limit_spinbox.value())
        config.set("file_preview_enabled", self.file_preview_checkbox.isChecked())
        config.set("notifications_enabled", self.notifications_checkbox.isChecked())
        config.set_sidebar_width(self.sidebar_width_slider.value())
        
        # Emit signal
        self.settings_changed.emit()
        
        # Close dialog
        self.accept()
    
    def closeEvent(self, event):
        """Handle close event"""
        # Revert theme if not saved
        current_theme = config.get_theme()
        theme_manager.apply_theme(current_theme)
        event.accept()
