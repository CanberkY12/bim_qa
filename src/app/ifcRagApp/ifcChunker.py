##
#           In this file only graphBasedChunking is used for the chunking of the ifc elements.
#           Initially the chunking based of ifcOpenShell, however in order to make RAG more graph aware it is better to chunk graph data directly.
#           ! When the code runs the chunks are saved in local directory. 


import ifcopenshell.util
import ifcopenshell.util.element

import ifcopenshell
import ifcopenshell.geom
from langchain.text_splitter import RecursiveCharacterTextSplitter

# neo4j connection for method testing is to be erased later on.
import dotenv
from neo4j import GraphDatabase
from langchain_community.graphs import Neo4jGraph



# Load the IFC file
ifc_file = ifcopenshell.open("C:/Users/berky/Downloads/small (1).ifc")


class IfcElement:
    def __init__(self, ifc_file):
        self.guid = None
        self.name = None
        self.description = None
        self.type_name = None
        self.ifc_file = ifc_file
        self.nodes = None
        self.relationships = None

        self.url= dotenv.get_key(".env" ,"url")
        self.username=dotenv.get_key(".env" ,"username")
        self.password=dotenv.get_key(".env" ,"password")
        self.user_input = None
        self.graph = Neo4jGraph(url=self.url,username=self.username,password=self.password,sanitize=True)
        self.schema = self.graph.schema
        self.driver = self.connect()



    def connect(self):
        
        driver = GraphDatabase.driver(self.url, auth=(self.username, self.password))

        print("Connected to the Neo4j driver.", driver)
        return driver
    
    def save_chunk(self, chunk):
        """Save a chunk to a file."""
        output_path = "C:/Users/berky/oxide/data/chunks.txt"
        with open(output_path, "a") as file:
            file.write(chunk + "\n")
        print(f"Saved chunks to {output_path}.")
        

    def graphBasedChunking(self):
        # Ifc models are based on aggregationand containment logic which is using nodes for indicating the relationships between IfcElements.
        # The retrieval of the content of the ifc KG must completely depend on node based statements.
        # During the cypher query generation the importatn part is to get the node labels right and the relationships can be completely skipped.
        # Firstly running hardcoded cypher queries to extract the nodes following their aggragation and containment relations.
        allNodesCypher = "MATCH (n)-[r]->(m) RETURN DISTINCT labels(n)"
        allRelNodesCypher = "MATCH (n)-[r]->(m) WHERE m.__instance_of STARTS WITH 'IfcRel' RETURN DISTINCT labels(m)"
        allNodesCon2NodesCypher = "MATCH (n)-[r]->(m)-[t]->(k) WHERE m.__instance_of STARTS WITH 'IfcRel' RETURN DISTINCT labels(n), labels(m), labels(k)"
        pathofNodesCypher= "MATCH p = shortestPath((w:IfcWindow)-[*]->(wall:IfcWallStandardCase)) RETURN DISTINCT p" # just an example but the implementation is dynamic.
        buildingCypher = "MATCH (n:IfcBuilding)-[r]->(m:IfcRelAggregates)-[t]->(k) RETURN DISTINCT labels(n), r, labels(m), t, labels(k)"

        # Now running these queiries and storing the nodes and rel nodes.
        session = self.driver.session()
        nodes = []
        relNodes = []
        try:
            result = session.run(allNodesCypher)
            for record in result:
                val = record.values()[0][0]
                if "IfcRel" in val:
                    relNodes.append(val)
                else:
                    nodes.append(val)
            print("Nodes: ",nodes)
            print("RelNodes: ",relNodes)
        except Exception as e:
            print("Error while querying the nodes and relationships from db: ", e)
        finally:
            session.close()

        # Now we have nodes and rel nodes, so its time to get the paths between all the elements in the kg (if they exist oc).
        nodeCons = []
        iterNodes = nodes
        try:
            node1 ="IfcBuilding"
            session = self.driver.session()
            
            iterNodes.remove(node1)
            print("node1: ",node1)
            for node2 in iterNodes:
                #print("node2: ",node2)
                if node1 != node2:
                    try:
                        result = session.run(f"MATCH p = shortestPath((n:{node1})-[*]->(m:{node2})) RETURN DISTINCT p")
                        nodeCons.append(result.data())
                    except Exception as e:
                        print("Error while querying the nodes and relationships: ", e)
                        continue
            for record in nodeCons:
                print("record: ",record)

            # Save the node connections to file
            for record in nodeCons:
                if record:  # Check if record is not empty
                    # Convert record to string format for saving
                    chunk_text = str(record)
                    self.save_chunk(chunk_text)
                    print(f"Saved connection between {node1} and another node")
        except Exception as e:
            print("Error while querying the nodes and relationships from db: ", e)
        finally:
            session.close()
    # Extract relevant data from IFC elements and prepare for chunking
    # This method was used for kg depending chunking but it is not used in ifcopenshell implementation.
    def extract_ifc_data(self):
        #self.llmBasedChunking()
        
        RelNodes = []
        with self.driver.session() as session:
            try:
                nodes = session.run("MATCH (n) RETURN DISTINCT labels(n) AS node")
                print("Nodes received from kg for chunking...")
                relationships = session.run("MATCH ()-[r]->() RETURN DISTINCT type(r) AS relationship")
                print("Relationships received from kg for chunking...")
                for record in nodes:
                    if any("IfcRel" in label for label in record["node"]):
                        RelNodes.append(record["node"])
                        #print(record["node"])
                
                #for record in relationships:
                #    print(record["relationship"])
            except Exception as e:
                print("Error while querying the nodes and relationships from db: ", e)
        
        data = []
        for element in self.ifc_file.by_type("IfcElement"):
            # Extract meaningful information
            name = getattr(element, "Name", "Unnamed")
            description = getattr(element, "Description", "No description")
            type_name = element.is_a()
            guid = element.GlobalId

            # Find relationships
            spatial_structure = [
                rel.RelatingStructure.Name for rel in self.ifc_file.by_type("IfcRelContainedInSpatialStructure")
                if element in rel.RelatedElements
            ]
            connected_elements = [
                rel.RelatingElement.Name for rel in self.ifc_file.by_type("IfcRelConnectsElements")
                if element == rel.RelatedElement
            ]



            # Create text representation
            relationships = (
                f"Contained in: {', '.join(spatial_structure) or 'None'}\n"
                f"Connected to: {', '.join(connected_elements) or 'None'}\n"
            )

            
            # Combine into a text representation
            text = f"GUID: {guid}\nType: {type_name}\nName: {name}\nDescription: {description}\n{relationships}\n"
            data.append(text)
        del self.ifc_file
        return "\n".join(data)  # Combine all data into a single string
    
    def create_chunks(self):
        """This cypher query gives the structure from building to the elements in the building.
        MATCH (n:IfcBuilding)-[r]->(m:IfcRelAggregates)-[t]->(k)-[y]->(l:IfcRelContainedInSpatialStructure)-[u]->(j)
        RETURN DISTINCT labels(n), r, labels(m), t, labels(k), y, labels(l), u, labels(j)

        """
        print("Creating chunks...")
        schema = self.graph.schema
        print("schema: ",schema)
        #RelNodes = []
        chunks = []
        with self.driver.session() as session:
            try:
                nodes = session.run("MATCH (n) RETURN DISTINCT labels(n) AS node")
                #print("Nodes received from kg for chunking...")
                relationships = session.run("MATCH ()-[r]->() RETURN DISTINCT type(r) AS relationship")
                #print("Relationships received from kg for chunking...")
                for record in nodes:
                    #print("record: ",record)

                    #if any("IfcRel" in label for label in record["node"]):
                    #    RelNodes.append(record["node"])
                        #print(record["node"])
                        
                    for ifcElem in record["node"]:
                        #print("ifcElem: ",ifcElem)
                        for element in self.ifc_file.by_type(ifcElem):
                            if hasattr(element, 'GlobalId'):
                                print("element: ",element)
                                #additional_attributes = {}
                                #related_nodes = []
                                #if any("Ifc" in label for label in element):
                                # Extract meaningful information
                                name = getattr(element, "Name", "Unnamed")
                                step_file_id = element.id()
                                type_name = element.is_a()
                                guid = element.GlobalId
                                related_nodes = getattr(element, "ObjectPlacement", "Unnamed")
                                #representation = getattr(element, "Representation", "Unnamed")
                                #print("name: ",name)
                                #print("step_file_id: ",step_file_id)
                                #print("type_name: ",type_name)
                                #print("guid: ",guid)
                                related_node_ids = [rel.id() for rel in related_nodes if hasattr(rel, 'id')]
                                #print("related_node_ids: ", related_node_ids)
                                #print("representation: ",representation)
                        
                                additional_attributes = {}
                                if element == "IfcWindow":
                                    additional_attributes["Width"] = getattr(element, "OverallWidth", "Unknown Width")
                                    additional_attributes["Height"] = getattr(element, "OverallHeight", "Unknown Height")
                                elif element == "IfcDoor":
                                    additional_attributes["Width"] = getattr(element, "OverallWidth", "Unknown Width")
                                    additional_attributes["Height"] = getattr(element, "OverallHeight", "Unknown Height")

                    # When a query comes, the base node has many relations and the llm must know each relation with to what node it is connected.
                    # that is the most crucial part of the llm based chunking.
                    # llm can have MATCH (w:ifcWindow), but must also be aware ifcFillingElement is connected ifcFilling sort of connections and send them to the llm.
                
                                # Create chunk with enriched data
                                chunk = {
                                    "GUID": guid,
                                    "Type": type_name,
                                    "Name": name,
                                    "step_file_id": step_file_id,
                                    "Relationships": related_node_ids,
                                    #"Representation": representation,
                                    #"AdditionalAttributes": additional_attributes  # Include additional attributes
                                }
                                #print("chunk: ",chunk)
                                chunks.append(chunk)


            except Exception as e:
                print("Error while querying the nodes and relationships from db: ", e)

        #print(f"Generated {len(chunks)} chunks.")
        return chunks



    def splitter(self):
        # Extract IFC data
        #ifc_text_data = self.extract_ifc_data()
        ifc_text_data = self.create_chunks()
        #print("ifc_text_data: ",type(ifc_text_data))
        ifc_text_data = [str(chunk) for chunk in ifc_text_data]
        # Define the splitter
        print("Splitting the text...")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,       # Maximum size of each chunk
            chunk_overlap=10      # Overlap between chunks to ensure context continuity
        )

        # Split the text
        chunks = splitter.create_documents(ifc_text_data)
        
        return chunks

# Create an instance of the IfcElement class
ifc_element = IfcElement(ifc_file)
#for element in ifc_file:
#    print(element,": " ,element.get_info())
 
 #"IfcRelContainedInSpatialStructure"

# Extract and split IFC data
chunks = ifc_element.graphBasedChunking()
"""
for chunk in chunks:
    print("chunk :", chunk)
    print(len(chunks))"""
# Close the file (useful in some scenarios)
