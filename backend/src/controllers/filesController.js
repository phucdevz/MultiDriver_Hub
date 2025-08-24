const express = require('express');
const router = express.Router();
const db = require('../models/database');

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

// Get file preview info
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
      previewUrl: `https://drive.google.com/file/d/${id}/preview`
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

module.exports = router;
