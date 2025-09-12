#!/usr/bin/env python3
"""
Test the new TimeCraft.Api structure
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


def test_new_api_structure():
    """Test that the new API structure works"""
    print("Testing new API structure...")
    
    # Change to the TimeCraft.Api directory
    os.chdir("TimeCraft.Api")
    
    venv_python = Path("..") / get_venv_python()
    if not venv_python.exists():
        print(f"FAIL: Virtual environment Python not found: {venv_python}")
        return False
    
    try:
        # Test imports first
        test_script = '''
import sys
import os
sys.path.insert(0, "TimeCraft.Api")

try:
    from api import startup
    print("SUCCESS: startup module imported from new location")
except Exception as e:
    print(f"FAIL: startup import error: {e}")
    sys.exit(1)

try:
    from api import models
    print("SUCCESS: models module imported from new location")  
except Exception as e:
    print(f"FAIL: models import error: {e}")
    sys.exit(1)
'''
        
        result = subprocess.run(
            [str(venv_python), "-c", test_script],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.getcwd()
        )
        
        print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        
        if result.returncode != 0:
            print("FAIL: Import test failed")
            return False
        
        # Test that the API starts
        print("Testing API startup...")
        process = subprocess.Popen(
            [str(venv_python), "TimeCraft.Api/main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("Waiting for API to start...")
        time.sleep(3)
        
        poll_result = process.poll()
        
        if poll_result is None:
            print("SUCCESS: New API structure starts successfully")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print("FAIL: New API failed to start")
            print(f"Exit code: {poll_result}")
            if stdout:
                print(f"STDOUT: {stdout}")
            if stderr:
                print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"FAIL: Exception testing new API: {e}")
        return False
    finally:
        # Change back to original directory
        os.chdir("..")


def main():
    """Test the restructured API"""
    print("=== Testing Restructured API ===")
    
    if test_new_api_structure():
        print("SUCCESS: Restructured API works!")
        return True
    else:
        print("FAIL: Restructured API has issues")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
