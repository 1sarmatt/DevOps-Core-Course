# Stage 1: Build Stage
FROM golang:1.24-alpine AS builder

# Install git (required for some Go modules)
RUN apk add --no-cache git

# Set the working directory
WORKDIR /app

# Copy go mod file
COPY go.mod ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-w -s" -o devops-info-service main.go

# Stage 2: Runtime Stage
FROM alpine:latest

# Install ca-certificates for HTTPS requests
RUN apk --no-cache add ca-certificates

# Create non-root user
RUN addgroup -g 1001 -S appuser && \
    adduser -u 1001 -S appuser -G appuser

# Set the working directory
WORKDIR /app

# Copy the binary from builder stage
COPY --from=builder /app/devops-info-service .

# Change ownership to non-root user
RUN chown appuser:appuser devops-info-service

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Run the binary
CMD ["./devops-info-service"]
