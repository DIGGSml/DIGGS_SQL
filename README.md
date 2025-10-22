# DIGGS_SQL
**Dataflow for DIGGS, SQL, and Excel**

This is an open source database architecture project developed with the Geo Institute for geotechnical engineering workflows. The system uses SQLite to archive data centrally with an Excel interface for easy data input and retrieval. The database can import and export DIGGS 2.6 compliant XML files.

**Current Status:** Fully operational and tested. Both CLI and GUI applications are working correctly.

**Database Schema:** https://dbdiagram.io/d/DIGGS-SQL-Structure-668dcbd19939893dae7ebb48

**Downloads:**
- Executable Program: https://github.com/geotechnick/DIGGS-Data-Processor-exe/releases/tag/v1.0.0
- Source Code: https://github.com/geotechnick/DIGGS_SQL/releases/tag/v1.0.0

## Architecture

The project implements the **Abstract Factory Design Pattern** for modular, extensible data processing:

- **Excel Processing Factory** - Template generation and Excel to SQLite conversion
- **DIGGS Processing Factory** - SQLite to DIGGS XML conversion and DIGGS XML import
- **Visualization Factory** - Interactive database analysis and visualization
- **Unified Interface** - Command-line manager for all operations
- **Modular Design** - Easy to extend with new processor types

## Installation

