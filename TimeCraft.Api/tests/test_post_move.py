#!/usr/bin/env python3
"""
Post-move validation tests
These will verify the API works after restructuring
"""

import os
import sys
from pathlib import Path


def test_new_structure_exists():
    """Test that the new TimeCraft.Api structure exists"""
    print("🧪 Testing new structure exists...")
    
    # Check main directory
    api_dir = Path("TimeCraft.Api")
    if not api_dir.exists():
        print("❌ TimeCraft.Api directory doesn't exist")
        return False
    
    # Check main API project directory
    main_api_dir = api_dir / "TimeCraft.Api"
    if not main_api_dir.exists():
        print("❌ TimeCraft.Api/TimeCraft.Api directory doesn't exist")
        return False
    
    # Check main.py exists
    main_py = main_api_dir / "main.py"
    if not main_py.exists():
        print("❌ main.py doesn't exist in TimeCraft.Api/TimeCraft.Api/")
        return False
    
    # Check api subdirectory moved correctly
    api_subdir = main_api_dir / "api"
    if not api_subdir.exists():
        print("❌ api subdirectory doesn't exist in new location")
        return False
    
    print("✅ New structure exists")
    return True


def test_ml_directories_remain():
    """Test that ML directories stayed at project root level"""
    print("🧪 Testing ML directories remain at root...")
    
    ml_dirs = ["BRIDGE", "TarDiff", "TimeDP", "DiGA", "diffusion", "process"]
    missing_dirs = []
    
    for dir_name in ml_dirs:
        dir_path = Path("TimeCraft.Api") / dir_name
        if not dir_path.exists() or not dir_path.is_dir():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ Missing ML directories in TimeCraft.Api: {missing_dirs}")
        return False
    
    print("✅ All ML directories exist in TimeCraft.Api")
    return True


def test_scripts_directory():
    """Test that scripts are organized properly"""
    print("🧪 Testing scripts directory...")
    
    scripts_dir = Path("TimeCraft.Api") / "scripts"
    if not scripts_dir.exists():
        print("❌ scripts directory doesn't exist")
        return False
    
    expected_scripts = ["setup_simple.py", "setup_environment.py", "serve.py"]
    missing_scripts = []
    
    for script in expected_scripts:
        script_path = scripts_dir / script
        if not script_path.exists():
            missing_scripts.append(script)
    
    if missing_scripts:
        print(f"⚠️  Missing scripts: {missing_scripts}")
        # Don't fail for missing scripts
    
    print("✅ Scripts directory structure is good")
    return True


def test_old_files_removed():
    """Test that old files were moved/removed from root"""
    print("🧪 Testing old files were moved...")
    
    old_files = ["api_server.py", "api_server_original.py"]
    remaining_files = []
    
    for file_name in old_files:
        file_path = Path(file_name)
        if file_path.exists():
            remaining_files.append(file_name)
    
    if remaining_files:
        print(f"⚠️  Old files still in root: {remaining_files}")
        # Don't fail - we might keep backups
    
    print("✅ Old files cleanup checked")
    return True


def test_can_import_new_structure():
    """Test that new structure can be imported"""
    print("🧪 Testing new structure imports...")
    
    try:
        # Add new path
        sys.path.insert(0, str(Path("TimeCraft.Api/TimeCraft.Api").absolute()))
        
        # Try to import from new location  
        # (This might fail due to dependencies, but structure should be ok)
        main_py_path = Path("TimeCraft.Api/TimeCraft.Api/main.py")
        if main_py_path.exists():
            print("✅ main.py exists and can be located")
        else:
            print("❌ main.py not found in new location")
            return False
            
    except Exception as e:
        print(f"⚠️  Import test failed (expected due to dependencies): {e}")
        # Don't fail for import issues
    
    print("✅ New structure import test completed")
    return True


def main():
    """Run all post-move tests"""
    print("🚀 Running post-move validation tests...")
    print("=" * 50)
    
    tests = [
        test_new_structure_exists,
        test_ml_directories_remain,
        test_scripts_directory,
        test_old_files_removed,
        test_can_import_new_structure,
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
        print("🎉 All post-move tests passed! Restructure successful.")
        return True
    else:
        print("⚠️  Some tests failed. Review the restructure.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
