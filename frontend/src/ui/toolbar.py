"""
Toolbar component with search and filters
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, 
    QPushButton, QComboBox, QLabel, QFrame, QGroupBox,
    QSpinBox, QDateEdit, QCheckBox, QGridLayout, QDialog
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QIcon

from utils.i18n import i18n

class Toolbar(QWidget):
    """Toolbar widget with search and filters"""
    
    # Signals
    search_requested = Signal(str)
    filter_changed = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.current_filters = {}
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the toolbar UI"""
        # Main layout (compact)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Search section
        search_section = QFrame()
        search_section.setStyleSheet("""
            QFrame {
                background: transparent;
                border: 1px solid #4a5568;
                border-radius: 8px;
                padding: 6px;
            }
        """)
        
        search_layout = QHBoxLayout(search_section)
        search_layout.setSpacing(8)  # Giảm từ 12 xuống 8
        
        # Search input layout
        search_input_layout = QHBoxLayout()
        search_input_layout.setSpacing(6)  # Giảm từ 8 xuống 6
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Quick search…")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #2d3748;
                border: 1px solid #4a5568;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e2e8f0;
                font-size: 12px;
                min-height: 24px;
            }
            QLineEdit:focus {
                border: 1px solid #667eea;
                background: #2d3748;
            }
        """)
        
        # Search button
        self.search_button = QPushButton("🔍 Search")
        self.search_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
                border: 1px solid #3b82f6;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: bold;
                min-height: 24px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2563eb, stop:1 #1d4ed8);
                border: 1px solid #2563eb;
            }
        """)
        self.search_button.clicked.connect(self.on_search_clicked)
        
        # Advanced button
        self.advanced_button = QPushButton("⚙️ Advanced")
        self.advanced_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f59e0b, stop:1 #d97706);
                color: white;
                border: 1px solid #f59e0b;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: bold;
                min-height: 24px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #d97706, stop:1 #b45309);
                border: 1px solid #d97706;
            }
        """)
        self.advanced_button.clicked.connect(self.open_advanced_dialog)
        
        # Advanced filters frame
        # Prepare advanced filters UI (used inside modal dialog)
        self.filters_frame = QFrame()
        self.filters_frame.setVisible(False)
        self.filters_frame.setStyleSheet("""
            QFrame {
                background: #1a202c;
                border: 1px solid #4a5568;
                border-radius: 6px;
                padding: 8px;
                margin-top: 6px;
            }
        """)
        
        filters_layout = QVBoxLayout(self.filters_frame)
        filters_layout.setSpacing(8)  # Giảm từ 10 xuống 8
        
        # Filter grid
        filter_grid = QGridLayout()
        filter_grid.setSpacing(8)  # Giảm từ 10 xuống 8
        
        # Account filter
        self.account_filter_label = QLabel("Account:")
        self.account_filter_label.setStyleSheet("""
            QLabel {
                color: #f3f4f6;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        filter_grid.addWidget(self.account_filter_label, 0, 0)
        
        self.account_filter_combo = QComboBox()
        self.account_filter_combo.addItem("All Accounts")
        self.account_filter_combo.setStyleSheet("""
            QComboBox {
                background-color: #374151;
                border: 2px solid #4b5563;
                border-radius: 8px;
                padding: 8px 12px;
                color: #f3f4f6;
                font-size: 13px;
                min-height: 15px;
            }
            QComboBox:hover {
                border-color: #6366f1;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #9ca3af;
                margin-right: 5px;
            }
        """)
        filter_grid.addWidget(self.account_filter_combo, 0, 1)
        
        # File type filter
        self.file_type_filter_label = QLabel("File Type:")
        self.file_type_filter_label.setStyleSheet("""
            QLabel {
                color: #f3f4f6;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        filter_grid.addWidget(self.file_type_filter_label, 0, 2)
        
        self.file_type_filter_combo = QComboBox()
        self.file_type_filter_combo.addItem("All Types")
        self.file_type_filter_combo.setStyleSheet("""
            QComboBox {
                background-color: #374151;
                border: 2px solid #4b5563;
                border-radius: 8px;
                padding: 8px 12px;
                color: #f3f4f6;
                font-size: 13px;
                min-height: 15px;
            }
            QComboBox:hover {
                border-color: #6366f1;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #9ca3af;
                margin-right: 5px;
            }
        """)
        filter_grid.addWidget(self.file_type_filter_combo, 0, 3)
        
        # Size filter
        self.size_filter_label = QLabel("Size:")
        self.size_filter_label.setStyleSheet("""
            QLabel {
                color: #f3f4f6;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        filter_grid.addWidget(self.size_filter_label, 1, 0)
        
        size_layout = QHBoxLayout()
        size_layout.setSpacing(10)
        
        self.min_size_input = QLineEdit()
        self.min_size_input.setPlaceholderText("Min")
        self.min_size_input.setStyleSheet("""
            QLineEdit {
                background-color: #374151;
                border: 2px solid #4b5563;
                border-radius: 8px;
                padding: 8px 12px;
                color: #f3f4f6;
                font-size: 13px;
                min-height: 15px;
            }
            QLineEdit:focus {
                border-color: #6366f1;
            }
        """)
        size_layout.addWidget(self.min_size_input)
        
        self.max_size_input = QLineEdit()
        self.max_size_input.setPlaceholderText("Max")
        self.max_size_input.setStyleSheet("""
            QLineEdit {
                background-color: #374151;
                border: 2px solid #4b5563;
                border-radius: 8px;
                padding: 8px 12px;
                color: #f3f4f6;
                font-size: 13px;
                min-height: 15px;
            }
            QLineEdit:focus {
                border-color: #6366f1;
            }
        """)
        size_layout.addWidget(self.max_size_input)
        
        filter_grid.addLayout(size_layout, 1, 1, 1, 2)
        
        # Date filter
        self.date_filter_label = QLabel("Modified Date:")
        self.date_filter_label.setStyleSheet("""
            QLabel {
                color: #f3f4f6;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        filter_grid.addWidget(self.date_filter_label, 2, 0)
        
        date_layout = QHBoxLayout()
        date_layout.setSpacing(10)
        
        self.from_date_input = QLineEdit()
        self.from_date_input.setPlaceholderText("From")
        self.from_date_input.setStyleSheet("""
            QLineEdit {
                background-color: #374151;
                border: 2px solid #4b5563;
                border-radius: 8px;
                padding: 8px 12px;
                color: #f3f4f6;
                font-size: 13px;
                min-height: 15px;
            }
            QLineEdit:focus {
                border-color: #6366f1;
            }
        """)
        date_layout.addWidget(self.from_date_input)
        
        self.to_date_input = QLineEdit()
        self.to_date_input.setPlaceholderText("To")
        self.to_date_input.setStyleSheet("""
            QLineEdit {
                background-color: #374151;
                border: 2px solid #4b5563;
                border-radius: 8px;
                padding: 8px 12px;
                color: #f3f4f6;
                font-size: 13px;
                min-height: 15px;
            }
            QLineEdit:focus {
                border-color: #6366f1;
            }
        """)
        date_layout.addWidget(self.to_date_input)
        
        filter_grid.addLayout(date_layout, 2, 1, 1, 2)
        
        filters_layout.addLayout(filter_grid)
        
        # Other filters section
        other_filters_layout = QHBoxLayout()
        other_filters_layout.setSpacing(20)
        
        self.other_filters_label = QLabel("Other Filters:")
        self.other_filters_label.setStyleSheet("""
            QLabel {
                color: #f3f4f6;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        other_filters_layout.addWidget(self.other_filters_label)
        
        # Enhanced checkboxes with modern styling
        self.include_trashed_checkbox = QCheckBox("Include Trashed")
        self.include_trashed_checkbox.setStyleSheet("""
            QCheckBox {
                color: #f3f4f6;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #4b5563;
                border-radius: 4px;
                background-color: #374151;
            }
            QCheckBox::indicator:checked {
                background-color: #6366f1;
                border-color: #6366f1;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            QCheckBox::indicator:hover {
                border-color: #6366f1;
            }
        """)
        other_filters_layout.addWidget(self.include_trashed_checkbox)
        
        self.include_shortcuts_checkbox = QCheckBox("Include Shortcuts")
        self.include_shortcuts_checkbox.setStyleSheet("""
            QCheckBox {
                color: #f3f4f6;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #4b5563;
                border-radius: 4px;
                background-color: #374151;
            }
            QCheckBox::indicator:checked {
                background-color: #6366f1;
                border-color: #6366f1;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            QCheckBox::indicator:hover {
                border-color: #6366f1;
            }
        """)
        other_filters_layout.addWidget(self.include_shortcuts_checkbox)
        
        other_filters_layout.addStretch()
        
        # Enhanced clear filters button
        self.clear_filters_button = QPushButton("🗑️ Clear Filters")
        self.clear_filters_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ef4444, stop:1 #dc2626);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                min-height: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #dc2626, stop:1 #b91c1c);
            }
        """)
        self.clear_filters_button.clicked.connect(self.clear_filters)
        other_filters_layout.addWidget(self.clear_filters_button)
        
        filters_layout.addLayout(other_filters_layout)
        
        # Do not show filters inline; they will be placed in a dialog on demand
        layout.addWidget(search_section)

    def open_advanced_dialog(self):
        """Open advanced filters in a modal dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Advanced Filters")
        dialog.setModal(True)
        dlg_layout = QVBoxLayout(dialog)
        dlg_layout.setContentsMargins(12, 12, 12, 12)
        dlg_layout.setSpacing(10)

        # Attach existing filters frame into dialog
        self.filters_frame.setParent(dialog)
        self.filters_frame.setVisible(True)
        dlg_layout.addWidget(self.filters_frame)

        # Dialog buttons
        btns = QHBoxLayout()
        btns.addStretch()
        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet("""
            QPushButton { background: #10b981; color: white; padding: 6px 12px; border-radius: 6px; }
            QPushButton:hover { background: #059669; }
        """)
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton { background: #6b7280; color: white; padding: 6px 12px; border-radius: 6px; }
            QPushButton:hover { background: #4b5563; }
        """)
        btns.addWidget(apply_btn)
        btns.addWidget(close_btn)
        dlg_layout.addLayout(btns)

        def on_apply():
            # Emit filters and close
            self.on_filter_changed()
            dialog.accept()

        def on_close():
            dialog.reject()

        apply_btn.clicked.connect(on_apply)
        close_btn.clicked.connect(on_close)

        # Show dialog
        dialog.exec()

        # Restore filters frame back to toolbar and hide
        self.filters_frame.setParent(self)
        self.filters_frame.setVisible(False)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.search_input.returnPressed.connect(self.on_search)
        self.account_filter_combo.currentTextChanged.connect(self.on_filter_changed)
        self.file_type_filter_combo.currentTextChanged.connect(self.on_filter_changed)
        self.min_size_input.textChanged.connect(self.on_filter_changed)
        self.max_size_input.textChanged.connect(self.on_filter_changed)
        self.from_date_input.textChanged.connect(self.on_filter_changed)
        self.to_date_input.textChanged.connect(self.on_filter_changed)
        self.include_trashed_checkbox.stateChanged.connect(self.on_filter_changed)
        self.include_shortcuts_checkbox.stateChanged.connect(self.on_filter_changed)
    
    def on_search_clicked(self):
        """Handle search button click"""
        self.on_search()
    
    def on_search(self):
        """Handle search request"""
        query = self.search_input.text().strip()
        if query:
            self.search_requested.emit(query)
    
    def toggle_advanced_filters(self):
        """Toggle advanced filters visibility"""
        self.filters_frame.setVisible(not self.filters_frame.isVisible())
        if self.filters_frame.isVisible():
            self.advanced_button.setText("⚙️ Hide Advanced")
        else:
            self.advanced_button.setText("⚙️ Advanced")
    
    def clear_filters(self):
        """Clear all filters"""
        self.search_input.clear()
        self.account_filter_combo.setCurrentIndex(0)
        self.file_type_filter_combo.setCurrentIndex(0)
        self.min_size_input.clear()
        self.max_size_input.clear()
        self.from_date_input.clear()
        self.to_date_input.clear()
        self.include_trashed_checkbox.setChecked(False)
        self.include_shortcuts_checkbox.setChecked(False)
        
        # Emit filter changed signal
        self.on_filter_changed()
    
    def on_filter_changed(self):
        """Handle filter changes"""
        filters = self.get_current_filters()
        self.filter_changed.emit(filters)
    
    def get_current_filters(self) -> dict:
        """Get current filter values"""
        return {
            'query': self.search_input.text().strip(),
            'account': self.account_filter_combo.currentText(),
            'file_type': self.file_type_filter_combo.currentText(),
            'min_size': self.min_size_input.text().strip(),
            'max_size': self.max_size_input.text().strip(),
            'from_date': self.from_date_input.text().strip(),
            'to_date': self.to_date_input.text().strip(),
            'include_trashed': self.include_trashed_checkbox.isChecked(),
            'include_shortcuts': self.include_shortcuts_checkbox.isChecked()
        }
    
    def get_current_query(self) -> str:
        """Get current search query"""
        return self.search_input.text().strip()
    
    def set_account_filter(self, account_key: str):
        """Set account filter to specific account"""
        for i in range(self.account_filter_combo.count()):
            if self.account_filter_combo.itemData(i) == account_key:
                self.account_filter_combo.setCurrentIndex(i)
                break
    
    def update_accounts(self, accounts):
        """Update account filter with available accounts"""
        self.account_filter_combo.clear()
        self.account_filter_combo.addItem("All Accounts", "")
        
        for account in accounts:
            name = account.get('account_key') or 'Unknown'
            key = account.get('account_key')
            self.account_filter_combo.addItem(name, key)
    
    def refresh_texts(self):
        """Refresh UI texts after language change"""
        # Update search placeholder
        self.search_input.setPlaceholderText(i18n.get("search"))
        
        # Update filter labels
        self.account_filter_label.setText(i18n.get("account"))
        self.file_type_filter_label.setText(i18n.get("file_type"))
        self.size_filter_label.setText(i18n.get("size"))
        self.date_filter_label.setText(i18n.get("modified_date"))
        
        # Update filter options
        self.account_filter_combo.setItemText(0, i18n.get("all_accounts"))
        self.file_type_filter_combo.setItemText(0, i18n.get("all_types"))
        
        # Update other filter labels
        self.include_trashed_checkbox.setText(i18n.get("include_trashed"))
        self.include_shortcuts_checkbox.setText(i18n.get("include_shortcuts"))
        
        # Update clear filters button
        self.clear_filters_button.setText(i18n.get("clear_filters"))
