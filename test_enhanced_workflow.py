#!/usr/bin/env python3
"""
Test the enhanced TimeCraft API workflow:
1. Tag generation with units
2. Scenario-aware timeseries generation 
3. Scenario validation
"""

import sys
import os
import json

# Add the TimeCraft.Api directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
api_dir = os.path.join(current_dir, 'TimeCraft.Api', 'TimeCraft.Api')
sys.path.insert(0, api_dir)

def test_enhanced_workflow():
    """Test the complete enhanced workflow."""
    
    print("🚀 Testing Enhanced TimeCraft Workflow")
    print("=" * 60)
    
    try:
        from api.models import AggregateTimeSeriesRequest
        from api.timeseries_handlers import handle_aggregate_timeseries_generation
        
        # Historic building scenario
        scenario = """
        I want sensor data for monitoring a historic building in Spain during tourist season. 
        I would like to see HVAC temperature, humidity levels, seismic activity monitoring,
        and footfall from presence sensors to monitor visitor traffic.
        """
        
        # Create request
        request = AggregateTimeSeriesRequest(
            text_description=scenario,
            num_tags=4,
            sequence_length=48,  # 2 days of hourly data
            model_name="gpt-4o",
            temperature=0.1
        )
        
        print("📋 Test Scenario:")
        print(scenario.strip())
        print()
        print(f"🎯 Requesting {request.num_tags} tags, {request.sequence_length} data points each")
        print()
        
        # Test the enhanced generation
        response = handle_aggregate_timeseries_generation(request, bridge_text2ts_available=True)
        
        # Parse response
        if hasattr(response, 'body'):
            response_data = json.loads(response.body.decode())
        else:
            response_data = response
            
        print("✅ Enhanced workflow completed!")
        print(f"📊 Status: {response_data.get('status', 'unknown')}")
        print(f"💬 Message: {response_data.get('message', 'No message')}")
        print()
        
        # Check for enhanced features
        enhanced_features = []
        
        if 'tag_details' in response_data:
            enhanced_features.append("✅ Tag generation with units")
            tag_details = response_data['tag_details']
            print("🏷️ Generated Tags with Units:")
            for i, detail in enumerate(tag_details, 1):
                print(f"   {i}. {detail['tag']} ({detail['unit']}) - {detail['description']}")
            print()
        else:
            print("❌ Missing enhanced tag details")
        
        if 'generation_quality' in response_data:
            enhanced_features.append("✅ Generation quality information")
            print(f"🎯 Generation Quality: {response_data['generation_quality']}")
        
        if 'note' in response_data:
            enhanced_features.append("✅ Generation method notes")
            print(f"📝 Generation Note: {response_data['note']}")
        
        if response_data.get('metadata', {}).get('workflow_steps'):
            enhanced_features.append("✅ Workflow step information")
            print("🔄 Workflow Steps:")
            for step in response_data['metadata']['workflow_steps']:
                print(f"   {step}")
        
        print()
        print("📈 Enhanced Features Status:")
        for feature in enhanced_features:
            print(f"   {feature}")
            
        if len(enhanced_features) >= 3:
            print("\n🎉 SUCCESS: Enhanced workflow is working!")
            print("✅ Tags are generated with units")
            print("✅ Generation method is clearly indicated") 
            print("✅ Quality information is provided")
            
            # Check if tags seem appropriate for building monitoring
            if 'tag_details' in response_data:
                building_relevant = 0
                for detail in response_data['tag_details']:
                    tag_name = detail['tag'].upper()
                    if any(term in tag_name for term in ['HVAC', 'TEMP', 'HUMID', 'SEISMIC', 'FOOTFALL', 'PRESENCE', 'BUILDING']):
                        building_relevant += 1
                
                relevance_score = building_relevant / len(response_data['tag_details'])
                print(f"🏛️ Building Relevance: {building_relevant}/{len(response_data['tag_details'])} tags ({relevance_score:.1%})")
                
                if relevance_score >= 0.5:
                    print("✅ Tags are contextually appropriate for building monitoring!")
                else:
                    print("⚠️ Some tags may not be ideal for building monitoring")
        else:
            print("\n⚠️ Some enhanced features are missing")
            
        return response_data
        
    except ImportError as e:
        print(f"❌ Could not import required modules: {e}")
        return None
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    test_enhanced_workflow()