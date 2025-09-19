#!/usr/bin/env python3
"""
Multi Driver Made With ♥️ By Truong Phuc - Python Frontend
Main application entry point
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QFont

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ui.main_window import MainWindow
from services.api_client import APIClient
from utils.config import config
from utils.i18n import i18n
from utils.theme_manager import theme_manager

class MainApp(QMainWindow):
    """Main application class"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize configuration
        self.config = config
        
        # Initialize API client
        self.api_client = APIClient(self.config.get_backend_url())
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
        
        # Check backend connection
        self.check_backend_connection()
        
        # Apply current theme
        theme_manager.apply_theme(config.get_theme())
    
    def setup_ui(self):
        """Setup the main UI"""
        # Set window title with i18n
        self.setWindowTitle(i18n.get("app_title"))
        
        # Set window size from config
        window_size = config.get_window_size()
        self.resize(window_size["width"], window_size["height"])
        self.setMinimumSize(1200, 800)
        
        # Set window icon using SVG logo
        from PySide6.QtSvg import QSvgRenderer
        from PySide6.QtGui import QPixmap, QPainter
        
        # Create application icon from SVG
        svg_path = Path(__file__).parent / "assets" / "icon.svg"
        if svg_path.exists():
            # Create QPixmap from SVG
            svg_renderer = QSvgRenderer(str(svg_path))
            if svg_renderer.isValid():
                # Create pixmap at 256x256 for high quality
                pixmap = QPixmap(256, 256)
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                svg_renderer.render(painter)
                painter.end()
                
                # Set as application icon
                self.setWindowIcon(QIcon(pixmap))
                print("✅ Application icon set successfully")
            else:
                print("❌ Failed to load SVG icon")
        else:
            print("❌ SVG icon file not found")
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create main window widget
        self.main_window = MainWindow(self.api_client)
        main_layout.addWidget(self.main_window)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Connect backend status signals
        self.main_window.backend_status_changed.connect(self.on_backend_status_changed)
        
        # Connect theme manager signals
        theme_manager.theme_changed.connect(self.on_theme_changed)
    
    def check_backend_connection(self):
        """Check if backend is accessible"""
        try:
            response = self.api_client.health_check()
            if response.get('success'):
                print("✅ Backend connected")
                self.main_window.set_backend_status(True)
            else:
                print("❌ Backend connection failed")
                self.main_window.set_backend_status(False)
        except Exception as e:
            print(f"❌ Backend error: {e}")
            self.main_window.set_backend_status(False)
    
    def on_backend_status_changed(self, is_connected):
        """Handle backend status changes"""
        if is_connected:
            self.setWindowTitle(f"{i18n.get('app_title')} - {i18n.get('connected')}")
        else:
            self.setWindowTitle(f"{i18n.get('app_title')} - {i18n.get('disconnected')}")
    
    def on_theme_changed(self, theme_name: str):
        """Handle theme changes"""
        print(f"🎨 Theme changed to: {theme_name}")
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Save window size
        size = self.size()
        config.set_window_size(size.width(), size.height())
        
        # Close main window
        self.main_window.close()
        
        event.accept()

def main():
    """Main application entry point"""
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName(i18n.get("app_title"))
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("MultiAPI Drive Manager")
    
    # Set application icon from SVG
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtGui import QPixmap, QPainter
    
    svg_path = Path(__file__).parent / "assets" / "icon.svg"
    if svg_path.exists():
        svg_renderer = QSvgRenderer(str(svg_path))
        if svg_renderer.isValid():
            # Create pixmap at 256x256 for high quality
            pixmap = QPixmap(256, 256)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            svg_renderer.render(painter)
            painter.end()
            
            # Set as application icon (for taskbar, etc.)
            app.setWindowIcon(QIcon(pixmap))
            print("✅ Application icon set for taskbar")
        else:
            print("❌ Failed to load SVG icon for application")
    else:
        print("❌ SVG icon file not found for application")
    
    # Set application style
    app.setStyle('Fusion')
    # Subtle global QComboBox arrow styling (keeps original sizing)
    app.setStyleSheet(app.styleSheet() + """
        QComboBox::drop-down { width: 20px; border-left: 1px solid #4a5568; background: #243042; }
        QComboBox::down-arrow {
            image: url('data:image/svg+xml;utf8,<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"12\" height=\"12\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"%23e2e8f0\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><polyline points=\"6 9 12 15 18 9\"/></svg>');
            width: 12px; height: 12px; margin-right: 4px;
        }
    """)
    
    # Set default font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    # Create and show main window
    main_window = MainApp()
    main_window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
