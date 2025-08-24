"""
Accounts panel component for managing Google Drive accounts
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QLineEdit, QTextEdit, QFormLayout,
    QComboBox, QSpinBox, QGroupBox, QProgressBar
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon

class AccountsPanel(QWidget):
    """Accounts management panel"""
    
    # Signals
    account_updated = Signal()
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.accounts = []
        
        self.setup_ui()
        self.refresh_accounts()
    
    def setup_ui(self):
        """Setup the accounts panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Google Drive Accounts")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Add account buttons
        oauth_btn = QPushButton("+ OAuth Account")
        oauth_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285F4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367D6;
            }
        """)
        oauth_btn.clicked.connect(self.add_oauth_account)
        header_layout.addWidget(oauth_btn)
        
        sa_btn = QPushButton("+ Service Account")
        sa_btn.setStyleSheet("""
            QPushButton {
                background-color: #34A853;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2E7D32;
            }
        """)
        sa_btn.clicked.connect(self.add_service_account)
        header_layout.addWidget(sa_btn)
        
        layout.addLayout(header_layout)
        
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
        
        # Set table style
        self.accounts_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                gridline-color: #eee;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #ddd;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.accounts_table)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_accounts)
        layout.addWidget(refresh_btn)
    
    def refresh_accounts(self):
        """Refresh the accounts list"""
        try:
            response = self.api_client.get_accounts()
            if response.get('success'):
                self.accounts = response.get('accounts', [])
                self.update_accounts_table()
            else:
                QMessageBox.warning(self, "Error", f"Failed to get accounts: {response.get('error')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error refreshing accounts: {str(e)}")
    
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
        
        # Status
        status = account.get('status', 'unknown')
        status_item = QTableWidgetItem(status.title())
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
                                      "OAuth flow started in your browser.\n\n"
                                      "Please complete the authorization and return here.\n\n"
                                      "Click 'Refresh' after completing OAuth to see your account.")
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
                                   "This will remove all associated files and cannot be undone.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                response = self.api_client.delete_account(account_key)
                if response.get('success'):
                    QMessageBox.information(self, "Success", 
                                          f"Account {account_key} deleted successfully!")
                    self.refresh_accounts()
                    self.account_updated.emit()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to delete account: {response.get('error')}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error deleting account: {str(e)}")

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
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Add Service Account")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Alias
        self.alias_input = QLineEdit()
        self.alias_input.setPlaceholderText("Enter a name for this service account")
        form_layout.addRow("Alias:", self.alias_input)
        
        # Private key
        self.private_key_input = QTextEdit()
        self.private_key_input.setPlaceholderText("Paste the private key JSON content here")
        self.private_key_input.setMaximumHeight(150)
        form_layout.addRow("Private Key:", self.private_key_input)
        
        # Root folder IDs
        self.root_folders_input = QTextEdit()
        self.root_folders_input.setPlaceholderText("Enter root folder IDs (one per line)")
        self.root_folders_input.setMaximumHeight(100)
        form_layout.addRow("Root Folder IDs:", self.root_folders_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        add_btn = QPushButton("Add Service Account")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_btn.clicked.connect(self.accept)
        button_layout.addWidget(add_btn)
        
        layout.addLayout(button_layout)
    
    def get_data(self):
        """Get the entered data"""
        return {
            'alias': self.alias_input.text().strip(),
            'private_key': self.private_key_input.toPlainText().strip(),
            'root_folder_ids': [fid.strip() for fid in self.root_folders_input.toPlainText().split('\n') if fid.strip()]
        }
