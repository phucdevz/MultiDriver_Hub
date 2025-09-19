"""
Search results component for displaying file search results
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QPushButton,
    QProgressBar, QFrame, QMessageBox, QMenu, QLineEdit,
    QDialog, QComboBox, QCheckBox, QRadioButton, QGroupBox,
    QProgressDialog, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, QSettings
from PySide6.QtGui import QFont, QIcon, QCursor, QAction, QKeySequence, QShortcut

class SearchResults(QWidget):
    """Search results widget for displaying files"""
    
    # Signals
    file_selected = Signal(str)
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.current_files = []
        self.current_pagination = {}
        self.selected_account = None  # Track selected account
        self.settings = QSettings('MultiAPIDriver', 'Frontend')
        
        self.setup_ui()
        self.setup_connections()
        
        # Auto-refresh timer for real-time sync
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh)
        self.refresh_timer.start(300000)  # 5 minutes
        
        # Initial load with delay to ensure UI is ready
        QTimer.singleShot(1000, self.refresh_my_drive)
    
    def setup_ui(self):
        """Setup the search results UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)  # Giảm từ 20,20,20,20 xuống 12,12,12,12
        layout.setSpacing(10)  # Giảm từ 15 xuống 10
        
        # Compact header frame with integrated search
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: #1a202c;
                border: 1px solid #4a5568;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(8, 6, 8, 6)
        header_layout.setSpacing(8)
        
        # Search input (compact)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search files...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #2d3748;
                border: 1px solid #4a5568;
                border-radius: 4px;
                padding: 6px 12px;
                color: #e2e8f0;
                font-size: 12px;
                min-height: 28px;
                max-width: 300px;
            }
            QLineEdit:focus {
                border: 1px solid #667eea;
                background: #2d3748;
            }
        """)
        self.search_input.returnPressed.connect(self.perform_search)
        
        # Search button with text
        self.search_button = QPushButton("🔍 Search")
        self.search_button.setStyleSheet("""
            QPushButton {
                background: #667eea;
                color: white;
                border: 1px solid #667eea;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                min-height: 28px;
            }
            QPushButton:hover {
                background: #5a67d8;
                border: 1px solid #5a67d8;
            }
        """)
        self.search_button.clicked.connect(self.perform_search)
        
        # Clear search button with text
        self.clear_search_button = QPushButton("❌ Clear")
        self.clear_search_button.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border: 1px solid #ef4444;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                min-height: 28px;
            }
            QPushButton:hover {
                background: #dc2626;
                border: 1px solid #dc2626;
            }
        """)
        self.clear_search_button.clicked.connect(self.clear_search)
        
        # Advanced filter button with text
        self.advanced_button = QPushButton("⚙️ Filters")
        self.advanced_button.setStyleSheet("""
            QPushButton {
                background: #f59e0b;
                color: white;
                border: 1px solid #f59e0b;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                min-height: 28px;
            }
            QPushButton:hover {
                background: #d97706;
                border: 1px solid #d97706;
            }
        """)
        self.advanced_button.clicked.connect(self.show_advanced_filters)
        
        # Refresh button with text
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: 1px solid #3b82f6;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                min-height: 28px;
            }
            QPushButton:hover {
                background: #2563eb;
                border: 1px solid #2563eb;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_my_drive)
        
        # Export button with text
        self.export_button = QPushButton("📊 Export")
        self.export_button.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: 1px solid #10b981;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                min-height: 28px;
            }
            QPushButton:hover {
                background: #059669;
                border: 1px solid #059669;
            }
        """)
        self.export_button.clicked.connect(self.export_results)
        
        # Upload button
        self.upload_button = QPushButton("📤 Upload")
        self.upload_button.setStyleSheet("""
            QPushButton {
                background: #38a169;
                color: white;
                border: 1px solid #38a169;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                min-height: 28px;
            }
            QPushButton:hover {
                background: #2f855a;
                border: 1px solid #2f855a;
            }
        """)
        self.upload_button.clicked.connect(self.show_upload_dialog)
        
        # Add widgets to header layout - all buttons together
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(self.search_button)
        header_layout.addWidget(self.clear_search_button)
        header_layout.addWidget(self.advanced_button)
        header_layout.addWidget(self.refresh_button)
        header_layout.addWidget(self.upload_button)
        header_layout.addWidget(self.export_button)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setStyleSheet("""
            QTableWidget {
                background: #1a202c;
                border: 1px solid #4a5568;
                border-radius: 6px;
                gridline-color: #4a5568;
                color: #e2e8f0;
                font-size: 11px;
                selection-background-color: #667eea;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 4px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #667eea;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: rgba(102, 126, 234, 0.1);
            }
            QHeaderView::section {
                background: #2d3748;
                color: #e2e8f0;
                padding: 6px 8px;
                border: 1px solid #4a5568;
                font-size: 11px;
                font-weight: bold;
            }
            QScrollBar:vertical {
                width: 14px;
                background: #2d3748;
                border-radius: 7px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #4a5568;
                border-radius: 7px;
                min-height: 30px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #667eea;
            }
            QScrollBar::handle:vertical:pressed {
                background: #5a67d8;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
            QScrollBar:horizontal {
                height: 14px;
                background: #2d3748;
                border-radius: 7px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #4a5568;
                border-radius: 7px;
                min-width: 30px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #667eea;
            }
            QScrollBar::handle:horizontal:pressed {
                background: #5a67d8;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
                background: transparent;
            }
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: transparent;
            }
        """)
        
        # Pagination frame
        pagination_frame = QFrame()
        pagination_frame.setStyleSheet("""
            QFrame {
                background: #1a202c;
                border: 1px solid #4a5568;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        
        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(8, 4, 8, 4)
        
        # Page size selector (compact)
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["25", "50", "100", "200"])
        self.page_size_combo.setFixedWidth(64)
        self.page_size_combo.setFixedHeight(24)
        self.page_size_combo.setStyleSheet("""
            QComboBox { background: #2d3748; border: 1px solid #4a5568; border-radius: 4px; padding: 2px 18px 2px 6px; color: #e2e8f0; font-size: 11px; min-height: 22px; }
            QComboBox:hover { border: 1px solid #667eea; }
        """)
        try:
            saved_page_size = int(self.settings.value('table/page_size', 50))
        except Exception:
            saved_page_size = 50
        if str(saved_page_size) in ["25", "50", "100", "200"]:
            self.page_size_combo.setCurrentText(str(saved_page_size))
        
        # Previous button
        self.previous_button = QPushButton("← Previous")
        self.previous_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #6b7280, stop:1 #4b5563);
                color: white;
                border: 1px solid #6b7280;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                min-height: 28px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4b5563, stop:1 #374151);
                border: 1px solid #4b5563;
            }
        """)
        
        # Page info
        self.page_info = QLabel("Page 1 of 1")
        self.page_info.setStyleSheet("""
            QLabel {
                color: #e2e8f0;
                font-size: 12px;
                padding: 6px 12px;
                border-radius: 4px;
                background: rgba(113, 128, 150, 0.1);
            }
        """)
        
        # Loading indicator (lightweight)
        self.loading_label = QLabel("Loading…")
        self.loading_label.setStyleSheet("color: #a0aec0; padding: 6px 12px;")
        self.loading_label.setVisible(False)
        
        # Next button
        self.next_button = QPushButton("Next →")
        self.next_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #6b7280, stop:1 #4b5563);
                color: white;
                border: 1px solid #6b7280;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                min-height: 28px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4b5563, stop:1 #374151);
                border: 1px solid #4b5563;
            }
        """)
        
        # Add widgets to layouts
        header_layout.addWidget(self.export_button)
        
        pagination_layout.addWidget(self.previous_button)
        pagination_layout.addStretch()
        # Unified "Page size" control inside one pill container
        page_size_container = QFrame()
        page_size_container.setStyleSheet("""
            QFrame {
                background: #2d3748;
                border: 1px solid #4a5568;
                border-radius: 6px;
            }
            QLabel {
                color: #e2e8f0;
                padding-left: 8px;
            }
        """)
        page_size_layout = QHBoxLayout(page_size_container)
        page_size_layout.setContentsMargins(8, 3, 6, 3)
        page_size_layout.setSpacing(6)
        self.page_size_label = QLabel("Page size:")
        page_size_layout.addWidget(self.page_size_label)
        page_size_layout.addWidget(self.page_size_combo)
        pagination_layout.addWidget(page_size_container)
        pagination_layout.addWidget(self.loading_label)
        pagination_layout.addWidget(self.page_info)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.next_button)
        
        # Connect signals
        self.export_button.clicked.connect(self.export_results)
        self.previous_button.clicked.connect(self.previous_page)
        self.next_button.clicked.connect(self.next_page)
        
        # Set up table columns
        self.setup_table_columns()
        
        # Enable sorting
        self.results_table.setSortingEnabled(True)
        
        # Enable alternating row colors
        self.results_table.setAlternatingRowColors(True)
        
        # Set selection behavior
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Performance optimizations for smooth scrolling
        self.results_table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        self.results_table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.results_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.results_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Reduce flickering during updates
        self.results_table.setUpdatesEnabled(True)
        self.results_table.viewport().setAttribute(Qt.WA_OpaquePaintEvent, False)
        
        # Additional performance optimizations
        self.results_table.setShowGrid(True)
        self.results_table.setGridStyle(Qt.SolidLine)
        self.results_table.setWordWrap(False)
        self.results_table.setTextElideMode(Qt.ElideRight)
        
        # Optimize for large datasets
        self.results_table.verticalHeader().setDefaultSectionSize(32)
        self.results_table.verticalHeader().setVisible(False)
        
        layout.addWidget(header_frame)
        layout.addWidget(self.results_table)
        layout.addWidget(pagination_frame)
        
        # Initialize pagination state
        self.current_page = 1
        self.total_pages = 1
        self.page_size = 50
        
        # Disable pagination initially
        self.previous_button.setEnabled(False)
        self.next_button.setEnabled(False)
        
        # Smooth scrolling optimization
        self.setup_smooth_scrolling()

        # Debounce timer for typing in the search box
        self.search_timer = QTimer(self)
        self.search_timer.setInterval(350)
        self.search_timer.setSingleShot(True)
        self.search_input.textChanged.connect(self.search_timer.start)
        self.search_timer.timeout.connect(self.perform_search)

        # Overlay label for empty/error states
        self.overlay_label = QLabel('', self.results_table)
        self.overlay_label.setAlignment(Qt.AlignCenter)
        self.overlay_label.setStyleSheet("color: #a0aec0; font-size: 12px;")
        self.overlay_label.hide()

        # Restore table settings
        self.restore_table_settings()
    
    def show_upload_dialog(self):
        """Show upload dialog"""
        try:
            from ui.upload_dialog import UploadDialog

            # Get accounts for upload dialog
            accounts_response = self.api_client.get_accounts()
            if not accounts_response.get('success'):
                QMessageBox.warning(self, "Error", "Failed to get accounts for upload.")
                return

            accounts = accounts_response.get('accounts', [])
            if not accounts:
                QMessageBox.warning(self, "No Accounts", "Please connect at least one Google Drive account first.")
                return

            # Show upload dialog
            upload_dialog = UploadDialog(self.api_client, accounts, self)
            upload_dialog.upload_completed.connect(self.refresh_my_drive)
            upload_dialog.exec()

        except ImportError:
            QMessageBox.warning(self, "Error", "Upload dialog not available.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to show upload dialog: {str(e)}")

    def setup_connections(self):
        """Setup signal connections"""
        self.results_table.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.results_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Enable context menu
        self.results_table.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Save settings on column resize/sort
        header = self.results_table.horizontalHeader()
        header.sectionResized.connect(self.save_table_settings)
        header.sortIndicatorChanged.connect(lambda *_: self.save_table_settings())
        
        # Page size change
        self.page_size_combo.currentTextChanged.connect(self.on_page_size_changed)
        
        # Shortcuts
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: self.search_input.setFocus())
        QShortcut(QKeySequence("F5"), self, activated=self.refresh_my_drive)
        QShortcut(QKeySequence("Ctrl+E"), self, activated=self.export_results)
    
    def setup_smooth_scrolling(self):
        """Setup smooth scrolling optimizations"""
        # Set scroll speed for smoother experience
        self.results_table.verticalScrollBar().setSingleStep(20)
        self.results_table.horizontalScrollBar().setSingleStep(20)
        
        # Enable smooth scrolling
        self.results_table.verticalScrollBar().setPageStep(100)
        self.results_table.horizontalScrollBar().setPageStep(100)
    
    def set_selected_account(self, account_key):
        """Set the selected account (but always show My Drive)"""
        self.selected_account = account_key
        # Always refresh My Drive regardless of selected account
        self.refresh_my_drive()
    
    def refresh_my_drive(self):
        """Refresh files for My Drive (Google Drive)"""
        self.load_my_drive_files()
    
    def update_results(self, files, pagination):
        """Update search results with new data"""
        self.current_files = files
        self.current_pagination = pagination
        
        # Disable updates during population for better performance
        self.results_table.setUpdatesEnabled(False)
        
        try:
            # Clear table
            self.results_table.setRowCount(0)
            
            # Pre-allocate rows for better performance
            self.results_table.setRowCount(len(files))
        
            # Populate table
            for i, file in enumerate(files):
                self.add_file_row_at_index(file, i)
        
            # Update pagination controls
            self.update_pagination_controls()
        
        finally:
            # Re-enable updates
            self.results_table.setUpdatesEnabled(True)
            # Overlay messages
            if len(files) == 0:
                self.show_overlay_message("No results found")
            else:
                self.hide_overlay_message()
            # Persist after updates
            self.save_table_settings()
    
    def add_file_row(self, file):
        """Add a file to the results table"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        self.add_file_row_at_index(file, row)
        
    def add_file_row_at_index(self, file, row):
        """Add a file to the results table at specific index"""
        # File name
        name_item = QTableWidgetItem(file.get('name', 'Unknown'))
        name_item.setData(Qt.UserRole, file.get('id'))  # Store file ID
        self.results_table.setItem(row, 0, name_item)
        
        # File type
        mime_type = file.get('mime_type', '')
        type_text = self.get_file_type_display(mime_type)
        type_item = QTableWidgetItem(type_text)
        type_item.setToolTip(mime_type)
        self.results_table.setItem(row, 1, type_item)
        
                # File size
        size = file.get('size', 0) or 0
        size_text = self.format_size(size)
        size_item = QTableWidgetItem(size_text)
        size_item.setData(Qt.UserRole, size)  # Store raw size for sorting
        self.results_table.setItem(row, 2, size_item)
        
        # Modified date
        modified = file.get('modified_time', '')
        if modified:
            modified_text = modified[:10]  # Show only date part
        else:
            modified_text = 'Unknown'
        modified_item = QTableWidgetItem(modified_text)
        self.results_table.setItem(row, 3, modified_item)
        
        # Owner
        owner = file.get('account_key', 'Unknown')
        owner_item = QTableWidgetItem(owner)
        self.results_table.setItem(row, 4, owner_item)
        
        # Path (placeholder for now)
        path_item = QTableWidgetItem("/")
        self.results_table.setItem(row, 5, path_item)
        
        # Actions
        actions_widget = self.create_actions_widget(file)
        self.results_table.setCellWidget(row, 6, actions_widget)
    
    def create_actions_widget(self, file):
        """Create actions widget for a file row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        # View button
        view_btn = QPushButton("��")
        view_btn.setToolTip("View file details")
        view_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: #2196F3;
                color: white;
                border-radius: 3px;
                padding: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        view_btn.clicked.connect(lambda: self.view_file(file))
        layout.addWidget(view_btn)
        
        # Open button
        open_btn = QPushButton("🔗")
        open_btn.setToolTip("Open in Google Drive")
        open_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: #4CAF50;
                color: white;
                border-radius: 3px;
                padding: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        open_btn.clicked.connect(lambda: self.open_in_drive(file))
        layout.addWidget(open_btn)
        
        # Download button (if applicable)
        if (file.get('size', 0) or 0) > 0:
            download_btn = QPushButton("⬇")
            download_btn.setToolTip("Download file")
            download_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background-color: #FF9800;
                    color: white;
                    border-radius: 3px;
                    padding: 4px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                }
            """)
            download_btn.clicked.connect(lambda: self.download_file(file))
            layout.addWidget(download_btn)
        
        layout.addStretch()
        return widget
    
    def get_file_type_display(self, mime_type):
        """Get display text for MIME type"""
        if not mime_type:
            return "Unknown"
        
        type_mapping = {
            'application/pdf': 'PDF',
            'application/vnd.google-apps.document': 'Google Doc',
            'application/vnd.google-apps.spreadsheet': 'Google Sheet',
            'application/vnd.google-apps.presentation': 'Google Slides',
            'image/jpeg': 'JPEG',
            'image/png': 'PNG',
            'image/gif': 'GIF',
            'video/mp4': 'MP4',
            'video/avi': 'AVI',
            'audio/mpeg': 'MP3',
            'audio/wav': 'WAV',
            'application/zip': 'ZIP',
            'application/rar': 'RAR'
        }
        
        return type_mapping.get(mime_type, mime_type.split('/')[-1].upper())
    
    def format_size(self, size_bytes):
        """Format size in bytes to human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def update_pagination_controls(self):
        """Update pagination control states"""
        pagination = self.current_pagination
        
        current_page = pagination.get('page', 1)
        total_pages = pagination.get('totalPages', 1)
        has_prev = pagination.get('hasPrev', False)
        has_next = pagination.get('hasNext', False)
        
        self.previous_button.setEnabled(has_prev)
        self.next_button.setEnabled(has_next)
        self.page_info.setText(f"Page {current_page} of {total_pages}")
    
    def previous_page(self):
        """Go to previous page"""
        current_page = self.current_pagination.get('page', 1)
        if current_page > 1:
            # Update pagination and trigger new search
            self.current_pagination['page'] = current_page - 1
            self.perform_search()
    
    def next_page(self):
        """Go to next page"""
        current_page = self.current_pagination.get('page', 1)
        total_pages = self.current_pagination.get('totalPages', 1)
        if current_page < total_pages:
            # Update pagination and trigger new search
            self.current_pagination['page'] = current_page + 1
            self.perform_search()
    
    def on_file_double_clicked(self, item):
        """Handle file double-click"""
        if item.column() == 0:  # Name column
            file_id = item.data(Qt.UserRole)
            if file_id:
                self.file_selected.emit(file_id)
    
    def show_context_menu(self, position):
        """Show context menu for file actions"""
        item = self.results_table.itemAt(position)
        if not item:
            return
        
        file_id = item.data(Qt.UserRole)
        if not file_id:
            return
        
        # Find the file data
        file_data = None
        for file in self.current_files:
            if file.get('id') == file_id:
                file_data = file
                break
        
        if not file_data:
            return
        
        # Create context menu
        menu = QMenu(self)
        
        # View details action
        view_action = QAction("View Details", self)
        view_action.triggered.connect(lambda: self.view_file(file_data))
        menu.addAction(view_action)
        
        # Open in Drive action
        open_action = QAction("Open in Google Drive", self)
        open_action.triggered.connect(lambda: self.open_in_drive(file_data))
        menu.addAction(open_action)
        
        # Download action (if applicable)
        if (file_data.get('size', 0) or 0) > 0:
            download_action = QAction("Download", self)
            download_action.triggered.connect(lambda: self.download_file(file_data))
            menu.addAction(download_action)
        
        menu.addSeparator()
        
        # Copy link action
        copy_action = QAction("Copy Link", self)
        copy_action.triggered.connect(lambda: self.copy_link(file_data))
        menu.addAction(copy_action)
        
        # Show menu
        menu.exec_(QCursor.pos())
    
    def view_file(self, file):
        """View file details"""
        file_id = file.get('id')
        if file_id:
            self.file_selected.emit(file_id)
    
    def open_in_drive(self, file):
        """Open file in Google Drive"""
        file_id = file.get('id')
        if file_id:
            import webbrowser
            url = f"https://drive.google.com/file/d/{file_id}/view"
            webbrowser.open(url)
    
    def download_file(self, file):
        """Download file"""
        file_id = file.get('id')
        file_name = file.get('name', 'Unknown')
        mime_type = file.get('mime_type', '')
        
        try:
            # Check if it's a Google Doc that needs export format
            if mime_type.startswith('application/vnd.google-apps.'):
                # Show format selection dialog for Google Docs
                format_dialog = QDialog(self)
                format_dialog.setWindowTitle("Export Format")
                format_dialog.setModal(True)
                
                layout = QVBoxLayout(format_dialog)
                
                # Add label
                label = QLabel(f"Select export format for: {file_name}")
                layout.addWidget(label)
                
                # Add format selection
                format_combo = QComboBox()
                format_combo.addItems(['PDF', 'DOCX', 'XLSX', 'PPTX', 'TXT', 'HTML'])
                layout.addWidget(format_combo)
                
                # Add buttons
                button_layout = QHBoxLayout()
                ok_button = QPushButton("Export")
                cancel_button = QPushButton("Cancel")
                button_layout.addWidget(ok_button)
                button_layout.addWidget(cancel_button)
                layout.addLayout(button_layout)
                
                # Connect signals
                ok_button.clicked.connect(format_dialog.accept)
                cancel_button.clicked.connect(format_dialog.reject)
                
                if format_dialog.exec_() == QDialog.Accepted:
                    selected_format = format_combo.currentText().lower()
                    # Download with format
                    self._download_file_with_format(file_id, file_name, selected_format)
            else:
                # Regular file download
                self._download_file_with_format(file_id, file_name)
                
        except Exception as e:
            QMessageBox.critical(self, "Download Error", 
                               f"Failed to download file: {str(e)}")
    
    def _download_file_with_format(self, file_id: str, file_name: str, format: str = None):
        """Download file with optional format (stream to disk)."""
        try:
            # Ask user where to save
            from PySide6.QtWidgets import QFileDialog
            default_name = file_name
            if format and not default_name.lower().endswith(f'.{format.lower()}'):
                default_name = f"{default_name}.{format.lower()}"
            dest_path, _ = QFileDialog.getSaveFileName(self, "Save File", default_name)
            if not dest_path:
                return

            # Show progress dialog
            progress = QProgressDialog("Downloading file...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()

            # Stream download to path
            self.api_client.download_file_to_path(file_id, dest_path, format)

            QMessageBox.information(self, "Download Complete", f"Saved to: {dest_path}")

        except Exception as e:
            QMessageBox.critical(self, "Download Failed", f"{e}")
        finally:
            try:
                progress.close()
            except Exception:
                pass
    
    def copy_link(self, file):
        """Copy file link to clipboard"""
        file_id = file.get('id')
        if file_id:
            from PySide6.QtWidgets import QApplication
            url = f"https://drive.google.com/file/d/{file_id}/view"
            QApplication.clipboard().setText(url)
            
            QMessageBox.information(self, "Link Copied", 
                                  "File link has been copied to clipboard!")
    
    def export_results(self):
        """Export search results"""
        if not self.current_files:
            QMessageBox.information(self, "Export", "No results to export")
            return
        
        try:
            # Show export dialog
            export_dialog = QDialog(self)
            export_dialog.setWindowTitle("Export Search Results")
            export_dialog.setModal(True)
            export_dialog.resize(400, 300)
            
            layout = QVBoxLayout(export_dialog)
            
            # Add label
            label = QLabel(f"Export {len(self.current_files)} files")
            layout.addWidget(label)
            
            # Format selection
            format_group = QGroupBox("Export Format")
            format_layout = QVBoxLayout(format_group)
            
            csv_radio = QRadioButton("CSV")
            json_radio = QRadioButton("JSON")
            excel_radio = QRadioButton("Excel")
            csv_radio.setChecked(True)
            
            format_layout.addWidget(csv_radio)
            format_layout.addWidget(json_radio)
            format_layout.addWidget(excel_radio)
            layout.addWidget(format_group)
            
            # Fields selection
            fields_group = QGroupBox("Fields to Export")
            fields_layout = QVBoxLayout(fields_group)
            
            field_checkboxes = {}
            default_fields = [
                ('name', 'File Name', True),
                ('mime_type', 'Type', True),
                ('size', 'Size', True),
                ('modified_time', 'Modified', True),
                ('account_key', 'Account', True),
                ('id', 'File ID', False),
                ('md5', 'MD5 Hash', False),
                ('trashed', 'Trashed', False),
                ('owned_by_me', 'Owned by Me', False)
            ]
            
            for field_id, field_name, default_checked in default_fields:
                checkbox = QCheckBox(field_name)
                checkbox.setChecked(default_checked)
                field_checkboxes[field_id] = checkbox
                fields_layout.addWidget(checkbox)
            
            layout.addWidget(fields_group)
            
            # Buttons
            button_layout = QHBoxLayout()
            export_button = QPushButton("Export")
            cancel_button = QPushButton("Cancel")
            button_layout.addWidget(export_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)
            
            # Connect signals
            export_button.clicked.connect(export_dialog.accept)
            cancel_button.clicked.connect(export_dialog.reject)
            
            if export_dialog.exec_() == QDialog.Accepted:
                # Get selected format
                if csv_radio.isChecked():
                    format = 'csv'
                elif json_radio.isChecked():
                    format = 'json'
                else:
                    format = 'excel'
                
                # Get selected fields
                selected_fields = [field_id for field_id, checkbox in field_checkboxes.items() if checkbox.isChecked()]
                fields_str = ','.join(selected_fields)
                
                # Show progress
                progress = QProgressDialog("Exporting results...", "Cancel", 0, 0, self)
                progress.setWindowModality(Qt.WindowModal)
                progress.show()
                
                try:
                    # Get current search parameters
                    current_query = self.current_search_params.get('q', '')
                    current_filters = {k: v for k, v in self.current_search_params.items() if k != 'q'}
                    
                    # Make export request
                    response = self.api_client.export_search_results(
                        query=current_query,
                        format=format,
                        fields=fields_str,
                        **current_filters
                    )
                    
                    if response.get('success'):
                        QMessageBox.information(self, "Export Complete", 
                                              f"Successfully exported {len(self.current_files)} files to {format.upper()}")
                    else:
                        QMessageBox.critical(self, "Export Failed", 
                                           f"Failed to export: {response.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", 
                                       f"Failed to export results: {str(e)}")
                finally:
                    progress.close()
                    
        except Exception as e:
            QMessageBox.critical(self, "Export Error", 
                               f"Failed to show export dialog: {str(e)}")
    
    def show_loading(self):
        """Show loading indicator"""
        # self.loading_bar.setVisible(True) # This line is removed as per new_code
        pass
    
    def clear_results(self):
        """Clear all search results"""
        self.current_files = []
        self.current_pagination = {}
        self.results_table.setRowCount(0)
        self.previous_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.page_info.setText("Page 1 of 1")

    def perform_search(self):
        """Perform search with current query"""
        query = self.search_input.text().strip()
        if query:
            try:
                self.set_loading(True)
                response = self.api_client.search_files(query, limit=int(self.page_size_combo.currentText()), owner='me', folders='false', page=self.current_pagination.get('page', 1))
                if response.get('success'):
                    data = response.get('data', {})
                    files = data.get('files', [])
                    pagination = data.get('pagination', {})
                    
                    self.update_results(files, pagination)
                else:
                    self.show_overlay_message("Search failed")
            except Exception as e:
                self.show_overlay_message(f"Error: {str(e)}")
            finally:
                self.set_loading(False)
        else:
            # If no query, refresh My Drive
            self.refresh_my_drive()

    def on_page_size_changed(self, value):
        try:
            self.settings.setValue('table/page_size', int(value))
            if self.search_input.text().strip():
                self.perform_search()
            else:
                self.refresh_my_drive()
        except Exception:
            pass

    def save_table_settings(self):
        try:
            header = self.results_table.horizontalHeader()
            widths = [header.sectionSize(i) for i in range(self.results_table.columnCount())]
            self.settings.setValue('table/widths', widths)
            self.settings.setValue('table/sort_column', header.sortIndicatorSection())
            self.settings.setValue('table/sort_order', int(header.sortIndicatorOrder()))
        except Exception:
            pass

    def restore_table_settings(self):
        try:
            widths = self.settings.value('table/widths')
            if widths:
                for i, w in enumerate(widths):
                    try:
                        self.results_table.setColumnWidth(i, int(w))
                    except Exception:
                        pass
            header = self.results_table.horizontalHeader()
            sort_col = int(self.settings.value('table/sort_column', 3))
            sort_order = int(self.settings.value('table/sort_order', int(Qt.DescendingOrder)))
            header.setSortIndicator(sort_col, Qt.SortOrder(sort_order))
        except Exception:
            pass
    

    
    def on_account_deleted(self):
        """Handle account deletion - refresh search results"""
        try:
            print("🔄 Account deleted - refreshing search results...")
            self.refresh_my_drive()
        except Exception as e:
            print(f"❌ Error refreshing search after account deletion: {str(e)}")
    
    def refresh_my_drive(self):
        """Refresh the search results"""
        try:
            # Clear current search
            self.search_input.clear()
            self.current_search_query = ""
            
            # Reset pagination
            self.current_page = 1
            
            # Load My Drive files directly (not through search)
            self.load_my_drive_files()
            
        except Exception as e:
            print(f"❌ Error refreshing search results: {str(e)}")
    
    def load_my_drive_files(self):
        """Load My Drive files directly without search"""
        try:
            self.set_loading(True)
            # First check if we have any accounts
            accounts_response = self.api_client.get_accounts()
            
            if not accounts_response.get('success'):
                print("❌ No accounts connected")
                return
            
            accounts = accounts_response.get('accounts', [])
            if not accounts:
                print("❌ Please connect a Google Drive account first")
                return
            
            print(f"✅ Found {len(accounts)} account(s)")
            
            # Get only files owned by the connected user
            response = self.api_client.search_files(limit=100, owner='me', folders='false')
            
            if response.get('success'):
                data = response.get('data', {}) if isinstance(response, dict) else {}
                files = data.get('files', response.get('files', []))
                pagination = data.get('pagination', response.get('pagination', {}))
                print(f"📊 Loaded {len(files)} files")
                self.update_results(files, pagination)
            else:
                error_msg = response.get('error', 'Unknown error')
                print(f"❌ Search error: {error_msg}")
                
        except Exception as e:
            print(f"❌ Error loading My Drive: {str(e)}")
        finally:
            self.set_loading(False)
    
    def auto_refresh(self):
        """Auto-refresh search results for real-time sync"""
        try:
            print("🔄 Auto-refreshing search results...")
            self.perform_search()
        except Exception as e:
            print(f"❌ Error in auto-refresh: {str(e)}")

    def show_overlay_message(self, text: str):
        try:
            self.overlay_label.setText(text)
            self.overlay_label.resize(self.results_table.viewport().size())
            self.overlay_label.move(0, 0)
            self.overlay_label.show()
        except Exception:
            pass

    def hide_overlay_message(self):
        try:
            self.overlay_label.hide()
        except Exception:
            pass

    def set_loading(self, is_loading: bool):
        try:
            self.loading_label.setVisible(is_loading)
            self.results_table.setDisabled(is_loading)
            QApplication.processEvents()
        except Exception:
            pass
    
    def clear_search(self):
        """Clear search and refresh My Drive"""
        self.search_input.clear()
        self.refresh_my_drive()
    
    def show_advanced_filters(self):
        """Show advanced filters dialog"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit, QCheckBox, QGridLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Advanced Filters")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        
        # Filter grid
        filter_grid = QGridLayout()
        filter_grid.setSpacing(10)
        
        # File type filter
        filter_grid.addWidget(QLabel("File Type:"), 0, 0)
        file_type_combo = QComboBox()
        file_type_combo.addItems(["All Types", "Documents", "Images", "Videos", "Audio", "Archives"])
        filter_grid.addWidget(file_type_combo, 0, 1)
        
        # Size filter
        filter_grid.addWidget(QLabel("Size:"), 1, 0)
        size_layout = QHBoxLayout()
        min_size = QLineEdit()
        min_size.setPlaceholderText("Min (KB)")
        max_size = QLineEdit()
        max_size.setPlaceholderText("Max (MB)")
        size_layout.addWidget(min_size)
        size_layout.addWidget(max_size)
        filter_grid.addLayout(size_layout, 1, 1)
        
        # Date filter
        filter_grid.addWidget(QLabel("Modified Date:"), 2, 0)
        date_layout = QHBoxLayout()
        from_date = QLineEdit()
        from_date.setPlaceholderText("From (YYYY-MM-DD)")
        to_date = QLineEdit()
        to_date.setPlaceholderText("To (YYYY-MM-DD)")
        date_layout.addWidget(from_date)
        date_layout.addWidget(to_date)
        filter_grid.addLayout(date_layout, 2, 1)
        
        # Other filters
        filter_grid.addWidget(QLabel("Other:"), 3, 0)
        include_trashed = QCheckBox("Include Trashed Files")
        include_shortcuts = QCheckBox("Include Shortcuts")
        filter_grid.addWidget(include_trashed, 3, 1)
        filter_grid.addWidget(include_shortcuts, 4, 1)
        
        layout.addLayout(filter_grid)
        
        # Buttons
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        apply_btn = QPushButton("Apply Filters")
        apply_btn.setStyleSheet("""
            QPushButton {
                background: #10b981; color: white; padding: 8px 16px; 
                border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background: #059669; }
        """)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #ef4444; color: white; padding: 8px 16px; 
                border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background: #dc2626; }
        """)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #6b7280; color: white; padding: 8px 16px; 
                border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background: #4b5563; }
        """)
        
        buttons.addWidget(clear_btn)
        buttons.addWidget(apply_btn)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)
        
        def on_apply():
            # Apply filters logic here
            dialog.accept()
        
        def on_clear():
            file_type_combo.setCurrentIndex(0)
            min_size.clear()
            max_size.clear()
            from_date.clear()
            to_date.clear()
            include_trashed.setChecked(False)
            include_shortcuts.setChecked(False)
        
        apply_btn.clicked.connect(on_apply)
        clear_btn.clicked.connect(on_clear)
        close_btn.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def refresh_texts(self):
        """Refresh UI texts after language change"""
        # Update column headers
        self.results_table.setHorizontalHeaderLabels([
            i18n.get("name"),
            i18n.get("type"),
            i18n.get("size"),
            i18n.get("modified"),
            i18n.get("owner"),
            i18n.get("path"),
            i18n.get("actions")
        ])
        
        # Update search placeholder
        self.search_input.setPlaceholderText("🔍 Search files...")
        
        # Update export button
        if self.export_button:
            self.export_button.setText(i18n.get("export_results"))
        
        # Update pagination texts
        if self.previous_button:
            self.previous_button.setText(i18n.get("previous"))
        if self.next_button:
            self.next_button.setText(i18n.get("next"))

    def setup_table_columns(self):
        """Setup table columns with proper sizing"""
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "Name", "Type", "Size", "Modified", "Owner", "Path", "Actions"
        ])
        
        # Set column widths - Tối ưu để sử dụng không gian tốt hơn
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)  # Name - cho phép resize
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Size
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Modified
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Owner
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Path
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions
        
        # Set specific column widths for better balance
        self.results_table.setColumnWidth(0, 300)  # Name: 300px thay vì stretch
        self.results_table.setColumnWidth(1, 120)  # Type: 120px
        self.results_table.setColumnWidth(2, 100)  # Size: 100px
        self.results_table.setColumnWidth(3, 120)  # Modified: 120px
        self.results_table.setColumnWidth(4, 200)  # Owner: 200px
        self.results_table.setColumnWidth(5, 150)  # Path: 150px
        self.results_table.setColumnWidth(6, 100)  # Actions: 100px
