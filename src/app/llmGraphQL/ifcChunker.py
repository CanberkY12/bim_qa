import sys
import os
import ifcopenshell.util
import ifcopenshell.util.element

import numpy
import operator
import itertools

import ollama
from langchain_ollama import OllamaLLM
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
import ifcopenshell
import ifcopenshell.geom
from langchain.text_splitter import RecursiveCharacterTextSplitter

# neo4j connection for method testing is to be erased later on.
import dotenv
import neo4j
from neo4j import GraphDatabase
from langchain_community.graphs import Neo4jGraph



# Load the IFC file
#ifc_file = ifcopenshell.open("C:/Users/berky/Downloads/small (1).ifc")


class IfcElement:
    def __init__(self, ifc_file):
        self.guid = None
        self.name = None
        self.description = None
        self.type_name = None
        self.ifc_file = ifc_file
        self.nodes = None
        self.relationships = None

        self.url=dotenv.get_key(".env" ,"url")
        self.username=dotenv.get_key(".env" ,"username")
        self.password=dotenv.get_key(".env" ,"password")
        self.user_input = None
        self.graph = Neo4jGraph(url=self.url,username=self.username,password=self.password,sanitize=True)
        self.schema = self.graph.schema
        self.driver = self.connect()


    def connect(self):
        
        driver = GraphDatabase.driver(self.url, auth=(self.username, self.password))
        print("Connected to the Neo4j driver.")
        return driver
    
    def llmBasedChunking(self):
        GROQ_API_KEY="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"
        #groq_api_key = os.getenv("GROQ_API_KEY")
        #if groq_api_key is None:
        #    raise ValueError("GROQ_API_KEY environment variable is not set")
        os.environ["GROQ_API_KEY"] = GROQ_API_KEY
        print("API key received")
        ollama.pull("llama3.2")
        llm = OllamaLLM(model="llama3.2")

        """llm = ChatGroq(
            model="llama3-8b-8192",
            temperature=0.0,
            max_tokens=100,
            timeout=None,
            max_retries=3,
            # other params...
        )"""
        if self.graph is None:
            raise ValueError("Neo4j graph is not set")
        schema = self.schema
        nodes = self.nodes
        relationships = self.relationships

        # Few-shot examples
        examples = """
            Example 1:
            Schema: IFC Knowledge Graph
            Nodes: 
            - GUID: abc123, Type: IfcWall, Name: Wall1
            - GUID: def456, Type: IfcDoor, Name: Door1
            Relationships:
            - ContainedInStructure(Floor1)
            - ConnectedTo(Wall1)
            Chunks:
            Chunk 1:
            GUID: abc123
            Type: IfcWall
            Name: Wall1
            Relationships: ContainedInStructure(Floor1)
            ---
            Chunk 2:
            GUID: def456
            Type: IfcDoor
            Name: Door1
            Relationships: ConnectedTo(Wall1)

            Example 2:
            Schema: IFC Knowledge Graph
            Nodes: 
            - GUID: xyz789, Type: IfcColumn, Name: ColumnA
            - GUID: ghi012, Type: IfcSlab, Name: Slab1
            Relationships:
            - ContainedInStructure(Building1)
            - Supports(ColumnA)
            Chunks:
            Chunk 1:
            GUID: xyz789
            Type: IfcColumn
            Name: ColumnA
            Relationships: Supports(Slab1)
            ---
            Chunk 2:
            GUID: ghi012
            Type: IfcSlab
            Name: Slab1
            Relationships: ContainedInStructure(Building1)
            ---
            """

        # Prompt with few-shot examples

        template = """You are an AI model specifically designed to create text chunks for Chroma vector database indexing.

        Given the schema, nodes, and relationships of an IFC/BIM knowledge graph (Neo4j-based), generate **self-contained textual chunks**. Each chunk should:
        1. Include the key information about a node (e.g., its attributes like name, type, GUID).
        2. Include relationships between the node and its neighbors (e.g., connections like `ContainedInStructure` or `HasProperties`).
        3. Be contextually complete and limited to approximately 500 characters.

        Below are a few examples of how to generate chunks from an IFC/BIM knowledge graph:

        {{examples}}

        Return only the generated chunks as a list, separated by `---`. Do not include any other text in the response.

        Input:
        schema: {schema}
        nodes: {nodes}
        relationships: {relationships}

        Chunks:
        """
        template_ = """You are a specific model that is only generating chunks for Chroma vectordb vector index creation.
        Based on the schema, nodes and relationships of IFC/BIM model's knowledge graph which is generated from the Neo4j graph below,
        write chunks for RAG based vector index producing.
        
        Return only the chunks in the response, nothing else.
        schema: {schema}
        nodes: {nodes}
        relationships: {relationships}
        
        chunks:"""

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Generate chunks for Chroma vector DB from IFC/BIM graph."
                ),
                ("human", template),
            ]
        )

        chain = prompt | llm.bind() | StrOutputParser()
        response = chain.invoke(
            {
                "schema": schema,
                "nodes": nodes,
                "relationships": relationships
            }
        )
        #print("llm based chunks: ",response)
        return response
    
    def create_chunks(self):
        print("Creating chunks...")
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
                                #print("element: ",element)
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

    # Extract relevant data from IFC elements and prepare for chunking
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
            chunk_overlap=50      # Overlap between chunks to ensure context continuity
        )

        # Split the text
        chunks = splitter.create_documents(ifc_text_data)
        
        return chunks

# Create an instance of the IfcElement class
#ifc_element = IfcElement(ifc_file)

# Extract and split IFC data
#chunks = ifc_element.splitter()
#i = 0
#for chunk in chunks:
#    print("chunk :", chunk)
#print(len(chunks))
# Close the file (useful in some scenarios)
