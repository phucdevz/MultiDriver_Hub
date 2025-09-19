const db = require('../models/database');
const googleDriveService = require('./googleDriveService');
const winston = require('winston');

class BackgroundSyncService {
  constructor() {
    this.logger = winston.createLogger({
      level: 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
      defaultMeta: { service: 'background-sync' },
      transports: [
        new winston.transports.File({ filename: 'logs/background-sync.log' })
      ]
    });
    
    this.syncIntervals = new Map(); // Store intervals for each account
    this.isRunning = false;
  }

  // Start background sync for all accounts
  async startBackgroundSync() {
    if (this.isRunning) {
      this.logger.info('Background sync already running');
      return;
    }

    this.isRunning = true;
    this.logger.info('Starting background sync service');

    try {
      // Get all active accounts
      const accounts = await db.all(
        'SELECT * FROM drive_accounts WHERE status != "error"'
      );

      for (const account of accounts) {
        await this.startAccountSync(account);
      }

      // Start periodic health check
      this.startHealthCheck();

    } catch (error) {
      this.logger.error('Failed to start background sync:', error);
      this.isRunning = false;
    }
  }

  // Start sync for a specific account
  async startAccountSync(account) {
    try {
      const accountKey = account.email || account.sa_alias;
      
      // Clear existing interval if any
      if (this.syncIntervals.has(accountKey)) {
        clearInterval(this.syncIntervals.get(accountKey));
      }

      // Determine sync interval based on account type and activity
      const syncInterval = this.getSyncInterval(account);
      
      this.logger.info(`Starting sync for ${accountKey} with interval ${syncInterval}ms`);

      // Start periodic sync
      const interval = setInterval(async () => {
        await this.performIncrementalSync(account);
      }, syncInterval);

      this.syncIntervals.set(accountKey, interval);

      // Perform initial sync if needed
      if (!account.last_sync_at) {
        await this.performInitialSync(account);
      } else {
        // Quick incremental sync on startup
        await this.performIncrementalSync(account);
      }

    } catch (error) {
      this.logger.error(`Failed to start sync for ${account.email || account.sa_alias}:`, error);
    }
  }

  // Get appropriate sync interval for account
  getSyncInterval(account) {
    // OAuth accounts: sync every 5 minutes
    if (account.auth_type === 'oauth') {
      return 5 * 60 * 1000; // 5 minutes
    }
    
    // SA accounts: sync every 15 minutes (less frequent for shared folders)
    if (account.auth_type === 'sa_share') {
      return 15 * 60 * 1000; // 15 minutes
    }

    // Default: 10 minutes
    return 10 * 60 * 1000;
  }

  // Perform initial sync for account
  async performInitialSync(account) {
    try {
      const accountKey = account.email || account.sa_alias;
      this.logger.info(`Starting initial sync for ${accountKey}`);

      // Update status to syncing
      await db.run(
        'UPDATE drive_accounts SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        ['syncing', account.id]
      );

      let totalFiles = 0;
      let totalSize = 0;

      if (account.auth_type === 'oauth') {
        const result = await this.crawlOAuthAccount(account);
        totalFiles = result.totalFiles;
        totalSize = result.totalSize;
      } else if (account.auth_type === 'sa_share') {
        const roots = JSON.parse(account.roots || '[]');
        for (const rootId of roots) {
          const result = await this.crawlSAFolder(account, rootId);
          totalFiles += result.totalFiles;
          totalSize += result.totalSize;
        }
      }

      // Update account status
      await db.run(
        `UPDATE drive_accounts SET 
         status = 'idle', 
         last_sync_at = CURRENT_TIMESTAMP,
         updated_at = CURRENT_TIMESTAMP
         WHERE id = ?`,
        [account.id]
      );

      this.logger.info(`Initial sync completed for ${accountKey}: ${totalFiles} files, ${totalSize} bytes`);

    } catch (error) {
      this.logger.error(`Initial sync failed for ${account.email || account.sa_alias}:`, error);
      
      // Update status to error
      await db.run(
        'UPDATE drive_accounts SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        ['error', account.id]
      );
    }
  }

