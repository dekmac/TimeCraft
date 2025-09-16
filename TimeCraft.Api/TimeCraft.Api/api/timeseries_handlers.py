"""
Time series generation endpoints for TimeCraft API.
"""

import math
import os
import random
import re
import time
import traceback
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from fastapi.responses import JSONResponse
from .models import (
    TextToTimeSeriesRequest, DomainPromptGenerationRequest, 
    TargetAwareGenerationRequest, AggregateTimeSeriesRequest,
    TagGenerationRequest, TagGenerationResponse,
    SingleTimeSeriesRequest, SingleTimeSeriesResponse
)
from .helpers import (
    create_demo_response, handle_api_error,
    parse_llm_timeseries_response
)

# Configuration flags for timeseries generation behavior
TIMESERIES_STRICT_LENGTH = os.environ.get('TIMESERIES_STRICT_LENGTH', 'false').lower() == 'true'
TIMESERIES_ENABLE_AUTO_IMPROVE = os.environ.get('TIMESERIES_ENABLE_AUTO_IMPROVE', 'true').lower() == 'true'

print(f"🔧 TimeSeries Config - STRICT_LENGTH: {TIMESERIES_STRICT_LENGTH}, AUTO_IMPROVE: {TIMESERIES_ENABLE_AUTO_IMPROVE}")


def generate_timestamps_for_horizon(time_horizon, sequence_length: int) -> List[str]:
    """Generate timestamp array for a given time horizon configuration."""
    timestamps = []
    start_time = datetime.now()
    
    # Calculate interval based on granularity
    if time_horizon.granularity == 'minute':
        interval = timedelta(minutes=1)
    elif time_horizon.granularity == 'hour':
        interval = timedelta(hours=1)
    elif time_horizon.granularity == 'day':
        interval = timedelta(days=1)
    else:
        interval = timedelta(hours=1)  # Default to hourly
    
    # Generate timestamps for the sequence
    for i in range(sequence_length):
        timestamp = start_time + (interval * i)
        timestamps.append(timestamp.isoformat())
    
    return timestamps

# Import prompts with try/except for development flexibility
try:
    from ..prompts import (
        prompt_manager,
        get_tag_generation_prompt,
        get_tag_reflection_prompt,
        get_timeseries_generation_prompt,
        get_timeseries_reflection_prompt,
        detect_device_type_from_tag
    )
    from ..prompts.keyword_fallbacks import (
        generate_tags_from_keywords,
        get_domain_specific_tags
    )
    PROMPTS_AVAILABLE = True
except ImportError:
    # Fallback imports for when running in isolation
    try:
        import sys
        import os
        # Add the parent directory to path for standalone execution
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        sys.path.insert(0, parent_dir)
        
        from prompts import (
            prompt_manager,
            get_tag_generation_prompt,
            get_tag_reflection_prompt,
            get_timeseries_generation_prompt,
            get_timeseries_reflection_prompt,
            detect_device_type_from_tag
        )
        from prompts.keyword_fallbacks import (
            generate_tags_from_keywords,
            get_domain_specific_tags
        )
        PROMPTS_AVAILABLE = True
    except ImportError as e:
        print(f"Warning: Could not import prompts module: {e}")
        PROMPTS_AVAILABLE = False


