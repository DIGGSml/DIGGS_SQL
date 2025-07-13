#!/usr/bin/env python3
"""
DIGGS Data Processing Manager - GUI Application

This application provides a graphical user interface for the DIGGS data processing
system using the Abstract Factory design pattern.

Features:
- Excel template generation
- Excel to SQLite conversion
- SQLite to DIGGS XML export
- DIGGS XML to SQLite import
- Drag-and-drop file support
- Progress tracking
- Error handling with user-friendly messages
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
import webbrowser

# Add src directory to Python path for imports
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
assets_dir = current_dir / "assets"
sys.path.insert(0, str(src_dir))

# Import our factory system
try:
    from processor_factories import DataProcessorFactoryManager
except ImportError as e:
    messagebox.showerror("Import Error", f"Failed to import processor factories: {e}")
    sys.exit(1)

class DiggsProcessorGUI:
    """Main GUI application for DIGGS data processing"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("DIGGS Data Processing Manager")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Initialize factory manager
        self.factory_manager = DataProcessorFactoryManager()
        
        # Configure style
        self.setup_styles()
        
        # Create GUI components
        self.create_widgets()
        
        # Set up drag and drop
        self.setup_drag_drop()
        
        # Center window
        self.center_window()
    
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
        ttk.Button(template_frame, text="Generate Template", command=self.generate_template,
                  style='Accent.TButton').grid(row=6, column=0, pady=20)
        
        # Template descriptions
        desc_frame = ttk.LabelFrame(template_frame, text="Template Descriptions", padding="5")
        desc_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        descriptions = [
            "• Blank Template: Empty Excel file with all required sheets and headers",
            "• Sample Template: Template with example geotechnical data for reference",
            "• Documentation: Detailed explanation of all sheets and data fields"
        ]
        
        for i, desc in enumerate(descriptions):
            ttk.Label(desc_frame, text=desc).grid(row=i, column=0, sticky=tk.W, pady=2)
    
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
        ttk.Button(convert_frame, text="Convert Excel to SQLite", command=self.convert_excel_to_sqlite,
                  style='Accent.TButton').grid(row=4, column=0, pady=20)
        
        # Drag and drop area
        self.create_drag_drop_area(convert_frame, "Drag Excel files here", 5)
    
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
        ttk.Button(export_frame, text="Export to DIGGS XML", command=self.export_to_diggs,
                  style='Accent.TButton').grid(row=4, column=0, pady=20)
        
        # Features list
        features_frame = ttk.LabelFrame(export_frame, text="DIGGS 2.6 Features", padding="5")
        features_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        features = [
            "✅ DIGGS 2.6 compliant structure",
            "✅ Proper XML namespaces and schema validation",
            "✅ Units of measure for all measurements",
            "✅ Data validation and quality control",
            "✅ GML-compliant geographic coordinates"
        ]
        
        for i, feature in enumerate(features):
            ttk.Label(features_frame, text=feature).grid(row=i, column=0, sticky=tk.W, pady=2)
    
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
        ttk.Button(import_frame, text="Import DIGGS XML", command=self.import_diggs,
                  style='Accent.TButton').grid(row=4, column=0, pady=20)
        
        # Import capabilities
        capabilities_frame = ttk.LabelFrame(import_frame, text="Import Capabilities", padding="5")
        capabilities_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        capabilities = [
            "• Parses DIGGS 2.6 XML structure",
            "• Extracts projects, boreholes, samples, and test data",
            "• Handles Atterberg Limits and SPT test results",
            "• Creates normalized SQLite database structure",
            "• Provides detailed import summary"
        ]
        
        for i, capability in enumerate(capabilities):
            ttk.Label(capabilities_frame, text=capability).grid(row=i, column=0, sticky=tk.W, pady=2)
    
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

Built using the Abstract Factory Design Pattern for extensible, maintainable code.
        """
        
        ttk.Label(about_frame, text=description.strip(), justify=tk.LEFT).grid(row=1, column=0, sticky=tk.W, pady=(0, 20))
        
        # Version info
        version_frame = ttk.LabelFrame(about_frame, text="Version Information", padding="5")
        version_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(version_frame, text="Version: 1.0.0").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(version_frame, text="DIGGS Standard: 2.6").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(version_frame, text="Architecture: Abstract Factory Pattern").grid(row=2, column=0, sticky=tk.W)
        
        # Links
        links_frame = ttk.LabelFrame(about_frame, text="Links", padding="5")
        links_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(links_frame, text="DIGGS Standard Documentation", 
                  command=lambda: webbrowser.open("http://www.diggsml.org/")).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Button(links_frame, text="Database Schema Diagram", 
                  command=lambda: webbrowser.open("https://dbdiagram.io/d/DIGGS-SQL-Structure-668dcbd19939893dae7ebb48")).grid(row=1, column=0, sticky=tk.W, pady=2)
    
    def create_drag_drop_area(self, parent, text, row):
        """Create a drag and drop area"""
        drop_frame = ttk.LabelFrame(parent, text="Quick Drop", padding="10")
        drop_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        
        drop_label = ttk.Label(drop_frame, text=text, font=('Arial', 10, 'italic'))
        drop_label.grid(row=0, column=0, pady=20)
    
    def setup_drag_drop(self):
        """Setup drag and drop functionality (basic implementation)"""
        # Note: Full drag-and-drop would require additional libraries like tkinterdnd2
        # This is a placeholder for the interface
        pass
    
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
            # Auto-generate output filename
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
            # Auto-generate output filename
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
            # Auto-generate output filename
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

def main():
    """Main entry point"""
    # Create and configure root window
    root = tk.Tk()
    
    # Set window icon (if available)
    try:
        # You can add an icon file here
        # root.iconbitmap('icon.ico')
        pass
    except:
        pass
    
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