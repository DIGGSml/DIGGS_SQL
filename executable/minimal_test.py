#!/usr/bin/env python3
"""
Minimal test to diagnose import issue
"""

import sys
import os
from pathlib import Path

print("=== Minimal Import Test ===")
print(f"Python executable: {sys.executable}")
print(f"Script location: {__file__}")
print(f"Current directory: {os.getcwd()}")
print(f"Frozen: {hasattr(sys, 'frozen')}")

# Add current directory to path
if hasattr(sys, 'frozen'):
    # For cx_Freeze executable, modules are in same dir as executable
    current_dir = os.path.dirname(os.path.abspath(sys.executable))
else:
    # For development
    current_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, current_dir)
print(f"Added to path: {current_dir}")

# List available modules
try:
    py_files = [f for f in os.listdir(current_dir) if f.endswith('.py')]
    print(f"Available .py files: {py_files[:5]}")
except Exception as e:
    print(f"Could not list files: {e}")
print("Python path:")
for p in sys.path[:5]:  # Show first 5 paths
    print(f"  {p}")

# Test imports one by one
try:
    print("\n=== Testing Imports ===")
    
    print("1. Testing processor_interfaces...")
    import processor_interfaces
    print("   ✓ processor_interfaces imported")
    
    print("2. Testing processor_factories...")
    import processor_factories
    print("   ✓ processor_factories imported")
    
    print("3. Testing DataProcessorFactoryManager...")
    from processor_factories import DataProcessorFactoryManager
    print("   ✓ DataProcessorFactoryManager imported")
    
    print("4. Creating factory manager...")
    manager = DataProcessorFactoryManager()
    print("   ✓ Factory manager created")
    
    print("5. Testing factory capabilities...")
    factories = manager.get_available_factories()
    print(f"   ✓ Available factories: {list(factories.keys())}")
    
    print("\n🎉 ALL IMPORTS SUCCESSFUL!")
    
except Exception as e:
    print(f"\n❌ IMPORT FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
if hasattr(sys, 'frozen'):
    input("Press Enter to exit...")  # Keep window open if running as exe