const express = require('express');
const router = express.Router();
const db = require('../models/database');
const googleDriveService = require('../services/googleDriveService');

// Start initial crawl for an account
router.post('/:accountKey/initial', async (req, res) => {
  try {
    const { accountKey } = req.params;
    
    // Get account details
    const account = await db.get(
      'SELECT * FROM drive_accounts WHERE email = ? OR sa_alias = ?',
      [accountKey, accountKey]
    );

    if (!account) {
      return res.status(404).json({
        success: false,
        error: 'Account not found'
      });
    }

    // Update account status to crawling
    await db.run(
      'UPDATE drive_accounts SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
      ['crawling', account.id]
    );

    // Start initial crawl in background
    initialCrawl(account).catch(error => {
      // Log detailed error information for diagnostics
      try {
        const details = {
          message: error?.message,
          code: error?.code,
          errors: error?.errors,
          responseData: error?.response?.data,
          stack: error?.stack
        };
        console.error('Initial crawl error details:', JSON.stringify(details, null, 2));
      } catch (e) {
        console.error('Initial crawl error:', error);
      }
      // Update status to error if crawl fails
      db.run(
        'UPDATE drive_accounts SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        ['error', account.id]
      );
    });

    res.json({
      success: true,
      message: 'Initial crawl started',
      accountKey: accountKey
    });

  } catch (error) {
    console.error('Error starting initial crawl:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start initial crawl'
    });
  }
});

// Start incremental sync for an account
router.post('/:accountKey/incremental', async (req, res) => {
  try {
    const { accountKey } = req.params;
    
    // Get account details
    const account = await db.get(
      'SELECT * FROM drive_accounts WHERE email = ? OR sa_alias = ?',
      [accountKey, accountKey]
    );

    if (!account) {
      return res.status(404).json({
        success: false,
        error: 'Account not found'
      });
    }

    // Update account status to syncing
    await db.run(
      'UPDATE drive_accounts SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
      ['syncing', account.id]
    );

    // Start incremental sync in background
    incrementalSync(account).catch(error => {
      try {
        const details = {
          message: error?.message,
          code: error?.code,
          errors: error?.errors,
          responseData: error?.response?.data,
          stack: error?.stack
        };
        console.error('Incremental sync error details:', JSON.stringify(details, null, 2));
      } catch (e) {
        console.error('Incremental sync error:', error);
      }
      // Update status to error if sync fails
      db.run(
        'UPDATE drive_accounts SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        ['error', account.id]
      );
    });

    res.json({
      success: true,
      message: 'Incremental sync started',
      accountKey: accountKey
    });

  } catch (error) {
    console.error('Error starting incremental sync:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start incremental sync'
    });
  }
});

// Get sync status for an account
router.get('/:accountKey/status', async (req, res) => {
  try {
    const { accountKey } = req.params;
    
    const account = await db.get(
      'SELECT status, last_sync_at FROM drive_accounts WHERE email = ? OR sa_alias = ?',
      [accountKey, accountKey]
    );

    if (!account) {
      return res.status(404).json({
        success: false,
        error: 'Account not found'
      });
    }

    // Get file count for this account
    const fileCount = await db.get(
      'SELECT COUNT(*) as count FROM drive_files WHERE account_key = ?',
      [accountKey]
    );

    res.json({
      success: true,
      status: account.status,
      lastSyncAt: account.last_sync_at,
      fileCount: fileCount.count
    });

  } catch (error) {
    console.error('Error getting sync status:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get sync status'
    });
  }
});

