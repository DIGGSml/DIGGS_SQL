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

        # Map GML IDs to database IDs for lookups
        self.gml_id_mapping = {
            'projects': {},  # gml_id -> db_id
            'holes': {},     # gml_id -> db_id
            'samples': {},   # gml_id -> db_id
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

    def find_element(self, parent, tag_name, use_gml=False):
        """Find element with namespace awareness"""
        ns_prefix = 'gml' if use_gml else 'diggs'

        # Debug for blowCount specifically
        debug_this = tag_name == 'blowCount' and not hasattr(self, '_blowcount_debug')
        if debug_this:
            self._blowcount_debug = True
            print(f"    DEBUG find_element: Looking for {tag_name}, ns_prefix={ns_prefix}")
            print(f"    DEBUG find_element: namespaces={self.namespaces}")

        # Try with namespace prefix
        elem = parent.find(f'.//{ns_prefix}:{tag_name}', self.namespaces)
        if debug_this:
            print(f"    DEBUG find_element: Try 1 (.//diggs:blowCount) = {elem is not None}")

        if elem is None:
            # Try with full namespace
            elem = parent.find(f'.//{{{self.namespaces[ns_prefix]}}}{tag_name}')
            if debug_this:
                print(f"    DEBUG find_element: Try 2 (full NS) = {elem is not None}")

        if elem is None:
            # Try without namespace
            elem = parent.find(f'.//{tag_name}')
            if debug_this:
                print(f"    DEBUG find_element: Try 3 (no NS) = {elem is not None}")

        return elem

    def findall_elements(self, parent, tag_name, use_gml=False):
        """Find all elements with namespace awareness"""
        ns_prefix = 'gml' if use_gml else 'diggs'
        # Try with namespace prefix
        elems = parent.findall(f'.//{ns_prefix}:{tag_name}', self.namespaces)
        if not elems:
            # Try with full namespace
            elems = parent.findall(f'.//{{{self.namespaces[ns_prefix]}}}{tag_name}')
        if not elems:
            # Try without namespace
            elems = parent.findall(f'.//{tag_name}')
        return elems
    
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

        # Detect actual namespace from root element
        if root.tag.startswith('{'):
            actual_ns = root.tag.split('}')[0][1:]
            print(f"Detected DIGGS namespace: {actual_ns}")
            # Update namespace if different
            if actual_ns != self.namespaces['diggs']:
                self.namespaces['diggs'] = actual_ns

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
        # Use helper method for namespace-aware search
        projects = self.findall_elements(root, 'Project')

        print(f"Importing {len(projects)} projects...")

        for project in projects:
            gml_id = project.get(f'{{{self.namespaces["gml"]}}}id')
            if not gml_id:
                gml_id = project.get('gml:id')

            if gml_id in self.imported_ids['projects']:
                continue

            # Extract project data - use GML namespace for these standard elements
            name_elem = self.find_element(project, 'name', use_gml=True)
            identifier_elem = self.find_element(project, 'internalIdentifier')
            description_elem = self.find_element(project, 'description', use_gml=True)
            
            # Extract client information from role
            role_elem = self.find_element(project, 'role')
            client_name = None
            client_contact = None

            if role_elem is not None:
                # Look for BusinessAssociate name
                ba_elem = self.find_element(role_elem, 'BusinessAssociate')
                if ba_elem is not None:
                    ba_name_elem = self.find_element(ba_elem, 'name', use_gml=True)
                    if ba_name_elem is not None:
                        client_name = self.safe_text(ba_name_elem)
            
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
        # Search for Borehole elements specifically
        features = self.findall_elements(root, 'Borehole')

        print(f"Importing {len(features)} sampling features...")

        for feature in features:
            gml_id = feature.get(f'{{{self.namespaces["gml"]}}}id')
            if not gml_id:
                gml_id = feature.get('gml:id')

            if gml_id in self.imported_ids['holes']:
                continue

            # Extract basic information
            name_elem = self.find_element(feature, 'name', use_gml=True)
            description_elem = self.find_element(feature, 'description', use_gml=True)

            # Extract coordinates from GML Point
            point_elem = self.find_element(feature, 'Point', use_gml=True)
            
            latitude = None
            longitude = None
            elevation = None
            
            if point_elem is not None:
                pos_elem = self.find_element(point_elem, 'pos', use_gml=True)

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
            rig_id = None
            drilling_elem = self.find_element(feature, 'drillingInformation')
            if drilling_elem is not None:
                rig_id = self.generate_id("RIG_")
                rig_desc_elem = self.find_element(drilling_elem, 'rigDescription')
                hammer_elem = self.find_element(drilling_elem, 'hammerType')
                efficiency_elem = self.find_element(drilling_elem, 'hammerEfficiency')

                try:
                    self.cur.execute('''INSERT OR IGNORE INTO "_Rig"
                                      ("_rigID", "_rigDescription", "hammerType", "hammerEfficiency")
                                      VALUES (?, ?, ?, ?)''',
                                   (rig_id, self.safe_text(rig_desc_elem),
                                    self.safe_text(hammer_elem), self.safe_float(efficiency_elem)))
                except sqlite3.Error as e:
                    print(f"  Warning: Could not create rig - {e}")
                    rig_id = None
            
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
                # Store the mapping from GML ID to database ID
                self.gml_id_mapping['holes'][gml_id] = hole_id
                print(f"  Imported borehole: {self.safe_text(name_elem)}")
                
            except sqlite3.Error as e:
                print(f"  Warning: Could not import borehole - {e}")
    
    def import_samples(self, root):
        """Import Sample elements"""
        # Use helper method for namespace-aware search
        samples = self.findall_elements(root, 'Sample')

        print(f"Importing {len(samples)} samples...")
        
        for sample in samples:
            gml_id = sample.get(f'{{{self.namespaces["gml"]}}}id')
            if not gml_id:
                gml_id = sample.get('gml:id')
            
            if gml_id in self.imported_ids['samples']:
                continue
            
            # Extract sample data
            name_elem = self.find_element(sample, 'name', use_gml=True)

            # Extract depth interval
            depth_elem = self.find_element(sample, 'depthInterval')
            top_depth = None
            bottom_depth = None

            if depth_elem is not None:
                top_elem = self.find_element(depth_elem, 'topDepth')
                bottom_elem = self.find_element(depth_elem, 'bottomDepth')
                top_depth = self.safe_float(top_elem)
                bottom_depth = self.safe_float(bottom_elem)

            # Extract sampling method
            method_elem = self.find_element(sample, 'samplingMethod')

            # Find associated hole ID from samplingActivityRef (samples link to activities, not directly to boreholes)
            hole_id = None
            activity_ref = self.find_element(sample, 'samplingActivityRef')
            if activity_ref is not None:
                href = activity_ref.get('{http://www.w3.org/1999/xlink}href')
                if href and href.startswith('#'):
                    # For now, just use first available hole
                    # TODO: Parse sampling activities to link properly
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
                # Store the mapping from GML ID to database ID
                self.gml_id_mapping['samples'][gml_id] = sample_id
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
        """Import measurement/Test elements containing test data"""
        # Search for measurement elements containing Test elements
        measurements = self.findall_elements(root, 'measurement')

        print(f"Importing {len(measurements)} measurements with test data...")

        if len(measurements) == 0:
            print("  Warning: No measurements found, trying alternate search methods...")
            # Debug: try different approaches
            measurements = root.findall('.//diggs:measurement', self.namespaces)
            print(f"  Found {len(measurements)} with direct namespace search")

        tests_imported = 0
        tests_found = 0
        tests_with_procedure = 0

        for i, measurement in enumerate(measurements):
            # Get the Test element
            test = self.find_element(measurement, 'Test')
            if test:
                tests_found += 1
                # Check if it has procedure
                procedure = self.find_element(test, 'procedure')
                if procedure:
                    tests_with_procedure += 1

                # Import test based on procedure type
                if self.import_test_from_measurement(test):
                    tests_imported += 1

            # Show progress every 500 tests
            if i > 0 and i % 500 == 0:
                print(f"  Processed {i}/{len(measurements)} measurements...")

        print(f"  Tests found: {tests_found}, with procedure: {tests_with_procedure}")
        if hasattr(self, '_spt_count'):
            print(f"  SPT tests found: {self._spt_count}, imported: {self._spt_success}")
        print(f"  Successfully imported {tests_imported} test records")
        return

        # OLD CODE BELOW - keep for reference of observation-based import
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

    def import_test_from_measurement(self, test_element):
        """Import a single test from a measurement/Test element"""
        try:
            # Get borehole reference
            sampling_ref = self.find_element(test_element, 'samplingFeatureRef')
            hole_id = None

            if sampling_ref is not None:
                href = sampling_ref.get('{http://www.w3.org/1999/xlink}href')
                if href:
                    # Extract the borehole ID from href (e.g., "#Location_B-01")
                    borehole_gml_id = href.lstrip('#')
                    # Find corresponding hole in database
                    self.cur.execute('SELECT "_holeID", "holeName" FROM "_HoleInfo"')
                    # For now, match by extracting the hole name from the test
                    test_name = self.find_element(test_element, 'name', use_gml=True)
                    test_name_text = self.safe_text(test_name)

            # Get the procedure element to determine test type
            procedure = self.find_element(test_element, 'procedure')
            if procedure is None:
                return False

            # Check what type of test is in the procedure
            spt_test = self.find_element(procedure, 'DrivenPenetrationTest')
            if spt_test:
                result = self.import_spt_from_procedure(spt_test, test_element)
                if not hasattr(self, '_spt_count'):
                    self._spt_count = 0
                    self._spt_success = 0
                self._spt_count += 1
                if result:
                    self._spt_success += 1
                return result

            atterberg_test = self.find_element(procedure, 'AtterbergLimitsTest')
            if atterberg_test:
                return self.import_atterberg_from_procedure(atterberg_test, test_element)

            # Add more test types as needed
            return False

        except Exception as e:
            print(f"    Warning: Error importing test - {e}")
            return False

    def import_spt_from_procedure(self, spt_elem, test_elem):
        """Import SPT test data from procedure element"""
        debug_first = not hasattr(self, '_spt_debug_done')
        if debug_first:
            self._spt_debug_done = True

        try:
            # Get test location (depth)
            outcome = self.find_element(test_elem, 'outcome')
            test_result = self.find_element(outcome, 'TestResult') if outcome else None
            location_elem = self.find_element(test_result, 'location') if test_result else None

            top_depth = None
            bottom_depth = None

            if location_elem:
                pos_list = self.find_element(location_elem, 'posList', use_gml=True)
                if pos_list and pos_list.text:
                    coords = pos_list.text.strip().split()
                    if len(coords) >= 2:
                        top_depth = self.safe_float(type('obj', (), {'text': coords[0]})())
                        bottom_depth = self.safe_float(type('obj', (), {'text': coords[1]})())

            # Get N-value from results
            n_value = None
            if test_result:
                results = self.find_element(test_result, 'results')
                if results:
                    result_set = self.find_element(results, 'ResultSet')
                    if result_set:
                        data_values = self.find_element(result_set, 'dataValues')
                        if data_values and data_values.text:
                            n_value = self.safe_int(data_values)

            # Get blow counts from drive sets
            drive_sets = self.findall_elements(spt_elem, 'driveSet')
            blow_counts = []

            if debug_first:
                print(f"    DEBUG: Found {len(drive_sets)} driveSets in SPT")

            for ds_idx, ds in enumerate(drive_sets):
                drive_set_elem = self.find_element(ds, 'DriveSet')
                if drive_set_elem:
                    if debug_first and ds_idx == 0:
                        print(f"    DEBUG: DriveSet tag = {drive_set_elem.tag}")
                        print(f"    DEBUG: DriveSet children = {[c.tag for c in list(drive_set_elem)[:5]]}")
                        print(f"    DEBUG: Namespace dict = {self.namespaces}")
                        # Try manual search
                        manual1 = drive_set_elem.find('.//diggs:blowCount', self.namespaces)
                        manual2 = drive_set_elem.find('.//{http://diggsml.org/schema-dev}blowCount')
                        print(f"    DEBUG: Manual diggs:blowCount = {manual1 is not None}")
                        print(f"    DEBUG: Manual full NS = {manual2 is not None}")

                    blow_count_elem = self.find_element(drive_set_elem, 'blowCount')
                    if blow_count_elem is not None:  # IMPORTANT: Elements evaluate to False in Python!
                        bc = self.safe_int(blow_count_elem)
                        if bc is not None:
                            blow_counts.append(bc)
                            if debug_first:
                                print(f"    DEBUG: blowCount = {bc}")
                        elif debug_first:
                            print(f"    DEBUG: blowCount is None, text={blow_count_elem.text}")
                    elif debug_first:
                        print(f"    DEBUG: blow_count_elem not found")
                elif debug_first:
                    print(f"    DEBUG: drive_set_elem not found")

            # Get borehole reference
            sampling_ref = self.find_element(test_elem, 'samplingFeatureRef')
            hole_id = None

            if sampling_ref is not None:
                href = sampling_ref.get('{http://www.w3.org/1999/xlink}href')
                if href:
                    borehole_gml_id = href.lstrip('#')
                    # Look up the database ID using the GML ID mapping
                    hole_id = self.gml_id_mapping['holes'].get(borehole_gml_id)
                    if not hole_id and debug_first:
                        print(f"    DEBUG: Borehole GML ID '{borehole_gml_id}' not found in mapping!")
                        print(f"    DEBUG: Available mappings: {list(self.gml_id_mapping['holes'].keys())[:5]}")

            # Get total penetration from SPT element
            total_pen_elem = self.find_element(spt_elem, 'totalPenetration')
            total_penetration = self.safe_float(total_pen_elem)

            # Insert SPT test - NOTE: SPT table uses _Sample_ID, not _holeID
            # For now, we'll skip SPT import until we can properly link tests to samples
            # Tests need to reference samples, but we need to determine which sample each test belongs to

            if debug_first:
                print(f"    DEBUG SPT: hole_id={hole_id}, blow_counts={blow_counts}, depth={top_depth}-{bottom_depth}, total_pen={total_penetration}")
                print(f"    DEBUG: SPT import requires sample linkage - skipping for now")

            # TODO: Implement proper SPT import with sample linkage
            # The database schema requires:
            # - _Sample_ID (need to link test to sample)
            # - blowCount_index1, blowCount_index2, blowCount_index3 (we have these)
            # - penetration_index1, penetration_index2, penetration_index3 (need to extract)

            return False

        except sqlite3.Error as e:
            print(f"    Warning: Could not import SPT test - {e}")
            return False

    def import_atterberg_from_procedure(self, atterberg_elem, test_elem):
        """Import Atterberg test data from procedure element"""
        # TODO: Implement Atterberg limits import
        return False

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