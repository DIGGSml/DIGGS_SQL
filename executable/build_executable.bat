@echo off
REM Build script for DIGGS Data Processing Manager executable
REM This script installs dependencies and builds the executable

echo ========================================
echo DIGGS Data Processing Manager Builder
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or newer from https://python.org
    pause
    exit /b 1
)

echo Installing required packages...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

echo.
echo Building executable...
python setup.py build

if errorlevel 1 (
    echo ERROR: Failed to build executable
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo The executable can be found in the 'build' directory.
echo Look for 'DIGGS_Processor_Manager.exe' in the build folder.
echo.
echo You can now distribute the entire build folder to other computers
echo without requiring Python to be installed.
echo.
pause