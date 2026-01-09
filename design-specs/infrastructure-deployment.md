# AI Navigator Platform - Infrastructure & Deployment

> Version: 1.0.0
> Created: 2026-01-09
> Region: Hong Kong (Primary) + China CDN

---

## 1. Infrastructure Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         PRODUCTION INFRASTRUCTURE                                │
└─────────────────────────────────────────────────────────────────────────────────┘

                                    ┌──────────────────┐
                                    │   DNS Provider   │
                                    │  (Cloudflare)    │
                                    └────────┬─────────┘
                                             │
         ┌───────────────────────────────────┼───────────────────────────────────┐
         │                                   │                                   │
         ▼                                   ▼                                   ▼
┌─────────────────┐               ┌─────────────────┐               ┌─────────────────┐
│   Cloudflare    │               │    七牛云 CDN    │               │   又拍云 CDN    │
│   (Global)      │               │  (China Nodes)  │               │  (China Nodes)  │
│                 │               │                 │               │                 │
│ • WAF           │               │ • Static Assets │               │ • Images        │
│ • DDoS          │               │ • ISR Pages     │               │ • Screenshots   │
│ • SSL           │               │                 │               │                 │
└────────┬────────┘               └────────┬────────┘               └────────┬────────┘
         │                                 │                                 │
         └─────────────────────────────────┼─────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           ALIYUN HONG KONG REGION                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                        VPC (10.0.0.0/16)                                   │ │
│  │                                                                            │ │
│  │  ┌────────────────────────────┐  ┌────────────────────────────┐           │ │
│  │  │     Public Subnet          │  │     Private Subnet         │           │ │
│  │  │     (10.0.1.0/24)          │  │     (10.0.2.0/24)          │           │ │
│  │  │                            │  │                            │           │ │
│  │  │  ┌──────────────────────┐  │  │  ┌──────────────────────┐  │           │ │
│  │  │  │    Load Balancer     │  │  │  │   Application Nodes  │  │           │ │
│  │  │  │    (SLB/ALB)         │──┼──┼──│   (ECS x 2)          │  │           │ │
│  │  │  │                      │  │  │  │                      │  │           │ │
│  │  │  │  • SSL Termination   │  │  │  │  • Next.js App       │  │           │ │
│  │  │  │  • Health Checks     │  │  │  │  • FastAPI Services  │  │           │ │
│  │  │  │  • Auto Scaling      │  │  │  │  • Celery Workers    │  │           │ │
│  │  │  └──────────────────────┘  │  │  └──────────────────────┘  │           │ │
│  │  │                            │  │                            │           │ │
│  │  │  ┌──────────────────────┐  │  │  ┌──────────────────────┐  │           │ │
│  │  │  │    Bastion Host      │  │  │  │   Worker Nodes       │  │           │ │
│  │  │  │    (Jump Server)     │  │  │  │   (ECS x 1)          │  │           │ │
│  │  │  │                      │  │  │  │                      │  │           │ │
│  │  │  │  • SSH Access        │  │  │  │  • Celery Beat       │  │           │ │
│  │  │  │  • Audit Logging     │  │  │  │  • Crawlers          │  │           │ │
│  │  │  └──────────────────────┘  │  │  │  • Scheduled Tasks   │  │           │ │
│  │  │                            │  │  └──────────────────────┘  │           │ │
│  │  └────────────────────────────┘  └────────────────────────────┘           │ │
│  │                                                                            │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                      Managed Services                                │  │ │
│  │  │                                                                      │  │ │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │  │ │
│  │  │  │ RDS         │  │ Redis       │  │ OSS         │  │ Meilisearch │ │  │ │
│  │  │  │ PostgreSQL  │  │ Cluster     │  │ Bucket      │  │ (Self-host) │ │  │ │
│  │  │  │             │  │             │  │             │  │             │ │  │ │
│  │  │  │ • 4 vCPU    │  │ • 2GB       │  │ • Standard  │  │ • 2 vCPU    │ │  │ │
│  │  │  │ • 16GB RAM  │  │ • Cluster   │  │ • 100GB     │  │ • 4GB RAM   │ │  │ │
│  │  │  │ • 200GB SSD │  │ • Sentinel  │  │ • CDN       │  │ • 50GB SSD  │ │  │ │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │  │ │
│  │  │                                                                      │  │ │
│  │  └─────────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                            │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Cloud Resource Specification

### 2.1 Compute Resources

