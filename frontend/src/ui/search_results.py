"""
Search results component for displaying file search results
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QPushButton,
    QProgressBar, QFrame, QMessageBox, QMenu, QLineEdit
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QCursor, QAction

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
        
        self.setup_ui()
        self.setup_connections()
        
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
        
        # Add widgets to header layout - all buttons together
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(self.search_button)
        header_layout.addWidget(self.clear_search_button)
        header_layout.addWidget(self.advanced_button)
        header_layout.addWidget(self.refresh_button)
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
            }
            QTableWidget::item {
                padding: 4px;
                border: none;
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
                width: 12px;
                background: #2d3748;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #4a5568;
                border-radius: 6px;
                min-height: 20px;
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
    
    def setup_connections(self):
        """Setup signal connections"""
        self.results_table.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.results_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Enable context menu
        self.results_table.setContextMenuPolicy(Qt.CustomContextMenu)
    
    def set_selected_account(self, account_key):
        """Set the selected account (but always show My Drive)"""
        self.selected_account = account_key
        # Always refresh My Drive regardless of selected account
        self.refresh_my_drive()
    
    def refresh_my_drive(self):
        """Refresh files for My Drive (Google Drive)"""
        try:
            # Debug: Log what we're doing
            print(f"🔍 Refreshing My Drive...")
            
            # First check if we have any accounts
            accounts_response = self.api_client.get_accounts()
            print(f"📋 Accounts response: {accounts_response}")
            
            if not accounts_response.get('success'):
                print("No accounts connected")
                return
            
            accounts = accounts_response.get('accounts', [])
            if not accounts:
                print("Please connect a Google Drive account first")
                return
            
            print(f"✅ Found {len(accounts)} accounts")
            
            # Get only files owned by the connected user
            response = self.api_client.search_files(limit=100, owner='me', folders='false')
            print(f"📁 Search response: {response}")
            
            if response.get('success'):
                data = response.get('data', {}) if isinstance(response, dict) else {}
                files = data.get('files', response.get('files', []))
                pagination = data.get('pagination', response.get('pagination', {}))
                print(f"📊 Found {len(files)} files")
                self.update_results(files, pagination)
            else:
                error_msg = response.get('error', 'Unknown error')
                print(f"❌ Error: {error_msg}")
                
        except Exception as e:
            error_msg = f"Error loading My Drive: {str(e)}"
            print(f"❌ Error: {error_msg}")
            print(f"💥 Exception: {error_msg}")
    
    def update_results(self, files, pagination):
        """Update search results with new data"""
        self.current_files = files
        self.current_pagination = pagination
        
                # Update results label - removed to save space
        pass
        
        # Clear table
        self.results_table.setRowCount(0)
        
        # Populate table
        for file in files:
            self.add_file_row(file)
        
        # Update pagination controls
        self.update_pagination_controls()
        
        # Hide loading indicator
        # self.loading_bar.setVisible(False) # This line is removed as per new_code
    
    def add_file_row(self, file):
        """Add a file to the results table"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
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
            # This would trigger a new search with updated pagination
            # For now, just show a message
            QMessageBox.information(self, "Pagination", "Previous page functionality will be implemented")
    
    def next_page(self):
        """Go to next page"""
        current_page = self.current_pagination.get('page', 1)
        total_pages = self.current_pagination.get('totalPages', 1)
        if current_page < total_pages:
            # This would trigger a new search with updated pagination
            # For now, just show a message
            QMessageBox.information(self, "Pagination", "Next page functionality will be implemented")
    
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
        
        QMessageBox.information(self, "Download", 
                              f"Download functionality will be implemented.\n\n"
                              f"File: {file_name}\n"
                              f"ID: {file_id}")
    
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
        
        QMessageBox.information(self, "Export", 
                              f"Export functionality will be implemented.\n\n"
                              f"Would export {len(self.current_files)} files to CSV/Excel")
    
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
                response = self.api_client.search_files(query, limit=100, owner='me', folders='false')
                if response.get('success'):
                    data = response.get('data', {})
                    files = data.get('files', [])
                    pagination = data.get('pagination', {})
                    
                    self.update_results(files, pagination)
                else:
                    QMessageBox.warning(self, "Search Failed", f"Error: {response.get('error')}")
            except Exception as e:
                QMessageBox.critical(self, "Search Error", f"Error: {str(e)}")
        else:
            # If no query, refresh My Drive
            self.refresh_my_drive()
    
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
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Owner
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Path
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions
        
        # Set specific column widths for better balance
        self.results_table.setColumnWidth(0, 300)  # Name: 300px thay vì stretch
        self.results_table.setColumnWidth(1, 120)  # Type: 120px
        self.results_table.setColumnWidth(2, 100)  # Size: 100px
        self.results_table.setColumnWidth(3, 120)  # Modified: 120px
        self.results_table.setColumnWidth(4, 200)  # Owner: 200px
        self.results_table.setColumnWidth(5, 150)  # Path: 150px
        self.results_table.setColumnWidth(6, 100)  # Actions: 100px
