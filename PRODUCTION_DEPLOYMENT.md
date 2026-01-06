# 🚀 Production Deployment Guide - Prometheus RAG

## ✅ Critical Issues Fixed

### Security & Configuration
- ✅ Removed hardcoded `C:\Users\DHEERAJ\...` paths
- ✅ Created comprehensive `.env.example` with all variables documented
- ✅ Added `SECRET_KEY` validation in config.py
- ✅ Replaced all `print()` with proper `logger.*()` calls
- ✅ Removed `console.log/error` from frontend

### Docker & Infrastructure
- ✅ Added health checks to backend Dockerfile
- ✅ Added health checks to docker-compose.yml
- ✅ Added proper volume mounts for data persistence
- ✅ Removed development code mounts from production
- ✅ Added curl to backend image for health checks
- ✅ Configured service dependencies with health conditions

---

## 📋 Pre-Deployment Checklist

### 1. Environment Configuration

**Backend (`prometheus-ui/backend/.env`):**
```bash
# Generate a strong SECRET_KEY
openssl rand -hex 32

# Copy and configure
cp .env.example .env
nano .env
```

**Required Changes:**
- [ ] Set strong `SECRET_KEY` (use openssl command above)
- [ ] Set `DEBUG=false`
- [ ] Update `ALLOWED_ORIGINS` with production domain
- [ ] Update `OLLAMA_BASE_URL` if using external Ollama
- [ ] Configure `DATASET_PATH` to match your deployment
- [ ] Set `LOG_LEVEL=WARNING` or `ERROR` for production

### 2. Dataset Preparation

**Ensure dataset is accessible:**
```bash
# Place your dataset at:
/path/to/RAGAS/dataset/cleaned_funding_synthetic_2010_2025.csv

# Or update DATASET_PATH in .env to point to correct location
```

### 3. SSL/TLS Configuration

**Add reverse proxy (recommended: nginx or Caddy):**

**nginx example:**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. Ollama Setup

**Install Ollama:**
```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Pull required model
ollama pull llama3.1:8b
```

**For Docker deployment, add Ollama service to docker-compose.yml:**
```yaml
services:
  ollama:
    image: ollama/ollama:latest
    container_name: prometheus-ollama
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    restart: unless-stopped
    networks:
      - prometheus-network

volumes:
  ollama_data:
    driver: local
```

**Update backend .env:**
```bash
OLLAMA_BASE_URL=http://ollama:11434
```

---

## 🐳 Docker Deployment

### Option 1: Docker Compose (Recommended)

**1. Build and start services:**
```bash
cd prometheus-ui
docker-compose up -d --build
```

**2. Check health status:**
```bash
docker-compose ps
docker-compose logs backend
docker-compose logs frontend
```

**3. View logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

**4. Stop services:**
```bash
docker-compose down
```

**5. Full cleanup (removes volumes):**
```bash
docker-compose down -v
```

### Option 2: Manual Docker Build

**Backend:**
```bash
cd prometheus-ui/backend
docker build -t prometheus-backend:latest .
docker run -d \
  --name prometheus-backend \
  -p 8000:8000 \
  -v $(pwd)/../dataset:/app/dataset:ro \
  -v prometheus-chroma:/app/chroma_db \
  -v prometheus-db:/app/data \
  --env-file .env \
  prometheus-backend:latest
```

**Frontend:**
```bash
cd prometheus-ui/frontend
docker build -t prometheus-frontend:latest .
docker run -d \
  --name prometheus-frontend \
  -p 3000:80 \
  prometheus-frontend:latest
```

---

## 🔒 Security Best Practices

### 1. Secrets Management
- [ ] Never commit `.env` files to git
- [ ] Use environment variables or secrets management (AWS Secrets Manager, HashiCorp Vault)
- [ ] Rotate `SECRET_KEY` periodically
- [ ] Use strong passwords for any admin accounts

### 2. Network Security
- [ ] Use HTTPS only (no HTTP in production)
- [ ] Configure firewall rules (allow only 443, 80)
- [ ] Set up CORS properly with specific domains
- [ ] Enable rate limiting (already configured)

### 3. Database Security
- [ ] Regular backups of `prometheus.db`
- [ ] Backup ChromaDB volume regularly
- [ ] Keep backup retention policy (7-30 days)

