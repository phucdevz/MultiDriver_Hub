# Multi Driver Made With ♥️ By Truong Phuc

Ứng dụng quản lý nhiều tài khoản Google Drive với khả năng tìm kiếm và đồng bộ dữ liệu mạnh mẽ.

## 🚀 Tính năng chính

- **Quản lý nhiều tài khoản**: Hỗ trợ 10+ tài khoản Google Drive
- **Xác thực linh hoạt**: OAuth người dùng và Service Account
- **Tìm kiếm nâng cao**: Full-text search với FTS5, filters theo MIME type, size, date
- **Upload file**: Upload nhiều file/thư mục lên Google Drive
- **Đồng bộ thông minh**: Initial crawl và incremental sync
- **Báo cáo chi tiết**: Duplicate detection, health monitoring, storage analysis
- **Giao diện đẹp**: Python GUI với PySide6, responsive design

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐    HTTP/HTTPS    ┌─────────────────┐
│   Python GUI    │ ◄──────────────► │  Node.js API    │
│   (PySide6)     │                  │   (Express)     │
└─────────────────┘                  └─────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │   SQLite DB     │
                                    │   (FTS5)        │
                                    └─────────────────┘
```

## 📋 Yêu cầu hệ thống

- **Backend**: Node.js 18+, Redis (tùy chọn)
- **Frontend**: Python 3.8+, PySide6
- **Database**: SQLite (built-in), PostgreSQL (production)
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

## 🛠️ Cài đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd MultiAPI-Driver-Python
```

### 2. Cài đặt Backend

```bash
cd backend

# Cài đặt dependencies
npm install

# Tạo file .env từ template
cp env.example .env

# Chỉnh sửa .env với thông tin Google API
# GOOGLE_CLIENT_ID=your_client_id
# GOOGLE_CLIENT_SECRET=your_client_secret
# ENCRYPTION_KEY=your_32_char_key

# Khởi động backend
npm run dev
```

### 3. Cài đặt Frontend

```bash
cd frontend

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Khởi động frontend
python src/main.py
```

## 🔧 Cấu hình Google API

### OAuth Setup (Khuyến nghị)

1. Tạo project trên [Google Cloud Console](https://console.cloud.google.com/)
2. Bật Google Drive API
3. Tạo OAuth 2.0 credentials (Desktop application)
4. Cập nhật `GOOGLE_CLIENT_ID` và `GOOGLE_CLIENT_SECRET` trong `.env`

### Service Account Setup (Tùy chọn)

1. Tạo Service Account trong GCP project
2. Tải private key JSON
3. Share thư mục Google Drive với email Service Account
4. Sử dụng API để đăng ký SA

## 📖 Sử dụng

### Kết nối tài khoản

1. **OAuth**: Click "Connect Account" → Đăng nhập Google → Authorize
2. **Service Account**: Nhập alias, private key và root folder IDs

### Tìm kiếm file

- **Tìm kiếm cơ bản**: Nhập từ khóa vào search bar
- **Filters**: Chọn MIME type, size range, date range
- **Advanced search**: Sử dụng multiple criteria và boolean logic

### Upload file

- **Upload nhiều file**: Chọn nhiều file cùng lúc
- **Upload thư mục**: Upload toàn bộ thư mục và file con
- **Chọn tài khoản**: Upload vào tài khoản Google Drive cụ thể
- **Chọn thư mục đích**: Upload vào thư mục con trong Drive
- **Theo dõi tiến trình**: Progress bar real-time
- **Hủy upload**: Dừng upload đang thực hiện

### Đồng bộ dữ liệu

- **Initial Crawl**: Lần đầu crawl toàn bộ Drive
- **Incremental Sync**: Cập nhật thay đổi định kỳ
- **Manual Sync**: Click sync button cho từng account

### Báo cáo

- **Duplicate Detection**: Tìm file trùng lặp theo MD5/size
- **Health Monitor**: Tình trạng hệ thống và accounts
- **Storage Analysis**: Phân tích dung lượng theo folder, date

## 🔒 Bảo mật

- **Encryption**: AES-256-GCM cho tokens/keys
- **Rate Limiting**: API protection với express-rate-limit
- **CORS**: Cấu hình chặt chẽ cho production
- **Secrets**: Lưu trữ an toàn trong OS keychain hoặc KMS

## 🚀 Triển khai Production

### Backend

```bash
# Build và deploy
npm run build
pm2 start ecosystem.config.js

# Hoặc Docker
docker build -t drive-manager-backend .
docker run -p 8080:8080 drive-manager-backend
```

### Frontend

```bash
# Đóng gói với PyInstaller
pyinstaller --onefile --windowed src/main.py

# Hoặc cx_Freeze
python setup.py build
```

## 📊 Performance

- **Database**: SQLite FTS5 cho search nhanh
- **Caching**: Redis cho job queue và caching
- **Pagination**: Virtual scrolling cho large datasets
- **Batch Processing**: Bulk operations cho sync

## 🐛 Troubleshooting

### Backend không khởi động

```bash
# Kiểm tra port
netstat -an | grep 8080

# Kiểm tra logs
npm run dev

# Kiểm tra .env file
cat .env
```

### Frontend không kết nối

```bash
# Kiểm tra backend URL
# Mặc định: http://localhost:8080

# Test API
curl http://localhost:8080/health
```

### OAuth lỗi

- Kiểm tra `GOOGLE_CLIENT_ID` và `GOOGLE_CLIENT_SECRET`
- Đảm bảo redirect URI đúng: `http://localhost:8080/accounts/oauth/callback`
- Kiểm tra Google Cloud Console OAuth consent screen

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

## 📝 License

MIT License - xem [LICENSE](LICENSE) file để biết thêm chi tiết.

## 📞 Hỗ trợ

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Wiki**: [Project Wiki](https://github.com/your-repo/wiki)

## 🔄 Roadmap

- [ ] Google Workspace integration
- [ ] Advanced file preview
- [ ] Collaborative features
- [ ] Mobile app
- [ ] Cloud deployment templates
- [ ] Plugin system

---

**Lưu ý**: Đây là dự án MVP. Vui lòng test kỹ trước khi sử dụng trong production.
