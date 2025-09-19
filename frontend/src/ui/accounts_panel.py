"""
Accounts panel component for managing Google Drive accounts
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QLineEdit, QTextEdit, QFormLayout,
    QComboBox, QSpinBox, QGroupBox, QProgressBar, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QColor

from utils.i18n import i18n

class AccountsPanel(QWidget):
    """Accounts management panel"""
    
    # Signals
    account_updated = Signal()
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.accounts = []
        
        self.setup_ui()
        
        # Auto-refresh accounts after a short delay
        QTimer.singleShot(2000, self.refresh_accounts)
        
        # Auto-refresh when accounts are crawling (every 10 seconds)
        self.crawl_refresh_timer = QTimer()
        self.crawl_refresh_timer.timeout.connect(self.refresh_if_crawling)
        self.crawl_refresh_timer.start(10000)  # 10 seconds
    
    def setup_ui(self):
        """Setup the accounts panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Header with centered title
        # Removed redundant banner header to declutter the panel
        
        # Removed top action buttons per request
        
        # Controls row (right aligned)
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.addStretch()

        # Add OAuth Account button
        add_oauth_btn = QPushButton("🔗 Add OAuth Account")
        add_oauth_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10B981, stop:1 #059669);
                color: white;
                border: 1px solid #059669;
                padding: 6px 14px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-height: 30px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #059669, stop:1 #047857);
                border: 1px solid #047857;
            }
        """)
        add_oauth_btn.clicked.connect(self.add_oauth_account)
        controls_layout.addWidget(add_oauth_btn)

        # Add Service Account button
        add_sa_btn = QPushButton("🔑 Add Service Account")
        add_sa_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F59E0B, stop:1 #D97706);
                color: white;
                border: 1px solid #D97706;
                padding: 6px 14px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-height: 30px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #D97706, stop:1 #B45309);
                border: 1px solid #B45309;
            }
        """)
        add_sa_btn.clicked.connect(self.add_service_account)
        controls_layout.addWidget(add_sa_btn)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4F46E5, stop:1 #4338CA);
                color: white;
                border: 1px solid #4338CA;
                padding: 6px 14px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-height: 30px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4338CA, stop:1 #3730A3);
                border: 1px solid #3730A3;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_accounts)
        controls_layout.addWidget(refresh_btn)
        layout.addLayout(controls_layout)

        # Accounts table
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(8)
        self.accounts_table.setHorizontalHeaderLabels([
            "Account", "Type", "Status", "Files", "Size", "Last Sync", "Connected", "Actions"
        ])
        
        # Set table properties
        self.accounts_table.setAlternatingRowColors(True)
        self.accounts_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.accounts_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Set column widths
        header = self.accounts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Account
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Files
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Size
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Last Sync
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Connected
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Actions
        
        # Set table style - Dark theme để phù hợp với app
        self.accounts_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #4a5568;
                border-radius: 8px;
                background-color: #1a202c;
                gridline-color: #4a5568;
                color: #e2e8f0;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #4a5568;
            }
            QTableWidget::item:selected {
                background-color: rgba(102, 126, 234, 0.2);
                color: #e2e8f0;
            }
            QHeaderView::section {
                background-color: #2d3748;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #4a5568;
                font-weight: bold;
                color: #e2e8f0;
                font-size: 13px;
            }
        """)
        
        layout.addWidget(self.accounts_table)
    
    def refresh_accounts(self):
        """Refresh the accounts list"""
        try:
            response = self.api_client.get_accounts()
            if response.get('success'):
                old_accounts = self.accounts.copy()
                self.accounts = response.get('accounts', [])
                self.update_accounts_table()
                print(f"✅ Loaded {len(self.accounts)} accounts")
                
                # Check for new accounts that started crawling
                for account in self.accounts:
                    if account.get('status') == 'crawling':
                        account_key = account.get('email') or account.get('sa_alias')
                        # Check if this account was not crawling before
                        old_account = next((a for a in old_accounts if (a.get('email') or a.get('sa_alias')) == account_key), None)
                        if not old_account or old_account.get('status') != 'crawling':
                            print(f"🔄 New account {account_key} started crawling!")
                
            else:
                print(f"❌ Failed to get accounts: {response.get('error')}")
                QMessageBox.warning(self, "Error", f"Failed to get accounts: {response.get('error')}")
        except Exception as e:
            print(f"❌ Error refreshing accounts: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error refreshing accounts: {str(e)}")
            
    def on_user_authenticated(self):
        """Called when user successfully logs in"""
        # Refresh accounts after successful authentication
        QTimer.singleShot(1000, self.refresh_accounts)  # Delay 1 second
    
    def update_accounts_table(self):
        """Update the accounts table with current data"""
        self.accounts_table.setRowCount(0)
        
        for account in self.accounts:
            self.add_account_row(account)
    
    def add_account_row(self, account):
        """Add an account to the table"""
        row = self.accounts_table.rowCount()
        self.accounts_table.insertRow(row)
        
        # Account name/email
        name = account.get('email') or account.get('sa_alias') or 'Unknown'
        name_item = QTableWidgetItem(name)
        self.accounts_table.setItem(row, 0, name_item)
        
        # Account type
        auth_type = account.get('auth_type', 'unknown')
        type_item = QTableWidgetItem(auth_type.title())
        self.accounts_table.setItem(row, 1, type_item)
        
        # Status with visual indicators
        status = account.get('status', 'unknown')
        status_item = QTableWidgetItem(status.title())
        
        # Add visual indicators for status
        if status == 'crawling':
            status_item.setText("🔄 Crawling...")
            status_item.setBackground(QColor(255, 193, 7, 50))  # Yellow background
        elif status == 'syncing':
            status_item.setText("⚡ Syncing...")
            status_item.setBackground(QColor(33, 150, 243, 50))  # Blue background
        elif status == 'error':
            status_item.setText("❌ Error")
            status_item.setBackground(QColor(244, 67, 54, 50))  # Red background
        elif status == 'idle':
            status_item.setText("✅ Idle")
            status_item.setBackground(QColor(76, 175, 80, 50))  # Green background
        
        self.accounts_table.setItem(row, 2, status_item)
        
        # File count (placeholder)
        files_item = QTableWidgetItem("0")
        self.accounts_table.setItem(row, 3, files_item)
        
        # Total size (placeholder)
        size_item = QTableWidgetItem("0 B")
        self.accounts_table.setItem(row, 4, size_item)
        
        # Last sync
        last_sync = account.get('last_sync_at', '')
        if last_sync:
            last_sync_text = last_sync[:10]  # Show only date part
        else:
            last_sync_text = 'Never'
        last_sync_item = QTableWidgetItem(last_sync_text)
        self.accounts_table.setItem(row, 5, last_sync_item)
        
        # Connected date
        connected = account.get('connected_at', '')
        if connected:
            connected_text = connected[:10]  # Show only date part
        else:
            connected_text = 'Unknown'
        connected_item = QTableWidgetItem(connected_text)
        self.accounts_table.setItem(row, 6, connected_item)
        
        # Actions
        actions_widget = self.create_actions_widget(account)
        self.accounts_table.setCellWidget(row, 7, actions_widget)
    
    def create_actions_widget(self, account):
        """Create actions widget for an account row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        # Sync button
        sync_btn = QPushButton("🔄")
        sync_btn.setToolTip("Sync account")
        sync_btn.setStyleSheet("""
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
        sync_btn.clicked.connect(lambda: self.sync_account(account))
        layout.addWidget(sync_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑")
        delete_btn.setToolTip("Delete account")
        delete_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: #F44336;
                color: white;
                border-radius: 3px;
                padding: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_account(account))
        layout.addWidget(delete_btn)
        
        layout.addStretch()
        return widget
    
    def add_oauth_account(self):
        """Add OAuth account"""
        try:
            response = self.api_client.start_oauth()
            if response.get('success'):
                auth_url = response.get('authUrl')
                
                # Open browser for OAuth
                import webbrowser
                webbrowser.open(auth_url)
                
                QMessageBox.information(self, "OAuth Started", 
                                      "🔗 OAuth flow started in your browser.\n\n"
                                      "📋 Please complete the authorization and return here.\n\n"
                                      "🔄 Click 'Refresh' after completing OAuth to see your account.\n\n"
                                      "💡 New accounts will automatically start crawling files!")
            else:
                QMessageBox.warning(self, "Error", f"Failed to start OAuth: {response.get('error')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error starting OAuth: {str(e)}")
    
    def add_service_account(self):
        """Add Service Account"""
        dialog = ServiceAccountDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                response = self.api_client.register_service_account(
                    data['alias'],
                    data['private_key'],
                    data['root_folder_ids']
                )
                
                if response.get('success'):
                    auto_crawl = response.get('autoCrawl', False)
                    if auto_crawl:
                        QMessageBox.information(self, "Success", 
                                              f"✅ Service Account '{data['alias']}' registered successfully!\n\n"
                                              f"🔄 Auto-crawl started - files will appear soon...\n"
                                              f"📊 Check status in the accounts table.")
                    else:
                        QMessageBox.information(self, "Success", 
                                              f"Service Account '{data['alias']}' registered successfully!")
                    
                    self.refresh_accounts()
                    self.account_updated.emit()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to register SA: {response.get('error')}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error registering SA: {str(e)}")
    
    def sync_account(self, account):
        """Sync an account"""
        account_key = account.get('email') or account.get('sa_alias')
        
        reply = QMessageBox.question(self, "Sync Account", 
                                   f"Start initial sync for {account_key}?\n\n"
                                   "This will crawl all files in the account.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                response = self.api_client.start_initial_crawl(account_key)
                if response.get('success'):
                    QMessageBox.information(self, "Sync Started", 
                                          f"Initial sync started for {account_key}")
                    self.refresh_accounts()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to start sync: {response.get('error')}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error starting sync: {str(e)}")
    
    def delete_account(self, account):
        """Delete an account"""
        account_key = account.get('email') or account.get('sa_alias')
        
        reply = QMessageBox.question(self, "Delete Account", 
                                   f"Are you sure you want to delete {account_key}?\n\n"
                                   "⚠️ This will permanently delete:\n"
                                   f"• Account: {account_key}\n"
                                   "• All associated files\n"
                                   "• All sync data\n\n"
                                   "This action cannot be undone!",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                response = self.api_client.delete_account(account_key)
                if response.get('success'):
                    deleted_files = response.get('deletedFiles', 0)
                    QMessageBox.information(self, "Success", 
                                          f"✅ Account deleted successfully!\n\n"
                                          f"🗑️ Deleted {deleted_files} files\n"
                                          f"📁 Account: {account_key}")
                    
                    # Real-time refresh
                    self.refresh_accounts()
                    self.account_updated.emit()
                    
                    # Emit signal to refresh other panels
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(100, self.emit_refresh_signals)
                    
                else:
                    QMessageBox.warning(self, "Error", f"Failed to delete account: {response.get('error')}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error deleting account: {str(e)}")
    
    def emit_refresh_signals(self):
        """Emit signals to refresh other panels"""
        try:
            # Import here to avoid circular imports
            from ui.search_results import SearchResultsPanel
            from ui.reports_panel import ReportsPanel
            
            # Emit signals to refresh search and reports
            self.account_updated.emit()
            
        except ImportError:
            pass
    
    def refresh_if_crawling(self):
        """Refresh accounts if any are in crawling status"""
        try:
            # Check if any accounts are crawling
            for account in self.accounts:
                if account.get('status') == 'crawling':
                    print(f"🔄 Account {account.get('email') or account.get('sa_alias')} is crawling - refreshing...")
                    self.refresh_accounts()
                    break
        except Exception as e:
            print(f"❌ Error in refresh_if_crawling: {str(e)}")

    def refresh_texts(self):
        """Refresh UI texts after language change"""
        # Update panel title
        if hasattr(self, 'title_label'):
            self.title_label.setText(i18n.get("accounts"))
        
        # Update column headers if table exists
        if hasattr(self, 'accounts_table'):
            self.accounts_table.setHorizontalHeaderLabels([
                i18n.get("name"),
                i18n.get("type"),
                i18n.get("status"),
                i18n.get("last_sync"),
                i18n.get("actions")
            ])
        
        # Update button texts
        if hasattr(self, 'add_account_button'):
            self.add_account_button.setText(i18n.get("add_account"))
        if hasattr(self, 'refresh_button'):
            self.refresh_button.setText(i18n.get("refresh"))


class ServiceAccountDialog(QDialog):
    """Dialog for adding Service Account"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Service Account")
        self.setModal(True)
        self.resize(500, 400)
        
        self.setup_ui()
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background: #1a202c;
                color: #e2e8f0;
            }
            QLabel {
                color: #e2e8f0;
                font-size: 12px;
            }
            QLineEdit, QTextEdit {
                background: #2d3748;
                border: 1px solid #4a5568;
                border-radius: 4px;
                padding: 8px;
                color: #e2e8f0;
                font-size: 12px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #667eea;
            }
            QPushButton {
                background: #667eea;
                color: white;
                border: 1px solid #667eea;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #5a67d8;
                border: 1px solid #5a67d8;
            }
            QPushButton:disabled {
                background: #4a5568;
                border: 1px solid #4a5568;
                color: #a0aec0;
            }
        """)
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Add Service Account")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Alias
        self.alias_input = QLineEdit()
        self.alias_input.setPlaceholderText("Enter a name for this service account")
        form_layout.addRow("Alias:", self.alias_input)
        
        # Private key
        self.private_key_input = QTextEdit()
        self.private_key_input.setPlaceholderText("Paste the private key JSON content here")
        self.private_key_input.setMaximumHeight(150)
        form_layout.addRow("Private Key (JSON):", self.private_key_input)
        
        # Root folder IDs
        self.root_folders_input = QTextEdit()
        self.root_folders_input.setPlaceholderText("Enter folder IDs separated by commas (optional)")
        self.root_folders_input.setMaximumHeight(80)
        form_layout.addRow("Root Folder IDs:", self.root_folders_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        add_btn = QPushButton("Add Service Account")
        add_btn.clicked.connect(self.accept)
        button_layout.addWidget(add_btn)
        
        layout.addLayout(button_layout)
    
    def get_data(self):
        """Get the entered data"""
        alias = self.alias_input.text().strip()
        private_key = self.private_key_input.toPlainText().strip()
        root_folders_text = self.root_folders_input.toPlainText().strip()
        
        # Parse root folder IDs (comma-separated)
        root_folder_ids = []
        if root_folders_text:
            root_folder_ids = [fid.strip() for fid in root_folders_text.split(',') if fid.strip()]
        
        return {
            'alias': alias,
            'private_key': private_key,
            'root_folder_ids': root_folder_ids
        }
