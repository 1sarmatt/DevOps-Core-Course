# DevOps Info Service

A comprehensive web service that provides detailed information about itself and its runtime environment. This service serves as the foundation for monitoring and system introspection in DevOps workflows.

## Overview

The DevOps Info Service is a lightweight Flask application that exposes system information, service metadata, and health status through RESTful endpoints. It's designed to be containerizable and serve as a building block for larger DevOps tooling and monitoring solutions.

## Prerequisites

- Python 3.11 or higher
- pip package manager
- Git (for cloning)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd DevOps-Core-Course/app_python
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Default Configuration
```bash
python app.py
```
The service will start on `http://0.0.0.0:8000`

### Custom Configuration
```bash
# Custom port
PORT=8080 python app.py

# Custom host and port
HOST=127.0.0.1 PORT=3000 python app.py

# Enable debug mode
DEBUG=True python app.py
```

## API Endpoints

### GET `/`
Returns comprehensive service and system information including:
- Service metadata (name, version, description, framework)
- System information (hostname, platform, architecture, CPU count, Python version)
- Runtime information (uptime, current time, timezone)
- Request details (client IP, user agent, method, path)
- Available endpoints list

**Example Response:**
```json
{
  "service": {
    "name": "devops-info-service",
    "version": "1.0.0",
    "description": "DevOps course info service",
    "framework": "Flask"
  },
  "system": {
    "hostname": "my-laptop",
    "platform": "Linux",
    "platform_version": "Ubuntu 24.04",
    "architecture": "x86_64",
    "cpu_count": 8,
    "python_version": "3.13.1"
  },
  "runtime": {
    "uptime_seconds": 3600,
    "uptime_human": "1 hour, 0 minutes",
    "current_time": "2026-01-07T14:30:00.000Z",
    "timezone": "UTC"
  },
  "request": {
    "client_ip": "127.0.0.1",
    "user_agent": "curl/7.81.0",
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
  "timestamp": "2024-01-15T14:30:00.000Z",
  "uptime_seconds": 3600
}
```

## Configuration

The application can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Bind address for the web server |
| `PORT` | `5000` | Port number for the web server |
| `DEBUG` | `False` | Enable Flask debug mode |

## Usage Examples

### Using curl
```bash
# Get service information
curl http://localhost:5000/

# Get health status
curl http://localhost:5000/health

# Pretty-print JSON output
curl http://localhost:5000/ | jq
```

### Using HTTPie
```bash
# Get service information
http http://localhost:5000/

# Get health status
http http://localhost:5000/health
```

## Development

### Code Structure
- `app.py` - Main application file with all endpoints
- `requirements.txt` - Python dependencies
- `tests/` - Unit tests (to be implemented in Lab 3)
- `docs/` - Documentation and lab submissions

### Best Practices Implemented
- Clean code organization with clear function separation
- Comprehensive error handling for 404 and 500 errors
- Structured logging with appropriate levels
- Environment-based configuration
- PEP 8 compliant code style
- Type hints and docstrings

## Future Enhancements

This service is designed to evolve throughout the DevOps course:
- Containerization with Docker (Lab 2)
- Unit testing and CI/CD pipeline (Lab 3)
- Metrics endpoint for Prometheus (Lab 8)
- Kubernetes deployment with health probes (Lab 9)
- Persistence and visit tracking (Lab 12)
- Multi-environment deployment (Lab 13)

## License

This project is part of the DevOps Core Course curriculum.
