"""
Internationalization (i18n) support for the application
"""

from typing import Dict, Any
from .config import LANGUAGES

class I18n:
    """Internationalization manager"""
    
    def __init__(self, language: str = "en"):
        self.language = language
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load translations for all supported languages"""
        return {
            "en": {
                # Main window
                "app_title": "Multi Driver V1.0.0",
                "connected": "Connected",
                "disconnected": "Disconnected",
                
                # Sidebar
                "accounts": "Accounts",
                "add_account": "+ Add Account",
                "type": "Type",
                "status": "Status",
                "last_sync": "Last sync",
                "idle": "Idle",
                "crawling": "Crawling",
                "syncing": "Syncing",
                "error": "Error",
                "oauth": "OAuth",
                "service_account": "Service Account",
                
                # Toolbar
                "search": "Search",
                "advanced": "Advanced",
                "account": "Account",
                "all_accounts": "All Accounts",
                "file_type": "File Type",
                "all_types": "All Types",
                "size": "Size",
                "min": "Min",
                "max": "Max",
                "modified_date": "Modified Date",
                "from": "From",
                "to": "To",
                "other": "Other",
                "include_trashed": "Include Trashed",
                "include_shortcuts": "Include Shortcuts",
                "clear_filters": "Clear Filters",
                
                # Tabs
                "search_results": "Search Results",
                "reports": "Reports",
                
                # Search results
                "no_search_performed": "No search performed",
                "export_results": "Export Results",
                "name": "Name",
                "type": "Type",
                "size": "Size",
                "modified": "Modified",
                "owner": "Owner",
                "path": "Path",
                "actions": "Actions",
                
                # Pagination
                "previous": "← Previous",
                "next": "Next →",
                "page": "Page",
                "of": "of",
                
                # Status bar
                "files": "Files",
                "size": "Size",
                
                # Actions
                "open": "Open",
                "download": "Download",
                "copy_link": "Copy Link",
                "share": "Share",
                "delete": "Delete",
                "move": "Move",
                "rename": "Rename",
                
                # Messages
                "search_found": "Found {count} files for '{query}'",
                "sync_started": "Sync started for {account}",
                "sync_completed": "Sync completed for {account}",
                "sync_failed": "Sync failed for {account}",
                "account_connected": "Account {email} connected successfully",
                "account_disconnected": "Account {email} disconnected",
                
                # Errors
                "connection_failed": "Connection failed",
                "search_failed": "Search failed",
                "sync_failed": "Sync failed",
                "unknown_error": "Unknown error occurred",
                
                # File types
                "folder": "Folder",
                "document": "Document",
                "spreadsheet": "Spreadsheet",
                "presentation": "Presentation",
                "image": "Image",
                "video": "Video",
                "audio": "Audio",
                "archive": "Archive",
                "other": "Other",
                
                # Settings
                "settings": "Settings",
                "language": "Language",
                "theme": "Theme",
                "appearance": "Appearance",
                "notifications": "Notifications",
                "auto_refresh": "Auto-refresh",
                "search_history": "Search History",
                "favorites": "Favorites",
                "about": "About",
                
                # Account details
                "account_details": "Account Details",
                "select_account_details": "Select an account to view details",
                "initial_sync": "Initial Sync",
                "incremental_sync": "Incremental Sync",
                
                # Reports
                "storage_usage": "Storage Usage",
                "file_types": "File Types",
                "sync_status": "Sync Status",
                "activity_log": "Activity Log",
                
                # Themes
                "dark": "Dark",
                "light": "Light",
                "midnight": "Midnight",
                "ocean": "Ocean",
                
                # Common
                "yes": "Yes",
                "no": "No",
                "cancel": "Cancel",
                "ok": "OK",
                "save": "Save",
                "close": "Close",
                "refresh": "Refresh",
                "loading": "Loading...",
                "no_results": "No results found",
                "select_all": "Select All",
                "deselect_all": "Deselect All"
            },
            "vi": {
                # Main window
                "app_title": "🚀 Multi Driver ♥️",
                "connected": "Đã kết nối",
                "disconnected": "Mất kết nối",
                
                # Sidebar
                "accounts": "Tài khoản",
                "add_account": "+ Thêm tài khoản",
                "type": "Loại",
                "status": "Trạng thái",
                "last_sync": "Đồng bộ cuối",
                "idle": "Chờ",
                "crawling": "Đang quét",
                "syncing": "Đang đồng bộ",
                "error": "Lỗi",
                "oauth": "OAuth",
                "service_account": "Tài khoản dịch vụ",
                
                # Toolbar
                "search": "Tìm kiếm",
                "advanced": "Nâng cao",
                "account": "Tài khoản",
                "all_accounts": "Tất cả tài khoản",
                "file_type": "Loại file",
                "all_types": "Tất cả loại",
                "size": "Kích thước",
                "min": "Tối thiểu",
                "max": "Tối đa",
                "modified_date": "Ngày sửa đổi",
                "from": "Từ",
                "to": "Đến",
                "other": "Khác",
                "include_trashed": "Bao gồm thùng rác",
                "include_shortcuts": "Bao gồm lối tắt",
                "clear_filters": "Xóa bộ lọc",
                
                # Tabs
                "search_results": "Kết quả tìm kiếm",
                "reports": "Báo cáo",
                
                # Search results
                "no_search_performed": "Chưa thực hiện tìm kiếm",
                "export_results": "Xuất kết quả",
                "name": "Tên",
                "type": "Loại",
                "size": "Kích thước",
                "modified": "Sửa đổi",
                "owner": "Chủ sở hữu",
                "path": "Đường dẫn",
                "actions": "Hành động",
                
                # Pagination
                "previous": "← Trước",
                "next": "Tiếp →",
                "page": "Trang",
                "of": "trên",
                
                # Status bar
                "files": "Tệp tin",
                "size": "Kích thước",
                
                # Actions
                "open": "Mở",
                "download": "Tải xuống",
                "copy_link": "Sao chép liên kết",
                "share": "Chia sẻ",
                "delete": "Xóa",
                "move": "Di chuyển",
                "rename": "Đổi tên",
                
                # Messages
                "search_found": "Tìm thấy {count} tệp tin cho '{query}'",
                "sync_started": "Bắt đầu đồng bộ cho {account}",
                "sync_completed": "Hoàn thành đồng bộ cho {account}",
                "sync_failed": "Đồng bộ thất bại cho {account}",
                "account_connected": "Tài khoản {email} đã kết nối thành công",
                "account_disconnected": "Tài khoản {email} đã ngắt kết nối",
                
                # Errors
                "connection_failed": "Kết nối thất bại",
                "search_failed": "Tìm kiếm thất bại",
                "sync_failed": "Đồng bộ thất bại",
                "unknown_error": "Đã xảy ra lỗi không xác định",
                
                # File types
                "folder": "Thư mục",
                "document": "Tài liệu",
                "spreadsheet": "Bảng tính",
                "presentation": "Trình bày",
                "image": "Hình ảnh",
                "video": "Video",
                "audio": "Âm thanh",
                "archive": "Lưu trữ",
                "other": "Khác",
                
                # Settings
                "settings": "Cài đặt",
                "language": "Ngôn ngữ",
                "theme": "Giao diện",
                "appearance": "Giao diện",
                "notifications": "Thông báo",
                "auto_refresh": "Tự động làm mới",
                "search_history": "Lịch sử tìm kiếm",
                "favorites": "Yêu thích",
                "about": "Giới thiệu",
                
                # Account details
                "account_details": "Chi tiết tài khoản",
                "select_account_details": "Chọn một tài khoản để xem chi tiết",
                "initial_sync": "Đồng bộ ban đầu",
                "incremental_sync": "Đồng bộ tăng",
                
                # Reports
                "storage_usage": "Sử dụng bộ nhớ",
                "file_types": "Loại tệp tin",
                "sync_status": "Trạng thái đồng bộ",
                "activity_log": "Nhật ký hoạt động",
                
                # Themes
                "dark": "Tối",
                "light": "Sáng",
                "midnight": "Nửa đêm",
                "ocean": "Đại dương",
                
                # Common
                "yes": "Có",
                "no": "Không",
                "cancel": "Hủy",
                "ok": "OK",
                "save": "Lưu",
                "close": "Đóng",
                "refresh": "Làm mới",
                "loading": "Đang tải...",
                "no_results": "Không tìm thấy kết quả",
                "select_all": "Chọn tất cả",
                "deselect_all": "Bỏ chọn tất cả"
            }
        }
    
    def set_language(self, language: str):
        """Set current language"""
        if language in LANGUAGES:
            self.language = language
    
    def get(self, key: str, **kwargs) -> str:
        """Get translation for key with optional formatting"""
        translation = self.translations.get(self.language, {}).get(key, key)
        
        # Format with kwargs if provided
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError):
                pass
        
        return translation
    
    def get_language_name(self, language_code: str) -> str:
        """Get language name in current language"""
        lang = LANGUAGES.get(language_code)
        if lang:
            if self.language == "vi":
                return lang.native_name
            else:
                return lang.name
        return language_code
    
    def get_current_language_info(self) -> Dict[str, Any]:
        """Get current language information"""
        return LANGUAGES.get(self.language, {})
    
    def get_supported_languages(self) -> Dict[str, Dict[str, Any]]:
        """Get all supported languages"""
        return LANGUAGES

# Global i18n instance
i18n = I18n()
