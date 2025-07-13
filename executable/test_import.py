#!/usr/bin/env python3
"""
Simple import test for debugging executable issues
"""

import sys
import os
from pathlib import Path

print("Python executable:", sys.executable)
print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Script location:", __file__)

# Show sys.path
print("\nPython path:")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")

# Test if we're in frozen environment
print(f"\nRunning as executable: {hasattr(sys, 'frozen')}")

# Test directory structure
current_dir = Path(__file__).parent
print(f"\nCurrent directory: {current_dir}")
print(f"Directory contents:")
for item in current_dir.iterdir():
    print(f"  {item.name} ({'DIR' if item.is_dir() else 'FILE'})")

# Test src directory
src_dir = current_dir / "src"
if src_dir.exists():
    print(f"\nSrc directory contents:")
    for item in src_dir.iterdir():
        print(f"  {item.name}")
else:
    print(f"\nSrc directory does not exist: {src_dir}")

# Test module imports
print("\n=== Testing Imports ===")

# Add paths
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(src_dir))

try:
    import processor_interfaces
    print("✓ processor_interfaces imported successfully")
except ImportError as e:
    print(f"✗ processor_interfaces import failed: {e}")

try:
    import processor_factories
    print("✓ processor_factories imported successfully")
except ImportError as e:
    print(f"✗ processor_factories import failed: {e}")

try:
    from processor_factories import DataProcessorFactoryManager
    manager = DataProcessorFactoryManager()
    print("✓ DataProcessorFactoryManager created successfully")
except Exception as e:
    print(f"✗ DataProcessorFactoryManager creation failed: {e}")

print("\n=== Import Test Complete ===")
input("Press Enter to exit...")