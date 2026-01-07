# Migration Guide for Existing Prometheus Users

This guide helps you migrate from older versions of Prometheus to the latest version with all improvements.

## Table of Contents
1. [What's New](#whats-new)
2. [Breaking Changes](#breaking-changes)
3. [Migration Steps](#migration-steps)
4. [Database Migration](#database-migration)
5. [Configuration Updates](#configuration-updates)
6. [Feature Upgrades](#feature-upgrades)
7. [Rollback Procedure](#rollback-procedure)

## What's New

### Version 2.1.0 Improvements

**Documentation & Clarity**
- ✅ Added OpenAPI/Swagger documentation at `/api/docs`
- ✅ Comprehensive environment variable validation
- ✅ Service-level documentation with dependency graphs
- ✅ Complete deployment guide

**Error Handling & Robustness**
- ✅ Consistent error handling across all services
- ✅ Fixed undefined references in `translation_cache.py`
- ✅ Retry logic for external services (Ollama, Redis, SMTP)
- ✅ ChromaDB initialization with fallback strategies

**Testing**
- ✅ Complete test suite (validators, utils, integration)
- ✅ Test configuration and fixtures
- ✅ Coverage reporting setup

**Security**
- ✅ CSRF protection middleware
- ✅ Enhanced security headers
- ✅ Strong password validation
- ✅ Improved SECRET_KEY validation
- ✅ Request sanitization

**Performance**
- ✅ Pagination support for all list endpoints
- ✅ Batch processing utilities
- ✅ Translation cache optimization (batch writes)
- ✅ Query optimization helpers
- ✅ Performance monitoring decorators

**Database**
- ✅ Migration management system
- ✅ Soft delete support
- ✅ Foreign key constraint enforcement
- ✅ Database backup utilities

**Code Quality**
- ✅ Removed magic numbers
- ✅ Consistent naming conventions
- ✅ Modular retry utilities
- ✅ Performance optimization utilities

## Breaking Changes

### 1. Environment Variables

**New Required Variables:**
```bash
# Previously optional, now recommended
REDIS_TTL=3600
ANALYTICS_RETENTION_DAYS=90
MAX_RESULTS_LIMIT=100
CHROMA_BATCH_SIZE=10
```

**Renamed Variables:**
None - all existing variables are backward compatible.

**Deprecated Variables:**
None yet, but check warnings in config validation.

### 2. API Changes

**New Headers for Protected Endpoints:**
```bash
# CSRF token now required for state-changing operations
X-CSRF-Token: <token>
```

**Pagination Parameters:**
```json
{
  "page": 1,
  "page_size": 20
}
```

**Response Format Changes:**
Paginated endpoints now return:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

### 3. Database Schema

**New Tables:**
- `schema_migrations` - Tracks database migrations

**New Columns:**
- `users.deleted_at` - Soft delete support
- `chat_history.deleted_at` - Soft delete support
- `feedback.deleted_at` - Soft delete support

**New Indexes:**
- `idx_analytics_event` - Analytics performance
- `idx_analytics_timestamp` - Time-based queries

## Migration Steps

### Step 1: Backup Everything

```bash
# Backup database
sqlite3 prometheus.db ".backup 'prometheus_backup_$(date +%Y%m%d).db'"

# Backup ChromaDB
tar -czf chroma_backup_$(date +%Y%m%d).tar.gz chroma_db/

# Backup configuration
cp .env .env.backup
cp config.py config.py.backup
```

### Step 2: Update Code

```bash
# Stash any local changes
git stash

# Pull latest changes
git pull origin main

# Restore local changes if needed
git stash pop
```

### Step 3: Update Dependencies

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Update pip
pip install --upgrade pip

# Install new dependencies
pip install -r requirements.txt

# Install test dependencies (optional)
pip install -r requirements-test.txt
```

### Step 4: Update Configuration

```bash
# Copy new environment template
cp .env.example .env.new

# Merge your existing config
# Edit .env.new to include your values from .env.backup
nano .env.new

# Validate new configuration
python config_validator.py

# If valid, replace old config
mv .env.new .env
```

### Step 5: Run Database Migrations

```bash
# Check current schema version
python migrations.py status

# Run pending migrations
python migrations.py migrate

# Verify migration success
python migrations.py status
```

### Step 6: Test the Application

```bash
# Run tests
pytest

# Start application in test mode
DEBUG=true python main.py

# Check health endpoint
curl http://localhost:8000/health
```

### Step 7: Deploy to Production

```bash
# Stop existing service
sudo systemctl stop prometheus-backend

# Run migrations in production
python migrations.py migrate

# Start service
sudo systemctl start prometheus-backend

# Monitor logs
sudo journalctl -u prometheus-backend -f
```

## Database Migration

### Automatic Migration

The new migration system handles schema updates automatically:

```bash
# View migration status
python migrations.py status

# Apply all pending migrations
python migrations.py migrate

# Rollback to specific version (if needed)
python migrations.py rollback 2
```

### Manual Migration (Advanced)

If you need to manually update the database:

```sql
-- Add soft delete columns
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP;
ALTER TABLE chat_history ADD COLUMN deleted_at TIMESTAMP;
ALTER TABLE feedback ADD COLUMN deleted_at TIMESTAMP;

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_analytics_event ON analytics(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp);

-- Update schema version
INSERT INTO schema_migrations (version, name) VALUES (4, 'add_soft_delete');
```

## Configuration Updates

### Update Environment Variables

Add these new variables to your `.env`:

```bash
# Performance tuning
MAX_RESULTS_LIMIT=100
CHROMA_BATCH_SIZE=10
OLLAMA_TIMEOUT=120

# Redis configuration
REDIS_TTL=3600
REDIS_PASSWORD=

# Analytics
ANALYTICS_RETENTION_DAYS=90

# Translation
TRANSLATION_CACHE_ENABLED=true
TRANSLATION_CACHE_FILE=translation_cache.json

# Query features
QUERY_EXPANSION_ENABLED=true
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2

# Email (if using)
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=noreply@prometheus.ai
```

### Validate Configuration

```bash
# Run comprehensive validation
python config_validator.py

# Should output:
# ✅ All configuration validations passed
```

## Feature Upgrades

### 1. Enable CSRF Protection

Update your frontend to include CSRF tokens:

```javascript
// Get CSRF token on login
const loginResponse = await fetch('/login', {
  method: 'POST',
  body: JSON.stringify({ username, password })
});
const { session_id, csrf_token } = await loginResponse.json();

// Include in subsequent requests
await fetch('/rag', {
  method: 'POST',
  headers: {
    'X-Session-Id': session_id,
    'X-CSRF-Token': csrf_token
  },
  body: JSON.stringify({ query })
});
```

### 2. Enable Retry Logic

External service calls now automatically retry on failure:

```python
# Ollama calls
from utils.retry import retry_with_backoff, RetryConfigs

@retry_with_backoff(
    exceptions=(ConnectionError, TimeoutError),
    config=RetryConfigs.STANDARD
)
def call_ollama(prompt):
    return ollama.generate(prompt)
```

### 3. Use Pagination

Update list endpoints to use pagination:

```python
# Old way
history = get_chat_history(user_id)

# New way
from utils.performance import PaginationParams

pagination = PaginationParams(page=1, page_size=20)
result = get_chat_history_paginated(user_id, pagination)
# result.items, result.total, result.total_pages
```

### 4. Enable Performance Monitoring

Track performance metrics:

```python
from utils.performance import measure_performance, perf_monitor

@measure_performance("rag_query")
def process_rag_query(query):
    # ... processing logic
    pass

# View stats
stats = perf_monitor.get_stats("rag_query")
print(f"Average: {stats['avg']:.2f}s")
```

## Rollback Procedure

If you encounter issues, you can rollback:

### 1. Rollback Database

```bash
# Stop service
sudo systemctl stop prometheus-backend

# Restore backup
cp prometheus_backup_YYYYMMDD.db prometheus.db

# Restore ChromaDB
rm -rf chroma_db
tar -xzf chroma_backup_YYYYMMDD.tar.gz

# Restart service
sudo systemctl start prometheus-backend
```

### 2. Rollback Code

```bash
# Checkout previous version
git log --oneline
git checkout <previous-commit-hash>

# Reinstall dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart prometheus-backend
```

### 3. Rollback Configuration

```bash
# Restore old config
cp .env.backup .env

# Restart service
sudo systemctl restart prometheus-backend
```

## Post-Migration Checklist

- [ ] All services start successfully
- [ ] Health check returns 200: `curl http://localhost:8000/health`
- [ ] API documentation accessible: http://localhost:8000/api/docs
- [ ] Login/signup works
- [ ] RAG queries return results
- [ ] Chat history saves and retrieves
- [ ] Feedback submission works
- [ ] Analytics data populates
- [ ] No errors in logs
- [ ] Performance metrics are reasonable
- [ ] Backups are configured
- [ ] Monitoring is active

## Troubleshooting

### Issue: Migration fails

```bash
# Check current version
python migrations.py status

# Try migrating one version at a time
python migrations.py migrate 1
python migrations.py migrate 2
# etc.

# If all else fails, restore backup and contact support
```

### Issue: Configuration validation errors

```bash
# Run detailed validation
python config_validator.py

# Fix reported errors in .env
# Re-run until all errors cleared
```

### Issue: Import errors

```bash
# Reinstall all dependencies
pip install --force-reinstall -r requirements.txt

# Check Python version
python --version  # Should be 3.9+
```

### Issue: Performance degradation

```bash
# Check if Redis is running
redis-cli ping

# Verify ChromaDB isn't corrupted
python -c "import chromadb; client = chromadb.PersistentClient(path='chroma_db'); print('OK')"

# Check database size
ls -lh prometheus.db
```

## Getting Help

If you encounter issues during migration:

1. Check logs: `tail -f /var/log/prometheus/backend.log`
2. Review documentation: `DOCUMENTATION.md`
3. Open GitHub issue with:
   - Current version
   - Target version
   - Error messages
   - Steps to reproduce

## Next Steps

After successful migration:

1. Review new API documentation at `/api/docs`
2. Set up automated tests: `pytest`
3. Configure monitoring and alerts
4. Update deployment scripts
5. Train team on new features
6. Consider enabling Redis caching for better performance
7. Review security settings and update SECRET_KEY

---

**Migration completed successfully?** ✅

Remember to update your monitoring dashboards and documentation to reflect the new features!