### Requirements
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone the Repository
```bash
git clone https://github.com/geotechnick/DIGGS_SQL.git
cd DIGGS_SQL
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- pandas (data manipulation)
- openpyxl (Excel file handling)
- matplotlib (visualization)
- numpy (numerical operations)

Note: sqlite3 and xml.etree are built into Python.

### Step 3: Verify Installation
```bash
python diggs_processor_manager.py list
```

If you see a list of available processing capabilities, the installation was successful.

## Quick Start Guide

### Basic Commands

List all available features:
```bash
python diggs_processor_manager.py list
```

Get help for any command:
```bash
python diggs_processor_manager.py --help
python diggs_processor_manager.py excel --help
python diggs_processor_manager.py diggs --help
```

### Step-by-Step Workflows

#### Workflow 1: Create a New Geotechnical Project

**Step 1:** Generate a blank Excel template
```bash
python diggs_processor_manager.py excel template --template-type blank
```
This creates `Geotechnical_Template_Blank.xlsx` in the current directory.

**Step 2:** Open the Excel file and enter your geotechnical data
- Fill in project information (client, location, coordinates)
- Add borehole data (depth, location, drilling details)
- Enter sample information (depth intervals, sample types)
- Record test results (SPT, Atterberg Limits, etc.)

**Step 3:** Convert Excel to SQLite database
```bash
python diggs_processor_manager.py excel converter Geotechnical_Template_Blank.xlsx
```
This creates `Geotechnical_Template_Blank.db` with normalized data.

**Step 4:** Export to DIGGS XML format
```bash
python diggs_processor_manager.py diggs converter Geotechnical_Template_Blank.db
```
This creates `Geotechnical_Template_Blank_diggs_2.6_compliant.xml` for sharing or archival.

#### Workflow 2: Import Existing DIGGS Data

**Step 1:** Import DIGGS XML to SQLite
```bash
python diggs_processor_manager.py diggs importer ExistingProject.xml
```
This creates `ExistingProject_imported.db`.

**Step 2:** View or analyze the imported data
```bash
python diggs_processor_manager.py visualization database ExistingProject_imported.db
```
This opens an interactive viewer with charts and data tables.

**Step 3:** Export updated DIGGS XML (optional)
```bash
python diggs_processor_manager.py diggs converter ExistingProject_imported.db
```

#### Workflow 3: Practice with Sample Data

**Step 1:** Generate sample template with example data
```bash
python diggs_processor_manager.py excel template --template-type sample
```

**Step 2:** Convert sample to database
```bash
python diggs_processor_manager.py excel converter Geotechnical_Template_Sample.xlsx
```

**Step 3:** Export sample as DIGGS XML
```bash
python diggs_processor_manager.py diggs converter Geotechnical_Template_Sample.db
```

**Step 4:** View sample data interactively
```bash
python diggs_processor_manager.py visualization database Geotechnical_Template_Sample.db
```

## Detailed Command Reference

### Excel Template Generation

Create blank template:
```bash
python diggs_processor_manager.py excel template --template-type blank
```

Create sample template with example data:
```bash
python diggs_processor_manager.py excel template --template-type sample
```

Create documentation template (explains all fields):
```bash
python diggs_processor_manager.py excel template --template-type documentation
```

Specify custom output location:
```bash
python diggs_processor_manager.py excel template --template-type blank --output "C:\Projects\MyTemplate.xlsx"
```

### Excel to SQLite Conversion

Basic conversion:
```bash
python diggs_processor_manager.py excel converter YourData.xlsx
```

Specify output database name:
```bash
python diggs_processor_manager.py excel converter YourData.xlsx --output MyDatabase.db
```

### SQLite to DIGGS XML Export

Basic export:
```bash
python diggs_processor_manager.py diggs converter YourDatabase.db
```

Specify output XML file:
```bash
python diggs_processor_manager.py diggs converter YourDatabase.db --output MyProject.xml
```

### DIGGS XML to SQLite Import

Basic import:
```bash
python diggs_processor_manager.py diggs importer ExistingData.xml
```

Specify output database name:
```bash
python diggs_processor_manager.py diggs importer ExistingData.xml --output ImportedData.db
```

### Database Visualization

Launch interactive viewer:
```bash
python diggs_processor_manager.py visualization database YourDatabase.db
```

The visualization tool provides:
- Database table browser with record counts
- Borehole location maps
- SPT blow count analysis charts
- Atterberg limits plasticity charts
- Soil profile depth visualizations
- Custom SQL query interface

## Excel Template Structure

The generated Excel templates include these sheets:

**Project Information:**
- Project - Basic project details, client info, location
- HoleInfo - Borehole locations, depths, drilling details
- TestMethod - Test standards and procedures

**Sample Data:**
- Samples - Sample identifiers and depth intervals
- FieldStrata - Field soil descriptions by layer
- FinalStrata - Final interpreted stratigraphy

**Laboratory Tests:**
- AtterbergLimits - Plastic limit, liquid limit, plasticity index
- Gradation - Sieve analysis results
- Consolidation - Consolidation test parameters
- ConsolidationLoading - Load increment data
- MoistureContent - Water content measurements
- 200wash - Percent passing No. 200 sieve
- Hydrometer - Clay and silt percentages

**Strength Tests:**
- SPT - Standard Penetration Test blow counts
- uuTest - Unconsolidated Undrained triaxial
- cuTest - Consolidated Undrained triaxial
- dsTest - Direct Shear test results

**Field Tests:**
- StaticConePenetrationTest - CPT data
- Pocket_Pen - Pocket penetrometer readings
- torvane - Torvane shear strength
- dilatometer - Dilatometer test results
- pressuremeter - Pressuremeter data

**Advanced Tests:**
- Perm - Permeability testing
- Proctor - Compaction test results
- CBR - California Bearing Ratio

**Rock Coring:**
- RockCoring - Core logging and RQD data
- CoringMethod - Coring equipment details

**Monitoring:**
- WellConstr - Well construction details
- WellReadings - Groundwater monitoring data
- riser - Riser pipe specifications
- piezometer - Piezometer installation details

## DIGGS 2.6 Compliance Features

The system generates fully compliant DIGGS 2.6 XML with:

- Proper XML namespaces and schema references
- Units of measure (UoM) for all numerical data
- GML-compliant geographic coordinates (latitude/longitude)
- Complete project and investigation metadata
- Sampling feature hierarchies (projects > boreholes > samples)
- Observation wrappers for all test data
- Data validation (negative values removed, types validated)
- ISO 19115 metadata standards

## Supported Data Standards

**Industry Standards:**
- DIGGS 2.6 - Data Interchange for Geotechnical and Geoenvironmental Specialists
- ASTM D1586 - Standard Penetration Test (SPT)
- ASTM D4318 - Atterberg Limits
- ASTM D2216 - Water Content
- ASTM D2487 - Unified Soil Classification System (USCS)
- AASHTO M 145 - Classification of Soils

**Coordinate Systems:**
- WGS84 (EPSG:4326) - Default for geographic coordinates
- Configurable coordinate datum per project

## Desktop Application

A standalone GUI application is available for users who prefer a graphical interface.

### Using the Desktop Application

**Option 1: Run with Python**
```bash
cd executable
python diggs_processor_gui_final.py
```

**Option 2: Build Standalone Executable (Windows)**
```bash
cd executable
python setup.py build
```

After building, the executable is located at:
```
executable/build/exe.win-amd64-3.XX/DIGGS_Processor_Manager.exe
```

**Option 3: Install with Desktop Shortcuts (Windows)**
```bash
cd executable
install.bat
```

### GUI Features

**Excel Templates Tab:**
- Generate blank, sample, or documentation templates
- Automatic file naming with date stamps
- Progress feedback

**Excel to SQLite Tab:**
- Browse for Excel files or drag-and-drop
- Automatic output path generation
- Real-time conversion progress

**SQLite to DIGGS Tab:**
- Convert databases to DIGGS 2.6 XML
- Data validation and quality control
- Compliance checklist display

**DIGGS to SQLite Tab:**
- Import DIGGS XML files
- Parse and validate XML structure
- Import summary with record counts

**Visualization Tab:**
- Interactive database viewer
- Charts and graphs
- Table browser

**About Tab:**
- Version information
- Documentation links
- Architecture overview

For complete desktop application documentation, see `executable/README_EXECUTABLE.md`.

## Programmatic API Usage

You can use the processors directly in Python code:

```python
from bin.processor_factories import DataProcessorFactoryManager

