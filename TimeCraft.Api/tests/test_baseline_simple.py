#!/usr/bin/env python3
"""
Simple API test without unicode characters
"""

import os
import sys
import time
import subprocess
from pathlib import Path


def get_venv_python():
    """Get the path to the virtual environment Python executable"""
    if sys.platform == "win32":
        return Path("venv") / "Scripts" / "python.exe"
    else:
        return Path("venv") / "bin" / "python"


def test_api_starts():
    """Test that the API starts without crashing"""
    print("Testing if API starts...")
    
    venv_python = get_venv_python()
    if not venv_python.exists():
        print(f"FAIL: Virtual environment Python not found: {venv_python}")
        return False
    
    try:
        # Start the API server using venv python
        process = subprocess.Popen(
            [str(venv_python), "api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("Waiting for API to start...")
        time.sleep(3)
        
        # Check if process is still running
        poll_result = process.poll()
        
        if poll_result is None:
            print("SUCCESS: API server started successfully")
            process.terminate()
            process.wait()
            return True
        else:
            # Process died, get error output
            stdout, stderr = process.communicate()
            print("FAIL: API server failed to start")
            print(f"Exit code: {poll_result}")
            if stdout:
                print(f"STDOUT: {stdout}")
            if stderr:
                print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"FAIL: Exception testing API: {e}")
        return False


def test_imports():
    """Test that basic imports work"""
    print("Testing imports...")
    
    venv_python = get_venv_python()
    
    try:
        # Simple import test without unicode
        test_script = '''
import sys
sys.path.insert(0, ".")

success = True
try:
    from api import startup
    print("SUCCESS: startup module imported")
except Exception as e:
    print(f"FAIL: startup import error: {e}")
    success = False

try:
    from fastapi import FastAPI
    print("SUCCESS: FastAPI imported")
except Exception as e:
    print(f"FAIL: FastAPI import error: {e}")
    success = False

if success:
    print("SUCCESS: All imports work")
else:
    print("FAIL: Some imports failed")
    sys.exit(1)
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
        print(f"FAIL: Exception in import test: {e}")
        return False


def main():
    """Run baseline API tests"""
    print("=== API Baseline Tests ===")
    
    tests = [
        ("Import Test", test_imports),
        ("API Start Test", test_api_starts),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"RESULT: {test_name} PASSED")
            else:
                failed += 1
                print(f"RESULT: {test_name} FAILED")
        except Exception as e:
            print(f"RESULT: {test_name} FAILED with exception: {e}")
            failed += 1
    
    print(f"\n=== SUMMARY ===")
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    
    if failed == 0:
        print("SUCCESS: All baseline tests passed! API is working.")
        return True
    else:
        print("FAIL: Some baseline tests failed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
