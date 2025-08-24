const express = require('express');
const router = express.Router();
const db = require('../models/database');

// Get duplicate files report
router.get('/dedup', async (req, res) => {
  try {
    const { 
      minSize = 0, 
      groupBy = 'md5', // 'md5', 'size', 'both'
      limit = 100 
    } = req.query;

    let query, params;

    if (groupBy === 'md5') {
      // Group by MD5 hash
      query = `
        SELECT 
          md5, 
          COUNT(*) as count, 
          SUM(size) as total_size,
          GROUP_CONCAT(id) as file_ids,
          GROUP_CONCAT(name) as file_names,
          GROUP_CONCAT(account_key) as accounts
        FROM drive_files 
        WHERE md5 IS NOT NULL AND size >= ? AND trashed = 0
        GROUP BY md5 
        HAVING COUNT(*) > 1
        ORDER BY total_size DESC 
        LIMIT ?
      `;
      params = [parseInt(minSize), parseInt(limit)];
    } else if (groupBy === 'size') {
      // Group by file size
      query = `
        SELECT 
          size, 
          COUNT(*) as count, 
          SUM(size) as total_size,
          GROUP_CONCAT(id) as file_ids,
          GROUP_CONCAT(name) as file_names,
          GROUP_CONCAT(account_key) as accounts
        FROM drive_files 
        WHERE size >= ? AND trashed = 0
        GROUP BY size 
        HAVING COUNT(*) > 1
        ORDER BY total_size DESC 
        LIMIT ?
      `;
      params = [parseInt(minSize), parseInt(limit)];
    } else {
      // Group by both MD5 and size
      query = `
        SELECT 
          md5, 
          size, 
          COUNT(*) as count, 
          SUM(size) as total_size,
          GROUP_CONCAT(id) as file_ids,
          GROUP_CONCAT(name) as file_names,
          GROUP_CONCAT(account_key) as accounts
        FROM drive_files 
        WHERE md5 IS NOT NULL AND size >= ? AND trashed = 0
        GROUP BY md5, size 
        HAVING COUNT(*) > 1
        ORDER BY total_size DESC 
        LIMIT ?
      `;
      params = [parseInt(minSize), parseInt(limit)];
    }

    const duplicates = await db.all(query, params);

    // Process results
    const processedDuplicates = duplicates.map(dup => {
      const result = {
        ...dup,
        fileIds: dup.file_ids ? dup.file_ids.split(',') : [],
        fileNames: dup.file_names ? dup.file_names.split(',') : [],
        accounts: dup.accounts ? dup.accounts.split(',') : [],
        potentialSavings: (dup.count - 1) * dup.size
      };
      
      // Remove raw concatenated fields
      delete result.file_ids;
      delete result.file_names;
      delete result.accounts;
      
      return result;
    });

    // Calculate summary
    const totalDuplicates = processedDuplicates.reduce((sum, dup) => sum + dup.count, 0);
    const totalSize = processedDuplicates.reduce((sum, dup) => sum + dup.total_size, 0);
    const potentialSavings = processedDuplicates.reduce((sum, dup) => sum + dup.potentialSavings, 0);

    res.json({
      success: true,
      data: {
        duplicates: processedDuplicates,
        summary: {
          totalGroups: processedDuplicates.length,
          totalDuplicates: totalDuplicates,
          totalSize: totalSize,
          potentialSavings: potentialSavings
        }
      }
    });

  } catch (error) {
    console.error('Error getting dedup report:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get dedup report'
    });
  }
});

// Get health report
router.get('/health', async (req, res) => {
  try {
    // Get overall statistics
    const overallStats = await db.get(`
      SELECT 
        COUNT(*) as total_files,
        SUM(size) as total_size,
        COUNT(DISTINCT account_key) as total_accounts
      FROM drive_files 
      WHERE trashed = 0
    `);

    // Get statistics by account
    const accountStats = await db.all(`
      SELECT 
        f.account_key,
        a.email,
        a.sa_alias,
        a.auth_type,
        a.status,
        a.last_sync_at,
        COUNT(*) as file_count,
        SUM(f.size) as total_size,
        COUNT(CASE WHEN f.md5 IS NULL THEN 1 END) as files_without_md5
      FROM drive_files f
              LEFT JOIN drive_accounts a ON f.account_key = a.account_key
      WHERE f.trashed = 0
      GROUP BY f.account_key
      ORDER BY total_size DESC
    `);

    // Get file type distribution
    const mimeTypeStats = await db.all(`
      SELECT 
        mime_type,
        COUNT(*) as count,
        SUM(size) as total_size
      FROM drive_files 
      WHERE trashed = 0
      GROUP BY mime_type 
      ORDER BY count DESC 
      LIMIT 10
    `);

    // Get size distribution
    const sizeDistribution = await db.all(`
      SELECT 
        CASE 
          WHEN size < 1024 THEN '0-1KB'
          WHEN size < 1024*1024 THEN '1KB-1MB'
          WHEN size < 10*1024*1024 THEN '1MB-10MB'
          WHEN size < 100*1024*1024 THEN '10MB-100MB'
          WHEN size < 1024*1024*1024 THEN '100MB-1GB'
          ELSE '1GB+'
        END as size_range,
        COUNT(*) as count,
        SUM(size) as total_size
      FROM drive_files 
      WHERE trashed = 0
      GROUP BY size_range
      ORDER BY total_size DESC
    `);

    // Get recent activity
    const recentActivity = await db.all(`
      SELECT 
        f.name,
        f.mime_type,
        f.size,
        f.modified_time,
        f.account_key
      FROM drive_files f
      WHERE f.trashed = 0
      ORDER BY f.modified_time DESC 
      LIMIT 10
    `);

    // Get sync status summary
    const syncStatusSummary = await db.all(`
      SELECT 
        status,
        COUNT(*) as count
      FROM drive_accounts 
      GROUP BY status
    `);

    // Calculate health score
    const healthScore = calculateHealthScore(overallStats, accountStats, syncStatusSummary);

    res.json({
      success: true,
      data: {
        overall: {
          totalFiles: overallStats.total_files || 0,
          totalSize: overallStats.total_size || 0,
          totalAccounts: overallStats.total_accounts || 0,
          healthScore: healthScore
        },
        accounts: accountStats,
        mimeTypes: mimeTypeStats,
        sizeDistribution: sizeDistribution,
        recentActivity: recentActivity,
        syncStatus: syncStatusSummary
      }
    });

  } catch (error) {
    console.error('Error getting health report:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get health report'
    });
  }
});

