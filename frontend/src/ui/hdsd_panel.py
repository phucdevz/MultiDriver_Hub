"""
HDSD (Hướng dẫn sử dụng) Panel
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QScrollArea, QFrame, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class HDSDPanel(QWidget):
    """Hướng dẫn sử dụng panel"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the HDSD UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Hướng Dẫn Sử Dụng Multi Driver")
        title.setStyleSheet("""
            QLabel {
                color: #e2e8f0;
                font-size: 24px;
                font-weight: bold;
                padding: 10px 0;
                border-bottom: 2px solid #4a5568;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Content scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
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
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Section 1: Getting Started
        self.add_section(content_layout, "Bắt Đầu", """
<h3>1. Kết nối tài khoản Google Drive</h3>
<ul>
<li>Bấm nút <strong>"+ Add Account"</strong> trong sidebar bên trái</li>
<li>Chọn <strong>"OAuth Account"</strong> để kết nối tài khoản cá nhân</li>
<li>Hoặc chọn <strong>"Service Account"</strong> để kết nối tài khoản doanh nghiệp</li>
<li>Làm theo hướng dẫn xác thực Google</li>
</ul>

<h3>2. Đồng bộ dữ liệu</h3>
<ul>
<li>Sau khi kết nối, bấm <strong>"Refresh"</strong> để đồng bộ file</li>
<li>Hoặc bấm <strong>"Initial Sync"</strong> để đồng bộ toàn bộ dữ liệu lần đầu</li>
<li>Quá trình đồng bộ có thể mất vài phút tùy số lượng file</li>
</ul>
        """)
        
        # Section 2: Using My Drive
        self.add_section(content_layout, "Sử Dụng My Drive", """
<h3>1. Xem file của bạn</h3>
<ul>
<li>Tab <strong>"My Drive"</strong> hiển thị tất cả file bạn sở hữu</li>
<li>Chỉ hiển thị file, không hiển thị thư mục</li>
<li>Không hiển thị file được chia sẻ từ người khác</li>
</ul>

<h3>2. Tìm kiếm file</h3>
<ul>
<li>Gõ từ khóa vào ô <strong>"🔍 Search files..."</strong></li>
<li>Nhấn Enter hoặc bấm nút <strong>"🔍 Search"</strong></li>
<li>Bấm <strong>"❌ Clear"</strong> để xóa tìm kiếm và về My Drive</li>
</ul>

<h3>3. Bộ lọc nâng cao</h3>
<ul>
<li>Bấm <strong>"⚙️ Filters"</strong> để mở bộ lọc nâng cao</li>
<li>Có thể lọc theo: loại file, kích thước, ngày sửa đổi</li>
<li>Bấm <strong>"Apply Filters"</strong> để áp dụng</li>
</ul>
        """)
        
        # Section 3: File Operations
        self.add_section(content_layout, "Thao Tác Với File", """
<h3>1. Xem chi tiết file</h3>
<ul>
<li>Double-click vào file để xem chi tiết</li>
<li>Hoặc click chuột phải → <strong>"View Details"</strong></li>
</ul>

<h3>2. Mở file trong Google Drive</h3>
<ul>
<li>Click chuột phải vào file → <strong>"Open in Google Drive"</strong></li>
<li>File sẽ mở trong trình duyệt</li>
</ul>

<h3>3. Sao chép link file</h3>
<ul>
<li>Click chuột phải → <strong>"Copy Link"</strong></li>
<li>Link sẽ được copy vào clipboard</li>
</ul>

<h3>4. Xuất dữ liệu</h3>
<ul>
<li>Bấm <strong>"📊 Export"</strong> để xuất danh sách file</li>
<li>Dữ liệu sẽ được xuất ra file CSV/Excel</li>
</ul>
        """)
        
        # Section 4: Accounts Management
        self.add_section(content_layout, "Quản Lý Tài Khoản", """
<h3>1. Xem tài khoản đã kết nối</h3>
<ul>
<li>Chuyển sang tab <strong>"Accounts"</strong></li>
<li>Xem danh sách tất cả tài khoản đã kết nối</li>
<li>Kiểm tra trạng thái đồng bộ</li>
</ul>

<h3>2. Đồng bộ lại tài khoản</h3>
<ul>
<li>Chọn tài khoản cần đồng bộ</li>
<li>Bấm <strong>"🔄 Refresh"</strong> để đồng bộ lại</li>
<li>Hoặc bấm <strong>"Initial Sync"</strong> để đồng bộ toàn bộ</li>
</ul>

<h3>3. Xóa tài khoản</h3>
<ul>
<li>Chọn tài khoản cần xóa</li>
<li>Bấm <strong>"🗑️ Delete"</strong> để xóa</li>
<li>Dữ liệu sẽ được xóa khỏi hệ thống</li>
</ul>
        """)
        
        # Section 5: Reports
        self.add_section(content_layout, "Báo Cáo", """
<h3>1. Xem báo cáo tổng quan</h3>
<ul>
<li>Chuyển sang tab <strong>"Reports"</strong></li>
<li>Xem thống kê tổng quan về dữ liệu</li>
</ul>

<h3>2. Các loại báo cáo</h3>
<ul>
<li><strong>Storage Report:</strong> Thống kê dung lượng lưu trữ</li>
<li><strong>File Types:</strong> Phân loại file theo loại</li>
<li><strong>Sync Status:</strong> Trạng thái đồng bộ các tài khoản</li>
<li><strong>Duplicate Files:</strong> Tìm file trùng lặp</li>
</ul>
        """)
        
        # Section 6: Tips
        self.add_section(content_layout, "💡 Mẹo Sử Dụng", """
<h3>1. Tối ưu hiệu suất</h3>
<ul>
<li>Không nên kết nối quá nhiều tài khoản cùng lúc</li>
<li>Đồng bộ từng tài khoản một để tránh lỗi</li>
<li>Đóng ứng dụng khi không sử dụng</li>
</ul>

<h3>2. Xử lý lỗi</h3>
<ul>
<li>Nếu gặp lỗi kết nối, thử refresh lại tài khoản</li>
<li>Kiểm tra kết nối internet</li>
<li>Đảm bảo tài khoản Google có quyền truy cập Drive</li>
</ul>

<h3>3. Bảo mật</h3>
<ul>
<li>Không chia sẻ thông tin đăng nhập</li>
<li>Đăng xuất khi sử dụng máy tính chung</li>
<li>Thường xuyên kiểm tra tài khoản đã kết nối</li>
</ul>
        """)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
    
    def add_section(self, layout, title, content):
        """Add a section with title and content"""
        # Section frame
        section_frame = QFrame()
        section_frame.setStyleSheet("""
            QFrame {
                background: #1a202c;
                border: 1px solid #4a5568;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(12)
        
        # Section title
        section_title = QLabel(title)
        section_title.setStyleSheet("""
            QLabel {
                color: #e2e8f0;
                font-size: 18px;
                font-weight: bold;
                padding: 8px 0;
                border-bottom: 1px solid #4a5568;
            }
        """)
        section_layout.addWidget(section_title)
        
        # Section content
        content_text = QTextEdit()
        content_text.setHtml(content)
        content_text.setReadOnly(True)
        content_text.setMaximumHeight(300)
        content_text.setStyleSheet("""
            QTextEdit {
                background: #2d3748;
                border: 1px solid #4a5568;
                border-radius: 6px;
                padding: 12px;
                color: #e2e8f0;
                font-size: 14px;
                line-height: 1.5;
            }
            QTextEdit h3 {
                color: #f7fafc;
                font-size: 16px;
                font-weight: bold;
                margin: 8px 0 4px 0;
            }
            QTextEdit ul {
                margin: 4px 0;
                padding-left: 20px;
            }
            QTextEdit li {
                margin: 2px 0;
            }
            QTextEdit strong {
                color: #fbbf24;
                font-weight: bold;
            }
        """)
        section_layout.addWidget(content_text)
        
        layout.addWidget(section_frame)
    
    def refresh_texts(self):
        """Refresh UI texts after language change"""
        pass
