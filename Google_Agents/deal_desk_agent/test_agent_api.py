"""
Test script to determine the correct Google ADK Agent API
"""
import os
import sys
from dotenv import load_dotenv

# Setup path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

load_dotenv()

# Import the agent
from agent import root_agent

# Test what methods are available
print("=" * 60)
print("Google ADK Agent API Inspection")
print("=" * 60)
print(f"\nAgent name: {root_agent.name}")
print(f"Agent type: {type(root_agent)}")
print(f"\nAvailable methods:")

# List all public methods
for attr in dir(root_agent):
    if not attr.startswith('_'):
        attr_value = getattr(root_agent, attr)
        if callable(attr_value):
            print(f"  - {attr}()")
        else:
            print(f"  - {attr} = {type(attr_value).__name__}")

# Try to find the correct invocation method
print("\n" + "=" * 60)
print("Testing invocation methods:")
print("=" * 60)

test_message = "Calculate quote with base MRC $1200, base NRC $800, MSA discount 15%, 36 month term"

# Test 1: send_message
if hasattr(root_agent, 'send_message'):
    print("\n✓ Agent has 'send_message' method")
    try:
        import inspect
        sig = inspect.signature(root_agent.send_message)
        print(f"  Signature: send_message{sig}")
    except Exception as e:
        print(f"  Could not get signature: {e}")
else:
    print("\n✗ Agent does NOT have 'send_message' method")

# Test 2: run
if hasattr(root_agent, 'run'):
    print("\n✓ Agent has 'run' method")
    try:
        import inspect
        sig = inspect.signature(root_agent.run)
        print(f"  Signature: run{sig}")
    except Exception as e:
        print(f"  Could not get signature: {e}")
else:
    print("\n✗ Agent does NOT have 'run' method")

# Test 3: __call__
if callable(root_agent):
    print("\n✓ Agent is callable (has __call__)")
    try:
        import inspect
        sig = inspect.signature(root_agent.__call__)
        print(f"  Signature: __call__{sig}")
    except Exception as e:
        print(f"  Could not get signature: {e}")
else:
    print("\n✗ Agent is NOT callable")

# Test 4: Other common methods
for method_name in ['execute', 'process', 'chat', 'invoke', 'generate']:
    if hasattr(root_agent, method_name):
        print(f"\n✓ Agent has '{method_name}' method")
        try:
            import inspect
            method = getattr(root_agent, method_name)
            sig = inspect.signature(method)
            print(f"  Signature: {method_name}{sig}")
        except Exception as e:
            print(f"  Could not get signature: {e}")

print("\n" + "=" * 60)

# Made with Bob
