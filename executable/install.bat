@echo off
REM Installation script for DIGGS Data Processing Manager
REM This script sets up the application and creates desktop shortcuts

echo ========================================
echo DIGGS Data Processing Manager Installer
echo ========================================
echo.

REM Get the current directory
set "APP_DIR=%~dp0"
set "APP_EXE=%APP_DIR%DIGGS_Processor_Manager.exe"

REM Check if executable exists
if not exist "%APP_EXE%" (
    echo ERROR: DIGGS_Processor_Manager.exe not found in current directory
    echo Please make sure you're running this script from the application folder
    echo or build the executable first using build_executable.bat
    pause
    exit /b 1
)

echo Found DIGGS Processor Manager executable
echo Location: %APP_EXE%
echo.

REM Create desktop shortcut
echo Creating desktop shortcut...
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\DIGGS Data Processing Manager.lnk"

REM Use PowerShell to create shortcut
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%APP_EXE%'; $Shortcut.WorkingDirectory = '%APP_DIR%'; $Shortcut.Description = 'DIGGS Data Processing Manager - Geotechnical data processing with Abstract Factory pattern'; $Shortcut.Save()}"

if exist "%SHORTCUT%" (
    echo Desktop shortcut created successfully: %SHORTCUT%
) else (
    echo Warning: Could not create desktop shortcut
)

echo.
REM Create start menu shortcut
echo Creating Start Menu shortcut...
set "STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
set "STARTMENU_SHORTCUT=%STARTMENU%\DIGGS Data Processing Manager.lnk"

powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTMENU_SHORTCUT%'); $Shortcut.TargetPath = '%APP_EXE%'; $Shortcut.WorkingDirectory = '%APP_DIR%'; $Shortcut.Description = 'DIGGS Data Processing Manager - Geotechnical data processing'; $Shortcut.Save()}"

if exist "%STARTMENU_SHORTCUT%" (
    echo Start Menu shortcut created successfully
) else (
    echo Warning: Could not create Start Menu shortcut
)

echo.
echo ========================================
echo Installation completed!
echo ========================================
echo.
echo The DIGGS Data Processing Manager has been installed successfully.
echo.
echo You can now:
echo   • Launch from desktop shortcut: DIGGS Data Processing Manager
echo   • Launch from Start Menu: DIGGS Data Processing Manager  
echo   • Run directly: %APP_EXE%
echo.
echo Application features:
echo   • Excel template generation
echo   • Excel to SQLite conversion
echo   • SQLite to DIGGS 2.6 XML export
echo   • DIGGS XML to SQLite import
echo   • Built with Abstract Factory design pattern
echo.
pause