const express = require('express');
const router = express.Router();
const db = require('../models/database');
const googleDriveService = require('../services/googleDriveService');

// Get file metadata by ID
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    const file = await db.get(
      `SELECT 
         f.id, f.name, f.mime_type, f.size, f.md5, f.parents,
         f.modified_time, f.is_shortcut, f.shortcut_target_id, f.trashed,
         f.account_key, f.created_at, f.updated_at,
         a.email, a.sa_alias, a.auth_type
       FROM drive_files f
               LEFT JOIN drive_accounts a ON f.account_key = a.account_key
       WHERE f.id = ?`,
      [id]
    );

    if (!file) {
      return res.status(404).json({
        success: false,
        error: 'File not found'
      });
    }

    // Parse parents array
    if (file.parents) {
      try {
        file.parents = JSON.parse(file.parents);
      } catch (e) {
        file.parents = [];
      }
    }

    // Generate Drive links
    file.driveLink = `https://drive.google.com/file/d/${file.id}/view`;
    file.downloadLink = `https://drive.google.com/uc?id=${file.id}&export=download`;

    res.json({
      success: true,
      file: file
    });

  } catch (error) {
    console.error('Error getting file:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get file'
    });
  }
});

// Download file
router.get('/:id/download', async (req, res) => {
  try {
    const { id } = req.params;
    const { format } = req.query; // Get format parameter
    
    const file = await db.get(
      'SELECT f.*, a.auth_type, a.refresh_token_enc FROM drive_files f LEFT JOIN drive_accounts a ON f.account_key = a.account_key WHERE f.id = ?',
      [id]
    );

    if (!file) {
      return res.status(404).json({
        success: false,
        error: 'File not found'
      });
    }

    // Set up credentials
    const encryptedToken = JSON.parse(file.refresh_token_enc);
    const token = googleDriveService.decryptToken(encryptedToken);
    
    if (file.auth_type === 'oauth') {
      googleDriveService.setCredentials({ refresh_token: token });
    } else {
      googleDriveService.setCredentials({ private_key: token });
    }

    // Get download URL from Google Drive
    const drive = googleDriveService.getDriveAPI();
    
    let response;
    if (format && format !== 'original') {
      // Export with format conversion
      const exportMimeType = getExportMimeType(format, file.mime_type);
      response = await drive.files.export({
        fileId: id,
        mimeType: exportMimeType,
        supportsAllDrives: true
      }, {
        responseType: 'stream'
      });
    } else {
      // Download original file
      response = await drive.files.get({
        fileId: id,
        alt: 'media',
        supportsAllDrives: true
      }, {
        responseType: 'stream'
      });
    }

    // Set headers
    const contentType = format && format !== 'original' ? getExportMimeType(format, file.mime_type) : file.mime_type;
    const fileName = getFileNameWithExtension(file.name, format);
    
    res.setHeader('Content-Type', contentType);
    res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`);
    if (file.size) {
      res.setHeader('Content-Length', file.size);
    }

    // Pipe the stream
    response.data.pipe(res);

  } catch (error) {
    console.error('Error downloading file:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to download file'
    });
  }
});

// Get file preview
router.get('/:id/preview', async (req, res) => {
  try {
    const { id } = req.params;
    
    const file = await db.get(
      'SELECT name, mime_type, size FROM drive_files WHERE id = ?',
      [id]
    );

    if (!file) {
      return res.status(404).json({
        success: false,
        error: 'File not found'
      });
    }

    const previewInfo = {
      fileId: id,
      fileName: file.name,
      mimeType: file.mime_type,
      size: file.size,
      canPreview: canPreviewFile(file.mime_type),
      previewUrl: `https://drive.google.com/file/d/${id}/preview`,
      downloadUrl: `/files/${id}/download`
    };

    res.json({
      success: true,
      preview: previewInfo
    });

  } catch (error) {
    console.error('Error getting preview info:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get preview info'
    });
  }
});

// Bulk operations
router.post('/bulk/delete', async (req, res) => {
  try {
    const { fileIds = [] } = req.body;
    
    if (!Array.isArray(fileIds) || fileIds.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'File IDs array is required'
      });
    }

    if (fileIds.length > 100) {
      return res.status(400).json({
        success: false,
        error: 'Maximum 100 files allowed per request'
      });
    }

    // Delete from database
    const placeholders = fileIds.map(() => '?').join(',');
    const result = await db.run(
      `DELETE FROM drive_files WHERE id IN (${placeholders})`,
      fileIds
    );

    res.json({
      success: true,
      message: `${result.changes} files deleted from database`,
      deletedCount: result.changes
    });

  } catch (error) {
    console.error('Error bulk deleting files:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to delete files'
    });
  }
});

