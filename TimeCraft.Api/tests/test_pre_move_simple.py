#!/usr/bin/env python3
"""
Simple pre-move tests that don't require external dependencies
"""

import os
import sys
from pathlib import Path


def test_import_structure():
    """Test that all imports work correctly before move"""
    print("🧪 Testing import structure...")
    
    # Test that key modules can be imported
    try:
        # Test API imports
        sys.path.append(".")
        from api import startup, models, helpers
        print("✅ Core API modules import successfully")
    except Exception as e:
        print(f"❌ API import error: {e}")
        return False
    
    return True


def test_api_directory_structure():
    """Test that the api directory has expected structure"""
    print("🧪 Testing API directory structure...")
    
    api_dir = Path("api")
    if not api_dir.exists():
        print("❌ api directory doesn't exist")
        return False
    
    if not api_dir.is_dir():
        print("❌ api is not a directory")
        return False
    
    expected_files = [
        "startup.py",
        "models.py", 
        "helpers.py",
        "file_handlers.py",
        "text_handlers.py",
        "timeseries_handlers.py",
        "anomaly_handlers.py"
    ]
    
    missing_files = []
    for file_name in expected_files:
        file_path = api_dir / file_name
        if not file_path.exists():
            missing_files.append(file_name)
    
    if missing_files:
        print(f"❌ Missing API files: {missing_files}")
        return False
    
    print("✅ API directory structure is correct")
    return True


def test_ml_directories_exist():
    """Test that ML component directories exist"""
    print("🧪 Testing ML directories exist...")
    
    ml_dirs = ["BRIDGE", "TarDiff", "TimeDP", "DiGA", "diffusion", "process"]
    missing_dirs = []
    
    for dir_name in ml_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists() or not dir_path.is_dir():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"⚠️  Missing ML directories: {missing_dirs}")
        # Don't fail - these might be optional
    else:
        print("✅ All ML directories exist")
    
    return True


def test_main_files_exist():
    """Test that main Python files exist in root"""
    print("🧪 Testing main files exist...")
    
    main_files = [
        "api_server.py",
        "setup_simple.py",
        "serve.py"
    ]
    
    missing_files = []
    for file_name in main_files:
        file_path = Path(file_name)
        if not file_path.exists():
            missing_files.append(file_name)
    
    if missing_files:
        print(f"❌ Missing main files: {missing_files}")
        return False
    
    print("✅ All main files exist")
    return True


def main():
    """Run all pre-move tests"""
    print("🚀 Running pre-move structure validation tests...")
    print("=" * 50)
    
    tests = [
        test_main_files_exist,
        test_api_directory_structure,
        test_ml_directories_exist,
        test_import_structure,
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
        print("🎉 All pre-move tests passed! Ready to restructure.")
        return True
    else:
        print("⚠️  Some tests failed. Review before proceeding.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