# Fallback ChatLLM implementation for environments without full BRIDGE dependencies
class FallbackChatLLM:
    """Fallback ChatLLM implementation that works without full BRIDGE dependencies."""
    
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0.7):
        self.model_name = model_name
        self.temperature = 0.7
        self.timeout = 30  # Reduced timeout to 30 seconds to prevent long waits
        self.max_retries = 2  # Reduced retries to 2 for faster failover
        
        # Load .env file if available
        self._load_env_file()
        
        self.has_openai = self._check_openai_availability()
        print(f"FallbackChatLLM initialized. OpenAI available: {self.has_openai}")
        print(f"Timeout set to {self.timeout}s, max retries: {self.max_retries}")
    
    def _load_env_file(self):
        """Load environment variables from .env file if available."""
        try:
            from dotenv import load_dotenv
            
            # Try to find .env file in various locations
            env_paths = [
                '.env',
                '../.env', 
                '../../.env',
                '../../../.env',
                os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')
            ]
            
            for env_path in env_paths:
                if os.path.exists(env_path):
                    print(f"🔧 Loading .env file from: {env_path}")
                    load_dotenv(env_path)
                    break
            else:
                print("ℹ️  No .env file found, using system environment variables")
                
        except ImportError:
            print("⚠️  python-dotenv not installed, using system environment variables")
    
    def _check_openai_availability(self):
        """Check if OpenAI is available and properly configured."""
        try:
            import openai
            api_key = os.environ.get('OPENAI_API_KEY')
            # Don't actually validate the API key since it may cause deployment errors
            # Just check if the module is available
            return bool(api_key)
        except ImportError:
            print("OpenAI package not installed")
            return False
    
    def generate(self, prompt):
        """Generate method that mimics the BRIDGE ChatLLM interface with timeout and retry logic."""
        print(f"🔍 FallbackChatLLM.generate() called with model: {self.model_name}")
        print(f"🔍 Environment check:")
        print(f"   OPENAI_API_KEY: {'SET' if os.environ.get('OPENAI_API_KEY') else 'NOT SET'}")
        print(f"   OPENAI_API_BASE: {os.environ.get('OPENAI_API_BASE', 'NOT SET')}")
        print(f"   OPENAI_DEPLOYMENT_NAME: {os.environ.get('OPENAI_DEPLOYMENT_NAME', 'NOT SET')}")
        print(f"   OPENAI_API_VERSION: {os.environ.get('OPENAI_API_VERSION', 'NOT SET')}")
        print(f"   Timeout: {self.timeout}s, Max retries: {self.max_retries}")
        
        # Try to use the actual API first with retry logic
        for attempt in range(self.max_retries):
            try:
                print(f"🔄 API attempt {attempt + 1}/{self.max_retries}")
                
                # Try different OpenAI import methods for compatibility
                client = None
                try:
                    # Try new OpenAI v1+ syntax first
                    from openai import AzureOpenAI
                    print(f"✅ OpenAI library imported successfully (v1+ syntax)")
                    
                    # Configure for Azure OpenAI - use explicit endpoint and deployment
                    if os.environ.get('OPENAI_API_KEY'):
                        print(f"🔄 Configuring Azure OpenAI...")
                        
                        api_base = os.environ.get('OPENAI_API_BASE', 'https://azure-openai-hou-hmi-2025.openai.azure.com')
                        api_version = os.environ.get('OPENAI_API_VERSION', '2024-08-01-preview')
                        api_key = os.environ.get('OPENAI_API_KEY')
                        deployment_name = os.environ.get('OPENAI_DEPLOYMENT_NAME', 'gpt-4o')
                        
                        print(f"✅ Azure OpenAI configured:")
                        print(f"   api_base: {api_base}")
                        print(f"   api_version: {api_version}")
                        print(f"   deployment_name: {deployment_name}")
                        
                        client = AzureOpenAI(
                            azure_endpoint=api_base,
                            api_key=api_key,
                            api_version=api_version
                        )
                        
                except ImportError:
                    # Try older OpenAI syntax as fallback
                    print("⚠️  New OpenAI syntax failed, trying legacy import")
                    import openai
                    print(f"✅ OpenAI library imported (legacy syntax)")
                    
                    if os.environ.get('OPENAI_API_KEY'):
                        openai.api_type = "azure"
                        openai.api_base = os.environ.get('OPENAI_API_BASE', 'https://azure-openai-hou-hmi-2025.openai.azure.com')
                        openai.api_version = os.environ.get('OPENAI_API_VERSION', '2024-08-01-preview')
                        openai.api_key = os.environ.get('OPENAI_API_KEY')
                        deployment_name = os.environ.get('OPENAI_DEPLOYMENT_NAME', 'gpt-4o')
                        
                        print(f"✅ Azure OpenAI configured (legacy):")
                        print(f"   api_base: {openai.api_base}")
                        print(f"   api_version: {openai.api_version}")
                        print(f"   deployment_name: {deployment_name}")
                
                if not os.environ.get('OPENAI_API_KEY'):
                    print("❌ No OPENAI_API_KEY found in environment variables")
                    raise Exception("No API key configured")
                    
                # Make the API call
                if client:
                    # New OpenAI v1+ syntax
                    deployment_name = os.environ.get('OPENAI_DEPLOYMENT_NAME', 'gpt-4o')
                    print(f"🚀 Making Azure OpenAI API call (timeout: {self.timeout}s)...")
                    
                    # GPT-5-mini specific adjustments
                    is_gpt5_mini = 'gpt-5' in deployment_name.lower() and 'mini' in deployment_name.lower()
                    if is_gpt5_mini:
                        system_message = "You are a helpful assistant. Generate the numeric time series data as requested."
                        tokens = 1000  # Token limit for GPT-5-mini
                        print(f"🔧 Using GPT-5-mini optimizations: system='{system_message}', tokens={tokens}")
                    else:
                        system_message = "You are a helpful assistant that returns only the requested data without explanation."
                        tokens = 2000
                    
                    response = client.chat.completions.create(
                        model=deployment_name,  # Use deployment name
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=self.temperature,
                        timeout=self.timeout,
                        max_completion_tokens=tokens
                    )
                    
                    print(f"✅ Azure OpenAI API call successful!")
                    result = response.choices[0].message.content
                    print(f"📝 Response: {result[:100]}...")
                    return result
                    
                else:
                    # Legacy OpenAI syntax
                    deployment_name = os.environ.get('OPENAI_DEPLOYMENT_NAME', 'gpt-4o')
                    print(f"🚀 Making Azure OpenAI API call (legacy) (timeout: {self.timeout}s)...")
                    
                    # GPT-5-mini specific adjustments for legacy API
                    is_gpt5_mini = 'gpt-5' in deployment_name.lower() and 'mini' in deployment_name.lower()
                    if is_gpt5_mini:
                        system_message = "You are a helpful assistant. Generate the numeric time series data as requested."
                        tokens = 1000  # Token limit for GPT-5-mini
                        print(f"🔧 Using GPT-5-mini optimizations (legacy): system='{system_message}', tokens={tokens}")
                    else:
                        system_message = "You are a helpful assistant that returns only the requested data without explanation."
                        tokens = 2000
                    
                    response = openai.ChatCompletion.create(
                        engine=deployment_name,  # Use engine for Azure
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=self.temperature,
                        request_timeout=self.timeout,
                        max_completion_tokens=tokens
                    )
                    
                    print(f"✅ Azure OpenAI API call successful!")
                    result = response.choices[0].message.content
                    print(f"📝 Response: {result[:100]}...")
                    return result
                    
            except Exception as e:
                error_type = type(e).__name__
                print(f"❌ Azure OpenAI API call failed (attempt {attempt + 1}): {e}")
                print(f"   Exception type: {error_type}")
                
                # Handle specific timeout errors
                if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                    print(f"⏰ Timeout detected - API call took longer than {self.timeout}s")
                elif "rate limit" in str(e).lower() or "429" in str(e):
                    print(f"🚫 Rate limit detected - API quota exceeded")
                elif "401" in str(e) or "unauthorized" in str(e).lower():
                    print(f"🔐 Authentication failed - check API key")
                    break  # No point retrying auth errors
                elif "404" in str(e) or "not found" in str(e).lower():
                    print(f"🔍 Deployment not found - check OPENAI_DEPLOYMENT_NAME")
                    break  # No point retrying if deployment doesn't exist
                
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    print(f"⏳ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"💥 All {self.max_retries} attempts failed")
                    print(f"   Full traceback:")
                    import traceback
                    traceback.print_exc()
                    
                    # Try regular OpenAI as final fallback
                    try:
                        print(f"🔄 Trying regular OpenAI as final fallback...")
                        from openai import OpenAI
                        
                        # Check for regular OpenAI key in environment
                        regular_openai_key = os.environ.get('OPENAI_API_KEY_REGULAR') or os.environ.get('OPENAI_KEY')
                        if regular_openai_key:
                            print(f"✅ Regular OpenAI key found, attempting connection...")
                            
                            client = OpenAI(api_key=regular_openai_key, timeout=self.timeout)
                            response = client.chat.completions.create(
                                model="gpt-4o" if "gpt-4" in self.model_name else "gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": "You are a helpful assistant that generates realistic time series data and sensor tags for industrial monitoring applications."},
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=self.temperature,
                                timeout=self.timeout
                            )
                            
                            result = response.choices[0].message.content
                            print(f"✅ Regular OpenAI API call successful!")
                            print(f"📝 Response: {result[:100]}...")
                            return result
                        else:
                            print(f"❌ No regular OpenAI key found (OPENAI_API_KEY_REGULAR or OPENAI_KEY)")
                            
                    except Exception as openai_error:
                        print(f"❌ Regular OpenAI also failed: {openai_error}")
                    
                    print("🔄 Falling back to mock responses")
                    break
        
        # Fall back behaviour: DO NOT fabricate timeseries. For tag generation we still supply domain tags; for timeseries return empty.
        print("⚠️  FallbackChatLLM: All API attempts failed. No synthetic timeseries will be generated.")
        prompt_lower = str(prompt).lower()
        is_tag_request = ("generate" in prompt_lower and ("tag" in prompt_lower or "name" in prompt_lower) and
                          "time series" not in prompt_lower and "timeseries" not in prompt_lower and
                          "numerical" not in prompt_lower and "values" not in prompt_lower)
        if is_tag_request:
            try:
                domain_tags = get_domain_specific_tags()
                # Provide some domain guided tags if possible; this is not timeseries data
                if any(keyword in prompt_lower for keyword in ["historic", "heritage", "monument", "museum", "tourist", "visitor", "footfall", "seismic", "spain"]):
                    return ", ".join(domain_tags['historic_building'][:5])
                return ", ".join(domain_tags['default'][:5])
            except Exception:
                return ""
        # timeseries path -> empty string so caller can detect and handle
        return ""
    
    def _generate_vibration_series(self, prompt):
        """Generate realistic vibration sensor data for structural monitoring."""
        import random
        import math
        
        # Extract length from prompt (default 24 for hourly data)
        length = 24
        if "hour" in prompt:
            if "24" in prompt: length = 24
            elif "48" in prompt: length = 48
        elif "day" in prompt: length = 24
        elif "week" in prompt: length = 168
        
        values = []
        for hour in range(length):
            # Base structural vibration (0.1-0.3 mm)
            base_vibration = 0.2 + random.uniform(-0.1, 0.1)
            
            # Traffic influence (higher during rush hours)
            time_of_day = hour % 24
            traffic_factor = 1.0
            if 7 <= time_of_day <= 9 or 17 <= time_of_day <= 19:  # Rush hours
                traffic_factor = 2.5 + random.uniform(0, 1.5)
            elif 22 <= time_of_day or time_of_day <= 6:  # Night
                traffic_factor = 0.3 + random.uniform(0, 0.2)
            elif 10 <= time_of_day <= 16:  # Day traffic
                traffic_factor = 1.5 + random.uniform(-0.3, 0.8)
            
            # Wind effects (random gusts)
            wind_factor = 1.0 + 0.3 * math.sin(hour * 0.3) + random.uniform(-0.2, 0.2)
            
            # Calculate final value
            vibration = base_vibration * traffic_factor * wind_factor
            
            # Add some measurement noise
            vibration += random.uniform(-0.02, 0.02)
            
            # Clamp to realistic range
            vibration = max(0.05, min(2.5, vibration))
            values.append(round(vibration, 3))
        
        return ", ".join(map(str, values))
    
    def _generate_strain_series(self, prompt):
        """Generate realistic strain gauge data (microstrain)."""
        import random
        import math
        
        length = 24
        values = []
        
        for hour in range(length):
            # Base strain (thermal + dead load)
            base_strain = 150 + 30 * math.sin(hour * math.pi / 12)  # Daily thermal cycle
            
            # Load-induced strain (traffic, wind)
            time_of_day = hour % 24
            if 7 <= time_of_day <= 9 or 17 <= time_of_day <= 19:
                load_strain = random.uniform(20, 80)  # Rush hour loads
            elif 22 <= time_of_day or time_of_day <= 6:
                load_strain = random.uniform(-10, 10)  # Night
            else:
                load_strain = random.uniform(5, 40)  # Normal day
            
            strain = base_strain + load_strain + random.uniform(-5, 5)
            values.append(round(strain, 1))
        
        return ", ".join(map(str, values))
    
    def _generate_displacement_series(self, prompt):
        """Generate realistic displacement/settlement data (mm)."""
        import random
        import math
        
        length = 24
        values = []
        
        for hour in range(length):
            # Base displacement with thermal effects
            base_displacement = 2.0 + 0.5 * math.sin(hour * math.pi / 12)
            
            # Progressive settlement (very small)
            settlement = hour * 0.001  # 0.001mm per hour
            
            # Dynamic response to loads
            dynamic = random.uniform(-0.1, 0.2)
            
            displacement = base_displacement + settlement + dynamic
            values.append(round(displacement, 3))
        
        return ", ".join(map(str, values))
    
    def _generate_temperature_series(self, prompt):
        """Generate realistic structural temperature data (°C)."""
        import random
        import math
        
        length = 24
        values = []
        
        for hour in range(length):
            # Daily temperature cycle
            time_of_day = hour % 24
            base_temp = 20 + 8 * math.sin((time_of_day - 6) * math.pi / 12)
            
            # Add weather variation
            weather_variation = random.uniform(-3, 3)
            
            # Thermal mass effects (structural lag)
            if time_of_day > 0:
                thermal_lag = 0.3 * values[-1] if values else base_temp
                temp = 0.7 * base_temp + 0.3 * thermal_lag + weather_variation
            else:
                temp = base_temp + weather_variation
            
            values.append(round(temp, 1))
        
        return ", ".join(map(str, values))
    
    def _generate_tilt_series(self, prompt):
        """Generate realistic tilt/inclination data (degrees)."""
        import random
        import math
        
        length = 24
        values = []
        base_tilt = 0.05  # Small base inclination
        
        for hour in range(length):
            # Wind-induced tilt
            wind_tilt = 0.02 * math.sin(hour * 0.5) + random.uniform(-0.01, 0.01)
            
            # Thermal differential tilt
            thermal_tilt = 0.01 * math.sin(hour * math.pi / 12)
            
            tilt = base_tilt + wind_tilt + thermal_tilt
            values.append(round(tilt, 4))
        
        return ", ".join(map(str, values))
    
    def _generate_contextual_timeseries(self, prompt):
        """Generate time series data based on detailed prompt context"""
        import random
        import math
        import re
        
        print(f"🎯 Parsing enhanced prompt for context...")
        
        # Extract key information from the sophisticated prompt
        context = self._parse_prompt_context(prompt)
        
        print(f"📊 Extracted context: {context}")
        
        # Generate data based on parsed context
        return self._generate_series_from_context(context)
    
    def _parse_prompt_context(self, prompt):
        """Parse the enhanced LLM prompt to extract scenario and time horizon context"""
        import re
        
        context = {
            'sensor_type': 'generic',
            'scenario': 'normal',
            'time_horizon': '24 hours',
            'sample_points': 24,
            'time_unit': 'hour',
            'severity': 'normal',
            'structure_type': 'building'
        }
        
        prompt_lower = prompt.lower()
        
        # Extract sensor type
        if "vibration" in prompt_lower:
            context['sensor_type'] = 'vibration'
        elif "strain" in prompt_lower:
            context['sensor_type'] = 'strain'
        elif "displacement" in prompt_lower or "settlement" in prompt_lower:
            context['sensor_type'] = 'displacement'
        elif "temperature" in prompt_lower:
            context['sensor_type'] = 'temperature'
        elif "tilt" in prompt_lower or "inclination" in prompt_lower:
            context['sensor_type'] = 'tilt'
        
        # Extract time horizon and sample points
        if "7 days" in prompt_lower or "7-day" in prompt_lower:
            context['time_horizon'] = '7 days'
            context['sample_points'] = 168  # hourly samples
            context['time_unit'] = 'hour'
        elif "30 days" in prompt_lower or "30-day" in prompt_lower:
            context['time_horizon'] = '30 days'
            context['sample_points'] = 240  # 3-hour samples
            context['time_unit'] = '3-hour'
        elif "24 hours" in prompt_lower or "24-hour" in prompt_lower:
            context['time_horizon'] = '24 hours'
            context['sample_points'] = 288  # 5-minute samples
            context['time_unit'] = '5-minute'
        
        # Extract sample points from mathematical constraints if specified
        points_match = re.search(r'(\d+)\s*(?:data\s*)?points?', prompt_lower)
        if points_match:
            context['sample_points'] = int(points_match.group(1))
        
        # Extract scenario context
        if any(word in prompt_lower for word in ['crack', 'damage', 'failure', 'collapse', 'severe']):
            context['scenario'] = 'damage'
            context['severity'] = 'high'
        elif any(word in prompt_lower for word in ['construction', 'load', 'traffic', 'wind', 'moderate']):
            context['scenario'] = 'loading'
            context['severity'] = 'moderate'
        elif any(word in prompt_lower for word in ['settlement', 'ground', 'foundation', 'gradual']):
            context['scenario'] = 'settlement'
            context['severity'] = 'gradual'
        
        # Extract structure type
        if any(word in prompt_lower for word in ['bridge', 'span']):
            context['structure_type'] = 'bridge'
        elif any(word in prompt_lower for word in ['tower', 'mast']):
            context['structure_type'] = 'tower'
        elif any(word in prompt_lower for word in ['tunnel']):
            context['structure_type'] = 'tunnel'
        
        return context
    
    def _generate_series_from_context(self, context):
        """Generate realistic time series data based on parsed context"""
        import random
        import math
        
        sensor_type = context['sensor_type']
        scenario = context['scenario']
        sample_points = context['sample_points']
        time_horizon = context['time_horizon']
        severity = context['severity']
        
        print(f"🔧 Generating {sample_points} points for {sensor_type} sensor in {scenario} scenario over {time_horizon}")
        
        # Base parameters by sensor type
        if sensor_type == 'vibration':
            base_range = (0.1, 2.0) if scenario == 'normal' else (0.5, 5.0)
            freq_component = True
        elif sensor_type == 'strain':
            base_range = (-100, 100) if scenario == 'normal' else (-500, 500)
            freq_component = False
        elif sensor_type == 'displacement':
            base_range = (-2, 2) if scenario == 'normal' else (-10, 15)
            freq_component = False
        elif sensor_type == 'temperature':
            base_range = (18, 25) if scenario == 'normal' else (15, 35)
            freq_component = False
        elif sensor_type == 'tilt':
            base_range = (-0.1, 0.1) if scenario == 'normal' else (-0.5, 0.8)
            freq_component = False
        else:
            base_range = (0.5, 1.5)
            freq_component = False
        
        # Scenario-specific modifications
        if scenario == 'damage':
            trend_factor = random.uniform(0.8, 2.0)  # Increasing trend
            noise_multiplier = 2.0
        elif scenario == 'loading':
            trend_factor = random.uniform(-0.3, 0.3)  # Variable loading
            noise_multiplier = 1.5
        elif scenario == 'settlement':
            trend_factor = random.uniform(0.2, 0.8)  # Gradual increase
            noise_multiplier = 0.8
        else:
            trend_factor = random.uniform(-0.1, 0.1)
            noise_multiplier = 1.0
        
        values = []
        base_mean = (base_range[0] + base_range[1]) / 2
        base_amplitude = (base_range[1] - base_range[0]) / 4
        
        for i in range(sample_points):
            # Time progression (0 to 1)
            t = i / (sample_points - 1) if sample_points > 1 else 0
            
            # Base trend
            if scenario == 'damage':
                # Exponential increase for damage
                trend = base_mean + (trend_factor * base_amplitude * (math.exp(t * 2) - 1))
            elif scenario == 'settlement':
                # Logarithmic increase for settlement
                trend = base_mean + (trend_factor * base_amplitude * math.log(1 + t * 4))
            else:
                # Linear trend
                trend = base_mean + (trend_factor * base_amplitude * t)
            
            # Frequency component (for vibration)
            if freq_component:
                # Add multiple frequency components
                freq1 = math.sin(2 * math.pi * t * 10) * base_amplitude * 0.3
                freq2 = math.sin(2 * math.pi * t * 25) * base_amplitude * 0.1
                trend += freq1 + freq2
            
            # Random noise
            noise_level = base_amplitude * 0.2 * noise_multiplier
            noise = random.gauss(0, noise_level)
            
            # Combine all components
            value = trend + noise
            
            # Sensor-specific constraints
            if sensor_type == 'vibration':
                value = max(0, value)  # Vibration can't be negative
            elif sensor_type == 'temperature':
                value = max(-50, min(100, value))  # Physical temperature limits
            
            values.append(round(value, 4))
        
        result = ", ".join(map(str, values))
        print(f"✅ Generated {len(values)} contextual data points")
        
        return result

    def _generate_generic_structural_series(self, prompt):
        """Generate generic but realistic structural monitoring data."""
        import random
        
        length = 24
        values = []
        
        for hour in range(length):
            # Base value with daily variation
            base = 50 + 10 * random.uniform(-1, 1)
            
            # Add some periodic components
            periodic = 5 * math.sin(hour * math.pi / 12) + 2 * math.sin(hour * math.pi / 6)
            
            # Random variation
            noise = random.uniform(-3, 3)
            
            value = base + periodic + noise
            values.append(round(value, 2))
        
        return ", ".join(map(str, values))


