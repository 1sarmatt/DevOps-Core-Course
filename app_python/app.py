import os
import socket
import platform
import logging
import json
import sys
from datetime import datetime, timezone
from flask import Flask, jsonify, request, Response

# JSON Formatter for structured logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'method'):
            log_data['method'] = record.method
        if hasattr(record, 'path'):
            log_data['path'] = record.path
        if hasattr(record, 'status_code'):
            log_data['status_code'] = record.status_code
        if hasattr(record, 'client_ip'):
            log_data['client_ip'] = record.client_ip
        if hasattr(record, 'user_agent'):
            log_data['user_agent'] = record.user_agent
            
        return json.dumps(log_data)

# Configure logging with JSON format
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Remove default handlers
logger.handlers = []

# Add JSON handler
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

app = Flask(__name__)

# Configuration
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Application start time
START_TIME = datetime.now(timezone.utc)

# Log application startup
logger.info('Application starting', extra={
    'host': HOST,
    'port': PORT,
    'debug': DEBUG,
    'python_version': platform.python_version(),
    'platform': platform.system()
})

def get_uptime():
    """Calculate application uptime."""
    delta = datetime.now(timezone.utc) - START_TIME
    seconds = int(delta.total_seconds())
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    
    if hours > 0:
        human_readable = f"{hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}"
    elif minutes > 0:
        human_readable = f"{minutes} minute{'s' if minutes != 1 else ''}, {remaining_seconds} second{'s' if remaining_seconds != 1 else ''}"
    else:
        human_readable = f"{remaining_seconds} second{'s' if remaining_seconds != 1 else ''}"
    
    return {
        'seconds': seconds,
        'human': human_readable
    }

def get_system_info():
    """Collect system information."""
    try:
        platform_info = platform.uname()
        return {
            'hostname': socket.gethostname(),
            'platform': platform_info.system,
            'platform_version': platform_info.version,
            'architecture': platform_info.machine,
            'cpu_count': os.cpu_count(),
            'python_version': platform.python_version()
        }
    except Exception as e:
        logger.error('Error getting system info', extra={'error': str(e)})
        return {
            'hostname': 'unknown',
            'platform': 'unknown',
            'platform_version': 'unknown',
            'architecture': 'unknown',
            'cpu_count': 0,
            'python_version': platform.python_version()
        }

def get_request_info():
    """Collect request information."""
    return {
        'client_ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'method': request.method,
        'path': request.path
    }

@app.before_request
def log_request():
    """Log incoming requests"""
    logger.info('Incoming request', extra={
        'method': request.method,
        'path': request.path,
        'client_ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    })

@app.after_request
def log_response(response):
    """Log outgoing responses"""
    logger.info('Outgoing response', extra={
        'method': request.method,
        'path': request.path,
        'status_code': response.status_code,
        'client_ip': request.remote_addr
    })
    return response

@app.route('/')
def index():
    """Main endpoint - service and system information."""
    uptime = get_uptime()
    system_info = get_system_info()
    request_info = get_request_info()
    
    response = {
        'service': {
            'name': 'devops-info-service',
            'version': '1.0.0',
            'description': 'DevOps course info service',
            'framework': 'Flask'
        },
        'system': system_info,
        'runtime': {
            'uptime_seconds': uptime['seconds'],
            'uptime_human': uptime['human'],
            'current_time': datetime.now(timezone.utc).isoformat(),
            'timezone': 'UTC'
        },
        'request': request_info,
        'endpoints': [
            {'path': '/', 'method': 'GET', 'description': 'Service information'},
            {'path': '/health', 'method': 'GET', 'description': 'Health check'}
        ]
    }
    
    # Check if pretty printing is requested
    pretty = request.args.get('pretty', 'false').lower() == 'true'
    if pretty:
        return Response(
            response=json.dumps(response, indent=4),
            status=200,
            mimetype='application/json'
        )
    else:
        return jsonify(response)

@app.route('/health')
def health():
    """Health check endpoint."""
    uptime = get_uptime()
    
    response = {
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'uptime_seconds': uptime['seconds']
    }
    
    # Check if pretty printing is requested
    pretty = request.args.get('pretty', 'false').lower() == 'true'
    if pretty:
        return Response(
            response=json.dumps(response, indent=4),
            status=200,
            mimetype='application/json'
        )
    else:
        return jsonify(response)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    logger.warning('Page not found', extra={
        'path': request.path,
        'client_ip': request.remote_addr
    })
    return jsonify({
        'error': 'Not Found',
        'message': 'Endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error('Internal server error', extra={
        'path': request.path,
        'error': str(error)
    })
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    logger.info('Starting DevOps Info Service', extra={
        'host': HOST,
        'port': PORT,
        'debug': DEBUG
    })
    app.run(host=HOST, port=PORT, debug=DEBUG)
