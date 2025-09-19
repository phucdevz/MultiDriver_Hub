const express = require('express');
const router = express.Router();
const db = require('../models/database');

// Search files with various filters
router.get('/', async (req, res) => {
  try {
    const {
      q = '', // search query
      owner = '', // account key (email or SA alias) or 'me'
      mime = '', // mime type filter
      minSize = '', // minimum file size
      maxSize = '', // maximum file size
      from = '', // date from (ISO string)
      to = '', // date to (ISO string)
      trashed = '', // include trashed files
      folders = '', // 'false' to exclude folders
      page = 1, // page number
      limit = 50, // items per page
      sort = 'modified_time' // sort field
    } = req.query;

    // Build WHERE clause
    let whereConditions = [];
    let params = [];
    let paramIndex = 1;

    // Text search using LIKE (fallback from FTS5)
    if (q.trim()) {
      whereConditions.push(`f.name LIKE ?`);
      params.push(`%${q}%`);
      paramIndex++;
    }

    // Owner filter
    if (owner) {
      if (owner === 'me') {
        // Only files the connected account actually owns
        whereConditions.push(`f.owned_by_me = 1`);
      } else {
        // Filter by a specific account key (email or SA alias)
        whereConditions.push(`f.account_key = ?`);
        params.push(owner);
        paramIndex++;
      }
    }

    // MIME type filter
    if (mime) {
      whereConditions.push(`f.mime_type = ?`);
      params.push(mime);
      paramIndex++;
    }

    // Exclude folders if requested
    if (folders === 'false') {
      whereConditions.push(`f.mime_type != 'application/vnd.google-apps.folder'`);
    }

    // Size filters
    if (minSize) {
      whereConditions.push(`f.size >= ?`);
      params.push(parseInt(minSize));
      paramIndex++;
    }
    if (maxSize) {
      whereConditions.push(`f.size <= ?`);
      params.push(parseInt(maxSize));
      paramIndex++;
    }

    // Date filters
    if (from) {
      whereConditions.push(`f.modified_time >= ?`);
      params.push(from);
      paramIndex++;
    }
    if (to) {
      whereConditions.push(`f.modified_time <= ?`);
      params.push(to);
      paramIndex++;
    }

    // Trashed filter
    if (trashed === 'true') {
      whereConditions.push(`f.trashed = 1`);
    } else if (trashed === 'false') {
      whereConditions.push(`f.trashed = 0`);
    }

    // Build the main query
    let query = `
      SELECT 
        f.id, f.name, f.mime_type, f.size, f.md5, f.parents,
        f.modified_time, f.is_shortcut, f.shortcut_target_id, f.trashed,
        f.account_key, f.owned_by_me, f.owner_email, f.created_at, f.updated_at
      FROM drive_files f
    `;

    // Add WHERE clause
    if (whereConditions.length > 0) {
      query += ` WHERE ` + whereConditions.join(' AND ');
    }
    
    // Add text search condition
    if (q.trim()) {
      const searchCondition = `f.name LIKE ?`;
      if (whereConditions.length > 0) {
        query += ` AND ${searchCondition}`;
      } else {
        query += ` WHERE ${searchCondition}`;
      }
      params.unshift(`%${q}%`);
    }

    // Add sorting
    const validSortFields = ['name', 'size', 'modified_time', 'created_at'];
    const sortField = validSortFields.includes(sort) ? sort : 'modified_time';
    const sortDirection = sort === 'name' ? 'ASC' : 'DESC';
    query += ` ORDER BY f.${sortField} ${sortDirection}`;

    // Add pagination
    const offset = (parseInt(page) - 1) * parseInt(limit);
    query += ` LIMIT ? OFFSET ?`;
    params.push(parseInt(limit), offset);

    // Execute search query
    const files = await db.all(query, params);

    // Get total count for pagination
    let countQuery = `
      SELECT COUNT(*) as total FROM drive_files f
    `;
    
    if (whereConditions.length > 0) {
      countQuery += ` WHERE ` + whereConditions.join(' AND ');
    }
    
    // Add text search condition to count query
    if (q.trim()) {
      const searchCondition = `f.name LIKE ?`;
      if (whereConditions.length > 0) {
        countQuery += ` AND ${searchCondition}`;
      } else {
        countQuery += ` WHERE ${searchCondition}`;
      }
    }

    const countResult = await db.get(countQuery, params.slice(0, -2)); // Remove LIMIT and OFFSET
    const total = countResult.total;

    // Calculate pagination info
    const totalPages = Math.ceil(total / parseInt(limit));
    const hasNext = parseInt(page) < totalPages;
    const hasPrev = parseInt(page) > 1;

    res.json({
      success: true,
      data: {
        files: files,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total: total,
          totalPages: totalPages,
          hasNext: hasNext,
          hasPrev: hasPrev
        }
      }
    });

  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({
      success: false,
      error: 'Search failed'
    });
  }
});