def reflect_on_tag_generation(description: str, generated_tags: List[str], 
                             num_tags: int, chat_llm, 
                             max_retries: int = 2) -> Tuple[List[str], bool]:
    """
    Use LLM self-reflection to assess and potentially improve tag generation.
    Returns (final_tags, was_improved)
    """
    current_tags = generated_tags.copy()
    
    for attempt in range(max_retries + 1):
        print(f"🔍 Tag reflection attempt {attempt + 1}/{max_retries + 1}")
        
        if attempt > 0:
            # Add delay between reflection attempts to prevent rate limiting
            print("⏳ Waiting 5s between reflection attempts...")
            time.sleep(5)
        
        try:
            # Create reflection prompt using the new prompt manager
            if PROMPTS_AVAILABLE:
                reflection_prompt = prompt_manager.get_tag_reflection_prompt(
                    description, current_tags, num_tags
                )
            else:
                # Fallback when prompts module not available
                tags_str = ", ".join(current_tags)
                reflection_prompt = f"""You are an expert in industrial monitoring systems. Please assess the quality of these generated sensor tag names.

ORIGINAL REQUEST: Generate {num_tags} realistic sensor tag names for: "{description}"
GENERATED TAGS: {tags_str}

Is this output ACCEPTABLE (YES/NO)?"""
            
            # Get reflection assessment
            print("🤔 Asking LLM to reflect on tag quality...")
            reflection_response = chat_llm.generate(reflection_prompt)
            print(f"📝 Reflection: {reflection_response[:200]}...")
            
            # Parse reflection response
            if "ACCEPTABLE: NO" in reflection_response.upper():
                print("❌ LLM says tags need improvement")
                
                # Look for better tags in the response
                if "BETTER_TAGS:" in reflection_response.upper():
                    lines = reflection_response.split('\n')
                    for line in lines:
                        if 'BETTER_TAGS:' in line.upper():
                            better_tags_str = line.split(':', 1)[1].strip()
                            improved_tags = [tag.strip() 
                                           for tag in better_tags_str.split(',') 
                                           if tag.strip()]
                            
                            if len(improved_tags) >= num_tags:
                                current_tags = improved_tags[:num_tags]
                                print(f"✅ Using improved tags: {current_tags}")
                                continue
                            else:
                                print(f"⚠️ Improved tags insufficient: {len(improved_tags)} < {num_tags}")
                                break
                
                # If no better tags provided, regenerate
                print("🔄 Regenerating tags with more specific prompt...")
                regeneration_prompt = prompt_manager.get_tag_regeneration_prompt(
                    description, num_tags, reflection_response
                )
                
                regenerated_response = chat_llm.generate(regeneration_prompt)
                regenerated_tags = parse_tag_names_response(regenerated_response, num_tags)
                current_tags = regenerated_tags
                print(f"🔄 Regenerated tags: {current_tags}")
                
            else:
                print("✅ LLM says tags are acceptable")
                was_improved = (attempt > 0)
                return current_tags, was_improved
                
        except Exception as e:
            print(f"❌ Reflection attempt {attempt + 1} failed: {e}")
            if attempt == max_retries:
                print("⚠️ Max reflection attempts reached, using current tags")
                return current_tags, False
            continue
    
    # If we've exhausted retries, return current tags
    return current_tags, (len(current_tags) != len(generated_tags) or 
                         current_tags != generated_tags)


def reflect_on_timeseries_generation(tag_name: str, description: str, 
                                   generated_values: List[float], 
                                   sequence_length: int, tag_index: int,
                                   chat_llm, max_retries: int = 2) -> Tuple[List[float], bool]:
    """
    Use LLM self-reflection to assess and potentially improve timeseries generation.
    Returns (final_values, was_improved)
    """
    current_values = generated_values.copy()
    
    for attempt in range(max_retries + 1):
        print(f"🔍 Timeseries reflection attempt {attempt + 1}/{max_retries + 1} for {tag_name}")
        
        if attempt > 0:
            # Add delay between reflection attempts to prevent rate limiting
            print("⏳ Waiting 5s between reflection attempts...")
            time.sleep(5)
        
        try:
            # Create reflection prompt using the new prompt manager
            reflection_prompt = prompt_manager.get_timeseries_reflection_prompt(
                tag_name, description, current_values, sequence_length
            )
            
            # Get reflection assessment
            print(f"🤔 Asking LLM to reflect on timeseries quality for {tag_name}...")
            reflection_response = chat_llm.generate(reflection_prompt)
            print(f"📝 Reflection: {reflection_response[:150]}...")
            
            # Parse reflection response
            if "ACCEPTABLE: NO" in reflection_response.upper():
                print(f"❌ LLM says timeseries for {tag_name} needs improvement")
                
                # Regenerate with more specific guidance
                print(f"🔄 Regenerating timeseries for {tag_name} with reflection feedback...")
                
                improvement_prompt = prompt_manager.get_timeseries_improvement_prompt(
                    tag_name, description, sequence_length, reflection_response
                )
                
                regenerated_response = chat_llm.generate(improvement_prompt)
                regenerated_values = parse_timeseries_response(
                    regenerated_response, tag_name, sequence_length, tag_index
                )
                current_values = regenerated_values
                print(f"🔄 Regenerated {len(current_values)} values for {tag_name}")
                
            else:
                print(f"✅ LLM says timeseries for {tag_name} is acceptable")
                was_improved = (attempt > 0)
                return current_values, was_improved
                
        except Exception as e:
            print(f"❌ Reflection attempt {attempt + 1} failed for {tag_name}: {e}")
            if attempt == max_retries:
                print(f"⚠️ Max reflection attempts reached for {tag_name}, using current values")
                return current_values, False
            continue
    
    # If we've exhausted retries, return current values
    return current_values, (len(current_values) != len(generated_values) or 
                           current_values != generated_values)


def get_sensor_specific_guidance(tag_name: str, tag_unit: str, time_horizon=None, sequence_length: int = 288) -> str:
    """Generate focused, sensor-specific guidance for realistic timeseries generation."""
    
    # Determine sensor type
    sensor_type = analyze_sensor_type(tag_name, tag_unit)
    sensor_category = sensor_type.get('category', 'unknown').lower()
    
    # Time context
    if time_horizon:
        duration = f"{time_horizon.period} {time_horizon.unit}"
        frequency = f"every {time_horizon.granularity}"
        time_info = f"TIMESPAN: {duration} ({sequence_length} measurements {frequency})"
    else:
        time_info = f"MEASUREMENTS: {sequence_length} sequential data points"
    
    # Sensor-specific patterns and rules
    if 'temp' in sensor_category:
        patterns = """
TEMPERATURE PATTERNS:
• Daily cycle: Cool night (18-20°C) → gradual morning rise → peak afternoon (24-26°C) → gradual fall
• SMOOTH curves only - NO zigzag, sawtooth, or multiple peaks
• Changes: 0.1-0.3°C per minute, 0.5-2°C per hour maximum
• Thermal mass prevents rapid temperature swings"""
        
    elif 'humidity' in sensor_category:
        patterns = """
HUMIDITY PATTERNS:
• Daily cycle: Peak early morning (60-65%) → minimum afternoon (45-50%) → rise evening
• NATURAL fluctuations with micro-variations (±0.1-0.3%)
• AVOID linear sequences (45.2, 45.3, 45.4...) - humidity varies naturally
• Changes: 1-3% per minute, 5-15% per hour maximum"""
        
    elif 'occupancy' in sensor_category or 'count' in sensor_category:
        patterns = """
OCCUPANCY PATTERNS:
• Daily cycle: Low overnight (1-3 people) → morning rise → peak tours (10-30 people) → evening decline
• Tour groups create periodic spikes every 30-60 minutes during peak hours
• AVOID all zeros - even at night there should be occasional security/maintenance staff
• Realistic range: 0-60 people with clear daily patterns"""
        
    elif 'co2' in sensor_category:
        patterns = """
CO2 PATTERNS:
• Baseline: 400-450 ppm (outdoor level)
• Occupied periods: Rise to 600-1200 ppm depending on crowding and ventilation
• Daily cycle follows occupancy with 15-30 minute lag due to air mixing
• Changes: 5-20 ppm per minute, 50-300 ppm per hour"""
        
    elif 'crack' in sensor_category or 'width' in sensor_category:
        patterns = """
CRACK WIDTH PATTERNS:
• Very stable measurements with minimal variation (±0.01-0.05 mm)
• Slow thermal expansion/contraction over day (±0.1 mm maximum)
• Small random sensor noise (±0.001-0.005 mm)
• AVOID constant values - include micro-variations from thermal effects"""
        
    else:
        patterns = f"""
GENERAL SENSOR PATTERNS:
• Include natural variations appropriate for {tag_name}
• Follow realistic physics for {tag_unit} measurements
• Avoid constant values, linear sequences, or unrealistic patterns"""
    
    return f"""{time_info}

{patterns}

CRITICAL RULES:
• NO constant values (all identical numbers)
• NO linear progressions (1.0, 1.1, 1.2, 1.3...)
• NO unrealistic patterns (zigzag, sawtooth, random spikes)
• Include natural micro-variations even in stable conditions"""


def get_gpt5mini_optimized_prompt(tag_name: str, tag_unit: str, sequence_length: int, time_horizon=None) -> str:
    """Generate a minimal, direct prompt optimized for GPT-5-mini's sensitivity."""
    
    # Determine sensor type for simple ranges
    tag_lower = tag_name.lower()
    
    if 'temp' in tag_lower:
        range_info = "18-26°C with daily variations"
        pattern = "smooth daily curve"
    elif 'humidity' in tag_lower or 'hum' in tag_lower:
        range_info = "45-65% with natural fluctuations"
        pattern = "varies with temperature"
    elif 'occupancy' in tag_lower or 'occ' in tag_lower or 'count' in tag_lower:
        range_info = "0-60 people with tour patterns"
        pattern = "peaks during tour times"
    elif 'co2' in tag_lower:
        range_info = "400-1200 ppm based on occupancy"
        pattern = "follows visitor patterns"
    elif 'crack' in tag_lower or 'fiss' in tag_lower or 'width' in tag_lower:
        range_info = "0.5-2.0 mm with minimal changes"
        pattern = "very stable with micro-variations"
    else:
        range_info = f"realistic {tag_unit} values"
        pattern = "appropriate for sensor type"
    
    # Time info
    if time_horizon:
        time_info = f"{sequence_length} values over {time_horizon.period} {time_horizon.unit}"
    else:
        time_info = f"{sequence_length} sequential values"
    
    # Minimal prompt optimized for GPT-5-mini
    return f"""Generate {time_info} for sensor {tag_name} ({tag_unit}).

Range: {range_info}
Pattern: {pattern}

Rules:
- Only numbers separated by commas
- No constant values
- No linear sequences
- Include natural variations

Output format: 23.4, 24.1, 23.8, 24.5, ..."""