// Initial crawl function
async function initialCrawl(account) {
  try {
    console.log(`Starting initial crawl for account: ${account.email || account.sa_alias}`);
    
    let totalFiles = 0;
    let totalSize = 0;
    
    if (account.auth_type === 'oauth') {
      // OAuth: crawl entire My Drive
      await crawlOAuthAccount(account, (fileCount, size) => {
        totalFiles += fileCount;
        totalSize += size;
      });
    } else if (account.auth_type === 'sa_share') {
      // SA: crawl only shared folders
      const roots = JSON.parse(account.roots || '[]');
      for (const rootId of roots) {
        await crawlSAFolder(account, rootId, (fileCount, size) => {
          totalFiles += fileCount;
          totalSize += size;
        });
      }
    }

    // Update account status and sync time
    await db.run(
      `UPDATE drive_accounts SET 
       status = 'idle', 
       last_sync_at = CURRENT_TIMESTAMP,
       updated_at = CURRENT_TIMESTAMP
       WHERE id = ?`,
      [account.id]
    );

    console.log(`Initial crawl completed for ${account.email || account.sa_alias}: ${totalFiles} files, ${totalSize} bytes`);

  } catch (error) {
    console.error('Initial crawl failed:', error);
    throw error;
  }
}

// Incremental sync function
async function incrementalSync(account) {
  try {
    console.log(`Starting incremental sync for account: ${account.email || account.sa_alias}`);
    
    if (account.auth_type === 'oauth') {
      // OAuth: use Changes API
      await syncOAuthChanges(account);
    } else if (account.auth_type === 'sa_share') {
      // SA: check modified time for shared folders
      await syncSAModifications(account);
    }

    // Update account status and sync time
    await db.run(
      `UPDATE drive_accounts SET 
       status = 'idle', 
       last_sync_at = CURRENT_TIMESTAMP,
       updated_at = CURRENT_TIMESTAMP
       WHERE id = ?`,
      [account.id]
    );

    console.log(`Incremental sync completed for ${account.email || account.sa_alias}`);

  } catch (error) {
    console.error('Incremental sync failed:', error);
    throw error;
  }
}

// Crawl OAuth account (entire My Drive)
async function crawlOAuthAccount(account, progressCallback) {
  // Set up credentials
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
      
      // Process files in batch
      await processFilesBatch(account, files);
      
      totalFiles += files.length;
      totalSize += files.reduce((sum, file) => sum + (file.size || 0), 0);
      
      if (progressCallback) {
        progressCallback(files.length, files.reduce((sum, file) => sum + (file.size || 0), 0));
      }

      pageToken = response.nextPageToken;
      
      // Rate limiting: wait a bit between requests
      await new Promise(resolve => setTimeout(resolve, 100));
      
    } catch (error) {
      const errorInfo = googleDriveService.handleAPIError(error);
      console.error('listFiles OAuth error:', {
        message: error?.message,
        code: error?.code,
        errors: error?.errors,
        responseData: error?.response?.data
      });
      if (errorInfo.shouldRetry) {
        console.log(`Rate limited, waiting ${errorInfo.retryAfter} seconds...`);
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
async function crawlSAFolder(account, folderId, progressCallback) {
  // Set up SA credentials
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
      
      // Process files in batch
      await processFilesBatch(account, files);
      
      totalFiles += files.length;
      totalSize += files.reduce((sum, file) => sum + (file.size || 0), 0);
      
      if (progressCallback) {
        progressCallback(files.length, files.reduce((sum, file) => sum + (file.size || 0), 0));
      }

      pageToken = response.nextPageToken;
      
      // Rate limiting
      await new Promise(resolve => setTimeout(resolve, 100));
      
    } catch (error) {
      const errorInfo = googleDriveService.handleAPIError(error);
      console.error('listFiles SA error:', {
        message: error?.message,
        code: error?.code,
        errors: error?.errors,
        responseData: error?.response?.data
      });
      if (errorInfo.shouldRetry) {
        console.log(`Rate limited, waiting ${errorInfo.retryAfter} seconds...`);
        await new Promise(resolve => setTimeout(resolve, errorInfo.retryAfter * 1000));
        continue;
      } else {
        throw error;
      }
    }
  } while (pageToken);

  return { totalFiles, totalSize };
}

// Process files batch and insert/update in database
async function processFilesBatch(account, files) {
  const accountKey = account.email || account.sa_alias;
  
  for (const file of files) {
    try {
      // Check if file already exists
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
        // Update existing file
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
        // Insert new file
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
      console.error(`Error processing file ${file.id}:`, error);
      // Continue with other files
    }
  }
}

