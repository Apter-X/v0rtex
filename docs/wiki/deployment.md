# v0rtex Deployment Guide

This guide covers deployment options for the v0rtex web scraping framework, from local development to production cloud deployments.

## 📚 Table of Contents

- [Local Development Setup](#local-development-setup)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## 🚀 Local Development Setup

### Prerequisites
- Python 3.8+
- Git
- pip or conda
- Chrome/Firefox browser
- Virtual environment tool

### Step-by-Step Setup

#### 1. Clone Repository
```bash
git clone https://github.com/your-org/v0rtex.git
cd v0rtex
```

#### 2. Create Virtual Environment
```bash
# Using venv (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
# Install base requirements
pip install -r requirements.txt

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

#### 4. Verify Installation
```bash
# Check if v0rtex is installed
python -c "import v0rtex; print('Installation successful!')"

# Run tests
pytest

# Check CLI
v0rtex --help
```

### Development Tools

#### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

#### Code Quality Tools
```bash
# Format code with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Lint with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

## 🏭 Production Deployment

### System Requirements

#### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **OS**: Ubuntu 20.04+, CentOS 8+, or Windows Server 2019+

#### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 100GB+ SSD
- **OS**: Ubuntu 22.04 LTS or CentOS Stream 9

### Installation Methods

#### 1. PyPI Installation (Recommended)
```bash
# Install from PyPI
pip install v0rtex

# Install with optional dependencies
pip install "v0rtex[vpn,proxy,dev]"
```

#### 2. Source Installation
```bash
# Clone and install from source
git clone https://github.com/your-org/v0rtex.git
cd v0rtex
pip install -e .
```

#### 3. System Package Installation
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip python3-venv
pip3 install v0rtex

# CentOS/RHEL
sudo yum install python3-pip
pip3 install v0rtex
```

### Production Configuration

#### Environment Variables
```bash
# Create environment file
cat > .env << EOF
V0RTEX_LOG_LEVEL=INFO
V0RTEX_CONFIG_PATH=/etc/v0rtex/config.json
V0RTEX_DATA_PATH=/var/lib/v0rtex/data
V0RTEX_LOG_PATH=/var/log/v0rtex
V0RTEX_SESSION_PATH=/var/lib/v0rtex/sessions
EOF

# Load environment variables
source .env
```

#### Systemd Service
```bash
# Create systemd service file
sudo tee /etc/systemd/system/v0rtex.service > /dev/null << EOF
[Unit]
Description=v0rtex Web Scraper
After=network.target

[Service]
Type=simple
User=v0rtex
Group=v0rtex
WorkingDirectory=/opt/v0rtex
Environment=PATH=/opt/v0rtex/venv/bin
ExecStart=/opt/v0rtex/venv/bin/v0rtex run -c /etc/v0rtex/config.json
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable v0rtex
sudo systemctl start v0rtex
```

#### User and Permissions
```bash
# Create v0rtex user
sudo useradd -r -s /bin/false v0rtex

# Create directories
sudo mkdir -p /opt/v0rtex /etc/v0rtex /var/lib/v0rtex /var/log/v0rtex

# Set permissions
sudo chown -R v0rtex:v0rtex /opt/v0rtex /etc/v0rtex /var/lib/v0rtex /var/log/v0rtex
sudo chmod 755 /opt/v0rtex /etc/v0rtex
sudo chmod 755 /var/lib/v0rtex /var/log/v0rtex
```

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV V0RTEX_CONFIG_PATH=/app/config/config.json

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY examples/ ./examples/

# Create necessary directories
RUN mkdir -p /app/config /app/data /app/logs /app/sessions

# Create non-root user
RUN useradd -m -u 1000 v0rtex && chown -R v0rtex:v0rtex /app
USER v0rtex

# Expose port (if needed)
EXPOSE 8000

# Default command
CMD ["python", "-m", "v0rtex", "run", "-c", "/app/config/config.json"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  v0rtex:
    build: .
    container_name: v0rtex-scraper
    volumes:
      - ./config:/app/config
      - ./data:/app/data
      - ./logs:/app/logs
      - ./sessions:/app/sessions
    environment:
      - V0RTEX_LOG_LEVEL=INFO
      - V0RTEX_CONFIG_PATH=/app/config/config.json
    restart: unless-stopped
    networks:
      - v0rtex-network

  # Optional: Redis for session storage
  redis:
    image: redis:7-alpine
    container_name: v0rtex-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - v0rtex-network

volumes:
  redis-data:

networks:
  v0rtex-network:
    driver: bridge
```

### Docker Commands
```bash
# Build image
docker build -t v0rtex:latest .

# Run container
docker run -d \
  --name v0rtex-scraper \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  v0rtex:latest

# Run with Docker Compose
docker-compose up -d

# View logs
docker logs v0rtex-scraper

# Execute commands in container
docker exec -it v0rtex-scraper bash
```

## ☁️ Cloud Deployment

### AWS Deployment

#### EC2 Instance Setup
```bash
# Launch EC2 instance (Ubuntu 22.04 LTS)
# Instance type: t3.medium or larger
# Storage: 50GB+ GP3 SSD

# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3-pip python3-venv git

# Clone repository
git clone https://github.com/your-org/v0rtex.git
cd v0rtex

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

#### AWS Lambda Deployment
```python
# lambda_function.py
import json
import v0rtex
from v0rtex.core.config import ScrapingConfig

def lambda_handler(event, context):
    try:
        # Load configuration from event
        config_data = event.get('config', {})
        config = ScrapingConfig.load_from_dict(config_data)
        
        # Create scraper and run
        scraper = v0rtex.V0rtexScraper(config)
        results = scraper.scrape()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'results': results,
                'count': len(results)
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }
```

#### ECS/Fargate Deployment
```yaml
# task-definition.json
{
  "family": "v0rtex-scraper",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "v0rtex",
      "image": "your-account.dkr.ecr.region.amazonaws.com/v0rtex:latest",
      "essential": true,
      "portMappings": [],
      "environment": [
        {"name": "V0RTEX_LOG_LEVEL", "value": "INFO"},
        {"name": "V0RTEX_CONFIG_PATH", "value": "/app/config/config.json"}
      ],
      "mountPoints": [
        {
          "sourceVolume": "config",
          "containerPath": "/app/config",
          "readOnly": true
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/v0rtex-scraper",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "volumes": [
    {
      "name": "config",
      "efsVolumeConfiguration": {
        "fileSystemId": "fs-12345678",
        "rootDirectory": "/"
      }
    }
  ]
}
```

### Azure Deployment

#### Azure Container Instances
```bash
# Deploy to Azure Container Instances
az container create \
  --resource-group your-rg \
  --name v0rtex-scraper \
  --image your-registry.azurecr.io/v0rtex:latest \
  --dns-name-label v0rtex-scraper \
  --ports 8000 \
  --environment-variables \
    V0RTEX_LOG_LEVEL=INFO \
    V0RTEX_CONFIG_PATH=/app/config/config.json
```

#### Azure Functions
```python
# function_app.py
import azure.functions as func
import v0rtex
from v0rtex.core.config import ScrapingConfig

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get configuration from request body
        config_data = req.get_json()
        config = ScrapingConfig.load_from_dict(config_data)
        
        # Run scraper
        scraper = v0rtex.V0rtexScraper(config)
        results = scraper.scrape()
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'results': results,
                'count': len(results)
            }),
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({
                'success': False,
                'error': str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
```

### Google Cloud Deployment

#### Cloud Run
```bash
# Deploy to Cloud Run
gcloud run deploy v0rtex-scraper \
  --image gcr.io/your-project/v0rtex:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars V0RTEX_LOG_LEVEL=INFO
```

#### Cloud Functions
```python
# main.py
import functions_framework
import v0rtex
from v0rtex.core.config import ScrapingConfig

@functions_framework.http
def scrape_website(request):
    try:
        # Get configuration from request
        config_data = request.get_json()
        config = ScrapingConfig.load_from_dict(config_data)
        
        # Run scraper
        scraper = v0rtex.V0rtexScraper(config)
        results = scraper.scrape()
        
        return {
            'success': True,
            'results': results,
            'count': len(results)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }, 500
```

## 📊 Monitoring and Maintenance

### Logging Configuration
```json
{
  "logging": {
    "level": "INFO",
    "file": "/var/log/v0rtex/v0rtex.log",
    "max_file_size": "100MB",
    "backup_count": 10,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "console_output": true,
    "file_output": true,
    "syslog": true
  }
}
```

### Health Checks
```python
# health_check.py
import requests
import time
from datetime import datetime

def health_check():
    try:
        # Check if scraper is responding
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print(f"[{datetime.now()}] Health check: OK")
            return True
        else:
            print(f"[{datetime.now()}] Health check: FAILED - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[{datetime.now()}] Health check: ERROR - {e}")
        return False

# Run health check every 5 minutes
while True:
    health_check()
    time.sleep(300)
```

### Monitoring with Prometheus
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
SCRAPING_REQUESTS = Counter('v0rtex_scraping_requests_total', 'Total scraping requests')
SCRAPING_DURATION = Histogram('v0rtex_scraping_duration_seconds', 'Scraping duration')
ACTIVE_SESSIONS = Gauge('v0rtex_active_sessions', 'Number of active sessions')
ERRORS_TOTAL = Counter('v0rtex_errors_total', 'Total errors', ['error_type'])

# Decorator for timing
def track_scraping_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            SCRAPING_REQUESTS.inc()
            return result
        except Exception as e:
            ERRORS_TOTAL.labels(error_type=type(e).__name__).inc()
            raise
        finally:
            duration = time.time() - start_time
            SCRAPING_DURATION.observe(duration)
```

### Backup and Recovery
```bash
#!/bin/bash
# backup.sh

# Backup configuration
tar -czf v0rtex-config-$(date +%Y%m%d).tar.gz /etc/v0rtex/

# Backup data
tar -czf v0rtex-data-$(date +%Y%m%d).tar.gz /var/lib/v0rtex/

# Backup logs
tar -czf v0rtex-logs-$(date +%Y%m%d).tar.gz /var/log/v0rtex/

# Upload to S3 (if using AWS)
aws s3 cp v0rtex-*-$(date +%Y%m%d).tar.gz s3://your-backup-bucket/

# Cleanup old backups (keep last 7 days)
find . -name "v0rtex-*.tar.gz" -mtime +7 -delete
```

## 🔒 Security Considerations

### Network Security
```bash
# Firewall configuration (UFW)
sudo ufw allow ssh
sudo ufw allow 8000/tcp  # If exposing API
sudo ufw enable

# Or with iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
sudo iptables -P INPUT DROP
```

### File Permissions
```bash
# Secure file permissions
sudo chown -R v0rtex:v0rtex /etc/v0rtex /var/lib/v0rtex /var/log/v0rtex
sudo chmod 750 /etc/v0rtex
sudo chmod 750 /var/lib/v0rtex
sudo chmod 750 /var/log/v0rtex

# Secure sensitive files
sudo chmod 600 /etc/v0rtex/secrets.json
sudo chmod 600 /etc/v0rtex/vpn-config.ovpn
```

### Environment Security
```bash
# Use environment variables for secrets
export V0RTEX_CAPTCHA_API_KEY="your-secret-key"
export V0RTEX_VPN_PASSWORD="your-vpn-password"

# Or use a secrets file
sudo tee /etc/v0rtex/secrets.env > /dev/null << EOF
V0RTEX_CAPTCHA_API_KEY=your-secret-key
V0RTEX_VPN_PASSWORD=your-vpn-password
EOF

# Source secrets
source /etc/v0rtex/secrets.env
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Browser Driver Issues
```bash
# Check Chrome installation
google-chrome --version

# Check ChromeDriver
chromedriver --version

# Install ChromeDriver
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
wget https://chromedriver.storage.googleapis.com/$(cat LATEST_RELEASE)/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

#### 2. Permission Issues
```bash
# Check file permissions
ls -la /etc/v0rtex/
ls -la /var/lib/v0rtex/
ls -la /var/log/v0rtex/

# Fix permissions
sudo chown -R v0rtex:v0rtex /etc/v0rtex /var/lib/v0rtex /var/log/v0rtex
sudo chmod 755 /etc/v0rtex /var/lib/v0rtex /var/log/v0rtex
```

#### 3. Memory Issues
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -10

# Increase swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Debug Mode
```bash
# Enable debug logging
export V0RTEX_LOG_LEVEL=DEBUG

# Run with verbose output
v0rtex run -c config.json -v

# Check logs
tail -f /var/log/v0rtex/v0rtex.log
```

### Performance Tuning
```bash
# Optimize Python performance
export PYTHONOPTIMIZE=1
export PYTHONHASHSEED=random

# Use PyPy for better performance (if compatible)
pypy3 -m pip install v0rtex
pypy3 -m v0rtex run -c config.json
```

## 📚 Related Documentation

- [Configuration Guide](configuration.md) - Configuration options
- [API Reference](api-reference.md) - API documentation
- [Architecture Documentation](../architecture.md) - System architecture
- [Contributing Guide](../contributing-guide.md) - Development guidelines