// Get file path (virtual path based on parents)
router.get('/:id/path', async (req, res) => {
  try {
    const { id } = req.params;
    
    const file = await db.get(
      'SELECT name, parents FROM drive_files WHERE id = ?',
      [id]
    );

    if (!file) {
      return res.status(404).json({
        success: false,
        error: 'File not found'
      });
    }

    // Build virtual path
    const path = await buildVirtualPath(id, file.parents);
    
    res.json({
      success: true,
      path: path
    });

  } catch (error) {
    console.error('Error getting file path:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get file path'
    });
  }
});

// Get file siblings (files in same folder)
router.get('/:id/siblings', async (req, res) => {
  try {
    const { id } = req.params;
    const { limit = 50 } = req.query;
    
    const file = await db.get(
      'SELECT parents, account_key FROM drive_files WHERE id = ?',
      [id]
    );

    if (!file) {
      return res.status(404).json({
        success: false,
        error: 'File not found'
      });
    }

    let siblings = [];
    
    if (file.parents) {
      const parents = JSON.parse(file.parents);
      if (parents.length > 0) {
        // Get files with same parent
        siblings = await db.all(
          `SELECT id, name, mime_type, size, modified_time, trashed
           FROM drive_files 
           WHERE account_key = ? AND parents LIKE ? AND id != ?
           ORDER BY name ASC
           LIMIT ?`,
          [file.account_key, `%${parents[0]}%`, id, parseInt(limit)]
        );
      }
    }

    res.json({
      success: true,
      siblings: siblings
    });

  } catch (error) {
    console.error('Error getting siblings:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get siblings'
    });
  }
});

// Get file versions (if any)
router.get('/:id/versions', async (req, res) => {
  try {
    const { id } = req.params;
    
    // For now, return empty array as Google Drive API v3 doesn't support versions
    // This could be implemented with Drive API v2 if needed
    res.json({
      success: true,
      versions: []
    });

  } catch (error) {
    console.error('Error getting versions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get versions'
    });
  }
});

// Get file sharing info
router.get('/:id/sharing', async (req, res) => {
  try {
    const { id } = req.params;
    
    const file = await db.get(
      'SELECT account_key, name FROM drive_files WHERE id = ?',
      [id]
    );

    if (!file) {
      return res.status(404).json({
        success: false,
        error: 'File not found'
      });
    }

    // Generate sharing links
    const sharingInfo = {
      fileId: id,
      fileName: file.name,
      owner: file.account_key,
      links: {
        view: `https://drive.google.com/file/d/${id}/view`,
        edit: `https://drive.google.com/file/d/${id}/edit`,
        download: `https://drive.google.com/uc?id=${id}&export=download`,
        embed: `https://drive.google.com/file/d/${id}/preview`
      }
    };

    res.json({
      success: true,
      sharing: sharingInfo
    });

  } catch (error) {
    console.error('Error getting sharing info:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get sharing info'
    });
  }
});

// Get file metadata in bulk
router.post('/bulk', async (req, res) => {
  try {
    const { fileIds = [] } = req.body;
    
    if (!Array.isArray(fileIds) || fileIds.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'File IDs array is required'
      });
    }

    if (fileIds.length > 100) {
      return res.status(400).json({
        success: false,
        error: 'Maximum 100 files allowed per request'
      });
    }

    const placeholders = fileIds.map(() => '?').join(',');
    const files = await db.all(
      `SELECT 
         id, name, mime_type, size, md5, parents,
         modified_time, is_shortcut, trashed,
         account_key, created_at, updated_at
       FROM drive_files 
       WHERE id IN (${placeholders})
       ORDER BY name ASC`,
      fileIds
    );

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

    res.json({
      success: true,
      files: files
    });

  } catch (error) {
    console.error('Error getting bulk files:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get bulk files'
    });
  }
});

