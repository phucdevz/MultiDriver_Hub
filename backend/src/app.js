const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const winston = require('winston');
const fileUpload = require('express-fileupload');
const os = require('os');
require('dotenv').config({ path: '.env' });

const app = express();
const PORT = process.env.PORT || 3000;

// Configure logging
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'multi-api-driver' },
  transports: [
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' })
  ]
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.combine(
      winston.format.colorize(),
      winston.format.simple()
    )
  }));
}

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.NODE_ENV === 'production' 
    ? ['https://yourdomain.com'] 
    : ['http://localhost:3000', 'http://127.0.0.1:3000'],
  credentials: true
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000, // 15 minutes
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
});

app.use(limiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// File upload middleware - only apply to multipart upload route
app.use('/files/upload/multipart', fileUpload({
  limits: { fileSize: 100 * 1024 * 1024 }, // 100MB limit
  abortOnLimit: true,
  createParentPath: true,
  useTempFiles: true,
  tempFileDir: os.tmpdir(), // Use system temp directory
  debug: process.env.NODE_ENV === 'development'
}));

// Request logging middleware
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.originalUrl}`, {
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    timestamp: new Date().toISOString()
  });
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    success: true,
    status: 'OK',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    environment: process.env.NODE_ENV,
    uptime: process.uptime()
  });
});

// Import background sync service
const backgroundSyncService = require('./services/backgroundSyncService');

// API Routes
app.use('/accounts', require('./controllers/accountsController')); 
app.use('/sync', require('./controllers/syncController').router);
app.use('/search', require('./controllers/searchController'));
app.use('/files', require('./controllers/filesController'));
app.use('/reports', require('./controllers/reportsController'));

// Background sync management endpoints
app.post('/background-sync/start', async (req, res) => {
  try {
    await backgroundSyncService.startBackgroundSync();
    res.json({
      success: true,
      message: 'Background sync started successfully'
    });
  } catch (error) {
    logger.error('Failed to start background sync:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start background sync'
    });
  }
});

app.post('/background-sync/stop', async (req, res) => {
  try {
    backgroundSyncService.stopBackgroundSync();
    res.json({
      success: true,
      message: 'Background sync stopped successfully'
    });
  } catch (error) {
    logger.error('Failed to stop background sync:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to stop background sync'
    });
  }
});

app.get('/background-sync/status', async (req, res) => {
  try {
    const status = await backgroundSyncService.getSyncStatus();
    res.json({
      success: true,
      status: status,
      isRunning: backgroundSyncService.isRunning
    });
  } catch (error) {
    logger.error('Failed to get background sync status:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get background sync status'
    });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error('Unhandled error:', {
    error: err.message,
    stack: err.stack,
    url: req.originalUrl,
    method: req.method,
    ip: req.ip
  });
  
  console.error(err.stack);
  res.status(500).json({
    error: 'Something went wrong!',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error',
    timestamp: new Date().toISOString()
  });
});

// 404 handler
app.use('*', (req, res) => {
  logger.warn('404 Not Found:', {
    url: req.originalUrl,
    method: req.method,
    ip: req.ip
  });
  
  res.status(404).json({
    error: 'Endpoint not found',
    path: req.originalUrl,
    timestamp: new Date().toISOString()
  });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  process.exit(0);
});

// Unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', {
    promise: promise,
    reason: reason
  });
});

// Uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', {
    error: error.message,
    stack: error.stack
  });
  process.exit(1);
});

// Start server
app.listen(PORT, async () => {
  logger.info(`🚀 Server running on port ${PORT}`, {
    port: PORT,
    environment: process.env.NODE_ENV,
    timestamp: new Date().toISOString()
  });
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🌍 Environment: ${process.env.NODE_ENV}`);
  
  // Auto-start background sync after server is ready
  try {
    await backgroundSyncService.startBackgroundSync();
    console.log(`🔄 Background sync started automatically`);
  } catch (error) {
    console.error(`❌ Failed to start background sync: ${error.message}`);
  }
});

module.exports = app;
