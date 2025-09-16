"""
Unit tests for enhanced timeseries parsing, variability heuristics, and improvement logic.

Tests the bug fixes implemented in the timeseries generation pipeline:
- Enhanced parsing with metadata filtering
- Variability heuristics for static data detection
- Improvement loop triggers
- Configuration flags support
"""

import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add the API directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'TimeCraft.Api', 'api'))

from timeseries_handlers import (
    parse_timeseries_response,
    compute_variability_heuristics,
    TIMESERIES_STRICT_LENGTH,
    TIMESERIES_ENABLE_AUTO_IMPROVE
)


class TestEnhancedParsing(unittest.TestCase):
    """Test enhanced parsing logic with metadata filtering."""
    
    def test_parse_clean_numeric_sequence(self):
        """Test parsing a clean comma-separated numeric sequence."""
        response = "23.4, 24.1, 23.8, 24.5, 23.9"
        result = parse_timeseries_response(response, "TEST_TEMP", 5, 0)
        expected = [23.4, 24.1, 23.8, 24.5, 23.9]
        self.assertEqual(result, expected)
    
    def test_parse_with_metadata_contamination(self):
        """Test parsing response with device specifications and metadata."""
        response = '''DEVICE TYPE: Temperature Sensor
SPECIFICATIONS: Range 0-50°C, Precision ±0.1°C
MEASUREMENT: Hourly readings
23.4, 24.1, 23.8, 24.5, 23.9, 24.2, 23.7, 24.0'''
        
        result = parse_timeseries_response(response, "TEST_TEMP", 8, 0)
        expected = [23.4, 24.1, 23.8, 24.5, 23.9, 24.2, 23.7, 24.0]
        self.assertEqual(result, expected)
    
    def test_parse_with_bullet_points(self):
        """Test parsing response with bullet point metadata."""
        response = '''• Point 1: Initial reading
• Point 2: Mid-day peak
- Temperature values: 18.2, 18.5, 18.9, 19.3, 19.8
• Point 3: Evening decline'''
        
        result = parse_timeseries_response(response, "TEST_TEMP", 5, 0)
        expected = [18.2, 18.5, 18.9, 19.3, 19.8]
        self.assertEqual(result, expected)
    
    def test_parse_over_length_truncation(self):
        """Test truncation of over-length sequences."""
        response = "1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0"
        result = parse_timeseries_response(response, "TEST_SENSOR", 5, 0)
        expected = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.assertEqual(result, expected)
    
    def test_parse_under_length_acceptance(self):
        """Test acceptance of under-length sequences."""
        response = "1.0, 2.0, 3.0"
        result = parse_timeseries_response(response, "TEST_SENSOR", 5, 0)
        expected = [1.0, 2.0, 3.0]
        self.assertEqual(result, expected)
    
    @patch('timeseries_handlers.TIMESERIES_STRICT_LENGTH', True)
    def test_strict_mode_rejection(self):
        """Test strict mode rejects non-exact lengths."""
        response = "1.0, 2.0, 3.0"  # 3 values, expecting 5
        result = parse_timeseries_response(response, "TEST_SENSOR", 5, 0) 
        self.assertEqual(result, [])  # Should return empty to force regeneration
    
    def test_dense_block_extraction(self):
        """Test extraction of dense numeric blocks from mixed content."""
        response = '''Here are the sensor readings for your request:
        
The values follow the expected pattern:
12.1, 12.3, 12.5, 12.7, 12.9, 13.1, 13.3, 13.5, 13.7, 13.9, 14.1, 14.3

Additional specifications: Range 10-20, Accuracy ±0.1'''
        
        result = parse_timeseries_response(response, "TEST_SENSOR", 12, 0)
        expected = [12.1, 12.3, 12.5, 12.7, 12.9, 13.1, 13.3, 13.5, 13.7, 13.9, 14.1, 14.3]
        self.assertEqual(result, expected)


