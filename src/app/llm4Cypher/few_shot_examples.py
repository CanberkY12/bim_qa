examples = [
    {
        "question": "Retrieve all walls.", 
        "cypher_query": "MATCH (n:IfcWall) RETURN n;"
    },
    {
        "question": "Find all doors with a specific width.", 
        "cypher_query": "MATCH (n:IfcDoor) WHERE n.Width IS NOT NULL RETURN n;"
    },
    {
        "question": "Find the name of each IfcBuilding.", 
        "cypher_query": "MATCH (b:IfcBuilding) RETURN b.Name"
    },
    {
        "question": "Query the construction type of all IfcWallStandardCase.", 
        "cypher_query": "MATCH (w:IfcWallStandardCase)-[:HAS_PROPERTY]->(p:IfcConstructionType) RETURN w, p"
    },
    {
        "question": "Get all IfcSlab elements and the spaces they are associated with.", 
        "cypher_query": "MATCH (s:IfcSlab)-[:PART_OF]->(sp:IfcSpace) RETURN s, sp"
    },
    {
        "question": "Retrieve all IfcWindow instances along with their dimensions.", 
        "cypher_query": "MATCH (w:IfcWindow)-[:HAS_PROPERTY]->(p:IfcDimension) RETURN w, p"
    },
    {
        "question": "Find the name of all IfcDoor elements and their material type.", 
        "cypher_query": "MATCH (d:IfcDoor)-[:HAS_PROPERTY]->(p:IfcMaterialType) RETURN d.Name, p"
    },
    {
        "question": "List all IfcSpace entities and their associated zones.", 
        "cypher_query": "MATCH (s:IfcSpace)-[:PART_OF]->(z:IfcZone) RETURN s, z"
    },
    {
        "question": "Get all IfcBuildingStorey instances and the height property.", 
        "cypher_query": "MATCH (b:IfcBuildingStorey)-[:HAS_PROPERTY]->(p:IfcHeight) RETURN b, p"
    },
    {
        "question": "Find all IfcBeam elements and their related load-bearing properties.", 
        "cypher_query": "MATCH (b:IfcBeam)-[:HAS_PROPERTY]->(p:IfcLoadBearing) RETURN b, p"
    },
    {
        "question": "Query all IfcPipeSegment instances and their associated flow properties.", 
        "cypher_query": "MATCH (p:IfcPipeSegment)-[:HAS_PROPERTY]->(f:IfcFlowProperty) RETURN p, f"
    },
    {
        "question": "Find the name of each IfcMaterial.", 
        "cypher_query": "MATCH (m:IfcMaterial) RETURN m.Name"
    },
    {
        "question": "Retrieve all IfcCovering elements and their associated thickness.", 
        "cypher_query": "MATCH (c:IfcCovering)-[:HAS_PROPERTY]->(t:IfcThickness) RETURN c, t"
    },
    {
        "question": "Get all IfcWallStandardCase instances and their fire rating property.", 
        "cypher_query": "MATCH (w:IfcWallStandardCase)-[:HAS_PROPERTY]->(f:IfcFireRating) RETURN w, f"
    },
    {
        "question": "Find all IfcElementQuantity instances and their associated material quantities.", 
        "cypher_query": "MATCH (e:IfcElementQuantity)-[:HAS_PROPERTY]->(q:IfcMaterialQuantity) RETURN e, q"
    },
    {
        "question": "Query all IfcSlab elements and their associated structural property.", 
        "cypher_query": "MATCH (s:IfcSlab)-[:HAS_PROPERTY]->(p:IfcStructuralProperty) RETURN s, p"
    },
    {
        "question": "Retrieve all IfcSpace instances and the associated space usage type.", 
        "cypher_query": "MATCH (s:IfcSpace)-[:HAS_PROPERTY]->(u:IfcSpaceUsageType) RETURN s, u"
    },
    {
        "question": "Find all IfcRelContainedInSpatialStructure relationships.", 
        "cypher_query": "MATCH (r:IfcRelContainedInSpatialStructure) RETURN r"
    },
    {
        "question": "Get the owner history of all IfcBuilding elements.", 
        "cypher_query": "MATCH (b:IfcBuilding)-[:HAS_OWNER_HISTORY]->(o:IfcOwnerHistory) RETURN b, o"
    },
    {
        "question": "Query all IfcWindow instances and their associated thermal transmittance property.", 
        "cypher_query": "MATCH (w:IfcWindow)-[:HAS_PROPERTY]->(t:IfcThermalTransmittance) RETURN w, t"
    },
    {
        "question": "Retrieve the thermal insulation properties of all IfcRoof instances.", 
        "cypher_query": "MATCH (r:IfcRoof)-[:HAS_PROPERTY]->(t:IfcThermalInsulation) RETURN r, t"
    },
    {
        "question": "Find all IfcMaterialLayer instances and their associated material types.", 
        "cypher_query": "MATCH (m:IfcMaterialLayer)-[:HAS_PROPERTY]->(t:IfcMaterialType) RETURN m, t"
    },
    {
        "question": "Get all IfcBuilding elements and their associated location.", 
        "cypher_query": "MATCH (b:IfcBuilding)-[:LOCATED_IN]->(l:IfcLocation) RETURN b, l"
    },
    {
        "question": "Find all IfcWall instances and their load-bearing properties.", 
        "cypher_query": "MATCH (w:IfcWall)-[:HAS_PROPERTY]->(l:IfcLoadBearingProperty) RETURN w, l"
    },
    {
        "question": "Get all IfcWindow instances and their associated visual properties.", 
        "cypher_query": "MATCH (w:IfcWindow)-[:HAS_PROPERTY]->(v:IfcVisualProperty) RETURN w, v"
    },
    {
        "question": "Retrieve all IfcZone instances and their associated spaces.", 
        "cypher_query": "MATCH (z:IfcZone)-[:HAS_SPACE]->(s:IfcSpace) RETURN z, s"
    },
    {
        "question": "Query the fire resistance properties of all IfcWall elements.", 
        "cypher_query": "MATCH (w:IfcWall)-[:HAS_PROPERTY]->(f:IfcFireResistance) RETURN w, f"
    },
    {
        "question": "Get all IfcRelAggregates relationships in the dataset.", 
        "cypher_query": "MATCH (r:IfcRelAggregates) RETURN r"
    },
    {
        "question": "Retrieve the dimension properties of all IfcSlab elements.", 
        "cypher_query": "MATCH (s:IfcSlab)-[:HAS_PROPERTY]->(d:IfcDimension) RETURN s, d"
    },
    {
        "question": "List all IfcSite elements and their related spatial location properties.", 
        "cypher_query": "MATCH (s:IfcSite)-[:HAS_PROPERTY]->(p:IfcSpatialLocation) RETURN s, p"
    },
    { 
        "question": "Find all IfcDoor instances and their associated fire rating.", 
        "cypher_query": "MATCH (d:IfcDoor)-[:HAS_PROPERTY]->(f:IfcFireRating) RETURN d, f"
    },
    {
        "question": "Get all IfcColumn instances and their associated weight properties.", 
        "cypher_query": "MATCH (c:IfcColumn)-[:HAS_PROPERTY]->(w:IfcWeight) RETURN c, w"
    },
    {
        "question": "Retrieve the structural properties of all IfcBeam elements.", 
        "cypher_query": "MATCH (b:IfcBeam)-[:HAS_PROPERTY]->(p:IfcStructuralProperty) RETURN b, p"
    },
    {
        "question": "Get all IfcMaterial instances and the quantity of material used.", 
        "cypher_query": "MATCH (m:IfcMaterial)-[:HAS_PROPERTY]->(q:IfcQuantity) RETURN m, q"
    }
    # Add more examples as needed...
]