def get_comprehensive_physics_knowledge(tag_name: str, tag_unit: str, time_horizon=None, scenario_context: str = "") -> str:
    """Generate comprehensive physics knowledge for any sensor type to guide LLM generation and validation."""
    
    # Determine sensor category
    sensor_type = analyze_sensor_type(tag_name, tag_unit)
    
    # Build comprehensive physics instructions
    physics_knowledge = f"""
=== COMPREHENSIVE SENSOR PHYSICS KNOWLEDGE ===

SENSOR: {tag_name} ({tag_unit})
CATEGORY: {sensor_type['category']}
MEASUREMENT TYPE: {sensor_type['measurement_type']}

=== FUNDAMENTAL PHYSICS PRINCIPLES ===

TEMPERATURE SENSORS:
• Thermal Dynamics: Temperature changes GRADUALLY due to thermal mass and heat transfer - NO RAPID OSCILLATIONS
• Smooth Curves: Temperature follows smooth curves, never sawtooth or zigzag patterns - thermal mass prevents rapid up/down changes
• Daily Cycles: Single smooth curve - Minimum typically 3-6 AM (pre-dawn cooling), Maximum typically 1-4 PM (peak solar heating)
• Rate Limits: Outdoor air: ~2-3°C/hour max, Indoor air: ~1-2°C/hour, Surfaces: ~0.5-1°C/hour, Liquids: ~0.1-0.5°C/hour
• Thermal Lag: Surfaces lag air by 1-3 hours, Deep materials lag by 2-6 hours - prevents rapid temperature swings
• Range Expectations: Outdoor 5-20°C daily, Indoor 2-8°C daily, Process systems vary widely
• CRITICAL: Generate smooth gradual transitions, NEVER create multiple peaks/valleys or oscillating patterns

HUMIDITY SENSORS:
• Moisture Physics: Relative humidity inversely related to temperature (warm air holds more moisture)
• Daily Patterns: Peak in early morning (3-7 AM) when air is coolest, Minimum in afternoon (2-5 PM) when air is warmest
• Rate Limits: ~10-15%/hour outdoors, ~5-10%/hour indoors, faster during weather changes
• Range Bounds: 0-100% physical limit, typically 30-90% in habitable spaces
• Temperature Coupling: For every 1°C increase, RH typically drops 3-5% (if absolute humidity constant)
• CRITICAL ANTI-LINEAR RULE: NEVER generate linear sequences like 45.2, 45.3, 45.4, 45.5 - humidity oscillates naturally
• Natural Fluctuation: Humidity shows minor random variations (±0.1-0.5%) even in stable conditions due to micro-circulation
• Pattern Requirements: Create realistic curves with small natural variations - NOT monotonic increases or decreases

PRESSURE SENSORS:
• Fluid Mechanics: Pressure changes follow hydraulic/pneumatic principles
• Atmospheric: Gradual changes 1-5 hPa/hour, 990-1040 hPa typical range, Weather fronts cause faster changes
• System Pressure: Can change rapidly with pumps/valves, smooth operation shows gradual changes
• Altitude Effects: ~12 hPa decrease per 100m elevation gain

CO2 SENSORS:
• Indoor Accumulation: CO2 builds up with occupancy, decreases with ventilation
• Outdoor Baseline: ~400-420 ppm atmospheric background
• Indoor Patterns: Rise during occupancy hours, fall overnight with ventilation
• Rate Changes: Can rise 50-200 ppm/hour with high occupancy, falls 20-100 ppm/hour with good ventilation

OCCUPANCY SENSORS:
• Daily Patterns: Tourist buildings have distinct occupancy cycles - NOT all zeros for 24 hours
• Business Hours: Peak visitor flow 9 AM - 6 PM, with lunch dip around 12-1 PM
• Tour Groups: Create periodic spikes of 10-30 people every 30-60 minutes during peak hours
• Evening/Night: Low but not zero occupancy (security, maintenance, late visitors)
• Realistic Values: Range 0-60 people with clear daily patterns
• CRITICAL ANTI-ZERO RULE: NEVER generate all zeros - even at night there should be 1-3 people occasionally
• Pattern Requirements: Create realistic occupancy curves with periodic visitor groups and daily cycles

=== OCCUPANCY AND ENVIRONMENTAL INTERACTIONS ===

HUMAN OCCUPANCY EFFECTS:
• Temperature: Each person adds ~100W heat load (can raise room temp 0.5-2°C depending on space size and HVAC)
• Humidity: Each person adds ~40-60g/hour moisture (can raise RH by 2-10% in typical rooms)
• CO2: Each person produces ~0.3-0.5 L/min CO2 (can raise levels 200-1000+ ppm in poorly ventilated spaces)
• Occupancy Patterns: Typically follow business hours (8 AM - 6 PM), lunch dips (12-1 PM), weekend differences

EQUIPMENT HEAT LOADS:
• Computers/Electronics: Add continuous heat, can raise local temperature 1-5°C
• Lighting: Traditional lighting adds significant heat, LED minimal impact
• Kitchen Equipment: Major heat and humidity sources during cooking times
• HVAC Systems: Create temperature/humidity gradients, air movement affects all sensors

BUILDING PHYSICS:
• Thermal Mass: Heavy buildings change temperature slowly, light buildings respond quickly
• Ventilation: Fresh air dilutes indoor pollutants and moisture
• Solar Gain: Windows cause temperature rise 2-8°C above ambient during sunny periods
• Infiltration: Outdoor air leakage affects all indoor environmental parameters

=== TIME-SCALE SPECIFIC PHYSICS ==="""

    # Add time-specific physics knowledge
    if time_horizon:
        if time_horizon.granularity == 'minute':
            physics_knowledge += f"""
MINUTE-LEVEL PHYSICS (Measurements every {time_horizon.granularity}):
• Temperature: Changes should be very gradual, max 0.1-0.3°C per minute in normal conditions
• Humidity: Small fluctuations, max 1-3% per minute unless major environmental change
  - NEVER create linear progressions (45.2, 45.3, 45.4...) - this violates natural humidity physics
  - Include micro-variations (±0.05-0.2%) due to air circulation even in stable conditions
  - Humidity varies quasi-randomly around mean levels, not in straight lines
• Pressure: Can be stable or show smooth trends, sudden spikes only with system events
• CO2: Can rise/fall 5-20 ppm/minute with occupancy changes or ventilation events
"""
        elif time_horizon.granularity == 'hour':
            physics_knowledge += f"""
HOURLY PHYSICS (Measurements every {time_horizon.granularity}):
• Temperature: SMOOTH gradual changes 0.5-3°C per hour, NO oscillations or sawtooth patterns - follow thermal physics
• Temperature Pattern: Create ONE smooth curve over 24 hours with gradual rise and fall - NOT multiple peaks/valleys
• AVOID: Rapid up-down temperature changes, zigzag patterns, multiple spikes, oscillatory behavior
• Humidity: Can change 5-15% per hour with weather, HVAC, or occupancy changes
• Pressure: Atmospheric changes 1-5 hPa/hour, system pressure can vary more rapidly
• CO2: Significant changes possible, 50-300 ppm/hour with occupancy/ventilation patterns
"""
        elif time_horizon.granularity == 'day':
            physics_knowledge += f"""
DAILY PHYSICS (Measurements every {time_horizon.granularity}):
• Temperature: Full daily cycles visible, 5-20°C range typical for outdoor sensors
• Humidity: Inverse temperature relationship clearly visible over daily cycles
• Pressure: Weather patterns drive multi-day trends, 10-30 hPa total variation
• CO2: Weekly patterns with occupancy, higher weekdays vs weekends
"""

    # Add scenario-specific physics
    if scenario_context:
        physics_knowledge += f"""
=== SCENARIO-SPECIFIC PHYSICS CONSIDERATIONS ===
Based on the scenario: "{scenario_context[:200]}..."

"""
        
        # Add specific 24-hour temperature pattern instructions
        if time_horizon and time_horizon.unit == 'days' and time_horizon.period == 1 and 'temp' in tag_name.lower():
            physics_knowledge += f"""
CRITICAL 24-HOUR TEMPERATURE PATTERN REQUIREMENTS:
==================================================
• MUST generate exactly ONE smooth daily temperature curve - NOT multiple waves
• Pattern: Cool night (20-22°C) → Gradual morning rise → Single afternoon peak (24-26°C) → Gradual fall → cool (night)
• NO OSCILLATIONS: Never create up-down-up-down patterns or multiple peaks - temperature has thermal mass
• SINGLE DAILY CYCLE: One minimum (3-6 AM), one maximum (12-4 PM), smooth transitions between all points
• AVOID: Rapid up-down temperature changes, zigzag patterns, multiple spikes, oscillatory behavior
"""
        # Analyze scenario for specific physics factors
        scenario_lower = scenario_context.lower()
        
        if any(word in scenario_lower for word in ['office', 'workplace', 'meeting', 'conference']):
            physics_knowledge += """
OFFICE ENVIRONMENT PHYSICS:
• Peak occupancy 9 AM - 5 PM creates temperature rise and humidity increase
• Lunch time (12-1 PM) shows temporary occupancy drop and environmental recovery
• Meeting rooms show rapid CO2 spikes during meetings, quick recovery after
• Computer equipment provides continuous heat load during business hours
• HVAC systems typically reduce activity evenings/weekends leading to drift toward outdoor conditions
"""
        
        if any(word in scenario_lower for word in ['outdoor', 'weather', 'ambient', 'external']):
            physics_knowledge += """
OUTDOOR ENVIRONMENT PHYSICS:
• Solar radiation drives daily temperature cycles with 3-8 hour thermal lag
• Weather fronts can cause rapid pressure changes and temperature/humidity shifts
• Wind affects all measurements - increases mixing and heat transfer
• Seasonal trends overlay daily patterns
• Precipitation events cause rapid humidity increases and temperature drops
"""
        
        if any(word in scenario_lower for word in ['industrial', 'factory', 'process', 'manufacturing']):
            physics_knowledge += """
INDUSTRIAL ENVIRONMENT PHYSICS:
• Process equipment creates significant heat loads affecting temperature patterns
• Shift patterns (day/night/weekend) strongly influence all environmental parameters
• Ventilation systems may be powerful, causing rapid environmental changes
• Steam/chemical processes can cause rapid humidity and temperature fluctuations
• Compressed air systems affect pressure measurements
"""

        if any(word in scenario_lower for word in ['kitchen', 'cooking', 'restaurant', 'food']):
            physics_knowledge += """
KITCHEN ENVIRONMENT PHYSICS:
• Cooking equipment creates massive heat and humidity loads during meal preparation
• Peak activity during meal times (breakfast 7-9 AM, lunch 11 AM-2 PM, dinner 5-8 PM)
• Exhaust fans create pressure changes and rapid environmental recovery
• Dishwashing creates high humidity spikes
• Refrigeration equipment provides cooling loads balancing cooking heat
"""

    physics_knowledge += f"""
=== VALIDATION PRINCIPLES ===

REALISTIC BEHAVIOR CHECKS:
• Values must stay within physically possible ranges for the measurement type
• Rate of change must respect physical limitations of the system being measured
• Patterns should align with known physics (daily cycles, occupancy effects, equipment schedules)
• Cross-correlations should make sense (temperature up → humidity down, occupancy up → CO2 up)

CRITICAL VALIDATION QUESTIONS:
• Do the timing of peaks and valleys align with physical drivers?
• Are the rates of change physically possible for the time scale?
• Do the absolute values make sense for the sensor type and environment?
• Are interactions between different environmental factors properly represented?
• Does the data reflect the specific scenario context provided?

COMMON PHYSICS VIOLATIONS TO AVOID:
• Temperature minimums at inappropriate times (like 3 PM instead of 3 AM)
• Impossible rate changes (10°C in 1 minute without major system event)
• Humidity over 100% or negative values
• Pressure readings outside possible ranges for the system type
• Missing correlation between occupancy and CO2/temperature/humidity
• Ignoring thermal mass and lag effects in temperature measurements
• Perfect stability when natural variation should occur
"""

    return physics_knowledge


def analyze_sensor_type(tag_name: str, tag_unit: str) -> dict:
    """Analyze sensor type and measurement characteristics."""
    tag_lower = tag_name.lower()
    unit_lower = tag_unit.lower()
    
    # Determine sensor category
    if any(word in tag_lower for word in ['temp', 'temperature', 'thermal']):
        category = 'temperature'
        measurement_type = 'thermal'
    elif any(word in tag_lower for word in ['humidity', 'rh', 'moisture']):
        category = 'humidity'
        measurement_type = 'moisture'
    elif any(word in tag_lower for word in ['pressure', 'bar', 'psi', 'pascal', 'hpa']):
        category = 'pressure'
        measurement_type = 'fluid'
    elif any(word in tag_lower for word in ['co2', 'carbon', 'dioxide', 'ppm']):
        category = 'gas_concentration'
        measurement_type = 'chemical'
    elif any(word in tag_lower for word in ['flow', 'rate', 'volume', 'velocity']):
        category = 'flow'
        measurement_type = 'fluid_dynamics'
    elif any(word in tag_lower for word in ['vibration', 'acceleration', 'shake']):
        category = 'vibration'
        measurement_type = 'mechanical'
    elif any(word in tag_lower for word in ['light', 'lux', 'illuminance', 'brightness']):
        category = 'light'
        measurement_type = 'optical'
    else:
        category = 'generic'
        measurement_type = 'unknown'
    
    return {
        'category': category,
        'measurement_type': measurement_type,
        'tag_name': tag_name,
        'tag_unit': tag_unit
    }


def get_expected_pattern_description(tag_name: str, time_horizon) -> str:
    """Get a description of the expected pattern for a sensor over a given time horizon."""
    is_temperature = any(temp_word in tag_name.lower() for temp_word in ['temp', 'temperature', 'thermal'])
    is_humidity = any(hum_word in tag_name.lower() for hum_word in ['humidity', 'rh', 'moisture'])
    is_pressure = any(press_word in tag_name.lower() for press_word in ['pressure', 'bar', 'psi', 'pascal'])
    
    if is_temperature:
        if time_horizon.unit == 'days' and time_horizon.period == 1:
            return "Daily cycle: cool in early morning (3-6 AM), warm in afternoon (2-4 PM)"
        elif time_horizon.unit == 'hours' and time_horizon.period <= 12:
            return "Gradual temperature changes with smooth transitions, no sudden spikes"
        else:
            return "Smooth temperature variations following thermal dynamics"
    elif is_humidity:
        if time_horizon.unit == 'days' and time_horizon.period == 1:
            return "Daily cycle: high humidity at night/early morning, lower during warm afternoon"
        else:
            return "Humidity variations (0-100%) with gradual changes, typically inverse to temperature"
    elif is_pressure:
        return "Gradual pressure changes following atmospheric or system dynamics, no sudden spikes without cause"
    else:
        return "Realistic sensor variations appropriate for the measurement type and time scale"


def parse_tag_names_response(response: str, num_tags: int) -> List[str]:
    """Parse LLM response to extract tag names (legacy format for backwards compatibility)."""
    try:
        # Clean the response
        response = response.strip()
        
        # Check if it's the new format with units (TAG_NAME|UNIT|DESCRIPTION)
        if '|' in response:
            return parse_enhanced_tag_response(response, num_tags)
        
        # Split by commas and clean each tag (legacy format)
        tags = [tag.strip() for tag in response.split(',') if tag.strip()]
        
        # Ensure we have exactly num_tags
        if len(tags) < num_tags:
            # Pad with generic tags
            for i in range(len(tags), num_tags):
                tags.append(f'Tag_{i + 1}')
        elif len(tags) > num_tags:
            tags = tags[:num_tags]
        
        return tags
        
    except Exception as e:
        print(f"Error parsing tag names response: {e}")
        # Return generic tags as fallback
        return [f'Tag_{i + 1}' for i in range(num_tags)]