  // Perform incremental sync for account
  async performIncrementalSync(account) {
    try {
      const accountKey = account.email || account.sa_alias;
      this.logger.info(`Starting incremental sync for ${accountKey}`);

      // Update status to syncing
      await db.run(
        'UPDATE drive_accounts SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        ['syncing', account.id]
      );

      let changes = 0;

      if (account.auth_type === 'oauth') {
        changes = await this.syncOAuthChanges(account);
      } else if (account.auth_type === 'sa_share') {
        changes = await this.syncSAModifications(account);
      }

      // Update account status
      await db.run(
        `UPDATE drive_accounts SET 
         status = 'idle', 
         last_sync_at = CURRENT_TIMESTAMP,
         updated_at = CURRENT_TIMESTAMP
         WHERE id = ?`,
        [account.id]
      );

      this.logger.info(`Incremental sync completed for ${accountKey}: ${changes} changes`);

    } catch (error) {
      this.logger.error(`Incremental sync failed for ${account.email || account.sa_alias}:`, error);
      
      // Update status to error
      await db.run(
        'UPDATE drive_accounts SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        ['error', account.id]
      );
    }
  }

  // Crawl OAuth account (entire My Drive)
  async crawlOAuthAccount(account) {
    const encryptedToken = JSON.parse(account.refresh_token_enc);
    const refreshToken = googleDriveService.decryptToken(encryptedToken);
    googleDriveService.setCredentials({ refresh_token: refreshToken });

    let pageToken = null;
    let totalFiles = 0;
    let totalSize = 0;

    do {
      try {
        const response = await googleDriveService.listFiles({
          pageToken: pageToken,
          pageSize: 1000,
          fields: 'nextPageToken, files(id, name, mimeType, size, md5Checksum, parents, modifiedTime, shortcutDetails, trashed, ownedByMe, owners(emailAddress))'
        });

        const files = response.files || [];
        await this.processFilesBatch(account, files);
        
        totalFiles += files.length;
        totalSize += files.reduce((sum, file) => sum + (file.size || 0), 0);

        pageToken = response.nextPageToken;
        await new Promise(resolve => setTimeout(resolve, 100)); // Rate limiting

      } catch (error) {
        const errorInfo = googleDriveService.handleAPIError(error);
        if (errorInfo.shouldRetry) {
          this.logger.warn(`Rate limited, waiting ${errorInfo.retryAfter} seconds...`);
          await new Promise(resolve => setTimeout(resolve, errorInfo.retryAfter * 1000));
          continue;
        } else {
          throw error;
        }
      }
    } while (pageToken);

    return { totalFiles, totalSize };
  }

  // Crawl SA shared folder
  async crawlSAFolder(account, folderId) {
    const encryptedKey = JSON.parse(account.refresh_token_enc);
    const privateKey = googleDriveService.decryptToken(encryptedKey);
    googleDriveService.setCredentials({ private_key: privateKey });

    let pageToken = null;
    let totalFiles = 0;
    let totalSize = 0;

    do {
      try {
        const response = await googleDriveService.listFiles({
          pageToken: pageToken,
          pageSize: 1000,
          query: `'${folderId}' in parents and trashed = false`,
          fields: 'nextPageToken, files(id, name, mimeType, size, md5Checksum, parents, modifiedTime, shortcutDetails, trashed, ownedByMe, owners(emailAddress))'
        });

        const files = response.files || [];
        await this.processFilesBatch(account, files);
        
        totalFiles += files.length;
        totalSize += files.reduce((sum, file) => sum + (file.size || 0), 0);

        pageToken = response.nextPageToken;
        await new Promise(resolve => setTimeout(resolve, 100)); // Rate limiting

      } catch (error) {
        const errorInfo = googleDriveService.handleAPIError(error);
        if (errorInfo.shouldRetry) {
          this.logger.warn(`Rate limited, waiting ${errorInfo.retryAfter} seconds...`);
          await new Promise(resolve => setTimeout(resolve, errorInfo.retryAfter * 1000));
          continue;
        } else {
          throw error;
        }
      }
    } while (pageToken);

    return { totalFiles, totalSize };
  }