| Resource | Specification | Purpose | Monthly Cost (USD) |
|----------|--------------|---------|-------------------|
| **App Server 1** | ECS g6.xlarge (4 vCPU, 8GB) | Next.js + FastAPI | ~$80 |
| **App Server 2** | ECS g6.xlarge (4 vCPU, 8GB) | Next.js + FastAPI | ~$80 |
| **Worker Server** | ECS g6.large (2 vCPU, 4GB) | Celery + Crawlers | ~$40 |
| **Meilisearch** | ECS g6.large (2 vCPU, 4GB) | Search Engine | ~$40 |
| **Total Compute** | | | **~$240** |

### 2.2 Database Resources

| Resource | Specification | Purpose | Monthly Cost (USD) |
|----------|--------------|---------|-------------------|
| **PostgreSQL RDS** | 4 vCPU, 16GB RAM, 200GB SSD | Primary Database | ~$150 |
| **Redis Cluster** | 2GB Memory, 2 Replicas | Cache + Sessions | ~$50 |
| **Total Database** | | | **~$200** |

### 2.3 Storage & CDN

| Resource | Specification | Purpose | Monthly Cost (USD) |
|----------|--------------|---------|-------------------|
| **OSS Bucket** | 100GB Standard | Static Assets | ~$10 |
| **七牛云 CDN** | 500GB Traffic | China Acceleration | ~$50 |
| **Cloudflare Pro** | Unlimited | Global CDN + WAF | $20 |
| **Total Storage** | | | **~$80** |

### 2.4 Networking

| Resource | Specification | Purpose | Monthly Cost (USD) |
|----------|--------------|---------|-------------------|
| **SLB** | Standard Load Balancer | Traffic Distribution | ~$30 |
| **NAT Gateway** | Small | Outbound Internet | ~$35 |
| **Elastic IP** | 2x Static IP | Public Access | ~$10 |
| **VPN Gateway** | Basic (optional) | Secure Admin Access | ~$25 |
| **Total Networking** | | | **~$100** |

### 2.5 Total Monthly Estimate

| Category | Cost (USD) |
|----------|-----------|
| Compute | $240 |
| Database | $200 |
| Storage & CDN | $80 |
| Networking | $100 |
| **Total** | **~$620/month** |

---

## 3. Docker Architecture

### 3.1 Docker Compose (Development)

```yaml
# docker-compose.yml

version: '3.8'

services:
  # Next.js Web Application
  web:
    build:
      context: ./web
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgres://postgres:postgres@db:5432/ainav
      - REDIS_URL=redis://redis:6379
      - MEILISEARCH_URL=http://meilisearch:7700
      - MEILISEARCH_API_KEY=masterKey
    volumes:
      - ./web:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - db
      - redis
      - meilisearch

  # FastAPI Content Service
  content-api:
    build:
      context: ./services/content-service
      dockerfile: Dockerfile
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/ainav
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./services/content-service:/app
    depends_on:
      - db
      - redis

  # FastAPI Search Service
  search-api:
    build:
      context: ./services/search-service
      dockerfile: Dockerfile
    ports:
      - "8002:8000"
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/ainav
      - MEILISEARCH_URL=http://meilisearch:7700
      - MEILISEARCH_API_KEY=masterKey
    volumes:
      - ./services/search-service:/app
    depends_on:
      - db
      - meilisearch

  # Celery Worker
  celery-worker:
    build:
      context: ./services/automation-service
      dockerfile: Dockerfile
    command: celery -A app.celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/ainav
      - REDIS_URL=redis://redis:6379
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    volumes:
      - ./services/automation-service:/app
    depends_on:
      - db
      - redis

  # Celery Beat (Scheduler)
  celery-beat:
    build:
      context: ./services/automation-service
      dockerfile: Dockerfile
    command: celery -A app.celery beat --loglevel=info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    volumes:
      - ./services/automation-service:/app
    depends_on:
      - redis

  # PostgreSQL Database
  db:
    image: pgvector/pgvector:pg16
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=ainav
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Meilisearch
  meilisearch:
    image: getmeili/meilisearch:v1.6
    ports:
      - "7700:7700"
    environment:
      - MEILI_MASTER_KEY=masterKey
      - MEILI_ENV=development
    volumes:
      - meilisearch_data:/meili_data

  # MinIO (S3-compatible storage)
  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"

volumes:
  postgres_data:
  redis_data:
  meilisearch_data:
  minio_data:
```

### 3.2 Dockerfile (Next.js)

```dockerfile
# web/Dockerfile

# Stage 1: Dependencies
FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN corepack enable pnpm && pnpm install --frozen-lockfile

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production

RUN corepack enable pnpm && pnpm build

# Stage 3: Runner
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

### 3.3 Dockerfile (FastAPI)

```dockerfile
# services/content-service/Dockerfile

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 4. Kubernetes Deployment (Phase 2)

