#!/usr/bin/env python3
"""
Setup script for creating DIGGS Data Processing Manager executable

This script uses cx_Freeze to create a standalone executable that includes
all dependencies and can be distributed without requiring Python installation.

Requirements:
    pip install cx_Freeze

Usage:
    python setup.py build
"""

import sys
import os
from pathlib import Path
from cx_Freeze import setup, Executable

# Get current directory
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
assets_dir = current_dir / "assets"

# Define build options
build_exe_options = {
    "packages": [
        "tkinter", "sqlite3", "xml", "uuid", "datetime", 
        "pandas", "numpy", "openpyxl", "threading", "webbrowser",
        "pathlib", "os", "sys", "matplotlib", "PIL"
    ],
    "include_files": [
        # Include assets directory
        (str(assets_dir), "assets"),
        # Include source modules in root for easier import
        (str(src_dir / "processor_interfaces.py"), "processor_interfaces.py"),
        (str(src_dir / "processor_factories.py"), "processor_factories.py"),
        (str(src_dir / "excel_processor.py"), "excel_processor.py"),
        (str(src_dir / "diggs_processor.py"), "diggs_processor.py"),
        (str(src_dir / "excel_to_sqlite_converter.py"), "excel_to_sqlite_converter.py"),
        (str(src_dir / "sqlite_to_diggs_converter.py"), "sqlite_to_diggs_converter.py"),
        (str(src_dir / "diggs_to_sqlite_importer.py"), "diggs_to_sqlite_importer.py"),
        (str(src_dir / "excel_template_generator.py"), "excel_template_generator.py"),
        (str(src_dir / "visualization_processor.py"), "visualization_processor.py"),
        # Also include in src subdirectory for compatibility
        (str(src_dir), "src"),
    ],
    "excludes": [
        # Exclude unnecessary packages to reduce size
        "scipy", "PyQt5", "PyQt6", "seaborn", "ipywidgets", "jupyter_client",
        "zmq", "pyzmq", "ipykernel", "jupyter_core",
        "tkinter.test", "test", "unittest", "doctest"
    ],
    "optimize": 2,  # Optimize bytecode
}

# Base for Windows GUI application (no console window)
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Define the main executable
executables = [
    Executable(
        script="diggs_processor_gui_final.py",
        base=base,
        target_name="DIGGS_Processor_Manager.exe",
        icon=None,  # You can add an icon file here: icon="icon.ico"
        shortcut_name="DIGGS Data Processing Manager",
        shortcut_dir="DesktopFolder",
    ),
    # Add test executable for debugging
    Executable(
        script="minimal_test.py",
        base=None,  # Console app for debugging
        target_name="minimal_test.exe",
    )
]

# Setup configuration
setup(
    name="DIGGS Data Processing Manager",
    version="1.0.0",
    description="Professional geotechnical data processing with DIGGS 2.6 support",
    long_description="""
    DIGGS Data Processing Manager provides a complete workflow for geotechnical 
    data processing using the Abstract Factory design pattern:
    
    • Excel Template Generation
    • Excel to SQLite Conversion
    • SQLite to DIGGS 2.6 XML Export
    • DIGGS XML to SQLite Import
    
    Built for the Geo Institute as an open source solution for standardized
    geotechnical data management and interchange.
    """,
    author="Geo Institute",
    author_email="support@geoinstitute.org",
    url="https://github.com/geoinstitute/DIGGS_SQL",
    options={"build_exe": build_exe_options},
    executables=executables,
    requires=["pandas", "openpyxl"],
)