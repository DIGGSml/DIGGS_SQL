# DIGGS_SQL
**Dataflow for DIGGS, SQL, and Excel**

This is an ongoing project with the Geo Institute to build an open source database architecture that can easily integrate into geotechnical engineering workflows. This structure uses SQLite to archive data in a central location with an Excel interface for easy data input and retrieval. The database can import and export DIGGS 2.6 compliant XML files.

**Database Schema:** https://dbdiagram.io/d/DIGGS-SQL-Structure-668dcbd19939893dae7ebb48

## Architecture

The project implements the **Abstract Factory Design Pattern** for modular, extensible data processing:

- **Excel Processing Factory** - Template generation and Excel to SQLite conversion
- **DIGGS Processing Factory** - SQLite to DIGGS XML conversion and DIGGS XML import
- **Unified Interface** - Command-line manager for all operations
- **Modular Design** - Easy to extend with new processor types

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-repo/DIGGS_SQL.git
cd DIGGS_SQL
```

2. Install required dependencies:
```bash
pip install pandas openpyxl sqlite3
```

## How to Use

### Quick Start

The system provides a unified command-line interface through `diggs_processor_manager.py`:

```bash
# List all available capabilities
python diggs_processor_manager.py list

# Get help for any command
python diggs_processor_manager.py --help
python diggs_processor_manager.py excel --help
python diggs_processor_manager.py diggs --help
```

### 1. Generate Excel Templates

Create standardized Excel templates for geotechnical data collection:

```bash
# Generate blank template for new projects
python diggs_processor_manager.py excel template --template-type blank

# Generate sample template with example data
python diggs_processor_manager.py excel template --template-type sample

# Generate documentation explaining template structure
python diggs_processor_manager.py excel template --template-type documentation

# Specify custom output path
python diggs_processor_manager.py excel template --template-type blank --output "MyProject_Template.xlsx"
```

**Generated Files:**
- `Geotechnical_Template_Blank.xlsx` - Empty template ready for data entry
- `Geotechnical_Template_Sample.xlsx` - Template with example geotechnical data
- `Template_Documentation.xlsx` - Detailed explanation of all sheets and columns

### 2. Convert Excel to SQLite Database

Transform Excel geotechnical data into normalized SQLite database:

```bash
# Convert Excel file to SQLite database
python diggs_processor_manager.py excel converter "YourData.xlsx"

# Specify custom output database name
python diggs_processor_manager.py excel converter "YourData.xlsx" --output "MyDatabase.db"
```

**Supported Excel Sheets:**
- Project, HoleInfo, TestMethod, Samples
- FieldStrata, FinalStrata, RockCoring
- Gradation, Consolidation, uuTest, cuTest, dsTest
- Perm, Proctor, CBR, WellConstr, WellReadings
- And more geotechnical test types

### 3. Export to DIGGS 2.6 XML

Generate DIGGS 2.6 compliant XML from SQLite database:

```bash
# Convert SQLite database to DIGGS XML
python diggs_processor_manager.py diggs converter "YourDatabase.db"

# Specify custom output XML file
python diggs_processor_manager.py diggs converter "YourDatabase.db" --output "MyProject_DIGGS.xml"
```

**DIGGS Features:**
- ✅ DIGGS 2.6 compliant structure
- ✅ Proper XML namespaces and schema validation
- ✅ Units of measure (UoM) for all measurements
- ✅ Data validation (removes negative blow counts, etc.)
- ✅ Complete observation wrappers for test data
- ✅ GML-compliant geographic coordinates

### 4. Import DIGGS XML to SQLite

Import existing DIGGS XML files into SQLite database:

```bash
# Import DIGGS XML to new SQLite database
python diggs_processor_manager.py diggs importer "ExistingDIGGS.xml"

# Specify custom output database name
python diggs_processor_manager.py diggs importer "ExistingDIGGS.xml" --output "ImportedData.db"
```

**Import Capabilities:**
- Parses DIGGS 2.6 XML structure
- Extracts projects, boreholes, samples, and test data
- Handles Atterberg Limits and SPT test results
- Creates normalized SQLite database structure
- Provides import summary with record counts

## Complete Workflow Examples

### Workflow 1: New Project Setup
```bash
# 1. Generate blank Excel template
python diggs_processor_manager.py excel template --template-type blank