### 4.1 Deployment Manifests

```yaml
# k8s/web-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: ainav-web
  labels:
    app: ainav-web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ainav-web
  template:
    metadata:
      labels:
        app: ainav-web
    spec:
      containers:
        - name: web
          image: registry.cn-hongkong.aliyuncs.com/ainav/web:latest
          ports:
            - containerPort: 3000
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          envFrom:
            - configMapRef:
                name: ainav-config
            - secretRef:
                name: ainav-secrets
          livenessProbe:
            httpGet:
              path: /api/health
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /api/health
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ainav-web
spec:
  selector:
    app: ainav-web
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ainav-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
    - hosts:
        - ainav.cn
        - www.ainav.cn
      secretName: ainav-tls
  rules:
    - host: ainav.cn
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: ainav-web
                port:
                  number: 80
```

### 4.2 Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ainav-web-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ainav-web
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

---

## 5. CI/CD Pipeline

### 5.1 GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml

name: Deploy to Production

on:
  push:
    branches:
      - main

env:
  REGISTRY: registry.cn-hongkong.aliyuncs.com
  NAMESPACE: ainav

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Run tests
        run: pnpm test

      - name: Run linting
        run: pnpm lint

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Login to Aliyun Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.ALIYUN_REGISTRY_USERNAME }}
          password: ${{ secrets.ALIYUN_REGISTRY_PASSWORD }}

      - name: Build and push web image
        uses: docker/build-push-action@v5
        with:
          context: ./web
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.NAMESPACE }}/web:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ env.NAMESPACE }}/web:latest

      - name: Build and push API image
        uses: docker/build-push-action@v5
        with:
          context: ./services/content-service
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.NAMESPACE }}/content-api:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ env.NAMESPACE }}/content-api:latest

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd /opt/ainav
            docker compose pull
            docker compose up -d --remove-orphans
            docker image prune -f

      - name: Notify Slack
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Deployment completed!'
          fields: repo,commit,author
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
        if: always()
```

### 5.2 Deployment Script

```bash
#!/bin/bash
# deploy.sh - Production deployment script

set -e

echo "🚀 Starting deployment..."

# Pull latest images
docker compose pull

# Run database migrations
docker compose run --rm content-api alembic upgrade head

# Blue-green deployment
docker compose up -d --no-deps --scale web=2 web
sleep 30

# Health check
curl -f http://localhost:3000/api/health || exit 1

# Remove old containers
docker compose up -d --remove-orphans

# Cleanup
docker image prune -f

# Invalidate CDN cache
echo "Invalidating CDN cache..."
# Add CDN purge command here

echo "✅ Deployment completed!"
```

---

## 6. Monitoring & Observability

### 6.1 Prometheus + Grafana Stack

```yaml
# docker-compose.monitoring.yml

version: '3.8'

services:
  prometheus:
    image: prom/prometheus:v2.48.0
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=15d'

  grafana:
    image: grafana/grafana:10.2.0
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_INSTALL_PLUGINS=grafana-piechart-panel

  loki:
    image: grafana/loki:2.9.0
    ports:
      - "3100:3100"
    volumes:
      - loki_data:/loki
      - ./loki-config.yml:/etc/loki/local-config.yaml

  promtail:
    image: grafana/promtail:2.9.0
    volumes:
      - /var/log:/var/log:ro
      - ./promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml

  alertmanager:
    image: prom/alertmanager:v0.26.0
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml

volumes:
  prometheus_data:
  grafana_data:
  loki_data:
```

### 6.2 Prometheus Configuration

```yaml
# prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - 'alerts/*.yml'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'nextjs'
    static_configs:
      - targets: ['web:3000']
    metrics_path: '/api/metrics'

  - job_name: 'fastapi'
    static_configs:
      - targets: ['content-api:8000', 'search-api:8000']
    metrics_path: '/metrics'

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'meilisearch'
    static_configs:
      - targets: ['meilisearch:7700']
    metrics_path: '/metrics'
```

### 6.3 Alert Rules

```yaml
# alerts/critical.yml

groups:
  - name: critical_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: ServiceDown
        expr: up == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"

      - alert: DatabaseConnectionsHigh
        expr: pg_stat_activity_count > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL connections approaching limit"
```

---

## 7. Backup Strategy

### 7.1 Database Backup

```bash
#!/bin/bash
# backup-db.sh

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"
RETENTION_DAYS=30

# Create backup
pg_dump -h $POSTGRES_HOST -U $POSTGRES_USER -Fc $POSTGRES_DB > \
  $BACKUP_DIR/ainav_$TIMESTAMP.dump