// Sync OAuth changes using Changes API
async function syncOAuthChanges(account) {
  try {
    console.log(`Starting OAuth changes sync for account: ${account.email}`);
    
    // Set up credentials
    const encryptedToken = JSON.parse(account.refresh_token_enc);
    const refreshToken = googleDriveService.decryptToken(encryptedToken);
    googleDriveService.setCredentials({ refresh_token: refreshToken });
    
    // Get or create start page token
    let startPageToken = account.start_page_token;
    if (!startPageToken) {
      startPageToken = await googleDriveService.getStartPageToken();
      // Update account with start page token
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
              // File was deleted
              await db.run(
                'DELETE FROM drive_files WHERE id = ? AND account_key = ?',
                [change.fileId, account.account_key]
              );
            } else if (change.file) {
              // File was modified or created
              const file = change.file;
              await processFilesBatch(account, [file]);
            }
            totalChanges++;
          }
        }
        
        pageToken = changes.nextPageToken;
        if (changes.newStartPageToken) {
          newStartPageToken = changes.newStartPageToken;
        }
        
        // Rate limiting
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        const errorInfo = googleDriveService.handleAPIError(error);
        if (errorInfo.shouldRetry) {
          console.log(`Rate limited, waiting ${errorInfo.retryAfter} seconds...`);
          await new Promise(resolve => setTimeout(resolve, errorInfo.retryAfter * 1000));
          continue;
        } else {
          throw error;
        }
      }
    } while (pageToken);
    
    // Update start page token for next sync
    if (newStartPageToken) {
      await db.run(
        'UPDATE drive_accounts SET start_page_token = ? WHERE id = ?',
        [newStartPageToken, account.id]
      );
    }
    
    console.log(`OAuth changes sync completed: ${totalChanges} changes processed`);
    
  } catch (error) {
    console.error('OAuth changes sync failed:', error);
    throw error;
  }
}

// Sync SA modifications by checking modified time
async function syncSAModifications(account) {
  try {
    console.log(`Starting SA modifications sync for account: ${account.sa_alias}`);
    
    // Set up SA credentials
    const encryptedKey = JSON.parse(account.refresh_token_enc);
    const privateKey = googleDriveService.decryptToken(encryptedKey);
    googleDriveService.setCredentials({ private_key: privateKey });
    
    const roots = JSON.parse(account.roots || '[]');
    let totalChanges = 0;
    
    for (const rootId of roots) {
      // Get last sync time for this root
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
            await processFilesBatch(account, files);
            totalChanges += files.length;
          }
          
          pageToken = response.nextPageToken;
          
          // Rate limiting
          await new Promise(resolve => setTimeout(resolve, 100));
          
        } catch (error) {
          const errorInfo = googleDriveService.handleAPIError(error);
          if (errorInfo.shouldRetry) {
            console.log(`Rate limited, waiting ${errorInfo.retryAfter} seconds...`);
            await new Promise(resolve => setTimeout(resolve, errorInfo.retryAfter * 1000));
            continue;
          } else {
            throw error;
          }
        }
      } while (pageToken);
    }
    
    console.log(`SA modifications sync completed: ${totalChanges} files updated`);
    
  } catch (error) {
    console.error('SA modifications sync failed:', error);
    throw error;
  }
}

// Export functions for use in other controllers
module.exports = {
  router,
  startInitialCrawl: async (accountKey) => {
    try {
      // Get account details
      const account = await db.get(
        'SELECT * FROM drive_accounts WHERE email = ? OR sa_alias = ?',
        [accountKey, accountKey]
      );

      if (!account) {
        throw new Error('Account not found');
      }

      // Update account status to crawling
      await db.run(
        'UPDATE drive_accounts SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        ['crawling', account.id]
      );

      // Start initial crawl in background
      initialCrawl(account).catch(error => {
        console.error(`Initial crawl failed for ${accountKey}:`, error);
        // Update status to error if crawl fails
        db.run(
          'UPDATE drive_accounts SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
          ['error', account.id]
        );
      });

      return { success: true, message: 'Initial crawl started' };
    } catch (error) {
      console.error('Error starting initial crawl:', error);
      throw error;
    }
  }
};
