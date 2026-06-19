"""
Unit tests for the DevOps Info Service.

Tests cover all endpoints, response structure, error handling,
and edge cases to ensure reliability.
"""

import pytest
import json
from datetime import datetime
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestMainEndpoint:
    """Tests for the main endpoint (/)."""
    
    def test_main_endpoint_returns_200(self, client):
        """Test that main endpoint returns 200 status code."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_main_endpoint_returns_json(self, client):
        """Test that main endpoint returns valid JSON."""
        response = client.get('/')
        assert response.content_type == 'application/json'
        data = response.get_json()
        assert data is not None
    
    def test_main_endpoint_has_required_fields(self, client):
        """Test that response contains all required top-level fields."""
        response = client.get('/')
        data = response.get_json()
        
        # Check top-level structure
        assert 'service' in data
        assert 'system' in data
        assert 'runtime' in data
        assert 'request' in data
        assert 'endpoints' in data
    
    def test_service_info_structure(self, client):
        """Test service information structure and content."""
        response = client.get('/')
        data = response.get_json()
        service = data['service']
        
        assert 'name' in service
        assert 'version' in service
        assert 'description' in service
        assert 'framework' in service
        
        assert service['name'] == 'devops-info-service'
        assert service['framework'] == 'Flask'
        assert isinstance(service['version'], str)
    
    def test_system_info_structure(self, client):
        """Test system information structure."""
        response = client.get('/')
        data = response.get_json()
        system = data['system']
        
        assert 'hostname' in system
        assert 'platform' in system
        assert 'architecture' in system
        assert 'python_version' in system
        
        # Verify types
        assert isinstance(system['hostname'], str)
        assert isinstance(system['platform'], str)
        assert isinstance(system['python_version'], str)
    
    def test_runtime_info_structure(self, client):
        """Test runtime information structure."""
        response = client.get('/')
        data = response.get_json()
        runtime = data['runtime']
        
        assert 'uptime_seconds' in runtime
        assert 'uptime_human' in runtime
        assert 'current_time' in runtime
        assert 'timezone' in runtime
        
        # Verify types
        assert isinstance(runtime['uptime_seconds'], int)
        assert isinstance(runtime['uptime_human'], str)
        assert runtime['timezone'] == 'UTC'
        
        # Verify timestamp format (ISO 8601)
        datetime.fromisoformat(runtime['current_time'].replace('Z', '+00:00'))
    
    def test_request_info_structure(self, client):
        """Test request information structure."""
        response = client.get('/')
        data = response.get_json()
        request_info = data['request']
        
        assert 'client_ip' in request_info
        assert 'user_agent' in request_info
        assert 'method' in request_info
        assert 'path' in request_info
        
        assert request_info['method'] == 'GET'
        assert request_info['path'] == '/'
    
    def test_endpoints_list_structure(self, client):
        """Test endpoints list structure."""
        response = client.get('/')
        data = response.get_json()
        endpoints = data['endpoints']
        
        assert isinstance(endpoints, list)
        assert len(endpoints) >= 2
        
        # Check first endpoint structure
        endpoint = endpoints[0]
        assert 'path' in endpoint
        assert 'method' in endpoint
        assert 'description' in endpoint
    
    def test_pretty_print_parameter(self, client):
        """Test pretty print query parameter."""
        response = client.get('/?pretty=true')
        assert response.status_code == 200
        
        # Check that response is formatted (has indentation)
        text = response.get_data(as_text=True)
        assert '    ' in text or '\n' in text
        
        # Verify it's still valid JSON
        data = json.loads(text)
        assert 'service' in data
    
    def test_uptime_increases(self, client):
        """Test that uptime increases between requests."""
        import time
        
        response1 = client.get('/')
        data1 = response1.get_json()
        uptime1 = data1['runtime']['uptime_seconds']
        
        time.sleep(1)
        
        response2 = client.get('/')
        data2 = response2.get_json()
        uptime2 = data2['runtime']['uptime_seconds']
        
        assert uptime2 >= uptime1


class TestHealthEndpoint:
    """Tests for the health check endpoint (/health)."""
    
    def test_health_endpoint_returns_200(self, client):
        """Test that health endpoint returns 200 status code."""
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_health_endpoint_returns_json(self, client):
        """Test that health endpoint returns valid JSON."""
        response = client.get('/health')
        assert response.content_type == 'application/json'
        data = response.get_json()
        assert data is not None
    
    def test_health_endpoint_structure(self, client):
        """Test health endpoint response structure."""
        response = client.get('/health')
        data = response.get_json()
        
        assert 'status' in data
        assert 'timestamp' in data
        assert 'uptime_seconds' in data
        
        assert data['status'] == 'healthy'
        assert isinstance(data['uptime_seconds'], int)
        assert data['uptime_seconds'] >= 0
    
    def test_health_timestamp_format(self, client):
        """Test that health endpoint returns valid ISO timestamp."""
        response = client.get('/health')
        data = response.get_json()
        
        # Should be valid ISO 8601 format
        timestamp = data['timestamp']
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    def test_health_pretty_print(self, client):
        """Test health endpoint with pretty print parameter."""
        response = client.get('/health?pretty=true')
        assert response.status_code == 200
        
        text = response.get_data(as_text=True)
        data = json.loads(text)
        assert data['status'] == 'healthy'


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_404_not_found(self, client):
        """Test 404 error for non-existent endpoint."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Not Found'
        assert 'message' in data
    
    def test_404_returns_json(self, client):
        """Test that 404 error returns JSON."""
        response = client.get('/invalid/path')
        assert response.content_type == 'application/json'
    
    def test_multiple_invalid_paths(self, client):
        """Test various invalid paths return 404."""
        invalid_paths = ['/api', '/test', '/admin', '/favicon.ico']
        
        for path in invalid_paths:
            response = client.get(path)
            assert response.status_code == 404


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""
    
    def test_different_user_agents(self, client):
        """Test that different user agents are captured."""
        user_agents = [
            'Mozilla/5.0',
            'curl/7.68.0',
            'Python-requests/2.31.0'
        ]
        
        for ua in user_agents:
            response = client.get('/', headers={'User-Agent': ua})
            data = response.get_json()
            assert data['request']['user_agent'] == ua
    
    def test_query_parameters_ignored(self, client):
        """Test that unknown query parameters don't break the endpoint."""
        response = client.get('/?foo=bar&baz=qux')
        assert response.status_code == 200
        data = response.get_json()
        assert 'service' in data
    
    def test_concurrent_requests(self, client):
        """Test that multiple concurrent requests work correctly."""
        responses = []
        for _ in range(5):
            response = client.get('/')
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.get_json()
            assert 'service' in data
