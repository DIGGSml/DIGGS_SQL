PRAGMA foreign_keys = ON;

CREATE TABLE "_Rig" (
  "_rigID" TEXT PRIMARY KEY,
  "_rigDescription" TEXT,
  "hammerType" TEXT,
  "hammerMass" REAL,
  "hammerDropHeight" REAL,
  "hammerEfficiency" REAL
);

CREATE TABLE "_Project" (
  "_Project_ID" TEXT PRIMARY KEY,
  "_Client_ID" TEXT,
  "projectName" TEXT,
  "projectNumber" TEXT,
  "projectCountry" TEXT,
  "projectState" TEXT,
  "projectCounty" TEXT,
  "coordinateDatum" TEXT,
  FOREIGN KEY("_Client_ID") REFERENCES "_Client"("_Client_ID")
);

CREATE TABLE "_Client" (
  "_Client_ID" TEXT PRIMARY KEY,
  "clientName" TEXT,
  "clientContact" TEXT
);

CREATE TABLE "_HoleInfo" (
  "_holeID" TEXT PRIMARY KEY,
  "_rigID" TEXT,
  "_Project_ID" TEXT,
  "holeName" TEXT,
  "measureType" TEXT,
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
  FOREIGN KEY("_rigID") REFERENCES "_Rig"("_rigID"),
  FOREIGN KEY("_Project_ID") REFERENCES "_Project"("_Project_ID")
);

CREATE TABLE "_waterLevels" (
  "_holeID" TEXT,
  "waterDepth" REAL,
  "TimeInterval_start" TEXT,
  "TimeInterval_end" TEXT,
  FOREIGN KEY("_holeID") REFERENCES "_HoleInfo"("_holeID")
);

CREATE TABLE "_caveIn" (
  "_holeID" TEXT,
  "caveInDepth" REAL,
  "TimeInterval_start" TEXT,
  "TimeInterval_end" TEXT,
  FOREIGN KEY("_holeID") REFERENCES "_HoleInfo"("_holeID")
);

CREATE TABLE "_Samples" (
  "_Sample_ID" TEXT PRIMARY KEY,
  "_holeID" TEXT,
  "sampleName" TEXT,
  "pos_topDepth" REAL,
  "pos_bottomDepth" REAL,
  "sampleMethod" TEXT,
  FOREIGN KEY("_holeID") REFERENCES "_HoleInfo"("_holeID")
);

CREATE TABLE "_SPT" (
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
  FOREIGN KEY("_Sample_ID") REFERENCES "_Samples"("_Sample_ID"),
  FOREIGN KEY("_Method_ID") REFERENCES "TestMethod"("_Method_ID")
);

CREATE TABLE "MoistureContent" (
  "_Sample_ID" TEXT,
  "_Method_ID" TEXT,
  "moistureContent" REAL,
  FOREIGN KEY("_Sample_ID") REFERENCES "_Samples"("_Sample_ID"),
  FOREIGN KEY("_Method_ID") REFERENCES "TestMethod"("_Method_ID")
);

CREATE TABLE "PorePressureElementType" (
  "cellId" TEXT PRIMARY KEY,
  "filterElementLocation" REAL,
  "poreCapacity" REAL,
  "porousElementType" TEXT,
  "saturationFluid" TEXT,
  "saturationMethod" TEXT,
  "saturationMethodRef" TEXT
);

CREATE TABLE "StaticConePenetrationTest" (
  "_Sample_ID" TEXT,
  "_Method_ID" TEXT,
  "cellId" TEXT,
  "_Cone_ID" TEXT,
  "penetrationRate" REAL,
  "tipResistance" REAL,
  "sleeveFriction" REAL,
  "porePressure" REAL,
  FOREIGN KEY("_Sample_ID") REFERENCES "_Samples"("_Sample_ID"),
  FOREIGN KEY("cellId") REFERENCES "PorePressureElementType"("cellId"),
  FOREIGN KEY("_Method_ID") REFERENCES "TestMethod"("_Method_ID"),
  FOREIGN KEY("_Cone_ID") REFERENCES "Cone_Info"("_Cone_ID")
);

CREATE TABLE "Cone_Info" (
  "_Cone_ID" TEXT PRIMARY KEY,
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
  "tipArea" REAL
);

