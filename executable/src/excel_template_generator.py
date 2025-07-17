import pandas as pd
import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
try:
    from geology_library import GeologyLibrary
except ImportError:
    # Fallback if geology_library is not available
    class GeologyLibrary:
        def get_standard_geology_types(self):
            return [{'strataName': 'Clay'}, {'strataName': 'Sand'}, {'strataName': 'Silt'}]

class ExcelTemplateGenerator:
    """Generate Excel template files based on DIGGS SQLite schema"""
    
    def __init__(self):
        self.template_structure = {
            'Project': {
                'columns': ['projectName', 'projectNumber', 'projectCountry', 'projectState', 
                           'projectCounty', 'coordinateDatum', 'clientName', 'clientContact'],
                'sample_data': [{
                    'projectName': 'Sample Project',
                    'projectNumber': '2024-001',
                    'projectCountry': 'US',
                    'projectState': 'VA',
                    'projectCounty': 'Henrico',
                    'coordinateDatum': 'WGS84',
                    'clientName': 'Sample Client',
                    'clientContact': 'client@example.com'
                }]
            },
            
            'HoleInfo': {
                'columns': ['holeName', 'holeType', 'topLatitude', 'topLongitude', 'groundSurface',
                           'azimuth', 'angle', 'bottomDepth', 'timeInterval_start', 'timeInterval_end',
                           'termination', 'initialWaterDepth', '24hrWater', 'caveInDepth',
                           '_rigDescription', 'hammerType', 'hammerEfficiency', 'miscID',
                           'drillMethod', 'rodType', 'Additives', 'misc'],
                'sample_data': [{
                    'holeName': 'B-1',
                    'holeType': 'boring',
                    'topLatitude': 37.5407,
                    'topLongitude': -77.4360,
                    'groundSurface': 150.0,
                    'azimuth': 0,
                    'angle': 90,
                    'bottomDepth': 50.0,
                    'timeInterval_start': '2024-01-15T08:00:00',
                    'timeInterval_end': '2024-01-15T16:00:00',
                    'termination': 'refusal',
                    'initialWaterDepth': 10.0,
                    '24hrWater': 8.5,
                    'caveInDepth': None,
                    '_rigDescription': 'CME 55',
                    'hammerType': 'automatic',
                    'hammerEfficiency': 89.0,
                    'miscID': 'RIG-001',
                    'drillMethod': 'hollow stem auger',
                    'rodType': 'A',
                    'Additives': 'none',
                    'misc': 'good conditions'
                }]
            },
            
            'TestMethod': {
                'columns': ['methodName', 'description', 'governingBody', 'units', 'modification'],
                'sample_data': [
                    {'methodName': 'ASTM D1586', 'description': 'Standard Penetration Test', 'governingBody': 'ASTM', 'units': 'blows/ft', 'modification': 'none'},
                    {'methodName': 'ASTM D4318', 'description': 'Atterberg Limits', 'governingBody': 'ASTM', 'units': '%', 'modification': 'none'},
                    {'methodName': 'ASTM D422', 'description': 'Particle Size Analysis', 'governingBody': 'ASTM', 'units': '%', 'modification': 'none'},
                    {'methodName': 'ASTM D2216', 'description': 'Moisture Content', 'governingBody': 'ASTM', 'units': '%', 'modification': 'none'}
                ]
            },
            
            'Samples': {
                'columns': ['Hole Name', 'Sample Name', 'topDepth', 'bottomDepth', 'sampleMethod',
                           'USCS', 'SPTMethod', 'SPT_1', 'SPT_2', 'SPT_3', 'SPT_4', 'recovery',
                           'moistureMethod', 'moistureContent', 'plasticityMethod', 'PL', 'LL', 'PI',
                           'passing200', 'pocketPenReading', 'torvaneReading', 'color', 'primaryComp',
                           'secondaryComp', 'secondaryCompMod', 'organicContent', 'visualMoisture',
                           'AASHTO', 'Misc', 'Geo_ID'],
                'sample_data': [{
                    'Hole Name': 'B-1',
                    'Sample Name': 'S-1',
                    'topDepth': 0.0,
                    'bottomDepth': 2.0,
                    'sampleMethod': 'split spoon',
                    'USCS': 'CL',
                    'SPTMethod': 'ASTM D1586',
                    'SPT_1': 4,
                    'SPT_2': 6,
                    'SPT_3': 8,
                    'SPT_4': 10,
                    'recovery': 95.0,
                    'moistureMethod': 'ASTM D2216',
                    'moistureContent': 18.5,
                    'plasticityMethod': 'ASTM D4318',
                    'PL': 15.0,
                    'LL': 28.0,
                    'PI': 13.0,
                    'passing200': 85.0,
                    'pocketPenReading': 2.5,
                    'torvaneReading': None,
                    'color': 'brown',
                    'primaryComp': 'clay',
                    'secondaryComp': 'silt',
                    'secondaryCompMod': 'little',
                    'organicContent': 2.0,
                    'visualMoisture': 'moist',
                    'AASHTO': 'A-6',
                    'Misc': 'stiff consistency',
                    'Geo_ID': 'GEO-001'
                }]
            },
            
            'RockCoring': {
                'columns': ['Hole Name', 'Sample Name', 'rockType', 'color', 'weathering', 'texture',
                           'relStrength', 'bedding', 'miscDesc', 'discontinuity', 'degreeFracture',
                           'width', 'surfaceRoughness', 'recovery', 'GSI_desc', 'surfaceDescription', 'RQD'],
                'sample_data': [{
                    'Hole Name': 'B-1',
                    'Sample Name': 'R-1',
                    'rockType': 'granite',
                    'color': 'gray',
                    'weathering': 'fresh',
                    'texture': 'medium grained',
                    'relStrength': 'very strong',
                    'bedding': 'massive',
                    'miscDesc': 'biotite granite',
                    'discontinuity': 'joints',
                    'degreeFracture': 2.0,
                    'width': '1-5mm',
                    'surfaceRoughness': 'rough',
                    'recovery': 98.0,
                    'GSI_desc': 'good',
                    'surfaceDescription': 'clean',
                    'RQD': 85.0
                }]
            },
            
            'FieldStrata': {
                'columns': ['Hole Name', 'soilstrength', 'topDepth', 'bottomDepth', 'color',
                           'primaryComp', 'secondaryComp', 'secondaryCompMod', 'organicContent',
                           'visualMoisture', 'USCS', 'AASHTO', 'Misc', 'Geo_ID'],
                'sample_data': [{
                    'Hole Name': 'B-1',
                    'soilstrength': 'stiff',
                    'topDepth': 0.0,
                    'bottomDepth': 5.0,
                    'color': 'brown',
                    'primaryComp': 'clay',
                    'secondaryComp': 'silt',
                    'secondaryCompMod': 'little',
                    'organicContent': 2.0,
                    'visualMoisture': 'moist',
                    'USCS': 'CL',
                    'AASHTO': 'A-6',
                    'Misc': 'root traces',
                    'Geo_ID': 'GEO-001'
                }]
            },
            
            'FinalStrata': {
                'columns': ['Hole Name', 'soilstrength', 'topDepth', 'bottomDepth', 'color',
                           'primaryComp', 'secondaryComp', 'secondaryCompMod', 'organicContent',
                           'visualMoisture', 'USCS', 'AASHTO', 'Misc', 'Geo_ID'],
                'sample_data': [{
                    'Hole Name': 'B-1',
                    'soilstrength': 'stiff',
                    'topDepth': 0.0,
                    'bottomDepth': 5.0,
                    'color': 'brown',
                    'primaryComp': 'clay',
                    'secondaryComp': 'silt',
                    'secondaryCompMod': 'little',
                    'organicContent': 2.0,
                    'visualMoisture': 'moist',
                    'USCS': 'CL',
                    'AASHTO': 'A-6',
                    'Misc': 'final interpretation',
                    'Geo_ID': 'GEO-001'
                }]
            },
            
            'Gradation': {
                'columns': ['Boring', 'Sample', 'retNo4', 'retNo10', 'retNo20', 'retNo40',
                           'retNo60', 'retNo100', 'retNo140', 'retNo200'],
                'sample_data': [{
                    'Boring': 'B-1',
                    'Sample': 'S-1',
                    'retNo4': 100.0,
                    'retNo10': 98.0,
                    'retNo20': 95.0,
                    'retNo40': 92.0,
                    'retNo60': 90.0,
                    'retNo100': 88.0,
                    'retNo140': 86.0,
                    'retNo200': 85.0
                }]
            },
            
            # Test data sheets
            'Consolidation': {
                'columns': ['Boring', 'Sample', '_Method_ID', '_Cons_Load_ID', 'initialVoidRatio',
                           'compressionIndex', 'recompressionIndex', 'overburdenPressure',
                           'preconsolidationPressure'],
                'sample_data': []
            },
            
            'ConsolidationLoading': {
                'columns': ['_Cons_Load_ID', 'loadIncrement', 'pressure', 'Cv', 'Calpha'],
                'sample_data': []
            },
            
            'uuTest': {
                'columns': ['_Sample_ID', '_Method_ID', 'uuSample', 'intWC', 'intDryDen', 'intSat',
                           'intVoid', 'testWC', 'testDryDen', 'testSat', 'testVoid', 'strainRate',
                           'backPres', 'cellPres', 'failStress', 'ultStress', 'sigma1', 'sigma3',
                           'totPhi', 'totC', 'effPhi', 'effC'],
                'sample_data': []
            },
            
            'cuTest': {
                'columns': ['_Sample_ID', '_Method_ID', 'cuSample', 'intWC', 'intDryDen', 'intSat',
                           'intVoid', 'testWC', 'testDryDen', 'testSat', 'testVoid', 'strainRate',
                           'backPres', 'cellPres', 'failStress', 'failPorePres', 'ultStress',
                           'ultPorePres', 'sigma1', 'sigma3', 'totPhi', 'totC', 'effPhi', 'effC'],
                'sample_data': []
            },
            
            'dsTest': {
                'columns': ['_Sample_ID', '_Method_ID', 'dsSample', 'intWC', 'intDryDen', 'intSat',
                           'intVoid', 'testWC', 'testDryDen', 'testSat', 'testVoid', 'strainRate',
                           'failStress', 'failDisp', 'ultStress', 'ultDisp', 'totPhi', 'totC',
                           'effPhi', 'effC'],
                'sample_data': []
            },
            
            'Perm': {
                'columns': ['_Sample_ID', '_Method_ID', 'permValue', 'confiningPres', 'backPres'],
                'sample_data': []
            },
            
            'Proctor': {
                'columns': ['_Sample_ID', '_Method_ID', 'sampleNumber', 'maxDryDensity',
                           'optimumMoisture', 'dryDensity', 'moistureContent'],
                'sample_data': []
            },
            
            'CBR': {
                'columns': ['_Sample_ID', '_Method_ID', 'sampleNumber', 'penetrationID', 'penetration'],
                'sample_data': []
            },
            
            'Cone_Info': {
                'columns': ['_Cone_ID', 'penetrometerType', 'distanceTipToSleeve', 'frictionReducer',
                           'frictionSleeveArea', 'netAreaRatioCorrection', 'piezoconeType',
                           'pushRodType', 'tipCapacity', 'sleeveCapacity', 'surfaceCapacity',
                           'tipApexAngle', 'tipArea'],
                'sample_data': []
            },
            
            'StaticConePenetrationTestType': {
                'columns': ['_Sample_ID', '_Method_ID', 'CPT Name', 'Depth', 'Tip Stress UNC_qc',
                           'Sleeve Stress_fs', 'Pore Pressure_u'],
                'sample_data': []
            },
            
            'WellConstr': {
                'columns': ['Boring', 'material', 'pos_topDepth', 'pos_bottomDepth'],
                'sample_data': []
            },
            
            'riser': {
                'columns': ['Boring', 'pipeMaterial', 'pipeSchedule', 'pipeCoupling', 'screenType',
                           'pos_topDepth', 'pos_bottomDepth'],
                'sample_data': []
            },
            
            'WellReadings': {
                'columns': ['Boring', 'reading', 'temp', 'TimeInterval'],
                'sample_data': []
            },
            
            'piezometer': {
                'columns': ['Boring', 'piezoType', 'pos_topDepth', 'pos_bottomDepth'],
                'sample_data': []
            },
            
            'pressuremeter': {
                'columns': ['_Sample_ID', '_Method_ID', 'pressure', 'volume'],
                'sample_data': []
            },
            
            'dilatometer': {
                'columns': ['_Sample_ID', '_Method_ID', 'reading1', 'reading2'],
                'sample_data': []
            }
        }
    
    def create_blank_template(self, output_path):
        """Create a blank Excel template with all sheets and headers"""
        print(f"Creating blank Excel template: {output_path}")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Create Geology_Library sheet first
            self._create_geology_library_sheet(writer)
            
            for sheet_name, sheet_data in self.template_structure.items():
                # Create empty DataFrame with just headers
                df = pd.DataFrame(columns=sheet_data['columns'])
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                print(f"  Created sheet: {sheet_name} ({len(sheet_data['columns'])} columns)")
            
            # Add dropdowns to sheets with Geo_ID columns
            self._add_geology_dropdowns(writer)
        
        print(f"Blank template created successfully!")
    
    def create_sample_template(self, output_path):
        """Create an Excel template with sample data for testing"""
        print(f"Creating sample Excel template: {output_path}")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Create Geology_Library sheet first
            self._create_geology_library_sheet(writer)
            
            for sheet_name, sheet_data in self.template_structure.items():
                # Create DataFrame with sample data if available, otherwise just headers
                if sheet_data['sample_data']:
                    df = pd.DataFrame(sheet_data['sample_data'])
                else:
                    df = pd.DataFrame(columns=sheet_data['columns'])
                
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                sample_count = len(sheet_data['sample_data'])
                print(f"  Created sheet: {sheet_name} ({len(sheet_data['columns'])} columns, {sample_count} sample rows)")
            
            # Add dropdowns to sheets with Geo_ID columns
            self._add_geology_dropdowns(writer)
        
        print(f"Sample template created successfully!")
    
    def create_documentation(self, output_path):
        """Create documentation sheet explaining the template structure"""
        documentation = {
            'Sheet Name': [],
            'Description': [],
            'Required': [],
            'Key Columns': []
        }
        
        sheet_descriptions = {
            'Project': ('Project information and client details', 'Yes', 'projectName, clientName'),
            'HoleInfo': ('Borehole locations and drilling information', 'Yes', 'holeName, topLatitude, topLongitude'),
            'TestMethod': ('Testing standards and methods used', 'Yes', 'methodName, governingBody'),
            'Samples': ('Sample information and basic test results', 'Yes', 'Hole Name, Sample Name, topDepth, bottomDepth'),
            'FieldStrata': ('Field description of soil layers', 'No', 'Hole Name, topDepth, bottomDepth'),
            'FinalStrata': ('Final interpreted soil layers', 'No', 'Hole Name, topDepth, bottomDepth'),
            'Gradation': ('Particle size distribution results', 'No', 'Boring, Sample, sieve sizes'),
            'RockCoring': ('Rock core description', 'No', 'Hole Name, Sample Name, rockType'),
            'Consolidation': ('Consolidation test results', 'No', '_Sample_ID, test parameters'),
            'uuTest': ('Unconsolidated undrained triaxial test', 'No', '_Sample_ID, strength parameters'),
            'cuTest': ('Consolidated undrained triaxial test', 'No', '_Sample_ID, strength parameters'),
            'dsTest': ('Direct shear test', 'No', '_Sample_ID, strength parameters'),
            'Perm': ('Permeability test results', 'No', '_Sample_ID, permeability values'),
            'Proctor': ('Compaction test results', 'No', '_Sample_ID, density values'),
            'CBR': ('California Bearing Ratio test', 'No', '_Sample_ID, CBR values'),
            'Cone_Info': ('Cone penetrometer specifications', 'No', '_Cone_ID, equipment specs'),
            'StaticConePenetrationTestType': ('CPT test results', 'No', '_Sample_ID, CPT readings'),
            'WellConstr': ('Well construction details', 'No', 'Boring, material, depths'),
            'riser': ('Well riser information', 'No', 'Boring, pipe details'),
            'WellReadings': ('Well monitoring readings', 'No', 'Boring, reading values'),
            'piezometer': ('Piezometer installation', 'No', 'Boring, instrument type'),
            'pressuremeter': ('Pressuremeter test results', 'No', '_Sample_ID, pressure values'),
            'dilatometer': ('Dilatometer test results', 'No', '_Sample_ID, readings')
        }
        
        for sheet_name in self.template_structure.keys():
            description, required, key_cols = sheet_descriptions.get(sheet_name, ('Additional test data', 'No', 'Varies'))
            documentation['Sheet Name'].append(sheet_name)
            documentation['Description'].append(description)
            documentation['Required'].append(required)
            documentation['Key Columns'].append(key_cols)
        
        doc_df = pd.DataFrame(documentation)
        doc_df.to_excel(output_path, sheet_name='Documentation', index=False)
        print(f"Documentation created: {output_path}")
    
    def _create_geology_library_sheet(self, writer):
        """Create a Geology_Library sheet with standardized geology types"""
        geology_lib = GeologyLibrary()
        geology_types = geology_lib.get_standard_geology_types()
        
        # Create DataFrame with geology data
        geology_df = pd.DataFrame(geology_types)
        
        # Add _Geo_ID column
        geology_df.insert(0, '_Geo_ID', range(1, len(geology_df) + 1))
        
        # Add missing columns with defaults
        for col in ['reference', 'mapID', 'memberGroup', 'tertComp', 'addNote']:
            if col not in geology_df.columns:
                geology_df[col] = ''
        
        # Reorder columns to match database structure
        column_order = ['_Geo_ID', 'reference', 'mapID', 'strataName', 'depositType', 
                       'epoch', 'memberGroup', 'primComp', 'secComp', 'tertComp', 'addNote']
        geology_df = geology_df.reindex(columns=column_order, fill_value='')
        
        # Add reference and mapID values
        geology_df['reference'] = 'Standard Geology Library'
        geology_df['mapID'] = geology_df['_Geo_ID'].apply(lambda x: f'STD_{x:03d}')
        geology_df['addNote'] = 'Standard geological classification'
        
        geology_df.to_excel(writer, sheet_name='Geology_Library', index=False)
        print(f"  Created Geology_Library sheet with {len(geology_df)} geology types")
    
    def _add_geology_dropdowns(self, writer):
        """Add geology dropdowns to sheets with Geo_ID columns"""
        sheets_with_geo_id = ['Samples', 'FieldStrata', 'FinalStrata']
        
        for sheet_name in sheets_with_geo_id:
            if sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                
                # Find the Geo_ID column
                geo_id_col = None
                for col_idx, cell in enumerate(worksheet[1], 1):
                    if cell.value == 'Geo_ID':
                        geo_id_col = col_idx
                        break
                
                if geo_id_col:
                    # Create data validation for geology dropdown
                    # Reference the strataName column in Geology_Library sheet
                    geology_range = "Geology_Library!$D$2:$D$100"  # Column D is strataName
                    
                    dv = DataValidation(
                        type="list",
                        formula1=geology_range,
                        showDropDown=True,
                        showErrorMessage=True,
                        errorTitle="Invalid Geology Type",
                        error="Please select a geology type from the dropdown list"
                    )
                    
                    # Apply validation to the entire column (rows 2-1000)
                    col_letter = worksheet.cell(row=1, column=geo_id_col).column_letter
                    range_string = f"{col_letter}2:{col_letter}1000"
                    dv.add(range_string)
                    worksheet.add_data_validation(dv)
                    
                    print(f"  Added geology dropdown to {sheet_name} column {col_letter}")

def main():
    import os
    
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        
        generator = ExcelTemplateGenerator()
        
        # Create different types of templates
        blank_template = os.path.join(parent_dir, "Geotechnical_Template_Blank.xlsx")
        sample_template = os.path.join(parent_dir, "Geotechnical_Template_Sample.xlsx")
        documentation = os.path.join(parent_dir, "Template_Documentation.xlsx")
        
        print("=== Excel Template Generator ===")
        print("Creating geotechnical data collection templates...\n")
        
        # Create blank template
        generator.create_blank_template(blank_template)
        print()
        
        # Create sample template
        generator.create_sample_template(sample_template)
        print()
        
        # Create documentation
        generator.create_documentation(documentation)
        print()
        
        print("=== Template Generation Complete ===")
        print(f"Files created:")
        print(f"  1. {blank_template} - Blank template for data entry")
        print(f"  2. {sample_template} - Template with sample data")
        print(f"  3. {documentation} - Documentation of template structure")
        print()
        print("Use the blank template for new projects.")
        print("Use the sample template to understand the expected data format.")
        
    except Exception as e:
        print(f"Error creating templates: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()