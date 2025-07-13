from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os

class DataProcessor(ABC):
    """Abstract base class for all DIGGS data processors"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.parent_dir = os.path.dirname(self.script_dir)
    
    @abstractmethod
    def process(self, input_path: str, output_path: str = None, **kwargs) -> bool:
        """Process data from input to output format"""
        pass
    
    @abstractmethod
    def validate_input(self, input_path: str) -> bool:
        """Validate that input file exists and is correct format"""
        pass
    
    @abstractmethod
    def get_processor_type(self) -> str:
        """Return the type of processor"""
        pass
    
    def get_default_output_path(self, input_path: str) -> str:
        """Generate default output path based on input and processor type"""
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        return os.path.join(self.parent_dir, f"{base_name}_{self.get_processor_type()}")

class ConverterProcessor(DataProcessor):
    """Abstract base class for data format converters"""
    
    @abstractmethod
    def get_input_format(self) -> str:
        """Return expected input format"""
        pass
    
    @abstractmethod
    def get_output_format(self) -> str:
        """Return output format"""
        pass

class GeneratorProcessor(DataProcessor):
    """Abstract base class for data generators/templates"""
    
    @abstractmethod
    def generate(self, output_path: str, template_type: str = "standard", **kwargs) -> bool:
        """Generate template or output file"""
        pass

class ImporterProcessor(DataProcessor):
    """Abstract base class for data importers"""
    
    @abstractmethod
    def import_data(self, input_path: str, target_path: str, **kwargs) -> bool:
        """Import data from input format to target format"""
        pass

class ProcessorFactory(ABC):
    """Abstract factory for creating data processors"""
    
    @abstractmethod
    def create_processor(self, processor_type: str, config: Optional[Dict[str, Any]] = None) -> DataProcessor:
        """Create a processor of the specified type"""
        pass
    
    @abstractmethod
    def get_available_processors(self) -> Dict[str, str]:
        """Return dictionary of available processor types and descriptions"""
        pass
    
    @abstractmethod
    def get_factory_type(self) -> str:
        """Return the type of factory"""
        pass