// Advanced search with multiple criteria
router.post('/advanced', async (req, res) => {
  try {
    const {
      queries = [], // array of search queries
      filters = {}, // object with filter criteria
      sort = {},
      pagination = {}
    } = req.body;

    // Build complex WHERE clause
    let whereConditions = [];
    let params = [];
    let paramIndex = 1;

    // Handle multiple search queries
    if (queries.length > 0) {
      const queryConditions = [];
      for (const query of queries) {
        if (query.field && query.value) {
          switch (query.field) {
            case 'name':
              queryConditions.push(`f.name LIKE ?`);
              params.push(`%${query.value}%`);
              paramIndex++;
              break;
            case 'content':
              // For future content search implementation
              break;
            case 'extension':
              queryConditions.push(`f.name LIKE ?`);
              params.push(`%.${query.value}`);
              paramIndex++;
              break;
          }
        }
      }
      if (queryConditions.length > 0) {
        whereConditions.push(`(${queryConditions.join(' OR ')})`);
      }
    }

    // Handle filters
    if (filters.owners && filters.owners.length > 0) {
      const placeholders = filters.owners.map(() => '?').join(',');
      whereConditions.push(`f.account_key IN (${placeholders})`);
      params.push(...filters.owners);
      paramIndex += filters.owners.length;
    }

    if (filters.mimeTypes && filters.mimeTypes.length > 0) {
      const placeholders = filters.mimeTypes.map(() => '?').join(',');
      whereConditions.push(`f.mime_type IN (${placeholders})`);
      params.push(...filters.mimeTypes);
      paramIndex += filters.mimeTypes.length;
    }

    if (filters.sizeRange) {
      if (filters.sizeRange.min !== undefined) {
        whereConditions.push(`f.size >= ?`);
        params.push(filters.sizeRange.min);
        paramIndex++;
      }
      if (filters.sizeRange.max !== undefined) {
        whereConditions.push(`f.size <= ?`);
        params.push(filters.sizeRange.max);
        paramIndex++;
      }
    }

    if (filters.dateRange) {
      if (filters.dateRange.from) {
        whereConditions.push(`f.modified_time >= ?`);
        params.push(filters.dateRange.from);
        paramIndex++;
      }
      if (filters.dateRange.to) {
        whereConditions.push(`f.modified_time <= ?`);
        params.push(filters.dateRange.to);
        paramIndex++;
      }
    }

    if (filters.trashed !== undefined) {
      whereConditions.push(`f.trashed = ?`);
      params.push(filters.trashed ? 1 : 0);
      paramIndex++;
    }

    if (filters.shortcuts !== undefined) {
      whereConditions.push(`f.is_shortcut = ?`);
      params.push(filters.shortcuts ? 1 : 0);
      paramIndex++;
    }

    // Build the main query
    let query = `
      SELECT 
        f.id, f.name, f.mime_type, f.size, f.md5, f.parents,
        f.modified_time, f.is_shortcut, f.shortcut_target_id, f.trashed,
        f.account_key, f.created_at, f.updated_at
      FROM drive_files f
    `;

    // Add FTS join if text search is used
    if (queries.some(q => q.field === 'name' || q.field === 'content')) {
      query += ` JOIN files_fts ON f.rowid = files_fts.rowid`;
    }

    // Add WHERE clause
    if (whereConditions.length > 0) {
      query += ` WHERE ` + whereConditions.join(' AND ');
    }

    // Add sorting
    const validSortFields = ['name', 'size', 'modified_time', 'created_at'];
    const sortField = validSortFields.includes(sort.field) ? sort.field : 'modified_time';
    const sortDirection = sort.direction === 'asc' ? 'ASC' : 'DESC';
    query += ` ORDER BY f.${sortField} ${sortDirection}`;

    // Add pagination
    const page = pagination.page || 1;
    const limit = pagination.limit || 50;
    const offset = (page - 1) * limit;
    query += ` LIMIT ? OFFSET ?`;
    params.push(limit, offset);

    // Execute search query
    const files = await db.all(query, params);

    // Get total count
    let countQuery = `
      SELECT COUNT(*) as total FROM drive_files f
    `;
    
    if (queries.some(q => q.field === 'name' || q.field === 'content')) {
      countQuery += ` JOIN files_fts ON f.rowid = files_fts.rowid`;
    }
    
    if (whereConditions.length > 0) {
      countQuery += ` WHERE ` + whereConditions.join(' AND ');
    }

    const countResult = await db.get(countQuery, params.slice(0, -2));
    const total = countResult.total;

    res.json({
      success: true,
      data: {
        files: files,
        pagination: {
          page: page,
          limit: limit,
          total: total,
          totalPages: Math.ceil(total / limit)
        }
      }
    });

  } catch (error) {
    console.error('Advanced search error:', error);
    res.status(500).json({
      success: false,
      error: 'Advanced search failed'
    });
  }
});

