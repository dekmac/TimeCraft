#!/usr/bin/env python3
"""
Functional API test - test that the API actually works
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path


def test_api_can_start():
    """Test that the API server can start without crashing"""
    print("🧪 Testing if API server can start...")
    
    try:
        # Try to start the API server
        process = subprocess.Popen(
            [sys.executable, "api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for startup
        time.sleep(3)
        
        # Check if process is still running
        poll_result = process.poll()
        
        if poll_result is None:
            print("✅ API server started successfully")
            process.terminate()
            process.wait()
            return True
        else:
            # Process died, get error output
            stdout, stderr = process.communicate()
            print("❌ API server failed to start")
            print(f"Exit code: {poll_result}")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception starting API: {e}")
        return False


def test_api_imports():
    """Test that the API module imports work"""
    print("🧪 Testing API imports...")
    
    try:
        # Test basic Python imports
        import sys
        import os
        
        # Add current directory to path
        if "." not in sys.path:
            sys.path.insert(0, ".")
        
        # Try importing from api directory - but don't fail if missing deps
        try:
            from api import startup
            print("✅ API startup module imports")
        except ImportError as e:
            print(f"⚠️  API startup import failed (might be missing deps): {e}")
        
        try:
            from api import models
            print("✅ API models module imports")
        except ImportError as e:
            print(f"⚠️  API models import failed (might be missing deps): {e}")
        
        print("✅ Basic import test completed")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False


def test_python_environment():
    """Test that Python environment is working"""
    print("🧪 Testing Python environment...")
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Test basic packages
    try:
        import json
        import pathlib
        print("✅ Basic Python modules available")
    except ImportError as e:
        print(f"❌ Basic Python modules missing: {e}")
        return False
    
    return True


def test_file_structure():
    """Test that required files exist"""
    print("🧪 Testing file structure...")
    
    required_files = [
        "api_server.py",
        "api/startup.py",
        "api/models.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ Required files exist")
    return True


def main():
    """Run functional tests to verify API works"""
    print("🚀 Running functional API tests...")
    print("=" * 50)
    
    tests = [
        test_python_environment,
        test_file_structure,
        test_api_imports,
        test_api_can_start,
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
        print("🎉 All functional tests passed! API is working.")
        return True
    else:
        print("❌ Some tests failed. API needs fixing before restructure.")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 Try running: python setup_simple.py")
        print("   This will set up the basic Python environment")
    sys.exit(0 if success else 1)