def parse_enhanced_tag_response(response: str, num_tags: int) -> Tuple[List[str], List[dict]]:
    """Parse enhanced LLM response to extract tag names, units, and descriptions."""
    try:
        tags = []
        tag_details = []
        
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        
        for line in lines:
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    tag_name = parts[0].strip()
                    unit = parts[1].strip()
                    description = parts[2].strip()
                    
                    tags.append(tag_name)
                    tag_details.append({
                        'tag': tag_name,
                        'unit': unit,
                        'description': description
                    })
                elif len(parts) == 2:
                    # Handle case with just TAG|UNIT
                    tag_name = parts[0].strip()
                    unit = parts[1].strip()
                    
                    tags.append(tag_name)
                    tag_details.append({
                        'tag': tag_name,
                        'unit': unit,
                        'description': f'{tag_name} sensor'
                    })
            else:
                # Fallback for lines without proper format
                tag_name = line.strip()
                tags.append(tag_name)
                tag_details.append({
                    'tag': tag_name,
                    'unit': 'units',
                    'description': f'{tag_name} sensor'
                })
        
        # Ensure we have exactly num_tags
        while len(tags) < num_tags:
            i = len(tags) + 1
            tag_name = f'SENSOR_TAG_{i:02d}'
            tags.append(tag_name)
            tag_details.append({
                'tag': tag_name,
                'unit': 'units',
                'description': f'Generic sensor {i}'
            })
            
        if len(tags) > num_tags:
            tags = tags[:num_tags]
            tag_details = tag_details[:num_tags]
        
        return tags, tag_details
        
    except Exception as e:
        print(f"Error parsing enhanced tag response: {e}")
        # Return fallback data
        tags = [f'Tag_{i + 1}' for i in range(num_tags)]
        tag_details = [{'tag': tag, 'unit': 'units', 'description': f'{tag} sensor'} for tag in tags]
        return tags, tag_details


def generate_tag_names_with_llm(description: str, num_tags: int, chat_llm) -> Tuple[List[str], List[dict]]:
    """Generate tag names with units using LLM with self-reflection for quality assurance."""
    try:
        prompt = prompt_manager.get_tag_generation_prompt(description, num_tags)
        print(f"Generating enhanced tags with units using prompt: '{prompt[:50]}...'")
        
        # Initial generation
        response = chat_llm.generate(prompt)
        print(f"LLM enhanced tag response: '{response[:100]}...'")
        
        # Try to parse as enhanced format first
        if '|' in response:
            initial_tags, tag_details = parse_enhanced_tag_response(response, num_tags)
            tag_preview = [f"{t['tag']}({t['unit']})" for t in tag_details[:3]]
            print(f"✅ Parsed enhanced tags with units: {tag_preview}...")
        else:
            # Fall back to legacy format
            initial_tags = parse_tag_names_response(response, num_tags)
            tag_details = [{'tag': tag, 'unit': 'units', 'description': f'{tag} sensor'} for tag in initial_tags]
            print(f"⚠️ Using legacy format tags: {initial_tags}")
        
        # Self-reflection step (for now, just on tag names)
        print("🔍 Starting tag generation self-reflection...")
        final_tags, was_improved = reflect_on_tag_generation(
            description, initial_tags, num_tags, chat_llm, max_retries=2
        )
        
        # Update tag_details if tags were improved
        if was_improved:
            print(f"✅ Tags improved through reflection: {final_tags}")
            # Create new tag details for improved tags (preserve units if possible)
            if len(final_tags) == len(tag_details):
                for i, tag in enumerate(final_tags):
                    tag_details[i]['tag'] = tag
            else:
                tag_details = [{'tag': tag, 'unit': 'units', 'description': f'{tag} sensor'} for tag in final_tags]
        else:
            print(f"✅ Initial tags passed reflection")
            
        return final_tags, tag_details
        
    except Exception as e:
        print(f"Error generating enhanced tags with LLM: {e}")
        print("Falling back to keyword-based tag generation")
        # Fallback to keyword-based generation
        tags = generate_tag_names_from_description(description, num_tags, chat_llm)
        tag_details = [{'tag': tag, 'unit': 'units', 'description': f'{tag} sensor'} for tag in tags]
        return tags, tag_details


def parse_timeseries_response(response: str, tag_name: str, sequence_length: int,
                            tag_index: int) -> List[float]:
    """Parse LLM response to extract timeseries values with enhanced metadata filtering.

    Enhanced behavior:
    - Pre-clean: Remove metadata blocks (DEVICE TYPE, SPECIFICATIONS, bullets, etc.)
    - Extract: Find longest contiguous comma-separated numeric region via regex
    - Fallback: Use token-based splitting if no dense block found
    - Strict mode (TIMESERIES_STRICT_LENGTH=true): Reject non-exact lengths, return [] to force regeneration
    - Flexible mode (default): Accept ANY positive number of numeric values (no synthetic padding)
    - If more than expected, truncate to expected length (log truncation)
    - If fewer than expected, keep as-is (log short series) – downstream logic can still validate
    - Only return [] when no numeric values could be parsed or strict mode rejects length mismatch
    """
    try:
        cleaned = (response or "").strip()
        if not cleaned:
            return []
        
        # STEP 1: Pre-extraction block removal - filter out metadata lines
        metadata_patterns = [
            r'^DEVICE TYPE:.*$',
            r'^SENSOR TYPE:.*$', 
            r'^CATEGORY:.*$',
            r'^SPECIFICATIONS:.*$',
            r'^MEASUREMENT:.*$',
            r'^TYPICAL:.*$',
            r'^\*\*.*\*\*$',  # markdown headers
            r'^[-•]\s+.*$',   # bullet points
            r'^VALUES?:.*$',  # values prefix
            r'^Here are.*:.*$',  # descriptive preambles
        ]
        
        lines = cleaned.split('\n')
        filtered_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line matches metadata patterns
            is_metadata = False
            for pattern in metadata_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    is_metadata = True
                    break
            
            # Keep non-metadata lines or lines that contain comma-separated numbers
            if not is_metadata or re.search(r'\d+(?:\.\d+)?\s*,\s*\d+(?:\.\d+)?', line):
                filtered_lines.append(line)
        
        filtered_text = '\n'.join(filtered_lines)
        
        # STEP 2: Numeric block isolation - find longest contiguous comma-separated numeric region
        # Pattern to match dense numeric sequences (at least 10 consecutive comma-separated numbers)
        numeric_block_pattern = r'(?:\d+(?:\.\d+)?\s*,\s*){9,}\d+(?:\.\d+)?'
        numeric_blocks = re.findall(numeric_block_pattern, filtered_text)
        
        values: List[float] = []
        raw_parsed_length = 0
        extraction_method = "fallback_split"
        
        if numeric_blocks:
            # Choose the longest numeric block
            longest_block = max(numeric_blocks, key=len)
            extraction_method = "dense_block"
            
            # Parse the longest block
            for part in re.split(r'[,;]+', longest_block):
                part = part.strip()
                if part:
                    try:
                        values.append(float(part))
                    except ValueError:
                        continue
        
        # STEP 3: Fallback to token-based splitting if no dense block found
        if not values:
            extraction_method = "token_split"
            raw_parts = [p for p in re.split(r'[\n,;]+', filtered_text) if p.strip()]
            for part in raw_parts:
                part = part.strip()
                if part:
                    try:
                        values.append(float(part))
                    except ValueError:
                        continue  # ignore non-numeric tokens silently
        
        raw_parsed_length = len(values)
        
        if not values:
            print(f"⚠️ No numeric values extracted from {tag_name} response using {extraction_method}")
            return []
        
        # STEP 4: Length handling and metadata collection with strict mode support
        if TIMESERIES_STRICT_LENGTH and len(values) != sequence_length:
            print(f"❌ STRICT MODE: Rejecting {len(values)} values for {tag_name} (expected {sequence_length}) to force regeneration")
            return []
        
        if len(values) > sequence_length:
            print(f"ℹ️ Extracted {len(values)} values for {tag_name} using {extraction_method}; expected {sequence_length}. Truncating to expected length.")
            return values[:sequence_length]
        elif len(values) < sequence_length:
            print(f"ℹ️ Extracted {len(values)} (<{sequence_length}) values for {tag_name} using {extraction_method}. Accepting short series without padding.")
        else:
            print(f"✅ Extracted exactly {len(values)} values for {tag_name} using {extraction_method}.")
        
        return values
        
    except Exception as e:
        print(f"Error parsing timeseries response for {tag_name}: {e}")
        return []


def compute_variability_heuristics(values: List[float], tag_name: str, sequence_length: int) -> dict:
    """Compute variability statistics to detect static/constant series and assess data quality.
    
    Returns dictionary with variability metrics and flags for improvement triggers.
    """
    if not values or len(values) == 0:
        return {
            'std_dev': 0.0,
            'unique_count': 0,
            'range_ratio': 0.0,
            'max_delta': 0.0,
            'is_constant': True,
            'is_low_variability': True,
            'needs_improvement': True,
            'variability_reason': 'Empty values'
        }
    
    import numpy as np
    
    # Basic statistics
    values_array = np.array(values)
    std_dev = float(np.std(values_array))
    unique_values = len(set(values))
    mean_val = float(np.mean(values_array))
    value_range = float(np.max(values_array) - np.min(values_array))
    
    # Compute maximum consecutive delta (rate of change assessment)
    max_delta = 0.0
    if len(values) > 1:
        deltas = [abs(values[i+1] - values[i]) for i in range(len(values)-1)]
        max_delta = float(max(deltas))
    
    # Range ratio: normalized range relative to mean (helps detect flat lines)
    range_ratio = value_range / abs(mean_val) if mean_val != 0 else 0.0
    
    # Heuristic thresholds (configurable)
    min_unique_ratio = 0.05  # At least 5% unique values for long series
    min_std_threshold = 0.01  # Minimum standard deviation
    min_range_ratio = 0.001   # Minimum normalized range
    
    # Detect problematic patterns
    is_constant = (unique_values <= 1)
    is_low_variability = (
        unique_values <= max(5, int(sequence_length * min_unique_ratio)) or
        std_dev < min_std_threshold or
        range_ratio < min_range_ratio
    )
    
    # Detect linear patterns (e.g., 45.2, 45.3, 45.4, 45.5...)
    is_linear = False
    linear_tolerance = 0.001  # Tolerance for detecting linear patterns
    if len(values) >= 10:  # Need enough points to detect linearity
        # Calculate differences between consecutive values
        diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
        
        # Check if differences are nearly constant (linear pattern)
        if len(diffs) > 0:
            diff_std = np.std(diffs)
            mean_diff = np.mean(diffs)
            # Linear if differences are very consistent AND non-zero
            is_linear = (diff_std < linear_tolerance and abs(mean_diff) > linear_tolerance)
            
            if is_linear:
                print(f"📈 Linear pattern detected for {tag_name}: consistent diff={mean_diff:.4f}, std_dev={diff_std:.6f}")
    
    # Special handling for all-zeros pattern (common with occupancy sensors)
    is_all_zeros = False
    if len(values) > 0:
        non_zero_count = sum(1 for v in values if abs(v) > 0.001)
        zero_ratio = (len(values) - non_zero_count) / len(values)
        is_all_zeros = zero_ratio > 0.95  # More than 95% zeros is suspicious
        
        if is_all_zeros:
            print(f"🔍 All-zeros pattern detected for {tag_name}: {non_zero_count}/{len(values)} non-zero values ({zero_ratio:.1%} zeros)")
    
    # Special handling for temperature and other sensor types
    sensor_type_adjustments = {
        'temp': {'min_std': 0.1, 'min_unique_ratio': 0.1},
        'humidity': {'min_std': 0.5, 'min_unique_ratio': 0.1}, 
        'co2': {'min_std': 5.0, 'min_unique_ratio': 0.05},
        'occupancy': {'min_std': 0.1, 'min_unique_ratio': 0.02},  # Binary can be lower
        'crack': {'min_std': 0.001, 'min_unique_ratio': 0.1}
    }
    
    # Apply sensor-specific thresholds
    for sensor_key, thresholds in sensor_type_adjustments.items():
        if sensor_key.lower() in tag_name.lower():
            min_std_threshold = thresholds.get('min_std', min_std_threshold)
            min_unique_ratio = thresholds.get('min_unique_ratio', min_unique_ratio)
            is_low_variability = (
                unique_values <= max(5, int(sequence_length * min_unique_ratio)) or
                std_dev < min_std_threshold
            )
            break
    
    # Determine if improvement is needed
    needs_improvement = is_constant or is_low_variability or is_linear or is_all_zeros
    
    # Generate reason for improvement need
    variability_reason = "Good variability"
    if is_constant:
        variability_reason = f"Constant values (all {values[0] if values else 'N/A'})"
    elif is_all_zeros:
        variability_reason = f"All-zeros pattern ({non_zero_count}/{len(values)} non-zero values)"
    elif is_linear:
        variability_reason = f"Linear pattern detected (consistent increment of {np.mean(diffs):.4f})"
    elif is_low_variability:
        variability_reason = f"Low variability (std={std_dev:.4f}, unique={unique_values}/{len(values)})"
    
    return {
        'std_dev': std_dev,
        'unique_count': unique_values,
        'range_ratio': range_ratio,
        'max_delta': max_delta,
        'mean_value': mean_val,
        'value_range': value_range,
        'is_constant': is_constant,
        'is_low_variability': is_low_variability,
        'is_linear': is_linear,
        'is_all_zeros': is_all_zeros,
        'needs_improvement': needs_improvement,
        'variability_reason': variability_reason
    }


