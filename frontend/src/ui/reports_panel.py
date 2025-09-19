"""
Reports panel component for displaying system reports
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QTabWidget, QGroupBox, QProgressBar,
    QSpinBox, QComboBox, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon

class ReportsPanel(QWidget):
    """Reports and analytics panel"""
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        
        self.setup_ui()
        # Don't auto-refresh on init to prevent API spam
        # self.refresh_reports()
    
    def setup_ui(self):
        """Setup the reports panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Reports & Analytics")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_reports)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Reports tabs
        self.reports_tabs = QTabWidget()
        
        # Health tab
        self.health_tab = self.create_health_tab()
        self.reports_tabs.addTab(self.health_tab, "System Health")
        
        # Duplicates tab
        self.duplicates_tab = self.create_duplicates_tab()
        self.reports_tabs.addTab(self.duplicates_tab, "Duplicate Files")
        
        # Storage tab
        self.storage_tab = self.create_storage_tab()
        self.reports_tabs.addTab(self.storage_tab, "Storage Analysis")
        
        # Sync Performance tab
        self.sync_tab = self.create_sync_tab()
        self.reports_tabs.addTab(self.sync_tab, "Sync Performance")
        
        layout.addWidget(self.reports_tabs)
    
    def create_health_tab(self):
        """Create system health tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Health score
        health_group = QGroupBox("System Health Score")
        health_layout = QVBoxLayout(health_group)
        
        self.health_score_label = QLabel("Loading...")
        self.health_score_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.health_score_label.setAlignment(Qt.AlignCenter)
        self.health_score_label.setStyleSheet("padding: 20px;")
        health_layout.addWidget(self.health_score_label)
        
        layout.addWidget(health_group)
        
        # Overall stats
        stats_group = QGroupBox("Overall Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.overall_stats_label = QLabel("Loading...")
        self.overall_stats_label.setStyleSheet("padding: 10px;")
        stats_layout.addWidget(self.overall_stats_label)
        
        layout.addWidget(stats_group)
        
        # Account status
        accounts_group = QGroupBox("Account Status")
        accounts_layout = QVBoxLayout(accounts_group)
        
        self.accounts_status_label = QLabel("Loading...")
        self.accounts_status_label.setStyleSheet("padding: 10px;")
        accounts_layout.addWidget(self.accounts_status_label)
        
        layout.addWidget(accounts_group)
        
        layout.addStretch()
        return widget
    
    def create_duplicates_tab(self):
        """Create duplicate files tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Min Size:"))
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setRange(0, 999999999)
        self.min_size_spin.setSuffix(" B")
        self.min_size_spin.setValue(1024)  # 1KB
        controls_layout.addWidget(self.min_size_spin)
        
        controls_layout.addWidget(QLabel("Group By:"))
        self.group_by_combo = QComboBox()
        self.group_by_combo.addItems(["MD5 Hash", "File Size", "Both"])
        controls_layout.addWidget(self.group_by_combo)
        
        controls_layout.addWidget(QLabel("Limit:"))
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(10, 1000)
        self.limit_spin.setValue(100)
        controls_layout.addWidget(self.limit_spin)
        
        scan_btn = QPushButton("Scan Duplicates")
        scan_btn.setStyleSheet("""
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
        scan_btn.clicked.connect(self.scan_duplicates)
        controls_layout.addWidget(scan_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Results
        self.duplicates_table = QTableWidget()
        self.duplicates_table.setColumnCount(6)
        self.duplicates_table.setHorizontalHeaderLabels([
            "Group", "Count", "Size", "Files", "Accounts", "Potential Savings"
        ])
        
        # Set table properties
        header = self.duplicates_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.duplicates_table)
        
        # Summary
        self.duplicates_summary = QLabel("No duplicate scan performed")
        self.duplicates_summary.setStyleSheet("padding: 10px; font-weight: bold;")
        layout.addWidget(self.duplicates_summary)
        
        return widget
    
    def create_storage_tab(self):
        """Create storage analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Account filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Account:"))
        self.storage_account_filter = QComboBox()
        self.storage_account_filter.addItem("All Accounts", "")
        filter_layout.addWidget(self.storage_account_filter)
        
        filter_layout.addStretch()
        
        refresh_storage_btn = QPushButton("Refresh Storage Data")
        refresh_storage_btn.setStyleSheet("""
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
        refresh_storage_btn.clicked.connect(self.refresh_storage_data)
        filter_layout.addWidget(refresh_storage_btn)
        
        layout.addLayout(filter_layout)
        
        # Storage by folder
        folder_group = QGroupBox("Storage by Folder")
        folder_layout = QVBoxLayout(folder_group)
        
        self.folder_storage_table = QTableWidget()
        self.folder_storage_table.setColumnCount(4)
        self.folder_storage_table.setHorizontalHeaderLabels([
            "Folder", "Files", "Size", "Average Size"
        ])
        
        header = self.folder_storage_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        folder_layout.addWidget(self.folder_storage_table)
        layout.addWidget(folder_group)
        
        # Monthly storage
        monthly_group = QGroupBox("Monthly Storage Growth")
        monthly_layout = QVBoxLayout(monthly_group)
        
        self.monthly_storage_table = QTableWidget()
        self.monthly_storage_table.setColumnCount(3)
        self.monthly_storage_table.setHorizontalHeaderLabels([
            "Month", "Files", "Size"
        ])
        
        header = self.monthly_storage_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        monthly_layout.addWidget(self.monthly_storage_table)
        layout.addWidget(monthly_group)
        
        return widget
    
    def create_sync_tab(self):
        """Create sync performance tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Sync performance table
        self.sync_table = QTableWidget()
        self.sync_table.setColumnCount(6)
        self.sync_table.setHorizontalHeaderLabels([
            "Account", "Status", "Last Sync", "Days Ago", "Account Age", "Health"
        ])
        
        # Set table properties
        header = self.sync_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.sync_table)
        
        # Sync recommendations
        self.sync_recommendations = QLabel("Loading sync performance data...")
        self.sync_recommendations.setStyleSheet("padding: 10px; font-weight: bold;")
        layout.addWidget(self.sync_recommendations)
        
        return widget
    
    def refresh_reports(self):
        """Refresh all reports with rate limiting check"""
        # Check if backend is connected by trying to get accounts
        try:
            accounts_response = self.api_client.get_accounts()
            if not accounts_response.get('success'):
                print("⚠️ Skipping reports refresh - backend not connected")
                return
        except Exception as e:
            print(f"⚠️ Skipping reports refresh - backend error: {str(e)}")
            return
            
        # Check if we're rate limited before making requests
        if hasattr(self.api_client, 'is_rate_limited') and self.api_client.is_rate_limited():
            print("Skipping reports refresh - rate limited")
            return
        
        # Add delay between API calls to prevent spam
        QTimer.singleShot(1000, self.refresh_health_report)
        QTimer.singleShot(2000, self.refresh_storage_data)
        QTimer.singleShot(3000, self.refresh_sync_performance)
    
    def refresh_health_report(self):
        """Refresh system health report"""
        try:
            response = self.api_client.get_health_report()
            if response.get('success'):
                data = response.get('data', {})
                overall = data.get('overall', {})
                accounts = data.get('accounts', [])
                sync_status = data.get('syncStatus', [])
                
                # Update health score
                health_score = overall.get('healthScore', 0)
                if health_score is None:
                    health_score = 0
                self.health_score_label.setText(f"{health_score}/100")
                
                # Color code health score
                if health_score >= 80:
                    color = "#4CAF50"  # Green
                elif health_score >= 60:
                    color = "#FF9800"  # Orange
                else:
                    color = "#F44336"  # Red
                
                self.health_score_label.setStyleSheet(f"""
                    padding: 20px; 
                    background-color: {color}; 
                    color: white; 
                    border-radius: 10px;
                """)
                
                # Update overall stats
                total_files = overall.get('totalFiles', 0) or 0
                total_size = overall.get('totalSize', 0) or 0
                total_accounts = overall.get('totalAccounts', 0) or 0
                
                stats_text = f"""
                <b>Total Files:</b> {total_files:,}<br>
                <b>Total Size:</b> {self.format_size(total_size)}<br>
                <b>Total Accounts:</b> {total_accounts}
                """
                self.overall_stats_label.setText(stats_text)
                
                # Update account status
                status_text = ""
                for status in sync_status:
                    count = status.get('count', 0) or 0
                    name = status.get('status', 'Unknown')
                    status_text += f"<b>{name.title()}:</b> {count}<br>"
                
                if not status_text:
                    status_text = "No account status data available"
                
                self.accounts_status_label.setText(status_text)
                
            else:
                self.health_score_label.setText("Error")
                self.health_score_label.setStyleSheet("padding: 20px; background-color: #F44336; color: white; border-radius: 10px;")
                
        except Exception as e:
            self.health_score_label.setText("Error")
            self.health_score_label.setStyleSheet("padding: 20px; background-color: #F44336; color: white; border-radius: 10px;")
            print(f"Error refreshing health report: {e}")
    
    def scan_duplicates(self):
        """Scan for duplicate files"""
        try:
            min_size = self.min_size_spin.value()
            group_by_map = {"MD5 Hash": "md5", "File Size": "size", "Both": "both"}
            group_by = group_by_map[self.group_by_combo.currentText()]
            limit = self.limit_spin.value()
            
            response = self.api_client.get_dedup_report(min_size, group_by, limit)
            if response.get('success'):
                data = response.get('data', {})
                duplicates = data.get('duplicates', [])
                summary = data.get('summary', {})
                
                # Update table
                self.duplicates_table.setRowCount(0)
                for dup in duplicates:
                    self.add_duplicate_row(dup, group_by)
                
                # Update summary
                total_groups = summary.get('totalGroups', 0) or 0
                total_duplicates = summary.get('totalDuplicates', 0) or 0
                potential_savings = summary.get('potentialSavings', 0) or 0
                
                summary_text = f"""
                <b>Summary:</b> {total_groups} duplicate groups found, 
                {total_duplicates} total files, 
                potential savings: {self.format_size(potential_savings)}
                """
                self.duplicates_summary.setText(summary_text)
                
            else:
                QMessageBox.warning(self, "Error", f"Failed to scan duplicates: {response.get('error')}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error scanning duplicates: {str(e)}")
    
    def add_duplicate_row(self, duplicate, group_by):
        """Add a duplicate group to the table"""
        row = self.duplicates_table.rowCount()
        self.duplicates_table.insertRow(row)
        
        # Group identifier
        if group_by == "md5":
            group_id = duplicate.get('md5', 'Unknown')[:8] + "..."
        elif group_by == "size":
            group_id = self.format_size(duplicate.get('size', 0))
        else:
            group_id = f"{duplicate.get('md5', 'Unknown')[:8]}... ({self.format_size(duplicate.get('size', 0))})"
        
        self.duplicates_table.setItem(row, 0, QTableWidgetItem(group_id))
        
        # Count
        count = duplicate.get('count', 0) or 0
        self.duplicates_table.setItem(row, 1, QTableWidgetItem(str(count)))
        
        # Size
        size = duplicate.get('size', 0) or 0
        self.duplicates_table.setItem(row, 2, QTableWidgetItem(self.format_size(size)))
        
        # Files
        file_names = duplicate.get('fileNames', [])
        files_text = ", ".join(file_names[:3])
        if len(file_names) > 3:
            files_text += f" (+{len(file_names) - 3} more)"
        self.duplicates_table.setItem(row, 3, QTableWidgetItem(files_text))
        
        # Accounts
        accounts = duplicate.get('accounts', [])
        accounts_text = ", ".join(set(accounts))
        self.duplicates_table.setItem(row, 4, QTableWidgetItem(accounts_text))
        
        # Potential savings
        savings = duplicate.get('potentialSavings', 0) or 0
        self.duplicates_table.setItem(row, 5, QTableWidgetItem(self.format_size(savings)))
    
    def refresh_storage_data(self):
        """Refresh storage analysis data"""
        try:
            account_key = self.storage_account_filter.currentData()
            response = self.api_client.get_storage_report(account_key)
            
            if response.get('success'):
                data = response.get('data', {})
                
                # Update folder storage
                folder_storage = data.get('folderStorage', [])
                self.folder_storage_table.setRowCount(0)
                for folder in folder_storage:
                    row = self.folder_storage_table.rowCount()
                    self.folder_storage_table.insertRow(row)
                    
                    self.folder_storage_table.setItem(row, 0, QTableWidgetItem(folder.get('folder_name', 'Unknown')))
                    self.folder_storage_table.setItem(row, 1, QTableWidgetItem(str(folder.get('file_count', 0))))
                    self.folder_storage_table.setItem(row, 2, QTableWidgetItem(self.format_size(folder.get('total_size', 0))))
                    self.folder_storage_table.setItem(row, 3, QTableWidgetItem(self.format_size(folder.get('avg_size', 0))))
                
                # Update monthly storage
                monthly_storage = data.get('monthlyStorage', [])
                self.monthly_storage_table.setRowCount(0)
                for month in monthly_storage:
                    row = self.monthly_storage_table.rowCount()
                    self.monthly_storage_table.insertRow(row)
                    
                    self.monthly_storage_table.setItem(row, 0, QTableWidgetItem(month.get('month', 'Unknown')))
                    self.monthly_storage_table.setItem(row, 1, QTableWidgetItem(str(month.get('file_count', 0))))
                    self.monthly_storage_table.setItem(row, 2, QTableWidgetItem(self.format_size(month.get('total_size', 0))))
                
            else:
                QMessageBox.warning(self, "Error", f"Failed to get storage data: {response.get('error')}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error refreshing storage data: {str(e)}")
    
    def refresh_sync_performance(self):
        """Refresh sync performance data"""
        try:
            response = self.api_client.get_sync_performance_report()
            if response.get('success'):
                data = response.get('data', {})
                performance = data.get('performance', [])
                
                # Update sync table
                self.sync_table.setRowCount(0)
                for perf in performance:
                    row = self.sync_table.rowCount()
                    self.sync_table.insertRow(row)
                    
                    self.sync_table.setItem(row, 0, QTableWidgetItem(perf.get('accountKey', 'Unknown')))
                    self.sync_table.setItem(row, 1, QTableWidgetItem(perf.get('status', 'Unknown')))
                    self.sync_table.setItem(row, 2, QTableWidgetItem(perf.get('lastSyncAt', 'Never')[:10] if perf.get('lastSyncAt') else 'Never'))
                    
                    last_sync_age = perf.get('lastSyncAge')
                    if last_sync_age is not None and last_sync_age >= 0:
                        age_text = f"{last_sync_age} days"
                    else:
                        age_text = "Never"
                    self.sync_table.setItem(row, 3, QTableWidgetItem(age_text))
                    
                    account_age = perf.get('accountAge', 0) or 0
                    if account_age is not None and account_age >= 0:
                        age_text = f"{account_age} days"
                    else:
                        age_text = "Unknown"
                    self.sync_table.setItem(row, 4, QTableWidgetItem(age_text))
                    
                    health = perf.get('syncHealth', 'Unknown')
                    health_item = QTableWidgetItem(health.title())
                    
                    # Color code health
                    if health == 'excellent':
                        health_item.setBackground(Qt.green)
                    elif health == 'good':
                        health_item.setBackground(Qt.lightGreen)
                    elif health == 'fair':
                        health_item.setBackground(Qt.yellow)
                    elif health == 'poor':
                        health_item.setBackground(Qt.red)
                    elif health == 'error':
                        health_item.setBackground(Qt.darkRed)
                        health_item.setForeground(Qt.white)
                    
                    self.sync_table.setItem(row, 5, health_item)
                
                # Generate recommendations
                recommendations = self.generate_sync_recommendations(performance)
                self.sync_recommendations.setText(recommendations)
                
            else:
                QMessageBox.warning(self, "Error", f"Failed to get sync performance: {response.get('error')}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error refreshing sync performance: {str(e)}")
    
    def generate_sync_recommendations(self, performance):
        """Generate sync recommendations based on performance data"""
        if not performance:
            return "No sync performance data available"
        
        recommendations = []
        
        for perf in performance:
            account = perf.get('accountKey', 'Unknown')
            health = perf.get('syncHealth', 'Unknown')
            last_sync_age = perf.get('lastSyncAge')
            
            if health == 'error':
                recommendations.append(f"⚠️ {account}: Account has sync errors, check configuration")
            elif health == 'poor' and last_sync_age is not None and last_sync_age >= 0:
                recommendations.append(f"🔴 {account}: Last sync was {last_sync_age} days ago, consider manual sync")
            elif health == 'fair' and last_sync_age is not None and last_sync_age >= 0:
                recommendations.append(f"🟡 {account}: Last sync was {last_sync_age} days ago, monitor closely")
        
        if not recommendations:
            return "✅ All accounts are syncing well!"
        
        return "<br>".join(recommendations)
    
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
    
    def update_accounts_list(self, accounts):
        """Update account filter lists"""
        # Update storage account filter
        self.storage_account_filter.clear()
        self.storage_account_filter.addItem("All Accounts", "")
        
        for account in accounts:
            name = account.get('account_key') or 'Unknown'
            key = account.get('account_key')
            self.storage_account_filter.addItem(name, key)

    def refresh_texts(self):
        """Refresh UI texts after language change"""
        # Update panel title
        if hasattr(self, 'title_label'):
            self.title_label.setText(i18n.get("reports"))
        
        # Update tab texts
        if hasattr(self, 'tab_widget'):
            self.tab_widget.setTabText(0, i18n.get("storage_usage"))
            self.tab_widget.setTabText(1, i18n.get("file_types"))
            self.tab_widget.setTabText(2, i18n.get("sync_status"))
            self.tab_widget.setTabText(3, i18n.get("activity_log"))
        
        # Update button texts
        if hasattr(self, 'refresh_button'):
            self.refresh_button.setText(i18n.get("refresh"))
        if hasattr(self, 'export_button'):
            self.export_button.setText(i18n.get("export_results"))
            
    def on_user_authenticated(self):
        """Called when user successfully logs in"""
        # Refresh reports after successful authentication
        QTimer.singleShot(3000, self.refresh_reports)  # Delay 3 seconds
