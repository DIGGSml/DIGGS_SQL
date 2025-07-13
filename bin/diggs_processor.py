import os
import sqlite3
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
from .processor_interfaces import ConverterProcessor, ImporterProcessor

class SQLiteToDiggsConverter(ConverterProcessor):
    """Convert SQLite database to DIGGS 2.6 XML format"""
    
    def get_processor_type(self) -> str:
        return "sqlite_to_diggs"
    
    def get_input_format(self) -> str:
        return "db"
    
    def get_output_format(self) -> str:
        return "xml"
    
    def validate_input(self, input_path: str) -> bool:
        """Validate SQLite database file exists and is accessible"""
        if not os.path.exists(input_path):
            return False
        
        if not input_path.lower().endswith('.db'):
            return False
        
        try:
            # Test database connection
            conn = sqlite3.connect(input_path)
            conn.close()
            return True
        except Exception:
            return False
    
    def process(self, input_path: str, output_path: str = None, **kwargs) -> bool:
        """Convert SQLite database to DIGGS XML"""
        if not self.validate_input(input_path):
            print(f"Invalid input database: {input_path}")
            return False
        
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(self.parent_dir, f"{base_name}_diggs_2.6_compliant.xml")
        
        try:
            # Import the DIGGS converter
            import sqlite_to_diggs_converter
            
            # Create and run the converter
            converter = sqlite_to_diggs_converter.DiggsCompliantXMLGenerator(input_path)
            converter.generate_diggs_xml(output_path)
            
            print(f"Successfully converted {input_path} to DIGGS XML: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error during SQLite to DIGGS conversion: {e}")
            return False

class DiggsToSQLiteImporter(ImporterProcessor):
    """Import DIGGS XML files into SQLite database"""
    
    def get_processor_type(self) -> str:
        return "diggs_to_sqlite"
    
    def validate_input(self, input_path: str) -> bool:
        """Validate DIGGS XML file exists and is well-formed"""
        if not os.path.exists(input_path):
            return False
        
        if not input_path.lower().endswith('.xml'):
            return False
        
        try:
            # Test XML parsing
            tree = ET.parse(input_path)
            root = tree.getroot()
            
            # Check if it's a DIGGS file
            if not (root.tag.endswith('Diggs') or 'diggs' in root.tag.lower()):
                return False
            
            return True
        except Exception:
            return False
    
    def process(self, input_path: str, output_path: str = None, **kwargs) -> bool:
        """Import DIGGS XML to SQLite - delegates to import_data method"""
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(self.parent_dir, f"{base_name}_imported.db")
        
        return self.import_data(input_path, output_path, **kwargs)
    
    def import_data(self, input_path: str, target_path: str, **kwargs) -> bool:
        """Import DIGGS XML data into SQLite database"""
        if not self.validate_input(input_path):
            print(f"Invalid DIGGS XML file: {input_path}")
            return False
        
        try:
            # Import the DIGGS importer
            import diggs_to_sqlite_importer
            
            # Create and run the importer
            importer = diggs_to_sqlite_importer.DiggsToSQLiteImporter(target_path)
            importer.import_diggs_xml(input_path)
            importer.close()
            
            print(f"Successfully imported DIGGS XML {input_path} to database: {target_path}")
            return True
            
        except Exception as e:
            print(f"Error during DIGGS to SQLite import: {e}")
            return False