# 2. Fill in your geotechnical data in the Excel file
# (Use Excel to enter project, borehole, sample, and test data)

# 3. Convert to SQLite database
python diggs_processor_manager.py excel converter "Geotechnical_Template_Blank.xlsx"

# 4. Export as DIGGS XML for sharing/archival
python diggs_processor_manager.py diggs converter "Geotechnical_Template_Blank.db"
```

### Workflow 2: Process Existing Data
```bash
# 1. Import existing DIGGS XML file
python diggs_processor_manager.py diggs importer "ReceivedProject.xml"

# 2. Convert database to DIGGS XML (with validation/cleanup)
python diggs_processor_manager.py diggs converter "ReceivedProject_imported.db"

# 3. Generate updated XML with proper compliance
# Output: ReceivedProject_imported_diggs_2.6_compliant.xml
```

### Workflow 3: Data Analysis Pipeline
```bash
# 1. Start with sample data
python diggs_processor_manager.py excel template --template-type sample

# 2. Convert to database for analysis
python diggs_processor_manager.py excel converter "Geotechnical_Template_Sample.xlsx"

# 3. Export final results as DIGGS XML
python diggs_processor_manager.py diggs converter "Geotechnical_Template_Sample.db"
```

## File Structure

```
DIGGS_SQL/
├── diggs_processor_manager.py      # Main command-line interface
├── bin/                            # Processing modules (Abstract Factory)
│   ├── processor_interfaces.py     # Abstract base classes
│   ├── processor_factories.py      # Concrete factory implementations
│   ├── excel_processor.py          # Excel processing classes
│   ├── diggs_processor.py          # DIGGS processing classes
│   ├── excel_to_sqlite_converter.py
│   ├── sqlite_to_diggs_converter.py
│   ├── diggs_to_sqlite_importer.py
│   └── excel_template_generator.py
├── DIGGS sqlite.py                 # Database schema definition
└── working/                        # Development files and examples
```

## Advanced Usage

### Programmatic API

You can also use the processors directly in Python code:

```python
from bin.processor_factories import DataProcessorFactoryManager

# Create factory manager
manager = DataProcessorFactoryManager()

# Create Excel to SQLite converter
converter = manager.create_processor('excel', 'converter')
success = converter.process('input.xlsx', 'output.db')

# Create DIGGS exporter
exporter = manager.create_processor('diggs', 'converter')
success = exporter.process('input.db', 'output.xml')

# Create template generator
generator = manager.create_processor('excel', 'template')
success = generator.generate('template.xlsx', 'blank')
```

### Custom Configuration

Pass configuration parameters to processors:

```python
config = {
    'validation_level': 'strict',
    'include_metadata': True,
    'coordinate_system': 'EPSG:4326'
}

processor = manager.create_processor('diggs', 'converter', config)
```

## Data Standards

The system supports industry-standard geotechnical data formats:

- **DIGGS 2.6** - Data Interchange for Geotechnical and Geoenvironmental Specialists
- **ASTM Standards** - D1586 (SPT), D4318 (Atterberg Limits), D2216 (Moisture Content)
- **USCS Classification** - Unified Soil Classification System
- **AASHTO Classification** - American Association of State Highway Transportation Officials

## Validation and Quality Control

The system includes built-in data validation:

- ✅ Removes negative blow counts from SPT data
- ✅ Validates DIGGS XML against schema requirements
- ✅ Ensures proper units of measure for all measurements
- ✅ Checks foreign key relationships in database
- ✅ Validates coordinate reference systems

## Contributing

This is an open source project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes following the Abstract Factory pattern
4. Add tests for new functionality
5. Submit a pull request

## Future Development

- [ ] Web-based interface
- [ ] Additional test method support
- [ ] Real-time data validation
- [ ] Integration with laboratory systems
- [ ] Executable distribution
- [ ] API endpoint for web services

**Built with the Abstract Factory Design Pattern for extensible, maintainable geotechnical data processing.**
