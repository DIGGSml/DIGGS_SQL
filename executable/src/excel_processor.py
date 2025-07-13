import os
import pandas as pd
from typing import Dict, Any, Optional
from processor_interfaces import ConverterProcessor, GeneratorProcessor

class ExcelToSQLiteConverter(ConverterProcessor):
    """Convert Excel files to SQLite database format"""
    
    def get_processor_type(self) -> str:
        return "excel_to_sqlite"
    
    def get_input_format(self) -> str:
        return "xlsx"
    
    def get_output_format(self) -> str:
        return "db"
    
    def validate_input(self, input_path: str) -> bool:
        """Validate Excel file exists and has required sheets"""
        if not os.path.exists(input_path):
            return False
        
        if not input_path.lower().endswith(('.xlsx', '.xls')):
            return False
        
        try:
            # Check if file can be opened
            pd.ExcelFile(input_path)
            return True
        except Exception:
            return False
    
    def process(self, input_path: str, output_path: str = None, **kwargs) -> bool:
        """Convert Excel to SQLite database"""
        if not self.validate_input(input_path):
            print(f"Invalid input file: {input_path}")
            return False
        
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(self.parent_dir, f"{base_name}.db")
        
        try:
            # Import and use the existing converter
            import excel_to_sqlite_converter
            
            # Run the conversion
            converter = excel_to_sqlite_converter.ExcelToSQLiteConverter()
            success = converter.convert_excel_to_sqlite(input_path, output_path)
            
            if success:
                print(f"Successfully converted {input_path} to {output_path}")
                return True
            else:
                print(f"Failed to convert {input_path}")
                return False
                
        except Exception as e:
            print(f"Error during Excel to SQLite conversion: {e}")
            return False

class ExcelTemplateGenerator(GeneratorProcessor):
    """Generate Excel templates for data collection"""
    
    def get_processor_type(self) -> str:
        return "excel_template"
    
    def validate_input(self, input_path: str) -> bool:
        """Template generator doesn't require input validation"""
        return True
    
    def process(self, input_path: str, output_path: str = None, **kwargs) -> bool:
        """Generate Excel template - delegates to generate method"""
        template_type = kwargs.get('template_type', 'blank')
        if output_path is None:
            output_path = os.path.join(self.parent_dir, f"Geotechnical_Template_{template_type.title()}.xlsx")
        
        return self.generate(output_path, template_type, **kwargs)
    
    def generate(self, output_path: str, template_type: str = "blank", **kwargs) -> bool:
        """Generate Excel template file"""
        try:
            # Import the template generator
            import excel_template_generator
            
            generator = excel_template_generator.ExcelTemplateGenerator()
            
            if template_type.lower() == "blank":
                generator.create_blank_template(output_path)
            elif template_type.lower() == "sample":
                generator.create_sample_template(output_path)
            elif template_type.lower() == "documentation":
                generator.create_documentation(output_path)
            else:
                print(f"Unknown template type: {template_type}")
                return False
            
            print(f"Successfully generated {template_type} template: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error generating Excel template: {e}")
            return False