# Upload to OSS
aliyun oss cp $BACKUP_DIR/ainav_$TIMESTAMP.dump \
  oss://ainav-backups/postgres/ainav_$TIMESTAMP.dump

# Cleanup old local backups
find $BACKUP_DIR -name "*.dump" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: ainav_$TIMESTAMP.dump"
```

### 7.2 Backup Schedule (Cron)

```cron
# /etc/cron.d/ainav-backups

# Database backup - daily at 3 AM HKT
0 3 * * * root /opt/ainav/scripts/backup-db.sh >> /var/log/backup.log 2>&1

# Redis backup - every 6 hours
0 */6 * * * root /opt/ainav/scripts/backup-redis.sh >> /var/log/backup.log 2>&1

# Meilisearch snapshot - daily at 4 AM HKT
0 4 * * * root /opt/ainav/scripts/backup-meilisearch.sh >> /var/log/backup.log 2>&1
```

---

## 8. Security Hardening

### 8.1 Network Security Groups

```hcl
# Terraform example - Security Groups

resource "alicloud_security_group_rule" "allow_http" {
  security_group_id = alicloud_security_group.app.id
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "80/80"
  cidr_ip           = "0.0.0.0/0"
  description       = "Allow HTTP"
}

resource "alicloud_security_group_rule" "allow_https" {
  security_group_id = alicloud_security_group.app.id
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "443/443"
  cidr_ip           = "0.0.0.0/0"
  description       = "Allow HTTPS"
}

resource "alicloud_security_group_rule" "allow_ssh_bastion" {
  security_group_id = alicloud_security_group.app.id
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "22/22"
  cidr_ip           = var.admin_ip_range
  description       = "Allow SSH from admin IPs only"
}

resource "alicloud_security_group_rule" "allow_internal" {
  security_group_id = alicloud_security_group.app.id
  type              = "ingress"
  ip_protocol       = "all"
  port_range        = "-1/-1"
  source_security_group_id = alicloud_security_group.app.id
  description       = "Allow all internal traffic"
}
```

### 8.2 SSL/TLS Configuration

```nginx
# nginx/ssl.conf

ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;

ssl_session_timeout 1d;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;

ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;

add_header Strict-Transport-Security "max-age=63072000" always;
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
```

---

## 9. Disaster Recovery

### 9.1 Recovery Point Objective (RPO)

| Data Type | RPO | Backup Frequency |
|-----------|-----|------------------|
| Database | 1 hour | Continuous WAL + Daily full |
| Redis | 6 hours | Every 6 hours |
| User uploads | 24 hours | Daily sync to OSS |
| Search index | 4 hours | Continuous sync |

### 9.2 Recovery Time Objective (RTO)

| Scenario | RTO | Recovery Steps |
|----------|-----|----------------|
| Single node failure | < 5 min | Auto-scaling replaces |
| Database failover | < 15 min | RDS automatic failover |
| Full region outage | < 4 hours | Restore from backup to new region |
| Data corruption | < 2 hours | Point-in-time recovery |

### 9.3 Recovery Playbook

```markdown
## DR Playbook: Database Corruption

### Symptoms
- Application errors indicating data inconsistency
- PostgreSQL reporting corruption warnings

### Steps
1. **Assess**: Identify affected tables and timeframe
2. **Isolate**: Take affected database read-only
3. **Restore**: Point-in-time recovery to pre-corruption state
   ```bash
   aliyun rds CreateTempDBInstance \
     --DBInstanceId <original-id> \
     --RestoreTime "2026-01-09T10:00:00Z"
   ```
4. **Validate**: Run data integrity checks
5. **Switch**: Update connection strings to restored instance
6. **Notify**: Update status page and notify users
```

---

## 10. Cost Optimization

### 10.1 Reserved Instances

| Resource | On-Demand | 1-Year Reserved | Savings |
|----------|-----------|-----------------|---------|
| ECS g6.xlarge x2 | $160/mo | $100/mo | 37% |
| RDS PostgreSQL | $150/mo | $90/mo | 40% |
| Redis | $50/mo | $35/mo | 30% |

### 10.2 Auto-Scaling Policies

```yaml
# Scale down during off-peak hours (China timezone)
schedule:
  - cron: "0 1 * * *"  # 1 AM CST
    minReplicas: 1
    maxReplicas: 3

  - cron: "0 8 * * *"  # 8 AM CST
    minReplicas: 2
    maxReplicas: 10
```

---

*This infrastructure design supports the AI Navigator platform from MVP through to enterprise scale, with clear upgrade paths and cost optimization strategies.*
