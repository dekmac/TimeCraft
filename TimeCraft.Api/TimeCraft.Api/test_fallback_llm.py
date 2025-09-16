from api.timeseries_handlers import FallbackChatLLM

# Test the enhanced FallbackChatLLM
llm = FallbackChatLLM()

# Test with a detailed prompt similar to what we generate
test_prompt = '''
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

print('🧪 Testing enhanced FallbackChatLLM with detailed prompt...')
result = llm.generate(test_prompt)
print(f'📊 Result length: {len(result)}')
if result and "," in result:
    data_points = len(result.split(","))
    print(f'📈 Data points: {data_points}')
else:
    print('📈 Data points: No comma-separated data')
print(f'🎯 First 100 chars: {result[:100] if result else "No result"}...')