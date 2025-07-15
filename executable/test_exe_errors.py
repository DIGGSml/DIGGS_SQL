#!/usr/bin/env python3
"""
Error Logging Script for DIGGS Processor Manager Executable

This script runs the DIGGS_Processor_Manager.exe and captures all errors,
exceptions, and output for debugging purposes.
"""

import subprocess
import os
import sys
import datetime
from pathlib import Path
import time
import json

class ExecutableErrorLogger:
    """Comprehensive error logging for executable testing"""
    
    def __init__(self, exe_path=None):
        self.script_dir = Path(__file__).parent
        
        # Auto-detect executable path if not provided
        if exe_path is None:
            build_dirs = list(self.script_dir.glob("build/exe.win-amd64-*"))
            if build_dirs:
                # Use the most recent build directory (prefer 3.13 over 3.9)
                latest_build = max(build_dirs, key=lambda p: (p.name, p.stat().st_mtime))
                self.exe_path = latest_build / "DIGGS_Processor_Manager.exe"
            else:
                raise FileNotFoundError("No executable build directory found")
        else:
            self.exe_path = Path(exe_path)
        
        # Create logs directory
        self.logs_dir = self.script_dir / "error_logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Generate timestamp for log files
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"Testing executable: {self.exe_path}")
        print(f"Logs will be saved to: {self.logs_dir}")
    
    def check_executable_exists(self):
        """Verify the executable exists and is accessible"""
        if not self.exe_path.exists():
            raise FileNotFoundError(f"Executable not found: {self.exe_path}")
        
        if not self.exe_path.is_file():
            raise FileNotFoundError(f"Path is not a file: {self.exe_path}")
        
        print(f"[OK] Executable found: {self.exe_path}")
        print(f"  Size: {self.exe_path.stat().st_size:,} bytes")
        print(f"  Modified: {datetime.datetime.fromtimestamp(self.exe_path.stat().st_mtime)}")
    
    def test_minimal_execution(self, timeout=30):
        """Test basic executable launch with minimal timeout"""
        print(f"\n=== Testing Minimal Execution (timeout: {timeout}s) ===")
        
        log_file = self.logs_dir / f"minimal_test_{self.timestamp}.log"
        error_file = self.logs_dir / f"minimal_errors_{self.timestamp}.log"
        
        try:
            # Run executable with timeout
            process = subprocess.Popen(
                [str(self.exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.exe_path.parent,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )
            
            print(f"Started process PID: {process.pid}")
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
                
                # Save output to files
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== DIGGS Processor Manager Test Log ===\n")
                    f.write(f"Timestamp: {datetime.datetime.now()}\n")
                    f.write(f"Executable: {self.exe_path}\n")
                    f.write(f"Return Code: {return_code}\n")
                    f.write(f"Timeout: {timeout}s\n\n")
                    f.write("=== STDOUT ===\n")
                    f.write(stdout)
                    f.write("\n\n=== STDERR ===\n")
                    f.write(stderr)
                
                with open(error_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== Error Analysis ===\n")
                    f.write(f"Timestamp: {datetime.datetime.now()}\n")
                    f.write(f"Return Code: {return_code}\n\n")
                    
                    if return_code == 0:
                        f.write("[OK] Process completed successfully\n")
                    else:
                        f.write(f"[FAIL] Process failed with return code: {return_code}\n")
                    
                    if stderr.strip():
                        f.write("\n=== STDERR CONTENT ===\n")
                        f.write(stderr)
                        
                        # Analyze common error patterns
                        if "ModuleNotFoundError" in stderr:
                            f.write("\n[ANALYSIS] Missing Python module detected\n")
                        if "ImportError" in stderr:
                            f.write("\n[ANALYSIS] Import error detected\n")
                        if "Traceback" in stderr:
                            f.write("\n[ANALYSIS] Python traceback detected\n")
                    else:
                        f.write("\nNo errors in STDERR\n")
                
                print(f"[OK] Process completed with return code: {return_code}")
                print(f"[OK] Output saved to: {log_file}")
                print(f"[OK] Errors saved to: {error_file}")
                
                return {
                    "success": return_code == 0,
                    "return_code": return_code,
                    "stdout": stdout,
                    "stderr": stderr,
                    "log_file": str(log_file),
                    "error_file": str(error_file)
                }
                
            except subprocess.TimeoutExpired:
                process.terminate()
                print(f"[WARNING] Process timed out after {timeout} seconds")
                
                # Try to get partial output
                try:
                    stdout, stderr = process.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                
                with open(error_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== TIMEOUT ERROR ===\n")
                    f.write(f"Process timed out after {timeout} seconds\n")
                    f.write(f"This may indicate the GUI launched successfully but didn't exit\n")
                    f.write(f"Partial STDOUT:\n{stdout}\n")
                    f.write(f"Partial STDERR:\n{stderr}\n")
                
                return {
                    "success": False,
                    "return_code": "TIMEOUT",
                    "stdout": stdout,
                    "stderr": stderr,
                    "error": f"Timeout after {timeout} seconds",
                    "error_file": str(error_file)
                }
                
        except Exception as e:
            error_msg = f"Failed to start process: {e}"
            print(f"[ERROR] {error_msg}")
            
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(f"=== EXECUTION FAILURE ===\n")
                f.write(f"Error: {error_msg}\n")
                f.write(f"Exception Type: {type(e).__name__}\n")
            
            return {
                "success": False,
                "error": error_msg,
                "error_file": str(error_file)
            }
    
    def test_import_modules(self):
        """Test module imports in the executable environment"""
        print(f"\n=== Testing Module Imports ===")
        
        # Test with the minimal_test.exe if it exists
        minimal_exe = self.exe_path.parent / "minimal_test.exe"
        if minimal_exe.exists():
            print(f"Using minimal test executable: {minimal_exe}")
            return self._run_import_test(minimal_exe)
        else:
            print("No minimal test executable found, skipping import test")
            return {"success": False, "error": "No minimal test executable"}
    
    def _run_import_test(self, exe_path):
        """Run the minimal import test executable"""
        log_file = self.logs_dir / f"import_test_{self.timestamp}.log"
        
        try:
            result = subprocess.run(
                [str(exe_path)],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=exe_path.parent
            )
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== Module Import Test ===\n")
                f.write(f"Timestamp: {datetime.datetime.now()}\n")
                f.write(f"Executable: {exe_path}\n")
                f.write(f"Return Code: {result.returncode}\n\n")
                f.write("=== STDOUT ===\n")
                f.write(result.stdout)
                f.write("\n\n=== STDERR ===\n")
                f.write(result.stderr)
            
            print(f"[OK] Import test completed: {log_file}")
            
            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "log_file": str(log_file)
            }
            
        except Exception as e:
            print(f"[ERROR] Import test failed: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_summary_report(self, results):
        """Generate a comprehensive summary report"""
        report_file = self.logs_dir / f"test_summary_{self.timestamp}.json"
        
        summary = {
            "timestamp": datetime.datetime.now().isoformat(),
            "executable_path": str(self.exe_path),
            "executable_exists": self.exe_path.exists(),
            "executable_size": self.exe_path.stat().st_size if self.exe_path.exists() else 0,
            "test_results": results,
            "recommendations": []
        }
        
        # Add recommendations based on results
        if not results.get("minimal", {}).get("success", False):
            if "TIMEOUT" in str(results.get("minimal", {}).get("return_code", "")):
                summary["recommendations"].append("GUI may have launched successfully - timeout is normal for GUI apps")
            elif "ModuleNotFoundError" in str(results.get("minimal", {}).get("stderr", "")):
                summary["recommendations"].append("Missing Python modules - check setup.py packages list")
            elif "ImportError" in str(results.get("minimal", {}).get("stderr", "")):
                summary["recommendations"].append("Import error - check module dependencies")
            else:
                summary["recommendations"].append("Check error logs for specific failure details")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n=== Summary Report ===")
        print(f"Report saved to: {report_file}")
        print(f"Executable exists: {summary['executable_exists']}")
        print(f"Executable size: {summary['executable_size']:,} bytes")
        
        if summary["recommendations"]:
            print("Recommendations:")
            for rec in summary["recommendations"]:
                print(f"  - {rec}")
        
        return summary
    
    def run_all_tests(self):
        """Run comprehensive testing suite"""
        print("=" * 60)
        print("DIGGS Processor Manager - Executable Error Testing")
        print("=" * 60)
        
        results = {}
        
        try:
            # Check if executable exists
            self.check_executable_exists()
            
            # Test minimal execution
            results["minimal"] = self.test_minimal_execution(timeout=15)
            
            # Test module imports
            results["imports"] = self.test_import_modules()
            
            # Generate summary
            summary = self.generate_summary_report(results)
            
            print(f"\n[OK] Testing complete! Check logs in: {self.logs_dir}")
            return summary
            
        except Exception as e:
            print(f"[ERROR] Testing failed: {e}")
            return {"error": str(e)}

def main():
    """Main entry point"""
    print("DIGGS Executable Error Logger\n")
    
    try:
        # Check for command line argument
        exe_path = sys.argv[1] if len(sys.argv) > 1 else None
        logger = ExecutableErrorLogger(exe_path)
        summary = logger.run_all_tests()
        
        # Exit with appropriate code
        if summary.get("test_results", {}).get("minimal", {}).get("success", False):
            print("\n[SUCCESS] Executable appears to be working!")
            sys.exit(0)
        else:
            print("\n[WARNING] Issues detected - check error logs for details")
            sys.exit(1)
            
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()