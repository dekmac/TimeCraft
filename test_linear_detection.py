#!/usr/bin/env python3
"""
Quick test script to verify linear pattern detection works correctly.
"""

import numpy as np
import sys
import os

# Add the API path to imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'TimeCraft.Api', 'TimeCraft.Api'))

def test_linear_detection():
    """Test the linear pattern detection logic."""
    
    # Simulate the linear detection logic from the code
    def detect_linear_pattern(values):
        """Detect linear patterns in time series data."""
        linear_tolerance = 0.001  # Tolerance for detecting linear patterns
        
        if len(values) < 10:
            return False, 0.0, 0.0
            
        # Calculate differences between consecutive values
        diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
        
        # Check if differences are nearly constant (linear pattern)
        if len(diffs) > 0:
            diff_std = np.std(diffs)
            mean_diff = np.mean(diffs)
            # Linear if differences are very consistent AND non-zero
            is_linear = (diff_std < linear_tolerance and abs(mean_diff) > linear_tolerance)
            return is_linear, mean_diff, diff_std
            
        return False, 0.0, 0.0
    
    # Test cases
    test_cases = [
        {
            'name': 'Linear Pattern (like humidity)',
            'data': [45.2, 45.3, 45.4, 45.5, 45.6, 45.7, 45.8, 45.9, 46.0, 46.1, 46.2, 46.3],
            'expected': True
        },
        {
            'name': 'Constant Pattern (like temperature)',
            'data': [18.5] * 12,
            'expected': False  # Constant is handled separately
        },
        {
            'name': 'Natural Variation',
            'data': [45.2, 45.1, 45.4, 45.0, 45.3, 45.5, 45.2, 45.6, 45.1, 45.8, 45.3, 45.4],
            'expected': False
        },
        {
            'name': 'Near-linear but with small variations',
            'data': [45.0, 45.1, 45.2, 45.21, 45.3, 45.31, 45.4, 45.41, 45.5, 45.51, 45.6, 45.61],
            'expected': False  # Should pass as having natural variation
        }
    ]
    
    print("=== Testing Linear Pattern Detection ===")
    
    for test_case in test_cases:
        is_linear, mean_diff, diff_std = detect_linear_pattern(test_case['data'])
        passed = is_linear == test_case['expected']
        status = "✅ PASS" if passed else "❌ FAIL"
        
        print(f"{status} {test_case['name']}")
        print(f"   Data: {test_case['data'][:6]}... (showing first 6)")
        print(f"   Linear detected: {is_linear} (expected: {test_case['expected']})")
        print(f"   Mean diff: {mean_diff:.6f}, Std diff: {diff_std:.6f}")
        print()
    
    print("=== Humidity Problem Example ===")
    humidity_problem = [45.2, 45.3, 45.4, 45.5, 45.6, 45.7, 45.8, 45.9, 46.0, 46.1]
    is_linear, mean_diff, diff_std = detect_linear_pattern(humidity_problem)
    print(f"Humidity linear pattern: {humidity_problem}")
    print(f"Is linear: {is_linear}")
    print(f"Mean increment: {mean_diff:.4f}")
    print(f"Consistency (std): {diff_std:.6f}")
    
    if is_linear:
        print("✅ This would now be detected as problematic and trigger improvement!")
    else:
        print("❌ This would NOT be detected - need to adjust thresholds")

if __name__ == "__main__":
    test_linear_detection()