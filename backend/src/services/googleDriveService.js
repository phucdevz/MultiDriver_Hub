const { google } = require('googleapis');
const crypto = require('crypto');

class GoogleDriveService {
  constructor() {
    this.oauth2Client = new google.auth.OAuth2(
      process.env.GOOGLE_CLIENT_ID,
      process.env.GOOGLE_CLIENT_SECRET,
      process.env.GOOGLE_REDIRECT_URI
    );
    
    // Preserve both raw key material (for legacy password-based cipher)
    // and a 32-byte key (for modern AES-256-GCM with IV)
    this.rawKeyMaterial = process.env.ENCRYPTION_KEY || 'default-key-32-chars-long-here';
    this.encryptionKey = crypto.createHash('sha256').update(String(this.rawKeyMaterial)).digest();
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
    try {
      const iv = crypto.randomBytes(12); // 96-bit IV recommended for GCM
      const cipher = crypto.createCipheriv('aes-256-gcm', this.encryptionKey, iv);
      const encrypted = Buffer.concat([cipher.update(token, 'utf8'), cipher.final()]);
      const authTag = cipher.getAuthTag();
      return {
        encrypted: encrypted.toString('hex'),
        iv: iv.toString('hex'),
        authTag: authTag.toString('hex')
      };
    } catch (error) {
      console.error('Error encrypting token:', error);
      throw new Error('Failed to encrypt token');
    }
  }

  // Decrypt refresh token for use
  decryptToken(encryptedData) {
    // Handle different encryption formats
    try {
      // Case 1: New AES-256-GCM format with IV and authTag
      if (encryptedData.iv && encryptedData.authTag && encryptedData.encrypted) {
        try {
          const iv = Buffer.from(encryptedData.iv, 'hex');
          const authTag = Buffer.from(encryptedData.authTag, 'hex');
          const decipher = crypto.createDecipheriv('aes-256-gcm', this.encryptionKey, iv);
          decipher.setAuthTag(authTag);
          const decrypted = Buffer.concat([
            decipher.update(Buffer.from(encryptedData.encrypted, 'hex')),
            decipher.final()
          ]);
          return decrypted.toString('utf8');
        } catch (gcmError) {
          console.warn('GCM decryption failed, trying legacy method:', gcmError.message);
        }
      }
      
      // Case 2: Legacy format - direct encrypted string
      if (typeof encryptedData === 'string') {
        try {
          // Try with raw key material first
          const legacyDecipher = crypto.createDecipher('aes-256-cbc', this.rawKeyMaterial);
          let decrypted = legacyDecipher.update(encryptedData, 'hex', 'utf8');
          decrypted += legacyDecipher.final('utf8');
          return decrypted;
        } catch (cbcError) {
          console.warn('CBC decryption failed, trying other methods:', cbcError.message);
        }
      }
      
      // Case 3: Legacy format - object with encrypted property
      if (encryptedData.encrypted && typeof encryptedData.encrypted === 'string') {
        try {
          const legacyDecipher = crypto.createDecipher('aes-256-cbc', this.rawKeyMaterial);
          let decrypted = legacyDecipher.update(encryptedData.encrypted, 'hex', 'utf8');
          decrypted += legacyDecipher.final('utf8');
          return decrypted;
        } catch (cbcError) {
          console.warn('CBC decryption with object failed:', cbcError.message);
        }
      }
      
      // Case 4: Try with different algorithms
      const algorithms = ['aes-256-cbc', 'aes-192-cbc', 'aes-128-cbc'];
      for (const algorithm of algorithms) {
        try {
          const legacyDecipher = crypto.createDecipher(algorithm, this.rawKeyMaterial);
          let decrypted;
          if (typeof encryptedData === 'string') {
            decrypted = legacyDecipher.update(encryptedData, 'hex', 'utf8');
            decrypted += legacyDecipher.final('utf8');
          } else if (encryptedData.encrypted) {
            decrypted = legacyDecipher.update(encryptedData.encrypted, 'hex', 'utf8');
            decrypted += legacyDecipher.final('utf8');
          } else {
            continue;
          }
          console.log(`Successfully decrypted with ${algorithm}`);
          return decrypted;
        } catch (algoError) {
          console.warn(`${algorithm} decryption failed:`, algoError.message);
        }
      }
      
      throw new Error('All decryption methods failed');
      
    } catch (error) {
      console.error('Error decrypting token (all methods failed):', error);
      console.error('Encrypted data format:', typeof encryptedData, encryptedData);
      throw new Error('Failed to decrypt token - data may be corrupted or encrypted with different key');
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
