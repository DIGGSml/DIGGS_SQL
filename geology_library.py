#!/usr/bin/env python3
"""
Geology Library Module for DIGGS Data Processing Manager

This module provides geological data integration using Natural Earth GeoJSON data
and creates standardized geology dropdowns for Excel templates.
"""

import requests
import json
import sqlite3
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional

class GeologyLibrary:
    """Manage geological data for DIGGS processing"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self.geology_data = {}
        self.base_url = "https://raw.githubusercontent.com/martynafford/natural-earth-geojson/master/"
        
    def download_geology_data(self, scale: str = "50m") -> Dict:
        """
        Download geological features from Natural Earth GeoJSON
        
        Args:
            scale: Map scale ("10m", "50m", "110m")
            
        Returns:
            Dictionary of geological features
        """
        geology_files = {
            "rivers": f"{scale}/physical/ne_{scale}_rivers_lake_centerlines.geojson",
            "lakes": f"{scale}/physical/ne_{scale}_lakes.geojson",
            "coastlines": f"{scale}/physical/ne_{scale}_coastline.geojson",
            "land": f"{scale}/physical/ne_{scale}_land.geojson",
            "glaciers": f"{scale}/physical/ne_{scale}_glaciated_areas.geojson",
            "bathymetry": f"{scale}/physical/ne_{scale}_bathymetry_all.geojson"
        }
        
        geology_data = {}
        
        for feature_type, file_path in geology_files.items():
            url = self.base_url + file_path
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    geology_data[feature_type] = response.json()
                    print(f"Downloaded {feature_type} data")
                else:
                    print(f"Failed to download {feature_type}: {response.status_code}")
            except Exception as e:
                print(f"Error downloading {feature_type}: {e}")
                
        return geology_data
    
    def get_standard_geology_types(self) -> List[Dict]:
        """
        Get comprehensive geology types for dropdown menus
        
        Returns:
            List of geology type dictionaries
        """
        standard_types = [
            # Sedimentary - Unconsolidated
            {"strataName": "Clay", "depositType": "Sedimentary", "epoch": "Quaternary", "primComp": "Clay"},
            {"strataName": "Silt", "depositType": "Sedimentary", "epoch": "Quaternary", "primComp": "Silt"},
            {"strataName": "Sand", "depositType": "Sedimentary", "epoch": "Quaternary", "primComp": "Sand"},
            {"strataName": "Gravel", "depositType": "Sedimentary", "epoch": "Quaternary", "primComp": "Gravel"},
            {"strataName": "Silty Clay", "depositType": "Sedimentary", "epoch": "Quaternary", "primComp": "Clay", "secComp": "Silt"},
            {"strataName": "Sandy Clay", "depositType": "Sedimentary", "epoch": "Quaternary", "primComp": "Clay", "secComp": "Sand"},
            {"strataName": "Clayey Sand", "depositType": "Sedimentary", "epoch": "Quaternary", "primComp": "Sand", "secComp": "Clay"},
            {"strataName": "Silty Sand", "depositType": "Sedimentary", "epoch": "Quaternary", "primComp": "Sand", "secComp": "Silt"},
            {"strataName": "Till", "depositType": "Glacial", "epoch": "Quaternary", "primComp": "Till"},
            {"strataName": "Alluvium", "depositType": "Alluvial", "epoch": "Quaternary", "primComp": "Mixed"},
            
            # Sedimentary - Consolidated
            {"strataName": "Sandstone", "depositType": "Sedimentary", "epoch": "Mesozoic", "primComp": "Sandstone"},
            {"strataName": "Limestone", "depositType": "Sedimentary", "epoch": "Paleozoic", "primComp": "Limestone"},
            {"strataName": "Shale", "depositType": "Sedimentary", "epoch": "Paleozoic", "primComp": "Shale"},
            {"strataName": "Mudstone", "depositType": "Sedimentary", "epoch": "Mesozoic", "primComp": "Mudstone"},
            {"strataName": "Siltstone", "depositType": "Sedimentary", "epoch": "Paleozoic", "primComp": "Siltstone"},
            {"strataName": "Conglomerate", "depositType": "Sedimentary", "epoch": "Mesozoic", "primComp": "Conglomerate"},
            {"strataName": "Breccia", "depositType": "Sedimentary", "epoch": "Mesozoic", "primComp": "Breccia"},
            {"strataName": "Dolomite", "depositType": "Sedimentary", "epoch": "Paleozoic", "primComp": "Dolomite"},
            {"strataName": "Chert", "depositType": "Sedimentary", "epoch": "Paleozoic", "primComp": "Chert"},
            {"strataName": "Coal", "depositType": "Sedimentary", "epoch": "Carboniferous", "primComp": "Coal"},
            {"strataName": "Evaporite", "depositType": "Sedimentary", "epoch": "Mesozoic", "primComp": "Evaporite"},
            
            # Igneous - Intrusive
            {"strataName": "Granite", "depositType": "Igneous", "epoch": "Precambrian", "primComp": "Granite"},
            {"strataName": "Granodiorite", "depositType": "Igneous", "epoch": "Mesozoic", "primComp": "Granodiorite"},
            {"strataName": "Diorite", "depositType": "Igneous", "epoch": "Mesozoic", "primComp": "Diorite"},
            {"strataName": "Gabbro", "depositType": "Igneous", "epoch": "Precambrian", "primComp": "Gabbro"},
            {"strataName": "Peridotite", "depositType": "Igneous", "epoch": "Precambrian", "primComp": "Peridotite"},
            {"strataName": "Syenite", "depositType": "Igneous", "epoch": "Paleozoic", "primComp": "Syenite"},
            {"strataName": "Monzonite", "depositType": "Igneous", "epoch": "Mesozoic", "primComp": "Monzonite"},
            {"strataName": "Pegmatite", "depositType": "Igneous", "epoch": "Precambrian", "primComp": "Pegmatite"},
            
            # Igneous - Extrusive
            {"strataName": "Basalt", "depositType": "Igneous", "epoch": "Cenozoic", "primComp": "Basalt"},
            {"strataName": "Andesite", "depositType": "Igneous", "epoch": "Cenozoic", "primComp": "Andesite"},
            {"strataName": "Rhyolite", "depositType": "Igneous", "epoch": "Cenozoic", "primComp": "Rhyolite"},
            {"strataName": "Dacite", "depositType": "Igneous", "epoch": "Cenozoic", "primComp": "Dacite"},
            {"strataName": "Obsidian", "depositType": "Igneous", "epoch": "Cenozoic", "primComp": "Obsidian"},
            {"strataName": "Pumice", "depositType": "Igneous", "epoch": "Cenozoic", "primComp": "Pumice"},
            {"strataName": "Tuff", "depositType": "Igneous", "epoch": "Cenozoic", "primComp": "Tuff"},
            {"strataName": "Scoria", "depositType": "Igneous", "epoch": "Cenozoic", "primComp": "Scoria"},
            
            # Metamorphic - Foliated
            {"strataName": "Slate", "depositType": "Metamorphic", "epoch": "Paleozoic", "primComp": "Slate"},
            {"strataName": "Phyllite", "depositType": "Metamorphic", "epoch": "Paleozoic", "primComp": "Phyllite"},
            {"strataName": "Schist", "depositType": "Metamorphic", "epoch": "Precambrian", "primComp": "Schist"},
            {"strataName": "Gneiss", "depositType": "Metamorphic", "epoch": "Precambrian", "primComp": "Gneiss"},
            {"strataName": "Migmatite", "depositType": "Metamorphic", "epoch": "Precambrian", "primComp": "Migmatite"},
            
            # Metamorphic - Non-foliated
            {"strataName": "Quartzite", "depositType": "Metamorphic", "epoch": "Precambrian", "primComp": "Quartzite"},
            {"strataName": "Marble", "depositType": "Metamorphic", "epoch": "Precambrian", "primComp": "Marble"},
            {"strataName": "Hornfels", "depositType": "Metamorphic", "epoch": "Mesozoic", "primComp": "Hornfels"},
            {"strataName": "Amphibolite", "depositType": "Metamorphic", "epoch": "Precambrian", "primComp": "Amphibolite"},
            {"strataName": "Serpentine", "depositType": "Metamorphic", "epoch": "Precambrian", "primComp": "Serpentine"},
            {"strataName": "Greenstone", "depositType": "Metamorphic", "epoch": "Precambrian", "primComp": "Greenstone"},
            
            # Weathered and Residual Materials
            {"strataName": "Weathered Rock", "depositType": "Residual", "epoch": "Quaternary", "primComp": "Weathered Rock"},
            {"strataName": "Saprolite", "depositType": "Residual", "epoch": "Quaternary", "primComp": "Saprolite"},
            {"strataName": "Laterite", "depositType": "Residual", "epoch": "Quaternary", "primComp": "Laterite"},
            {"strataName": "Caliche", "depositType": "Residual", "epoch": "Quaternary", "primComp": "Caliche"},
            
            # Anthropogenic Materials
            {"strataName": "Fill", "depositType": "Anthropogenic", "epoch": "Holocene", "primComp": "Mixed"},
            {"strataName": "Topsoil", "depositType": "Organic", "epoch": "Holocene", "primComp": "Organic"},
            {"strataName": "Peat", "depositType": "Organic", "epoch": "Holocene", "primComp": "Peat"},
            {"strataName": "Muck", "depositType": "Organic", "epoch": "Holocene", "primComp": "Muck"},
            
            # Special Geological Materials
            {"strataName": "Karst", "depositType": "Dissolution", "epoch": "Paleozoic", "primComp": "Limestone"},
            {"strataName": "Colluvium", "depositType": "Colluvial", "epoch": "Quaternary", "primComp": "Mixed"},
            {"strataName": "Loess", "depositType": "Eolian", "epoch": "Quaternary", "primComp": "Silt"},
            {"strataName": "Hardpan", "depositType": "Cemented", "epoch": "Quaternary", "primComp": "Cemented"}
        ]
        
        return standard_types
    
    def create_geology_library_table(self, db_path: str) -> None:
        """
        Create and populate the Geology_Library table in SQLite database
        
        Args:
            db_path: Path to SQLite database
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create table exactly as defined in DIGGS sqlite.py
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "Geology_Library" (
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
            )
        ''')
        
        # Clear existing data
        cursor.execute('DELETE FROM "Geology_Library"')
        
        # Insert standard geology types
        standard_types = self.get_standard_geology_types()
        
        for i, geo_type in enumerate(standard_types, 1):
            cursor.execute('''
                INSERT INTO "Geology_Library" 
                ("_Geo_ID", "reference", "mapID", "strataName", "depositType", "epoch", "memberGroup", "primComp", "secComp", "tertComp", "addNote")
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"GEO_{i:03d}",  # TEXT PRIMARY KEY format
                "Standard Geology Library",
                f"STD_{i:03d}",
                geo_type["strataName"],
                geo_type["depositType"],
                geo_type["epoch"],
                geo_type.get("memberGroup", ""),
                geo_type["primComp"],
                geo_type.get("secComp", ""),
                geo_type.get("tertComp", ""),
                "Standard geological classification"
            ))
        
        conn.commit()
        conn.close()
        print(f"Created Geology_Library table with {len(standard_types)} entries")
    
    def get_geology_dropdown_data(self, db_path: str) -> List[str]:
        """
        Get geology data for dropdown menus
        
        Args:
            db_path: Path to SQLite database
            
        Returns:
            List of geology names for dropdown
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT "strataName" FROM "Geology_Library" ORDER BY "strataName"')
        results = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in results]
    
    def get_geology_details(self, db_path: str, strata_name: str) -> Optional[Dict]:
        """
        Get detailed geology information for a specific strata
        
        Args:
            db_path: Path to SQLite database
            strata_name: Name of the geological strata
            
        Returns:
            Dictionary with geology details or None if not found
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM "Geology_Library" WHERE "strataName" = ?
        ''', (strata_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, result))
        return None

if __name__ == "__main__":
    # Example usage
    geology_lib = GeologyLibrary()
    
    # Create a test database
    test_db = "test_geology.db"
    geology_lib.create_geology_library_table(test_db)
    
    # Get dropdown data
    dropdown_data = geology_lib.get_geology_dropdown_data(test_db)
    print(f"Available geology types: {dropdown_data}")
    
    # Get details for a specific type
    details = geology_lib.get_geology_details(test_db, "Clay")
    print(f"Clay details: {details}")