# Initialize factory manager
manager = DataProcessorFactoryManager()

# List all available processors
manager.list_capabilities()

# Convert Excel to SQLite
excel_converter = manager.create_processor('excel', 'converter')
success = excel_converter.process('input.xlsx', 'output.db')

# Convert SQLite to DIGGS XML
diggs_exporter = manager.create_processor('diggs', 'converter')
success = diggs_exporter.process('input.db', 'output.xml')

# Import DIGGS XML
diggs_importer = manager.create_processor('diggs', 'importer')
success = diggs_importer.import_data('input.xml', 'output.db')

# Generate Excel template
template_generator = manager.create_processor('excel', 'template')
success = template_generator.generate('template.xlsx', 'blank')
```

## File Structure

```
DIGGS_SQL/
├── README.md                       # This file
├── CLAUDE.md                       # Developer documentation
├── DBdiagram.txt                   # Database schema (DBML format)
├── DIGGS sqlite.py                 # Database creation script
├── diggs_processor_manager.py      # Main CLI interface
├── requirements.txt                # Python dependencies
├── bin/                            # Processing modules
│   ├── processor_interfaces.py     # Abstract base classes
│   ├── processor_factories.py      # Factory implementations
│   ├── excel_processor.py          # Excel processing wrapper
│   ├── diggs_processor.py          # DIGGS processing wrapper
│   ├── visualization_processor.py  # Visualization wrapper
│   ├── excel_to_sqlite_converter.py    # Excel converter
│   ├── sqlite_to_diggs_converter.py    # DIGGS exporter
│   ├── diggs_to_sqlite_importer.py     # DIGGS importer
│   └── excel_template_generator.py     # Template generator
├── executable/                     # GUI application
│   ├── diggs_processor_gui_final.py    # Main GUI
│   ├── setup.py                        # Build configuration
│   ├── build_executable.bat            # Windows build script
│   ├── install.bat                     # Installation script
│   ├── requirements.txt                # GUI dependencies
│   ├── README_EXECUTABLE.md            # GUI documentation
│   ├── src/                            # GUI source modules
│   └── assets/                         # Static resources
├── working/                        # Development files
└── Geotechnical_Template_Sample.*  # Sample data files
```

## Data Validation

The system includes automatic data validation:

- Removes negative blow counts from SPT data
- Validates XML structure against DIGGS schema
- Ensures proper units of measure (meters, tons per square foot, etc.)
- Checks database foreign key relationships
- Validates coordinate reference systems
- Confirms required fields are present

## Troubleshooting

**Problem:** Command not found or ModuleNotFoundError

**Solution:** Ensure you are in the DIGGS_SQL directory and Python is in your PATH:
```bash
cd /path/to/DIGGS_SQL
python --version  # Should show Python 3.8 or higher
python diggs_processor_manager.py list
```

**Problem:** Import errors when running commands

**Solution:** Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

**Problem:** Excel file not converting

**Solution:** Verify the Excel file uses the correct template structure. Generate a sample template to see the expected format:
```bash
python diggs_processor_manager.py excel template --template-type sample
```

**Problem:** GUI won't launch

**Solution:** Install GUI-specific dependencies:
```bash
cd executable
pip install -r requirements.txt
python diggs_processor_gui_final.py
```

**Problem:** Database visualization errors

**Solution:** Ensure matplotlib is installed:
```bash
pip install matplotlib numpy
```

## Development

### Adding New Test Methods

1. Update database schema in `DIGGS sqlite.py`
2. Update `DBdiagram.txt` with new relationships
3. Modify `bin/excel_template_generator.py` to include new sheet
4. Update `bin/excel_to_sqlite_converter.py` to parse new data
5. Update `bin/sqlite_to_diggs_converter.py` to export new test type
6. Mirror changes in `executable/src/` directory

### Extending the Factory Pattern

1. Create new processor class inheriting from appropriate interface
2. Register in relevant factory in `processor_factories.py`
3. Update CLI argument parser in `diggs_processor_manager.py`
4. Add to factory capabilities list

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Follow the Abstract Factory pattern
4. Use relative imports in all module files
5. Update both `/bin/` and `/executable/src/` if modifying processors
6. Add tests for new functionality
7. Update documentation
8. Submit a pull request

## License

This is an open source project developed with the Geo Institute. See repository for license details.

## Support and Resources

- Database Schema Visualization: https://dbdiagram.io/d/DIGGS-SQL-Structure-668dcbd19939893dae7ebb48
- Executable Releases: https://github.com/geotechnick/DIGGS-Data-Processor-exe/releases
- Source Code: https://github.com/geotechnick/DIGGS_SQL/releases
- DIGGS Standard: http://www.diggsml.org

## Acknowledgments

Developed in collaboration with the Geo Institute for standardized geotechnical data management and interchange.

Built with the Abstract Factory Design Pattern for extensible, maintainable geotechnical data processing.
