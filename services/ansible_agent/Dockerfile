# Ansible Executor Service Dockerfile
# Production-ready Ansible automation service for configuration management

FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ANSIBLE_STDOUT_CALLBACK=json

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-client \
    sshpass \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create application user
RUN groupadd -r ansible && \
    useradd -r -g ansible -u 1000 -d /app -m ansible

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /workspace /app/logs && \
    chown -R ansible:ansible /app /workspace

# Copy application files
COPY --chown=ansible:ansible . .

# Switch to non-root user
USER ansible

# Expose application port
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

# Production command
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8081", "--workers", "1"]

# Metadata labels
LABEL maintainer="Configuration Management Team" \
      description="Production Ansible executor service" \
      version="1.0.0" \
      service="ansible-executor"
