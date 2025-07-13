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
        "pandas", "openpyxl", "threading", "webbrowser",
        "pathlib", "os", "sys"
    ],
    "include_files": [
        # Include assets directory
        (str(assets_dir), "assets"),
        # Include source modules
        (str(src_dir / "processor_interfaces.py"), "src/processor_interfaces.py"),
        (str(src_dir / "processor_factories.py"), "src/processor_factories.py"),
        (str(src_dir / "excel_processor.py"), "src/excel_processor.py"),
        (str(src_dir / "diggs_processor.py"), "src/diggs_processor.py"),
        (str(src_dir / "excel_to_sqlite_converter.py"), "src/excel_to_sqlite_converter.py"),
        (str(src_dir / "sqlite_to_diggs_converter.py"), "src/sqlite_to_diggs_converter.py"),
        (str(src_dir / "diggs_to_sqlite_importer.py"), "src/diggs_to_sqlite_importer.py"),
        (str(src_dir / "excel_template_generator.py"), "src/excel_template_generator.py"),
    ],
    "excludes": [
        # Exclude unnecessary packages to reduce size
        "numpy", "matplotlib", "scipy", "PIL", "PyQt5", "PyQt6",
        "tkinter.test", "test", "unittest", "doctest"
    ],
    "optimize": 2,  # Optimize bytecode
    "include_msvcrt": True,  # Include Visual C++ runtime on Windows
}

# Base for Windows GUI application (no console window)
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Define the main executable
executables = [
    Executable(
        script="diggs_processor_gui.py",
        base=base,
        target_name="DIGGS_Processor_Manager.exe",
        icon=None,  # You can add an icon file here: icon="icon.ico"
        shortcut_name="DIGGS Data Processing Manager",
        shortcut_dir="DesktopFolder",
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