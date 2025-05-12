# DIGGS_SQL
Dataflow for DIGGS, SQL, and Excel

This is an Ongoing project with the Geo Institute to build an open source database architecture that can easily integrate into geotechnical engineering workflows. This structure uses SQL to archive data in a central location with an excel interface for easy data input and retrieval. This database is also intended to be able to import and export DIGGS files. 

https://dbdiagram.io/d/DIGGS-SQL-Structure-668dcbd19939893dae7ebb48 is the current visual representation of the SQL structure being used. 

classDiagram
    class GeoData {
        <<interface>>
    }

    class SQL {
    }
    class DIGGS {
    }
    class Excel {
    }

    GeoData <|.. SQL
    GeoData <|.. DIGGS
    GeoData <|.. Excel

    class GeoData_Factory {
        <<interface>>
        +createGeoData()
    }

    class SQL_Factory {
        +createGeoData()
    }

    class DIGGS_Factory {
        +createGeoData()
    }

    class Excel_Factory {
        +createGeoData()
    }

    GeoData_Factory <|.. SQL_Factory
    GeoData_Factory <|.. DIGGS_Factory
    GeoData_Factory <|.. Excel_Factory

    SQL_Factory --> SQL : creates
    DIGGS_Factory --> DIGGS : creates
    Excel_Factory --> Excel : creates
