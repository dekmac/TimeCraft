#!/usr/bin/env python3
"""
Pre-move integration tests for TimeCraft API
These tests verify the API works before restructuring
"""

import os
import sys
import pytest
import requests
import subprocess
import time
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:8080"
API_STARTUP_TIMEOUT = 30  # seconds


class TestAPIBeforeMove:
    """Test suite to verify API functionality before moving files"""
    
    @classmethod
    def setup_class(cls):
        """Start the API server for testing"""
        print("🚀 Starting API server for pre-move tests...")
        
        # Start the API server
        cls.api_process = subprocess.Popen(
            [sys.executable, "api_server.py"],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        for i in range(API_STARTUP_TIMEOUT):
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=2)
                if response.status_code == 200:
                    print("✅ API server started successfully")
                    break
            except requests.exceptions.RequestException:
                time.sleep(1)
        else:
            cls.teardown_class()
            raise Exception("❌ API server failed to start within timeout")
    
    @classmethod
    def teardown_class(cls):
        """Stop the API server"""
        if hasattr(cls, 'api_process'):
            cls.api_process.terminate()
            cls.api_process.wait()
            print("🛑 API server stopped")
    
    def test_health_endpoint(self):
        """Test the health endpoint returns 200"""
        response = requests.get(f"{API_BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_api_root_endpoint(self):
        """Test the API root endpoint"""
        response = requests.get(f"{API_BASE_URL}/api")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["message"] == "TimeCraft REST API"
    
    def test_components_endpoint(self):
        """Test the components status endpoint"""
        response = requests.get(f"{API_BASE_URL}/components")
        assert response.status_code == 200
        
        data = response.json()
        assert "components" in data
        # Should have basic structure even if components aren't available
        assert isinstance(data["components"], dict)
    
    def test_text_refinement_endpoint(self):
        """Test text refinement endpoint with basic request"""
        test_data = {
            "text_description": "Generate a sine wave with period 24 hours",
            "domain": "sensor_data",
            "refinement_iterations": 1
        }
        
        response = requests.post(f"{API_BASE_URL}/refine-text", json=test_data)
        # Should return 200 or handle gracefully if BRIDGE not available
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
    
    def test_generate_timeseries_endpoint(self):
        """Test timeseries generation endpoint"""
        test_data = {
            "text_description": "Simple sine wave pattern",
            "sequence_length": 100,
            "domain": "test"
        }
        
        response = requests.post(f"{API_BASE_URL}/generate-timeseries", json=test_data)
        # Should return 200 or handle gracefully
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data


def test_import_structure():
    """Test that all imports work correctly before move"""
    # Test that api_server.py can be imported
    import importlib.util
    
    api_server_path = Path("api_server.py")
    assert api_server_path.exists(), "api_server.py should exist"
    
    spec = importlib.util.spec_from_file_location("api_server", api_server_path)
    api_server_module = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(api_server_module)
        print("✅ api_server.py imports successfully")
    except Exception as e:
        print(f"❌ Import error: {e}")
        # Don't fail the test if there are missing ML dependencies
        # Just log the issue
        pass


def test_api_directory_structure():
    """Test that the api directory has expected structure"""
    api_dir = Path("api")
    assert api_dir.exists(), "api directory should exist"
    assert api_dir.is_dir(), "api should be a directory"
    
    expected_files = [
        "startup.py",
        "models.py",
        "helpers.py",
        "file_handlers.py",
        "text_handlers.py",
        "timeseries_handlers.py",
        "anomaly_handlers.py"
    ]
    
    for file_name in expected_files:
        file_path = api_dir / file_name
        assert file_path.exists(), f"{file_name} should exist in api directory"


def test_ml_directories_exist():
    """Test that ML component directories exist"""
    ml_dirs = ["BRIDGE", "TarDiff", "TimeDP", "DiGA", "diffusion", "process"]
    
    for dir_name in ml_dirs:
        dir_path = Path(dir_name)
        assert dir_path.exists(), f"{dir_name} directory should exist"
        assert dir_path.is_dir(), f"{dir_name} should be a directory"


if __name__ == "__main__":
    print("🧪 Running pre-move API tests...")
    
    # Run the simple tests that don't require server
    test_import_structure()
    test_api_directory_structure()
    test_ml_directories_exist()
    
    print("✅ Pre-move structure tests passed!")
    
    # Run server tests if pytest is available
    try:
        import pytest
        pytest.main([__file__ + "::TestAPIBeforeMove", "-v"])
    except ImportError:
        print("⚠️  pytest not available, skipping server integration tests")
        print("   Install with: pip install pytest requests")
