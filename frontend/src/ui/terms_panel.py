"""
Terms and Conditions Panel
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QScrollArea, QFrame, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class TermsPanel(QWidget):
    """Terms and conditions panel"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the Terms UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Điều Khoản Sử Dụng Multi Driver")
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
        
        # Section 1: Acceptance
        self.add_section(content_layout, "✅ Chấp Nhận Điều Khoản", """
<h3>1. Điều khoản sử dụng</h3>
<p>Bằng việc sử dụng ứng dụng Multi Driver, bạn đồng ý tuân thủ các điều khoản và điều kiện được nêu trong tài liệu này. Nếu bạn không đồng ý với bất kỳ phần nào của các điều khoản này, vui lòng không sử dụng ứng dụng.</p>

<h3>2. Thay đổi điều khoản</h3>
<p>Chúng tôi có quyền thay đổi các điều khoản này vào bất kỳ lúc nào. Những thay đổi sẽ có hiệu lực ngay khi được đăng tải. Việc tiếp tục sử dụng ứng dụng sau khi có thay đổi được coi là chấp nhận các điều khoản mới.</p>
        """)
        
        # Section 2: Privacy
        self.add_section(content_layout, "🔒 Chính Sách Bảo Mật", """
<h3>1. Thu thập thông tin</h3>
<p>Ứng dụng Multi Driver thu thập và lưu trữ thông tin sau:</p>
<ul>
<li>Thông tin tài khoản Google Drive (được mã hóa)</li>
<li>Metadata của file (tên, kích thước, ngày tạo/sửa đổi)</li>
<li>Thông tin đăng nhập và phiên làm việc</li>
</ul>

<h3>2. Sử dụng thông tin</h3>
<p>Thông tin được thu thập chỉ được sử dụng để:</p>
<ul>
<li>Cung cấp dịch vụ đồng bộ và quản lý file</li>
<li>Cải thiện trải nghiệm người dùng</li>
<li>Xử lý lỗi và bảo trì hệ thống</li>
</ul>

<h3>3. Bảo vệ thông tin</h3>
<p>Chúng tôi cam kết bảo vệ thông tin cá nhân của bạn bằng cách:</p>
<ul>
<li>Mã hóa tất cả dữ liệu nhạy cảm</li>
<li>Không chia sẻ thông tin với bên thứ ba</li>
<li>Tuân thủ các quy định bảo mật quốc tế</li>
</ul>
        """)
        
        # Section 3: Usage
        self.add_section(content_layout, "📋 Điều Khoản Sử Dụng", """
<h3>1. Sử dụng hợp pháp</h3>
<p>Bạn cam kết sử dụng ứng dụng chỉ cho các mục đích hợp pháp và không vi phạm quyền của người khác. Bạn không được:</p>
<ul>
<li>Sử dụng để lưu trữ nội dung bất hợp pháp</li>
<li>Vi phạm bản quyền hoặc quyền sở hữu trí tuệ</li>
<li>Phân phối phần mềm độc hại hoặc spam</li>
<li>Thực hiện các hành vi phá hoại hệ thống</li>
</ul>

<h3>2. Giới hạn sử dụng</h3>
<p>Chúng tôi có quyền giới hạn hoặc tạm ngưng quyền sử dụng của bạn nếu:</p>
<ul>
<li>Vi phạm các điều khoản này</li>
<li>Sử dụng quá mức tài nguyên hệ thống</li>
<li>Gây ra lỗi hoặc thiệt hại cho hệ thống</li>
</ul>

<h3>3. Trách nhiệm người dùng</h3>
<p>Bạn chịu trách nhiệm:</p>
<ul>
<li>Bảo vệ thông tin đăng nhập của mình</li>
<li>Đảm bảo tính bảo mật của dữ liệu</li>
<li>Tuân thủ các quy định pháp luật hiện hành</li>
</ul>
        """)
        
        # Section 4: Limitations
        self.add_section(content_layout, "⚠️ Giới Hạn Trách Nhiệm", """
<h3>1. Từ chối bảo hành</h3>
<p>Ứng dụng được cung cấp "nguyên trạng" mà không có bất kỳ bảo hành nào, rõ ràng hoặc ngụ ý. Chúng tôi không đảm bảo:</p>
<ul>
<li>Ứng dụng sẽ hoạt động không gián đoạn</li>
<li>Dữ liệu sẽ được bảo vệ hoàn toàn</li>
<li>Không có lỗi hoặc thiếu sót</li>
<li>Tương thích với tất cả hệ thống</li>
</ul>

<h3>2. Giới hạn trách nhiệm</h3>
<p>Trong mọi trường hợp, chúng tôi sẽ không chịu trách nhiệm về:</p>
<ul>
<li>Mất mát hoặc hư hỏng dữ liệu</li>
<li>Gián đoạn dịch vụ</li>
<li>Thiệt hại gián tiếp hoặc phát sinh</li>
<li>Thiệt hại thương mại hoặc lợi nhuận</li>
</ul>

<h3>3. Bồi thường</h3>
<p>Bạn đồng ý bồi thường và bảo vệ chúng tôi khỏi mọi khiếu nại, thiệt hại hoặc chi phí phát sinh từ việc sử dụng ứng dụng của bạn.</p>
        """)
        
        # Section 5: Intellectual Property
        self.add_section(content_layout, "📄 Sở Hữu Trí Tuệ", """
<h3>1. Bản quyền</h3>
<p>Ứng dụng Multi Driver và tất cả nội dung liên quan được bảo vệ bởi luật bản quyền. Bạn không được:</p>
<ul>
<li>Sao chép, phân phối hoặc sửa đổi mã nguồn</li>
<li>Đảo ngược kỹ thuật hoặc decompile</li>
<li>Tạo sản phẩm phái sinh</li>
<li>Sử dụng cho mục đích thương mại mà không được phép</li>
</ul>

<h3>2. Thương hiệu</h3>
<p>Tên "Multi Driver" và logo liên quan là thương hiệu của chúng tôi. Bạn không được sử dụng chúng mà không có sự cho phép bằng văn bản.</p>

<h3>3. Nội dung người dùng</h3>
<p>Bạn giữ quyền sở hữu đối với nội dung bạn tải lên. Tuy nhiên, bạn cấp cho chúng tôi quyền sử dụng để cung cấp dịch vụ.</p>
        """)
        
        # Section 6: Termination
        self.add_section(content_layout, "🚫 Chấm Dứt Dịch Vụ", """
<h3>1. Chấm dứt bởi người dùng</h3>
<p>Bạn có thể chấm dứt việc sử dụng ứng dụng bất kỳ lúc nào bằng cách:</p>
<ul>
<li>Xóa tài khoản đã kết nối</li>
<li>Gỡ cài đặt ứng dụng</li>
<li>Liên hệ hỗ trợ để yêu cầu xóa dữ liệu</li>
</ul>

<h3>2. Chấm dứt bởi chúng tôi</h3>
<p>Chúng tôi có quyền chấm dứt hoặc tạm ngưng dịch vụ nếu:</p>
<ul>
<li>Vi phạm điều khoản sử dụng</li>
<li>Không thanh toán phí dịch vụ (nếu có)</li>
<li>Hành vi gây hại cho hệ thống</li>
<li>Yêu cầu của cơ quan chức năng</li>
</ul>

<h3>3. Hậu quả chấm dứt</h3>
<p>Sau khi chấm dứt:</p>
<ul>
<li>Quyền truy cập sẽ bị vô hiệu hóa</li>
<li>Dữ liệu có thể bị xóa vĩnh viễn</li>
<li>Không hoàn lại phí đã thanh toán</li>
</ul>
        """)
        
        # Section 7: Contact
        self.add_section(content_layout, "📞 Liên Hệ", """
<h3>1. Thông tin liên hệ</h3>
<p>Nếu bạn có câu hỏi về các điều khoản này, vui lòng liên hệ:</p>
<ul>
<li><strong>Email:</strong> support@multidriver.com</li>
<li><strong>Website:</strong> https://multidriver.com</li>
<li><strong>Địa chỉ:</strong> [Địa chỉ công ty]</li>
</ul>

<h3>2. Khiếu nại</h3>
<p>Để khiếu nại về dịch vụ hoặc vi phạm điều khoản:</p>
<ul>
<li>Gửi email chi tiết về vấn đề</li>
<li>Bao gồm thông tin tài khoản và bằng chứng</li>
<li>Chúng tôi sẽ phản hồi trong vòng 48 giờ</li>
</ul>

<h3>3. Cập nhật</h3>
<p>Phiên bản mới nhất của điều khoản này có thể được tìm thấy tại:</p>
<p><strong>https://multidriver.com/terms</strong></p>
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
            QTextEdit p {
                margin: 8px 0;
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
