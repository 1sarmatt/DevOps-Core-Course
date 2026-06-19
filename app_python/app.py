
import os
import socket
import platform
import logging
import json
from datetime import datetime, timezone
from flask import Flask, jsonify, request, Response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Application start time
START_TIME = datetime.now(timezone.utc)

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
        logger.error(f"Error getting system info: {e}")
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

@app.route('/')
def index():
    """Main endpoint - service and system information."""
    logger.info(f"Request to main endpoint from {request.remote_addr}")
    
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
    return jsonify({
        'error': 'Not Found',
        'message': 'Endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    logger.info(f'Starting DevOps Info Service on {HOST}:{PORT}')
    logger.info(f'Debug mode: {DEBUG}')
    
    app.run(host=HOST, port=PORT, debug=DEBUG)
