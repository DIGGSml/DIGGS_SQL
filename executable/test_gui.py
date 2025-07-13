#!/usr/bin/env python3
"""
Test script for DIGGS Processor GUI

This script tests the GUI components and factory functionality
without launching the actual GUI window.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import tkinter as tk
        print("[OK] tkinter imported successfully")
    except ImportError as e:
        print(f"[FAIL] tkinter import failed: {e}")
        return False
    
    try:
        from processor_factories import DataProcessorFactoryManager
        print("[OK] DataProcessorFactoryManager imported successfully")
    except ImportError as e:
        print(f"[FAIL] DataProcessorFactoryManager import failed: {e}")
        return False
    
    try:
        import pandas
        print("[OK] pandas imported successfully")
    except ImportError as e:
        print(f"[FAIL] pandas import failed: {e}")
        return False
    
    try:
        import openpyxl
        print("[OK] openpyxl imported successfully")
    except ImportError as e:
        print(f"[FAIL] openpyxl import failed: {e}")
        return False
    
    return True

def test_factory_system():
    """Test the abstract factory system"""
    print("\nTesting factory system...")
    
    try:
        from processor_factories import DataProcessorFactoryManager
        
        # Create factory manager
        manager = DataProcessorFactoryManager()
        print("[OK] Factory manager created successfully")
        
        # Test factory capabilities
        factories = manager.get_available_factories()
        print(f"[OK] Available factories: {list(factories.keys())}")
        
        # Test processor creation
        excel_converter = manager.create_processor('excel', 'converter')
        print("[OK] Excel converter created successfully")
        
        diggs_converter = manager.create_processor('diggs', 'converter')
        print("[OK] DIGGS converter created successfully")
        
        template_generator = manager.create_processor('excel', 'template')
        print("[OK] Template generator created successfully")
        
        diggs_importer = manager.create_processor('diggs', 'importer')
        print("[OK] DIGGS importer created successfully")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Factory system test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files are present"""
    print("\nTesting file structure...")
    
    required_files = [
        "src/processor_interfaces.py",
        "src/processor_factories.py", 
        "src/excel_processor.py",
        "src/diggs_processor.py",
        "src/excel_to_sqlite_converter.py",
        "src/sqlite_to_diggs_converter.py",
        "src/diggs_to_sqlite_importer.py",
        "src/excel_template_generator.py",
        "assets/DIGGS sqlite.py"
    ]
    
    all_present = True
    for file_path in required_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[FAIL] {file_path} - MISSING")
            all_present = False
    
    return all_present

def test_gui_components():
    """Test GUI component creation without showing window"""
    print("\nTesting GUI components...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # Create root window (but don't show it)
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test basic widget creation
        frame = ttk.Frame(root)
        label = ttk.Label(frame, text="Test")
        button = ttk.Button(frame, text="Test Button")
        entry = ttk.Entry(frame)
        
        print("[OK] Basic widgets created successfully")
        
        # Test notebook widget
        notebook = ttk.Notebook(frame)
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Test Tab")
        
        print("[OK] Notebook widget created successfully")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"[FAIL] GUI component test failed: {e}")
        return False

def test_template_generation():
    """Test template generation functionality"""
    print("\nTesting template generation...")
    
    try:
        from processor_factories import DataProcessorFactoryManager
        
        manager = DataProcessorFactoryManager()
        generator = manager.create_processor('excel', 'template')
        
        # Test template generation (to a test file)
        test_output = current_dir / "test_template.xlsx"
        success = generator.generate(str(test_output), "blank")
        
        if success and test_output.exists():
            print("[OK] Template generation successful")
            # Clean up test file
            test_output.unlink()
            return True
        else:
            print("[FAIL] Template generation failed")
            return False
            
    except Exception as e:
        print(f"[FAIL] Template generation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("DIGGS Processor GUI Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_file_structure,
        test_factory_system,
        test_gui_components,
        test_template_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"[FAIL] Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed! The GUI system is ready for use.")
        print("\nYou can now:")
        print("  • Run the GUI: python diggs_processor_gui.py")
        print("  • Build executable: python setup.py build")
        print("  • Install requirements: pip install -r requirements.txt")
    else:
        print("[FAIL] Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())