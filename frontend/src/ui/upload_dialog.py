"""
Upload Dialog for uploading files to Google Drive
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFileDialog, QComboBox, QLineEdit, QTextEdit,
    QFrame, QMessageBox, QApplication, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QIcon, QDragEnterEvent, QDropEvent
import os
from typing import List, Dict, Any

class UploadWorker(QThread):
    """Worker thread for file uploads"""
    
    # Signals
    progress_updated = Signal(int)
    upload_completed = Signal(dict)
    upload_error = Signal(str)
    
    def __init__(self, api_client, account_key: str, file_paths: List[str], parent_id: str = None):
        super().__init__()
        self.api_client = api_client
        self.account_key = account_key
        self.file_paths = file_paths
        self.parent_id = parent_id
        self.is_cancelled = False
    
    def run(self):
        """Run upload process"""
        try:
            total_files = len(self.file_paths)
            completed = 0
            
            for file_path in self.file_paths:
                if self.is_cancelled:
                    break
                
                try:
                    # Upload file
                    result = self.api_client.upload_file(
                        self.account_key, 
                        file_path, 
                        self.parent_id
                    )
                    
                    if result.get('success'):
                        completed += 1
                        self.upload_completed.emit({
                            'file_path': file_path,
                            'result': result
                        })
                    else:
                        self.upload_error.emit(f"Failed to upload {os.path.basename(file_path)}: {result.get('error', 'Unknown error')}")
                    
                    # Update progress
                    progress = int((completed / total_files) * 100)
                    self.progress_updated.emit(progress)
                    
                except Exception as e:
                    self.upload_error.emit(f"Error uploading {os.path.basename(file_path)}: {str(e)}")
            
        except Exception as e:
            self.upload_error.emit(f"Upload process error: {str(e)}")
    
    def cancel(self):
        """Cancel upload process"""
        self.is_cancelled = True

class UploadDialog(QDialog):
    """Dialog for uploading files to Google Drive"""
    
    # Signals
    upload_completed = Signal()
    
    def __init__(self, api_client, accounts: List[Dict[str, Any]], parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.accounts = accounts
        self.selected_files = []
        self.upload_worker = None
        
        self.setup_ui()
        self.setup_connections()
        
        # Apply theme
        self.setStyleSheet("""
            QDialog {
                background: #1a202c;
                color: #e2e8f0;
                border: 1px solid #4a5568;
                border-radius: 8px;
            }
            QLabel {
                color: #e2e8f0;
                font-size: 12px;
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
            QComboBox {
                background: #2d3748;
                border: 1px solid #4a5568;
                border-radius: 4px;
                padding: 6px 12px;
                color: #e2e8f0;
                font-size: 12px;
                min-height: 32px;
            }
            QComboBox:focus {
                border: 1px solid #667eea;
            }
            QLineEdit {
                background: #2d3748;
                border: 1px solid #4a5568;
                border-radius: 4px;
                padding: 6px 12px;
                color: #e2e8f0;
                font-size: 12px;
                min-height: 32px;
            }
            QLineEdit:focus {
                border: 1px solid #667eea;
            }
            QTextEdit {
                background: #2d3748;
                border: 1px solid #4a5568;
                border-radius: 4px;
                padding: 8px;
                color: #e2e8f0;
                font-size: 12px;
            }
            QProgressBar {
                border: 1px solid #4a5568;
                border-radius: 4px;
                text-align: center;
                background: #2d3748;
                color: #e2e8f0;
            }
            QProgressBar::chunk {
                background: #667eea;
                border-radius: 3px;
            }
        """)
    
    def setup_ui(self):
        """Setup the upload dialog UI"""
        self.setWindowTitle("Upload Files to Google Drive")
        self.setModal(True)
        self.resize(600, 500)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Upload Files to Google Drive")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Account selection
        account_frame = QFrame()
        account_frame.setStyleSheet("QFrame { border: 1px solid #4a5568; border-radius: 6px; padding: 12px; }")
        account_layout = QVBoxLayout(account_frame)
        
        account_label = QLabel("Select Account:")
        account_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        account_layout.addWidget(account_label)
        
        self.account_combo = QComboBox()
        for account in self.accounts:
            display_name = account.get('email') or account.get('sa_alias', 'Unknown')
            self.account_combo.addItem(display_name, account.get('account_key'))
        account_layout.addWidget(self.account_combo)
        
        layout.addWidget(account_frame)
        
        # File selection
        file_frame = QFrame()
        file_frame.setStyleSheet("QFrame { border: 1px solid #4a5568; border-radius: 6px; padding: 12px; }")
        file_layout = QVBoxLayout(file_frame)
        
        file_label = QLabel("Select Files:")
        file_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        file_layout.addWidget(file_label)
        
        # File selection buttons
        file_buttons_layout = QHBoxLayout()
        
        self.select_files_btn = QPushButton("📁 Select Files")
        self.select_files_btn.clicked.connect(self.select_files)
        file_buttons_layout.addWidget(self.select_files_btn)
        
        self.select_folder_btn = QPushButton("📂 Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)
        file_buttons_layout.addWidget(self.select_folder_btn)
        
        self.clear_files_btn = QPushButton("❌ Clear All")
        self.clear_files_btn.clicked.connect(self.clear_files)
        file_buttons_layout.addWidget(self.clear_files_btn)
        
        file_layout.addLayout(file_buttons_layout)
        
        # Selected files display
        self.files_text = QTextEdit()
        self.files_text.setMaximumHeight(120)
        self.files_text.setPlaceholderText("No files selected. Click 'Select Files' or 'Select Folder' to choose files to upload.")
        file_layout.addWidget(self.files_text)
        
        layout.addWidget(file_frame)
        
        # Upload options
        options_frame = QFrame()
        options_frame.setStyleSheet("QFrame { border: 1px solid #4a5568; border-radius: 6px; padding: 12px; }")
        options_layout = QVBoxLayout(options_frame)
        
        options_label = QLabel("Upload Options:")
        options_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        options_layout.addWidget(options_label)
        
        # Parent folder
        parent_layout = QHBoxLayout()
        parent_label = QLabel("Parent Folder ID:")
        parent_layout.addWidget(parent_label)
        
        self.parent_id_edit = QLineEdit()
        self.parent_id_edit.setPlaceholderText("Leave empty for root folder")
        parent_layout.addWidget(self.parent_id_edit)
        
        options_layout.addLayout(parent_layout)
        
        # Options
        self.overwrite_checkbox = QCheckBox("Overwrite existing files")
        self.overwrite_checkbox.setChecked(False)
        options_layout.addWidget(self.overwrite_checkbox)
        
        layout.addWidget(options_frame)
        
        # Progress
        progress_frame = QFrame()
        progress_frame.setStyleSheet("QFrame { border: 1px solid #4a5568; border-radius: 6px; padding: 12px; }")
        progress_layout = QVBoxLayout(progress_frame)
        
        progress_label = QLabel("Upload Progress:")
        progress_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        progress_layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to upload")
        self.status_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_frame)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.upload_btn = QPushButton("🚀 Start Upload")
        self.upload_btn.clicked.connect(self.start_upload)
        self.upload_btn.setEnabled(False)
        buttons_layout.addWidget(self.upload_btn)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.cancel_upload)
        self.cancel_btn.setEnabled(False)
        buttons_layout.addWidget(self.cancel_btn)
        
        self.close_btn = QPushButton("✖ Close")
        self.close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(self.close_btn)
        
        layout.addLayout(buttons_layout)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Update upload button state when files are selected
        self.files_text.textChanged.connect(self.update_upload_button)
    
    def select_files(self):
        """Select multiple files"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Upload",
            "",
            "All Files (*.*)"
        )
        
        if files:
            self.selected_files.extend(files)
            self.update_files_display()
    
    def select_folder(self):
        """Select folder and get all files"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Upload"
        )
        
        if folder:
            files = []
            for root, dirs, filenames in os.walk(folder):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    files.append(file_path)
            
            if files:
                self.selected_files.extend(files)
                self.update_files_display()
    
    def clear_files(self):
        """Clear all selected files"""
        self.selected_files.clear()
        self.update_files_display()
    
    def update_files_display(self):
        """Update the files display text"""
        if not self.selected_files:
            self.files_text.clear()
            self.files_text.setPlaceholderText("No files selected. Click 'Select Files' or 'Select Folder' to choose files to upload.")
        else:
            file_list = "\n".join([f"• {os.path.basename(f)} ({self.format_file_size(os.path.getsize(f))})" 
                                  for f in self.selected_files])
            self.files_text.setText(file_list)
    
    def update_upload_button(self):
        """Update upload button state"""
        self.upload_btn.setEnabled(len(self.selected_files) > 0)
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def start_upload(self):
        """Start the upload process"""
        if not self.selected_files:
            QMessageBox.warning(self, "No Files", "Please select files to upload.")
            return
        
        account_key = self.account_combo.currentData()
        if not account_key:
            QMessageBox.warning(self, "No Account", "Please select an account.")
            return
        
        # Confirm upload
        reply = QMessageBox.question(
            self,
            "Confirm Upload",
            f"Upload {len(self.selected_files)} files to Google Drive?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # Start upload worker
        self.upload_worker = UploadWorker(
            self.api_client,
            account_key,
            self.selected_files,
            self.parent_id_edit.text() if self.parent_id_edit.text().strip() else None
        )
        
        self.upload_worker.progress_updated.connect(self.update_progress)
        self.upload_worker.upload_completed.connect(self.on_upload_completed)
        self.upload_worker.upload_error.connect(self.on_upload_error)
        self.upload_worker.finished.connect(self.on_upload_finished)
        
        # Update UI
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting upload...")
        self.upload_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.select_files_btn.setEnabled(False)
        self.select_folder_btn.setEnabled(False)
        
        # Start worker
        self.upload_worker.start()
    
    def cancel_upload(self):
        """Cancel the upload process"""
        if self.upload_worker and self.upload_worker.isRunning():
            self.upload_worker.cancel()
            self.status_label.setText("Cancelling upload...")
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        self.status_label.setText(f"Uploading... {value}%")
    
    def on_upload_completed(self, data):
        """Handle upload completion for a file"""
        file_name = os.path.basename(data['file_path'])
        self.status_label.setText(f"Uploaded: {file_name}")
    
    def on_upload_error(self, error_message):
        """Handle upload error"""
        QMessageBox.warning(self, "Upload Error", error_message)
    
    def on_upload_finished(self):
        """Handle upload process finished"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Upload completed!")
        self.upload_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.select_files_btn.setEnabled(True)
        self.select_folder_btn.setEnabled(True)
        
        # Emit completion signal
        self.upload_completed.emit()
        
        # Show completion message
        QMessageBox.information(
            self,
            "Upload Complete",
            "File upload process has completed!"
        )
