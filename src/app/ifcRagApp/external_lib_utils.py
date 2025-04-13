#
#       In this file, external libraries such as bSDD are utilised for providing extra definitions and content to ifc narrations.
#       This utility is implemented in order to enrich the information embedded for RAG search.
#
#       The workflor follows: Get Ifc BuiltElements in the Graph -> Get all the extra descriptions from bsdd and add to the attributes under name  "description"
#       The following libraries are used: 
#

import os
import bsdd

import json
from neo4j import GraphDatabase
from langchain_community.graphs import Neo4jGraph

class ExternalLibUtils:
    def __init__(self):
        self.url=os.getenv("url")
        self.username=os.getenv("username")
        self.password=os.getenv("password")
        self.driver = self.connect()
        self.graph = Neo4jGraph(url=self.url,username=self.username,password=self.password)

    def connect(self):
        driver = GraphDatabase.driver(self.url, auth=(self.username, self.password))
        print("Connected to the Neo4j graph.")
        return driver
    
    
    def getListofBuiltElements(self):
        """
                   In this method, the IfcBuiltElement subclasses are gathered.
                   For some reason, the iteration only goes untill the letter "R" and the rest 
                   is written/added manually.
        """

        client = bsdd.Client()
        
        offset = 0
        try:
            classes = client.get_classes(
                dictionary_uri="https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3",
                use_nested_classes=False,
                offset=offset
                
            )
            
            #print("Classes:", classes)
            #for cl in classes["classes"]: 
            #    print(cl)
            #print(classes["classes"])
            # Filter classes where parentClassCode is IfcBuiltElement
            
            ifcbe = client.get_class(class_uri = "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/IfcBuiltElement")
            #print("ifcbe: ", ifcbe)

            built_element_classes = [
                cls for cls in classes["classes"]
                if isinstance(cls, dict) and cls.get('parentClassCode') == 'IfcBuiltElement'
            ]
            
            
            # "code" in the keys refers to the IfcType name.
            built_element_names = [
                cls.get('code') for cls in built_element_classes
            ]

            # Adding here the uniterated part of the subclasses
            built_element_names.extend([
                "IfcSlab", 
                "IfcWall", 
                "IfcWindow", 
                "IfcStair"
            ])
            
            print(f"Found {len(built_element_names)} built element classes from bSDD")
            return sorted(list(set(built_element_names)))  # Removing duplicates
        
        except Exception as e:
            print(f"Error retrieving classes from bSDD: {e}")
            return []

        
    def getListofFurnishingElements(self):
        """
        Same subclass listing method is applied for IfcFurnishingElement.
        Furnishing elements added as extra because the users might want to query information about the 
        many elements such as tables, chairs, etc. as well.
        """

        client = bsdd.Client()
        
        offset = 0
        try:
            classes = client.get_classes(
                dictionary_uri="https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3",
                use_nested_classes=False,
                offset=offset
            )
            
            # Filter classes where parentClassCode is IfcFurnishingElement
            furnishing_element_classes = [
                cls for cls in classes["classes"]
                if isinstance(cls, dict) and cls.get('parentClassCode') == 'IfcFurniture'
            ]
            
            # Extract the names here
            furnishing_element_names = [
                cls.get('code') for cls in furnishing_element_classes
            ]
            furnishing_element_names.extend(["IfcFurnishingElement"])
            
            print(f"Found {len(furnishing_element_names)} furnishing element classes from bSDD")
            return sorted(list(set(furnishing_element_names)))  # Removing duplicates
        
        except Exception as e:
            print(f"Error retrieving classes from bSDD: {e}")
            return []
        
        
    def getAllElementDescription(self, element_name):
        """
        Get the description of an element from bSDD

        dict_keys(['classType', 'referenceCode', 'parentClassReference', 'classProperties', 
        'childClassReferences', 'hierarchy', 'dictionaryUri', 'activationDateUtc', 'code', 
        'countriesOfUse', 'definition', 'name', 'uri', 'replacedObjectCodes', 'replacingObjectCodes',
        'status', 'subdivisionsOfUse', 'uid', 'versionDateUtc'])

        """
        try:
        
            client = bsdd.Client()
    
            element = client.get_class(class_uri = f"https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/class/{element_name}")
            #print("Element: ", element)
            if element:
                #print(f"Retrieved element from bSDD: {element_name}")
                #print("name: ",element.get('name'))
                #print("code: ",element.get('code'))
                #print("uri: ",element.get('uri'))
                #print("versionDateUtc: ",element.get('versionDateUtc')) # No need
                #print("status: ",element.get('status')) # No need
                #print("countriesOfUse: ",element.get('countriesOfUse'))
                #print("definition: ",element.get('definition'))
                #print("classProperties: ",element.get('classProperties'))
                #print("childClassReferences: ",element.get('childClassReferences'))
                #print("hierarchy: ",element.get('hierarchy'))
                #print("subdivisionsOfUse: ",element.get('subdivisionsOfUse'))
                #print("replacedObjectCodes: ",element.get('replacedObjectCodes'))
                #print("replacingObjectCodes: ",element.get('replacingObjectCodes'))
                #print("activationDateUtc: ",element.get('activationDateUtc'))
                #print("classType: ",element.get('classType'))
                #print("referenceCode: ",element.get('referenceCode'))
                #print("parentClassReference: ",element.get('parentClassReference'))
                #print("uid: ",element.get('uid'))
       
                properties = []
                if element.get('classProperties'):
                    for prop in element.get('classProperties'):
                        if prop.get('name'):
                            #print(f"Property: {prop.get('name')}")
                            properties.append(prop.get('name'))
                #print("properties: ",properties)

                # Definition part is highly important as it contains domain specific words and phrases taht would enhance RAG comprehension.
                description = {
                    "code": element.get("code", ""),
                    "name": element.get("name", ""),
                    "definition": element.get('definition'),
                    #"properties": properties   No need for properties
                }
                print(f"Retrieved description for {element_name}", description)
                return json.dumps(description)
            else:
                return ""
        except Exception as e:
            print(f"Error retrieving description from bSDD: {e}")

    def getGermanDescription(self, element_name):
        """
        Get the German description of an element from bSDD

        Practically the same code , but this time focusing on the German description.
        """
        try:
            # Create a bSDD client
            client = bsdd.Client()
            
            # Search for the element by name
            element = client.get_class(class_uri = f"https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/class/{element_name}",
                                       language_code="de")
            
            print(element.keys())
            if element:


                description = {
                    "code": element.get("code", ""),
                    "name": element.get("name", ""),
                    "definition": element.get('definition'),
                    #"properties": properties   No need for properties
                }
                print(f"Retrieved DE description for {element_name}", description)
                return json.dumps(description)
        except Exception as e:
            print(f"Error retrieving German description from bSDD: {e}")
            return ""
        
    def addCollectedDataToNodes(self, element_name, description):
        """
        In this method the collected descriptions are going to be added to their correspoing nodes in the knowledge graph.
        """
        # The cypher query for adding the description to the nodes.
        #Simply iteratively receives the node names and their descriptions.
        nodeRecCypher = f"MATCH (n:{element_name}) SET n.description = '{description}'"

        try:
            with self.driver.session() as session:
                session.run(nodeRecCypher)
        except Exception as e:
            print(f"Error adding description to nodes: {e}")

    def main(self):
        built_elements = self.getListofBuiltElements()
        furnishing_elements = self.getListofFurnishingElements()
        print("Built elements:", built_elements)
        print("Furnishing elements:", furnishing_elements)
        for element in built_elements:
            #description = self.getAllElementDescription(element)
            german_description = self.getGermanDescription(element)
            #self.addCollectedDataToNodes(element, description)
        #for element in furnishing_elements:
            #description = self.getAllElementDescription(element)
            #self.addCollectedDataToNodes(element, description)
        print("Done")
        
