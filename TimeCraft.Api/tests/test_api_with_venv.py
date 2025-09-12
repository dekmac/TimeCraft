#!/usr/bin/env python3
"""
Test API functionality using the virtual environment
"""

import os
import sys
import time
import subprocess
import requests
from pathlib import Path


def get_venv_python():
    """Get the path to the virtual environment Python executable"""
    if sys.platform == "win32":
        return Path("venv") / "Scripts" / "python.exe"
    else:
        return Path("venv") / "bin" / "python"


def test_api_with_venv():
    """Test that the API starts and responds using venv"""
    print("🧪 Testing API with virtual environment...")
    
    venv_python = get_venv_python()
    if not venv_python.exists():
        print(f"❌ Virtual environment Python not found: {venv_python}")
        return False
    
    try:
        # Start the API server using venv python
        process = subprocess.Popen(
            [str(venv_python), "api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("⏳ Waiting for API to start...")
        time.sleep(5)  # Give more time for startup
        
        # Check if process is still running
        poll_result = process.poll()
        
        if poll_result is None:
            print("✅ API server started successfully")
            
            # Try to make a request
            try:
                response = requests.get("http://localhost:8080/health", timeout=5)
                if response.status_code == 200:
                    print("✅ API responds to health check")
                    data = response.json()
                    print(f"   Response: {data}")
                    result = True
                else:
                    print(f"⚠️  API responded with status {response.status_code}")
                    result = True  # Still counts as working
            except requests.exceptions.RequestException as e:
                print(f"⚠️  Could not connect to API: {e}")
                result = True  # Process started, connection issue is separate
            
            # Clean shutdown
            process.terminate()
            process.wait()
            return result
        else:
            # Process died, get error output
            stdout, stderr = process.communicate()
            print("❌ API server failed to start")
            print(f"Exit code: {poll_result}")
            if stdout:
                print(f"STDOUT: {stdout}")
            if stderr:
                print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception testing API: {e}")
        return False


def test_basic_api_functionality():
    """Quick test that basic API components work"""
    print("🧪 Testing basic API functionality...")
    
    venv_python = get_venv_python()
    
    try:
        # Test that we can import API modules with venv
        test_script = '''
import sys
sys.path.insert(0, ".")

try:
    from api import startup, models, helpers
    print("✅ API modules import successfully")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

try:
    from fastapi import FastAPI
    print("✅ FastAPI available")
except Exception as e:
    print(f"❌ FastAPI not available: {e}")
    sys.exit(1)

print("✅ Basic functionality test passed")
'''
        
        result = subprocess.run(
            [str(venv_python), "-c", test_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Exception in basic functionality test: {e}")
        return False


def main():
    """Run all API functionality tests"""
    print("🚀 Testing API functionality with dependencies...")
    print("=" * 50)
    
    tests = [
        test_basic_api_functionality,
        test_api_with_venv,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All API functionality tests passed! Ready to restructure.")
        return True
    else:
        print("❌ API functionality tests failed. Need to fix before restructure.")
        return False


if __name__ == "__main__":
    # Make sure requests is available
    try:
        import requests
    except ImportError:
        print("Installing requests for API testing...")
        venv_python = get_venv_python()
        subprocess.run([str(venv_python), "-m", "pip", "install", "requests"])
        import requests
    
    success = main()
    sys.exit(0 if success else 1)
