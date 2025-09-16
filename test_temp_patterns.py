# Test the enhanced 24-hour temperature pattern generation
import sys
import os
sys.path.append("TimeCraft.Api/TimeCraft.Api")
from api.timeseries_handlers import generate_timeseries_with_tag
import asyncio
from models import TimeHorizon

async def test_temperature():
    time_horizon = TimeHorizon(period=1, unit='days')
    tag_name = 'Temp_Outside'
    scenario = 'Monitoring outdoor temperature at a residential location during a typical summer day'
    
    result = await generate_timeseries_with_tag(
        tag_name=tag_name,
        time_horizon=time_horizon, 
        scenario_context=scenario,
        user_prompt='Generate realistic 24-hour outdoor temperature data'
    )
    
    if result and 'values' in result:
        values = result['values']
        print(f'Generated {len(values)} temperature values:')
        
        # Show first 12 hours to check for smooth progression
        for i in range(min(12, len(values))):
            hour = i
            temp = values[i]
            print(f'Hour {hour:2d}: {temp:.1f}°C')
            
        print('\n--- Pattern Analysis ---')
        # Check for oscillations (multiple direction changes)
        direction_changes = 0
        prev_direction = None
        
        for i in range(1, len(values)):
            current_direction = 'up' if values[i] > values[i-1] else 'down'
            if prev_direction and current_direction != prev_direction:
                direction_changes += 1
            prev_direction = current_direction
            
        print(f'Direction changes: {direction_changes} (should be 1-2 for smooth daily curve)')
        print(f'Min temp: {min(values):.1f}°C')
        print(f'Max temp: {max(values):.1f}°C')
        
        # Find peak hour
        peak_hour = values.index(max(values))
        print(f'Peak at hour {peak_hour} (should be around 12-16 for afternoon)')
        
        # Check for sawtooth pattern (consecutive ups and downs)
        sawtooth_count = 0
        for i in range(2, len(values)):
            if ((values[i-2] < values[i-1] > values[i]) or 
                (values[i-2] > values[i-1] < values[i])):
                sawtooth_count += 1
        
        print(f'Sawtooth patterns: {sawtooth_count} (should be 0-1 for smooth curve)')
        
        if direction_changes <= 2 and sawtooth_count <= 1:
            print('✅ SUCCESS: Generated smooth daily temperature curve!')
        else:
            print('❌ FAILED: Still showing oscillating/sawtooth patterns')
    else:
        print('Failed to generate temperature data')

if __name__ == "__main__":
    asyncio.run(test_temperature())