def validate_scenario_alignment(tag_name: str, tag_unit: str, description: str, 
                               generated_values: List[float], chat_llm, time_horizon=None) -> Tuple[bool, str]:
    """Validate that generated timeseries makes sense against the original scenario with physics-based checks."""
    try:
        # Create validation prompt
        values_preview = ", ".join([f"{v:.3f}" for v in generated_values[:10]])
        if len(generated_values) > 10:
            values_preview += f"... (showing first 10 of {len(generated_values)} values)"
        
        # Compute enhanced statistics including variability heuristics
        stats = {
            'min': min(generated_values),
            'max': max(generated_values),
            'avg': sum(generated_values) / len(generated_values),
            'range': max(generated_values) - min(generated_values)
        }
        
        # Add variability heuristics for quality assessment
        variability_metrics = compute_variability_heuristics(generated_values, tag_name, len(generated_values))
        stats.update(variability_metrics)
        
        # Get comprehensive physics knowledge for this sensor type
        physics_knowledge = get_comprehensive_physics_knowledge(tag_name, tag_unit, time_horizon, description)
        
        # Create time-aware validation context
        time_context = ""
        if time_horizon:
            time_context = f"""
TIME HORIZON CONTEXT:
• Duration: {time_horizon.period} {time_horizon.unit}
• Measurement frequency: Every {time_horizon.granularity}
• Total data points: {len(generated_values)}
• Expected pattern: {get_expected_pattern_description(tag_name, time_horizon)}
"""
        
        validation_prompt = f"""You are an expert sensor physics validation specialist with comprehensive knowledge of environmental sensor behavior, industrial systems, and real-world physics.

VALIDATION TASK: Analyze the generated sensor data for physics compliance and realism.

ORIGINAL SCENARIO: {description}
SENSOR TAG: {tag_name} (Units: {tag_unit})
{time_context}
GENERATED DATA PREVIEW: {values_preview}
DATA STATISTICS: Min={stats['min']:.3f}, Max={stats['max']:.3f}, Avg={stats['avg']:.3f}, Range={stats['range']:.3f}
VARIABILITY ANALYSIS: StdDev={stats['std_dev']:.4f}, Unique={stats['unique_count']}/{len(generated_values)}, MaxDelta={stats['max_delta']:.3f}
QUALITY FLAGS: {"❌ CONSTANT VALUES" if stats['is_constant'] else "❌ LOW VARIABILITY" if stats['is_low_variability'] else "✅ GOOD VARIABILITY"} - {stats['variability_reason']}

{physics_knowledge}

COMPREHENSIVE VALIDATION REQUIREMENTS:
1. Apply the physics knowledge above to validate this specific sensor data
2. Check if patterns align with known physical behavior for this sensor type
3. Verify that timing of peaks/valleys matches expected physics drivers
4. Confirm rates of change are physically possible for the measurement frequency
5. Validate that values are within realistic ranges for the sensor and scenario
6. Ensure cross-correlations with other environmental factors would be realistic
7. Consider occupancy, equipment, and environmental effects mentioned in the scenario

CRITICAL ASSESSMENT:
- PHYSICS_COMPLIANCE (1-10): Does this data follow the physics principles above?
- TIME_PATTERN_REALISM (1-10): Do patterns align with known physical drivers?
- VALUE_REALISM (1-10): Are values realistic for this sensor type and scenario?
- RATE_REALISM (1-10): Are change rates physically possible for the time scale?
- SCENARIO_ALIGNMENT (1-10): Does data reflect the specific scenario context?
- OVERALL_VALID (YES/NO): Is this data acceptable for real-world use?
- CRITICAL_ISSUES: [List specific physics violations or unrealistic patterns]
- IMPROVEMENT_NEEDED: [Specific guidance based on physics knowledge above]

Format your response as:
PHYSICS_COMPLIANCE: [score]
TIME_PATTERN_REALISM: [score]
VALUE_REALISM: [score]
RATE_REALISM: [score]
SCENARIO_ALIGNMENT: [score]
OVERALL_VALID: [YES/NO]
CRITICAL_ISSUES: [issues]
IMPROVEMENT_NEEDED: [guidance]"""

        print(f"🔍 Validating scenario alignment with comprehensive physics knowledge for {tag_name}...")
        
        validation_response = chat_llm.generate(validation_prompt)
        print(f"📝 Validation response: {validation_response[:200]}...")
        
        # Parse validation response - look for OVERALL_VALID: YES
        is_valid = "OVERALL_VALID: YES" in validation_response.upper()
        
        return is_valid, validation_response
        
    except Exception as e:
        print(f"❌ Scenario validation failed for {tag_name}: {e}")
        # Default to valid if validation fails
        return True, f"Validation failed but assuming valid: {e}"


def generate_timeseries_with_llm(tag_name: str, description: str,
                                sequence_length: int, tag_index: int,
                                chat_llm, tag_unit: str = "units",
                                time_horizon=None) -> dict:
    """Generate timeseries data using LLM with enhanced workflow: units, scenario awareness, and validation.
    Returns dict: {"values": List[float], "validation": {...}, "source": str}
    """
    try:
        print(f"🚀 Enhanced timeseries generation for {tag_name} ({tag_unit})")
        print(f"📅 Time horizon received: {time_horizon}")
        if time_horizon:
            print(f"📊 Time details - Period: {time_horizon.period}, Unit: {time_horizon.unit}, Granularity: {time_horizon.granularity}")
        else:
            print(f"⚠️ No time horizon provided!")
        
        # Step 1: Generate device-specific prompt
        device_info = detect_device_type_from_tag(tag_name)
        device_prompt = prompt_manager.get_device_analysis_prompt(tag_name, device_info)
        
        # Step 2: Generate focused, sensor-specific guidance
        sensor_guidance = get_sensor_specific_guidance(tag_name, tag_unit, time_horizon, sequence_length)
        
        # Step 3: Generate model-specific prompt (GPT-5-mini needs simpler prompts)
        model_name = getattr(chat_llm, 'model_name', 'unknown').lower()
        deployment_name = os.environ.get('OPENAI_DEPLOYMENT_NAME', '').lower()
        is_gpt5_mini = ('gpt-5' in model_name and 'mini' in model_name) or ('gpt-5' in deployment_name and 'mini' in deployment_name)
        
        print(f"🔍 Model detection: model_name='{model_name}', deployment_name='{deployment_name}', is_gpt5_mini={is_gpt5_mini}")
        
        if is_gpt5_mini:
            # Use the dynamic GPT-5-mini optimized prompt function
            enhanced_prompt = get_gpt5mini_optimized_prompt(tag_name, tag_unit, sequence_length, time_horizon)
            print(f"🔧 Using GPT-5-mini optimized prompt")
            print(f"📋 GPT-5-mini prompt preview (first 300 chars):")
            print(f"    {enhanced_prompt[:300]}...")
        else:
            # Original enhanced prompt for other models
            enhanced_prompt = f"""Generate {sequence_length} realistic sensor values for: {tag_name} ({tag_unit})

SCENARIO: {description}

{sensor_guidance}

OUTPUT FORMAT:
Your response must be ONLY comma-separated numbers. Start with a number, not text.

CORRECT: 23.4, 24.1, 23.8, 24.5, 23.9, 24.2
WRONG: DEVICE TYPE: Temperature Sensor
WRONG: Values: 23.4, 24.1, 23.8"""

        print(f"🤖 Generating timeseries for {tag_name} with enhanced context")
        print(f"📝 Tag: {tag_name}, Units: {tag_unit}")
        print(f"🎯 Model: {getattr(chat_llm, 'model_name', 'unknown')}")
        print(f"📋 Enhanced prompt preview (first 500 chars):")
        print(f"    {enhanced_prompt[:500]}...")
        if time_horizon:
            print(f"🕒 Time-aware prompt includes: {time_horizon.period} {time_horizon.unit} with {time_horizon.granularity} granularity")
        else:
            print(f"⚠️ Using fallback prompt without time horizon")
            
        # Step 3 & 4: Regeneration loop until we get correct length or exhaust attempts
        attempts = 3
        final_data: List[float] = []
        validation_feedback = None
        for attempt in range(attempts):
            attempt_prompt = enhanced_prompt if attempt == 0 else (
                enhanced_prompt + f"\n\nPREVIOUS ATTEMPT HAD NO PARSABLE NUMERIC VALUES. REGENERATE CLEAN COMMA-SEPARATED LIST ONLY."  # Only escalate if zero-length parse
            )
            response = chat_llm.generate(attempt_prompt)
            
            # Log full raw LLM output for debugging
            print(f"🤖 === RAW LLM OUTPUT for {tag_name} (Attempt {attempt+1}) ===")
            print(f"📝 Response length: {len(response)} characters")
            print(f"📄 Full raw response:")
            print("=" * 80)
            print(response)
            print("=" * 80)
            print(f"🔚 === END RAW OUTPUT for {tag_name} ===")
            
            values = parse_timeseries_response(response, tag_name, sequence_length, tag_index)
            if values:  # accept any non-empty list (may be short or truncated already)
                final_data = values
                break
            print(f"⚠️ Attempt {attempt+1}/{attempts} produced no parsable numeric values for {tag_name}.")
        if not final_data:
            print(f"❌ Unable to obtain any numeric values for {tag_name} after {attempts} attempts. Returning empty list.")
            return {"values": [], "validation": {"error": "llm_generation_failed", "attempts": attempts}, "source": "llm_failure"}
        original_length = len(final_data)
        length_status = "exact" if original_length == sequence_length else ("short" if original_length < sequence_length else "truncated")
        if length_status != "exact":
            print(f"✅ Obtained {original_length} values for {tag_name} (length_status={length_status}, expected={sequence_length})")
        else:
            print(f"✅ Obtained {original_length} values for {tag_name} (exact match)")
        # Scenario validation with variability assessment
        is_valid, validation_feedback = validate_scenario_alignment(
            tag_name, tag_unit, description, final_data, chat_llm, time_horizon
        )
        
        # Check if improvement is needed based on validation or variability
        variability_metrics = compute_variability_heuristics(final_data, tag_name, sequence_length)
        needs_improvement = not is_valid or variability_metrics.get('needs_improvement', False)
        
        # Attempt improvement if validation failed or variability is poor
        improved_data = final_data
        improvement_attempted = False
        
        if needs_improvement and TIMESERIES_ENABLE_AUTO_IMPROVE:
            improvement_reason = []
            if not is_valid:
                improvement_reason.append("physics validation failed")
            if variability_metrics.get('needs_improvement', False):
                improvement_reason.append(f"poor variability ({variability_metrics.get('variability_reason', 'unknown')})")
            
            print(f"🔄 Attempting improvement for {tag_name}: {', '.join(improvement_reason)}")
            
            # Create improvement prompt with specific feedback
            improvement_prompt = f"""The previous timeseries generation needs improvement. Please regenerate based on the feedback below.

ORIGINAL SCENARIO: {description}
SENSOR: {tag_name} ({tag_unit})
PREVIOUS DATA ISSUES: {', '.join(improvement_reason)}

PHYSICS VALIDATION FEEDBACK:
{validation_feedback}

VARIABILITY REQUIREMENTS:
- Avoid constant values (all identical numbers)
- Ensure realistic variation patterns for {tag_name}
- Standard deviation should be > {variability_metrics.get('std_dev', 0.01):.4f} 
- Need more than {variability_metrics.get('unique_count', 5)} unique values out of {sequence_length}

GENERATE IMPROVED DATA:
Create {sequence_length} realistic values that address the issues above.
Focus on natural variation patterns that follow physics principles for {tag_name}.

{enhanced_prompt.split('OUTPUT FORMAT STRICT:')[1] if 'OUTPUT FORMAT STRICT:' in enhanced_prompt else 'OUTPUT FORMAT: Return only numerical values as a comma-separated list.'}"""
            
            try:
                improvement_response = chat_llm.generate(improvement_prompt)
                
                # Log full raw LLM improvement output for debugging
                print(f"🔄 === RAW LLM IMPROVEMENT OUTPUT for {tag_name} ===")
                print(f"📝 Improvement response length: {len(improvement_response)} characters")
                print(f"📄 Full raw improvement response:")
                print("=" * 80)
                print(improvement_response)
                print("=" * 80)
                print(f"🔚 === END RAW IMPROVEMENT OUTPUT for {tag_name} ===")
                
                improved_values = parse_timeseries_response(improvement_response, tag_name, sequence_length, tag_index)
                
                if improved_values:
                    # Re-validate the improved data
                    improved_variability = compute_variability_heuristics(improved_values, tag_name, sequence_length)
                    improved_valid, improved_feedback = validate_scenario_alignment(
                        tag_name, tag_unit, description, improved_values, chat_llm, time_horizon
                    )
                    
                    # Use improved data if it's better (either physics validity or variability improved)
                    if (improved_valid and not is_valid) or (improved_variability.get('needs_improvement', True) < variability_metrics.get('needs_improvement', True)):
                        improved_data = improved_values
                        improvement_attempted = True
                        print(f"✅ Improvement successful for {tag_name}: physics_valid={improved_valid}, variability_improved={not improved_variability.get('needs_improvement', True)}")
                        
                        # Update validation results with improved data
                        is_valid = improved_valid
                        validation_feedback = improved_feedback
                        variability_metrics = improved_variability
                    else:
                        print(f"⚠️ Improvement attempt for {tag_name} did not yield better results; keeping original")
                else:
                    print(f"⚠️ Improvement attempt for {tag_name} failed to parse; keeping original")
                    
            except Exception as improvement_error:
                print(f"⚠️ Improvement attempt for {tag_name} failed: {improvement_error}; keeping original")
        elif needs_improvement and not TIMESERIES_ENABLE_AUTO_IMPROVE:
            improvement_reason = []
            if not is_valid:
                improvement_reason.append("physics validation failed")
            if variability_metrics.get('needs_improvement', False):
                improvement_reason.append(f"poor variability ({variability_metrics.get('variability_reason', 'unknown')})")
            print(f"⚙️ Auto-improvement disabled for {tag_name} (would improve: {', '.join(improvement_reason)})")
        
        if not is_valid and not improvement_attempted:
            print(f"⚠️ Scenario validation failed for {tag_name}; no improvement attempted, keeping original values.")
        # Optional numeric validator
        try:
            from .ts_validators import validate_and_repair
        except Exception:
            try:
                from ts_validators import validate_and_repair
            except Exception as _e:
                print(f"⚠️ Validator import failed: {_e}; returning unvalidated data.")
                return {
                    "values": improved_data, 
                    "validation": {
                        "note": "no_validator", 
                        "scenario_valid": is_valid, 
                        "length_status": length_status, 
                        "original_length": original_length, 
                        "expected_length": sequence_length,
                        "improvement_attempted": improvement_attempted,
                        "variability_metrics": variability_metrics
                    }, 
                    "source": "llm"
                }
        validation_result = validate_and_repair(tag_name, improved_data, time_horizon=time_horizon)
        validation_result.setdefault("scenario_valid", is_valid)
        # Attach enhanced metadata including improvement and variability
        validation_result.setdefault("length_status", length_status)
        validation_result.setdefault("original_length", original_length)
        validation_result.setdefault("expected_length", sequence_length)
        validation_result.setdefault("improvement_attempted", improvement_attempted)
        validation_result.setdefault("variability_metrics", variability_metrics)
        return {
            "values": validation_result.get("final_values", improved_data), 
            "validation": validation_result, 
            "source": validation_result.get("source", "llm")
        }
    except Exception as e:
        print(f"❌ ERROR in generate_timeseries_with_llm for {tag_name}: {e}")
        import traceback; traceback.print_exc()
        return {"values": [], "validation": {"error": str(e)}, "source": "exception"}