// Get storage analysis report
router.get('/storage', async (req, res) => {
  try {
    const { accountKey = '' } = req.query;
    
    let whereClause = 'WHERE trashed = 0';
    let params = [];
    
    if (accountKey) {
      whereClause += ' AND account_key = ?';
      params.push(accountKey);
    }

    // Get storage by folder (virtual folders based on parents)
    const folderStorage = await db.all(`
      SELECT 
        COALESCE(
          (SELECT name FROM drive_files WHERE id = (
            SELECT json_extract(parents, '$[0]') FROM drive_files f2 WHERE f2.id = f.id
          )), 
          'Root'
        ) as folder_name,
        COUNT(*) as file_count,
        SUM(size) as total_size,
        AVG(size) as avg_size
      FROM drive_files f
      ${whereClause}
      GROUP BY folder_name
      ORDER BY total_size DESC
      LIMIT 20
    `, params);

    // Get storage by date (monthly)
    const monthlyStorage = await db.all(`
      SELECT 
        strftime('%Y-%m', modified_time) as month,
        COUNT(*) as file_count,
        SUM(size) as total_size
      FROM drive_files 
      ${whereClause}
      GROUP BY month
      ORDER BY month DESC
      LIMIT 12
    `, params);

    // Get largest files
    const largestFiles = await db.all(`
      SELECT 
        name, 
        mime_type, 
        size, 
        modified_time, 
        account_key
      FROM drive_files 
      ${whereClause}
      ORDER BY size DESC 
      LIMIT 20
    `, params);

    res.json({
      success: true,
      data: {
        folderStorage: folderStorage,
        monthlyStorage: monthlyStorage,
        largestFiles: largestFiles
      }
    });

  } catch (error) {
    console.error('Error getting storage report:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get storage report'
    });
  }
});

// Get sync performance report
router.get('/sync-performance', async (req, res) => {
  try {
    // Get sync history for each account
    const syncPerformance = await db.all(`
      SELECT 
        account_key,
        status,
        last_sync_at,
        created_at
      FROM drive_accounts 
      ORDER BY last_sync_at DESC
    `);

    // Calculate sync frequency and performance
    const performanceData = syncPerformance.map(account => {
      const lastSync = account.last_sync_at ? new Date(account.last_sync_at) : null;
      const created = new Date(account.created_at);
      const now = new Date();
      
      let syncFrequency = null;
      let lastSyncAge = null;
      
      if (lastSync) {
        lastSyncAge = Math.floor((now - lastSync) / (1000 * 60 * 60 * 24)); // days
      }
      
      const accountAge = Math.floor((now - created) / (1000 * 60 * 60 * 24)); // days
      
      return {
        accountKey: account.account_key,
        status: account.status,
        lastSyncAt: account.last_sync_at,
        lastSyncAge: lastSyncAge,
        accountAge: accountAge,
        syncHealth: getSyncHealth(account.status, lastSyncAge)
      };
    });

    res.json({
      success: true,
      data: {
        performance: performanceData
      }
    });

  } catch (error) {
    console.error('Error getting sync performance report:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get sync performance report'
    });
  }
});

// Helper function to calculate health score
function calculateHealthScore(overallStats, accountStats, syncStatusSummary) {
  let score = 100;
  
  // Deduct points for accounts with errors
  const errorAccounts = syncStatusSummary.find(s => s.status === 'error');
  if (errorAccounts) {
    score -= errorAccounts.count * 10;
  }
  
  // Deduct points for accounts not synced recently
  const now = new Date();
  const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
  
  accountStats.forEach(account => {
    if (account.last_sync_at) {
      const lastSync = new Date(account.last_sync_at);
      if (lastSync < oneWeekAgo) {
        score -= 5;
      }
    } else {
      score -= 15; // Never synced
    }
  });
  
  return Math.max(0, score);
}

// Helper function to get sync health status
function getSyncHealth(status, lastSyncAge) {
  if (status === 'error') return 'error';
  if (status === 'crawling' || status === 'syncing') return 'syncing';
  if (lastSyncAge === null) return 'never';
  if (lastSyncAge <= 1) return 'excellent';
  if (lastSyncAge <= 7) return 'good';
  if (lastSyncAge <= 30) return 'fair';
  return 'poor';
}

module.exports = router;