  // Sync OAuth changes using Changes API
  async syncOAuthChanges(account) {
    const encryptedToken = JSON.parse(account.refresh_token_enc);
    const refreshToken = googleDriveService.decryptToken(encryptedToken);
    googleDriveService.setCredentials({ refresh_token: refreshToken });

    let startPageToken = account.start_page_token;
    if (!startPageToken) {
      startPageToken = await googleDriveService.getStartPageToken();
      await db.run(
        'UPDATE drive_accounts SET start_page_token = ? WHERE id = ?',
        [startPageToken, account.id]
      );
    }

    let pageToken = startPageToken;
    let newStartPageToken = null;
    let totalChanges = 0;

    do {
      try {
        const changes = await googleDriveService.getChanges(pageToken, 1000);

        if (changes.changes) {
          for (const change of changes.changes) {
            if (change.removed) {
              await db.run(
                'DELETE FROM drive_files WHERE id = ? AND account_key = ?',
                [change.fileId, account.account_key]
              );
            } else if (change.file) {
              await this.processFilesBatch(account, [change.file]);
            }
            totalChanges++;
          }
        }

        pageToken = changes.nextPageToken;
        if (changes.newStartPageToken) {
          newStartPageToken = changes.newStartPageToken;
        }

        await new Promise(resolve => setTimeout(resolve, 100)); // Rate limiting

      } catch (error) {
        const errorInfo = googleDriveService.handleAPIError(error);
        if (errorInfo.shouldRetry) {
          this.logger.warn(`Rate limited, waiting ${errorInfo.retryAfter} seconds...`);
          await new Promise(resolve => setTimeout(resolve, errorInfo.retryAfter * 1000));
          continue;
        } else {
          throw error;
        }
      }
    } while (pageToken);

    if (newStartPageToken) {
      await db.run(
        'UPDATE drive_accounts SET start_page_token = ? WHERE id = ?',
        [newStartPageToken, account.id]
      );
    }

    return totalChanges;
  }

  // Sync SA modifications by checking modified time
  async syncSAModifications(account) {
    const encryptedKey = JSON.parse(account.refresh_token_enc);
    const privateKey = googleDriveService.decryptToken(encryptedKey);
    googleDriveService.setCredentials({ private_key: privateKey });

    const roots = JSON.parse(account.roots || '[]');
    let totalChanges = 0;

    for (const rootId of roots) {
      const lastSyncTime = account.last_sync_at || new Date(0).toISOString();

      let pageToken = null;
      do {
        try {
          const response = await googleDriveService.listFiles({
            pageToken: pageToken,
            pageSize: 1000,
            query: `'${rootId}' in parents and modifiedTime > '${lastSyncTime}' and trashed = false`,
            fields: 'nextPageToken, files(id, name, mimeType, size, md5Checksum, parents, modifiedTime, shortcutDetails, trashed, ownedByMe, owners(emailAddress))'
          });

          const files = response.files || [];
          if (files.length > 0) {
            await this.processFilesBatch(account, files);
            totalChanges += files.length;
          }

          pageToken = response.nextPageToken;
          await new Promise(resolve => setTimeout(resolve, 100)); // Rate limiting

        } catch (error) {
          const errorInfo = googleDriveService.handleAPIError(error);
          if (errorInfo.shouldRetry) {
            this.logger.warn(`Rate limited, waiting ${errorInfo.retryAfter} seconds...`);
            await new Promise(resolve => setTimeout(resolve, errorInfo.retryAfter * 1000));
            continue;
          } else {
            throw error;
          }
        }
      } while (pageToken);
    }

    return totalChanges;
  }

