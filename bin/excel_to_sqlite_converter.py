import pandas as pd
import sqlite3
import uuid
import os
from datetime import datetime

class ExcelToSQLiteConverter:
    """Convert Excel files to SQLite database with DIGGS structure"""
    
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.parent_dir = os.path.dirname(self.script_dir)
    
    def create_database_structure(self, db_path):
        """Create the SQLite database with exact DIGGS structure"""
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        cur.execute('PRAGMA foreign_keys = ON;')
        
        # Use exact table definitions from DIGGS sqlite.py
        tables = [
            '''CREATE TABLE IF NOT EXISTS "_Rig" (
              "_rigID" TEXT PRIMARY KEY,
              "_rigDescription" TEXT,
              "hammerType" TEXT,
              "hammerEfficiency" REAL,
              "miscID" TEXT
            );''',
            
            '''CREATE TABLE IF NOT EXISTS "_Client" (
              "_Client_ID" TEXT PRIMARY KEY,
              "clientName" TEXT,
              "clientContact" TEXT
            );''',
            
            '''CREATE TABLE IF NOT EXISTS "_Project" (
              "_Project_ID" TEXT PRIMARY KEY,
              "_Client_ID" TEXT,
              "projectName" TEXT,
              "projectNumber" TEXT,
              "projectCountry" TEXT,
              "projectState" TEXT,
              "projectCounty" TEXT,
              "coordinateDatum" TEXT,
              FOREIGN KEY ("_Client_ID") REFERENCES "_Client" ("_Client_ID")
            );''',
            
            '''CREATE TABLE IF NOT EXISTS "_HoleInfo" (
              "_holeID" TEXT PRIMARY KEY,
              "_rigID" TEXT,
              "_Project_ID" TEXT,
              "holeName" TEXT,
              "holeType" TEXT,
              "topLatitude" REAL,
              "topLongitude" REAL,
              "groundSurface" REAL,
              "azimuth" REAL,
              "angle" REAL,
              "bottomDepth" REAL,
              "timeInterval_start" TEXT,
              "timeInterval_end" TEXT,
              "hole_diameter" REAL,
              "termination" TEXT,
              FOREIGN KEY ("_rigID") REFERENCES "_Rig" ("_rigID"),
              FOREIGN KEY ("_Project_ID") REFERENCES "_Project" ("_Project_ID")
            );''',
            
            '''CREATE TABLE IF NOT EXISTS "TestMethod" (
              "_Method_ID" TEXT PRIMARY KEY,
              "methodName" TEXT,
              "description" TEXT,
              "governingBody" TEXT,
              "units" TEXT,
              "modification" TEXT
            );''',
            
            '''CREATE TABLE IF NOT EXISTS "_Samples" (
              "_Sample_ID" TEXT PRIMARY KEY,
              "_holeID" TEXT,
              "sampleName" TEXT,
              "pos_topDepth" REAL,
              "pos_bottomDepth" REAL,
              "sampleMethod" TEXT,
              FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID")
            );''',
            
            '''CREATE TABLE IF NOT EXISTS "_SPT" (
              "_Sample_ID" TEXT,
              "_Method_ID" TEXT,
              "blowCount_index1" INTEGER,
              "blowCount_index2" INTEGER,
              "blowCount_index3" INTEGER,
              "blowCount_index4" INTEGER,
              "penetration_index1" REAL,
              "penetration_index2" REAL,
              "penetration_index3" REAL,
              "penetration_index4" REAL,
              "samplerLength" REAL,
              "samplerInternalDiameter" REAL,
              "recovery" REAL,
              FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
              FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
            );''',
            
            '''CREATE TABLE IF NOT EXISTS "AtterbergLimits" (
              "_Sample_ID" TEXT,
              "_Method_ID" TEXT,
              "plasticLimit" REAL,
              "liquidLimit" REAL,
              "plasticityIndex" REAL,
              FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
              FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
            );''',
            
            '''CREATE TABLE IF NOT EXISTS "_waterLevels" (
              "_holeID" TEXT,
              "waterDepth" REAL,
              "TimeInterval_start" TEXT,
              "TimeInterval_end" TEXT,
              FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID")
            );'''
        ]
        
        for table_sql in tables:
            cur.execute(table_sql)
        
        conn.commit()
        return conn, cur
    
    def generate_id(self, prefix=""):
        """Generate a unique ID"""
        return f"{prefix}{str(uuid.uuid4())[:8]}"
    
    def safe_get(self, row, key, default=None):
        """Safely get value from pandas row, handling NaN/NaT values and timestamps"""
        value = row.get(key, default)
        if pd.isna(value):
            return default
        if hasattr(value, 'strftime'):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return value
    
    def convert_excel_to_sqlite(self, excel_path, db_path):
        """Convert Excel file to SQLite database following exact DIGGS structure"""
        
        conn, cur = self.create_database_structure(db_path)
        excel_file = pd.ExcelFile(excel_path)
        
        # Track created IDs for foreign key relationships
        client_ids = {}
        project_ids = {}
        rig_ids = {}
        hole_ids = {}
        sample_ids = {}
        method_ids = {}
        
        # Process Project sheet
        if 'Project' in excel_file.sheet_names:
            df = pd.read_excel(excel_path, sheet_name='Project')
            for _, row in df.iterrows():
                # Create client
                client_key = f"{self.safe_get(row, 'clientName', '')}_{self.safe_get(row, 'clientContact', '')}"
                if client_key not in client_ids:
                    client_id = self.generate_id("CLIENT_")
                    client_ids[client_key] = client_id
                    cur.execute('''INSERT INTO "_Client" ("_Client_ID", "clientName", "clientContact") 
                                  VALUES (?, ?, ?)''', 
                               (client_id, self.safe_get(row, 'clientName'), self.safe_get(row, 'clientContact')))
                
                # Create project
                project_id = self.generate_id("PROJ_")
                project_key = f"{self.safe_get(row, 'projectName', '')}_{self.safe_get(row, 'projectNumber', '')}"
                project_ids[project_key] = project_id
                
                cur.execute('''INSERT INTO "_Project" 
                              ("_Project_ID", "_Client_ID", "projectName", "projectNumber", 
                               "projectCountry", "projectState", "projectCounty", "coordinateDatum") 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                           (project_id, client_ids[client_key], self.safe_get(row, 'projectName'), 
                            self.safe_get(row, 'projectNumber'), self.safe_get(row, 'projectCountry'), 
                            self.safe_get(row, 'projectState'), self.safe_get(row, 'projectCounty'), 
                            self.safe_get(row, 'coordinateDatum')))
        
        # Process TestMethod sheet
        if 'TestMethod' in excel_file.sheet_names:
            df = pd.read_excel(excel_path, sheet_name='TestMethod')
            for _, row in df.iterrows():
                method_id = self.generate_id("METHOD_")
                method_key = self.safe_get(row, 'methodName', '')
                method_ids[method_key] = method_id
                
                cur.execute('''INSERT INTO "TestMethod" 
                              ("_Method_ID", "methodName", "governingBody", "units", "modification") 
                              VALUES (?, ?, ?, ?, ?)''',
                           (method_id, self.safe_get(row, 'methodName'), 
                            self.safe_get(row, 'governingBody'), self.safe_get(row, 'units'), 
                            self.safe_get(row, 'modification')))
        
        # Process HoleInfo sheet
        if 'HoleInfo' in excel_file.sheet_names:
            df = pd.read_excel(excel_path, sheet_name='HoleInfo')
            for _, row in df.iterrows():
                # Create rig if needed
                rig_key = f"{self.safe_get(row, '_rigDescription', '')}_{self.safe_get(row, 'hammerType', '')}"
                if rig_key not in rig_ids:
                    rig_id = self.generate_id("RIG_")
                    rig_ids[rig_key] = rig_id
                    cur.execute('''INSERT INTO "_Rig" ("_rigID", "_rigDescription", "hammerType", "hammerEfficiency", "miscID") 
                                  VALUES (?, ?, ?, ?, ?)''',
                               (rig_id, self.safe_get(row, '_rigDescription'), self.safe_get(row, 'hammerType'), 
                                self.safe_get(row, 'hammerEfficiency'), self.safe_get(row, 'miscID')))
                
                # Create hole
                hole_id = self.generate_id("HOLE_")
                hole_key = self.safe_get(row, 'holeName', '')
                hole_ids[hole_key] = hole_id
                
                # Get project ID (assume first project if multiple)
                project_id = list(project_ids.values())[0] if project_ids else None
                
                cur.execute('''INSERT INTO "_HoleInfo" 
                              ("_holeID", "_rigID", "_Project_ID", "holeName", "holeType", 
                               "topLatitude", "topLongitude", "groundSurface", "azimuth", "angle", 
                               "bottomDepth", "timeInterval_start", "timeInterval_end", "hole_diameter", "termination") 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (hole_id, rig_ids[rig_key], project_id, self.safe_get(row, 'holeName'), 
                            self.safe_get(row, 'holeType'), self.safe_get(row, 'topLatitude'), 
                            self.safe_get(row, 'topLongitude'), self.safe_get(row, 'groundSurface'),
                            self.safe_get(row, 'azimuth'), self.safe_get(row, 'angle'), 
                            self.safe_get(row, 'bottomDepth'), self.safe_get(row, 'timeInterval_start'), 
                            self.safe_get(row, 'timeInterval_end'), None, self.safe_get(row, 'termination')))
        
        # Process Samples sheet
        if 'Samples' in excel_file.sheet_names:
            df = pd.read_excel(excel_path, sheet_name='Samples')
            for _, row in df.iterrows():
                sample_id = self.generate_id("SAMPLE_")
                hole_name = self.safe_get(row, 'Hole Name', '')
                hole_id = hole_ids.get(hole_name)
                
                if hole_id:
                    sample_key = f"{hole_name}_{self.safe_get(row, 'Sample Name', '')}"
                    sample_ids[sample_key] = sample_id
                    
                    cur.execute('''INSERT INTO "_Samples" 
                                  ("_Sample_ID", "_holeID", "sampleName", "pos_topDepth", "pos_bottomDepth", "sampleMethod") 
                                  VALUES (?, ?, ?, ?, ?, ?)''',
                               (sample_id, hole_id, self.safe_get(row, 'Sample Name'), 
                                self.safe_get(row, 'topDepth'), self.safe_get(row, 'bottomDepth'),
                                self.safe_get(row, 'sampleMethod')))
                    
                    # Add SPT data if present
                    if pd.notna(row.get('SPT_1')):
                        method_name = self.safe_get(row, 'SPTMethod', 'ASTM D1586')
                        method_id = method_ids.get(method_name)
                        
                        cur.execute('''INSERT INTO "_SPT" 
                                      ("_Sample_ID", "_Method_ID", "blowCount_index1", "blowCount_index2", 
                                       "blowCount_index3", "blowCount_index4", "recovery") 
                                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                   (sample_id, method_id, self.safe_get(row, 'SPT_1'), self.safe_get(row, 'SPT_2'),
                                    self.safe_get(row, 'SPT_3'), self.safe_get(row, 'SPT_4'), self.safe_get(row, 'recovery')))
                    
                    # Add Atterberg data if present
                    if pd.notna(row.get('PL')):
                        method_name = self.safe_get(row, 'plasticityMethod', 'ASTM D4318')
                        method_id = method_ids.get(method_name)
                        
                        cur.execute('''INSERT INTO "AtterbergLimits" 
                                      ("_Sample_ID", "_Method_ID", "plasticLimit", "liquidLimit", "plasticityIndex") 
                                      VALUES (?, ?, ?, ?, ?)''',
                                   (sample_id, method_id, self.safe_get(row, 'PL'), self.safe_get(row, 'LL'), 
                                    self.safe_get(row, 'PI')))
        
        conn.commit()
        conn.close()
        print(f"Successfully converted Excel data to SQLite database: {db_path}")
        return True

def main():
    converter = ExcelToSQLiteConverter()
    
    # Default paths - can be overridden
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    excel_path = os.path.join(parent_dir, "Geotechnical_Schema.xlsx")
    db_path = os.path.join(parent_dir, "GeoDataBase_corrected.db")
    
    if os.path.exists(excel_path):
        converter.convert_excel_to_sqlite(excel_path, db_path)
    else:
        print(f"Excel file not found: {excel_path}")

if __name__ == "__main__":
    main()