// Upload file to Google Drive
router.post('/upload', async (req, res) => {
  try {
    const { accountKey, parentId, fileName, mimeType, fileSize } = req.body;
    
    if (!accountKey || !fileName) {
      return res.status(400).json({
        success: false,
        error: 'Account key and file name are required'
      });
    }

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

    // Set up credentials
    const encryptedToken = JSON.parse(account.refresh_token_enc);
    const token = googleDriveService.decryptToken(encryptedToken);
    
    if (account.auth_type === 'oauth') {
      googleDriveService.setCredentials({ refresh_token: token });
    } else {
      googleDriveService.setCredentials({ private_key: token });
    }

    // Generate upload URL
    const drive = googleDriveService.getDriveAPI();
    const uploadUrl = await generateUploadUrl(drive, {
      fileName,
      mimeType: mimeType || 'application/octet-stream',
      parentId: parentId || 'root',
      fileSize
    });

    res.json({
      success: true,
      uploadUrl: uploadUrl,
      fileId: uploadUrl.fileId,
      accountKey: accountKey
    });

  } catch (error) {
    console.error('Error generating upload URL:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to generate upload URL'
    });
  }
});

// Complete file upload
router.post('/upload/:fileId/complete', async (req, res) => {
  try {
    const { fileId } = req.params;
    const { accountKey } = req.body;
    
    if (!accountKey) {
      return res.status(400).json({
        success: false,
        error: 'Account key is required'
      });
    }

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

    // Set up credentials
    const encryptedToken = JSON.parse(account.refresh_token_enc);
    const token = googleDriveService.decryptToken(encryptedToken);
    
    if (account.auth_type === 'oauth') {
      googleDriveService.setCredentials({ refresh_token: token });
    } else {
      googleDriveService.setCredentials({ private_key: token });
    }

    // Get file metadata from Google Drive
    const drive = googleDriveService.getDriveAPI();
    const fileMetadata = await drive.files.get({
      fileId: fileId,
      fields: 'id,name,mimeType,size,md5Checksum,parents,modifiedTime,ownedByMe,owners',
      supportsAllDrives: true
    });

    // Insert file into database
    const fileData = fileMetadata.data;
    await db.run(
      `INSERT OR REPLACE INTO drive_files 
       (id, account_key, name, mime_type, size, md5, parents, modified_time, owned_by_me, owner_email, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)`,
      [
        fileData.id,
        accountKey,
        fileData.name,
        fileData.mimeType,
        fileData.size || 0,
        fileData.md5Checksum || null,
        fileData.parents ? JSON.stringify(fileData.parents) : null,
        fileData.modifiedTime,
        fileData.ownedByMe ? 1 : 0,
        fileData.owners ? fileData.owners[0].emailAddress : null
      ]
    );

    // Update FTS index - DISABLED due to FTS5 issues
    // await db.run(
    //   `INSERT OR REPLACE INTO files_fts (id, name) VALUES (?, ?)`,
    //   [fileData.id, fileData.name]
    // );

    res.json({
      success: true,
      message: 'File uploaded successfully',
      file: {
        id: fileData.id,
        name: fileData.name,
        mimeType: fileData.mimeType,
        size: fileData.size,
        accountKey: accountKey
      }
    });

  } catch (error) {
    console.error('Error completing upload:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to complete upload'
    });
  }
});

