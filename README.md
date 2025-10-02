# IAC Agent Engine

A microservices-based Infrastructure as Code (IaC) automation platform that provides API-driven Terraform and Ansible execution with enterprise-grade state management, security, and observability.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [Service Documentation](#service-documentation)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Development](#development)
- [Deployment](#deployment)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Overview

The IAC Agent Engine is a production-ready platform that orchestrates infrastructure automation through three core microservices:

1. **Terraform Agent** - Executes Terraform configurations across multiple cloud providers
2. **Ansible Agent** - Runs Ansible playbooks for configuration management
3. **IAC Agent Manager** - Orchestrates agents, manages state, and provides unified API

### Key Benefits

- **Multi-Cloud Support**: Azure, AWS, and GCP integration
- **State Management**: Distributed state storage with versioning and locking
- **High Availability**: Resilient architecture with health checks and auto-recovery
- **Security First**: Built-in authentication, encryption, and audit logging
- **Observability**: Comprehensive metrics, logging, and monitoring
- **API-Driven**: RESTful APIs for seamless integration with CI/CD pipelines

## Architecture

### System Architecture

```

                     IAC Agent Engine                         

                                                               
       
    Terraform Agent     Ansible Agent        Redis     
     Port: 8080          Port: 8081        Port: 6379  
       
                                                           
                                      
                                                            
                       
             IAC Agent Manager       MinIO      
               Port: 8003                    Port: 9000   
                       
                                                               

```

### Network Architecture

- **Network**: Custom bridge network `n8n_network` (172.20.0.0/16)
- **Service IPs**:
  - Redis: 172.20.0.10
  - MinIO: 172.20.0.11
  - Terraform Agent: 172.20.0.20
  - Ansible Agent: 172.20.0.21
  - IAC Agent Manager: 172.20.0.30

### Data Flow

1. **Execution Request**  IAC Agent Manager receives API request
2. **State Retrieval**  Manager fetches state from MinIO/Redis
3. **Agent Dispatch**  Work distributed to Terraform/Ansible agents
4. **Execution**  Agents execute IaC operations
5. **State Update**  Results stored in MinIO with versioning
6. **Response**  Manager returns execution results and state

## Features

### Terraform Agent

- Multi-cloud provider support (Azure, AWS, GCP)
- Terraform plan, apply, destroy operations
- Workspace management
- State file handling
- Variable injection
- Output parsing
- Execution history

### Ansible Agent

- Playbook execution
- Dynamic inventory management
- Multi-host orchestration
- Concurrent playbook execution (configurable limit)
- Timeout management
- Cloud provider integration
- Execution logs and artifacts

### IAC Agent Manager

- Unified orchestration layer
- Terraform state management with S3-compatible backend (MinIO)
- State versioning and rollback capabilities
- Distributed locking mechanism
- Backup and recovery
- Authentication and authorization
- Rate limiting and request validation
- Metrics and health monitoring
- Audit logging

## Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 1.29+
- 8GB RAM minimum
- 20GB disk space

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd iac_agent_engine
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials and settings
   nano .env
   ```

3. **Start services**:
   ```bash
   docker-compose up -d
   ```

4. **Verify deployment**:
   ```bash
   docker-compose ps
   docker-compose logs
   ```

5. **Check service health**:
   ```bash
   curl http://localhost:8080/health  # Terraform Agent
   curl http://localhost:8081/health  # Ansible Agent
   curl http://localhost:8003/health  # IAC Agent Manager
   ```

### First Steps

1. **Access MinIO Console**: http://localhost:9001
   - Login with credentials from `.env`
   - Verify buckets are created

2. **Test Terraform Agent**:
   ```bash
   curl -X POST http://localhost:8080/execute \
     -H "Content-Type: application/json" \
     -d '{"action": "version"}'
   ```

3. **Test Ansible Agent**:
   ```bash
   curl http://localhost:8081/health
   ```

4. **Test IAC Manager**:
   ```bash
   curl http://localhost:8003/health
   ```

## Service Documentation

### Terraform Agent

**Purpose**: Execute Terraform operations via REST API

**Key Endpoints**:
- `POST /execute` - Execute Terraform commands
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /workspaces` - List workspaces
- `POST /workspace` - Create workspace

**Environment Variables**:
```
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8080
LOG_LEVEL=info
REDIS_HOST=redis
REDIS_DB=0
ARM_CLIENT_ID=<azure-sp-id>
AWS_ACCESS_KEY_ID=<aws-key>
GOOGLE_CREDENTIALS=<gcp-json>
```

### Ansible Agent

**Purpose**: Execute Ansible playbooks via REST API

**Key Endpoints**:
- `POST /playbook/execute` - Run playbook
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /playbooks` - List available playbooks
- `POST /inventory` - Update dynamic inventory

**Environment Variables**:
```
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8081
MAX_CONCURRENT_PLAYBOOKS=10
PLAYBOOK_TIMEOUT=3600
INVENTORY_CACHE_TTL=300
```

### IAC Agent Manager

**Purpose**: Orchestrate agents and manage infrastructure state

**Key Endpoints**:
- `POST /terraform/state` - Manage Terraform state
- `GET /terraform/state/{name}` - Retrieve state
- `POST /terraform/lock` - Acquire state lock
- `DELETE /terraform/lock` - Release state lock
- `GET /backups` - List state backups
- `POST /backup/restore` - Restore from backup
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

**State Management Features**:
- Versioning with configurable retention
- Automatic backups with compression
- State validation and integrity checks
- Distributed locking (prevents concurrent modifications)
- Audit logging for compliance

## API Endpoints

### Terraform Agent API

#### Execute Terraform Command
```bash
POST /execute
Content-Type: application/json

{
  "action": "plan",
  "workspace": "production",
  "config": "<terraform-config>",
  "variables": {
    "region": "eastus",
    "environment": "prod"
  }
}
```

#### Get Workspace State
```bash
GET /workspaces/{workspace_name}
```

### Ansible Agent API

#### Execute Playbook
```bash
POST /playbook/execute
Content-Type: application/json

{
  "playbook": "deploy.yml",
  "inventory": "production",
  "extra_vars": {
    "deploy_version": "v1.2.3",
    "environment": "production"
  },
  "limit": "webservers",
  "tags": ["deploy", "config"]
}
```

#### Get Execution Status
```bash
GET /execution/{execution_id}
```

### IAC Agent Manager API

#### Store Terraform State
```bash
POST /terraform/state
Content-Type: application/json
X-API-Key: your-api-key

{
  "name": "production-network",
  "state": "<terraform-state-json>",
  "version": 5,
  "metadata": {
    "terraform_version": "1.5.0",
    "serial": 5
  }
}
```

#### Retrieve Terraform State
```bash
GET /terraform/state/{state_name}
X-API-Key: your-api-key
```

#### Lock State
```bash
POST /terraform/lock
Content-Type: application/json
X-API-Key: your-api-key

{
  "state_name": "production-network",
  "lock_info": {
    "operation": "apply",
    "who": "terraform-user",
    "id": "unique-lock-id"
  }
}
```

#### List State Versions
```bash
GET /terraform/state/{state_name}/versions
X-API-Key: your-api-key
```

#### Create Backup
```bash
POST /backup
Content-Type: application/json
X-API-Key: your-api-key

{
  "state_name": "production-network",
  "description": "Pre-major-update backup"
}
```

## Configuration

### Environment Variables

All configuration is done through environment variables in the `.env` file:

#### Redis Configuration
```env
REDIS_PORT=6379
REDIS_PASSWORD=secure_password
```

#### MinIO Configuration
```env
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=secure_secret_key
MINIO_BUCKET_PREFIX=terraform-state
```

#### Cloud Provider Credentials

**Azure**:
```env
ARM_CLIENT_ID=<service-principal-id>
ARM_CLIENT_SECRET=<service-principal-secret>
ARM_SUBSCRIPTION_ID=<subscription-id>
ARM_TENANT_ID=<tenant-id>
```

**AWS**:
```env
AWS_ACCESS_KEY_ID=<access-key>
AWS_SECRET_ACCESS_KEY=<secret-key>
AWS_REGION=us-east-1
```

**GCP**:
```env
GOOGLE_CREDENTIALS=<service-account-json>
GCP_PROJECT_ID=<project-id>
```

#### Security Configuration
```env
REQUIRE_AUTH=true
API_KEY_HEADER=X-API-Key
ALLOWED_ORIGINS=https://your-domain.com
```

#### Resource Limits
```env
MAX_REQUEST_SIZE=104857600
RATE_LIMIT=1000
MAX_STATE_SIZE=524288000
LOCK_TIMEOUT=1800
```

### Volume Mounts

- `terraform_workspace` - Terraform working directory
- `ansible_workspace` - Ansible working directory
- `iac_manager_data` - State manager data
- `iac_manager_workspace` - Manager working directory
- `shared_data` - Shared storage across services
- `redis_data` - Redis persistence
- `minio_data` - MinIO object storage

## Development

### Local Development Setup

1. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Run services in development mode**:
   ```bash
   docker-compose up
   ```

3. **View logs**:
   ```bash
   docker-compose logs -f terraform-agent
   docker-compose logs -f ansible-agent
   docker-compose logs -f iac-agent-manager
   ```

4. **Access service shells**:
   ```bash
   docker-compose exec terraform-agent sh
   docker-compose exec ansible-agent sh
   docker-compose exec iac-agent-manager sh
   ```

### Building Images

Build all service images:
```bash
docker-compose build
```

Build specific service:
```bash
docker-compose build terraform-agent
```

### Testing

Run health checks:
```bash
./scripts/health-check.sh
```

Test Terraform execution:
```bash
./scripts/test-terraform.sh
```

Test Ansible execution:
```bash
./scripts/test-ansible.sh
```

## Deployment

### Production Deployment

1. **Update production environment**:
   ```bash
   cp .env.example .env.production
   # Configure production values
   nano .env.production
   ```

2. **Deploy with production settings**:
   ```bash
   docker-compose --env-file .env.production up -d
   ```

3. **Enable SSL/TLS** (recommended):
   - Use reverse proxy (nginx, traefik, etc.)
   - Configure SSL certificates
   - Update ALLOWED_ORIGINS

### Kubernetes Deployment

Kubernetes manifests are available in the parent n8n-iac-agentic-automation repository:

```bash
kubectl apply -f apps/base/terraform-agent.yaml
kubectl apply -f apps/base/ansible-agent.yaml
kubectl apply -f apps/base/iac-agent-manager.yaml
```

### High Availability

For HA deployment:
1. Scale services horizontally
2. Use external Redis cluster
3. Configure MinIO in distributed mode
4. Implement load balancer
5. Enable service mesh (optional)

## Security

### Authentication

IAC Agent Manager supports API key authentication:

1. **Enable authentication**:
   ```env
   REQUIRE_AUTH=true
   API_KEY_HEADER=X-API-Key
   ```

2. **Use API keys in requests**:
   ```bash
   curl -H "X-API-Key: your-secret-key" \
     http://localhost:8003/terraform/state/mystate
   ```

### Network Security

- Services isolated in custom Docker network
- Fixed IP addresses for service discovery
- No external exposure of Redis/MinIO by default
- Health checks validate service integrity

### Secrets Management

Supports HashiCorp Vault integration:

```env
VAULT_ADDR=http://vault:8200
VAULT_TOKEN=your-vault-token
VAULT_TRANSIT_PATH=transit
VAULT_KEY_NAME=terraform-state
```

### Audit Logging

All state operations are logged:
- State creation/updates
- Lock acquisition/release
- Backup operations
- Authentication attempts

Logs format: Structured JSON for SIEM integration

## Troubleshooting

### Common Issues

**Services not starting**:
```bash
# Check Docker logs
docker-compose logs

# Verify network
docker network ls | grep n8n_network

# Check volumes
docker volume ls
```

**Redis connection errors**:
```bash
# Test Redis connection
docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping

# Check Redis logs
docker-compose logs redis
```

**MinIO not accessible**:
```bash
# Check MinIO status
docker-compose ps minio

# Access MinIO logs
docker-compose logs minio

# Verify bucket creation
docker-compose exec minio mc ls local/
```

**Terraform execution failures**:
```bash
# Check Terraform agent logs
docker-compose logs terraform-agent

# Verify cloud credentials
docker-compose exec terraform-agent env | grep ARM_
docker-compose exec terraform-agent env | grep AWS_
```

**State lock issues**:
```bash
# List active locks
curl http://localhost:8003/terraform/locks

# Force release lock (use with caution)
curl -X DELETE http://localhost:8003/terraform/lock/mystate?force=true
```

### Debug Mode

Enable debug logging:
```env
TERRAFORM_DEBUG=true
ANSIBLE_DEBUG=true
IAC_MANAGER_DEBUG=true
TERRAFORM_LOG_LEVEL=debug
ANSIBLE_LOG_LEVEL=DEBUG
IAC_MANAGER_LOG_LEVEL=DEBUG
```

### Performance Tuning

Adjust resource limits in docker-compose.yml:
```yaml
resources:
  limits:
    memory: 4Gi    # Increase for large state files
    cpu: 2000m     # Increase for concurrent operations
```

## Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Standards

- Follow PEP 8 for Python code
- Include docstrings for all functions
- Add unit tests for new features
- Update documentation

### Testing Requirements

- All tests must pass
- Code coverage > 80%
- Linting errors must be resolved
- Security scan must pass

## License

This project is part of the n8n-iac-agentic-automation platform.

## Support

For issues and questions:
- Open GitHub issue
- Check documentation wiki
- Review troubleshooting guide

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.
