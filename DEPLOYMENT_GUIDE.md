# Production Deployment Guide for Prometheus

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Security Hardening](#security-hardening)
4. [Database Setup](#database-setup)
5. [Service Configuration](#service-configuration)
6. [Docker Deployment](#docker-deployment)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)
9. [Performance Tuning](#performance-tuning)
10. [Troubleshooting](#troubleshooting)

## Pre-Deployment Checklist

### Critical Items
- [ ] Generate secure `SECRET_KEY` (minimum 32 characters)
- [ ] Set `DEBUG=false` in production
- [ ] Configure production database paths
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Create backup strategy
- [ ] Review and update CORS origins
- [ ] Configure rate limiting
- [ ] Set up log rotation
- [ ] Review all environment variables
- [ ] Run security audit
- [ ] Perform load testing

### Recommended Items
- [ ] Set up Redis for caching
- [ ] Configure CDN for static assets
- [ ] Set up reverse proxy (Nginx/Apache)
- [ ] Configure process manager (systemd/supervisor)
- [ ] Set up CI/CD pipeline
- [ ] Create disaster recovery plan
- [ ] Document deployment procedures
- [ ] Set up error tracking (Sentry, etc.)

## Environment Setup

### 1. System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8GB
- Disk: 50GB SSD
- OS: Ubuntu 20.04+ / Debian 11+ / CentOS 8+

**Recommended:**
- CPU: 8+ cores
- RAM: 16GB+
- Disk: 100GB+ SSD
- OS: Ubuntu 22.04 LTS

### 2. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install python3.9 python3.9-venv python3-pip -y

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Install Redis (optional but recommended)
sudo apt install redis-server -y

# Install Nginx (reverse proxy)
sudo apt install nginx -y

# Install certbot (SSL certificates)
sudo apt install certbot python3-certbot-nginx -y
```

### 3. Create Application User

```bash
# Create dedicated user
sudo useradd -m -s /bin/bash prometheus
sudo usermod -aG sudo prometheus

# Switch to prometheus user
sudo su - prometheus
```

### 4. Clone and Setup Application

```bash
# Clone repository
git clone https://github.com/sai-chakrith/Prometheus.git
cd Prometheus/prometheus-ui/backend

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Security Hardening

### 1. Generate Secure Keys

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Save to .env
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

### 2. Configure Firewall

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow application port (if needed)
# sudo ufw allow 8000/tcp

# Deny all other incoming
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Check status
sudo ufw status
```

### 3. Set File Permissions

```bash
# Set ownership
sudo chown -R prometheus:prometheus /home/prometheus/Prometheus

# Protect sensitive files
chmod 600 .env
chmod 600 prometheus.db

# Protect configuration
chmod 644 config.py
```

### 4. Production Environment Variables

Create `.env` file:

```bash
# Security
SECRET_KEY=<your-secure-key-here>
DEBUG=false
SESSION_EXPIRY_DAYS=7

# Database
DATABASE_PATH=/var/lib/prometheus/prometheus.db
CHROMA_PATH=/var/lib/prometheus/chroma_db

# Server
HOST=127.0.0.1
PORT=8000

# CORS - Update with your domain
ALLOWED_ORIGINS=https://yourdomain.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
LOGIN_RATE_LIMIT=3/minute
API_RATE_LIMIT=50/minute

# Redis
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_TTL=3600

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Logging
LOG_LEVEL=INFO
```

## Database Setup

### 1. Create Database Directory

```bash
# Create data directory
sudo mkdir -p /var/lib/prometheus
sudo chown prometheus:prometheus /var/lib/prometheus
sudo chmod 755 /var/lib/prometheus
```

### 2. Run Migrations

```bash
cd /home/prometheus/Prometheus/prometheus-ui/backend
source venv/bin/activate

# Validate configuration
python config_validator.py

# Run migrations
python migrations.py migrate

# Verify
python migrations.py status
```

### 3. Initialize Dataset

```bash
# Load funding dataset
python -c "
import database as db
from config import Config
db.init_db()
print('Database initialized successfully')
"
```

## Service Configuration

### 1. Create Systemd Service

Create `/etc/systemd/system/prometheus-backend.service`:

```ini
[Unit]
Description=Prometheus RAG Backend
After=network.target redis.service

[Service]
Type=simple
User=prometheus
Group=prometheus
WorkingDirectory=/home/prometheus/Prometheus/prometheus-ui/backend
Environment="PATH=/home/prometheus/Prometheus/prometheus-ui/backend/venv/bin"
ExecStart=/home/prometheus/Prometheus/prometheus-ui/backend/venv/bin/python main.py
Restart=always
RestartSec=10

# Resource limits
LimitNOFILE=65535
MemoryLimit=4G

# Logging
StandardOutput=append:/var/log/prometheus/backend.log
StandardError=append:/var/log/prometheus/backend-error.log

[Install]
WantedBy=multi-user.target
```

### 2. Create Log Directory

```bash
sudo mkdir -p /var/log/prometheus
sudo chown prometheus:prometheus /var/log/prometheus
```

### 3. Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable prometheus-backend

# Start service
sudo systemctl start prometheus-backend

# Check status
sudo systemctl status prometheus-backend

# View logs
sudo journalctl -u prometheus-backend -f
```

### 4. Configure Nginx Reverse Proxy

Create `/etc/nginx/sites-available/prometheus`:

```nginx
upstream prometheus_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Logging
    access_log /var/log/nginx/prometheus-access.log;
    error_log /var/log/nginx/prometheus-error.log;
    
    # Client body size
    client_max_body_size 10M;
    
    # Proxy settings
    location / {
        proxy_pass http://prometheus_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # WebSocket support
    location /ws {
        proxy_pass http://prometheus_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # Static files (if any)
    location /static {
        alias /home/prometheus/Prometheus/prometheus-ui/backend/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:

```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/prometheus /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 5. Set up SSL Certificate

```bash
# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured by default
# Test renewal
sudo certbot renew --dry-run
```

## Docker Deployment

### 1. Build and Deploy with Docker Compose

Update `prometheus-ui/docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: prometheus-backend
    restart: unless-stopped
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
      - REDIS_ENABLED=true
      - REDIS_HOST=redis
    ports:
      - "8000:8000"
    volumes:
      - ./backend/prometheus.db:/app/prometheus.db
      - ./backend/chroma_db:/app/chroma_db
    depends_on:
      - redis
    networks:
      - prometheus-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    container_name: prometheus-frontend
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    networks:
      - prometheus-network

  redis:
    image: redis:7-alpine
    container_name: prometheus-redis
    restart: unless-stopped
    volumes:
      - redis-data:/data
    networks:
      - prometheus-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

networks:
  prometheus-network:
    driver: bridge

volumes:
  redis-data:
```

### 2. Deploy

```bash
# Set environment variables
echo "SECRET_KEY=$(openssl rand -hex 32)" > .env

# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

## Monitoring & Logging

### 1. Set up Log Rotation

Create `/etc/logrotate.d/prometheus`:

```
/var/log/prometheus/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 prometheus prometheus
    sharedscripts
    postrotate
        systemctl reload prometheus-backend > /dev/null 2>&1 || true
    endscript
}
```

### 2. Monitor System Resources

Install monitoring tools:

```bash
# Install htop for process monitoring
sudo apt install htop -y

# Install netdata for comprehensive monitoring
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
```

### 3. Application Monitoring

Check logs:

```bash
# Application logs
tail -f /var/log/prometheus/backend.log

# Error logs
tail -f /var/log/prometheus/backend-error.log

# Nginx logs
tail -f /var/log/nginx/prometheus-access.log
tail -f /var/log/nginx/prometheus-error.log
```

## Backup & Recovery

### 1. Automated Backup Script

Create `/home/prometheus/backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/var/backups/prometheus"
DATE=$(date +%Y%m%d_%H%M%S)
DB_PATH="/var/lib/prometheus/prometheus.db"
CHROMA_PATH="/var/lib/prometheus/chroma_db"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup SQLite database
sqlite3 $DB_PATH ".backup '$BACKUP_DIR/prometheus_$DATE.db'"

# Backup ChromaDB
tar -czf "$BACKUP_DIR/chroma_$DATE.tar.gz" -C /var/lib/prometheus chroma_db

# Backup configuration
cp /home/prometheus/Prometheus/prometheus-ui/backend/.env "$BACKUP_DIR/env_$DATE.txt"

# Remove backups older than 30 days
find $BACKUP_DIR -name "prometheus_*.db" -mtime +30 -delete
find $BACKUP_DIR -name "chroma_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

Make executable and add to cron:

```bash
chmod +x /home/prometheus/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/prometheus/backup.sh") | crontab -
```

### 2. Recovery Procedure

```bash
# Stop service
sudo systemctl stop prometheus-backend

# Restore database
cp /var/backups/prometheus/prometheus_YYYYMMDD_HHMMSS.db /var/lib/prometheus/prometheus.db

# Restore ChromaDB
tar -xzf /var/backups/prometheus/chroma_YYYYMMDD_HHMMSS.tar.gz -C /var/lib/prometheus

# Fix permissions
sudo chown -R prometheus:prometheus /var/lib/prometheus

# Start service
sudo systemctl start prometheus-backend
```

## Performance Tuning

### 1. Optimize Ollama

```bash
# Allocate more resources to Ollama
# Edit /etc/systemd/system/ollama.service or similar
Environment="OLLAMA_NUM_PARALLEL=4"
Environment="OLLAMA_MAX_LOADED_MODELS=2"
```

### 2. Optimize Redis

Edit `/etc/redis/redis.conf`:

```
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### 3. Optimize PostgreSQL (if used)

If migrating from SQLite to PostgreSQL:

```sql
-- Increase connection pool
max_connections = 100

-- Optimize memory
shared_buffers = 2GB
effective_cache_size = 6GB
```

## Troubleshooting

### Common Issues

**Issue: Service won't start**
```bash
# Check logs
sudo journalctl -u prometheus-backend -n 50

# Validate configuration
python config_validator.py

# Check permissions
ls -la /var/lib/prometheus
```

**Issue: High memory usage**
```bash
# Monitor memory
htop

# Reduce batch size in config
CHROMA_BATCH_SIZE=5

# Restart service
sudo systemctl restart prometheus-backend
```

**Issue: Slow queries**
```bash
# Check ChromaDB size
du -sh /var/lib/prometheus/chroma_db

# Enable Redis caching
REDIS_ENABLED=true

# Increase Redis TTL
REDIS_TTL=7200
```

**Issue: SSL certificate errors**
```bash
# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

## Support

For additional help:
- Check logs: `/var/log/prometheus/`
- Review documentation: `DOCUMENTATION.md`
- GitHub Issues: https://github.com/sai-chakrith/Prometheus/issues