// Get search suggestions (autocomplete)
router.get('/suggestions', async (req, res) => {
  try {
    const { q = '', limit = 10 } = req.query;

    if (!q.trim()) {
      return res.json({
        success: true,
        suggestions: []
      });
    }

    // Get suggestions from FTS
    const suggestions = await db.all(
      `SELECT DISTINCT f.name 
       FROM drive_files f 
       JOIN files_fts ON f.rowid = files_fts.rowid 
       WHERE files_fts.name MATCH ? 
       ORDER BY f.modified_time DESC 
       LIMIT ?`,
      [q, parseInt(limit)]
    );

    res.json({
      success: true,
      suggestions: suggestions.map(s => s.name)
    });

  } catch (error) {
    console.error('Suggestions error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get suggestions'
    });
  }
});

// Get search statistics
router.get('/stats', async (req, res) => {
  try {
    const { owner = '' } = req.query;

    let whereClause = '';
    let params = [];

    if (owner) {
      whereClause = 'WHERE account_key = ?';
      params.push(owner);
    }

    // Get file count by MIME type
    const mimeStats = await db.all(
      `SELECT mime_type, COUNT(*) as count, SUM(size) as total_size
       FROM drive_files 
       ${whereClause}
       GROUP BY mime_type 
       ORDER BY count DESC 
       LIMIT 10`,
      params
    );

    // Get total file count and size
    const totalStats = await db.get(
      `SELECT COUNT(*) as total_files, SUM(size) as total_size
       FROM drive_files 
       ${whereClause}`,
      params
    );

    // Get recent files
    const recentFiles = await db.all(
      `SELECT name, mime_type, size, modified_time, account_key
       FROM drive_files 
       ${whereClause}
       ORDER BY modified_time DESC 
       LIMIT 5`,
      params
    );

    res.json({
      success: true,
      stats: {
        mimeTypes: mimeStats,
        totals: totalStats,
        recentFiles: recentFiles
      }
    });

  } catch (error) {
    console.error('Stats error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get search statistics'
    });
  }
});