CREATE TABLE "TestMethod" (
  "_Method_ID" TEXT PRIMARY KEY,
  "methodName" TEXT,
  "governingBody" TEXT,
  "units" TEXT,
  "modification" TEXT
);

CREATE TABLE "AtterbergLimits" (
  "_Sample_ID" TEXT,
  "_Method_ID" TEXT,
  "plasticLimit" REAL,
  "liquidLimit" REAL,
  "plasticityIndex" REAL,
  FOREIGN KEY("_Sample_ID") REFERENCES "_Samples"("_Sample_ID"),
  FOREIGN KEY("_Method_ID") REFERENCES "TestMethod"("_Method_ID")
);

CREATE TABLE "ShelbyTube" (
  "_Sample_ID" TEXT,
  "_Method_ID" TEXT,
  FOREIGN KEY("_Sample_ID") REFERENCES "_Samples"("_Sample_ID"),
  FOREIGN KEY("_Method_ID") REFERENCES "TestMethod"("_Method_ID")
);

CREATE TABLE "Gradation" (
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
  FOREIGN KEY("_Sample_ID") REFERENCES "_Samples"("_Sample_ID"),
  FOREIGN KEY("_Method_ID") REFERENCES "TestMethod"("_Method_ID")
);

CREATE TABLE "Consolidation" (
  "_Sample_ID" TEXT,
  "_Method_ID" TEXT,
  "_Cons_Load_ID" TEXT,
  "initialVoidRatio" REAL,
  "compressionIndex" REAL,
  "recompressionIndex" REAL,
  "overburdenPressure" REAL,
  "preconsolidationPressure" REAL,
  FOREIGN KEY("_Sample_ID") REFERENCES "_Samples"("_Sample_ID"),
  FOREIGN KEY("_Method_ID") REFERENCES "TestMethod"("_Method_ID"),
  FOREIGN KEY("_Cons_Load_ID") REFERENCES "ConsolidationLoading"("_Cons_Load_ID")
);

CREATE TABLE "ConsolidationLoading" (
  "_Cons_Load_ID" TEXT PRIMARY KEY,
  "loadIncrement" REAL,
  "pressure" REAL,
  "Cv" REAL,
  "Calpha" REAL
);

CREATE TABLE "Geology_Library" (
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
);

CREATE TABLE "Field_Strata" (
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
  FOREIGN KEY("_holeID") REFERENCES "_HoleInfo"("_holeID"),
  FOREIGN KEY("_Geo_ID") REFERENCES "Geology_Library"("_Geo_ID")
);

CREATE TABLE "Final_Strata" (
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
  FOREIGN KEY("_holeID") REFERENCES "_HoleInfo"("_holeID"),
  FOREIGN KEY("_Geo_ID") REFERENCES "Geology_Library"("_Geo_ID")
);

CREATE TABLE "WellConstr" (
  "_holeID" TEXT,
  "material" TEXT,
  "pos_topDepth" REAL,
  "pos_bottomDepth" REAL,
  FOREIGN KEY("_holeID") REFERENCES "_HoleInfo"("_holeID")
);

CREATE TABLE "RockCoring" (
  "_Sample_ID" TEXT,
  "_Method_ID" TEXT,
  "_CoringMethod_ID" TEXT,
  "rockType" TEXT,
  "color" TEXT,
  "weathering" TEXT,
  "TEXTure" TEXT,
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
  FOREIGN KEY("_Sample_ID") REFERENCES "_Samples"("_Sample_ID"),
  FOREIGN KEY("_Method_ID") REFERENCES "TestMethod"("_Method_ID"),
  FOREIGN KEY("_CoringMethod_ID") REFERENCES "CoringMethod"("_CoringMethod_ID")
);

CREATE TABLE "CoringMethod" (
  "_CoringMethod_ID" TEXT PRIMARY KEY,
  "coreSize" TEXT,
  "bitSize" REAL,
  "bitType" TEXT
);

CREATE TABLE "DrillMethod" (
  "_holeID" TEXT,
  "drillMethod" TEXT,
  "rodType" TEXT,
  "additives" TEXT,
  "misc" TEXT,
  FOREIGN KEY("_holeID") REFERENCES "_HoleInfo"("_holeID")
);

