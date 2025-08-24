const { google } = require('googleapis');
const crypto = require('crypto');

class GoogleDriveService {
  constructor() {
    this.oauth2Client = new google.auth.OAuth2(
      process.env.GOOGLE_CLIENT_ID,
      process.env.GOOGLE_CLIENT_SECRET,
      process.env.GOOGLE_REDIRECT_URI
    );
    
    this.encryptionKey = process.env.ENCRYPTION_KEY || 'default-key-32-chars-long-here';
  }

  // Generate OAuth URL for user to authorize
  generateAuthUrl() {
    const scopes = [
      'https://www.googleapis.com/auth/drive.metadata.readonly',
      'https://www.googleapis.com/auth/drive.readonly'
    ];

    return this.oauth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: scopes,
      prompt: 'consent',
      redirect_uri: process.env.GOOGLE_REDIRECT_URI
    });
  }

  // Exchange authorization code for tokens
  async getTokensFromCode(code) {
    try {
      const { tokens } = await this.oauth2Client.getToken(code);
      return tokens;
    } catch (error) {
      console.error('Error getting tokens:', error);
      throw new Error('Failed to exchange authorization code for tokens');
    }
  }

  // Encrypt refresh token for storage
  encryptToken(token) {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipher('aes-256-gcm', this.encryptionKey);
    
    let encrypted = cipher.update(token, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    return {
      encrypted: encrypted,
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex')
    };
  }

  // Decrypt refresh token for use
  decryptToken(encryptedData) {
    try {
      const decipher = crypto.createDecipher('aes-256-gcm', this.encryptionKey);
      decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));
      
      let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      
      return decrypted;
    } catch (error) {
      console.error('Error decrypting token:', error);
      throw new Error('Failed to decrypt token');
    }
  }

  // Set credentials for API calls
  setCredentials(tokens) {
    this.oauth2Client.setCredentials(tokens);
  }

  // Get Drive API instance
  getDriveAPI() {
    return google.drive({ version: 'v3', auth: this.oauth2Client });
  }

  // List files from Drive
  async listFiles(options = {}) {
    try {
      const drive = this.getDriveAPI();
      const response = await drive.files.list({
        pageSize: options.pageSize || 1000,
        fields: options.fields || 'nextPageToken, files(id, name, mimeType, size, md5Checksum, parents, modifiedTime, shortcutDetails, trashed)',
        q: options.query || '',
        supportsAllDrives: true,
        includeItemsFromAllDrives: true,
        ...options
      });
      
      return response.data;
    } catch (error) {
      console.error('Error listing files:', error);
      throw error;
    }
  }

  // Get file metadata
  async getFile(fileId, fields = 'id, name, mimeType, size, md5Checksum, parents, modifiedTime, shortcutDetails, trashed') {
    try {
      const drive = this.getDriveAPI();
      const response = await drive.files.get({
        fileId: fileId,
        fields: fields,
        supportsAllDrives: true
      });
      
      return response.data;
    } catch (error) {
      console.error('Error getting file:', error);
      throw error;
    }
  }

  // Get changes using Changes API
  async getChanges(startPageToken, pageSize = 1000) {
    try {
      const drive = this.getDriveAPI();
      const response = await drive.changes.list({
        pageToken: startPageToken,
        pageSize: pageSize,
        fields: 'nextPageToken, newStartPageToken, changes(file(id, name, mimeType, size, md5Checksum, parents, modifiedTime, shortcutDetails, trashed), fileId, removed)',
        supportsAllDrives: true,
        includeItemsFromAllDrives: true
      });
      
      return response.data;
    } catch (error) {
      console.error('Error getting changes:', error);
      throw error;
    }
  }

  // Get start page token for changes
  async getStartPageToken() {
    try {
      const drive = this.getDriveAPI();
      const response = await drive.changes.getStartPageToken({
        supportsAllDrives: true
      });
      
      return response.data.startPageToken;
    } catch (error) {
      console.error('Error getting start page token:', error);
      throw error;
    }
  }

  // Check if user has access to specific folder (for SA-share)
  async checkFolderAccess(folderId) {
    try {
      const drive = this.getDriveAPI();
      await drive.files.get({
        fileId: folderId,
        fields: 'id, name',
        supportsAllDrives: true
      });
      return true;
    } catch (error) {
      if (error.code === 404) {
        return false;
      }
      throw error;
    }
  }

  // Handle rate limiting and quota errors
  handleAPIError(error) {
    if (error.code === 429 || error.code === 403) {
      // Rate limit or quota exceeded
      const retryAfter = error.headers?.['retry-after'] || 60;
      return {
        shouldRetry: true,
        retryAfter: parseInt(retryAfter),
        error: 'Rate limit exceeded, please try again later'
      };
    }
    
    return {
      shouldRetry: false,
      error: error.message || 'Unknown error occurred'
    };
  }
}

module.exports = new GoogleDriveService();
