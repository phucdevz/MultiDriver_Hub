"""
Sidebar component for accounts and navigation
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem,
    QFrame, QGroupBox, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon

class Sidebar(QWidget):
    """Sidebar widget for accounts and navigation"""
    
    # Signals
    account_selected = Signal(str)
    sync_requested = Signal(str, str)
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.accounts = []
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the sidebar UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Multi Driver Hub")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
                padding: 12px 16px;
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #667eea, stop:1 #764ba2);
                border: 1px solid #4c63d2;
                margin-bottom: 12px;
                text-align: center;
            }
        """)
        
        # Add account button
        self.add_account_btn = QPushButton("+ Add Account")
        self.add_account_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #10b981, stop:1 #059669);
                color: white;
                border: 1px solid #10b981;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #059669, stop:1 #047857);
                border: 1px solid #059669;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #047857, stop:1 #065f46);
            }
        """)
        self.add_account_btn.clicked.connect(self.show_add_account_dialog)
        
        # Accounts list
        self.accounts_list = QListWidget()
        self.accounts_list.setStyleSheet("""
            QListWidget {
                background: #1a202c;
                border: 2px solid #4a5568;
                border-radius: 8px;
                padding: 6px;
                color: #e2e8f0;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px 12px;
                margin: 3px;
                border-radius: 6px;
                background: transparent;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: 1px solid #4c63d2;
            }
            QListWidget::item:hover {
                background: rgba(102, 126, 234, 0.1);
                border: 1px solid rgba(102, 126, 234, 0.3);
            }
        """)
        
        # Account details group
        self.account_details = QGroupBox("Account Details")
        self.account_details.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #e2e8f0;
                border: 2px solid #4a5568;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background: #1a202c;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: #667eea;
            }
        """)
        
        self.account_details_layout = QVBoxLayout(self.account_details)
        self.account_details_layout.setSpacing(8)
        
        # Account info label
        self.account_info_label = QLabel("Select an account to view details")
        self.account_info_label.setStyleSheet("""
            QLabel {
                color: #a0aec0;
                padding: 8px 12px;
                border-radius: 6px;
                background: rgba(160, 174, 192, 0.1);
                font-size: 12px;
                line-height: 1.5;
                border: 1px solid rgba(160, 174, 192, 0.2);
            }
        """)
        
        # Sync controls layout
        self.sync_controls_layout = QHBoxLayout()
        self.sync_controls_layout.setSpacing(8)
        
        # Initial sync button
        self.initial_sync_btn = QPushButton("Initial Sync")
        self.initial_sync_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f59e0b, stop:1 #d97706);
                color: white;
                border: 2px solid #f59e0b;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
                min-height: 32px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #d97706, stop:1 #b45309);
                border: 2px solid #d97706;
            }
        """)
        
        # Incremental sync button
        self.incremental_sync_btn = QPushButton("Incremental")
        self.incremental_sync_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f59e0b, stop:1 #d97706);
                color: white;
                border: 2px solid #f59e0b;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
                min-height: 32px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #d97706, stop:1 #b45309);
                border: 2px solid #d97706;
            }
        """)
        
        # Sync progress
        self.sync_progress = QProgressBar()
        self.sync_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #4a5568;
                border-radius: 6px;
                text-align: center;
                background: #1a202c;
                height: 18px;
                font-weight: bold;
                color: white;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #10b981, stop:1 #059669);
                border-radius: 4px;
                margin: 1px;
            }
        """)
        
        # Account status label
        self.account_status_label = QLabel("Status: Idle")
        self.account_status_label.setStyleSheet("""
            QLabel {
                color: #48bb78;
                padding: 6px 8px;
                border-radius: 6px;
                background: rgba(72, 187, 120, 0.1);
                font-size: 11px;
                font-weight: bold;
                margin: 6px 0;
                border: 1px solid rgba(72, 187, 120, 0.3);
                text-align: center;
            }
        """)
        
        # Footer
        footer = QLabel("Multi Driver Made With ♥️ By Truong Phuc")
        footer.setStyleSheet("""
            QLabel {
                color: #718096;
                font-size: 11px;
                padding: 10px;
                text-align: center;
                border-radius: 6px;
                background: rgba(113, 128, 150, 0.1);
                border: 1px solid rgba(113, 128, 150, 0.2);
                margin-top: 8px;
            }
        """)
        
        layout.addWidget(title)
        layout.addWidget(self.add_account_btn)
        layout.addWidget(self.accounts_list)
        layout.addWidget(self.account_details)
        self.account_details_layout.addWidget(self.account_info_label)
        self.account_details_layout.addLayout(self.sync_controls_layout)
        self.account_details_layout.addWidget(self.sync_progress)
        self.account_details_layout.addWidget(self.account_status_label)
        layout.addWidget(footer)
        
        # Stretch to push everything to the top
        layout.addStretch()
    
    def setup_connections(self):
        """Setup signal connections"""
        self.accounts_list.itemClicked.connect(self.on_account_selected)
    
    def update_accounts(self, accounts):
        """Update the accounts list"""
        self.accounts = accounts
        self.accounts_list.clear()
        
        for account in accounts:
            item = QListWidgetItem()
            
            # Create account widget
            account_widget = self.create_account_widget(account)
            item.setSizeHint(account_widget.sizeHint())
            
            self.accounts_list.addItem(item)
            self.accounts_list.setItemWidget(item, account_widget)
    
    def create_account_widget(self, account):
        """Create a widget for an account item"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Account name/email
        name = account.get('account_key') or 'Unknown'
        name_label = QLabel(name)
        name_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        name_label.setStyleSheet("color: #333;")
        layout.addWidget(name_label)
        
        # Account type and status
        auth_type = account.get('auth_type', 'unknown')
        status = account.get('status', 'unknown')
        
        info_text = f"Type: {auth_type.title()} | Status: {status.title()}"
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #666; font-size: 9px;")
        layout.addWidget(info_label)
        
        # Last sync info
        last_sync = account.get('last_sync_at')
        if last_sync and len(last_sync) >= 10:
            sync_label = QLabel(f"Last sync: {last_sync[:10]}")
            sync_label.setStyleSheet("color: #888; font-size: 8px;")
            layout.addWidget(sync_label)
        
        return widget
    
    def on_account_selected(self, item):
        """Handle account selection"""
        index = self.accounts_list.row(item)
        if 0 <= index < len(self.accounts):
            account = self.accounts[index]
            self.show_account_details(account)
            self.account_selected.emit(account.get('account_key'))
            
            # Emit signal to refresh search results for this account
            self.parent().parent().search_results.set_selected_account(account.get('account_key'))
    
    def show_account_details(self, account):
        """Show details for selected account"""
        self.account_details.setVisible(True)
        
        # Update account info
        name = account.get('account_key') or 'Unknown'
        auth_type = account.get('auth_type', 'unknown')
        status = account.get('status', 'unknown')
        
        info_text = f"""
        <b>Account:</b> {name}<br>
        <b>Type:</b> {auth_type.title()}<br>
        <b>Status:</b> {status.title()}<br>
        <b>Connected:</b> {account.get('connected_at', 'Unknown')[:10] if account.get('connected_at') else 'Unknown'}
        """
        
        last_sync = account.get('last_sync_at')
        if last_sync and len(last_sync) >= 10:
            info_text += f"<br><b>Last Sync:</b> {last_sync[:10]}"
        
        self.account_info_label.setText(info_text)
        
        # Update status label
        self.update_status_label(status)
        
        # Store current account for sync operations
        self.current_account = account
    
    def update_status_label(self, status):
        """Update the status label with appropriate styling"""
        status_colors = {
            'idle': '#4CAF50',
            'crawling': '#FF9800',
            'syncing': '#2196F3',
            'error': '#F44336'
        }
        
        color = status_colors.get(status, '#666')
        self.account_status_label.setText(f"Status: {status.title()}")
        self.account_status_label.setStyleSheet(f"""
            padding: 5px; 
            border-radius: 3px; 
            background-color: {color}; 
            color: white; 
            font-weight: bold;
        """)
    
    def start_initial_sync(self):
        """Start initial sync for current account"""
        if hasattr(self, 'current_account'):
            account_key = self.current_account.get('account_key')
            self.sync_requested.emit(account_key, 'initial')
            self.show_sync_progress()
    
    def start_incremental_sync(self):
        """Start incremental sync for current account"""
        if hasattr(self, 'current_account'):
            account_key = self.current_account.get('account_key')
            self.sync_requested.emit(account_key, 'incremental')
            self.show_sync_progress()
    
    def show_sync_progress(self):
        """Show sync progress bar"""
        self.sync_progress.setVisible(True)
        self.sync_progress.setRange(0, 0)  # Indeterminate progress
    
    def hide_sync_progress(self):
        """Hide sync progress bar"""
        self.sync_progress.setVisible(False)
    
    def get_api_client(self):
        """Get API client from parent hierarchy"""
        try:
            # Method 1: Try to get from main window
            if hasattr(self, 'parent') and hasattr(self.parent(), 'api_client'):
                return self.parent().api_client
            
            # Method 2: Try to get from main window through parent chain
            parent = self.parent()
            if parent and hasattr(parent, 'parent') and hasattr(parent.parent(), 'api_client'):
                return parent.parent().api_client
            
            # Method 3: Try to get from QApplication
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                for widget in app.topLevelWidgets():
                    if hasattr(widget, 'api_client'):
                        return widget.api_client
            
            return None
        except Exception as e:
            print(f"Error getting API client: {e}")
            return None

    def show_add_account_dialog(self):
        """Show dialog to add new account"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTabWidget, QWidget, QFrame
        
        class AddAccountDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Add Google Drive Account")
                self.setModal(True)
                self.resize(450, 320)
                self.setStyleSheet("""
                    QDialog {
                        background: #1a202c;
                        color: #e2e8f0;
                    }
                    QTabWidget::pane {
                        border: 1px solid #4a5568;
                        border-radius: 6px;
                        background: #2d3748;
                    }
                    QTabBar::tab {
                        background: #4a5568;
                        color: #e2e8f0;
                        padding: 8px 16px;
                        margin-right: 2px;
                        border-radius: 4px 4px 0 0;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QTabBar::tab:selected {
                        background: #667eea;
                        color: white;
                    }
                    QTabBar::tab:hover {
                        background: #5a6fd8;
                    }
                """)
                self.setup_ui()
            
            def setup_ui(self):
                layout = QVBoxLayout(self)
                layout.setContentsMargins(15, 15, 15, 15)
                layout.setSpacing(12)
                
                # Title
                title = QLabel("Choose Account Type")
                title.setStyleSheet("""
                    QLabel {
                        font-size: 18px;
                        font-weight: bold;
                        color: #667eea;
                        text-align: center;
                        padding: 12px 16px;
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                            stop:0 rgba(102, 126, 234, 0.1), stop:1 rgba(118, 75, 162, 0.1));
                        border-radius: 8px;
                        border: 1px solid rgba(102, 126, 234, 0.3);
                    }
                """)
                title.setAlignment(Qt.AlignCenter)
                layout.addWidget(title)
                
                # Tab widget for different account types
                tabs = QTabWidget()
                
                # OAuth Tab
                oauth_tab = QWidget()
                oauth_layout = QVBoxLayout(oauth_tab)
                oauth_layout.setContentsMargins(20, 20, 20, 20)
                oauth_layout.setSpacing(12)
                
                # OAuth info card
                oauth_card = QFrame()
                oauth_card.setStyleSheet("""
                    QFrame {
                        background: rgba(66, 133, 244, 0.1);
                        border: 1px solid rgba(66, 133, 244, 0.3);
                        border-radius: 8px;
                        padding: 12px;
                    }
                """)
                oauth_card_layout = QVBoxLayout(oauth_card)
                oauth_card_layout.setSpacing(8)
                
                oauth_info = QLabel(
                    "🔐 OAuth Account (Recommended)\n\n"
                    "• Connect your personal Google account\n"
                    "• Access to all files in My Drive\n"
                    "• Secure token-based authentication\n"
                    "• Full sync capabilities\n"
                    "• Automatic token refresh"
                )
                oauth_info.setStyleSheet("""
                    QLabel {
                        color: #e2e8f0;
                        font-size: 12px;
                        line-height: 1.4;
                        padding: 12px;
                        background: rgba(66, 133, 244, 0.05);
                        border-radius: 6px;
                        border: 1px solid rgba(66, 133, 244, 0.2);
                    }
                """)
                oauth_info.setAlignment(Qt.AlignCenter)
                oauth_card_layout.addWidget(oauth_info)
                
                oauth_btn = QPushButton("🚀 Start OAuth Flow")
                oauth_btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #4285F4, stop:1 #3367D6);
                        color: white;
                        border: 1px solid #4285F4;
                        border-radius: 6px;
                        padding: 10px 20px;
                        font-weight: bold;
                        font-size: 13px;
                        min-height: 36px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #3367D6, stop:1 #2E5BB8);
                        border: 1px solid #3367D6;
                    }
                    QPushButton:pressed {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #2E5BB8, stop:1 #1E4B98);
                    }
                """)
                oauth_btn.clicked.connect(self.start_oauth)
                oauth_card_layout.addWidget(oauth_btn)
                
                oauth_layout.addWidget(oauth_card)
                oauth_layout.addStretch()
                
                tabs.addTab(oauth_tab, "🔐 OAuth Account")
                
                # Service Account Tab
                sa_tab = QWidget()
                sa_layout = QVBoxLayout(sa_tab)
                sa_layout.setContentsMargins(20, 20, 20, 20)
                sa_layout.setSpacing(12)
                
                # Service Account info card
                sa_card = QFrame()
                sa_card.setStyleSheet("""
                    QFrame {
                        background: rgba(52, 168, 83, 0.1);
                        border: 1px solid rgba(52, 168, 83, 0.3);
                        border-radius: 8px;
                        padding: 12px;
                    }
                """)
                sa_card_layout = QVBoxLayout(sa_card)
                sa_card_layout.setSpacing(8)
                
                sa_info = QLabel(
                    "⚙️ Service Account\n\n"
                    "• Connect shared folders only\n"
                    "• No user interaction required\n"
                    "• Limited to specific folders\n"
                    "• Requires manual folder sharing\n"
                    "• Ideal for automation"
                )
                sa_info.setStyleSheet("""
                    QLabel {
                        color: #e2e8f0;
                        font-size: 12px;
                        line-height: 1.4;
                        padding: 12px;
                        background: rgba(52, 168, 83, 0.05);
                        border-radius: 6px;
                        border: 1px solid rgba(52, 168, 83, 0.2);
                    }
                """)
                sa_info.setAlignment(Qt.AlignCenter)
                sa_card_layout.addWidget(sa_info)
                
                sa_btn = QPushButton("⚙️ Add Service Account")
                sa_btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #34A853, stop:1 #2E8B47);
                        color: white;
                        border: 1px solid #34A853;
                        border-radius: 6px;
                        padding: 10px 20px;
                        font-weight: bold;
                        font-size: 13px;
                        min-height: 36px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #2E8B47, stop:1 #228B22);
                        border: 1px solid #2E8B47;
                    }
                    QPushButton:pressed {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #228B22, stop:1 #006400);
                    }
                """)
                sa_btn.clicked.connect(self.add_service_account)
                sa_card_layout.addWidget(sa_btn)
                
                sa_layout.addWidget(sa_card)
                sa_layout.addStretch()
                
                tabs.addTab(sa_tab, "⚙️ Service Account")
                
                layout.addWidget(tabs)
                
                # Close button
                close_btn = QPushButton("❌ Close")
                close_btn.setStyleSheet("""
                    QPushButton {
                        background: #6b7280;
                        color: white;
                        border: 1px solid #6b7280;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: bold;
                        font-size: 12px;
                        min-height: 32px;
                    }
                    QPushButton:hover {
                        background: #4b5563;
                        border: 1px solid #4b5563;
                    }
                """)
                close_btn.clicked.connect(self.close)
                layout.addWidget(close_btn)
            
            def start_oauth(self):
                """Start OAuth flow"""
                try:
                    # Get API client from parent sidebar
                    api_client = self.parent().get_api_client()
                    print(f"API Client from sidebar: {api_client}")  # Debug
                    
                    if api_client:
                        # Test health check first
                        health_response = api_client.health_check()
                        
                        # Call backend to start OAuth
                        response = api_client.start_oauth()
                        
                        if response and response.get('success'):
                            auth_url = response.get('authUrl')
                            if auth_url:
                                # Open browser for OAuth
                                import webbrowser
                                webbrowser.open(auth_url)
                                
                                QMessageBox.information(self, "OAuth Started", 
                                    "✅ OAuth flow started successfully!\n\n"
                                    "🌐 Your browser has opened for Google authentication.\n\n"
                                    "📋 Please complete the authorization and return here.\n\n"
                                    "🔄 Click 'Refresh' after completing OAuth to see your account.")
                                self.accept()
                            else:
                                QMessageBox.warning(self, "Error", "❌ No auth URL received from backend")
                        else:
                            error_msg = response.get('error', 'Unknown error') if response else 'No response'
                            QMessageBox.warning(self, "Error", f"❌ Failed to start OAuth: {error_msg}")
                    else:
                        QMessageBox.warning(self, "Error", "❌ Cannot access API client from sidebar")
                        
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"❌ Error starting OAuth: {str(e)}")
                    print(f"OAuth error: {e}")
            
            def add_service_account(self):
                """Add service account"""
                try:
                    # Get API client from parent sidebar
                    api_client = self.parent().get_api_client()
                    print(f"API Client from sidebar: {api_client}")  # Debug
                    
                    if api_client:
                        # Show input dialog for service account details
                        from PySide6.QtWidgets import QInputDialog, QLineEdit
                        
                        # Get alias
                        alias, ok = QInputDialog.getText(self, "Service Account Alias", 
                            "Enter a name for this service account:")
                        if not ok or not alias:
                            return
                        
                        # Get private key
                        private_key, ok = QInputDialog.getText(self, "Private Key", 
                            "Enter the private key (JSON content):", QLineEdit.Normal, "")
                        if not ok or not private_key:
                            return
                        
                        # Get root folder IDs
                        folder_ids, ok = QInputDialog.getText(self, "Root Folder IDs", 
                            "Enter comma-separated folder IDs to access:")
                        if not ok or not folder_ids:
                            return
                        
                        # Call backend to register service account
                        response = api_client.register_service_account(alias, private_key, folder_ids)
                        
                        if response and response.get('success'):
                            QMessageBox.information(self, "Success", 
                                f"✅ Service Account '{alias}' added successfully!\n\n"
                                "🔄 The account will appear in your accounts list.")
                            self.accept()
                        else:
                            error_msg = response.get('error', 'Unknown error') if response else 'No response'
                            QMessageBox.warning(self, "Error", f"❌ Failed to add service account: {error_msg}")
                    else:
                        QMessageBox.warning(self, "Error", "❌ Cannot access API client - tried multiple methods")
                        
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"❌ Error adding service account: {str(e)}")
                    print(f"Service Account error: {e}")
        
        dialog = AddAccountDialog(self)
        dialog.exec()
    
    def update_sync_status(self, account_key, status):
        """Update sync status for an account"""
        # Find and update the account in the list
        for i, account in enumerate(self.accounts):
            key = account.get('account_key')
            if key == account_key:
                account['status'] = status
                
                # Update the list item
                item = self.accounts_list.item(i)
                if item:
                    account_widget = self.create_account_widget(account)
                    item.setSizeHint(account_widget.sizeHint())
                    self.accounts_list.setItemWidget(item, account_widget)
                
                # Update details if this account is currently selected
                if hasattr(self, 'current_account'):
                    current_key = self.current_account.get('account_key')
                    if current_key == account_key:
                        self.update_status_label(status)
                
                break

    def refresh_texts(self):
        """Refresh UI texts after language change"""
        # Update title
        title = self.findChild(QLabel)
        if title and title.text() == "Accounts":
            title.setText(i18n.get("accounts"))
        
        # Update add account button
        add_account_btn = self.findChild(QPushButton, "+ Add Account")
        if add_account_btn:
            add_account_btn.setText(i18n.get("add_account"))
        
        # Update account details group title
        if self.account_details:
            self.account_details.setTitle(i18n.get("account_details"))
        
        # Update account info label
        if self.account_info_label:
            self.account_info_label.setText(i18n.get("select_account_details"))
        
        # Update sync button texts
        if self.initial_sync_btn:
            self.initial_sync_btn.setText(i18n.get("initial_sync"))
        if self.incremental_sync_btn:
            self.incremental_sync_btn.setText(i18n.get("incremental_sync"))
        
        # Update account list items (if any)
        self._refresh_account_list_texts()
    
    def _refresh_account_list_texts(self):
        """Refresh texts in account list items"""
        for i in range(self.accounts_list.count()):
            item = self.accounts_list.item(i)
            if item:
                # Update account type and status texts if they exist
                widget = self.accounts_list.itemWidget(item)
                if widget:
                    # This would need to be implemented based on how account items are structured
                    pass
