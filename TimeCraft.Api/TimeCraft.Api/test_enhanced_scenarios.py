from api.timeseries_handlers import FallbackChatLLM

def test_different_scenarios():
    """Test FallbackChatLLM with different scenarios and time horizons"""
    llm = FallbackChatLLM()
    
    test_cases = [
        {
            'name': '24 Hours Bridge Strain',
            'prompt': '''
You are an expert in structural health monitoring and time series data generation.

SCENARIO CONTEXT: Monitoring a bridge during heavy traffic loading
STRUCTURE TYPE: Bridge  
SENSOR TYPE: Strain gauge monitoring
TIME HORIZON: 24 hours with 288 data points (5-minute intervals)

Generate realistic strain gauge readings that reflect:
- Bridge response to traffic loading patterns
- Daily traffic cycles with peak and off-peak periods
- Realistic strain values in microstrains (µε)
- 288 data points representing 5-minute sampling intervals over 24 hours

Mathematical constraint: Generate exactly 288 numerical values to match the 5-minute sampling frequency over 24 hours.
'''
        },
        {
            'name': '7 Days Vibration Normal',
            'prompt': '''
You are an expert in structural health monitoring and time series data generation.

SCENARIO CONTEXT: Normal operational monitoring of a building
STRUCTURE TYPE: Building  
SENSOR TYPE: Vibration monitoring
TIME HORIZON: 7 days with 168 data points (hourly intervals)

Generate realistic vibration readings that reflect:
- Normal building vibrations
- Daily patterns with reduced activity at night
- Weekly patterns with different weekday vs weekend activity
- 168 data points representing hourly sampling over 7 days

Mathematical constraint: Generate exactly 168 numerical values to match the hourly sampling frequency over 7 days.
'''
        },
        {
            'name': '30 Days Settlement Monitoring',
            'prompt': '''
You are an expert in structural health monitoring and time series data generation.

SCENARIO CONTEXT: Long-term foundation settlement monitoring after construction
STRUCTURE TYPE: Building  
SENSOR TYPE: Displacement monitoring
TIME HORIZON: 30 days with 240 data points (3-hour intervals)

Generate realistic settlement displacement readings that reflect:
- Gradual foundation settlement over time
- Logarithmic settlement curve typical of soil consolidation
- Small thermal effects and measurement noise
- 240 data points representing 3-hour sampling over 30 days

Mathematical constraint: Generate exactly 240 numerical values to match the 3-hour sampling frequency over 30 days.
'''
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print("=" * 60)
        
        result = llm.generate(test_case['prompt'])
        
        if result:
            # Clean the result by removing brackets and extracting numbers
            cleaned_result = result.strip()
            if cleaned_result.startswith('[') and cleaned_result.endswith(']'):
                cleaned_result = cleaned_result[1:-1]
            
            if "," in cleaned_result:
                try:
                    # Split and clean values
                    raw_values = cleaned_result.split(",")
                    values = []
                    for val in raw_values:
                        clean_val = val.strip()
                        try:
                            values.append(float(clean_val))
                        except ValueError:
                            continue
                    
                    if values:
                        data_points = len(values)
                        first_5 = values[:5]
                        
                        print(f"✅ Generated {data_points} data points")
                        print(f"📊 First 5 values: {first_5}")
                        print(f"📈 Sample range: {min(values):.4f} to {max(values):.4f}")
                    else:
                        print("❌ No valid numerical values found")
                        print(f"📝 Raw result: {result[:200]}...")
                except Exception as e:
                    print(f"❌ Error parsing values: {e}")
                    print(f"📝 Raw result: {result[:200]}...")
            else:
                print("❌ No comma-separated data found")
                print(f"📝 Result: {result[:200]}...")
        else:
            print("❌ No result returned")

if __name__ == "__main__":
    print("🎯 Testing Enhanced FallbackChatLLM with Scenario Awareness")
    print("=" * 70)
    test_different_scenarios()