// Upload file with multipart form data
router.post('/upload/multipart', async (req, res) => {
  try {
    const { accountKey, parentId } = req.body;
    
    if (!accountKey) {
      return res.status(400).json({
        success: false,
        error: 'Account key is required'
      });
    }

    // Check if file was uploaded
    if (!req.files || !req.files.file) {
      return res.status(400).json({
        success: false,
        error: 'No file uploaded'
      });
    }

    const uploadedFile = req.files.file;
    
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

    // Set up credentials
    const encryptedToken = JSON.parse(account.refresh_token_enc);
    const token = googleDriveService.decryptToken(encryptedToken);
    
    if (account.auth_type === 'oauth') {
      googleDriveService.setCredentials({ refresh_token: token });
    } else {
      googleDriveService.setCredentials({ private_key: token });
    }

    // Upload file to Google Drive
    const drive = googleDriveService.getDriveAPI();
    const fileMetadata = {
      name: uploadedFile.name,
      parents: parentId ? [parentId] : undefined
    };

    const media = {
      mimeType: uploadedFile.mimetype || 'application/octet-stream',
      body: uploadedFile.data
    };

    const file = await drive.files.create({
      resource: fileMetadata,
      media: media,
      fields: 'id,name,mimeType,size,md5Checksum,parents,modifiedTime,ownedByMe,owners',
      supportsAllDrives: true
    });

    const fileData = file.data;

    // Insert file into database
    await db.run(
      `INSERT OR REPLACE INTO drive_files 
       (id, account_key, name, mime_type, size, md5, parents, modified_time, owned_by_me, owner_email, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)`,
      [
        fileData.id,
        accountKey,
        fileData.name,
        fileData.mimeType,
        fileData.size || 0,
        fileData.md5Checksum || null,
        fileData.parents ? JSON.stringify(fileData.parents) : null,
        fileData.modifiedTime,
        fileData.ownedByMe ? 1 : 0,
        fileData.owners ? fileData.owners[0].emailAddress : null
      ]
    );

    // Update FTS index - DISABLED due to FTS5 issues
    // await db.run(
    //   `INSERT OR REPLACE INTO files_fts (id, name) VALUES (?, ?)`,
    //   [fileData.id, fileData.name]
    // );

    res.json({
      success: true,
      message: 'File uploaded successfully',
      file: {
        id: fileData.id,
        name: fileData.name,
        mimeType: fileData.mimeType,
        size: fileData.size,
        accountKey: accountKey
      }
    });

  } catch (error) {
    console.error('Error uploading file:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to upload file'
    });
  }
});

// Helper function to build virtual path
async function buildVirtualPath(fileId, parentsJson) {
  if (!parentsJson) return '/';
  
  try {
    const parents = JSON.parse(parentsJson);
    if (parents.length === 0) return '/';
    
    const path = [];
    let currentId = parents[0];
    
    while (currentId) {
      const parent = await db.get(
        'SELECT name, parents FROM drive_files WHERE id = ?',
        [currentId]
      );
      
      if (!parent) break;
      
      path.unshift(parent.name);
      currentId = parent.parents ? JSON.parse(parent.parents)[0] : null;
    }
    
    return '/' + path.join('/');
  } catch (error) {
    console.error('Error building path:', error);
    return '/';
  }
}

// Helper function to check if file can be previewed
function canPreviewFile(mimeType) {
  const previewableTypes = [
    'application/pdf',
    'text/plain',
    'text/html',
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/bmp',
    'image/webp',
    'video/mp4',
    'video/webm',
    'video/ogg',
    'audio/mpeg',
    'audio/ogg',
    'audio/wav'
  ];
  
  return previewableTypes.includes(mimeType);
}

// Helper function to get export MIME type
function getExportMimeType(format, originalMimeType) {
  const exportMimeTypes = {
    'pdf': 'application/pdf',
    'csv': 'text/csv',
    'html': 'text/html',
    'txt': 'text/plain',
    'jpg': 'image/jpeg',
    'png': 'image/png',
    'webp': 'image/webp'
  };
  
  return exportMimeTypes[format] || originalMimeType;
}

// Helper function to get filename with correct extension
function getFileNameWithExtension(fileName, format) {
  if (!format || format === 'original') {
    return fileName;
  }
  
  const name = fileName.replace(/\.[^/.]+$/, ''); // Remove existing extension
  const extensions = {
    'pdf': '.pdf',
    'csv': '.csv',
    'html': '.html',
    'txt': '.txt',
    'jpg': '.jpg',
    'png': '.png',
    'webp': '.webp'
  };
  
  return name + (extensions[format] || '');
}

// Helper function to generate upload URL
async function generateUploadUrl(drive, options) {
  const { fileName, mimeType, parentId, fileSize } = options;
  
  const fileMetadata = {
    name: fileName,
    parents: parentId === 'root' ? undefined : [parentId]
  };

  const request = {
    resource: fileMetadata,
    media: {
      mimeType: mimeType,
      body: 'placeholder' // Will be replaced by actual file data
    },
    fields: 'id',
    supportsAllDrives: true
  };

  // For large files, use resumable upload
  if (fileSize && fileSize > 5 * 1024 * 1024) { // 5MB
    const response = await drive.files.create(request, {
      uploadType: 'resumable'
    });
    
    return {
      fileId: response.data.id,
      uploadUrl: response.headers.location,
      uploadType: 'resumable'
    };
  } else {
    // For small files, return direct upload info
    return {
      uploadType: 'multipart',
      fileMetadata: fileMetadata,
      mimeType: mimeType
    };
  }
}

module.exports = router;
