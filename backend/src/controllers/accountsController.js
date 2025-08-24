const express = require('express');
const router = express.Router();
const db = require('../models/database');
const googleDriveService = require('../services/googleDriveService');

// Start OAuth flow
router.post('/oauth/start', async (req, res) => {
  try {
    const authUrl = googleDriveService.generateAuthUrl();
    res.json({
      success: true,
      authUrl: authUrl
    });
  } catch (error) {
    console.error('Error starting OAuth:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start OAuth flow'
    });
  }
});

// OAuth callback
router.get('/oauth/callback', async (req, res) => {
  try {
    const { code } = req.query;
    
    if (!code) {
      return res.status(400).json({
        success: false,
        error: 'Authorization code is required'
      });
    }

    // Exchange code for tokens
    const tokens = await googleDriveService.getTokensFromCode(code);
    
    if (!tokens.refresh_token) {
      return res.status(400).json({
        success: false,
        error: 'No refresh token received. Please try again with consent prompt.'
      });
    }

    // Get user info from Google
    googleDriveService.setCredentials(tokens);
    const drive = googleDriveService.getDriveAPI();
    const about = await drive.about.get({ fields: 'user' });
    const userEmail = about.data.user.emailAddress;

    // Encrypt refresh token
    const encryptedToken = googleDriveService.encryptToken(tokens.refresh_token);

    // Check if account already exists
    const existingAccount = await db.get(
      'SELECT * FROM drive_accounts WHERE account_key = ?',
      [userEmail]
    );

    if (existingAccount) {
      // Update existing account
      await db.run(
        `UPDATE drive_accounts SET 
         refresh_token_enc = ?, 
         auth_type = 'oauth',
         status = 'idle',
         updated_at = CURRENT_TIMESTAMP
         WHERE account_key = ?`,
        [JSON.stringify(encryptedToken), userEmail]
      );
    } else {
      // Create new account
      await db.run(
        `INSERT INTO drive_accounts 
         (email, account_key, auth_type, refresh_token_enc, connected_at, status) 
         VALUES (?, ?, 'oauth', ?, CURRENT_TIMESTAMP, 'idle')`,
        [userEmail, userEmail, JSON.stringify(encryptedToken)]
      );
    }

    res.json({
      success: true,
      message: 'Account connected successfully',
      email: userEmail
    });

  } catch (error) {
    console.error('Error in OAuth callback:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to complete OAuth flow'
    });
  }
});

// Register Service Account
router.post('/sa', async (req, res) => {
  try {
    const { alias, privateKey, rootFolderIds } = req.body;

    if (!alias || !privateKey || !rootFolderIds || !Array.isArray(rootFolderIds)) {
      return res.status(400).json({
        success: false,
        error: 'Alias, private key, and root folder IDs array are required'
      });
    }

    // Check if SA alias already exists
    const existingAccount = await db.get(
      'SELECT * FROM drive_accounts WHERE account_key = ?',
      [alias]
    );

    if (existingAccount) {
      return res.status(409).json({
        success: false,
        error: 'Service Account alias already exists'
      });
    }

    // Encrypt private key
    const encryptedKey = googleDriveService.encryptToken(privateKey);

    // Create account
    await db.run(
      `INSERT INTO drive_accounts 
       (sa_alias, account_key, auth_type, refresh_token_enc, roots, status) 
       VALUES (?, ?, 'sa_share', ?, ?, 'idle')`,
      [alias, alias, JSON.stringify(encryptedKey), JSON.stringify(rootFolderIds)]
    );

    res.json({
      success: true,
      message: 'Service Account registered successfully',
      alias: alias
    });

  } catch (error) {
    console.error('Error registering SA:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to register Service Account'
    });
  }
});

// Get all accounts
router.get('/', async (req, res) => {
  try {
    const accounts = await db.all(
      `SELECT 
         id, email, sa_alias, account_key, auth_type, status, 
         connected_at, last_sync_at, created_at
       FROM drive_accounts 
       ORDER BY created_at DESC`
    );

    res.json({
      success: true,
      accounts: accounts
    });

  } catch (error) {
    console.error('Error getting accounts:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get accounts'
    });
  }
});

// Get account by key (email or SA alias)
router.get('/:key', async (req, res) => {
  try {
    const { key } = req.params;
    
    const account = await db.get(
      `SELECT 
         id, email, sa_alias, account_key, auth_type, status, 
         connected_at, last_sync_at, created_at
       FROM drive_accounts 
       WHERE account_key = ?`,
      [key]
    );

    if (!account) {
      return res.status(404).json({
        success: false,
        error: 'Account not found'
      });
    }

    res.json({
      success: true,
      account: account
    });

  } catch (error) {
    console.error('Error getting account:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get account'
    });
  }
});

// Delete account
router.delete('/:key', async (req, res) => {
  try {
    const { key } = req.params;
    
    // First delete all files associated with this account
    await db.run(
      'DELETE FROM drive_files WHERE account_key = ?',
      [key]
    );

    // Then delete the account
    const result = await db.run(
      'DELETE FROM drive_accounts WHERE account_key = ?',
      [key]
    );

    if (result.changes === 0) {
      return res.status(404).json({
        success: false,
        error: 'Account not found'
      });
    }

    res.json({
      success: true,
      message: 'Account deleted successfully'
    });

  } catch (error) {
    console.error('Error deleting account:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to delete account'
    });
  }
});

// Get account status
router.get('/:key/status', async (req, res) => {
  try {
    const { key } = req.params;
    
    const account = await db.get(
      'SELECT status, last_sync_at FROM drive_accounts WHERE account_key = ?',
      [key]
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
      [key]
    );

    res.json({
      success: true,
      status: account.status,
      lastSyncAt: account.last_sync_at,
      fileCount: fileCount.count
    });

  } catch (error) {
    console.error('Error getting account status:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get account status'
    });
  }
});

module.exports = router;
