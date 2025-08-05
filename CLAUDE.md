# CLAUDE.md - Context for Future Claude Instances

## Project Overview
**DIGGS_SQL** is an open-source geotechnical database architecture project developed with the Geo Institute. It provides a comprehensive solution for managing geotechnical engineering data through Excel interfaces, SQLite databases, and DIGGS 2.6 XML compliance.

### Key Features
- **Excel ↔ SQLite ↔ DIGGS XML** data flow pipeline
- **Abstract Factory Design Pattern** implementation for extensible processing
- **DIGGS 2.6 compliant** XML export/import
- **Standalone GUI application** for end users
- **Comprehensive geotechnical test support** (SPT, Atterberg Limits, Consolidation, etc.)

## Architecture & Design Patterns

### Abstract Factory Pattern Implementation
The project uses the Abstract Factory pattern located in `/bin/`:

- **`processor_interfaces.py`** - Abstract base classes and interfaces
- **`processor_factories.py`** - Concrete factory implementations
- **`diggs_processor_manager.py`** - Main CLI manager using factory pattern

### Factory Structure
```
DataProcessorFactoryManager
├── ExcelProcessorFactory
│   ├── ExcelToSQLiteConverter
│   └── ExcelTemplateGenerator
├── DiggsProcessorFactory
│   ├── SQLiteToDiggsConverter
│   └── DiggsToSQLiteImporter
└── VisualizationProcessorFactory
    └── DatabaseVisualizationProcessor
```

## Database Schema
**Location**: `/workspaces/DIGGS_SQL/DBdiagram.txt` and `DIGGS sqlite.py`

### Core Tables Structure
- **Project Management**: `_Project`, `_Client`, `_HoleInfo`, `_Samples`
- **Equipment**: `_Rig`, `Cone_Info`, `CoringMethod`, `TestMethod`
- **Geology**: `Geology_Library`, `Field_Strata`, `Final_Strata`, `RockCoring`
- **Laboratory Tests**: `AtterbergLimits`, `Gradation`, `Consolidation`, `_SPT`, `MoistureContent`
- **Advanced Tests**: `uuTest`, `cuTest`, `dsTest`, `Perm`, `Proctor`, `CBR`
- **Field Tests**: `StaticConePenetrationTest`, `Pocket_Pen`, `torvane`, `dilatometer`
- **Well/Monitoring**: `WellConstr`, `WellReadings`, `riser`, `piezometer`

### Database Relationships
- Foreign key constraints enforced with `PRAGMA foreign_keys = ON`
- Hierarchical structure: Project → Holes → Samples → Tests
- Geology library for standardized geological descriptions

## Command Line Interface

### Main Entry Point
**File**: `diggs_processor_manager.py`

### Key Commands
```bash
# List all capabilities
python diggs_processor_manager.py list

# Excel Processing
python diggs_processor_manager.py excel converter input.xlsx [--output database.db]
python diggs_processor_manager.py excel template --template-type [blank|sample|documentation]

# DIGGS Processing  
python diggs_processor_manager.py diggs converter database.db [--output output.xml]
python diggs_processor_manager.py diggs importer input.xml [--output database.db]

# Visualization
python diggs_processor_manager.py visualization database input.db
```

## File Structure & Key Locations

```
DIGGS_SQL/
├── CLAUDE.md                          # This file - context for future Claude instances
├── README.md                          # Comprehensive user documentation
├── DBdiagram.txt                      # Database schema in DBML format
├── DIGGS sqlite.py                    # Database creation script
├── diggs_processor_manager.py         # Main CLI interface
├── requirements.txt                   # Python dependencies
├── bin/                              # Core processing modules (Abstract Factory)
│   ├── processor_interfaces.py       # Abstract base classes
│   ├── processor_factories.py        # Factory implementations
│   ├── excel_processor.py           # Excel processing classes
│   ├── diggs_processor.py           # DIGGS processing classes
│   ├── excel_to_sqlite_converter.py # Excel→SQLite converter
│   ├── sqlite_to_diggs_converter.py # SQLite→DIGGS XML converter
│   ├── diggs_to_sqlite_importer.py  # DIGGS XML→SQLite importer
│   ├── excel_template_generator.py  # Excel template generator
│   └── visualization_processor.py    # Database visualization tool
├── executable/                       # GUI application and distribution
│   ├── diggs_processor_gui.py       # Main GUI application
│   ├── build_executable.bat         # Build script for Windows executable
│   ├── requirements.txt             # GUI-specific dependencies
│   └── src/                         # GUI source modules
└── working/                         # Development and example files
```

