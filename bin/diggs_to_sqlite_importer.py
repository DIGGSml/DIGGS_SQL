import xml.etree.ElementTree as ET
import sqlite3
import uuid
import os
from datetime import datetime

class DiggsToSQLiteImporter:
    """Import DIGGS 2.6 XML files into SQLite database"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        
        # Enable foreign keys
        self.cur.execute('PRAGMA foreign_keys = ON;')
        
        # DIGGS namespaces
        self.namespaces = {
            'diggs': 'http://diggsml.org/schemas/2.6',
            'gml': 'http://www.opengis.net/gml/3.2',
            'diggs_geo': 'http://diggsml.org/schemas/2.6/geotechnical',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }
        
        # Track imported elements to avoid duplicates
        self.imported_ids = {
            'projects': set(),
            'holes': set(),
            'samples': set(),
            'tests': set()
        }
    
    def generate_id(self, prefix=""):
        """Generate a unique ID"""
        return f"{prefix}{str(uuid.uuid4())[:8]}"
    
    def safe_text(self, element):
        """Safely extract text from XML element"""
        if element is not None and element.text:
            return element.text.strip()
        return None
    
    def safe_float(self, element):
        """Safely convert element text to float"""
        text = self.safe_text(element)
        if text:
            try:
                return float(text)
            except (ValueError, TypeError):
                return None
        return None
    
    def safe_int(self, element):
        """Safely convert element text to integer"""
        text = self.safe_text(element)
        if text:
            try:
                return int(float(text))  # Handle cases like "5.0"
            except (ValueError, TypeError):
                return None
        return None
    
    def create_database_if_not_exists(self):
        """Create database tables if they don't exist"""
        print("Checking database structure...")
        
        # Read the DIGGS schema file to create tables
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        schema_file = os.path.join(parent_dir, "DIGGS sqlite.py")
        
        if os.path.exists(schema_file):
            try:
                # Execute the schema creation script
                with open(schema_file, 'r') as f:
                    schema_content = f.read()
                
                # Extract just the CREATE TABLE statements
                lines = schema_content.split('\n')
                create_statements = []
                in_create = False
                current_statement = []
                
                for line in lines:
                    if line.strip().startswith('cur.execute(\'\'\'') and 'CREATE TABLE' in line:
                        in_create = True
                        current_statement = [line.split('\'\'\'')[1]]
                    elif in_create:
                        if line.strip().endswith('\'\'\')'):
                            current_statement.append(line.split('\'\'\'')[0])
                            create_statements.append('\n'.join(current_statement))
                            in_create = False
                            current_statement = []
                        else:
                            current_statement.append(line)
                
                # Execute CREATE TABLE statements with IF NOT EXISTS
                for statement in create_statements:
                    modified_statement = statement.replace('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS')
                    try:
                        self.cur.execute(modified_statement)
                    except sqlite3.Error as e:
                        print(f"Warning: Could not create table - {e}")
                
                self.conn.commit()
                print("Database structure verified/created.")
                
            except Exception as e:
                print(f"Warning: Could not load schema file - {e}")
                print("Proceeding with existing database structure...")
        else:
            print("Schema file not found. Using existing database structure...")
    
    def import_diggs_xml(self, xml_path):
        """Import DIGGS XML file into SQLite database"""
        print(f"Importing DIGGS XML file: {xml_path}")
        
        if not os.path.exists(xml_path):
            raise FileNotFoundError(f"XML file not found: {xml_path}")
        
        # Parse XML
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML file: {e}")
        
        # Verify this is a DIGGS file
        if not (root.tag.endswith('Diggs') or 'diggs' in root.tag.lower()):
            raise ValueError("This does not appear to be a DIGGS XML file")
        
        print("Parsing DIGGS XML structure...")
        
        # Create database structure if needed
        self.create_database_if_not_exists()
        
        # Import in dependency order
        self.import_projects(root)
        self.import_investigation_targets(root)
        self.import_sampling_features(root)
        self.import_samples(root)
        self.import_test_methods(root)
        self.import_observations(root)
        
        self.conn.commit()
        print("DIGGS XML import completed successfully!")
        
        # Print import summary
        self.print_import_summary()
    
    def import_projects(self, root):
        """Import Project elements"""
        projects = root.findall('.//Project', self.namespaces)
        if not projects:
            # Try without namespace
            projects = root.findall('.//Project')
        
        print(f"Importing {len(projects)} projects...")
        
        for project in projects:
            gml_id = project.get(f'{{{self.namespaces["gml"]}}}id')
            if not gml_id:
                gml_id = project.get('gml:id')
            
            if gml_id in self.imported_ids['projects']:
                continue
            
            # Extract project data
            name_elem = project.find('.//name')
            identifier_elem = project.find('.//internalIdentifier')
            description_elem = project.find('.//description')
            
            # Extract client information from role
            role_elem = project.find('.//role')
            client_name = None
            client_contact = None
            
            if role_elem is not None:
                org_elem = role_elem.find('.//organization')
                contact_elem = role_elem.find('.//contact')
                if org_elem is not None:
                    client_name = self.safe_text(org_elem)
                if contact_elem is not None:
                    client_contact = self.safe_text(contact_elem)
            
            # Create client record
            client_id = self.generate_id("CLIENT_")
            try:
                self.cur.execute('''INSERT OR IGNORE INTO "_Client" 
                                  ("_Client_ID", "clientName", "clientContact") 
                                  VALUES (?, ?, ?)''',
                               (client_id, client_name, client_contact))
            except sqlite3.Error:
                pass  # Table might not exist
            
            # Create project record
            project_id = self.generate_id("PROJ_")
            try:
                self.cur.execute('''INSERT OR IGNORE INTO "_Project" 
                                  ("_Project_ID", "_Client_ID", "projectName", "projectNumber", 
                                   "projectCountry", "projectState", "projectCounty", "coordinateDatum") 
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                               (project_id, client_id, self.safe_text(name_elem), 
                                self.safe_text(identifier_elem), None, None, None, None))
                
                self.imported_ids['projects'].add(gml_id)
                print(f"  Imported project: {self.safe_text(name_elem)}")
                
            except sqlite3.Error as e:
                print(f"  Warning: Could not import project - {e}")
    
    def import_investigation_targets(self, root):
        """Import Investigation Target elements"""
        targets = root.findall('.//InvestigationTarget', self.namespaces)
        if not targets:
            targets = root.findall('.//InvestigationTarget')
        
        print(f"Found {len(targets)} investigation targets (metadata only)")
    
    def import_sampling_features(self, root):
        """Import SamplingFeature elements (boreholes)"""
        features = root.findall('.//SamplingFeature', self.namespaces)
        if not features:
            features = root.findall('.//SamplingFeature')
        
        print(f"Importing {len(features)} sampling features...")
        
        for feature in features:
            gml_id = feature.get(f'{{{self.namespaces["gml"]}}}id')
            if not gml_id:
                gml_id = feature.get('gml:id')
            
            if gml_id in self.imported_ids['holes']:
                continue
            
            # Extract basic information
            name_elem = feature.find('.//name')
            description_elem = feature.find('.//description')
            
            # Extract coordinates from GML Point
            point_elem = feature.find('.//Point', self.namespaces)
            if not point_elem:
                point_elem = feature.find('.//Point')
            
            latitude = None
            longitude = None
            elevation = None
            
            if point_elem is not None:
                pos_elem = point_elem.find('.//pos', self.namespaces)
                if not pos_elem:
                    pos_elem = point_elem.find('.//pos')
                
                if pos_elem is not None and pos_elem.text:
                    coords = pos_elem.text.strip().split()
                    if len(coords) >= 2:
                        try:
                            latitude = float(coords[0])
                            longitude = float(coords[1])
                            if len(coords) >= 3:
                                elevation = float(coords[2])
                        except ValueError:
                            pass
            
            # Extract borehole details
            borehole_elem = feature.find('.//boreholeDetails')
            total_depth = None
            diameter = None
            termination = None
            
            if borehole_elem is not None:
                depth_elem = borehole_elem.find('.//totalDepth')
                diam_elem = borehole_elem.find('.//diameter')
                term_elem = borehole_elem.find('.//terminationReason')
                
                total_depth = self.safe_float(depth_elem)
                diameter = self.safe_float(diam_elem)
                termination = self.safe_text(term_elem)
            
            # Create rig record if drilling info exists
            rig_id = self.generate_id("RIG_")
            drilling_elem = feature.find('.//drillingInformation')
            if drilling_elem is not None:
                rig_desc_elem = drilling_elem.find('.//rigDescription')
                hammer_elem = drilling_elem.find('.//hammerType')
                efficiency_elem = drilling_elem.find('.//hammerEfficiency')
                
                try:
                    self.cur.execute('''INSERT OR IGNORE INTO "_Rig" 
                                      ("_rigID", "_rigDescription", "hammerType", "hammerEfficiency") 
                                      VALUES (?, ?, ?, ?)''',
                                   (rig_id, self.safe_text(rig_desc_elem), 
                                    self.safe_text(hammer_elem), self.safe_float(efficiency_elem)))
                except sqlite3.Error:
                    pass
            
            # Get project ID (use first available)
            project_id = None
            try:
                self.cur.execute('SELECT "_Project_ID" FROM "_Project" LIMIT 1')
                result = self.cur.fetchone()
                if result:
                    project_id = result[0]
            except sqlite3.Error:
                pass
            
            # Create hole record
            hole_id = self.generate_id("HOLE_")
            try:
                self.cur.execute('''INSERT OR IGNORE INTO "_HoleInfo" 
                                  ("_holeID", "_rigID", "_Project_ID", "holeName", "holeType",
                                   "topLatitude", "topLongitude", "groundSurface", "bottomDepth", "termination") 
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                               (hole_id, rig_id, project_id, self.safe_text(name_elem), 'boring',
                                latitude, longitude, elevation, total_depth, termination))
                
                self.imported_ids['holes'].add(gml_id)
                print(f"  Imported borehole: {self.safe_text(name_elem)}")
                
            except sqlite3.Error as e:
                print(f"  Warning: Could not import borehole - {e}")
    
    def import_samples(self, root):
        """Import Sample elements"""
        samples = root.findall('.//Sample', self.namespaces)
        if not samples:
            samples = root.findall('.//Sample')
        
        print(f"Importing {len(samples)} samples...")
        
        for sample in samples:
            gml_id = sample.get(f'{{{self.namespaces["gml"]}}}id')
            if not gml_id:
                gml_id = sample.get('gml:id')
            
            if gml_id in self.imported_ids['samples']:
                continue
            
            # Extract sample data
            name_elem = sample.find('.//name')
            
            # Extract depth interval
            depth_elem = sample.find('.//depthInterval')
            top_depth = None
            bottom_depth = None
            
            if depth_elem is not None:
                top_elem = depth_elem.find('.//topDepth')
                bottom_elem = depth_elem.find('.//bottomDepth')
                top_depth = self.safe_float(top_elem)
                bottom_depth = self.safe_float(bottom_elem)
            
            # Extract sampling method
            method_elem = sample.find('.//samplingMethod')
            
            # Find associated hole ID from samplingFeature reference
            hole_id = None
            sf_ref = sample.find('.//samplingFeature')
            if sf_ref is not None:
                href = sf_ref.get('gml:href') or sf_ref.get('href')
                if href and href.startswith('#'):
                    # This is a reference to a sampling feature
                    # For now, use the first available hole
                    try:
                        self.cur.execute('SELECT "_holeID" FROM "_HoleInfo" LIMIT 1')
                        result = self.cur.fetchone()
                        if result:
                            hole_id = result[0]
                    except sqlite3.Error:
                        pass
            
            # Create sample record
            sample_id = self.generate_id("SAMPLE_")
            try:
                self.cur.execute('''INSERT OR IGNORE INTO "_Samples" 
                                  ("_Sample_ID", "_holeID", "sampleName", "pos_topDepth", 
                                   "pos_bottomDepth", "sampleMethod") 
                                  VALUES (?, ?, ?, ?, ?, ?)''',
                               (sample_id, hole_id, self.safe_text(name_elem),
                                top_depth, bottom_depth, self.safe_text(method_elem)))
                
                self.imported_ids['samples'].add(gml_id)
                print(f"  Imported sample: {self.safe_text(name_elem)}")
                
            except sqlite3.Error as e:
                print(f"  Warning: Could not import sample - {e}")
    
    def import_test_methods(self, root):
        """Import test method information from test elements"""
        print("Extracting test methods...")
        
        # Look for test elements that contain method information
        test_elements = []
        for test_type in ['AtterbergLimitsTest', 'DrivenPenetrationTest', 'ConsolidationTest']:
            tests = root.findall(f'.//{test_type}', self.namespaces)
            if not tests:
                tests = root.findall(f'.//{test_type}')
            test_elements.extend(tests)
        
        methods_imported = set()
        
        for test in test_elements:
            method_elem = test.find('.//testMethod')
            if method_elem is not None:
                name_elem = method_elem.find('.//name')
                standard_elem = method_elem.find('.//standard')
                
                method_name = self.safe_text(name_elem)
                standard = self.safe_text(standard_elem)
                
                if method_name and method_name not in methods_imported:
                    method_id = self.generate_id("METHOD_")
                    try:
                        self.cur.execute('''INSERT OR IGNORE INTO "TestMethod" 
                                          ("_Method_ID", "methodName", "governingBody", "units", "modification") 
                                          VALUES (?, ?, ?, ?, ?)''',
                                       (method_id, method_name, standard, None, None))
                        methods_imported.add(method_name)
                        print(f"  Imported test method: {method_name}")
                    except sqlite3.Error:
                        pass
    
    def import_observations(self, root):
        """Import observation elements containing test data"""
        observations = root.findall('.//observation', self.namespaces)
        if not observations:
            observations = root.findall('.//observation')
        
        print(f"Importing {len(observations)} observations with test data...")
        
        for obs in observations:
            # Import Atterberg Limits tests
            atterberg_tests = obs.findall('.//AtterbergLimitsTest', self.namespaces)
            if not atterberg_tests:
                atterberg_tests = obs.findall('.//AtterbergLimitsTest')
            
            for test in atterberg_tests:
                self.import_atterberg_test(test, obs)
            
            # Import SPT tests
            spt_tests = obs.findall('.//DrivenPenetrationTest', self.namespaces)
            if not spt_tests:
                spt_tests = obs.findall('.//DrivenPenetrationTest')
            
            for test in spt_tests:
                self.import_spt_test(test, obs)
    
    def import_atterberg_test(self, test_elem, obs_elem):
        """Import Atterberg Limits test data"""
        # Get sample reference
        sample_ref = obs_elem.find('.//sample')
        sample_id = None
        
        if sample_ref is not None:
            href = sample_ref.get('gml:href') or sample_ref.get('href')
            if href:
                # For now, use first available sample
                try:
                    self.cur.execute('SELECT "_Sample_ID" FROM "_Samples" LIMIT 1')
                    result = self.cur.fetchone()
                    if result:
                        sample_id = result[0]
                except sqlite3.Error:
                    pass
        
        # Get method ID
        method_id = None
        try:
            self.cur.execute('SELECT "_Method_ID" FROM "TestMethod" WHERE "methodName" LIKE "%Atterberg%" OR "methodName" LIKE "%4318%" LIMIT 1')
            result = self.cur.fetchone()
            if result:
                method_id = result[0]
        except sqlite3.Error:
            pass
        
        # Extract test results
        results_elem = test_elem.find('.//testResults')
        if not results_elem:
            results_elem = test_elem.find('.//results')
        
        if results_elem is not None:
            pl_elem = results_elem.find('.//plasticLimit')
            ll_elem = results_elem.find('.//liquidLimit')
            pi_elem = results_elem.find('.//plasticityIndex')
            
            plastic_limit = self.safe_float(pl_elem)
            liquid_limit = self.safe_float(ll_elem)
            plasticity_index = self.safe_float(pi_elem)
            
            try:
                self.cur.execute('''INSERT OR IGNORE INTO "AtterbergLimits" 
                                  ("_Sample_ID", "_Method_ID", "plasticLimit", "liquidLimit", "plasticityIndex") 
                                  VALUES (?, ?, ?, ?, ?)''',
                               (sample_id, method_id, plastic_limit, liquid_limit, plasticity_index))
                print(f"    Imported Atterberg test: PL={plastic_limit}, LL={liquid_limit}")
            except sqlite3.Error as e:
                print(f"    Warning: Could not import Atterberg test - {e}")
    
    def import_spt_test(self, test_elem, obs_elem):
        """Import SPT test data"""
        # Get sample reference
        sample_ref = obs_elem.find('.//sample')
        sample_id = None
        
        if sample_ref is not None:
            href = sample_ref.get('gml:href') or sample_ref.get('href')
            if href:
                # For now, use first available sample
                try:
                    self.cur.execute('SELECT "_Sample_ID" FROM "_Samples" LIMIT 1')
                    result = self.cur.fetchone()
                    if result:
                        sample_id = result[0]
                except sqlite3.Error:
                    pass
        
        # Get method ID
        method_id = None
        try:
            self.cur.execute('SELECT "_Method_ID" FROM "TestMethod" WHERE "methodName" LIKE "%SPT%" OR "methodName" LIKE "%1586%" OR "methodName" LIKE "%Penetration%" LIMIT 1')
            result = self.cur.fetchone()
            if result:
                method_id = result[0]
        except sqlite3.Error:
            pass
        
        # Extract blow counts from increments
        increments_elem = test_elem.find('.//penetrationIncrements')
        if not increments_elem:
            increments_elem = test_elem.find('.//increments')
        
        blow_counts = [None, None, None, None]
        
        if increments_elem is not None:
            increments = increments_elem.findall('.//increment')
            for increment in increments:
                num_elem = increment.find('.//incrementNumber')
                blow_elem = increment.find('.//blowCount')
                
                if num_elem is not None and blow_elem is not None:
                    try:
                        increment_num = int(self.safe_text(num_elem))
                        blow_count = self.safe_int(blow_elem)
                        if 1 <= increment_num <= 4:
                            blow_counts[increment_num - 1] = blow_count
                    except (ValueError, TypeError):
                        pass
        
        # Extract recovery
        recovery_elem = test_elem.find('.//sampleRecovery')
        if not recovery_elem:
            recovery_elem = test_elem.find('.//recovery')
        recovery = self.safe_float(recovery_elem)
        
        try:
            self.cur.execute('''INSERT OR IGNORE INTO "_SPT" 
                              ("_Sample_ID", "_Method_ID", "blowCount_index1", "blowCount_index2", 
                               "blowCount_index3", "blowCount_index4", "recovery") 
                              VALUES (?, ?, ?, ?, ?, ?, ?)''',
                           (sample_id, method_id, blow_counts[0], blow_counts[1], 
                            blow_counts[2], blow_counts[3], recovery))
            print(f"    Imported SPT test: Blows={blow_counts}, Recovery={recovery}")
        except sqlite3.Error as e:
            print(f"    Warning: Could not import SPT test - {e}")
    
    def print_import_summary(self):
        """Print summary of imported data"""
        print("\n=== Import Summary ===")
        
        try:
            # Count records in each table
            tables_to_check = [
                ('_Project', 'Projects'),
                ('_HoleInfo', 'Boreholes'),
                ('_Samples', 'Samples'),
                ('TestMethod', 'Test Methods'),
                ('AtterbergLimits', 'Atterberg Tests'),
                ('_SPT', 'SPT Tests')
            ]
            
            for table_name, display_name in tables_to_check:
                try:
                    self.cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                    count = self.cur.fetchone()[0]
                    print(f"{display_name}: {count}")
                except sqlite3.Error:
                    print(f"{display_name}: Table not found")
                    
        except Exception as e:
            print(f"Could not generate summary: {e}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def main():
    import sys
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        
        # Get input parameters
        if len(sys.argv) > 1:
            xml_path = sys.argv[1]
        else:
            # Default to looking for DIGGS XML files in the parent directory
            xml_files = [f for f in os.listdir(parent_dir) if f.endswith('.xml') and 'diggs' in f.lower()]
            if xml_files:
                xml_path = os.path.join(parent_dir, xml_files[0])
                print(f"Using XML file: {xml_path}")
            else:
                print("No DIGGS XML file specified.")
                print("Usage: python diggs_to_sqlite_importer.py <path_to_diggs_xml>")
                print("Or place a DIGGS XML file in the parent directory.")
                return
        
        # Database path
        db_path = os.path.join(parent_dir, "GeoDataBase_imported.db")
        
        print("=== DIGGS to SQLite Importer ===")
        print(f"XML file: {xml_path}")
        print(f"Database: {db_path}")
        print()
        
        # Import DIGGS XML
        importer = DiggsToSQLiteImporter(db_path)
        importer.import_diggs_xml(xml_path)
        importer.close()
        
        print(f"\nImport completed! Database saved as: {db_path}")
        
    except Exception as e:
        print(f"Error during import: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()