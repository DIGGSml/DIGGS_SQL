@echo off
REM Error Testing Script for DIGGS Processor Manager
REM This batch file runs the executable and captures all output and errors

setlocal enabledelayedexpansion

echo =====================================================
echo DIGGS Processor Manager - Error Testing
echo =====================================================
echo.

REM Create logs directory
if not exist "error_logs" mkdir error_logs

REM Generate timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do set datestr=%%c%%a%%b
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set timestr=%%a%%b
set timestamp=%datestr%_%timestr%

REM Find the executable
set "exe_path="
for /d %%d in (build\exe.win-amd64-*) do (
    if exist "%%d\DIGGS_Processor_Manager.exe" (
        set "exe_path=%%d\DIGGS_Processor_Manager.exe"
        echo Found executable: %%d\DIGGS_Processor_Manager.exe
    )
)

if "%exe_path%"=="" (
    echo ERROR: No DIGGS_Processor_Manager.exe found in build directories
    echo Please build the executable first using: python setup.py build
    pause
    exit /b 1
)

echo.
echo Testing executable: %exe_path%
echo Logs will be saved to: error_logs\
echo.

REM Test 1: Basic execution with timeout
echo === Test 1: Basic Execution (15 second timeout) ===
echo Running executable...

set "log_file=error_logs\execution_log_%timestamp%.txt"
set "error_file=error_logs\execution_errors_%timestamp%.txt"

echo DIGGS Processor Manager Test Log > "%log_file%"
echo Timestamp: %date% %time% >> "%log_file%"
echo Executable: %exe_path% >> "%log_file%"
echo. >> "%log_file%"

REM Run with timeout (using start and taskkill for timeout)
start /b "" "%exe_path%" > "%log_file%" 2> "%error_file%"
set exe_pid=%!

REM Wait 15 seconds then check if still running
timeout /t 15 /nobreak > nul

REM Check if process is still running (for GUI apps, this is normal)
tasklist /fi "imagename eq DIGGS_Processor_Manager.exe" | find /i "DIGGS_Processor_Manager.exe" > nul
if %errorlevel%==0 (
    echo Process is still running after 15 seconds - this is normal for GUI applications
    echo You can manually close the application window
    echo Check the log files for any startup errors
) else (
    echo Process completed or crashed
)

echo.
echo === Test 2: Checking for common errors ===

REM Check error file for common issues
if exist "%error_file%" (
    findstr /i "error traceback exception modulenotfounderror importerror" "%error_file%" > nul
    if !errorlevel!==0 (
        echo ERRORS DETECTED in %error_file%:
        echo.
        type "%error_file%"
        echo.
    ) else (
        echo No obvious errors detected in stderr
    )
) else (
    echo No error file generated
)

REM Test 3: Check if minimal test exists
echo === Test 3: Module Import Test ===
set "minimal_exe=build\exe.win-amd64-*\minimal_test.exe"
for %%f in (%minimal_exe%) do (
    if exist "%%f" (
        echo Running module import test: %%f
        "%%f" > "error_logs\import_test_%timestamp%.txt" 2>&1
        if !errorlevel!==0 (
            echo Import test completed successfully
        ) else (
            echo Import test failed - check error_logs\import_test_%timestamp%.txt
        )
    )
)

echo.
echo === Test Summary ===
echo Log files created:
if exist "%log_file%" echo   - %log_file%
if exist "%error_file%" echo   - %error_file%
if exist "error_logs\import_test_%timestamp%.txt" echo   - error_logs\import_test_%timestamp%.txt

echo.
echo === Recommendations ===
echo 1. If the GUI window opened briefly then closed, check the error logs
echo 2. If no window appeared at all, there may be missing dependencies
echo 3. If the process is still running, the GUI likely launched successfully
echo 4. Check Windows Event Viewer for additional error details if needed

echo.
echo Testing complete! Press any key to exit...
pause > nul