def generate_tag_names_from_description(description: str, num_tags: int, chat_llm=None) -> list:
    """Generate appropriate tag names using LLM or fallback to keyword matching."""
    
    # Try LLM-based generation first if available
    if chat_llm is not None:
        try:
            print(f"🚀 Generating {num_tags} tag names using LLM for: '{description[:50]}...'")
            prompt = prompt_manager.get_tag_generation_prompt(description, num_tags)
            response = chat_llm.generate(prompt)
            print(f"📝 LLM tag response: '{response[:50]}...'")
            tags = parse_tag_names_response(response, num_tags)
            print(f"✅ LLM generated {len(tags)} tags successfully")
            return tags
        except Exception as e:
            print(f"❌ LLM tag generation failed: {e}")
            print("🔄 Falling back to keyword-based tag generation")
    else:
        print("⚠️ No LLM available, using keyword-based tag generation")
    
    # Use the keyword fallback system
    return generate_tags_from_keywords(description, num_tags)

def handle_generate_timeseries_from_text(request: TextToTimeSeriesRequest, bridge_text2ts_available: bool) -> JSONResponse:
    """Generate time series data from text description using BRIDGE model."""
    try:
        if not bridge_text2ts_available:
            print("ℹ️ BRIDGE Text2TS model not available; returning empty timeseries as per policy (no mock data).")
            return create_demo_response(
                "no_model",
                "BRIDGE Text2TS model not available; empty timeseries returned.",
                timeseries=[],
                text=request.text,
                length=request.length,
                frequency=getattr(request, 'frequency', 'hourly')
            )
        

        
        # Try to use BRIDGE components - avoid importing non-existent modules
        try:
            from BRIDGE.self_refine.task_init import TimeSeriesTaskInit
            from BRIDGE.llm_agents.llm import ChatLLM
            
            # Use available BRIDGE components for generation
            # Since the specific inference module doesn't exist, use BRIDGE components
            # to generate time series through the available interfaces
            
            # For now, generate mock data with BRIDGE-enhanced metadata
            print("ℹ️ BRIDGE components present but generation pathway not implemented; returning empty list.")
            return JSONResponse({
                "status": "unavailable",
                "message": "BRIDGE components detected but direct generation not implemented; empty timeseries returned.",
                "text": request.text,
                "length": request.length,
                "frequency": getattr(request, 'frequency', 'hourly'),
                "timeseries": []
            })
            
        except ImportError as e:
            # If BRIDGE import fails, fall back to mock data
            print(f"BRIDGE components not available: {e}")
            print("ℹ️ BRIDGE components not available; returning empty timeseries.")
            return create_demo_response(
                "no_model",
                "BRIDGE components not available; empty timeseries returned.",
                text=request.text,
                length=request.length,
                frequency=getattr(request, 'frequency', 'hourly'),
                timeseries=[]
            )
        
    except Exception as e:
        return handle_api_error("generate_timeseries_from_text", e)


def handle_domain_prompt_generation(request: DomainPromptGenerationRequest, timedp_available: bool) -> JSONResponse:
    """Generate time series data using TimeDP domain prompts."""
    try:
        if not timedp_available:
            print("ℹ️ TimeDP model not available; returning empty timeseries (no mock).")
            return create_demo_response(
                "no_model", 
                "TimeDP model not available; empty timeseries returned.",
                timeseries=[],
                domain=request.domain,
                length=request.length
            )
        
        # Import TimeDP modules
        from TimeDP.inference.domain_generation import generate_with_domain_prompt
        
        # Generate time series with domain prompts
        result = generate_with_domain_prompt(
            domain=request.domain,
            length=request.length,
            num_samples=getattr(request, 'num_samples', 1)
        )
        
        return JSONResponse({
            "status": "success", 
            "domain": request.domain,
            "length": request.length,
            "num_samples": getattr(request, 'num_samples', 1),
            "timeseries": result.get("timeseries", []),
            "details": result
        })
        
    except Exception as e:
        return handle_api_error("domain_prompt_generation", e)


def handle_target_aware_generation(request: TargetAwareGenerationRequest, tardiff_available: bool) -> JSONResponse:
    """Generate time series data using TarDiff target-aware generation."""
    try:
        if not tardiff_available:
            print("ℹ️ TarDiff model not available; returning empty timeseries (no mock).")
            return create_demo_response(
                "no_model",
                "TarDiff model not available; empty timeseries returned.",
                timeseries=[],
                target_value=request.target_value,
                length=request.length
            )
        
        # Try to import TarDiff modules - fallback to our dynamic physics system if not available
        try:
            from TarDiff.inference.target_aware_generation import generate_target_aware_timeseries
            
            # Generate target-aware time series
            result = generate_target_aware_timeseries(
                target_value=request.target_value,
                length=request.length,
                guidance_scale=getattr(request, 'guidance_scale', 1.0),
                num_samples=getattr(request, 'num_samples', 1)
            )
            
            return JSONResponse({
                "status": "success",
                "target_value": request.target_value, 
                "length": request.length,
                "guidance_scale": getattr(request, 'guidance_scale', 1.0),
                "num_samples": getattr(request, 'num_samples', 1),
                "timeseries": result.get("timeseries", []),
                "details": result
            })
            
        except ImportError as e:
            print(f"⚠️ TarDiff not available: {e}")
            print("🔄 Falling back to dynamic physics generation...")
            
            # Fallback to our enhanced LLM-based generation with dynamic physics
            chat_llm = FallbackChatLLM('gpt-4o', temperature=0.5)
            
            # Create a scenario description that incorporates the target value
            scenario_description = f"Generate sensor data that targets around {request.target_value} with realistic physics-based variations"
            tag_name = f"TARGET_SENSOR_{request.target_value}"
            
            # Generate using our dynamic physics system
            result_dict = generate_timeseries_with_llm(
                tag_name=tag_name,
                description=scenario_description,
                sequence_length=request.length,
                tag_index=0,
                chat_llm=chat_llm,
                tag_unit="units"
            )
            generated_data = result_dict.get("values", [])
            diagnostics = result_dict.get("validation")
            return JSONResponse({
                "status": "success",
                "message": "Generated using dynamic physics system (TarDiff not available)",
                "target_value": request.target_value,
                "length": request.length,
                "guidance_scale": getattr(request, 'guidance_scale', 1.0),
                "num_samples": getattr(request, 'num_samples', 1),
                "timeseries": generated_data,
                "generation_method": "dynamic_physics_fallback",
                "details": {
                    "fallback": True,
                    "method": "LLM with dynamic physics",
                    "target_value": request.target_value,
                    "validation": diagnostics
                }
            })
        
    except Exception as e:
        return handle_api_error("target_aware_generation", e)


def handle_generate_tags(request: TagGenerationRequest, bridge_text2ts_available: bool) -> JSONResponse:
    """Generate tag names from text description."""
    print(f"🏷️  === HANDLE_GENERATE_TAGS CALLED ===")
    print(f"🏷️  Request: {request}")
    print(f"🏷️  Text description: '{request.text_description}'")
    print(f"🏷️  Bridge available: {bridge_text2ts_available}")
    
    try:
        print(f"Tag generation started - bridge_text2ts_available: {bridge_text2ts_available}")
        
        # Step 1: Try LLM-based generation (highest priority)
        llm_available = False
        chat_llm = None
        
        print(f"🔄 Attempting LLM-based tag generation...")
        
        # Always try FallbackChatLLM first (bypass BRIDGE dependency issues)
        try:
            model_name = getattr(request, 'model_name', 'gpt-4o')
            print(f"🚀 Creating FallbackChatLLM with model: {model_name}")
            
            chat_llm = FallbackChatLLM(
                model_name=model_name,
                temperature=getattr(request, 'temperature', 0.7)
            )
            llm_available = True
            print(f"✅ FallbackChatLLM created successfully")
        except Exception as e:
            print(f"❌ FallbackChatLLM failed: {e}")
        
        # Only try BRIDGE if FallbackChatLLM failed
        if not llm_available and bridge_text2ts_available:
            try:
                from BRIDGE.llm_agents.llm import ChatLLM
                model_name = getattr(request, 'model_name', 'gpt-3.5-turbo')
                print(f"🔄 Falling back to BRIDGE ChatLLM with model: {model_name}")
                
                chat_llm = ChatLLM(
                    model_name=model_name,
                    temperature=getattr(request, 'temperature', 0.7)
                )
                llm_available = True
                print(f"✅ Using full BRIDGE ChatLLM with model {model_name}")
            except (ImportError, Exception) as e:
                print(f"❌ Full BRIDGE ChatLLM failed: {e}")
        
        # Step 2: Generate tag names using the best available method
        tag_details = []  # Initialize tag details
        
        if llm_available and chat_llm:
            print("Generating tags with enhanced LLM")
            
            # Include time horizon context in tag generation
            description = request.text_description
            if request.time_horizon:
                time_context = f" The data will span {request.time_horizon.period} {request.time_horizon.unit} with measurements every {request.time_horizon.granularity}, totaling {request.time_horizon.total_points} data points."
                description = f"{request.text_description}{time_context}"
            
            generated_tags, tag_details = generate_tag_names_with_llm(
                description, 
                request.num_tags, 
                chat_llm
            )
            tag_generation_method = "llm_enhanced"
        else:
            print("Generating tags with keyword mapping")
            generated_tags = generate_tag_names_from_description(
                request.text_description, 
                request.num_tags,
                chat_llm
            )
            # Create basic tag details for fallback
            tag_details = [{'tag': tag, 'unit': 'units', 'description': f'{tag} sensor'} for tag in generated_tags]
            tag_generation_method = "keyword"
        
        print(f"Generated tags: {generated_tags}")
        print(f"Tag details: {[(td['tag'], td['unit']) for td in tag_details]}")
        
        # Step 3: Prepare enhanced response with tag details
        response_data = {
            "status": "success",
            "message": f"Tag names generated successfully using {tag_generation_method} method",
            "text_description": request.text_description,
            "num_tags": request.num_tags,
            "tags": generated_tags,  # Keep for backwards compatibility
            "tag_details": tag_details,  # Enhanced tag information with units
            "generation_method": tag_generation_method
        }

        print(f"Returning tag response with method: {tag_generation_method}")
        return JSONResponse(response_data)
        
    except Exception as e:
        print(f"Error in generate_tags: {traceback.format_exc()}")
        return handle_api_error("generate_tags", e)


