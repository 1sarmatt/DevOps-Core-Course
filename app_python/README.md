# DevOps Info Service

[![Python CI](https://github.com/1sarmatt/DevOps-Core-Course/workflows/Python%20CI%2FCD/badge.svg)](https://github.com/1sarmatt/DevOps-Core-Course/actions/workflows/python-ci.yml)
[![codecov](https://codecov.io/gh/1sarmatt/DevOps-Core-Course/branch/main/graph/badge.svg?flag=python)](https://codecov.io/gh/1sarmatt/DevOps-Core-Course?flag=python)

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

## Docker

This application can be run using Docker for containerized deployment.

### Building the Image

```bash
# Build the Docker image
docker build -t devops-info-service:latest .

# Build with custom tag
docker build -t yourusername/devops-info-service:v1.0.0 .
```

### Running the Container

```bash
# Run the container with default port mapping
docker run -d -p 5000:5000 --name devops-info devops-info-service:latest

# Run with custom port
docker run -d -p 8080:5000 --name devops-info devops-info-service:latest

# Run with environment variables
docker run -d -p 5000:5000 --name devops-info -e PORT=8080 -e DEBUG=True devops-info-service:latest
```

### Pulling from Docker Hub

```bash
# Pull the image
docker pull yourusername/devops-info-service:latest

# Run the pulled image
docker run -d -p 5000:5000 --name devops-info yourusername/devops-info-service:latest
```

### Container Features

- **Non-root user**: Runs as `appuser` for security
- **Minimal base image**: Uses `python:3.13-slim` for smaller size
- **Health checks**: Built-in health check endpoint
- **Optimized layers**: Efficient layer caching for faster rebuilds

### Container Testing

```bash
# Test the running container
curl http://localhost:5000/
curl http://localhost:5000/health

# Check container logs
docker logs devops-info

# Verify non-root user
docker exec devops-info whoami
```

## Development

### Running Tests

This project uses pytest for comprehensive unit testing.

#### Install Test Dependencies
```bash
pip install -r requirements-dev.txt
```

#### Run Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_app.py

# Run specific test class
pytest tests/test_app.py::TestMainEndpoint -v
```

#### Test Coverage
Current test coverage: **97%** (237 statements, 8 missed)

Tests cover:
- ✅ All endpoints (/, /health)
- ✅ Response structure and data types
- ✅ Error handling (404, 500)
- ✅ Edge cases (user agents, query params, concurrent requests)
- ✅ Time-based functionality (uptime tracking)

### Code Structure
- `app.py` - Main application file with all endpoints
- `requirements.txt` - Python dependencies
- `requirements-dev.txt` - Development dependencies (pytest, coverage, etc.)
- `tests/` - Unit tests with pytest
- `docs/` - Documentation and lab submissions
- `pytest.ini` - Pytest configuration
- `.dockerignore` - Files excluded from Docker builds

### Linting
```bash
# Install pylint
pip install pylint

# Run linter
pylint app.py
```

### Best Practices Implemented
- Clean code organization with clear function separation
- Comprehensive error handling for 404 and 500 errors
- Structured logging with appropriate levels
- Environment-based configuration
- PEP 8 compliant code style
- Type hints and docstrings
- **Comprehensive unit testing with pytest**
- **CI/CD pipeline with GitHub Actions**
- **Automated security scanning with Snyk**
- **Test coverage tracking with Codecov**

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment:

- ✅ **Automated Testing** - Runs pytest on every push/PR
- ✅ **Code Linting** - Pylint checks code quality
- ✅ **Security Scanning** - Snyk checks for vulnerabilities
- ✅ **Docker Build & Push** - Automated image publishing to Docker Hub
- ✅ **Coverage Tracking** - Codecov integration for coverage reports
- ✅ **Calendar Versioning** - Automatic CalVer tagging (YYYY.MM.DD)

See [docs/LAB03.md](docs/LAB03.md) for detailed CI/CD documentation.

## Future Enhancements

This service is designed to evolve throughout the DevOps course:
- ✅ Containerization with Docker (Lab 2) - **COMPLETED**
- ✅ Unit testing and CI/CD pipeline (Lab 3) - **COMPLETED**
- Metrics endpoint for Prometheus (Lab 8)
- Kubernetes deployment with health probes (Lab 9)
- Persistence and visit tracking (Lab 12)
- Multi-environment deployment (Lab 13)

