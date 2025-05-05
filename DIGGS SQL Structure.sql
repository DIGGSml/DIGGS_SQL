CREATE TABLE "_Rig" (
  "_rigID" text PRIMARY KEY,
  "_rigDescription" text,
  "hammerType" text,
  "hammerMass" real,
  "hammerDropHeight" real,
  "hammerEfficiency" real
);

CREATE TABLE "_Project" (
  "_Project_ID" text PRIMARY KEY,
  "_Client_ID" text,
  "projectName" text,
  "projectNumber" text,
  "projectCountry" text,
  "projectState" text,
  "projectCounty" text,
  "coordinateDatum" text
);

CREATE TABLE "_Client" (
  "_Client_ID" text PRIMARY KEY,
  "clientName" text,
  "clientContact" text
);

CREATE TABLE "_HoleInfo" (
  "_holeID" text PRIMARY KEY,
  "_rigID" text,
  "_Project_ID" text,
  "holeName" text,
  "measureType" text,
  "topLatitude" real,
  "topLongitude" real,
  "groundSurface" real,
  "azimuth" real,
  "angle" real,
  "bottomDepth" real,
  "timeInterval_start" timestamp,
  "timeInterval_end" timestamp,
  "hole_diameter" real,
  "termination" text
);

CREATE TABLE "_waterLevels" (
  "_holeID" text,
  "waterDepth" real,
  "TimeInterval_start" timestamp,
  "TimeInterval_end" timestamp
);

CREATE TABLE "_caveIn" (
  "_holeID" text,
  "caveInDepth" real,
  "TimeInterval_start" timestamp,
  "TimeInterval_end" timestamp
);

CREATE TABLE "_Samples" (
  "_Sample_ID" text PRIMARY KEY,
  "_holeID" text,
  "sampleName" text,
  "pos_topDepth" real,
  "pos_bottomDepth" real,
  "sampleMethod" text
);

CREATE TABLE "_SPT" (
  "_Sample_ID" text,
  "_Method_ID" text,
  "samplerLength" real,
  "samplerInternalDiameter" real,
  "depthCasing" real,
  "totalPenetration" real,
  "blowCount_index1" integer,
  "penetration_index1" real,
  "blowCount_index2" integer,
  "penetration_index2" real,
  "blowCount_index3" integer,
  "penetration_index3" real,
  "blowCount_index4" integer,
  "penetration_index4" real,
  "recovery" real
);

CREATE TABLE "MoistureContent" (
  "_Sample_ID" text,
  "_Method_ID" text,
  "moistureContent" real
);

CREATE TABLE "PorePressureElementType" (
  "cellId" text PRIMARY KEY,
  "filterElementLocation" real,
  "poreCapacity" real,
  "porousElementType" text,
  "saturationFluid" text,
  "saturationMethod" text,
  "saturationMethodRef" text
);

CREATE TABLE "StaticConePenetrationTest" (
  "_Sample_ID" text,
  "_Method_ID" text,
  "cellId" text,
  "_Cone_ID" text,
  "penetrationRate" real,
  "tipResistance" real,
  "sleeveFriction" real,
  "porePressure" real
);

CREATE TABLE "Cone_Info" (
  "_Cone_ID" text PRIMARY KEY,
  "penetrometerType" text,
  "distanceTipToSleeve" real,
  "frictionReducer" text,
  "frictionSleeveArea" text,
  "netAreaRatioCorrection" text,
  "piezoconeType" text,
  "pushRodType" text,
  "tipCapacity" real,
  "sleeveCapacity" real,
  "surfaceCapacity" real,
  "tipApexAngle" real,
  "tipArea" real
);

CREATE TABLE "TestMethod" (
  "_Method_ID" text PRIMARY KEY,
  "methodName" text,
  "governingBody" text,
  "units" text,
  "modification" text
);

CREATE TABLE "AtterbergLimits" (
  "_Sample_ID" text,
  "_Method_ID" text,
  "plasticLimit" real,
  "liquidLimit" real,
  "plasticityIndex" real
);

CREATE TABLE "ShelbyTube" (
  "_Sample_ID" text,
  "_Method_ID" text
);

CREATE TABLE "Gradation" (
  "_Sample_ID" text,
  "_Method_ID" text,
  "retNo4" real,
  "retNo10" real,
  "retNo20" real,
  "retNo40" real,
  "retNo60" real,
  "retNo100" real,
  "retNo140" real,
  "retNo200" real
);

CREATE TABLE "Consolidation" (
  "_Sample_ID" text,
  "_Method_ID" text,
  "_Cons_Load_ID" text,
  "initialVoidRatio" real,
  "compressionIndex" real,
  "recompressionIndex" real,
  "overburdenPressure" real,
  "preconsolidationPressure" real
);

CREATE TABLE "ConsolidationLoading" (
  "_Cons_Load_ID" text,
  "loadIncrement" real,
  "pressure" real,
  "Cv" real,
  "Calpha" real
);

