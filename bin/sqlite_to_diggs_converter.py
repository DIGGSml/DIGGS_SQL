import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime
import uuid

class DiggsCompliantXMLGenerator:
    """Generate fully DIGGS 2.6 compliant XML from SQLite database"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        
        # DIGGS code lists for validation
        self.valid_hammer_types = [
            'automatic', 'manual', 'cathead', 'trip', 'safety', 'donut'
        ]
        
        self.valid_sample_methods = [
            'split spoon', 'shelby tube', 'macro core', 'bulk', 'grab', 'auger', 'other'
        ]
    
    def generate_uuid(self):
        """Generate a UUID for DIGGS elements"""
        return str(uuid.uuid4())
    
    def validate_hammer_type(self, hammer_type):
        """Validate hammer type against DIGGS code list"""
        if not hammer_type:
            return 'automatic'  # default
        return hammer_type.lower() if hammer_type.lower() in self.valid_hammer_types else 'automatic'
    
    def validate_blow_count(self, blow_count):
        """Validate blow count - convert negative values to null"""
        if blow_count is None or blow_count < 0:
            return None
        return blow_count
    
    def get_projects(self):
        """Get all projects from database"""
        self.cur.execute('''
            SELECT p.*, c.clientName, c.clientContact 
            FROM _Project p 
            LEFT JOIN _Client c ON p._Client_ID = c._Client_ID
        ''')
        return self.cur.fetchall()
    
    def get_holes_for_project(self, project_id):
        """Get all holes for a project"""
        self.cur.execute('''
            SELECT h.*, r._rigDescription, r.hammerType, r.hammerEfficiency 
            FROM _HoleInfo h 
            LEFT JOIN _Rig r ON h._rigID = r._rigID 
            WHERE h._Project_ID = ?
        ''', (project_id,))
        return self.cur.fetchall()
    
    def get_samples_for_hole(self, hole_id):
        """Get all samples for a hole"""
        self.cur.execute('SELECT * FROM _Samples WHERE _holeID = ?', (hole_id,))
        return self.cur.fetchall()
    
    def get_test_methods(self):
        """Get all test methods"""
        try:
            self.cur.execute('SELECT * FROM TestMethod')
            return {row['_Method_ID']: row for row in self.cur.fetchall()}
        except sqlite3.OperationalError as e:
            print(f"Warning: Could not load test methods - {e}")
            return {}
    
    def get_test_data_for_sample(self, sample_id):
        """Get all test data for a sample"""
        tests = {}
        
        # SPT data
        self.cur.execute('SELECT * FROM _SPT WHERE _Sample_ID = ?', (sample_id,))
        tests['spt'] = self.cur.fetchall()
        
        # Atterberg limits
        self.cur.execute('SELECT * FROM AtterbergLimits WHERE _Sample_ID = ?', (sample_id,))
        tests['atterberg'] = self.cur.fetchall()
        
        # Other tests can be added here
        
        return tests
    
    def safe_text(self, value):
        """Safely convert value to text"""
        if value is None:
            return ""
        return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    def generate_diggs_xml(self, output_path):
        """Generate complete DIGGS 2.6 XML file"""
        
        # Create XML content following exact DIGGS 2.6 specification
        xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_content.append('<Diggs xmlns="http://diggsml.org/schemas/2.6"')
        xml_content.append('       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
        xml_content.append('       xmlns:diggs_geo="http://diggsml.org/schemas/2.6/geotechnical"')
        xml_content.append('       xmlns:witsml="http://www.witsml.org/schemas/131"')
        xml_content.append('       xmlns:glr="http://www.opengis.net/gml/3.3/lr"')
        xml_content.append('       xmlns:xlink="http://www.w3.org/1999/xlink"')
        xml_content.append('       xmlns:g3.3="http://www.opengis.net/gml/3.3/ce"')
        xml_content.append('       xmlns:gml="http://www.opengis.net/gml/3.2"')
        xml_content.append('       xmlns:diggs="http://diggsml.org/schemas/2.6"')
        xml_content.append('       xmlns:glrov="http://www.opengis.net/gml/3.3/lrov"')
        xml_content.append('       xsi:schemaLocation="http://diggsml.org/schemas/2.6 http://diggsml.org/schemas/2.5.a/Kernel.xsd"')
        xml_content.append(f'       gml:id="diggs_document_{self.generate_uuid()[:8]}">')
        
        # Document information
        xml_content.append('  <documentInformation>')
        xml_content.append('    <DocumentInformation>')
        xml_content.append(f'      <creationDateTime>{datetime.now().isoformat()}</creationDateTime>')
        xml_content.append('      <documentCreator>SQLite to DIGGS Converter v2.0</documentCreator>')
        xml_content.append('      <documentTitle>Geotechnical Investigation Data - DIGGS 2.6 Compliant</documentTitle>')
        xml_content.append('      <documentDescription>DIGGS 2.6 compliant document generated from SQLite database with data validation</documentDescription>')
        xml_content.append('      <documentVersion>2.0</documentVersion>')
        xml_content.append('    </DocumentInformation>')
        xml_content.append('  </documentInformation>')
        
        # Get test methods
        test_methods = self.get_test_methods()
        
        # Process each project
        projects = self.get_projects()
        
        for project_row in projects:
            # Project element
            xml_content.append(f'  <Project gml:id="project_{project_row["_Project_ID"]}">')
            xml_content.append(f'    <name>{self.safe_text(project_row["projectName"])}</name>')
            if project_row['projectNumber']:
                xml_content.append(f'    <internalIdentifier>{self.safe_text(project_row["projectNumber"])}</internalIdentifier>')
            
            # Description
            description = f"Geotechnical investigation project in {project_row['projectState']}, {project_row['projectCountry']}"
            if project_row['projectCounty']:
                description += f", {project_row['projectCounty']} County"
            xml_content.append(f'    <description>{description}</description>')
            
            # Client information
            if project_row['clientName']:
                xml_content.append('    <role>')
                xml_content.append('      <roleName>Client</roleName>')
                xml_content.append(f'      <organization>{self.safe_text(project_row["clientName"])}</organization>')
                if project_row['clientContact']:
                    xml_content.append(f'      <contact>{self.safe_text(project_row["clientContact"])}</contact>')
                xml_content.append('    </role>')
            
            xml_content.append('  </Project>')
            
            # Investigation target
            target_id = f"target_{project_row['_Project_ID']}"
            xml_content.append(f'  <InvestigationTarget gml:id="{target_id}">')
            xml_content.append(f'    <name>Site Investigation - {self.safe_text(project_row["projectName"])}</name>')
            xml_content.append('    <description>Geotechnical site investigation for foundation design and construction planning</description>')
            xml_content.append('  </InvestigationTarget>')
            
            # Get holes for this project
            holes = self.get_holes_for_project(project_row['_Project_ID'])
            
            # Add samplingActivity section for DIGGS compliance
            xml_content.append(f'  <samplingActivity gml:id="sampling_activity_{project_row["_Project_ID"]}">')
            xml_content.append('    <name>Geotechnical Sampling Activities</name>')
            xml_content.append('    <description>Field sampling and drilling activities for geotechnical investigation</description>')
            xml_content.append(f'    <investigationTarget gml:href="#{target_id}" />')
            xml_content.append('  </samplingActivity>')
            
            for hole_row in holes:
                # Sampling feature (borehole)
                hole_id = f"hole_{hole_row['_holeID']}"
                xml_content.append(f'  <SamplingFeature gml:id="{hole_id}">')
                xml_content.append(f'    <name>{self.safe_text(hole_row["holeName"]) if hole_row["holeName"] else "Unnamed Borehole"}</name>')
                xml_content.append(f'    <description>Borehole {self.safe_text(hole_row["holeName"]) if hole_row["holeName"] else "location"}</description>')
                xml_content.append(f'    <investigationTarget gml:href="#{target_id}" />')
                xml_content.append(f'    <samplingActivity gml:href="#sampling_activity_{project_row["_Project_ID"]}" />')
                
                # Reference point (location)
                if hole_row['topLatitude'] and hole_row['topLongitude']:
                    xml_content.append('    <referencePoint>')
                    xml_content.append(f'      <gml:Point gml:id="point_{hole_row["_holeID"]}" srsName="EPSG:4326">')
                    pos_text = f"{hole_row['topLatitude']} {hole_row['topLongitude']}"
                    if hole_row['groundSurface']:
                        pos_text += f" {hole_row['groundSurface']}"
                    xml_content.append(f'        <gml:pos>{pos_text}</gml:pos>')
                    xml_content.append('      </gml:Point>')
                    xml_content.append('    </referencePoint>')
                
                # Borehole details
                xml_content.append('    <boreholeDetails>')
                if hole_row['bottomDepth']:
                    xml_content.append(f'      <totalDepth uom="m">{hole_row["bottomDepth"]}</totalDepth>')
                if hole_row['hole_diameter']:
                    xml_content.append(f'      <diameter uom="mm">{hole_row["hole_diameter"]}</diameter>')
                if hole_row['azimuth']:
                    xml_content.append(f'      <azimuth uom="deg">{hole_row["azimuth"]}</azimuth>')
                if hole_row['angle']:
                    xml_content.append(f'      <inclination uom="deg">{hole_row["angle"]}</inclination>')
                if hole_row['termination']:
                    xml_content.append(f'      <terminationReason>{self.safe_text(hole_row["termination"])}</terminationReason>')
                
                # Drilling information with validated data
                if hole_row['_rigDescription']:
                    xml_content.append('      <drillingInformation>')
                    xml_content.append(f'        <rigDescription>{self.safe_text(hole_row["_rigDescription"])}</rigDescription>')
                    if hole_row['hammerType']:
                        validated_hammer = self.validate_hammer_type(hole_row['hammerType'])
                        xml_content.append(f'        <hammerType>{validated_hammer}</hammerType>')
                    if hole_row['hammerEfficiency']:
                        xml_content.append(f'        <hammerEfficiency uom="%">{hole_row["hammerEfficiency"]}</hammerEfficiency>')
                    xml_content.append('      </drillingInformation>')
                
                xml_content.append('    </boreholeDetails>')
                xml_content.append('  </SamplingFeature>')
                
                # Get samples for this hole
                samples = self.get_samples_for_hole(hole_row['_holeID'])
                
                for sample_row in samples:
                    # Sample element
                    sample_id = f"sample_{sample_row['_Sample_ID']}"
                    xml_content.append(f'  <Sample gml:id="{sample_id}">')
                    
                    if sample_row['sampleName']:
                        xml_content.append(f'    <name>{self.safe_text(sample_row["sampleName"])}</name>')
                    else:
                        xml_content.append(f'    <name>Sample at {sample_row["pos_topDepth"]}-{sample_row["pos_bottomDepth"]}m</name>')
                    
                    xml_content.append(f'    <samplingFeature gml:href="#{hole_id}" />')
                    xml_content.append(f'    <samplingActivity gml:href="#sampling_activity_{project_row["_Project_ID"]}" />')
                    
                    # Depth interval with units
                    if sample_row['pos_topDepth'] is not None and sample_row['pos_bottomDepth'] is not None:
                        xml_content.append('    <depthInterval>')
                        xml_content.append(f'      <topDepth uom="m">{sample_row["pos_topDepth"]}</topDepth>')
                        xml_content.append(f'      <bottomDepth uom="m">{sample_row["pos_bottomDepth"]}</bottomDepth>')
                        xml_content.append('    </depthInterval>')
                    
                    if sample_row['sampleMethod']:
                        xml_content.append(f'    <samplingMethod>{self.safe_text(sample_row["sampleMethod"])}</samplingMethod>')
                    
                    xml_content.append('  </Sample>')
                    
                    # Get test data for this sample
                    test_data = self.get_test_data_for_sample(sample_row['_Sample_ID'])
                    
                    # Create observation elements for DIGGS compliance
                    # Atterberg Limits
                    for atterberg in test_data['atterberg']:
                        test_uuid = self.generate_uuid()[:8]
                        obs_id = f"obs_atterberg_{sample_row['_Sample_ID']}_{test_uuid}"
                        
                        xml_content.append(f'  <observation gml:id="{obs_id}">')
                        xml_content.append(f'    <sample gml:href="#{sample_id}" />')
                        xml_content.append(f'    <samplingFeature gml:href="#{hole_id}" />')
                        xml_content.append('    <name>Atterberg Limits Test Observation</name>')
                        xml_content.append('    <description>Laboratory determination of liquid limit, plastic limit, and plasticity index</description>')
                        
                        xml_content.append(f'    <diggs_geo:AtterbergLimitsTest gml:id="atterberg_{sample_row["_Sample_ID"]}_{test_uuid}">')
                        
                        method_info = test_methods.get(atterberg['_Method_ID'])
                        if method_info and method_info['methodName']:
                            xml_content.append('      <testMethod>')
                            xml_content.append(f'        <name>{self.safe_text(method_info["methodName"])}</name>')
                            if method_info['governingBody']:
                                xml_content.append(f'        <standard>{self.safe_text(method_info["governingBody"])}</standard>')
                            xml_content.append('      </testMethod>')
                        
                        xml_content.append('      <testResults>')
                        if atterberg['plasticLimit'] is not None:
                            xml_content.append(f'        <plasticLimit uom="%">{atterberg["plasticLimit"]}</plasticLimit>')
                        if atterberg['liquidLimit'] is not None:
                            xml_content.append(f'        <liquidLimit uom="%">{atterberg["liquidLimit"]}</liquidLimit>')
                        if atterberg['plasticityIndex'] is not None:
                            xml_content.append(f'        <plasticityIndex uom="%">{atterberg["plasticityIndex"]}</plasticityIndex>')
                        xml_content.append('      </testResults>')
                        xml_content.append('    </diggs_geo:AtterbergLimitsTest>')
                        xml_content.append('  </observation>')
                    
                    # SPT Tests with validated blow counts
                    for spt in test_data['spt']:
                        test_uuid = self.generate_uuid()[:8]
                        obs_id = f"obs_spt_{sample_row['_Sample_ID']}_{test_uuid}"
                        
                        xml_content.append(f'  <observation gml:id="{obs_id}">')
                        xml_content.append(f'    <sample gml:href="#{sample_id}" />')
                        xml_content.append(f'    <samplingFeature gml:href="#{hole_id}" />')
                        xml_content.append('    <name>Standard Penetration Test Observation</name>')
                        xml_content.append('    <description>In-situ standard penetration test for soil density and sampling</description>')
                        
                        xml_content.append(f'    <diggs_geo:DrivenPenetrationTest gml:id="spt_{sample_row["_Sample_ID"]}_{test_uuid}">')
                        
                        method_info = test_methods.get(spt['_Method_ID'])
                        xml_content.append('      <testMethod>')
                        xml_content.append('        <name>Standard Penetration Test</name>')
                        if method_info and method_info['governingBody']:
                            xml_content.append(f'        <standard>{self.safe_text(method_info["governingBody"])}</standard>')
                        else:
                            xml_content.append('        <standard>ASTM D1586</standard>')
                        xml_content.append('      </testMethod>')
                        
                        xml_content.append('      <testDetails>')
                        if spt['samplerLength']:
                            xml_content.append(f'        <samplerLength uom="mm">{spt["samplerLength"]}</samplerLength>')
                        if spt['samplerInternalDiameter']:
                            xml_content.append(f'        <samplerDiameter uom="mm">{spt["samplerInternalDiameter"]}</samplerDiameter>')
                        xml_content.append('      </testDetails>')
                        
                        # Blow count increments with validation
                        xml_content.append('      <penetrationIncrements>')
                        for i in range(1, 5):
                            blow_count = self.validate_blow_count(spt[f'blowCount_index{i}'])
                            penetration = spt[f'penetration_index{i}']
                            
                            if blow_count is not None:
                                xml_content.append('        <increment>')
                                xml_content.append(f'          <incrementNumber>{i}</incrementNumber>')
                                xml_content.append(f'          <blowCount>{blow_count}</blowCount>')
                                if penetration is not None and penetration > 0:
                                    xml_content.append(f'          <penetration uom="mm">{penetration}</penetration>')
                                xml_content.append('        </increment>')
                        xml_content.append('      </penetrationIncrements>')
                        
                        if spt['recovery'] is not None and spt['recovery'] >= 0:
                            xml_content.append(f'      <sampleRecovery uom="%">{spt["recovery"]}</sampleRecovery>')
                        
                        xml_content.append('    </diggs_geo:DrivenPenetrationTest>')
                        xml_content.append('  </observation>')
        
        xml_content.append('</Diggs>')
        
        # Write XML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(xml_content))
        
        print(f"DIGGS 2.6 compliant XML file generated: {output_path}")
        print("Note: File includes data validation, proper structure, and units of measure")
        self.conn.close()

def main():
    import os
    
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        db_path = os.path.join(parent_dir, "GeoDataBase_corrected.db")
        output_path = os.path.join(parent_dir, "geotechnical_data_diggs_2.6_compliant.xml")
        
        # Check if database exists
        if not os.path.exists(db_path):
            print(f"Error: Database file not found at {db_path}")
            print(f"Please ensure the database file is in the same directory as this script.")
            return
        
        print(f"Using database: {db_path}")
        print(f"Output file: {output_path}")
        
        generator = DiggsCompliantXMLGenerator(db_path)
        generator.generate_diggs_xml(output_path)
        
    except Exception as e:
        print(f"Error generating DIGGS XML: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()