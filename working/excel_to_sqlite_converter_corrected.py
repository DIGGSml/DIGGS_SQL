import pandas as pd
import sqlite3
import uuid
from datetime import datetime

def create_database_structure(db_path):
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
        
        '''CREATE TABLE IF NOT EXISTS "_waterLevels" (
          "_holeID" TEXT,
          "waterDepth" REAL,
          "TimeInterval_start" TEXT,
          "TimeInterval_end" TEXT,
          FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "_caveIn" (
          "_holeID" TEXT,
          "caveInDepth" REAL,
          "TimeInterval_start" TEXT,
          "TimeInterval_end" TEXT,
          FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID")
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
        
        '''CREATE TABLE IF NOT EXISTS "TestMethod" (
          "_Method_ID" TEXT PRIMARY KEY,
          "methodName" TEXT,
          "governingBody" TEXT,
          "units" TEXT,
          "modification" TEXT
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "_SPT" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "samplerLength" REAL,
          "samplerInternalDiameter" REAL,
          "depthCasing" REAL,
          "totalPenetration" REAL,
          "blowCount_index1" INTEGER,
          "penetration_index1" REAL,
          "blowCount_index2" INTEGER,
          "penetration_index2" REAL,
          "blowCount_index3" INTEGER,
          "penetration_index3" REAL,
          "blowCount_index4" INTEGER,
          "penetration_index4" REAL,
          "recovery" REAL,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "MoistureContent" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "moistureContent" REAL,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "StaticConePenetrationTest" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "penetrationRate" REAL,
          "tipStress_tsf" REAL,
          "sleeveStress_tsf" REAL,
          "porePressure_tsf" REAL,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "Cone_Info" (
          "_rigID" TEXT,
          "penetrometerType" TEXT,
          "distanceTipToSleeve" REAL,
          "frictionReducer" TEXT,
          "frictionSleeveArea" TEXT,
          "netAreaRatioCorrection" TEXT,
          "piezoconeType" TEXT,
          "pushRodType" TEXT,
          "tipCapacity" REAL,
          "sleeveCapacity" REAL,
          "surfaceCapacity" REAL,
          "tipApexAngle" REAL,
          "tipArea" REAL,
          "Nkt" REAL,
          FOREIGN KEY ("_rigID") REFERENCES "_Rig" ("_rigID")
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
        
        '''CREATE TABLE IF NOT EXISTS "Gradation" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "retNo4" REAL,
          "retNo10" REAL,
          "retNo20" REAL,
          "retNo40" REAL,
          "retNo60" REAL,
          "retNo100" REAL,
          "retNo140" REAL,
          "retNo200" REAL,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "Consolidation" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "_Cons_Load_ID" TEXT,
          "initialVoidRatio" REAL,
          "compressionIndex" REAL,
          "recompressionIndex" REAL,
          "overburdenPressure" REAL,
          "preconsolidationPressure" REAL,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "ConsolidationLoading" (
          "_Cons_Load_ID" TEXT,
          "loadIncrement" REAL,
          "pressure" REAL,
          "Cv" REAL,
          "Calpha" REAL,
          FOREIGN KEY ("_Cons_Load_ID") REFERENCES "Consolidation" ("_Cons_Load_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "Geology_Library" (
          "_Geo_ID" TEXT PRIMARY KEY,
          "reference" TEXT,
          "mapID" TEXT,
          "strataName" TEXT,
          "depositType" TEXT,
          "epoch" TEXT,
          "memberGroup" TEXT,
          "primComp" TEXT,
          "secComp" TEXT,
          "tertComp" TEXT,
          "addNote" TEXT
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "Field_Strata" (
          "_holeID" TEXT,
          "_Geo_ID" TEXT,
          "soilStrength" TEXT,
          "color" TEXT,
          "primaryComp" TEXT,
          "secondaryComp" TEXT,
          "secondaryCompMod" TEXT,
          "organicContent" REAL,
          "visualMoisture" TEXT,
          "soilDesc" TEXT,
          "addNote" TEXT,
          "pos_topDepth" REAL,
          "pos_bottomDepth" REAL,
          FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID"),
          FOREIGN KEY ("_Geo_ID") REFERENCES "Geology_Library" ("_Geo_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "Final_Strata" (
          "_holeID" TEXT,
          "_Geo_ID" TEXT,
          "soilStrength" TEXT,
          "color" TEXT,
          "primaryComp" TEXT,
          "secondaryComp" TEXT,
          "secondaryCompMod" TEXT,
          "organicContent" REAL,
          "visualMoisture" TEXT,
          "soilDesc" TEXT,
          "addNote" TEXT,
          "pos_topDepth" REAL,
          "pos_bottomDepth" REAL,
          FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID"),
          FOREIGN KEY ("_Geo_ID") REFERENCES "Geology_Library" ("_Geo_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "WellConstr" (
          "_holeID" TEXT,
          "material" TEXT,
          "pos_topDepth" REAL,
          "pos_bottomDepth" REAL,
          FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "RockCoring" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "_CoringMethod_ID" TEXT,
          "_Geo_ID" TEXT,
          "rockType" TEXT,
          "color" TEXT,
          "weathering" TEXT,
          "texture" TEXT,
          "relStrength" TEXT,
          "bedding" TEXT,
          "miscDesc" TEXT,
          "discontinuity" TEXT,
          "fractureType" TEXT,
          "degreeFracture" REAL,
          "width" TEXT,
          "surfaceRoughness" TEXT,
          "recovery" REAL,
          "GSI_desc" TEXT,
          "surfaceDescription" TEXT,
          "RQD" REAL,
          "soilLens" TEXT,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID"),
          FOREIGN KEY ("_CoringMethod_ID") REFERENCES "CoringMethod" ("_CoringMethod_ID"),
          FOREIGN KEY ("_Geo_ID") REFERENCES "Geology_Library" ("_Geo_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "CoringMethod" (
          "_CoringMethod_ID" TEXT PRIMARY KEY,
          "coreSize" TEXT,
          "bitSize" REAL,
          "bitType" TEXT
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "DrillMethod" (
          "_holeID" TEXT,
          "drillMethod" TEXT,
          "rodType" TEXT,
          "additives" TEXT,
          "misc" TEXT,
          FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "fieldSoilDesc" (
          "_Sample_ID" TEXT,
          "_Geo_ID" TEXT,
          "soilStrength" TEXT,
          "color" TEXT,
          "primaryComp" TEXT,
          "secondaryComp" TEXT,
          "secondaryCompMod" TEXT,
          "organicContent" REAL,
          "visualMoisture" TEXT,
          "soilDesc" TEXT,
          "addNote" TEXT,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Geo_ID") REFERENCES "Geology_Library" ("_Geo_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "WellReadings" (
          "_holeID" TEXT,
          "reading" REAL,
          "temp" REAL,
          "TimeInterval" TEXT,
          FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "riser" (
          "_holeID" TEXT,
          "pipeMaterial" TEXT,
          "pipeSchedule" TEXT,
          "pipeCoupling" TEXT,
          "screenType" TEXT,
          "pos_topDepth" REAL,
          "pos_bottomDepth" REAL,
          FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "piezometer" (
          "_holeID" TEXT,
          "piezoType" TEXT,
          "pos_topDepth" REAL,
          "pos_bottomDepth" REAL,
          FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "uuTest" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "uuSample" REAL,
          "intWC" REAL,
          "intDryDen" REAL,
          "intSat" REAL,
          "intVoid" REAL,
          "testWC" REAL,
          "testDryDen" REAL,
          "testSat" REAL,
          "testVoid" REAL,
          "strainRate" REAL,
          "backPres" REAL,
          "cellPres" REAL,
          "failStress" REAL,
          "ultStress" REAL,
          "sigma1" REAL,
          "sigma3" REAL,
          "totPhi" REAL,
          "totC" REAL,
          "effPhi" REAL,
          "effC" REAL,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "cuTest" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "cuSample" REAL,
          "intWC" REAL,
          "intDryDen" REAL,
          "intSat" REAL,
          "intVoid" REAL,
          "testWC" REAL,
          "testDryDen" REAL,
          "testSat" REAL,
          "testVoid" REAL,
          "strainRate" REAL,
          "backPres" REAL,
          "cellPres" REAL,
          "failStress" REAL,
          "failPorePres" REAL,
          "ultStress" REAL,
          "ultPorePres" REAL,
          "sigma1" REAL,
          "sigma3" REAL,
          "totPhi" REAL,
          "totC" REAL,
          "effPhi" REAL,
          "effC" REAL,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "dsTest" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "dsSample" REAL,
          "intWC" REAL,
          "intDryDen" REAL,
          "intSat" REAL,
          "intVoid" REAL,
          "testWC" REAL,
          "testDryDen" REAL,
          "testSat" REAL,
          "testVoid" REAL,
          "strainRate" REAL,
          "failStress" REAL,
          "failDisp" REAL,
          "ultStress" REAL,
          "ultDisp" REAL,
          "totPhi" REAL,
          "totC" REAL,
          "effPhi" REAL,
          "effC" REAL,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "Perm" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "permKv" REAL,
          "permKh" REAL,
          "confiningPres" REAL,
          "backPres" REAL,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "Proctor" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "sampleNumber" REAL,
          "maxDryDensity" REAL,
          "optimumMoisture" REAL,
          "dryDensity" REAL,
          "moistureContent" REAL,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "CBR" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "sampleNumber" REAL,
          "penetrationID" TEXT,
          "penetration" REAL,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "200wash" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "passing200" REAL,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "Hydrometer" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "percentClay" REAL,
          "percentSilt" REAL,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "Pocket_Pen" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "reading" REAL,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "torvane" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "reading" REAL,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "dilatometer" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "reading1" REAL,
          "reading2" REAL,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
        );''',
        
        '''CREATE TABLE IF NOT EXISTS "pressuremeter" (
          "_Sample_ID" TEXT,
          "_Method_ID" TEXT,
          "pressure" REAL,
          "volume" REAL,
          FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID"),
          FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID")
        );'''
    ]
    
    for table_sql in tables:
        cur.execute(table_sql)
    
    conn.commit()
    return conn, cur

def generate_id(prefix=""):
    """Generate a unique ID"""
    return f"{prefix}{str(uuid.uuid4())[:8]}"

def safe_get(row, key, default=None):
    """Safely get value from pandas row, handling NaN/NaT values and timestamps"""
    value = row.get(key, default)
    if pd.isna(value):
        return default
    if hasattr(value, 'strftime'):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    return value

def convert_excel_to_sqlite(excel_path, db_path):
    """Convert Excel file to SQLite database following exact DIGGS structure"""
    
    conn, cur = create_database_structure(db_path)
    excel_file = pd.ExcelFile(excel_path)
    
    # Track created IDs for foreign key relationships
    client_ids = {}
    project_ids = {}
    rig_ids = {}
    hole_ids = {}
    sample_ids = {}
    method_ids = {}
    geo_ids = {}
    
    # Process Project sheet
    if 'Project' in excel_file.sheet_names:
        df = pd.read_excel(excel_path, sheet_name='Project')
        for _, row in df.iterrows():
            # Create client
            client_key = f"{safe_get(row, 'clientName', '')}_{safe_get(row, 'clientContact', '')}"
            if client_key not in client_ids:
                client_id = generate_id("CLIENT_")
                client_ids[client_key] = client_id
                cur.execute('''INSERT INTO "_Client" ("_Client_ID", "clientName", "clientContact") 
                              VALUES (?, ?, ?)''', 
                           (client_id, safe_get(row, 'clientName'), safe_get(row, 'clientContact')))
            
            # Create project
            project_id = generate_id("PROJ_")
            project_key = f"{safe_get(row, 'projectName', '')}_{safe_get(row, 'projectNumber', '')}"
            project_ids[project_key] = project_id
            
            cur.execute('''INSERT INTO "_Project" 
                          ("_Project_ID", "_Client_ID", "projectName", "projectNumber", 
                           "projectCountry", "projectState", "projectCounty", "coordinateDatum") 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (project_id, client_ids[client_key], safe_get(row, 'projectName'), 
                        safe_get(row, 'projectNumber'), safe_get(row, 'projectCountry'), safe_get(row, 'projectState'), 
                        safe_get(row, 'projectCounty'), safe_get(row, 'coordinateDatum')))
    
    # Process TestMethod sheet
    if 'TestMethod' in excel_file.sheet_names:
        df = pd.read_excel(excel_path, sheet_name='TestMethod')
        for _, row in df.iterrows():
            method_id = generate_id("METHOD_")
            method_key = safe_get(row, 'methodName', '')
            method_ids[method_key] = method_id
            
            cur.execute('''INSERT INTO "TestMethod" 
                          ("_Method_ID", "methodName", "governingBody", "units", "modification") 
                          VALUES (?, ?, ?, ?, ?)''',
                       (method_id, safe_get(row, 'methodName'), 
                        safe_get(row, 'governingBody'), safe_get(row, 'units'), safe_get(row, 'modification')))
    
    # Process HoleInfo sheet
    if 'HoleInfo' in excel_file.sheet_names:
        df = pd.read_excel(excel_path, sheet_name='HoleInfo')
        for _, row in df.iterrows():
            # Create rig if needed
            rig_key = f"{safe_get(row, '_rigDescription', '')}_{safe_get(row, 'hammerType', '')}"
            if rig_key not in rig_ids:
                rig_id = generate_id("RIG_")
                rig_ids[rig_key] = rig_id
                cur.execute('''INSERT INTO "_Rig" ("_rigID", "_rigDescription", "hammerType", "hammerEfficiency", "miscID") 
                              VALUES (?, ?, ?, ?, ?)''',
                           (rig_id, safe_get(row, '_rigDescription'), safe_get(row, 'hammerType'), 
                            safe_get(row, 'hammerEfficiency'), safe_get(row, 'miscID')))
            
            # Create hole
            hole_id = generate_id("HOLE_")
            hole_key = safe_get(row, 'holeName', '')
            hole_ids[hole_key] = hole_id
            
            # Get project ID (assume first project if multiple)
            project_id = list(project_ids.values())[0] if project_ids else None
            
            cur.execute('''INSERT INTO "_HoleInfo" 
                          ("_holeID", "_rigID", "_Project_ID", "holeName", "holeType", 
                           "topLatitude", "topLongitude", "groundSurface", "azimuth", "angle", 
                           "bottomDepth", "timeInterval_start", "timeInterval_end", "hole_diameter", "termination") 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (hole_id, rig_ids[rig_key], project_id, safe_get(row, 'holeName'), safe_get(row, 'holeType'),
                        safe_get(row, 'topLatitude'), safe_get(row, 'topLongitude'), safe_get(row, 'groundSurface'),
                        safe_get(row, 'azimuth'), safe_get(row, 'angle'), safe_get(row, 'bottomDepth'),
                        safe_get(row, 'timeInterval_start'), safe_get(row, 'timeInterval_end'), 
                        safe_get(row, 'hole_diameter'), safe_get(row, 'termination')))
            
            # Create water level record if present
            if pd.notna(row.get('initialWaterDepth')):
                cur.execute('''INSERT INTO "_waterLevels" 
                              ("_holeID", "waterDepth", "TimeInterval_start", "TimeInterval_end") 
                              VALUES (?, ?, ?, ?)''',
                           (hole_id, safe_get(row, 'initialWaterDepth'), safe_get(row, 'timeInterval_start'), None))
            
            # Create 24hr water reading if different
            if pd.notna(row.get('24hrWater')) and row.get('24hrWater') != row.get('initialWaterDepth'):
                cur.execute('''INSERT INTO "_waterLevels" 
                              ("_holeID", "waterDepth", "TimeInterval_start", "TimeInterval_end") 
                              VALUES (?, ?, ?, ?)''',
                           (hole_id, safe_get(row, '24hrWater'), safe_get(row, 'timeInterval_end'), None))
            
            # Create cave-in record if present
            if pd.notna(row.get('caveInDepth')):
                cur.execute('''INSERT INTO "_caveIn" 
                              ("_holeID", "caveInDepth", "TimeInterval_start", "TimeInterval_end") 
                              VALUES (?, ?, ?, ?)''',
                           (hole_id, safe_get(row, 'caveInDepth'), safe_get(row, 'timeInterval_start'), None))
            
            # Create drill method record
            cur.execute('''INSERT INTO "DrillMethod" 
                          ("_holeID", "drillMethod", "rodType", "additives", "misc") 
                          VALUES (?, ?, ?, ?, ?)''',
                       (hole_id, safe_get(row, 'drillMethod'), safe_get(row, 'rodType'), 
                        safe_get(row, 'Additives'), safe_get(row, 'misc')))
    
    # Process Cone_Info sheet
    if 'Cone_Info' in excel_file.sheet_names:
        df = pd.read_excel(excel_path, sheet_name='Cone_Info')
        for _, row in df.iterrows():
            # Find corresponding rig (use _Cone_ID to match with rig)
            rig_id = list(rig_ids.values())[0] if rig_ids else None
            
            cur.execute('''INSERT INTO "Cone_Info" 
                          ("_rigID", "penetrometerType", "distanceTipToSleeve", "frictionReducer", 
                           "frictionSleeveArea", "netAreaRatioCorrection", "piezoconeType", "pushRodType", 
                           "tipCapacity", "sleeveCapacity", "surfaceCapacity", "tipApexAngle", "tipArea", "Nkt") 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (rig_id, safe_get(row, 'penetrometerType'), safe_get(row, 'distanceTipToSleeve'),
                        safe_get(row, 'frictionReducer'), safe_get(row, 'frictionSleeveArea'),
                        safe_get(row, 'netAreaRatioCorrection'), safe_get(row, 'piezoconeType'),
                        safe_get(row, 'pushRodType'), safe_get(row, 'tipCapacity'),
                        safe_get(row, 'sleeveCapacity'), safe_get(row, 'surfaceCapacity'),
                        safe_get(row, 'tipApexAngle'), safe_get(row, 'tipArea'), safe_get(row, 'Nkt')))
    
    # Process Samples sheet
    if 'Samples' in excel_file.sheet_names:
        df = pd.read_excel(excel_path, sheet_name='Samples')
        for _, row in df.iterrows():
            # Create sample
            sample_id = generate_id("SAMPLE_")
            sample_key = f"{safe_get(row, 'Hole Name', '')}_{safe_get(row, 'Sample Name', '')}"
            sample_ids[sample_key] = sample_id
            
            hole_id = hole_ids.get(safe_get(row, 'Hole Name'))
            
            cur.execute('''INSERT INTO "_Samples" 
                          ("_Sample_ID", "_holeID", "sampleName", "pos_topDepth", "pos_bottomDepth", "sampleMethod") 
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (sample_id, hole_id, safe_get(row, 'Sample Name'), safe_get(row, 'topDepth'), 
                        safe_get(row, 'bottomDepth'), safe_get(row, 'sampleMethod')))
            
            # Create SPT record if SPT data exists
            if any(pd.notna(row.get(f'SPT_{i}')) for i in range(1, 5)):
                method_id = method_ids.get(safe_get(row, 'SPTMethod'))
                
                cur.execute('''INSERT INTO "_SPT" 
                              ("_Sample_ID", "_Method_ID", "blowCount_index1", "penetration_index1",
                               "blowCount_index2", "penetration_index2", "blowCount_index3", "penetration_index3",
                               "blowCount_index4", "penetration_index4", "recovery") 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (sample_id, method_id, safe_get(row, 'SPT_1'), None, safe_get(row, 'SPT_2'), None,
                            safe_get(row, 'SPT_3'), None, safe_get(row, 'SPT_4'), None, safe_get(row, 'recovery')))
            
            # Create moisture content record
            if pd.notna(row.get('moistureContent')):
                method_id = method_ids.get(safe_get(row, 'moistureMethod'))
                cur.execute('''INSERT INTO "MoistureContent" 
                              ("_Sample_ID", "_Method_ID", "moistureContent") 
                              VALUES (?, ?, ?)''',
                           (sample_id, method_id, safe_get(row, 'moistureContent')))
            
            # Create Atterberg limits record
            if any(pd.notna(row.get(field)) for field in ['PL', 'LL', 'PI']):
                method_id = method_ids.get(safe_get(row, 'plasticityMethod'))
                cur.execute('''INSERT INTO "AtterbergLimits" 
                              ("_Sample_ID", "_Method_ID", "plasticLimit", "liquidLimit", "plasticityIndex") 
                              VALUES (?, ?, ?, ?, ?)''',
                           (sample_id, method_id, safe_get(row, 'PL'), safe_get(row, 'LL'), safe_get(row, 'PI')))
            
            # Create 200 wash record
            if pd.notna(row.get('passing200')):
                cur.execute('''INSERT INTO "200wash" 
                              ("_Sample_ID", "_Method_ID", "passing200") 
                              VALUES (?, ?, ?)''',
                           (sample_id, None, safe_get(row, 'passing200')))
            
            # Create pocket penetrometer record
            if pd.notna(row.get('pocketPenReading')):
                cur.execute('''INSERT INTO "Pocket_Pen" 
                              ("_Sample_ID", "_Method_ID", "reading") 
                              VALUES (?, ?, ?)''',
                           (sample_id, None, safe_get(row, 'pocketPenReading')))
            
            # Create torvane record
            if pd.notna(row.get('torvaneReading')):
                cur.execute('''INSERT INTO "torvane" 
                              ("_Sample_ID", "_Method_ID", "reading") 
                              VALUES (?, ?, ?)''',
                           (sample_id, None, safe_get(row, 'torvaneReading')))
            
            # Create field soil description record
            if pd.notna(row.get('Geo_ID')):
                cur.execute('''INSERT INTO "fieldSoilDesc" 
                              ("_Sample_ID", "_Geo_ID", "color", "primaryComp", 
                               "secondaryComp", "secondaryCompMod", "organicContent", "visualMoisture") 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                           (sample_id, safe_get(row, 'Geo_ID'), safe_get(row, 'color'), 
                            safe_get(row, 'primaryComp'), safe_get(row, 'secondaryComp'), 
                            safe_get(row, 'secondaryCompMod'), safe_get(row, 'organicContent'), 
                            safe_get(row, 'visualMoisture')))
    
    # Process Field and Final Strata sheets
    for strata_type in ['FieldStrata', 'FinalStrata']:
        table_name = "Field_Strata" if strata_type == 'FieldStrata' else "Final_Strata"
        if strata_type in excel_file.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=strata_type)
            for _, row in df.iterrows():
                hole_id = hole_ids.get(safe_get(row, 'Hole Name'))
                
                cur.execute(f'''INSERT INTO "{table_name}" 
                              ("_holeID", "_Geo_ID", "soilStrength", "color", "primaryComp", 
                               "secondaryComp", "secondaryCompMod", "organicContent", "visualMoisture", 
                               "pos_topDepth", "pos_bottomDepth") 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (hole_id, safe_get(row, 'Geo_ID'), safe_get(row, 'soilstrength'),
                            safe_get(row, 'color'), safe_get(row, 'primaryComp'), safe_get(row, 'secondaryComp'),
                            safe_get(row, 'secondaryCompMod'), safe_get(row, 'organicContent'),
                            safe_get(row, 'visualMoisture'), safe_get(row, 'topDepth'), safe_get(row, 'bottomDepth')))
    
    # Process Gradation sheet
    if 'Gradation' in excel_file.sheet_names:
        df = pd.read_excel(excel_path, sheet_name='Gradation')
        for _, row in df.iterrows():
            sample_key = f"{safe_get(row, 'Boring', '')}_{safe_get(row, 'Sample', '')}"
            sample_id = sample_ids.get(sample_key)
            
            cur.execute('''INSERT INTO "Gradation" 
                          ("_Sample_ID", "_Method_ID", "retNo4", "retNo10", "retNo20", 
                           "retNo40", "retNo60", "retNo100", "retNo140", "retNo200") 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (sample_id, None, safe_get(row, 'retNo4'), safe_get(row, 'retNo10'),
                        safe_get(row, 'retNo20'), safe_get(row, 'retNo40'), safe_get(row, 'retNo60'),
                        safe_get(row, 'retNo100'), safe_get(row, 'retNo140'), safe_get(row, 'retNo200')))
    
    # Process Consolidation and ConsolidationLoading sheets
    if 'Consolidation' in excel_file.sheet_names:
        df = pd.read_excel(excel_path, sheet_name='Consolidation')
        for _, row in df.iterrows():
            sample_key = f"{safe_get(row, 'Boring', '')}_{safe_get(row, 'Sample', '')}"
            sample_id = sample_ids.get(sample_key)
            
            cur.execute('''INSERT INTO "Consolidation" 
                          ("_Sample_ID", "_Method_ID", "_Cons_Load_ID", "initialVoidRatio", 
                           "compressionIndex", "recompressionIndex", "overburdenPressure", 
                           "preconsolidationPressure") 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (sample_id, safe_get(row, '_Method_ID'), safe_get(row, '_Cons_Load_ID'),
                        safe_get(row, 'initialVoidRatio'), safe_get(row, 'compressionIndex'),
                        safe_get(row, 'recompressionIndex'), safe_get(row, 'overburdenPressure'),
                        safe_get(row, 'preconsolidationPressure')))
    
    if 'ConsolidationLoading' in excel_file.sheet_names:
        df = pd.read_excel(excel_path, sheet_name='ConsolidationLoading')
        for _, row in df.iterrows():
            cur.execute('''INSERT INTO "ConsolidationLoading" 
                          ("_Cons_Load_ID", "loadIncrement", "pressure", "Cv", "Calpha") 
                          VALUES (?, ?, ?, ?, ?)''',
                       (safe_get(row, '_Cons_Load_ID'), safe_get(row, 'loadIncrement'),
                        safe_get(row, 'pressure'), safe_get(row, 'Cv'), safe_get(row, 'Calpha')))
    
    # Process test sheets (uuTest, cuTest, dsTest, etc.) - these use existing _Sample_ID and _Method_ID
    test_sheets = ['uuTest', 'cuTest', 'dsTest', 'Perm', 'Proctor', 'CBR', 'pressuremeter', 'dilatometer']
    
    for sheet_name in test_sheets:
        if sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            for _, row in df.iterrows():
                sample_id = safe_get(row, '_Sample_ID')
                method_id = safe_get(row, '_Method_ID')
                
                # Build column list and values excluding IDs
                columns = [col for col in df.columns if col not in ['_Sample_ID', '_Method_ID']]
                values = [safe_get(row, col) for col in columns]
                placeholders = ', '.join(['?' for _ in columns])
                column_names = ', '.join([f'"{col}"' for col in columns])
                
                cur.execute(f'''INSERT INTO "{sheet_name}" 
                              ("_Sample_ID", "_Method_ID", {column_names}) 
                              VALUES (?, ?, {placeholders})''',
                           [sample_id, method_id] + values)
    
    # Process CPT data
    if 'StaticConePenetrationTestType' in excel_file.sheet_names:
        df = pd.read_excel(excel_path, sheet_name='StaticConePenetrationTestType')
        for _, row in df.iterrows():
            sample_id = safe_get(row, '_Sample_ID')
            method_id = safe_get(row, '_Method_ID')
            
            # Map Excel columns to database columns
            cur.execute('''INSERT INTO "StaticConePenetrationTest" 
                          ("_Sample_ID", "_Method_ID", "penetrationRate", "tipStress_tsf", 
                           "sleeveStress_tsf", "porePressure_tsf") 
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (sample_id, method_id, None, safe_get(row, 'Tip Stress UNC_qc'),
                        safe_get(row, 'Sleeve Stress_fs'), safe_get(row, 'Pore Pressure_u')))
    
    # Process well construction sheets
    well_sheets = [
        ('WellConstr', 'WellConstr'),
        ('riser', 'riser'), 
        ('WellReadings', 'WellReadings'),
        ('piezometer', 'piezometer')
    ]
    
    for excel_sheet, table_name in well_sheets:
        if excel_sheet in excel_file.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=excel_sheet)
            for _, row in df.iterrows():
                hole_id = hole_ids.get(safe_get(row, 'Boring'))
                
                if table_name == 'WellConstr':
                    cur.execute('''INSERT INTO "WellConstr" 
                                  ("_holeID", "material", "pos_topDepth", "pos_bottomDepth") 
                                  VALUES (?, ?, ?, ?)''',
                               (hole_id, safe_get(row, 'material'), safe_get(row, 'pos_topDepth'), 
                                safe_get(row, 'pos_bottomDepth')))
                elif table_name == 'riser':
                    cur.execute('''INSERT INTO "riser" 
                                  ("_holeID", "pipeMaterial", "pipeSchedule", "pipeCoupling", 
                                   "screenType", "pos_topDepth", "pos_bottomDepth") 
                                  VALUES (?, ?, ?, ?, ?, ?, ?)''',
                               (hole_id, safe_get(row, 'pipeMaterial'), safe_get(row, 'pipeSchedule'),
                                safe_get(row, 'pipeCoupling'), safe_get(row, 'screenType'),
                                safe_get(row, 'pos_topDepth'), safe_get(row, 'pos_bottomDepth')))
                elif table_name == 'WellReadings':
                    cur.execute('''INSERT INTO "WellReadings" 
                                  ("_holeID", "reading", "temp", "TimeInterval") 
                                  VALUES (?, ?, ?, ?)''',
                               (hole_id, safe_get(row, 'reading'), safe_get(row, 'temp'), 
                                safe_get(row, 'TimeInterval')))
                elif table_name == 'piezometer':
                    cur.execute('''INSERT INTO "piezometer" 
                                  ("_holeID", "piezoType", "pos_topDepth", "pos_bottomDepth") 
                                  VALUES (?, ?, ?, ?)''',
                               (hole_id, safe_get(row, 'piezoType'), safe_get(row, 'pos_topDepth'), 
                                safe_get(row, 'pos_bottomDepth')))
    
    # Process RockCoring sheet
    if 'RockCoring' in excel_file.sheet_names:
        df = pd.read_excel(excel_path, sheet_name='RockCoring')
        for _, row in df.iterrows():
            sample_key = f"{safe_get(row, 'Hole Name', '')}_{safe_get(row, 'Sample Name', '')}"
            sample_id = sample_ids.get(sample_key)
            
            cur.execute('''INSERT INTO "RockCoring" 
                          ("_Sample_ID", "_Method_ID", "_CoringMethod_ID", "_Geo_ID", "rockType", 
                           "color", "weathering", "texture", "relStrength", "bedding", "miscDesc", 
                           "discontinuity", "degreeFracture", "width", "surfaceRoughness", "recovery", 
                           "GSI_desc", "surfaceDescription", "RQD") 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (sample_id, None, None, None, safe_get(row, 'rockType'), safe_get(row, 'color'),
                        safe_get(row, 'weathering'), safe_get(row, 'texture'), safe_get(row, 'relStrength'),
                        safe_get(row, 'bedding'), safe_get(row, 'miscDesc'), safe_get(row, 'discontinuity'),
                        safe_get(row, 'degreeFracture'), safe_get(row, 'width'), safe_get(row, 'surfaceRoughness'),
                        safe_get(row, 'recovery'), safe_get(row, 'GSI_desc'), safe_get(row, 'surfaceDescription'),
                        safe_get(row, 'RQD')))
    
    conn.commit()
    conn.close()
    print(f"Successfully converted Excel data to SQLite database: {db_path}")

if __name__ == "__main__":
    excel_path = r"C:\Users\hosti\Documents\GitHub\DIGGS_SQL\working\Geotechnical_Schema.xlsx"
    db_path = "GeoDataBase_corrected.db"
    
    convert_excel_to_sqlite(excel_path, db_path)