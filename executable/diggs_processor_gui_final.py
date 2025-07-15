#!/usr/bin/env python3
"""
DIGGS Data Processing Manager - GUI Application (Final Fixed Version)

This version correctly handles the executable environment where modules
are in the root directory but Python looks in lib/library.zip by default.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
import webbrowser
import sqlite3
import pandas as pd

def setup_import_paths():
    """Setup import paths for executable environment"""
    if hasattr(sys, 'frozen'):
        # Running as executable - cx_Freeze specific
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        
        print(f"Executable directory: {exe_dir}")
        print(f"Current sys.path: {sys.path[:3]}")
        
        # For cx_Freeze, modules are in the same directory as the executable
        # Add executable directory to the beginning of sys.path
        if exe_dir not in sys.path:
            sys.path.insert(0, exe_dir)
            print(f"Added to path: {exe_dir}")
        
        # Also check src subdirectory
        src_dir = os.path.join(exe_dir, "src")
        if os.path.exists(src_dir) and src_dir not in sys.path:
            sys.path.insert(0, src_dir)
            print(f"Added src to path: {src_dir}")
        
        # List available .py files in executable directory
        try:
            py_files = [f for f in os.listdir(exe_dir) if f.endswith('.py')]
            print(f"Available .py files: {py_files[:5]}")  # Show first 5
        except Exception as e:
            print(f"Could not list files: {e}")
            
        return exe_dir
    else:
        # Running in development
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(current_dir, "src")
        
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        if os.path.exists(src_dir) and src_dir not in sys.path:
            sys.path.insert(0, src_dir)
            
        return current_dir

def import_factory_manager():
    """Import the factory manager with detailed debugging"""
    print("=== Import Debug Info ===")
    print(f"Python executable: {sys.executable}")
    print(f"Frozen: {hasattr(sys, 'frozen')}")
    print(f"Current working directory: {os.getcwd()}")
    
    print("\nPython path:")
    for i, path in enumerate(sys.path[:10]):  # Show first 10 paths
        print(f"  {i}: {path}")
    
    # List files in executable directory
    if hasattr(sys, 'frozen'):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        print(f"\nFiles in executable directory ({exe_dir}):")
        try:
            files = os.listdir(exe_dir)
            for f in sorted(files):
                if f.endswith('.py') or f.endswith('.pyc'):
                    print(f"  {f}")
        except Exception as e:
            print(f"  Error listing files: {e}")
    
    print("\n=== Attempting Imports ===")
    
    try:
        print("1. Trying direct import...")
        import processor_interfaces
        print("   [OK] processor_interfaces imported")
        
        import processor_factories
        print("   [OK] processor_factories imported")
        
        from processor_factories import DataProcessorFactoryManager
        print("   [OK] DataProcessorFactoryManager imported")
        
        return DataProcessorFactoryManager
        
    except ImportError as e:
        print(f"   [FAILED] Direct import failed: {e}")
        
        # Try adding current executable directory explicitly
        if hasattr(sys, 'frozen'):
            exe_dir = os.path.dirname(os.path.abspath(sys.executable))
            print(f"2. Trying with explicit path: {exe_dir}")
            
            # Check if files exist
            interfaces_file = os.path.join(exe_dir, "processor_interfaces.py")
            factories_file = os.path.join(exe_dir, "processor_factories.py")
            
            print(f"   processor_interfaces.py exists: {os.path.exists(interfaces_file)}")
            print(f"   processor_factories.py exists: {os.path.exists(factories_file)}")
            
            if exe_dir not in sys.path:
                sys.path.insert(0, exe_dir)
                print(f"   Added {exe_dir} to path")
            
            try:
                import processor_interfaces
                import processor_factories
                from processor_factories import DataProcessorFactoryManager
                print("   [OK] Import successful with explicit path")
                return DataProcessorFactoryManager
            except ImportError as e2:
                print(f"   [FAILED] Still failed: {e2}")
        
        # Show error dialog
        error_msg = f"Failed to import processor factories.\n\nError: {e}\n\nDebugging info:\n"
        error_msg += f"Frozen: {hasattr(sys, 'frozen')}\n"
        error_msg += f"Executable: {sys.executable}\n"
        error_msg += f"Working dir: {os.getcwd()}\n"
        error_msg += f"Python path: {sys.path[:3]}\n"
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Import Error", error_msg)
        return None

# Setup paths
print("Setting up import paths...")
current_dir = setup_import_paths()

# Try to import factory manager
print("Importing factory manager...")
DataProcessorFactoryManager = import_factory_manager()

if DataProcessorFactoryManager is None:
    print("Failed to import factory manager, exiting...")
    input("Press Enter to exit...")
    sys.exit(1)

print("[OK] Successfully imported DataProcessorFactoryManager")

class DiggsProcessorGUI:
    """Main GUI application for DIGGS data processing"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("DIGGS Data Processing Manager")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Initialize factory manager
        try:
            self.factory_manager = DataProcessorFactoryManager()
            print("[OK] Factory manager initialized successfully")
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize factory manager: {e}")
            sys.exit(1)
        
        # Configure style
        self.setup_styles()
        
        # Create GUI components
        self.create_widgets()
        
        # Center window
        self.center_window()
        
        # Log success
        self.log_message("DIGGS Data Processing Manager started successfully")
        self.log_message("All factory components loaded and ready")
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom colors
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="DIGGS Data Processing Manager", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Create notebook for different operations
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create tabs
        self.create_template_tab()
        self.create_convert_tab()
        self.create_export_tab()
        self.create_import_tab()
        self.create_data_viewer_tab()
        self.create_about_tab()
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="5")
        progress_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(progress_frame, height=8, wrap=tk.WORD)
        self.output_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear output button
        clear_btn = ttk.Button(progress_frame, text="Clear Output", command=self.clear_output)
        clear_btn.grid(row=2, column=0, sticky=tk.E, pady=(5, 0))
    
    def create_template_tab(self):
        """Create Excel template generation tab"""
        template_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(template_frame, text="Excel Templates")
        
        # Template type selection
        ttk.Label(template_frame, text="Template Type:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.template_type = tk.StringVar(value="blank")
        ttk.Radiobutton(template_frame, text="Blank Template", variable=self.template_type, 
                       value="blank").grid(row=1, column=0, sticky=tk.W, padx=(20, 0))
        ttk.Radiobutton(template_frame, text="Sample Template", variable=self.template_type, 
                       value="sample").grid(row=2, column=0, sticky=tk.W, padx=(20, 0))
        ttk.Radiobutton(template_frame, text="Documentation", variable=self.template_type, 
                       value="documentation").grid(row=3, column=0, sticky=tk.W, padx=(20, 0))
        
        # Output file selection
        ttk.Label(template_frame, text="Output File:", style='Header.TLabel').grid(row=4, column=0, sticky=tk.W, pady=(20, 5))
        
        output_frame = ttk.Frame(template_frame)
        output_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        
        self.template_output = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.template_output).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_template_output).grid(row=0, column=1)
        
        # Generate button
        ttk.Button(template_frame, text="Generate Template", command=self.generate_template).grid(row=6, column=0, pady=20)
    
    def create_convert_tab(self):
        """Create Excel to SQLite conversion tab"""
        convert_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(convert_frame, text="Excel → SQLite")
        
        # Input file selection
        ttk.Label(convert_frame, text="Excel Input File:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        input_frame = ttk.Frame(convert_frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        self.excel_input = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.excel_input).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(input_frame, text="Browse", command=self.browse_excel_input).grid(row=0, column=1)
        
        # Output database selection
        ttk.Label(convert_frame, text="SQLite Output Database:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(20, 5))
        
        output_frame = ttk.Frame(convert_frame)
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        
        self.sqlite_output = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.sqlite_output).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_sqlite_output).grid(row=0, column=1)
        
        # Convert button
        ttk.Button(convert_frame, text="Convert Excel to SQLite", command=self.convert_excel_to_sqlite).grid(row=4, column=0, pady=20)
    
    def create_export_tab(self):
        """Create SQLite to DIGGS export tab"""
        export_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(export_frame, text="SQLite → DIGGS")
        
        # Input database selection
        ttk.Label(export_frame, text="SQLite Input Database:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        input_frame = ttk.Frame(export_frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        self.db_input = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.db_input).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(input_frame, text="Browse", command=self.browse_db_input).grid(row=0, column=1)
        
        # Output XML selection
        ttk.Label(export_frame, text="DIGGS XML Output File:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(20, 5))
        
        output_frame = ttk.Frame(export_frame)
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        
        self.xml_output = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.xml_output).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_xml_output).grid(row=0, column=1)
        
        # Export button
        ttk.Button(export_frame, text="Export to DIGGS XML", command=self.export_to_diggs).grid(row=4, column=0, pady=20)
    
    def create_import_tab(self):
        """Create DIGGS to SQLite import tab"""
        import_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(import_frame, text="DIGGS → SQLite")
        
        # Input XML selection
        ttk.Label(import_frame, text="DIGGS XML Input File:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        input_frame = ttk.Frame(import_frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        self.xml_input = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.xml_input).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(input_frame, text="Browse", command=self.browse_xml_input).grid(row=0, column=1)
        
        # Output database selection
        ttk.Label(import_frame, text="SQLite Output Database:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(20, 5))
        
        output_frame = ttk.Frame(import_frame)
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        
        self.db_output = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.db_output).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_db_output).grid(row=0, column=1)
        
        # Import button
        ttk.Button(import_frame, text="Import DIGGS XML", command=self.import_diggs).grid(row=4, column=0, pady=20)
    
    def create_data_viewer_tab(self):
        """Create data viewer tab with table display and filters"""
        viewer_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(viewer_frame, text="Data Viewer")
        
        # Configure grid weights
        viewer_frame.columnconfigure(0, weight=1)
        viewer_frame.rowconfigure(3, weight=1)
        
        # Database file selection
        ttk.Label(viewer_frame, text="SQLite Database:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        db_frame = ttk.Frame(viewer_frame)
        db_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        db_frame.columnconfigure(0, weight=1)
        
        self.viewer_db_path = tk.StringVar()
        ttk.Entry(db_frame, textvariable=self.viewer_db_path).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(db_frame, text="Browse", command=self.browse_viewer_database).grid(row=0, column=1)
        ttk.Button(db_frame, text="Load Data", command=self.load_database_data).grid(row=0, column=2, padx=(5, 0))
        
        # Filters frame
        filters_frame = ttk.LabelFrame(viewer_frame, text="Filters", padding="5")
        filters_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filters_frame.columnconfigure(1, weight=1)
        filters_frame.columnconfigure(3, weight=1)
        
        # Table dropdown
        ttk.Label(filters_frame, text="Table:").grid(row=0, column=0, padx=(0, 5))
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(filters_frame, textvariable=self.table_var, state="readonly")
        self.table_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.table_combo.bind('<<ComboboxSelected>>', self.on_table_selected)
        
        # Column filter dropdown
        ttk.Label(filters_frame, text="Filter Column:").grid(row=0, column=2, padx=(0, 5))
        self.filter_column_var = tk.StringVar()
        self.filter_column_combo = ttk.Combobox(filters_frame, textvariable=self.filter_column_var, state="readonly")
        self.filter_column_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 10))
        self.filter_column_combo.bind('<<ComboboxSelected>>', self.on_filter_column_selected)
        
        # Filter value dropdown
        ttk.Label(filters_frame, text="Filter Value:").grid(row=1, column=0, padx=(0, 5), pady=(5, 0))
        self.filter_value_var = tk.StringVar()
        self.filter_value_combo = ttk.Combobox(filters_frame, textvariable=self.filter_value_var)
        self.filter_value_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
        
        # Search box
        ttk.Label(filters_frame, text="Search:").grid(row=1, column=2, padx=(0, 5), pady=(5, 0))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filters_frame, textvariable=self.search_var)
        search_entry.grid(row=1, column=3, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
        search_entry.bind('<KeyRelease>', self.on_search_changed)
        
        # Filter buttons
        button_frame = ttk.Frame(filters_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=(10, 0))
        
        ttk.Button(button_frame, text="Apply Filter", command=self.apply_filters).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Clear Filters", command=self.clear_filters).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="Refresh", command=self.refresh_data).grid(row=0, column=2, padx=(0, 5))
        
        # Table display frame
        table_frame = ttk.LabelFrame(viewer_frame, text="Data", padding="5")
        table_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Create Treeview for table display
        self.tree_frame = ttk.Frame(table_frame)
        self.tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_frame.rowconfigure(0, weight=1)
        
        # Info label
        self.info_label = ttk.Label(table_frame, text="Select a database to view data")
        self.info_label.grid(row=1, column=0, pady=(5, 0))
        
        # Initialize variables
        self.current_db_path = None
        self.current_data = None
        self.filtered_data = None
        self.tree = None
    
    def create_about_tab(self):
        """Create about/help tab"""
        about_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(about_frame, text="About")
        
        # Title and description
        ttk.Label(about_frame, text="DIGGS Data Processing Manager", 
                 style='Title.TLabel').grid(row=0, column=0, pady=(0, 10))
        
        description = """
This application provides a complete workflow for geotechnical data processing:

• Excel Template Generation - Create standardized data collection templates
• Excel to SQLite Conversion - Transform Excel data into normalized database
• SQLite to DIGGS Export - Generate DIGGS 2.6 compliant XML files
• DIGGS XML Import - Import existing DIGGS files into SQLite database
• Data Viewer - Browse, filter, and search SQLite database tables with interactive interface

Built using the Abstract Factory Design Pattern for extensible, maintainable code.
        """
        
        ttk.Label(about_frame, text=description.strip(), justify=tk.LEFT).grid(row=1, column=0, sticky=tk.W, pady=(0, 20))
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    # File browser methods
    def browse_template_output(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.template_output.set(filename)
    
    def browse_excel_input(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            self.excel_input.set(filename)
            if not self.sqlite_output.get():
                base = os.path.splitext(filename)[0]
                self.sqlite_output.set(f"{base}.db")
    
    def browse_sqlite_output(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite database", "*.db"), ("All files", "*.*")]
        )
        if filename:
            self.sqlite_output.set(filename)
    
    def browse_db_input(self):
        filename = filedialog.askopenfilename(
            filetypes=[("SQLite database", "*.db"), ("All files", "*.*")]
        )
        if filename:
            self.db_input.set(filename)
            if not self.xml_output.get():
                base = os.path.splitext(filename)[0]
                self.xml_output.set(f"{base}_diggs_2.6_compliant.xml")
    
    def browse_xml_output(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filename:
            self.xml_output.set(filename)
    
    def browse_xml_input(self):
        filename = filedialog.askopenfilename(
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filename:
            self.xml_input.set(filename)
            if not self.db_output.get():
                base = os.path.splitext(filename)[0]
                self.db_output.set(f"{base}_imported.db")
    
    def browse_db_output(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite database", "*.db"), ("All files", "*.*")]
        )
        if filename:
            self.db_output.set(filename)
    
    # Processing methods
    def log_message(self, message, level="INFO"):
        """Add message to output text area"""
        self.output_text.insert(tk.END, f"[{level}] {message}\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete(1.0, tk.END)
    
    def start_progress(self):
        """Start progress bar animation"""
        self.progress.start(10)
    
    def stop_progress(self):
        """Stop progress bar animation"""
        self.progress.stop()
    
    def run_in_thread(self, func, *args, **kwargs):
        """Run function in separate thread to prevent GUI freezing"""
        def worker():
            try:
                self.start_progress()
                func(*args, **kwargs)
            except Exception as e:
                self.log_message(f"Error: {str(e)}", "ERROR")
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
            finally:
                self.stop_progress()
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def generate_template(self):
        """Generate Excel template"""
        def worker():
            template_type = self.template_type.get()
            output_path = self.template_output.get()
            
            if not output_path:
                output_path = f"Geotechnical_Template_{template_type.title()}.xlsx"
            
            self.log_message(f"Generating {template_type} template...")
            
            try:
                generator = self.factory_manager.create_processor('excel', 'template')
                success = generator.generate(output_path, template_type)
                
                if success:
                    self.log_message(f"Template generated successfully: {output_path}", "SUCCESS")
                    messagebox.showinfo("Success", f"Template generated successfully!\n\nLocation: {output_path}")
                else:
                    self.log_message("Template generation failed", "ERROR")
                    messagebox.showerror("Error", "Template generation failed")
                    
            except Exception as e:
                self.log_message(f"Error generating template: {str(e)}", "ERROR")
                messagebox.showerror("Error", f"Error generating template: {str(e)}")
        
        self.run_in_thread(worker)
    
    def convert_excel_to_sqlite(self):
        """Convert Excel to SQLite"""
        def worker():
            input_path = self.excel_input.get()
            output_path = self.sqlite_output.get()
            
            if not input_path:
                messagebox.showerror("Error", "Please select an Excel input file")
                return
            
            if not output_path:
                base = os.path.splitext(input_path)[0]
                output_path = f"{base}.db"
                self.sqlite_output.set(output_path)
            
            self.log_message(f"Converting Excel to SQLite...")
            self.log_message(f"Input: {input_path}")
            self.log_message(f"Output: {output_path}")
            
            try:
                converter = self.factory_manager.create_processor('excel', 'converter')
                success = converter.process(input_path, output_path)
                
                if success:
                    self.log_message("Conversion completed successfully", "SUCCESS")
                    messagebox.showinfo("Success", f"Excel file converted successfully!\n\nDatabase: {output_path}")
                else:
                    self.log_message("Conversion failed", "ERROR")
                    messagebox.showerror("Error", "Excel to SQLite conversion failed")
                    
            except Exception as e:
                self.log_message(f"Error during conversion: {str(e)}", "ERROR")
                messagebox.showerror("Error", f"Error during conversion: {str(e)}")
        
        self.run_in_thread(worker)
    
    def export_to_diggs(self):
        """Export SQLite to DIGGS XML"""
        def worker():
            input_path = self.db_input.get()
            output_path = self.xml_output.get()
            
            if not input_path:
                messagebox.showerror("Error", "Please select a SQLite database file")
                return
            
            if not output_path:
                base = os.path.splitext(input_path)[0]
                output_path = f"{base}_diggs_2.6_compliant.xml"
                self.xml_output.set(output_path)
            
            self.log_message(f"Exporting SQLite to DIGGS XML...")
            self.log_message(f"Input: {input_path}")
            self.log_message(f"Output: {output_path}")
            
            try:
                exporter = self.factory_manager.create_processor('diggs', 'converter')
                success = exporter.process(input_path, output_path)
                
                if success:
                    self.log_message("DIGGS XML export completed successfully", "SUCCESS")
                    messagebox.showinfo("Success", f"DIGGS XML exported successfully!\n\nFile: {output_path}")
                else:
                    self.log_message("DIGGS XML export failed", "ERROR")
                    messagebox.showerror("Error", "SQLite to DIGGS XML export failed")
                    
            except Exception as e:
                self.log_message(f"Error during export: {str(e)}", "ERROR")
                messagebox.showerror("Error", f"Error during export: {str(e)}")
        
        self.run_in_thread(worker)
    
    def import_diggs(self):
        """Import DIGGS XML to SQLite"""
        def worker():
            input_path = self.xml_input.get()
            output_path = self.db_output.get()
            
            if not input_path:
                messagebox.showerror("Error", "Please select a DIGGS XML file")
                return
            
            if not output_path:
                base = os.path.splitext(input_path)[0]
                output_path = f"{base}_imported.db"
                self.db_output.set(output_path)
            
            self.log_message(f"Importing DIGGS XML to SQLite...")
            self.log_message(f"Input: {input_path}")
            self.log_message(f"Output: {output_path}")
            
            try:
                importer = self.factory_manager.create_processor('diggs', 'importer')
                success = importer.process(input_path, output_path)
                
                if success:
                    self.log_message("DIGGS XML import completed successfully", "SUCCESS")
                    messagebox.showinfo("Success", f"DIGGS XML imported successfully!\n\nDatabase: {output_path}")
                else:
                    self.log_message("DIGGS XML import failed", "ERROR")
                    messagebox.showerror("Error", "DIGGS XML to SQLite import failed")
                    
            except Exception as e:
                self.log_message(f"Error during import: {str(e)}", "ERROR")
                messagebox.showerror("Error", f"Error during import: {str(e)}")
        
        self.run_in_thread(worker)
    
    # Data viewer methods
    def browse_viewer_database(self):
        """Browse for database file to view"""
        filename = filedialog.askopenfilename(
            filetypes=[("SQLite database", "*.db"), ("All files", "*.*")]
        )
        if filename:
            self.viewer_db_path.set(filename)
    
    def load_database_data(self):
        """Load database and populate table dropdown"""
        db_path = self.viewer_db_path.get()
        if not db_path:
            messagebox.showerror("Error", "Please select a database file")
            return
        
        if not os.path.exists(db_path):
            messagebox.showerror("Error", "Database file does not exist")
            return
        
        try:
            self.current_db_path = db_path
            
            # Connect to database and get table names
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            if not tables:
                messagebox.showwarning("Warning", "No tables found in database")
                return
            
            # Populate table dropdown
            self.table_combo['values'] = tables
            self.table_var.set(tables[0])  # Select first table
            
            # Clear other dropdowns
            self.filter_column_combo['values'] = []
            self.filter_value_combo['values'] = []
            self.filter_column_var.set('')
            self.filter_value_var.set('')
            self.search_var.set('')
            
            # Load first table
            self.on_table_selected(None)
            
            self.log_message(f"Loaded database: {os.path.basename(db_path)} ({len(tables)} tables)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load database: {str(e)}")
            self.log_message(f"Error loading database: {str(e)}", "ERROR")
    
    def on_table_selected(self, event):
        """Handle table selection"""
        if not self.current_db_path or not self.table_var.get():
            return
        
        try:
            table_name = self.table_var.get()
            
            # Load table data
            conn = sqlite3.connect(self.current_db_path)
            self.current_data = pd.read_sql_query(f"SELECT * FROM `{table_name}`", conn)
            conn.close()
            
            if self.current_data.empty:
                self.info_label.config(text=f"Table '{table_name}' is empty")
                self.create_empty_tree()
                return
            
            # Populate column filter dropdown
            columns = list(self.current_data.columns)
            self.filter_column_combo['values'] = columns
            self.filter_column_var.set('')
            self.filter_value_var.set('')
            
            # Reset filtered data
            self.filtered_data = self.current_data.copy()
            
            # Update display
            self.update_tree_display()
            
            self.info_label.config(text=f"Table: {table_name} | Rows: {len(self.current_data)} | Columns: {len(columns)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load table data: {str(e)}")
            self.log_message(f"Error loading table: {str(e)}", "ERROR")
    
    def on_filter_column_selected(self, event):
        """Handle filter column selection"""
        if not hasattr(self, 'current_data') or self.current_data is None:
            return
        
        column = self.filter_column_var.get()
        if not column:
            return
        
        try:
            # Get unique values for the selected column
            unique_values = sorted(self.current_data[column].dropna().unique().astype(str))
            self.filter_value_combo['values'] = unique_values
            self.filter_value_var.set('')
            
        except Exception as e:
            self.log_message(f"Error loading filter values: {str(e)}", "ERROR")
    
    def on_search_changed(self, event):
        """Handle search text change with delay"""
        # Cancel previous search timer if exists
        if hasattr(self, 'search_timer'):
            self.root.after_cancel(self.search_timer)
        
        # Set new timer for 500ms delay
        self.search_timer = self.root.after(500, self.apply_filters)
    
    def apply_filters(self):
        """Apply all filters and update display"""
        if not hasattr(self, 'current_data') or self.current_data is None:
            return
        
        try:
            # Start with original data
            filtered_data = self.current_data.copy()
            
            # Apply column filter
            filter_column = self.filter_column_var.get()
            filter_value = self.filter_value_var.get()
            
            if filter_column and filter_value:
                filtered_data = filtered_data[filtered_data[filter_column].astype(str) == filter_value]
            
            # Apply search filter (search across all columns)
            search_text = self.search_var.get().strip()
            if search_text:
                # Create a mask for rows that contain the search text in any column
                mask = filtered_data.astype(str).apply(
                    lambda x: x.str.contains(search_text, case=False, na=False)
                ).any(axis=1)
                filtered_data = filtered_data[mask]
            
            self.filtered_data = filtered_data
            self.update_tree_display()
            
            # Update info label
            table_name = self.table_var.get()
            total_rows = len(self.current_data)
            filtered_rows = len(self.filtered_data)
            
            if filtered_rows < total_rows:
                self.info_label.config(text=f"Table: {table_name} | Showing: {filtered_rows} of {total_rows} rows")
            else:
                self.info_label.config(text=f"Table: {table_name} | Rows: {total_rows}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filters: {str(e)}")
            self.log_message(f"Error applying filters: {str(e)}", "ERROR")
    
    def clear_filters(self):
        """Clear all filters"""
        self.filter_column_var.set('')
        self.filter_value_var.set('')
        self.search_var.set('')
        
        if hasattr(self, 'current_data') and self.current_data is not None:
            self.filtered_data = self.current_data.copy()
            self.update_tree_display()
            
            table_name = self.table_var.get()
            self.info_label.config(text=f"Table: {table_name} | Rows: {len(self.current_data)}")
    
    def refresh_data(self):
        """Refresh the current table data"""
        if self.table_var.get():
            self.on_table_selected(None)
    
    def create_empty_tree(self):
        """Create empty tree view"""
        if self.tree:
            self.tree.destroy()
        
        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add scrollbars
        v_scroll = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=v_scroll.set)
        
        h_scroll = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.tree.configure(xscrollcommand=h_scroll.set)
    
    def update_tree_display(self):
        """Update the tree view with current filtered data"""
        if not hasattr(self, 'filtered_data') or self.filtered_data is None:
            return
        
        # Clear existing tree
        if self.tree:
            self.tree.destroy()
        
        # Create new tree
        columns = list(self.filtered_data.columns)
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='tree headings', height=15)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure column 0 (tree column)
        self.tree.heading('#0', text='Row')
        self.tree.column('#0', width=50, minwidth=50)
        
        # Configure data columns
        for col in columns:
            self.tree.heading(col, text=col)
            # Set column width based on content
            max_width = max(len(col) * 8, 100)  # Minimum 100 pixels
            self.tree.column(col, width=max_width, minwidth=50)
        
        # Add scrollbars
        v_scroll = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=v_scroll.set)
        
        h_scroll = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.tree.configure(xscrollcommand=h_scroll.set)
        
        # Populate with data (limit to first 1000 rows for performance)
        max_rows = min(1000, len(self.filtered_data))
        for i, (index, row) in enumerate(self.filtered_data.head(max_rows).iterrows()):
            # Convert all values to strings and handle NaN/None
            values = [str(val) if pd.notna(val) else '' for val in row]
            self.tree.insert('', 'end', text=str(index), values=values)
        
        # Show warning if data was truncated
        if len(self.filtered_data) > max_rows:
            self.info_label.config(text=f"{self.info_label.cget('text')} (Showing first {max_rows} rows)")

def main():
    """Main entry point"""
    # Create and configure root window
    root = tk.Tk()
    
    # Create and run application
    app = DiggsProcessorGUI(root)
    
    # Handle window closing
    def on_closing():
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()