  // Process files batch and insert/update in database
  async processFilesBatch(account, files) {
    const accountKey = account.email || account.sa_alias;

    for (const file of files) {
      try {
        const existingFile = await db.get(
          'SELECT id FROM drive_files WHERE id = ? AND account_key = ?',
          [file.id, accountKey]
        );

        const fileData = {
          id: file.id,
          account_key: accountKey,
          name: file.name,
          mime_type: file.mimeType,
          size: file.size || 0,
          md5: file.md5Checksum || null,
          parents: file.parents ? JSON.stringify(file.parents) : null,
          modified_time: file.modifiedTime,
          is_shortcut: file.shortcutDetails ? 1 : 0,
          shortcut_target_id: file.shortcutDetails?.targetId || null,
          trashed: file.trashed ? 1 : 0,
          owned_by_me: file.ownedByMe ? 1 : 0,
          owner_email: Array.isArray(file.owners) && file.owners.length > 0 ? (file.owners[0].emailAddress || null) : null
        };

        if (existingFile) {
          await db.run(
            `UPDATE drive_files SET 
             name = ?, mime_type = ?, size = ?, md5 = ?, parents = ?,
             modified_time = ?, is_shortcut = ?, shortcut_target_id = ?, trashed = ?,
             owned_by_me = ?, owner_email = ?,
             updated_at = CURRENT_TIMESTAMP
             WHERE id = ? AND account_key = ?`,
            [
              fileData.name, fileData.mime_type, fileData.size, fileData.md5,
              fileData.parents, fileData.modified_time, fileData.is_shortcut,
              fileData.shortcut_target_id, fileData.trashed,
              fileData.owned_by_me, fileData.owner_email,
              fileData.id, accountKey
            ]
          );
        } else {
          await db.run(
            `INSERT INTO drive_files 
             (id, account_key, name, mime_type, size, md5, parents, modified_time, is_shortcut, shortcut_target_id, trashed, owned_by_me, owner_email)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
            [
              fileData.id, fileData.account_key, fileData.name, fileData.mime_type,
              fileData.size, fileData.md5, fileData.parents, fileData.modified_time,
              fileData.is_shortcut, fileData.shortcut_target_id, fileData.trashed,
              fileData.owned_by_me, fileData.owner_email
            ]
          );
        }
      } catch (error) {
        this.logger.error(`Error processing file ${file.id}:`, error);
      }
    }
  }

  // Start health check
  startHealthCheck() {
    setInterval(async () => {
      try {
        const accounts = await db.all(
          'SELECT * FROM drive_accounts WHERE status = "error"'
        );

        for (const account of accounts) {
          this.logger.info(`Attempting to restart sync for ${account.email || account.sa_alias}`);
          await this.startAccountSync(account);
        }
      } catch (error) {
        this.logger.error('Health check failed:', error);
      }
    }, 30 * 60 * 1000); // Every 30 minutes
  }

  // Stop background sync
  stopBackgroundSync() {
    this.isRunning = false;
    
    for (const [accountKey, interval] of this.syncIntervals) {
      clearInterval(interval);
      this.logger.info(`Stopped sync for ${accountKey}`);
    }
    
    this.syncIntervals.clear();
    this.logger.info('Background sync service stopped');
  }

  // Get sync status for all accounts
  async getSyncStatus() {
    try {
      const accounts = await db.all(
        'SELECT email, sa_alias, auth_type, status, last_sync_at, updated_at FROM drive_accounts'
      );

      return accounts.map(account => ({
        accountKey: account.email || account.sa_alias,
        authType: account.auth_type,
        status: account.status,
        lastSyncAt: account.last_sync_at,
        updatedAt: account.updated_at,
        isActive: this.syncIntervals.has(account.email || account.sa_alias)
      }));
    } catch (error) {
      this.logger.error('Failed to get sync status:', error);
      return [];
    }
  }
}

module.exports = new BackgroundSyncService();
