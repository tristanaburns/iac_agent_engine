# Terraform Executor Service Dockerfile
# Production-ready Terraform automation service for multi-cloud deployments

FROM hashicorp/terraform:1.6 AS terraform-base

# Install additional dependencies
FROM alpine:3.18 AS dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    jq \
    bash \
    git \
    openssh-client \
    ca-certificates

# Production stage
FROM alpine:3.18 AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TF_IN_AUTOMATION=true \
    TF_CLI_ARGS="-no-color"

# Install runtime dependencies including build tools for Python packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    jq \
    bash \
    git \
    openssh-client \
    ca-certificates \
    tini \
    gcc \
    python3-dev \
    musl-dev \
    linux-headers

# Copy Terraform binary from official image
COPY --from=terraform-base /bin/terraform /usr/local/bin/terraform

# Create application user
RUN addgroup -g 1000 terraform && \
    adduser -D -u 1000 -G terraform terraform

# Set working directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /workspace /app/logs && \
    chown -R terraform:terraform /app /workspace

# Copy application files
COPY --chown=terraform:terraform requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY --chown=terraform:terraform . .

# Switch to non-root user
USER terraform

# Expose application port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Use tini for proper signal handling
ENTRYPOINT ["tini", "--"]

# Production command
CMD ["python3", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]

# Metadata labels
LABEL maintainer="IaC Team" \
      description="Production Terraform executor service" \
      version="1.0.0" \
      service="terraform-executor"