def handle_generate_single_timeseries(request: SingleTimeSeriesRequest, bridge_text2ts_available: bool) -> JSONResponse:
    """Generate timeseries data for a single tag."""
    try:
        print(f"Single timeseries generation started for tag: {request.tag_name}")
        
        # Step 1: Try LLM-based generation (highest priority)
        llm_available = False
        chat_llm = None
        
        print(f"🔄 Attempting LLM-based timeseries generation...")
        
        # Always try FallbackChatLLM first (bypass BRIDGE dependency issues)
        try:
            model_name = getattr(request, 'model_name', 'gpt-4o')
            print(f"🚀 Creating FallbackChatLLM with model: {model_name}")
            
            chat_llm = FallbackChatLLM(
                model_name=model_name,
                temperature=getattr(request, 'temperature', 0.7)
            )
            llm_available = True
            print(f"✅ FallbackChatLLM created successfully for timeseries")
        except Exception as e:
            print(f"❌ FallbackChatLLM failed for timeseries: {e}")
        
        # Only try BRIDGE if FallbackChatLLM failed
        if not llm_available and bridge_text2ts_available:
            try:
                from BRIDGE.llm_agents.llm import ChatLLM
                model_name = getattr(request, 'model_name', 'gpt-3.5-turbo')
                print(f"🔄 Falling back to BRIDGE ChatLLM for timeseries")
                
                chat_llm = ChatLLM(
                    model_name=model_name,
                    temperature=getattr(request, 'temperature', 0.7)
                )
                llm_available = True
                print(f"✅ Using full BRIDGE ChatLLM for timeseries")
            except (ImportError, Exception) as e:
                print(f"❌ Full BRIDGE ChatLLM failed for timeseries: {e}")
        
        # Step 2: Generate timeseries data using the best available method
        tag_index = getattr(request, 'tag_index', 0)
        
        # Use time horizon info if available, otherwise fall back to sequence_length
        if request.time_horizon:
            sequence_length = request.time_horizon.total_points
            
            # Handle batching for large datasets
            if request.time_horizon.batch_size and request.time_horizon.batch_index is not None:
                # Calculate the range for this batch
                batch_size = request.time_horizon.batch_size
                batch_index = request.time_horizon.batch_index
                start_idx = batch_index * batch_size
                end_idx = min(start_idx + batch_size, sequence_length)
                actual_batch_size = end_idx - start_idx
                print(f"Generating batch {batch_index + 1}: points {start_idx}-{end_idx} ({actual_batch_size} points)")
                sequence_length = actual_batch_size
            else:
                print(f"Generating full dataset: {sequence_length} points for {request.time_horizon.period} {request.time_horizon.unit} at {request.time_horizon.granularity} intervals")
        else:
            sequence_length = request.sequence_length
        
        if llm_available and chat_llm:
            print(f"Generating timeseries for {request.tag_name} with LLM workflow")
            tag_unit = getattr(request, 'tag_unit', None)
            
            # If no tag_unit provided, try to infer from tag name
            if not tag_unit or tag_unit == 'units':
                tag_lower = request.tag_name.lower()
                if 'temp' in tag_lower:
                    tag_unit = '°C'
                elif 'hum' in tag_lower:
                    tag_unit = '%'
                elif 'occ' in tag_lower or 'count' in tag_lower:
                    tag_unit = 'people'
                elif 'co2' in tag_lower:
                    tag_unit = 'ppm'
                elif 'crack' in tag_lower or 'fiss' in tag_lower or 'width' in tag_lower:
                    tag_unit = 'mm'
                else:
                    tag_unit = 'units'
                    
            print(f"🏷️ Using tag_unit: {tag_unit} for {request.tag_name}")
            result_dict = generate_timeseries_with_llm(
                request.tag_name,
                request.text_description,
                sequence_length,
                tag_index,
                chat_llm,
                tag_unit,
                request.time_horizon
            )
            timeseries_data = result_dict.get("values", [])
            validation = result_dict.get("validation")
            generation_method = "llm"
        else:
            print(f"⚠️ No LLM available for {request.tag_name}; returning empty timeseries.")
            timeseries_data = []
            generation_method = "none"
        
        # Step 3: Generate timestamps if time horizon is specified
        timestamps = None
        if request.time_horizon:
            timestamps = generate_timestamps_for_horizon(request.time_horizon, sequence_length)
        
        # Step 4: Prepare response
        response_data = {
            "status": "success",
            "message": f"Timeseries generated successfully for {request.tag_name} using {generation_method} method",
            "tag_name": request.tag_name,
            "text_description": request.text_description,
            "sequence_length": sequence_length,
            "timeseries": timeseries_data,
            "timestamps": timestamps,
            "generation_method": generation_method,
            "time_horizon": request.time_horizon.dict() if request.time_horizon else None
        }
        
        # Attach validation if available from LLM path (convert problematic values for JSON compatibility)
        if 'validation' in locals() and validation:
            print(f"🔍 DEBUG: validation dict contents: {validation}")
            print(f"🔍 DEBUG: validation dict keys and types: {[(k, type(v)) for k, v in validation.items()]}")
            
            def make_json_safe(obj):
                """Recursively convert non-JSON-serializable objects to safe alternatives."""
                if isinstance(obj, dict):
                    return {key: make_json_safe(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [make_json_safe(item) for item in obj]
                elif isinstance(obj, (bool, int, float, str)) or obj is None:
                    return obj  # These should all be JSON serializable
                else:
                    # Convert any other type to string
                    print(f"🔍 DEBUG: Converting non-JSON-safe type {type(obj)} to string: {obj}")
                    return str(obj)
            
            response_data["validation"] = make_json_safe(validation)
        
        print(f"Returning timeseries response for {request.tag_name} with method: {generation_method}")
        return JSONResponse(response_data)
        
    except Exception as e:
        print(f"Error in generate_single_timeseries for {request.tag_name}: {traceback.format_exc()}")
        return handle_api_error("generate_single_timeseries", e)


def handle_aggregate_timeseries_generation(request: AggregateTimeSeriesRequest, bridge_text2ts_available: bool) -> JSONResponse:
    """Generate multiple time series data for different tags based on a text description."""
    try:
        print(f"Aggregate generation started - bridge_text2ts_available: {bridge_text2ts_available}")
        # Step 1: Try LLM-based generation (highest priority)
        llm_available = False
        chat_llm = None
        # Check if we can use LLM (either full BRIDGE ChatLLM or fallback)
        if bridge_text2ts_available:
            try:
                from BRIDGE.llm_agents.llm import ChatLLM
                # Get the model name from the request
                model_name = getattr(request, 'model_name', 'gpt-3.5-turbo')
                # Use the requested model directly - no special handling for GPT-4o
                print(f"Attempting to use model: {model_name}")
                
                chat_llm = ChatLLM(
                    model_name=model_name,
                    temperature=getattr(request, 'temperature', 0.7)
                )
                llm_available = True
                print(f"Using full BRIDGE ChatLLM with model {model_name}")
            except (ImportError, Exception) as e:
                print(f"Full BRIDGE ChatLLM not available: {e}")
                # Try fallback ChatLLM (still treat as LLM available)
                try:
                    model_name = getattr(request, 'model_name', 'gpt-4o')
                    print(f"Using fallback FallbackChatLLM model {model_name}")
                    chat_llm = FallbackChatLLM(
                        model_name=model_name,
                        temperature=getattr(request, 'temperature', 0.7)
                    )
                    llm_available = True
                    print("✅ FallbackChatLLM ready; proceeding with LLM-enhanced generation")
                except Exception as e2:
                    print(f"Fallback ChatLLM failed: {e2}")
        
        # Step 2: Generate tag names with units using the best available method
        tag_details = []  # Will store tag info including units
        
        if llm_available and chat_llm:
            print("Generating enhanced tags with units using LLM")
            generated_tags, tag_details = generate_tag_names_with_llm(
                request.text_description, 
                request.num_tags, 
                chat_llm
            )
            tag_generation_method = "llm_enhanced"
        else:
            print("Generating tags with keyword mapping")
            generated_tags = generate_tag_names_from_description(
                request.text_description, 
                request.num_tags,
                chat_llm
            )
            # Create basic tag details for fallback
            tag_details = [{'tag': tag, 'unit': 'units', 'description': f'{tag} sensor'} for tag in generated_tags]
            tag_generation_method = "keyword"
        
        print(f"Generated tags with details: {[(td['tag'], td['unit']) for td in tag_details]}")
        
        # Step 3: Generate timeseries data using the best available method
        generated_timeseries = {}
        # Initialize diagnostics map for per-tag validations
        per_tag_validation = {}

        if llm_available and chat_llm:
            print("Generating timeseries with LLM workflow (no synthetic fallback)")
            for i, tag_detail in enumerate(tag_details):
                tag_name = tag_detail['tag']
                tag_unit = tag_detail['unit']
                result_dict = generate_timeseries_with_llm(
                    tag_name,
                    request.text_description,
                    request.sequence_length,
                    i,
                    chat_llm,
                    tag_unit,
                    request.time_horizon
                )
                generated_timeseries[tag_name] = result_dict.get("values", [])
                per_tag_validation[tag_name] = result_dict.get("validation")
            generation_method = "llm"
            status_message = "Time series generated using LLM workflow."
        else:
            print("⚠️ No LLM available; returning empty timeseries for all tags.")
            for tag_detail in tag_details:
                generated_timeseries[tag_detail['tag']] = []
            generation_method = "none"
            status_message = "LLM unavailable; empty timeseries returned for all tags."
        
        # Step 4: Prepare enhanced response with tag details and generation information
        response_data = {
            "status": "success",
            "message": status_message,
            "text_description": request.text_description,
            "tags": generated_tags,  # Keep for backwards compatibility
            "tag_details": tag_details,  # Enhanced tag information with units
            "sequence_length": request.sequence_length,
            "num_tags": request.num_tags,
            "generated_timeseries": generated_timeseries,
            "metadata": {
                "generation_method": generation_method,
                "tag_generation_method": tag_generation_method,
                "llm_available": llm_available,
                "bridge_available": bridge_text2ts_available,
                "workflow_steps": [
                    "1. Generate tag names with units based on scenario",
                    "2. Generate timeseries data considering tag, units, and scenario",
                    "3. Validate output alignment with original scenario"
                ]
            },
            "validations": per_tag_validation,
        }
        
        # Add enhanced notes based on generation method
        if generation_method == "llm":
            response_data["note"] = "🤖 Generated using LLM; no synthetic post-processing applied"
            response_data["generation_quality"] = "LLM"
        elif generation_method == "none":
            response_data["note"] = "⚠️ LLM unavailable; empty timeseries returned (no mock data)"
            response_data["generation_quality"] = "none"
        
        print(f"Returning response with method: {generation_method}")
        return JSONResponse(response_data)
        
    except Exception as e:
        print(f"Error in aggregate_timeseries_generation: {traceback.format_exc()}")
        return handle_api_error("aggregate_timeseries_generation", e)


def refine_scenario_prompt(scenario: str, sequence_length: int = 168) -> str:
    """
    Use Azure OpenAI to rewrite a user's scenario prompt into an explicit, LLM-friendly prompt for timeseries generation.
    """
    try:
        import openai
        # Set up Azure OpenAI config from environment
        openai.api_type = "azure"
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        openai.api_base = os.environ.get('OPENAI_API_BASE', 'https://oai-shared-02.openai.azure.com/')
        openai.api_version = os.environ.get('OPENAI_API_VERSION', '2023-05-15')
        deployment = os.environ.get('OPENAI_DEPLOYMENT_NAME', 'gpt-4o')

        system_prompt, user_prompt = prompt_manager.get_scenario_refinement_prompts(scenario, sequence_length)
        response = openai.ChatCompletion.create(
            deployment_id=deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_completion_tokens=512
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Azure OpenAI refine_scenario_prompt fallback] {e}")
        # Fallback to the prompt manager's fallback prompt
        return prompt_manager.get_fallback_scenario_prompt(scenario, sequence_length)