CREATE TABLE "Geology_Library" (
  "_Geo_ID" text PRIMARY KEY,
  "reference" text,
  "mapID" text,
  "strataName" text,
  "depositType" text,
  "epoch" text,
  "memberGroup" text,
  "primComp" text,
  "secComp" text,
  "tertComp" text,
  "addNote" text
);

CREATE TABLE "Field_Strata" (
  "_holeID" text,
  "_Geo_ID" text,
  "soilStrength" text,
  "color" text,
  "primaryComp" text,
  "secondaryComp" text,
  "secondaryCompMod" text,
  "organicContent" real,
  "visualMoisture" text,
  "soilDesc" text,
  "addNote" text,
  "pos_topDepth" real,
  "pos_bottomDepth" real
);

CREATE TABLE "Final_Strata" (
  "_holeID" text,
  "_Geo_ID" text,
  "soilStrength" text,
  "color" text,
  "primaryComp" text,
  "secondaryComp" text,
  "secondaryCompMod" text,
  "organicContent" real,
  "visualMoisture" text,
  "soilDesc" text,
  "addNote" text,
  "pos_topDepth" real,
  "pos_bottomDepth" real
);

CREATE TABLE "WellConstr" (
  "_holeID" text,
  "material" text,
  "pos_topDepth" real,
  "pos_bottomDepth" real
);

CREATE TABLE "RockCoring" (
  "_Sample_ID" text,
  "_Method_ID" text,
  "_CoringMethod_ID" text,
  "rockType" text,
  "color" text,
  "weathering" text,
  "texture" text,
  "relStrength" text,
  "bedding" text,
  "miscDesc" text,
  "discontinuity" text,
  "fractureType" text,
  "degreeFracture" real,
  "width" text,
  "surfaceRoughness" text,
  "recovery" real,
  "GSI_desc" text,
  "surfaceDescription" text,
  "RQD" real,
  "soilLens" text
);

CREATE TABLE "CoringMethod" (
  "_CoringMethod_ID" text PRIMARY KEY,
  "coreSize" text,
  "bitSize" real,
  "bitType" text
);

CREATE TABLE "DrillMethod" (
  "_holeID" text,
  "drillMethod" text,
  "rodType" text,
  "additives" text,
  "misc" text
);

CREATE TABLE "fieldSoilDesc" (
  "_Sample_ID" text,
  "soilStrength" text,
  "color" text,
  "primaryComp" text,
  "secondaryComp" text,
  "secondaryCompMod" text,
  "organicContent" real,
  "visualMoisture" text,
  "soilDesc" text,
  "addNote" text
);

CREATE TABLE "WellReadings" (
  "_holeID" text,
  "reading" real,
  "temp" real,
  "TimeInterval" timestamp
);

CREATE TABLE "riser" (
  "_holeID" text,
  "pipeMaterial" text,
  "pipeSchedule" text,
  "pipeCoupling" text,
  "screenType" text,
  "pos_topDepth" real,
  "pos_bottomDepth" real
);

CREATE TABLE "piezometer" (
  "_holeID" text,
  "piezoType" text,
  "pos_topDepth" real,
  "pos_bottomDepth" real
);

CREATE TABLE "uuTest" (
  "_Sample_ID" text,
  "_Method_ID" text,
  "uuSample" real,
  "intWC" real,
  "intDryDen" real,
  "intSat" real,
  "intVoid" real,
  "testWC" real,
  "testDryDen" real,
  "testSat" real,
  "testVoid" real,
  "strainRate" real,
  "backPres" real,
  "cellPres" real,
  "failStress" real,
  "ultStress" real,
  "sigma1" real,
  "sigma3" real,
  "totPhi" real,
  "totC" real,
  "effPhi" real,
  "effC" real
);

CREATE TABLE "cuTest" (
  "_Sample_ID" text,
  "_Method_ID" text,
  "cuSample" real,
  "intWC" real,
  "intDryDen" real,
  "intSat" real,
  "intVoid" real,
  "testWC" real,
  "testDryDen" real,
  "testSat" real,
  "testVoid" real,
  "strainRate" real,
  "backPres" real,
  "cellPres" real,
  "failStress" real,
  "failPorePres" real,
  "ultStress" real,
  "ultPorePres" real,
  "sigma1" real,
  "sigma3" real,
  "totPhi" real,
  "totC" real,
  "effPhi" real,
  "effC" real
);

CREATE TABLE "dsTest" (
  "_Sample_ID" text,
  "_Method_ID" text,
  "dsSample" real,
  "intWC" real,
  "intDryDen" real,
  "intSat" real,
  "intVoid" real,
  "testWC" real,
  "testDryDen" real,
  "testSat" real,
  "testVoid" real,
  "strainRate" real,
  "failStress" real,
  "failDisp" real,
  "ultStress" real,
  "ultDisp" real,
  "totPhi" real,
  "totC" real,
  "effPhi" real,
  "effC" real
);

CREATE TABLE "Perm" (
  "_Sample_ID" text,
  "_Method_ID" text,
  "permKv" real,
  "permKh" real,
  "confiningPres" real,
  "backPres" real
);

