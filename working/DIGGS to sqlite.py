import sqlite3
import xml.etree.ElementTree as ET

# --- Database connection ---
conn = sqlite3.connect("GeoDataBase")
cur = conn.cursor()

# --- Load DIGGS XML file ---
tree = ET.parse('example DIGGS file.xml')  # or any valid DIGGS file
root = tree.getroot()

ns = {
    'gml': 'http://www.opengis.net/gml/3.2',
    'diggs': 'http://diggsml.org/schema-dev',
    'xlink': 'http://www.w3.org/1999/xlink'
}

# --- Insert Client ---
clients = {}
for role in root.findall('.//diggs:role', ns):
    business = role.find('.//diggs:businessAssociate', ns)
    if business is not None:
        client_id = business.attrib.get('{http://www.opengis.net/gml/3.2}id')
        client_name = business.find('gml:name', ns).text if business.find('gml:name', ns) is not None else None
        clients[client_id] = client_name
        cur.execute('INSERT OR IGNORE INTO _Client (_Client_ID, clientName) VALUES (?, ?)', (client_id, client_name))

# --- Insert Project ---
project = root.find('.//diggs:project/diggs:Project', ns)
if project is not None:
    project_id = project.attrib.get('{http://www.opengis.net/gml/3.2}id')
    project_name = project.find('gml:name', ns).text if project.find('gml:name', ns) is not None else None
    project_desc = project.find('gml:description', ns).text if project.find('gml:description', ns) is not None else None
    client_id = next(iter(clients))  # pick first client for this example

    cur.execute('''
        INSERT OR IGNORE INTO _Project (_Project_ID, _Client_ID, projectName, projectNumber, projectCountry, projectState, projectCounty, coordinateDatum)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (project_id, client_id, project_name, None, None, None, None, None))

# --- Insert Rig Info from Equipment under constructionMethod ---
rigs = set()
for equip in root.findall('.//diggs:constructionEquipment/diggs:Equipment', ns):
    rig_id = equip.attrib.get('{http://www.opengis.net/gml/3.2}id')
    rig_name = equip.find('gml:name', ns).text if equip.find('gml:name', ns) is not None else None
    rigs.add(rig_id)
    cur.execute('''
        INSERT OR IGNORE INTO _Rig (_rigID, _rigDescription)
        VALUES (?, ?)
    ''', (rig_id, rig_name))

# --- Insert Borehole / HoleInfo ---
for borehole in root.findall('.//diggs:Borehole', ns):
    hole_id = borehole.attrib.get('{http://www.opengis.net/gml/3.2}id')
    hole_name = borehole.find('gml:name', ns).text if borehole.find('gml:name', ns) is not None else None
    borehole_type = borehole.find('diggs:boreholeType', ns).text if borehole.find('diggs:boreholeType', ns) is not None else None
    depth = borehole.find('diggs:totalMeasuredDepth', ns).text if borehole.find('diggs:totalMeasuredDepth', ns) is not None else None
    plunge = borehole.find('diggs:plunge', ns).text if borehole.find('diggs:plunge', ns) is not None else None
    bearing = borehole.find('diggs:bearing', ns).text if borehole.find('diggs:bearing', ns) is not None else None

    # Coordinates from <gml:pos>
    pos = borehole.find('.//gml:pos', ns)
    lat, lon, elev = map(float, pos.text.split()) if pos is not None else (None, None, None)

    # Start/end time
    time_interval = borehole.find('.//diggs:whenConstructed/diggs:TimeInterval', ns)
    start_time = time_interval.find('diggs:start', ns).text if time_interval is not None else None
    end_time = time_interval.find('diggs:end', ns).text if time_interval is not None else None

    # Choose a rig arbitrarily
    rig_id = next(iter(rigs)) if rigs else None

    cur.execute('''
        INSERT OR IGNORE INTO _HoleInfo (_holeID, _rigID, _Project_ID, holeName, holeType,
                                         topLatitude, topLongitude, groundSurface,
                                         azimuth, angle, bottomDepth,
                                         timeInterval_start, timeInterval_end)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        hole_id, rig_id, project_id, hole_name, borehole_type,
        lat, lon, elev,
        bearing, plunge, depth,
        start_time, end_time
    ))

# --- Commit and close ---
conn.commit()
conn.close()