class TestVariabilityHeuristics(unittest.TestCase):
    """Test variability heuristics for static data detection."""
    
    def test_constant_series_detection(self):
        """Test detection of constant/static series."""
        values = [18.5] * 288  # All identical values
        metrics = compute_variability_heuristics(values, "TEST_TEMP", 288)
        
        self.assertTrue(metrics['is_constant'])
        self.assertTrue(metrics['needs_improvement'])
        self.assertIn("Constant values", metrics['variability_reason'])
        self.assertEqual(metrics['std_dev'], 0.0)
        self.assertEqual(metrics['unique_count'], 1)
    
    def test_low_variability_detection(self):
        """Test detection of low variability series."""
        values = [18.5, 18.5, 18.6, 18.5, 18.5] * 57  # Very low variation, 285 total
        metrics = compute_variability_heuristics(values, "TEST_TEMP", 285)
        
        self.assertFalse(metrics['is_constant'])  # Not constant but low variability
        self.assertTrue(metrics['is_low_variability'])
        self.assertTrue(metrics['needs_improvement'])
        self.assertIn("Low variability", metrics['variability_reason'])
        self.assertLess(metrics['std_dev'], 0.1)  # Very small standard deviation
    
    def test_good_variability_acceptance(self):
        """Test acceptance of series with good variability."""
        # Realistic temperature variation over 24 hours
        import math
        values = [20 + 5 * math.sin(i * 2 * math.pi / 24) + (i % 3 - 1) * 0.2 
                 for i in range(144)]  # 144 points = 6-hour intervals
        
        metrics = compute_variability_heuristics(values, "TEST_TEMP", 144)
        
        self.assertFalse(metrics['is_constant'])
        self.assertFalse(metrics['is_low_variability'])
        self.assertFalse(metrics['needs_improvement'])
        self.assertEqual(metrics['variability_reason'], "Good variability")
        self.assertGreater(metrics['std_dev'], 1.0)  # Reasonable variation
    
    def test_sensor_specific_thresholds(self):
        """Test sensor-specific variability thresholds."""
        # CO2 sensor should have higher std dev requirements
        values = [400.0, 400.1, 400.2, 400.1, 400.0] * 20  # 100 total
        co2_metrics = compute_variability_heuristics(values, "CO2_SENSOR_01", 100)
        temp_metrics = compute_variability_heuristics(values, "TEMP_SENSOR_01", 100)
        
        # Same data should be judged differently for different sensor types
        # CO2 should be more strict about variability than temperature
        self.assertTrue(co2_metrics['needs_improvement'])  # CO2 needs more variation
        # Temperature might be more tolerant of small variations
    
    def test_empty_values_handling(self):
        """Test handling of empty value arrays."""
        metrics = compute_variability_heuristics([], "TEST_SENSOR", 100)
        
        self.assertTrue(metrics['is_constant'])
        self.assertTrue(metrics['needs_improvement'])
        self.assertEqual(metrics['variability_reason'], "Empty values")
        self.assertEqual(metrics['unique_count'], 0)


class TestConfigurationFlags(unittest.TestCase):
    """Test configuration flag behavior."""
    
    @patch.dict(os.environ, {'TIMESERIES_STRICT_LENGTH': 'true'})
    def test_strict_length_environment_variable(self):
        """Test that strict length mode can be enabled via environment variable."""
        # Need to reload the module to pick up new env var
        import importlib
        import timeseries_handlers
        importlib.reload(timeseries_handlers)
        
        self.assertTrue(timeseries_handlers.TIMESERIES_STRICT_LENGTH)
    
    @patch.dict(os.environ, {'TIMESERIES_ENABLE_AUTO_IMPROVE': 'false'})
    def test_auto_improve_disable_environment_variable(self):
        """Test that auto-improve can be disabled via environment variable."""
        # Need to reload the module to pick up new env var
        import importlib
        import timeseries_handlers
        importlib.reload(timeseries_handlers)
        
        self.assertFalse(timeseries_handlers.TIMESERIES_ENABLE_AUTO_IMPROVE)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete enhancement pipeline."""
    
    def test_metadata_removal_plus_variability_check(self):
        """Test that metadata removal and variability check work together."""
        # Response with metadata that would inflate count, but actual data is constant
        response = '''DEVICE TYPE: Temperature Sensor
SPECIFICATIONS: Range 0-50°C
MEASUREMENT POINTS: 5
VALUES: 23.0, 23.0, 23.0, 23.0, 23.0'''
        
        values = parse_timeseries_response(response, "TEST_TEMP", 5, 0)
        self.assertEqual(values, [23.0, 23.0, 23.0, 23.0, 23.0])
        
        # Check that variability heuristics correctly identify this as problematic
        metrics = compute_variability_heuristics(values, "TEST_TEMP", 5)
        self.assertTrue(metrics['is_constant'])
        self.assertTrue(metrics['needs_improvement'])
    
    def test_realistic_scenario_processing(self):
        """Test processing of a realistic LLM response that would have failed before."""
        # This mimics the problematic responses seen in logs
        response = '''DEVICE TYPE: SF Building Humidity Sensor
CATEGORY: Environmental Monitoring
SPECIFICATIONS:
- Range: 0-100% RH
- Precision: ±2% RH
- TYPICAL VALUES: 45-65% for office environments

Here are the humidity readings:
52.3, 53.1, 52.8, 54.2, 53.5, 52.9, 53.7, 54.0, 53.2, 52.6,
53.4, 54.1, 53.8, 52.4, 53.0, 53.6, 54.3, 53.9, 52.7, 53.3'''
        
        values = parse_timeseries_response(response, "SF_BLDG_HUMIDITY_SENSOR_01", 20, 0)
        self.assertEqual(len(values), 20)
        self.assertTrue(all(52.0 <= v <= 55.0 for v in values))  # Reasonable range
        
        # Check variability
        metrics = compute_variability_heuristics(values, "SF_BLDG_HUMIDITY_SENSOR_01", 20)
        self.assertFalse(metrics['needs_improvement'])  # Should have good variability


if __name__ == '__main__':
    print("🧪 Running enhanced timeseries generation tests...")
    print(f"   Configuration: STRICT_LENGTH={TIMESERIES_STRICT_LENGTH}, AUTO_IMPROVE={TIMESERIES_ENABLE_AUTO_IMPROVE}")
    
    unittest.main(verbosity=2)