if __name__ == "__main__":
    external_lib_utils = ExternalLibUtils()
    external_lib_utils.main()
    
        
    










"""
# Print the bSDD version
print(f"bSDD version: {bsdd.__version__}")

# Create a client - no auth needed for public endpoints
client = bsdd.Client()
print("-----------------------------------------------")

# Use the updated method names with better error handling
print("Searching for wall-related classes in NL-SfB classification...")
try:
    wall_classes = client.search_in_dictionary(
        dictionary_uri="https://identifier.buildingsmart.org/uri/nlsfb/nlsfb2005/2.2",
        related_ifc_entity="IfcWall"
    )
    print(f"Found {len(wall_classes)} wall-related classes")
    
    # Debug the structure of the returned data
    print("Type of wall_classes:", type(wall_classes))
    if isinstance(wall_classes, list) and wall_classes:
        print("Type of first result:", type(wall_classes[0]))
        if isinstance(wall_classes[0], str):
            print("Results appear to be strings. Attempting to parse as JSON...")
            for i, cls_str in enumerate(wall_classes[:3]):  # Show only first 3
                try:
                    cls = json.loads(cls_str)
                    print(f"Class {i+1}: {cls.get('code', 'No code')} - {cls.get('name', 'No name')}")
                except:
                    print(f"Class {i+1}: {cls_str[:50]}...")  # Just print the string
        else:
            # Original approach for dictionary objects
            for i, cls in enumerate(wall_classes[:3]):
                print(f"Class {i+1}: {cls}")
    else:
        print("wall_classes is not a list or is empty:", wall_classes)
except Exception as e:
    print(f"Error in search_in_dictionary: {e}")
    wall_classes = []  # Initialize as empty list to avoid errors later
print("-----------------------------------------------")

# Function to generate IFC-compatible GUID
def create_guid():
    Create a new GUID for IFC entities
    return ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$', k=22))

# Now work with IfcOpenShell directly instead of using the api module
try:
    print("Working with IfcOpenShell directly...")
    ifc_file = ifcopenshell.open("C:/Users/berky/Downloads/small (1).ifc")
    
    # First, let's see what's in the file
    print(f"File schema: {ifc_file.schema}")
    
    # Find walls
    walls = ifc_file.by_type("IfcWall")
    if walls:
        wall = walls[0]
        print(f"Found wall with ID: {wall.id()}, GlobalId: {getattr(wall, 'GlobalId', 'N/A')}")
        
        # Get existing property sets
        print("\nExisting property sets:")
        for rel in ifc_file.by_type("IfcRelDefinesByProperties"):
            if wall in rel.RelatedObjects:
                pset = rel.RelatingPropertyDefinition
                print(f"  Property Set: {pset.Name}")
                
                # Show properties
                if pset.is_a("IfcPropertySet"):
                    for prop in pset.HasProperties:
                        if prop.is_a("IfcPropertySingleValue"):
                            value = prop.NominalValue.wrappedValue if prop.NominalValue else "None"
                            print(f"    - {prop.Name}: {value}")
        
        # Create a new property set manually
        print("\nCreating new property set...")
        
        # Create owner history
        owner_history = ifc_file.by_type("IfcOwnerHistory")[0]
        
        # Create property set with custom GUID generator
        pset = ifc_file.create_entity("IfcPropertySet", 
            GlobalId=create_guid(),
            OwnerHistory=owner_history,
            Name="Pset_WallCommon_bSDD",
            Description="Common properties for walls from bSDD"
        )
        
        # Create properties
        properties = []
        
        # IsExternal property (boolean)
        is_external = ifc_file.create_entity("IfcPropertySingleValue",
            Name="IsExternal",
            Description="Indicates if this wall is designed for use in the exterior of the building.",
            NominalValue=ifc_file.create_entity("IfcBoolean", True)
        )
        properties.append(is_external)
        
        # LoadBearing property (boolean)
        load_bearing = ifc_file.create_entity("IfcPropertySingleValue",
            Name="LoadBearing",
            Description="Indicates whether the wall is intended to carry loads.",
            NominalValue=ifc_file.create_entity("IfcBoolean", True)
        )
        properties.append(load_bearing)
        
        # ThermalTransmittance property (real)
        thermal = ifc_file.create_entity("IfcPropertySingleValue",
            Name="ThermalTransmittance",
            Description="Thermal transmittance coefficient (U-value).",
            NominalValue=ifc_file.create_entity("IfcReal", 0.24)
        )
        properties.append(thermal)
        
        # FireRating property (text)
        fire_rating = ifc_file.create_entity("IfcPropertySingleValue",
            Name="FireRating",
            Description="Fire rating for this wall.",
            NominalValue=ifc_file.create_entity("IfcLabel", "1HR")
        )
        properties.append(fire_rating)
        
        # Add properties to property set
        pset.HasProperties = properties
        
        # Create relationship to wall
        rel = ifc_file.create_entity("IfcRelDefinesByProperties",
            GlobalId=create_guid(),
            OwnerHistory=owner_history,
            RelatedObjects=[wall],
            RelatingPropertyDefinition=pset
        )
        
        print("Successfully created property set and linked to wall")
        
        # Define bSDD-related properties based on search results to create a narrative
        print("\nCreating bSDD narrative based on search results...")
        bsdd_narrative = "Wall information from bSDD:\n\n"
        bsdd_narrative += "Wall in IFC has the following properties:\n"
        
        # Add existing property details to the narrative
        for rel in ifc_file.by_type("IfcRelDefinesByProperties"):
            if wall in rel.RelatedObjects:
                pset = rel.RelatingPropertyDefinition
                if pset.is_a("IfcPropertySet"):
                    bsdd_narrative += f"\nProperty Set: {pset.Name}\n"
                    for prop in pset.HasProperties:
                        if prop.is_a("IfcPropertySingleValue"):
                            value = prop.NominalValue.wrappedValue if prop.NominalValue else "None"
                            bsdd_narrative += f"  - {prop.Name}: {value}\n"
        
        # Add wall class information if available - safely check the structure first
        if hasattr(wall_classes, '__len__') and len(wall_classes) > 0:
            bsdd_narrative += f"\nNL-SfB Classifications: Found {len(wall_classes)} related classes\n"
            
            # Check if we have a list of strings or another structure
            if len(wall_classes) > 0 and isinstance(wall_classes[0], str):
                for i, cls_str in enumerate(wall_classes[:3]):
                    try:
                        cls = json.loads(cls_str)
                        bsdd_narrative += f"Class {i+1}: {cls.get('code', 'Unknown')} - {cls.get('name', 'Unknown')}\n"
                    except:
                        bsdd_narrative += f"Class {i+1}: {cls_str[:50]}...\n"
        
        # Add buildingSMART definitions manually since the API calls aren't working
        bsdd_narrative += "\nIFC wall definition from buildingSMART:\n"
        bsdd_narrative += "A wall is a vertical construction that bounds or subdivides spaces. Wall is "
        bsdd_narrative += "a vertical, planar element that may bound or subdivide space. "
        bsdd_narrative += "Walls are usually vertical, or nearly vertical, planar elements, "
        bsdd_narrative += "often designed to bear structural loads. However, walls need not be load bearing.\n\n"
        
        bsdd_narrative += "Common wall properties according to buildingSMART:\n"
        bsdd_narrative += "- IsExternal: Indicates whether the wall is designed for use in the exterior of the building\n"
        bsdd_narrative += "- LoadBearing: Indicates whether the wall is intended to carry loads\n"
        bsdd_narrative += "- FireRating: Fire resistance rating for the wall\n"
        bsdd_narrative += "- ThermalTransmittance: Thermal transmittance coefficient (U-value)\n"
        
        print(bsdd_narrative)
        
        # Save to a text file for RAG purposes
        narrative_file = "C:/Users/berky/Downloads/wall_bsdd_narrative.txt"
        with open(narrative_file, "w", encoding="utf-8") as f:
            f.write(bsdd_narrative)
        print(f"Saved narrative to {narrative_file} for RAG system")
        
        # Save modified file
        output_file = "C:/Users/berky/Downloads/small_modified.ifc"
        ifc_file.write(output_file)
        print(f"Saved modified file to {output_file}")
        
    else:
        print("No walls found in the IFC file")
except Exception as e:
    print(f"Error working with IFC file: {e}")
    import traceback
    traceback.print_exc()


    # Add a function to fetch and print all available bSDD dictionaries
    def list_all_bsdd_dictionaries():
        print("\n-----------------------------------------------")
        print("Listing all available bSDD dictionaries:")
        try:
            # Get all dictionaries from bSDD
            dictionaries = client.list_dictionaries()
            
            # Print number of dictionaries found
            print(f"Found {len(dictionaries)} dictionaries")
            
            # Print each dictionary with its details
            for i, dictionary in enumerate(dictionaries):
                # Extract key details - adapt based on actual response structure
                dictionary_id = dictionary.get('namespaceUri', '')
                name = dictionary.get('name', '')
                version = dictionary.get('version', '')
                
                print(f"{i+1}. {name} (v{version})")
                print(f"   URI: {dictionary_id}")
                print()
            
            return dictionaries
        except Exception as e:
            print(f"Error listing dictionaries: {e}")
            return []

    # Call the function to print all dictionaries
    all_dictionaries = list_all_bsdd_dictionaries()
    print("-----------------------------------------------")"""