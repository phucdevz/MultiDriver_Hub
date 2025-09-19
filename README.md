# 🚀 MultiDriver Hub

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Node.js](https://img.shields.io/badge/node.js-16+-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

**Advanced Google Drive Management with Multi-Account Support**

[Features](#-features) • [Screenshots](#-screenshots) • [Installation](#-installation) • [Usage](#-usage) • [API](#-api) • [Contributing](#-contributing)

</div>

---

## ✨ Overview

**MultiDriver Hub** is a powerful, modern desktop application for managing multiple Google Drive accounts simultaneously. Built with a sleek Python GUI and robust Node.js backend, it provides enterprise-grade file management, advanced search capabilities, and intelligent synchronization.

### 🎯 Why MultiDriver Hub?

- **🔐 Multi-Account Management**: Seamlessly manage personal and business Google Drive accounts
- **🔍 Advanced Search**: Full-text search across all accounts with powerful filters
- **⚡ Real-time Sync**: Intelligent background synchronization with conflict resolution
- **📊 Analytics & Reports**: Comprehensive insights into your storage usage and file patterns
- **🎨 Modern UI**: Beautiful, customizable interface with dark/light themes
- **🌍 Internationalization**: Support for multiple languages (English, Vietnamese)
- **🔒 Enterprise Security**: OAuth2 and Service Account authentication with encrypted storage

---

## 🚀 Features

### 🔐 **Account Management**
- **OAuth2 Integration**: Connect personal Google accounts with secure authentication
- **Service Account Support**: Manage business accounts with service credentials
- **Encrypted Storage**: All credentials stored with AES-256-GCM encryption
- **Account Status Monitoring**: Real-time sync status and health monitoring

### 🔍 **Advanced Search & Discovery**
- **Full-Text Search**: Search across file names, content, and metadata
- **Smart Filters**: Filter by file type, size, date, owner, and more
- **Pagination**: Handle large result sets efficiently
- **Export Results**: Export search results to CSV, JSON, or Excel

### 📁 **File Operations**
- **Bulk Operations**: Upload, download, move, or delete multiple files
- **File Preview**: Preview documents, images, and videos
- **Sharing Management**: View and manage file sharing permissions
- **Virtual Paths**: Navigate through folder structures intuitively

### 📊 **Analytics & Reporting**
- **Storage Analysis**: Detailed breakdown of storage usage by folder and account
- **Duplicate Detection**: Find and manage duplicate files across accounts
- **Sync Performance**: Monitor sync health and performance metrics
- **Usage Trends**: Track storage growth and file activity over time

### ⚡ **Performance & Reliability**
- **Background Sync**: Automatic synchronization every 5-30 minutes
- **Batch Processing**: Efficient handling of large file operations
- **Rate Limiting**: Smart API usage to prevent quota exhaustion
- **Error Recovery**: Robust error handling with automatic retry mechanisms

---

## 📸 Screenshots

<div align="center">

### Main Interface
![Main Interface](https://via.placeholder.com/800x500/1a202c/ffffff?text=Main+Interface+with+Multi-Account+Support)

### Advanced Search
![Advanced Search](https://via.placeholder.com/800x500/2d3748/ffffff?text=Advanced+Search+with+Filters)

### Analytics Dashboard
![Analytics](https://via.placeholder.com/800x500/4a5568/ffffff?text=Analytics+and+Reports)

### Settings Panel
![Settings](https://via.placeholder.com/800x500/1a202c/ffffff?text=Settings+and+Configuration)

</div>

---

## 🛠️ Installation

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Google Cloud Console** account for API credentials

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/MultiDriver_Hub.git
   cd MultiDriver_Hub
   ```

2. **Backend Setup**
   ```bash
   cd backend
   npm install
   cp .env.example .env
   # Edit .env with your configuration
   npm start
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   pip install -r requirements.txt
   python src/main.py
   ```

### Detailed Installation

<details>
<summary>Click to expand detailed installation steps</summary>

#### Backend Installation

```bash
# Navigate to backend directory
cd backend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Edit .env file with your settings
nano .env
```

**Required Environment Variables:**
```env
# Server Configuration
PORT=3000
NODE_ENV=development

# Database
DB_PATH=./data/drive_manager.db

# Google OAuth2
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:3000/api/accounts/oauth/callback

# Encryption
ENCRYPTION_KEY=your_32_character_encryption_key

# Logging
LOG_LEVEL=info
```

#### Frontend Installation

```bash
# Navigate to frontend directory
cd frontend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

</details>

---

## 🚀 Usage

### First Time Setup

1. **Start the Backend**
   ```bash
   cd backend
   npm start
   ```

2. **Launch the Frontend**
   ```bash
   cd frontend
   python src/main.py
   ```

3. **Add Your First Account**
   - Click "**+ Add Account**" in the sidebar
   - Choose "**OAuth Account**" for personal accounts
   - Follow the Google authentication flow
   - Wait for initial sync to complete

### Daily Usage

#### 🔍 **Searching Files**
- Use the search bar for quick file lookup
- Click "**⚙️ Advanced**" for detailed filters
- Filter by account, file type, size, or date range

#### 📁 **Managing Files**
- Double-click files to view details
- Right-click for context menu actions
- Use bulk operations for multiple files

#### 📊 **Viewing Reports**
- Switch to "**Reports**" tab for analytics
- Monitor storage usage and sync status
- Find duplicate files to free up space

---

## 🔧 Configuration

### Google API Setup

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Google Drive API**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Drive API" and enable it

3. **Create OAuth2 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Set redirect URI: `http://localhost:3000/api/accounts/oauth/callback`

4. **Create Service Account (Optional)**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Download the JSON key file
   - Share Google Drive folders with the service account email

### Application Settings

Access settings through the main menu:
- **Appearance**: Themes, language, and UI preferences
- **Sync**: Auto-refresh intervals and sync behavior
- **Security**: Encryption settings and credential management

---

## 📚 API Documentation

### Backend API Endpoints

#### Account Management
```http
GET    /api/accounts              # List all accounts
POST   /api/accounts/oauth/start  # Start OAuth flow
GET    /api/accounts/oauth/callback # OAuth callback
POST   /api/accounts/sa           # Register service account
DELETE /api/accounts/:key         # Delete account
```

#### File Operations
```http
GET    /api/files/:id             # Get file metadata
GET    /api/files/:id/download    # Download file
POST   /api/files/upload          # Upload file
POST   /api/files/bulk            # Bulk operations
```

#### Search & Analytics
```http
GET    /api/search                # Basic search
POST   /api/search/advanced       # Advanced search
GET    /api/reports/health        # System health report
GET    /api/reports/storage       # Storage analysis
```

### Frontend API Client

The frontend uses a comprehensive API client (`services/api_client.py`) that handles:
- HTTP requests with proper error handling
- Authentication token management
- File upload/download with progress tracking
- Rate limiting and retry logic

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────┐    HTTP/REST API    ┌─────────────────┐    SQLite    ┌─────────────────┐
│   Frontend      │ ◄─────────────────► │   Backend       │ ◄──────────► │   Database      │
│   (Python       │                     │   (Node.js      │              │   (SQLite)      │
│   PySide6)      │                     │   Express)      │              │                 │
└─────────────────┘                     └─────────────────┘              └─────────────────┘
         │                                       │
         │                                       │
         ▼                                       ▼
┌─────────────────┐                     ┌─────────────────┐
│   Google Drive  │                     │   Google Drive  │
│   API (OAuth)   │                     │   API (Service  │
│                 │                     │   Account)      │
└─────────────────┘                     └─────────────────┘
```

### Technology Stack

**Frontend:**
- **PySide6**: Modern Qt-based GUI framework
- **Python 3.8+**: Core application language
- **Requests/HTTPX**: HTTP client for API communication
- **SQLite**: Local caching and configuration

**Backend:**
- **Node.js 16+**: Runtime environment
- **Express.js**: Web framework
- **SQLite3**: Database with FTS5 support
- **Google APIs**: Drive API integration
- **Winston**: Logging framework

**Security:**
- **AES-256-GCM**: Token encryption
- **OAuth2**: Google authentication
- **Helmet**: Security headers
- **Rate Limiting**: API protection

---

## 🔒 Security

### Data Protection
- **Encrypted Storage**: All credentials encrypted with AES-256-GCM
- **Secure Communication**: HTTPS for all API communications
- **Token Management**: Automatic token refresh and secure storage
- **Input Validation**: Comprehensive input sanitization

### Privacy
- **Local Processing**: All data processed locally
- **No Cloud Storage**: No data sent to third-party services
- **Configurable Logging**: Control what gets logged
- **Secure Deletion**: Proper cleanup of sensitive data

---

## 🚀 Performance

### Optimization Features
- **Batch Processing**: Handle thousands of files efficiently
- **Background Sync**: Non-blocking synchronization
- **Smart Caching**: Reduce API calls with intelligent caching
- **Pagination**: Handle large datasets without memory issues
- **Rate Limiting**: Prevent API quota exhaustion

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB for application + database
- **Network**: Stable internet connection for sync
- **CPU**: Modern multi-core processor recommended

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Run tests**
   ```bash
   npm test  # Backend tests
   python -m pytest  # Frontend tests
   ```
5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Code Style
- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ESLint configuration
- **Commits**: Use conventional commit messages

---

## 📝 Changelog

### [1.0.0] - 2024-01-01
- ✨ Initial release
- 🔐 Multi-account Google Drive support
- 🔍 Advanced search with filters
- 📊 Comprehensive analytics
- 🎨 Modern UI with themes
- 🌍 Multi-language support

---

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check if port 3000 is available
- Verify Node.js version (16+)
- Check environment variables in `.env`

**Frontend crashes:**
- Ensure Python 3.8+ is installed
- Check PySide6 installation
- Verify backend is running

**Sync issues:**
- Check Google API credentials
- Verify internet connection
- Check rate limiting status

**Performance issues:**
- Reduce number of connected accounts
- Increase sync intervals
- Check available disk space

### Getting Help

- 📖 Check the [Wiki](https://github.com/yourusername/MultiDriver_Hub/wiki)
- 🐛 Report bugs via [Issues](https://github.com/yourusername/MultiDriver_Hub/issues)
- 💬 Join discussions in [Discussions](https://github.com/yourusername/MultiDriver_Hub/discussions)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Drive API** for providing the underlying file management capabilities
- **Qt/PySide6** for the excellent GUI framework
- **Express.js** for the robust backend framework
- **SQLite** for the reliable local database
- **All contributors** who help make this project better

---

## 📞 Support

<div align="center">

**Made with ❤️ by [Your Name]**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/yourusername)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/yourusername)
[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/yourusername)

**⭐ Star this repository if you found it helpful!**

</div>

---

<div align="center">

### 🚀 Ready to manage your Google Drive like a pro?

[**Get Started Now**](#-installation) • [**View Screenshots**](#-screenshots) • [**Read Documentation**](#-usage)

</div>