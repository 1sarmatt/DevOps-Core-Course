# DevOps Info Service - Go Implementation

A high-performance Go implementation of the DevOps Info Service that provides detailed system and service information through RESTful endpoints.

## Overview

This Go version delivers the same functionality as the Python implementation but with significant performance advantages, smaller memory footprint, and faster startup times. It's designed for production environments where efficiency and reliability are critical.

## Prerequisites

- Go 1.21 or higher
- Git (for cloning)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd DevOps-Core-Course/app_go
   ```

2. Download dependencies:
   ```bash
   go mod tidy
   ```

## Building and Running

### Build the Application
```bash
# Build for current platform
go build -o devops-info-service main.go

# Build for different platforms
GOOS=linux GOARCH=amd64 go build -o devops-info-service-linux main.go
GOOS=windows GOARCH=amd64 go build -o devops-info-service.exe main.go
```

### Run the Application

#### Development Mode
```bash
go run main.go
```

#### Production Mode
```bash
./devops-info-service
```

#### Custom Configuration
```bash
# Custom port
PORT=9090 go run main.go

# Custom host and port
HOST=127.0.0.1 PORT=3000 go run main.go
```

## API Endpoints

### GET `/`
Returns comprehensive service and system information with the same JSON structure as the Python version.

**Example Response:**
```json
{
    "service": {
        "name": "devops-info-service",
        "version": "1.0.0",
        "description": "DevOps course info service",
        "framework": "Go"
    },
    "system": {
        "hostname": "MacBook-Pro",
        "platform": "darwin",
        "platform_version": "darwin arm64",
        "architecture": "arm64",
        "cpu_count": 10,
        "python_version": "N/A (Go application)"
    },
    "runtime": {
        "uptime_seconds": 123,
        "uptime_human": "2 minutes, 3 seconds",
        "current_time": "2026-01-26T13:35:00Z",
        "timezone": "UTC"
    },
    "request": {
        "client_ip": "127.0.0.1",
        "user_agent": "curl/8.7.1",
        "method": "GET",
        "path": "/"
    },
    "endpoints": [
        {"path": "/", "method": "GET", "description": "Service information"},
        {"path": "/health", "method": "GET", "description": "Health check"}
    ]
}
```

### GET `/health`
Simple health check endpoint for monitoring and load balancer probes.

**Example Response:**
```json
{
    "status": "healthy",
    "timestamp": "2026-01-26T13:35:00Z",
    "uptime_seconds": 123
}
```

### Pretty-Printed Output
Both endpoints support the `?pretty=true` parameter for formatted JSON output:

```bash
curl "http://localhost:8080/?pretty=true"
curl "http://localhost:8080/health?pretty=true"
```

## Configuration

The application can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Bind address for the web server |
| `PORT` | `8080` | Port number for the web server |

## Usage Examples

### Using curl
```bash
# Get service information
curl http://localhost:8080/

# Get health status
curl http://localhost:8080/health

# Pretty-printed output
curl "http://localhost:8080/?pretty=true"

# With custom port
PORT=9090 go run main.go
curl http://localhost:9090/
```

### Using HTTPie
```bash
# Get service information
http http://localhost:8080/

# Get health status
http http://localhost:8080/health
```

## Performance Comparison

### Binary Size
- **Go binary**: ~5-10 MB (single static binary)
- **Python application**: ~50+ MB (Python interpreter + dependencies)

### Memory Usage
- **Go**: ~2-5 MB baseline
- **Python**: ~20-50 MB baseline

### Startup Time
- **Go**: < 100ms
- **Python**: ~500ms-1s

### Performance
- **Go**: Higher throughput, lower latency
- **Python**: Adequate for moderate loads

## Development

### Code Structure
- `main.go` - Main application with all endpoints and logic
- `go.mod` - Go module definition
- `docs/` - Documentation and lab submissions

### Go Best Practices Applied
- Strong typing with custom structs
- Proper error handling
- Environment variable configuration
- Structured logging
- Clean code organization
- No external dependencies (standard library only)

### Building for Production

#### Static Binary (Recommended)
```bash
# Build fully static binary
CGO_ENABLED=0 go build -ldflags="-w -s" -o devops-info-service main.go
```

#### Docker Multi-Stage Build
```dockerfile
# Build stage
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-w -s" -o devops-info-service main.go

# Runtime stage
FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/devops-info-service .
CMD ["./devops-info-service"]
```

## Advantages of Go Implementation

1. **Performance**: Compiled to native code, significantly faster execution
2. **Memory Efficiency**: Lower memory footprint and better garbage collection
3. **Single Binary**: No runtime dependencies, easy deployment
4. **Concurrency**: Built-in support for concurrent operations
5. **Cross-Platform**: Easy compilation for different architectures
6. **Type Safety**: Compile-time error checking reduces runtime issues

## Future Enhancements

This Go implementation is ready for production deployment and can be enhanced with:
- Graceful shutdown handling
- Metrics collection with Prometheus
- Configuration file support
- TLS/HTTPS support
- Request timeouts and rate limiting
- Structured logging with levels

## License

This project is part of the DevOps Core Course curriculum.