## Development Guidelines

### When Working on This Project

1. **Follow Abstract Factory Pattern**: Always extend existing factories rather than creating standalone modules
2. **Database Schema Changes**: Update both `DBdiagram.txt` and `DIGGS sqlite.py` 
3. **Testing**: Use existing sample files in root directory for testing
4. **DIGGS Compliance**: Ensure all XML exports maintain DIGGS 2.6 compliance
5. **Error Handling**: Follow existing patterns in processor classes

### Key Dependencies
```python
pandas          # Data manipulation
openpyxl        # Excel file handling  
sqlite3         # Database operations (built-in)
xml.etree       # XML processing (built-in)
tkinter         # GUI framework (built-in)
```

### Testing Files Available
- `Geotechnical_Template_Sample.xlsx` - Sample Excel data
- `Geotechnical_Template_Sample.db` - Sample SQLite database
- `Geotechnical_Template_Sample_diggs_2.6_compliant.xml` - Sample DIGGS XML
- Various `.db` files for testing different scenarios

## Common Tasks

### Adding New Test Methods
1. Update database schema in `DIGGS sqlite.py`
2. Update `DBdiagram.txt` with new table relationships
3. Extend Excel template generator in `/bin/excel_template_generator.py`
4. Update converters to handle new test data

### Adding New Processors
1. Create new processor class inheriting from appropriate interface
2. Register in relevant factory in `processor_factories.py`
3. Update CLI argument parser in `diggs_processor_manager.py`
4. Add to factory capabilities list

### GUI Application
- Located in `/executable/` directory
- Built using tkinter for cross-platform compatibility
- Can be compiled to standalone executable using `build_executable.bat`
- Professional interface with drag-and-drop support

## Standards & Compliance

### DIGGS 2.6 Compliance Features
- ✅ Proper XML namespaces and schema validation
- ✅ Units of measure (UoM) for all measurements
- ✅ Data validation (removes negative blow counts, etc.)
- ✅ Complete observation wrappers for test data
- ✅ GML-compliant geographic coordinates

### Supported Industry Standards
- **DIGGS 2.6** - Data Interchange for Geotechnical and Geoenvironmental Specialists
- **ASTM Standards** - D1586 (SPT), D4318 (Atterberg Limits), D2216 (Moisture Content)
- **USCS Classification** - Unified Soil Classification System
- **AASHTO Classification** - American Association of State Highway Transportation Officials

## Typical Workflows

### New Project Setup
```bash
python diggs_processor_manager.py excel template --template-type blank
# User fills Excel template with project data
python diggs_processor_manager.py excel converter Geotechnical_Template_Blank.xlsx
python diggs_processor_manager.py diggs converter Geotechnical_Template_Blank.db
```

### Import Existing DIGGS Data
```bash
python diggs_processor_manager.py diggs importer existing_project.xml
python diggs_processor_manager.py diggs converter existing_project_imported.db
```

### Data Analysis
```bash
python diggs_processor_manager.py visualization database project_data.db
```

## Important Notes for Future Claude Instances

1. **Never break the Abstract Factory pattern** - always extend existing factories
2. **Database changes require updating both DBML and SQLite creation script**
3. **All file paths in the system use absolute paths** - validate paths before processing
4. **Error handling follows factory pattern** - implement in base classes
5. **DIGGS compliance is critical** - validate all XML outputs
6. **The system supports both CLI and GUI interfaces** - maintain compatibility
7. **Sample data files are provided** - use for testing new features
8. **The project has both source and executable distributions** - consider both when making changes

## External Resources
- **Database Schema Visualization**: https://dbdiagram.io/d/DIGGS-SQL-Structure-668dcbd19939893dae7ebb48
- **Executable Releases**: https://github.com/geotechnick/DIGGS-Data-Processor-exe/releases/tag/v1.0.0
- **Source Code Releases**: https://github.com/geotechnick/DIGGS_SQL/releases/tag/v1.0.0

This project represents a comprehensive solution for geotechnical data management with a focus on industry standards, extensibility, and user-friendly interfaces.