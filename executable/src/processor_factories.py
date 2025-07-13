from typing import Dict, Any, Optional
from processor_interfaces import ProcessorFactory, DataProcessor
from excel_processor import ExcelToSQLiteConverter, ExcelTemplateGenerator
from diggs_processor import SQLiteToDiggsConverter, DiggsToSQLiteImporter

class ExcelProcessorFactory(ProcessorFactory):
    """Factory for Excel-related processors"""
    
    def get_factory_type(self) -> str:
        return "excel"
    
    def create_processor(self, processor_type: str, config: Optional[Dict[str, Any]] = None) -> DataProcessor:
        """Create Excel processor of specified type"""
        processors = {
            "converter": ExcelToSQLiteConverter,
            "excel_to_sqlite": ExcelToSQLiteConverter,
            "template_generator": ExcelTemplateGenerator,
            "template": ExcelTemplateGenerator
        }
        
        if processor_type.lower() not in processors:
            raise ValueError(f"Unknown Excel processor type: {processor_type}")
        
        processor_class = processors[processor_type.lower()]
        return processor_class(config)
    
    def get_available_processors(self) -> Dict[str, str]:
        """Return available Excel processors"""
        return {
            "converter": "Convert Excel files to SQLite database format",
            "excel_to_sqlite": "Convert Excel files to SQLite database format",
            "template_generator": "Generate Excel templates for data collection", 
            "template": "Generate Excel templates for data collection"
        }

class DiggsProcessorFactory(ProcessorFactory):
    """Factory for DIGGS-related processors"""
    
    def get_factory_type(self) -> str:
        return "diggs"
    
    def create_processor(self, processor_type: str, config: Optional[Dict[str, Any]] = None) -> DataProcessor:
        """Create DIGGS processor of specified type"""
        processors = {
            "converter": SQLiteToDiggsConverter,
            "sqlite_to_diggs": SQLiteToDiggsConverter,
            "importer": DiggsToSQLiteImporter,
            "diggs_to_sqlite": DiggsToSQLiteImporter
        }
        
        if processor_type.lower() not in processors:
            raise ValueError(f"Unknown DIGGS processor type: {processor_type}")
        
        processor_class = processors[processor_type.lower()]
        return processor_class(config)
    
    def get_available_processors(self) -> Dict[str, str]:
        """Return available DIGGS processors"""
        return {
            "converter": "Convert SQLite database to DIGGS 2.6 XML format",
            "sqlite_to_diggs": "Convert SQLite database to DIGGS 2.6 XML format", 
            "importer": "Import DIGGS XML files into SQLite database",
            "diggs_to_sqlite": "Import DIGGS XML files into SQLite database"
        }

class DataProcessorFactoryManager:
    """Manager for all processor factories - implements Abstract Factory pattern"""
    
    def __init__(self):
        self._factories = {
            "excel": ExcelProcessorFactory(),
            "diggs": DiggsProcessorFactory()
        }
    
    def get_factory(self, factory_type: str) -> ProcessorFactory:
        """Get factory by type"""
        if factory_type.lower() not in self._factories:
            raise ValueError(f"Unknown factory type: {factory_type}")
        
        return self._factories[factory_type.lower()]
    
    def create_processor(self, factory_type: str, processor_type: str, 
                        config: Optional[Dict[str, Any]] = None) -> DataProcessor:
        """Create processor using specified factory"""
        factory = self.get_factory(factory_type)
        return factory.create_processor(processor_type, config)
    
    def get_available_factories(self) -> Dict[str, str]:
        """Return all available factories"""
        return {
            "excel": "Excel file processing (conversion and template generation)",
            "diggs": "DIGGS XML processing (conversion and import)"
        }
    
    def get_all_available_processors(self) -> Dict[str, Dict[str, str]]:
        """Return all available processors grouped by factory"""
        result = {}
        for factory_type, factory in self._factories.items():
            result[factory_type] = factory.get_available_processors()
        return result
    
    def list_capabilities(self) -> None:
        """Print all available capabilities"""
        print("=== DIGGS Data Processing System ===")
        print("Available processing capabilities:\n")
        
        for factory_type, factory in self._factories.items():
            print(f"{factory_type.upper()} Factory:")
            processors = factory.get_available_processors()
            for proc_type, description in processors.items():
                print(f"  • {proc_type}: {description}")
            print()
        
        print("Usage Examples:")
        print("  manager.create_processor('excel', 'converter', config)")
        print("  manager.create_processor('diggs', 'importer', config)")
        print("  manager.create_processor('excel', 'template', config)")
        print("  manager.create_processor('diggs', 'converter', config)")
        print()