// Export search results
router.get('/export', async (req, res) => {
  try {
    const {
      q = '', // search query
      owner = '', // account key (email or SA alias) or 'me'
      mime = '', // mime type filter
      minSize = '', // minimum file size
      maxSize = '', // maximum file size
      from = '', // date from (ISO string)
      to = '', // date to (ISO string)
      trashed = '', // include trashed files
      folders = '', // 'false' to exclude folders
      format = 'csv', // export format: csv, json, excel
      fields = 'name,mime_type,size,modified_time,account_key' // fields to export
    } = req.query;

    // Build WHERE clause (same as search)
    let whereConditions = [];
    let params = [];
    let paramIndex = 1;

    // Text search using LIKE (fallback from FTS5)
    if (q.trim()) {
      whereConditions.push(`f.name LIKE ?`);
      params.push(`%${q}%`);
      paramIndex++;
    }

    // Owner filter
    if (owner) {
      if (owner === 'me') {
        whereConditions.push(`f.owned_by_me = 1`);
      } else {
        whereConditions.push(`f.account_key = ?`);
        params.push(owner);
        paramIndex++;
      }
    }

    // MIME type filter
    if (mime) {
      whereConditions.push(`f.mime_type = ?`);
      params.push(mime);
      paramIndex++;
    }

    // Exclude folders if requested
    if (folders === 'false') {
      whereConditions.push(`f.mime_type != 'application/vnd.google-apps.folder'`);
    }

    // Size filters
    if (minSize) {
      whereConditions.push(`f.size >= ?`);
      params.push(parseInt(minSize));
      paramIndex++;
    }
    if (maxSize) {
      whereConditions.push(`f.size <= ?`);
      params.push(parseInt(maxSize));
      paramIndex++;
    }

    // Date filters
    if (from) {
      whereConditions.push(`f.modified_time >= ?`);
      params.push(from);
      paramIndex++;
    }
    if (to) {
      whereConditions.push(`f.modified_time <= ?`);
      params.push(to);
      paramIndex++;
    }

    // Trashed filter
    if (trashed === 'true') {
      whereConditions.push(`f.trashed = 1`);
    } else if (trashed === 'false') {
      whereConditions.push(`f.trashed = 0`);
    }

    // Build the main query
    let query = `
      SELECT 
        f.id, f.name, f.mime_type, f.size, f.md5, f.parents,
        f.modified_time, f.is_shortcut, f.shortcut_target_id, f.trashed,
        f.account_key, f.owned_by_me, f.owner_email, f.created_at, f.updated_at
      FROM drive_files f
    `;

    // No FTS join needed - using LIKE search instead

    // Add WHERE clause
    if (whereConditions.length > 0) {
      query += ` WHERE ${whereConditions.join(' AND ')}`;
    }

    // Add ORDER BY
    query += ` ORDER BY f.modified_time DESC`;

    // Execute query
    const files = await db.all(query, params);

    // Parse parents for each file
    files.forEach(file => {
      if (file.parents) {
        try {
          file.parents = JSON.parse(file.parents);
        } catch (e) {
          file.parents = [];
        }
      }
    });

    // Parse fields to export
    const fieldList = fields.split(',').map(f => f.trim()).filter(f => f);
    const validFields = [
      'id', 'name', 'mime_type', 'size', 'md5', 'parents',
      'modified_time', 'is_shortcut', 'shortcut_target_id', 'trashed',
      'account_key', 'owned_by_me', 'owner_email', 'created_at', 'updated_at'
    ];

    const exportFields = fieldList.filter(field => validFields.includes(field));
    if (exportFields.length === 0) {
      exportFields.push('name', 'mime_type', 'size', 'modified_time', 'account_key');
    }

    // Export based on format
    let exportData;
    let contentType;
    let fileName;

    switch (format.toLowerCase()) {
      case 'json':
        exportData = JSON.stringify(files, null, 2);
        contentType = 'application/json';
        fileName = 'search_results.json';
        break;
      
      case 'excel':
        // For Excel, we'll return JSON and let frontend handle conversion
        exportData = JSON.stringify(files, null, 2);
        contentType = 'application/json';
        fileName = 'search_results.json';
        break;
      
      case 'csv':
      default:
        // Generate CSV
        const csvHeaders = exportFields.join(',');
        const csvRows = files.map(file => {
          return exportFields.map(field => {
            const value = file[field];
            if (value === null || value === undefined) {
              return '';
            }
            // Escape quotes and wrap in quotes if contains comma or quote
            const strValue = String(value);
            if (strValue.includes(',') || strValue.includes('"') || strValue.includes('\n')) {
              return `"${strValue.replace(/"/g, '""')}"`;
            }
            return strValue;
          }).join(',');
        });
        
        exportData = [csvHeaders, ...csvRows].join('\n');
        contentType = 'text/csv';
        fileName = 'search_results.csv';
        break;
    }

    // Set response headers
    res.setHeader('Content-Type', contentType);
    res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`);
    res.setHeader('Content-Length', Buffer.byteLength(exportData, 'utf8'));

    res.send(exportData);

  } catch (error) {
    console.error('Error exporting search results:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to export search results'
    });
  }
});

module.exports = router;
