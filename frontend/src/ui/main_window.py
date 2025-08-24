"""
Main window UI component
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QLabel, QPushButton, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget, QProgressBar, QStatusBar, QMessageBox,
    QFrame, QScrollArea, QGroupBox, QCheckBox, QMenuBar,
    QMenu, QToolBar, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap, QAction

from ui.sidebar import Sidebar
from ui.toolbar import Toolbar
from ui.search_results import SearchResults
from ui.accounts_panel import AccountsPanel
from ui.reports_panel import ReportsPanel
from ui.settings_dialog import SettingsDialog

from utils.config import config
from utils.i18n import i18n
from utils.theme_manager import theme_manager

class MainWindow(QWidget):
    """Main window widget containing all UI components"""
    
    # Signals
    backend_status_changed = Signal(bool)
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.backend_connected = False
        self.health_check_failures = 0  # Track consecutive failures
        self.max_health_check_interval = 300000  # Max 5 minutes
        
        self.setup_ui()
        self.setup_connections()
        
        # Delay initial refresh to prevent startup API spam
        QTimer.singleShot(2000, self.refresh_accounts)  # Delay 2 seconds
        
        # Apply current theme
        theme_manager.apply_theme(config.get_theme())
    
    def setup_ui(self):
        """Setup the main UI layout"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create splitter for resizable sidebar
        splitter = QSplitter(Qt.Horizontal)
        
        # Left sidebar
        self.sidebar = Sidebar(self.api_client)
        splitter.addWidget(self.sidebar)
        
        # Right content area
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Toolbar
        self.toolbar = Toolbar()
        right_layout.addWidget(self.toolbar)
        
        # Content tabs
        self.content_tabs = QTabWidget()
        self.content_tabs.setTabPosition(QTabWidget.North)
        
        # Search results tab
        self.search_results = SearchResults(self.api_client)
        self.content_tabs.addTab(self.search_results, i18n.get("search_results"))
        
        # Accounts tab
        self.accounts_panel = AccountsPanel(self.api_client)
        self.content_tabs.addTab(self.accounts_panel, i18n.get("accounts"))
        
        # Reports tab
        self.reports_panel = ReportsPanel(self.api_client)
        self.content_tabs.addTab(self.reports_panel, i18n.get("reports"))
        
        right_layout.addWidget(self.content_tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        right_layout.addWidget(self.status_bar)
        
        splitter.addWidget(right_widget)
        
        # Set splitter proportions (sidebar:content = 1:4 thay vì 1:3)
        sidebar_width = min(config.get_sidebar_width(), 280)  # Giới hạn sidebar width tối đa 280px
        content_width = 1200 - sidebar_width
        splitter.setSizes([sidebar_width, content_width])
        
        main_layout.addWidget(splitter)
        
        # Setup status bar
        self.setup_status_bar()
        
        # Setup periodic refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.periodic_refresh)
        self.refresh_timer.start(config.get("auto_refresh_interval", 120) * 1000)  # Tăng từ 60s lên 120s
        
        # Setup health check timer
        self.health_timer = QTimer()
        self.health_timer.timeout.connect(self.check_backend_health)
        self.health_timer.start(60000)  # Tăng từ 30s lên 60s
    
    def create_menu_bar(self):
        """Create application menu bar"""
        # Create menu bar widget with enhanced styling
        menu_bar_widget = QFrame()
        menu_bar_widget.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #0f172a, stop:1 #1e293b);
                border-bottom: 2px solid #374151;
                border-radius: 0px;
            }
        """)
        # Menu bar layout
        menu_bar_layout = QHBoxLayout(menu_bar_widget)
        menu_bar_layout.setContentsMargins(15, 8, 15, 8)  # Giảm từ 20,15,20,15 xuống 15,8,15,8
        menu_bar_layout.setSpacing(12)  # Giảm từ 20 xuống 12
        
        # Title label
        title_label = QLabel(i18n.get("app_title"))
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #667eea, stop:1 #764ba2);
                border: 1px solid #4c63d2;
            }
        """)
        
        # Settings button
        settings_button = QPushButton("⚙️ " + i18n.get("settings"))
        settings_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: 1px solid #4c63d2;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                min-height: 28px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #5a6fd8, stop:1 #6a4190);
                border: 1px solid #3d52b8;
            }
        """)
        
        # Language combo
        language_combo = QComboBox()
        language_combo.addItem("🇺🇸 English", "en")
        language_combo.addItem("🇻🇳 Tiếng Việt", "vi")
        language_combo.setCurrentText("🇺🇸 English")
        language_combo.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: 1px solid #4c63d2;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                min-width: 120px;
                min-height: 28px;
            }
            QComboBox::drop-down {
                width: 20px;
                border: none;
            }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background: #2d3748;
                border: 1px solid #4c63d2;
                border-radius: 6px;
                selection-background-color: #667eea;
            }
        """)
        
        # Theme combo
        theme_combo = QComboBox()
        theme_combo.addItem("🌙 Dark", "dark")
        theme_combo.addItem("☀️ Light", "light")
        theme_combo.addItem("🌊 Ocean", "ocean")
        theme_combo.addItem("🌃 Midnight", "midnight")
        theme_combo.setCurrentText("🌙 Dark")
        theme_combo.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: 1px solid #4c63d2;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                min-width: 120px;
                min-height: 28px;
            }
            QComboBox::drop-down {
                width: 20px;
                border: none;
            }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background: #2d3748;
                border: 1px solid #4c63d2;
                border-radius: 6px;
                selection-background-color: #667eea;
            }
        """)
        
        # Add widgets to layout
        menu_bar_layout.addWidget(title_label)
        menu_bar_layout.addStretch()
        menu_bar_layout.addWidget(settings_button)
        menu_bar_layout.addWidget(language_combo)
        menu_bar_layout.addWidget(theme_combo)
        
        # Connect signals
        settings_button.clicked.connect(self.show_settings)
        language_combo.currentTextChanged.connect(self.on_language_changed)
        theme_combo.currentTextChanged.connect(self.on_theme_changed)
        
        # Store references
        self.settings_button = settings_button
        self.language_combo = language_combo
        self.theme_combo = theme_combo
    
    def setup_language_selector(self):
        """Setup language selector combo box"""
        current_lang = config.get_language()
        
        for lang_code, lang in i18n.get_supported_languages().items():
            self.language_combo.addItem(
                f"{lang.flag} {lang.native_name}", 
                lang_code
            )
            if lang_code == current_lang:
                self.language_combo.setCurrentIndex(self.language_combo.count() - 1)
        
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
    
    def setup_theme_selector(self):
        """Setup theme selector combo box"""
        current_theme = config.get_theme()
        
        for theme_code, theme in theme_manager.get_available_themes().items():
            self.theme_combo.addItem(theme, theme_code)
            if theme_code == current_theme:
                self.theme_combo.setCurrentIndex(self.theme_combo.count() - 1)
        
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Toolbar signals
        self.toolbar.search_requested.connect(self.on_search_requested)
        self.toolbar.filter_changed.connect(self.on_filter_changed)
        
        # Sidebar signals
        self.sidebar.account_selected.connect(self.on_account_selected)
        self.sidebar.sync_requested.connect(self.on_sync_requested)
        
        # Content signals
        self.search_results.file_selected.connect(self.on_file_selected)
        self.accounts_panel.account_updated.connect(self.refresh_accounts)
        
        # Theme manager signals
        theme_manager.theme_changed.connect(self.on_theme_changed)
    
    def setup_status_bar(self):
        """Setup status bar with connection indicator"""
        # Status bar styling
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #1a202c, stop:1 #2d3748);
                color: #e2e8f0;
                border-top: 1px solid #4a5568;
                font-size: 11px;
                padding: 4px;
            }
        """)
        
        # Connection status
        self.connection_label = QLabel("● Connected")
        self.connection_label.setStyleSheet("""
            QLabel {
                color: #48bb78;
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 4px;
                background: rgba(72, 187, 120, 0.1);
                font-size: 10px;
                min-width: 80px;
            }
        """)
        
        # Separator
        separator = QLabel("|")
        separator.setStyleSheet("""
            QLabel {
                color: #718096;
                margin: 0 4px;
                font-size: 10px;
            }
        """)
        
        # File count
        self.file_count_label = QLabel("Files: 0")
        self.file_count_label.setStyleSheet("""
            QLabel {
                color: #e2e8f0;
                padding: 2px 6px;
                border-radius: 4px;
                background: rgba(113, 128, 150, 0.1);
                font-size: 10px;
                min-width: 60px;
            }
        """)
        
        # Separator 2
        separator2 = QLabel("|")
        separator2.setStyleSheet("""
            QLabel {
                color: #718096;
                margin: 0 4px;
                font-size: 10px;
            }
        """)
        
        # Total size
        self.total_size_label = QLabel("Size: 0 B")
        self.total_size_label.setStyleSheet("""
            QLabel {
                color: #e2e8f0;
                padding: 2px 6px;
                border-radius: 4px;
                background: rgba(113, 128, 150, 0.1);
                font-size: 10px;
                min-width: 70px;
            }
        """)
        self.status_bar.addWidget(self.connection_label)
        
        # Enhanced separator
        separator = QLabel("|")
        separator.setStyleSheet("""
            color: #6366f1; 
            margin: 0 6px;
            font-weight: bold;
            font-size: 12px;
        """)
        self.status_bar.addWidget(separator)
        
        # File count with enhanced styling
        self.file_count_label = QLabel(f"{i18n.get('files')}: 0")
        self.file_count_label.setStyleSheet("""
            QLabel {
                color: #f3f4f6;
                padding: 6px 12px;
                background-color: #374151;
                border-radius: 6px;
                border: 1px solid #4b5563;
                font-weight: bold;
                min-width: 80px;
                text-align: center;
            }
        """)
        self.status_bar.addWidget(self.file_count_label)
        
        # Enhanced separator
        separator2 = QLabel("|")
        separator2.setStyleSheet("""
            color: #6366f1; 
            margin: 0 6px;
            font-weight: bold;
            font-size: 12px;
        """)
        self.status_bar.addWidget(separator2)
        
        # Total size with enhanced styling
        self.total_size_label = QLabel(f"{i18n.get('size')}: 0 B")
        self.total_size_label.setStyleSheet("""
            QLabel {
                color: #f3f4f6;
                padding: 6px 12px;
                background-color: #374151;
                border-radius: 6px;
                border: 1px solid #4b5563;
                font-weight: bold;
                min-width: 100px;
                text-align: center;
            }
        """)
        self.status_bar.addWidget(self.total_size_label)
        
        # Stretch to push everything to the left
        self.status_bar.addPermanentWidget(QLabel(""))
    
    def set_backend_status(self, is_connected: bool):
        """Update backend connection status"""
        self.backend_connected = is_connected
        
        if is_connected:
            self.connection_label.setText("● Connected")
            self.connection_label.setStyleSheet("""
                QLabel {
                    color: #48bb78;
                    font-weight: bold;
                    padding: 2px 6px;
                    border-radius: 4px;
                    background: rgba(72, 187, 120, 0.1);
                    font-size: 10px;
                    min-width: 80px;
                }
            """)
            self.backend_status_changed.emit(True)
        else:
            self.connection_label.setText("● Disconnected")
            self.connection_label.setStyleSheet("""
                QLabel {
                    color: #ef4444;
                    font-weight: bold;
                    padding: 2px 6px;
                    border-radius: 4px;
                    background: rgba(239, 68, 68, 0.1);
                    font-size: 10px;
                    min-width: 80px;
                }
            """)
            self.backend_status_changed.emit(False)
    
    def refresh_accounts(self):
        """Refresh accounts list in sidebar with rate limit handling"""
        try:
            response = self.api_client.get_accounts()
            if response.get('success'):
                accounts = response.get('accounts', [])
                self.sidebar.update_accounts(accounts)
                
                # Update status bar with total counts
                self.update_status_counts()
                
                # Set backend as connected
                self.set_backend_status(True)
                self.health_check_failures = 0  # Reset failures on success
            else:
                print(f"Failed to get accounts: {response.get('error')}")
                
                # Check if it's a rate limit error
                if response.get('rate_limited') or '429' in str(response.get('error', '')) or 'Too Many Requests' in str(response.get('error', '')):
                    print("Rate limit hit, will retry much later...")
                    # Schedule retry with much longer delay
                    QTimer.singleShot(120000, self.refresh_accounts)  # Retry in 2 minutes
                    return
                
                # Check if it's a connection error
                if 'connection failed' in response.get('error', '').lower():
                    self.set_backend_status(False)
                    self.health_check_failures += 1
                
        except Exception as e:
            print(f"Error refreshing accounts: {e}")
            self.set_backend_status(False)
            self.health_check_failures += 1
            
            # Schedule retry with exponential backoff, but cap it
            retry_delay = min(300000, 10000 * (2 ** min(self.health_check_failures, 4)))  # Max 5 minutes
            print(f"Scheduling retry in {retry_delay/1000:.0f} seconds")
            QTimer.singleShot(retry_delay, self.refresh_accounts)
    
    def update_status_counts(self):
        """Update status bar with file counts and sizes"""
        try:
            response = self.api_client.get_search_stats()
            if response.get('success'):
                stats = response.get('stats', {})
                totals = stats.get('totals', {})
                
                file_count = totals.get('total_files', 0) or 0
                total_size = totals.get('total_size', 0) or 0
                
                self.file_count_label.setText(f"{i18n.get('files')}: {file_count:,}")
                self.total_size_label.setText(f"{i18n.get('size')}: {self.format_size(total_size)}")
        except Exception as e:
            print(f"Error updating status counts: {e}")
    
    def format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def on_search_requested(self, query: str):
        """Handle search request from toolbar"""
        try:
            # Get current filters from toolbar
            filters = self.toolbar.get_current_filters()
            
            # Perform search
            response = self.api_client.search_files(query, **filters)
            
            if response.get('success'):
                data = response.get('data', {})
                files = data.get('files', [])
                pagination = data.get('pagination', {})
                
                # Update search results
                self.search_results.update_results(files, pagination)
                
                # Add to recent searches
                if query.strip():
                    config.add_recent_search(query)
                
                # Switch to search results tab
                self.content_tabs.setCurrentIndex(0)
                
                # Update status
                self.status_bar.showMessage(
                    i18n.get("search_found", count=len(files), query=query), 
                    3000
                )
            else:
                QMessageBox.warning(
                    self, 
                    i18n.get("search_failed"), 
                    f"{i18n.get('search_failed')}: {response.get('error')}"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                i18n.get("search_failed"), 
                f"{i18n.get('search_failed')}: {str(e)}"
            )
    
    def on_filter_changed(self, filters: dict):
        """Handle filter changes from toolbar"""
        # Re-run current search with new filters if there's an active search
        current_query = self.toolbar.get_current_query()
        if current_query:
            self.on_search_requested(current_query)
    
    def on_account_selected(self, account_key: str):
        """Handle account selection from sidebar"""
        # Update search results to show files from selected account
        try:
            response = self.api_client.search_files(owner=account_key)
            if response.get('success'):
                data = response.get('data', {})
                files = data.get('files', [])
                pagination = data.get('pagination', {})
                
                self.search_results.update_results(files, pagination)
                self.content_tabs.setCurrentIndex(0)
                
                # Update toolbar to show selected account
                self.toolbar.set_account_filter(account_key)
                
        except Exception as e:
            print(f"Error loading account files: {e}")
    
    def on_sync_requested(self, account_key: str, sync_type: str):
        """Handle sync request from sidebar"""
        try:
            if sync_type == 'initial':
                response = self.api_client.start_initial_crawl(account_key)
                message = i18n.get("sync_started", account=account_key)
            else:
                response = self.api_client.start_incremental_sync(account_key)
                message = i18n.get("sync_started", account=account_key)
            
            if response.get('success'):
                self.status_bar.showMessage(message, 3000)
                # Refresh accounts to update status
                QTimer.singleShot(2000, self.refresh_accounts)
            else:
                QMessageBox.warning(
                    self, 
                    i18n.get("sync_failed"), 
                    f"{i18n.get('sync_failed')}: {response.get('error')}"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                i18n.get("sync_failed"), 
                f"{i18n.get('sync_failed')}: {str(e)}"
            )
    
    def on_file_selected(self, file_id: str):
        """Handle file selection from search results"""
        # This could open a file details dialog or preview
        print(f"File selected: {file_id}")
    
    def on_language_changed(self, text: str):
        """Handle language change"""
        # Find the language code for the selected text
        for i in range(self.language_combo.count()):
            if self.language_combo.itemText(i) == text:
                lang_code = self.language_combo.itemData(i)
                i18n.set_language(lang_code)
                config.set_language(lang_code)
                self.refresh_ui_texts()
                break
    
    def on_theme_changed(self, theme_name: str):
        """Handle theme change"""
        # Update theme combo box if it exists
        if hasattr(self, 'theme_combo') and self.theme_combo:
            try:
                for i in range(self.theme_combo.count()):
                    if self.theme_combo.itemData(i) == theme_name:
                        self.theme_combo.setCurrentIndex(i)
                        break
            except RuntimeError:
                # Widget was deleted, ignore
                pass
    
    def refresh_ui_texts(self):
        """Refresh all UI texts after language change"""
        # Update window title
        if self.backend_connected:
            self.setWindowTitle(f"{i18n.get('app_title')} - {i18n.get('connected')}")
        else:
            self.setWindowTitle(f"{i18n.get('app_title')} - {i18n.get('disconnected')}")
        
        # Update tab texts
        self.content_tabs.setTabText(0, i18n.get("search_results"))
        self.content_tabs.setTabText(1, i18n.get("accounts"))
        self.content_tabs.setTabText(2, i18n.get("reports"))
        
        # Update status bar texts
        self.update_status_counts()
        
        # Update other UI components
        self.sidebar.refresh_texts()
        self.toolbar.refresh_texts()
        self.search_results.refresh_texts()
        self.accounts_panel.refresh_texts()
        self.reports_panel.refresh_texts()
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self.on_settings_changed)
        dialog.exec()
    
    def on_settings_changed(self):
        """Handle settings changes"""
        # Update refresh timer
        interval = config.get("auto_refresh_interval", 30) * 1000
        self.refresh_timer.setInterval(interval)
        
        # Update sidebar width
        sidebar_width = config.get_sidebar_width()
        splitter = self.findChild(QSplitter)
        if splitter:
            current_sizes = splitter.sizes()
            content_width = current_sizes[1] + (current_sizes[0] - sidebar_width)
            splitter.setSizes([sidebar_width, content_width])
        
        # Refresh UI
        self.refresh_ui_texts()
    
    def periodic_refresh(self):
        """Periodic refresh of data with rate limit checking"""
        if self.backend_connected and self.health_check_failures == 0:
            # Check if we're rate limited before making request
            if hasattr(self.api_client, 'is_rate_limited') and self.api_client.is_rate_limited():
                print("Skipping periodic refresh - rate limited")
                return
            
            # Only refresh if backend is healthy and we haven't had recent failures
            self.refresh_accounts()
        else:
            print("Skipping periodic refresh - backend not healthy")
    
    def check_backend_health(self):
        """Check backend health status"""
        try:
            response = self.api_client.health_check()
            if response.get('success'):
                self.set_backend_status(True)
                self.health_check_failures = 0 # Reset failures on success
            else:
                self.set_backend_status(False)
                self.health_check_failures += 1
                current_interval = min(self.max_health_check_interval, 
                                       self.health_timer.interval() * (2 ** self.health_check_failures))
                self.health_timer.setInterval(current_interval)
                print(f"Backend health check failed. Retrying in {current_interval / 1000}s. Failures: {self.health_check_failures}")
        except Exception as e:
            self.set_backend_status(False)
            self.health_check_failures += 1
            current_interval = min(self.max_health_check_interval, 
                                   self.health_timer.interval() * (2 ** self.health_check_failures))
            self.health_timer.setInterval(current_interval)
            print(f"Backend health check failed. Retrying in {current_interval / 1000}s. Failures: {self.health_check_failures}")
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Stop timers
        self.refresh_timer.stop()
        self.health_timer.stop()
        
        # Save window size
        size = self.size()
        config.set_window_size(size.width(), size.height())
        
        # Close API client
        self.api_client.close()
        
        event.accept()