### 4. Monitoring & Logging
- [ ] Set `LOG_LEVEL=WARNING` or `ERROR` in production
- [ ] Monitor `/health` endpoint
- [ ] Set up alerting for service failures
- [ ] Monitor disk space (ChromaDB and database can grow)

---

## 📊 Health Monitoring

### Health Check Endpoints

**Backend health:**
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": 1704556800.0,
  "version": "2.0.0",
  "checks": {
    "database": "healthy",
    "ollama": "healthy",
    "chromadb": "healthy (2500 documents)",
    "embedding_model": "loaded",
    "whisper_model": "loaded",
    "dataset": "loaded (2500 records)"
  }
}
```

### Docker Health Checks

**Check container health:**
```bash
docker ps
# Look for "healthy" status in HEALTH column
```

---

## 🔄 Backup & Recovery

### Database Backup

**Automated backup script:**
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/prometheus"
mkdir -p $BACKUP_DIR

# Backup SQLite database
cp /path/to/prometheus.db $BACKUP_DIR/prometheus_$DATE.db

# Backup ChromaDB
tar -czf $BACKUP_DIR/chroma_$DATE.tar.gz /path/to/chroma_db/

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

**Add to crontab:**
```bash
crontab -e
# Add: Daily backup at 2 AM
0 2 * * * /path/to/backup.sh
```

### Recovery

**Restore database:**
```bash
# Stop services
docker-compose down

# Restore database
cp /backups/prometheus/prometheus_20240106.db ./prometheus-ui/backend/prometheus.db

# Restore ChromaDB
tar -xzf /backups/prometheus/chroma_20240106.tar.gz -C ./prometheus-ui/backend/

# Restart services
docker-compose up -d
```

---

## 📈 Scaling Considerations

### Horizontal Scaling

**For high traffic, use load balancer:**
```yaml
# docker-compose.yml with multiple backend instances
services:
  backend1:
    # ... backend config
  backend2:
    # ... backend config
  
  nginx-lb:
    image: nginx:alpine
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "8000:80"
```

**nginx-lb.conf:**
```nginx
upstream backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
    }
}
```

### Vertical Scaling

**Increase Docker resource limits:**
```yaml
services:
  backend:
    # ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Health check failing**
```bash
# Check logs
docker logs prometheus-backend

# Check if service is listening
docker exec prometheus-backend curl http://localhost:8000/health

# Check network
docker network inspect prometheus-network
```

**2. ChromaDB not persisting**
```bash
# Verify volume
docker volume inspect prometheus-ui_chroma_db

# Check permissions
docker exec prometheus-backend ls -la /app/chroma_db
```

**3. Ollama connection failed**
```bash
# Test Ollama
curl http://localhost:11434/api/version

# Pull model if missing
ollama pull llama3.1:8b

# Check Ollama logs (if using Docker)
docker logs prometheus-ollama
```

**4. Frontend can't reach backend**
```bash
# Check CORS settings in backend .env
ALLOWED_ORIGINS=https://yourdomain.com

# Check nginx/proxy configuration
# Ensure /api routes to backend
```

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks

**Weekly:**
- [ ] Check disk space
- [ ] Review error logs
- [ ] Verify backups are running

**Monthly:**
- [ ] Update dependencies (security patches)
- [ ] Review and rotate logs
- [ ] Test backup restoration
- [ ] Review rate limiting metrics

**Quarterly:**
- [ ] Update Ollama models
- [ ] Review and optimize database
- [ ] Security audit
- [ ] Performance testing

---

## 🎯 Production Readiness Status

### ✅ READY FOR PRODUCTION

All critical issues have been addressed:
- Security hardening complete
- Docker health checks implemented
- Proper logging configured
- Environment configuration documented
- Data persistence configured
- Error handling improved

### Next Steps:
1. Configure production `.env` file
2. Set up SSL/TLS certificates
3. Configure backup automation
4. Set up monitoring/alerting
5. Deploy to production server
6. Run smoke tests
7. Monitor for 24 hours

**Estimated deployment time: 2-4 hours** (including setup and testing)

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Ollama Documentation](https://ollama.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [nginx Configuration](https://nginx.org/en/docs/)
- [Let's Encrypt SSL](https://letsencrypt.org/)

---

**Last Updated:** January 6, 2026
**Version:** 2.0.0 Production Ready
