import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime

# Connect to SQLite
conn = sqlite3.connect("GeoDataBase")
cur = conn.cursor()

# Namespaces
NSMAP = {
    None: "http://diggsml.org/schemas/2.6",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'xlink': "http://www.w3.org/1999/xlink",
    'gml': "http://www.opengis.net/gml/3.2",
    'diggs': "http://diggsml.org/schemas/2.6"
}

ET.register_namespace('', NSMAP[None])
ET.register_namespace('xsi', NSMAP['xsi'])
ET.register_namespace('xlink', NSMAP['xlink'])
ET.register_namespace('gml', NSMAP['gml'])
ET.register_namespace('diggs', NSMAP['diggs'])

# Root <Diggs> element
diggs = ET.Element("Diggs", {
    "xmlns": NSMAP[None],
    "xmlns:xsi": NSMAP['xsi'],
    "xmlns:xlink": NSMAP['xlink'],
    "xmlns:gml": NSMAP['gml'],
    "xmlns:diggs": NSMAP['diggs'],
    "xsi:schemaLocation": "http://diggsml.org/schemas/2.6 http://diggsml.org/schemas/2.5.a/Kernel.xsd",
    "gml:id": "GeoExport_001"
})

# 1. documentInformation
doc_info = ET.SubElement(diggs, "documentInformation")
document = ET.SubElement(doc_info, "DocumentInformation", {"gml:id": "docinfo-001"})
ET.SubElement(document, "creationDate").text = datetime.now().strftime("%Y-%m-%d")
author = ET.SubElement(document, "author")
ba = ET.SubElement(author, "BusinessAssociate", {"gml:id": "client-001"})
ET.SubElement(ba, "{%s}name" % NSMAP['gml']).text = "GeneratedClient"

# 2. project
cur.execute('SELECT _Project_ID, projectName FROM _Project')
for row in cur.fetchall():
    proj_id, proj_name = row
    project_tag = ET.SubElement(diggs, "project")
    project = ET.SubElement(project_tag, "Project", {"gml:id": proj_id})
    ET.SubElement(project, "{%s}name" % NSMAP['gml']).text = proj_name
    ET.SubElement(project, "{%s}description" % NSMAP['gml']).text = f"Exported DIGGS project {proj_name}"

# 3. samplingFeature (boreholes)
cur.execute('SELECT _holeID, _Project_ID, holeName, topLatitude, topLongitude, groundSurface, bottomDepth FROM _HoleInfo')
for row in cur.fetchall():
    hole_id, proj_id, hole_name, lat, lon, elev, depth = row
    sf_tag = ET.SubElement(diggs, "samplingFeature")
    borehole = ET.SubElement(sf_tag, "Borehole", {"gml:id": hole_id})
    ET.SubElement(borehole, "{%s}name" % NSMAP['gml']).text = hole_name
    ET.SubElement(borehole, "boreholeType").text = "BH"
    ET.SubElement(borehole, "projectRef", {"{%s}href" % NSMAP['xlink']: f"#{proj_id}"})
    
    # location
    ref_point = ET.SubElement(borehole, "referencePoint")
    point = ET.SubElement(ref_point, "PointLocation", {"gml:id": f"pt-{hole_id}"})
    ET.SubElement(point, "{%s}pos" % NSMAP['gml'], {
        "srsDimension": "3",
        "srsName": "http://www.opengis.net/def/crs/EPSG/0/4326"
    }).text = f"{lat} {lon} {elev}"
    
    ET.SubElement(borehole, "totalMeasuredDepth", {"uom": "ft"}).text = str(depth)

# 4. Write to file
tree = ET.ElementTree(diggs)
tree.write("exported_diggs.xml", encoding="utf-8", xml_declaration=True)

print("DIGGS XML successfully exported to 'exported_diggs.xml'")