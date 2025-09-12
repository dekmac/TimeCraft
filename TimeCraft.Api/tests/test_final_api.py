#!/usr/bin/env python3
"""
Final end-to-end test of the restructured API
"""

import subprocess
import sys
import time
import requests
from pathlib import Path


def test_api_end_to_end():
    """Test the complete API functionality"""
    print("=== Final End-to-End API Test ===")
    
    venv_python = Path("venv/Scripts/python.exe")
    api_script = Path("TimeCraft.Api/TimeCraft.Api/main.py")
    
    try:
        # Start the API
        print("Starting restructured API server...")
        process = subprocess.Popen(
            [str(venv_python), str(api_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for startup
        time.sleep(5)
        
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"API failed to start: {stderr}")
            return False
        
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get("http://localhost:8080/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ Health endpoint works")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test API root
        print("Testing API root...")
        response = requests.get("http://localhost:8080/api", timeout=5)
        
        if response.status_code == 200:
            print("✅ API root works")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ API root failed: {response.status_code}")
            return False
        
        print("🎉 All end-to-end tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        return False
    finally:
        # Clean up
        if 'process' in locals():
            process.terminate()
            process.wait()
            print("API server stopped")


if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("Installing requests...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    success = test_api_end_to_end()
    sys.exit(0 if success else 1)