CREATE TABLE "Proctor" (
  "_Sample_ID" text,
  "_Method_ID" text,
  "sampleNumber" real,
  "maxDryDensity" real,
  "optimumMoisture" real,
  "dryDensity" real,
  "moistureContent" real
);

CREATE TABLE "CBR" (
  "_Sample_ID" text,
  "_Method_ID" text,
  "sampleNumber" real,
  "penetrationID" text,
  "penetration" real
);

CREATE TABLE "200wash" (
  "_Sample_ID" text,
  "_Method_ID" text,
  "passing200" real
);

CREATE TABLE "Hydrometer" (
  "_Sample_ID" text,
  "_Method_ID" text,
  "percentClay" real,
  "percentSilt" real
);

ALTER TABLE "_waterLevels" ADD FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID");

ALTER TABLE "_HoleInfo" ADD FOREIGN KEY ("_rigID") REFERENCES "_Rig" ("_rigID");

ALTER TABLE "_HoleInfo" ADD FOREIGN KEY ("_Project_ID") REFERENCES "_Project" ("_Project_ID");

ALTER TABLE "_Samples" ADD FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID");

ALTER TABLE "_SPT" ADD FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID");

ALTER TABLE "StaticConePenetrationTest" ADD FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID");

ALTER TABLE "StaticConePenetrationTest" ADD FOREIGN KEY ("cellId") REFERENCES "PorePressureElementType" ("cellId");

ALTER TABLE "StaticConePenetrationTest" ADD FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID");

ALTER TABLE "StaticConePenetrationTest" ADD FOREIGN KEY ("_Cone_ID") REFERENCES "Cone_Info" ("_Cone_ID");

ALTER TABLE "_SPT" ADD FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID");

ALTER TABLE "AtterbergLimits" ADD FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID");

ALTER TABLE "Consolidation" ADD FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID");

ALTER TABLE "MoistureContent" ADD FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID");

ALTER TABLE "Gradation" ADD FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID");

ALTER TABLE "AtterbergLimits" ADD FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID");

ALTER TABLE "Consolidation" ADD FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID");

ALTER TABLE "MoistureContent" ADD FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID");

ALTER TABLE "Gradation" ADD FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID");

ALTER TABLE "ConsolidationLoading" ADD FOREIGN KEY ("_Cons_Load_ID") REFERENCES "Consolidation" ("_Cons_Load_ID");

ALTER TABLE "WellConstr" ADD FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID");

ALTER TABLE "RockCoring" ADD FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID");

ALTER TABLE "RockCoring" ADD FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID");

ALTER TABLE "ShelbyTube" ADD FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID");

ALTER TABLE "ShelbyTube" ADD FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID");

ALTER TABLE "fieldSoilDesc" ADD FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID");

ALTER TABLE "WellReadings" ADD FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID");

ALTER TABLE "riser" ADD FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID");

ALTER TABLE "piezometer" ADD FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID");

ALTER TABLE "uuTest" ADD FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID");

ALTER TABLE "uuTest" ADD FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID");

ALTER TABLE "cuTest" ADD FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID");

ALTER TABLE "cuTest" ADD FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID");

ALTER TABLE "dsTest" ADD FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID");

ALTER TABLE "dsTest" ADD FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID");

ALTER TABLE "Perm" ADD FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID");

ALTER TABLE "Perm" ADD FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID");

ALTER TABLE "Proctor" ADD FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID");

ALTER TABLE "Proctor" ADD FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID");

ALTER TABLE "CBR" ADD FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID");

ALTER TABLE "CBR" ADD FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID");

ALTER TABLE "DrillMethod" ADD FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID");

ALTER TABLE "_Client" ADD FOREIGN KEY ("_Client_ID") REFERENCES "_Project" ("_Client_ID");

ALTER TABLE "Final_Strata" ADD FOREIGN KEY ("_Geo_ID") REFERENCES "Geology_Library" ("_Geo_ID");

ALTER TABLE "Field_Strata" ADD FOREIGN KEY ("_Geo_ID") REFERENCES "Geology_Library" ("_Geo_ID");

ALTER TABLE "Final_Strata" ADD FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID");

ALTER TABLE "Field_Strata" ADD FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID");

ALTER TABLE "200wash" ADD FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID");

ALTER TABLE "200wash" ADD FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID");

ALTER TABLE "Hydrometer" ADD FOREIGN KEY ("_Sample_ID") REFERENCES "_Samples" ("_Sample_ID");

ALTER TABLE "Hydrometer" ADD FOREIGN KEY ("_Method_ID") REFERENCES "TestMethod" ("_Method_ID");

ALTER TABLE "RockCoring" ADD FOREIGN KEY ("_CoringMethod_ID") REFERENCES "CoringMethod" ("_CoringMethod_ID");

ALTER TABLE "_caveIn" ADD FOREIGN KEY ("_holeID") REFERENCES "_HoleInfo" ("_holeID");
