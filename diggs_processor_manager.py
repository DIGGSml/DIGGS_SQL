#!/usr/bin/env python3
"""
DIGGS Data Processing Manager

This program implements the Abstract Factory design pattern to manage
various DIGGS data processing operations including:
- Excel to SQLite conversion
- SQLite to DIGGS XML conversion  
- DIGGS XML to SQLite import
- Excel template generation

Usage examples:
    python diggs_processor_manager.py --help
    python diggs_processor_manager.py list
    python diggs_processor_manager.py excel converter input.xlsx
    python diggs_processor_manager.py diggs converter database.db
    python diggs_processor_manager.py excel template --template-type blank
"""

import sys
import os
import argparse
from typing import Optional, Dict, Any

# Add bin directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bin'))

from bin.processor_factories import DataProcessorFactoryManager

class DiggsProcessorManager:
    """Main manager for DIGGS data processing operations"""
    
    def __init__(self):
        self.factory_manager = DataProcessorFactoryManager()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
    
    def process_data(self, factory_type: str, processor_type: str, 
                    input_path: str, output_path: Optional[str] = None,
                    config: Optional[Dict[str, Any]] = None, **kwargs) -> bool:
        """Process data using specified factory and processor"""
        try:
            # Create processor using factory pattern
            processor = self.factory_manager.create_processor(
                factory_type, processor_type, config
            )
            
            # Process the data
            success = processor.process(input_path, output_path, **kwargs)
            
            if success:
                print(f"[SUCCESS] Processing completed successfully")
            else:
                print(f"[FAILED] Processing failed")
            
            return success
            
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            return False
    
    def generate_template(self, template_type: str = "blank", 
                         output_path: Optional[str] = None,
                         config: Optional[Dict[str, Any]] = None) -> bool:
        """Generate Excel template using factory pattern"""
        try:
            # Create template generator
            generator = self.factory_manager.create_processor(
                "excel", "template", config
            )
            
            if output_path is None:
                output_path = os.path.join(
                    self.script_dir, 
                    f"Geotechnical_Template_{template_type.title()}.xlsx"
                )
            
            # Generate template
            success = generator.generate(output_path, template_type)
            
            if success:
                print(f"[SUCCESS] Template generated successfully: {output_path}")
            else:
                print(f"[FAILED] Template generation failed")
            
            return success
            
        except Exception as e:
            print(f"[ERROR] Error generating template: {e}")
            return False
    
    def list_capabilities(self):
        """List all available processing capabilities"""
        self.factory_manager.list_capabilities()
    
    def validate_file_path(self, file_path: str) -> str:
        """Validate and resolve file path"""
        if not os.path.isabs(file_path):
            # Convert relative path to absolute
            file_path = os.path.join(self.script_dir, file_path)
        
        return os.path.normpath(file_path)

def create_arg_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="DIGGS Data Processing Manager - Abstract Factory Pattern Implementation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                                    # List all capabilities
  %(prog)s excel converter data.xlsx              # Convert Excel to SQLite
  %(prog)s excel converter data.xlsx --output db.db
  %(prog)s diggs converter database.db            # Convert SQLite to DIGGS XML
  %(prog)s diggs importer data.xml                # Import DIGGS XML to SQLite
  %(prog)s excel template --template-type blank   # Generate blank Excel template
  %(prog)s excel template --template-type sample  # Generate sample Excel template
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all available processing capabilities')
    
    # Excel factory commands
    excel_parser = subparsers.add_parser('excel', help='Excel processing operations')
    excel_subparsers = excel_parser.add_subparsers(dest='processor', help='Excel processors')
    
    # Excel converter
    excel_conv_parser = excel_subparsers.add_parser('converter', help='Convert Excel to SQLite')
    excel_conv_parser.add_argument('input', help='Input Excel file path')
    excel_conv_parser.add_argument('--output', '-o', help='Output SQLite database path')
    
    # Excel template generator
    excel_temp_parser = excel_subparsers.add_parser('template', help='Generate Excel template')
    excel_temp_parser.add_argument('--template-type', '-t', 
                                  choices=['blank', 'sample', 'documentation'],
                                  default='blank', help='Type of template to generate')
    excel_temp_parser.add_argument('--output', '-o', help='Output Excel file path')
    
    # DIGGS factory commands
    diggs_parser = subparsers.add_parser('diggs', help='DIGGS processing operations')
    diggs_subparsers = diggs_parser.add_subparsers(dest='processor', help='DIGGS processors')
    
    # DIGGS converter (SQLite to XML)
    diggs_conv_parser = diggs_subparsers.add_parser('converter', help='Convert SQLite to DIGGS XML')
    diggs_conv_parser.add_argument('input', help='Input SQLite database path')
    diggs_conv_parser.add_argument('--output', '-o', help='Output DIGGS XML file path')
    
    # DIGGS importer (XML to SQLite)
    diggs_imp_parser = diggs_subparsers.add_parser('importer', help='Import DIGGS XML to SQLite')
    diggs_imp_parser.add_argument('input', help='Input DIGGS XML file path')
    diggs_imp_parser.add_argument('--output', '-o', help='Output SQLite database path')
    
    return parser

def main():
    """Main entry point"""
    parser = create_arg_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Create processor manager
    manager = DiggsProcessorManager()
    
    print("=== DIGGS Data Processing Manager ===")
    print("Using Abstract Factory Design Pattern\n")
    
    if args.command == 'list':
        manager.list_capabilities()
        return
    
    # Handle Excel operations
    if args.command == 'excel':
        if not args.processor:
            print("Error: Excel processor type required")
            return
        
        if args.processor == 'converter':
            input_path = manager.validate_file_path(args.input)
            output_path = manager.validate_file_path(args.output) if args.output else None
            
            print(f"Processing: Excel to SQLite")
            print(f"Input:  {input_path}")
            print(f"Output: {output_path or 'Auto-generated'}")
            print()
            
            success = manager.process_data('excel', 'converter', input_path, output_path)
            
        elif args.processor == 'template':
            output_path = manager.validate_file_path(args.output) if args.output else None
            
            print(f"Generating: Excel Template ({args.template_type})")
            print(f"Output: {output_path or 'Auto-generated'}")
            print()
            
            success = manager.generate_template(args.template_type, output_path)
    
    # Handle DIGGS operations
    elif args.command == 'diggs':
        if not args.processor:
            print("Error: DIGGS processor type required")
            return
        
        if args.processor == 'converter':
            input_path = manager.validate_file_path(args.input)
            output_path = manager.validate_file_path(args.output) if args.output else None
            
            print(f"Processing: SQLite to DIGGS XML")
            print(f"Input:  {input_path}")
            print(f"Output: {output_path or 'Auto-generated'}")
            print()
            
            success = manager.process_data('diggs', 'converter', input_path, output_path)
            
        elif args.processor == 'importer':
            input_path = manager.validate_file_path(args.input)
            output_path = manager.validate_file_path(args.output) if args.output else None
            
            print(f"Processing: DIGGS XML to SQLite")
            print(f"Input:  {input_path}")
            print(f"Output: {output_path or 'Auto-generated'}")
            print()
            
            success = manager.process_data('diggs', 'importer', input_path, output_path)
    
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()

if __name__ == "__main__":
    main()