CREATE TABLE "fieldSoilDesc" (
  "_Sample_ID" TEXT,
  "soilStrength" TEXT,
  "color" TEXT,
  "primaryComp" TEXT,
  "secondaryComp" TEXT,
  "secondaryCompMod" TEXT,
  "organicContent" REAL,
  "visualMoisture" TEXT,
  "soilDesc" TEXT,
  "addNote" TEXT,
  FOREIGN KEY("_Sample_ID") REFERENCES "_Samples"("_Sample_ID")
);

CREATE TABLE "WellReadings" (
  "_holeID" TEXT,
  "reading" REAL,
  "temp" REAL,
  "TimeInterval" TEXT,
  FOREIGN KEY("_holeID") REFERENCES "_HoleInfo"("_holeID")
);

CREATE TABLE "riser" (
  "_holeID" TEXT,
  "pipeMaterial" TEXT,
  "pipeSchedule" TEXT,
  "pipeCoupling" TEXT,
  "screenType" TEXT,
  "pos_topDepth" REAL,
  "pos_bottomDepth" REAL,
  FOREIGN KEY("_holeID") REFERENCES "_HoleInfo"("_holeID")
);

CREATE TABLE "piezometer" (
  "_holeID" TEXT,
  "piezoType" TEXT,
  "pos_topDepth" REAL,
  "pos_bottomDepth" REAL,
  FOREIGN KEY("_holeID") REFERENCES "_HoleInfo"("_holeID")
);

CREATE TABLE "uuTest" (
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
  FOREIGN KEY("_Sample_ID") REFERENCES "_Samples"("_Sample_ID"),
  FOREIGN KEY("_Method_ID") REFERENCES "TestMethod"("_Method_ID")
);

CREATE TABLE "cuTest" (
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
  FOREIGN KEY("_Sample_ID") REFERENCES "_Samples"("_Sample_ID"),
  FOREIGN KEY("_Method_ID") REFERENCES "TestMethod"("_Method_ID")
);

CREATE TABLE "dsTest" (
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
  FOREIGN KEY("_Sample_ID") REFERENCES "_Samples"("_Sample_ID"),
  FOREIGN KEY("_Method_ID") REFERENCES "TestMethod"("_Method_ID")
);

CREATE TABLE "Perm" (
  "_Sample_ID" TEXT,
  "_Method_ID" TEXT,
  "permKv" REAL,
  "permKh" REAL,
  "confiningPres" REAL,
  "backPres" REAL,
  FOREIGN KEY("_Sample_ID") REFERENCES "_Samples"("_Sample_ID"),
  FOREIGN KEY("_Method_ID") REFERENCES "TestMethod"("_Method_ID")
);

CREATE TABLE "Proctor" (
  "_Sample_ID" TEXT,
  "_Method_ID" TEXT,
  "sampleNumber" REAL,
  "maxDryDensity" REAL,
  "optimumMoisture" REAL,
  "dryDensity" REAL,
  "moistureContent" REAL,
  FOREIGN KEY("_Sample_ID") REFERENCES "_Samples"("_Sample_ID"),
  FOREIGN KEY("_Method_ID") REFERENCES "TestMethod"("_Method_ID")
);

CREATE TABLE "CBR" (
  "_Sample_ID" TEXT,
  "_Method_ID" TEXT,
  "sampleNumber" REAL,
  "penetrationID" TEXT,
  "penetration" REAL,
  FOREIGN KEY("_Sample_ID") REFERENCES "_Samples"("_Sample_ID"),
  FOREIGN KEY("_Method_ID") REFERENCES "TestMethod"("_Method_ID")
);

CREATE TABLE "200wash" (
  "_Sample_ID" TEXT,
  "_Method_ID" TEXT,
  "passing200" REAL,
  FOREIGN KEY("_Sample_ID") REFERENCES "_Samples"("_Sample_ID"),
  FOREIGN KEY("_Method_ID") REFERENCES "TestMethod"("_Method_ID")
);

CREATE TABLE "Hydrometer" (
  "_Sample_ID" TEXT,
  "_Method_ID" TEXT,
  "percentClay" REAL,
  "percentSilt" REAL,
  FOREIGN KEY("_Sample_ID") REFERENCES "_Samples"("_Sample_ID"),
  FOREIGN KEY("_Method_ID") REFERENCES "TestMethod"("_Method_ID")
);