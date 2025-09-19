const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

class Database {
  constructor() {
    this.dbPath = process.env.DB_PATH || path.join(__dirname, '../../data/drive_manager.db');
    this.ensureDataDirectory();
    this.db = new sqlite3.Database(this.dbPath);
    // Initialize database asynchronously
    this.init().catch(err => {
      console.error('Database initialization failed:', err);
      process.exit(1);
    });
  }

  ensureDataDirectory() {
    const dataDir = path.dirname(this.dbPath);
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }
  }

  async init() {
    return new Promise((resolve, reject) => {
      this.db.serialize(() => {
        // Create drive_accounts table
        this.db.run(`
          CREATE TABLE IF NOT EXISTS drive_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(255),
            sa_alias VARCHAR(255),
            account_key VARCHAR(255) UNIQUE NOT NULL,
            auth_type VARCHAR(20) NOT NULL CHECK (auth_type IN ('oauth', 'sa_share')),
            refresh_token_enc TEXT,
            roots TEXT,
            start_page_token TEXT,
            connected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_sync_at DATETIME,
            status VARCHAR(20) DEFAULT 'idle' CHECK (status IN ('idle', 'crawling', 'syncing', 'error')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
          )
        `);

        // Create drive_files table
        this.db.run(`
          CREATE TABLE IF NOT EXISTS drive_files (
            id VARCHAR(255) PRIMARY KEY,
            account_key VARCHAR(255) NOT NULL,
            name VARCHAR(500) NOT NULL,
            mime_type VARCHAR(100),
            size BIGINT,
            md5 VARCHAR(32),
            parents TEXT,
            modified_time DATETIME,
            is_shortcut BOOLEAN DEFAULT 0,
            shortcut_target_id VARCHAR(255),
            trashed BOOLEAN DEFAULT 0,
            owned_by_me BOOLEAN DEFAULT 0,
            owner_email VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_key) REFERENCES drive_accounts(account_key) ON DELETE CASCADE
          )
        `);

        // Backfill/migrate: add columns if table existed without them
        this.db.all(`PRAGMA table_info(drive_files)`, [], (err, rows) => {
          if (err) {
            console.error('PRAGMA table_info error:', err);
            reject(err);
            return;
          }
          
          const columnNames = rows.map(r => r.name);
          let migrationCount = 0;
          let totalMigrations = 0;
          
          // Check which migrations are needed
          if (!columnNames.includes('owned_by_me')) {
            totalMigrations++;
          }
          if (!columnNames.includes('owner_email')) {
            totalMigrations++;
          }
          
          if (totalMigrations === 0) {
            // No migrations needed, continue with indexes and triggers
            this.createIndexesAndTriggers(resolve);
            return;
          }
          
          // Execute migrations
          if (!columnNames.includes('owned_by_me')) {
            this.db.run(`ALTER TABLE drive_files ADD COLUMN owned_by_me BOOLEAN DEFAULT 0`, [], (e) => {
              if (e) {
                console.warn('ALTER TABLE add owned_by_me failed:', e.message);
              }
              migrationCount++;
              if (migrationCount === totalMigrations) {
                this.createIndexesAndTriggers(resolve);
              }
            });
          }
          
          if (!columnNames.includes('owner_email')) {
            this.db.run(`ALTER TABLE drive_files ADD COLUMN owner_email VARCHAR(255)`, [], (e) => {
              if (e) {
                console.warn('ALTER TABLE add owner_email failed:', e.message);
              }
              migrationCount++;
              if (migrationCount === totalMigrations) {
                this.createIndexesAndTriggers(resolve);
              }
            });
          }
        });
      });
    });
  }

  createIndexesAndTriggers(resolve) {
    // Create indexes
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_files_account_key ON drive_files(account_key)`);
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_files_mime_type ON drive_files(mime_type)`);
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_files_modified_time ON drive_files(modified_time)`);
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_files_md5_size ON drive_files(md5, size)`);
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_files_trashed ON drive_files(trashed)`);
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_files_owned_by_me ON drive_files(owned_by_me)`);
    
    // Additional performance indexes
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_files_name ON drive_files(name)`);
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_files_size ON drive_files(size)`);
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_files_created_at ON drive_files(created_at)`);
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_files_updated_at ON drive_files(updated_at)`);
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_files_parents ON drive_files(parents)`);
    
    // Composite indexes for common queries
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_files_account_trashed ON drive_files(account_key, trashed)`);
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_files_account_mime ON drive_files(account_key, mime_type)`);
    this.db.run(`CREATE INDEX IF NOT EXISTS idx_files_account_modified ON drive_files(account_key, modified_time)`);

    // FTS5 virtual table - DISABLED due to SQLite compilation issues
    // this.db.run(`
    //   CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(
    //     name, 
    //     content='drive_files', 
    //     content_rowid='rowid'
    //   )
    // `);

    // FTS5 triggers - DISABLED due to SQLite compilation issues
    // this.db.run(`
    //   CREATE TRIGGER IF NOT EXISTS files_ai AFTER INSERT ON drive_files BEGIN
    //     INSERT INTO files_fts(rowid, name) VALUES (new.rowid, new.name);
    //   END
    // `);

    // this.db.run(`
    //   CREATE TRIGGER IF NOT EXISTS files_ad AFTER DELETE ON drive_files BEGIN
    //     INSERT INTO files_fts(files_fts, rowid, name) VALUES('delete', old.rowid, old.name);
    //   END
    // `);

    // this.db.run(`
    //   CREATE TRIGGER IF NOT EXISTS files_au AFTER UPDATE ON drive_files BEGIN
    //     INSERT INTO files_fts(files_fts, rowid, name) VALUES('delete', old.rowid, old.name);
    //     INSERT INTO files_fts(rowid, name) VALUES (new.rowid, new.name);
    //   END
    // `);

    console.log('✅ Database initialized successfully');
    resolve();
  }

  // Helper method to run queries with promises
  run(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.run(sql, params, function(err) {
        if (err) reject(err);
        else resolve({ id: this.lastID, changes: this.changes });
      });
    });
  }

  get(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.get(sql, params, (err, row) => {
        if (err) reject(err);
        else resolve(row);
      });
    });
  }

  all(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.all(sql, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  }

  close() {
    return new Promise((resolve, reject) => {
      this.db.close((err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }
}

module.exports = new Database();
