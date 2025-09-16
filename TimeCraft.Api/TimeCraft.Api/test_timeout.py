from api.timeseries_handlers import FallbackChatLLM
import time

def test_timeout_configuration():
    """Test timeout configuration with a simple prompt"""
    print("🧪 Testing Azure OpenAI timeout configuration...")
    print("=" * 60)
    
    # Create LLM with shorter timeout for testing
    llm = FallbackChatLLM(model_name="gpt-4o", temperature=0.1)
    
    # Simple test prompt that should respond quickly
    test_prompt = """Generate exactly 10 comma-separated numbers between 1 and 100.
    
Example format: 23, 45, 67, 12, 89, 34, 56, 78, 91, 15

Only return the numbers, no explanation."""
    
    print(f"🚀 Testing with simple prompt (timeout: {llm.timeout}s)...")
    start_time = time.time()
    
    try:
        result = llm.generate(test_prompt)
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ API call completed in {duration:.2f} seconds")
        print(f"📊 Result: {result}")
        
        if "," in result:
            values = [val.strip() for val in result.split(",")]
            print(f"✅ Successfully parsed {len(values)} values")
        else:
            print("⚠️ Result not in expected comma-separated format")
            
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ API call failed after {duration:.2f} seconds")
        print(f"   Error: {e}")
        print(f"   Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_timeout_configuration()