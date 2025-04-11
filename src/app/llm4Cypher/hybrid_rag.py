#
#           This file is not part of the workflow.
#           It is completely different implementation that is meant for learning the logic of hybrid RAG.
#           So, this is not runnin gin the app.
#



import os
import dotenv

# Package imports
import ollama
import subprocess
import ifcopenshell
from neo4j import GraphDatabase
from langchain_ollama import OllamaLLM
#from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from neo4j_graphrag.indexes import create_vector_index
from neo4j_graphrag.retrievers import VectorRetriever
from langchain_community.vectorstores import SKLearnVectorStore
from neo4j_graphrag.retrievers import HybridCypherRetriever
from neo4j_graphrag.generation import RagTemplate, GraphRAG

# Import the client

os.environ["GROQ_API_KEY"] = dotenv.get_key(".env" ,"GROQ_API_KEY")

class RunHybridRAG:
    def __init__(self):
        self.url=dotenv.get_key(".env" ,"url")
        self.username=dotenv.get_key(".env" ,"username")
        self.password=dotenv.get_key(".env" ,"password")
        self.user_input = "Retrieve all the slabs in the model."
        self.cypher_query = None
        self.driver = self.connect()

    def connect(self):
        
        driver = GraphDatabase.driver(self.url, auth=(self.username, self.password))
        print("Connected to the Neo4j graph.")
        return driver

    # Create a vector index
    def create_vector_index(self):
        DIMENSION=1536
        # This file is going to be received from the frontend as a file upload. For now, it is hardcoded.
        # However, the ifcChunker also needs to receive nodes from kg of neo4j and iterate over them to create the chunks.
        #ifc_file = ifcopenshell.open("C:/Users/berky/Downloads/small (1).ifc")
        #ifc_element = ifcChunker.IfcElement(ifc_file)
        #with self.driver.session() as session:
        #    try:
        #        nodes = session.run("MATCH (n) RETURN DISTINCT labels(n) AS node")
        #        print("Nodes received from kg for chunking...")
        #        relationships = session.run("MATCH ()-[r]->() RETURN DISTINCT type(r) AS relationship")
        #        print("Relationships received from kg for chunking...")
        #    except Exception as e:
        #        print("Error while querying the nodes and relationships from db: ", e)

        #chunks = ifc_element.splitter()
        create_vector_index(
            self.driver,
            name="ifcModelEmbeddings",
            label="IfcElement",
            embedding_property="vectorProperty",
            dimensions=DIMENSION,
            similarity_fn="euclidean",
        )
        


    
    # Create a full-text index
    def create_fulltext_index(self):
        query = """
        CREATE FULLTEXT INDEX ifcFulltext IF NOT EXISTS FOR (n:Entity) ON EACH [n.name, n.description, n.type, n.GlobalId]
        """
        with self.driver.session() as session:
            try:
                session.run(query)
                print("Full-text index 'ifcFulltext' created successfully.")
            except:
                print("Full-text index 'ifcFulltext' already exists.")

    def llm(self):
        ollama.pull("llama3.2")
        llm = OllamaLLM(
            model="llama3.2",
            temperature=0.0,
            max_tokens=None,
            timeout=None,
            max_retries=3,
        )
        return llm

    def main(self):

        # Create an embedder
        ollama.pull("llama3.2")
        embedder = OllamaEmbeddings(model="llama3.2")
        print("Embedder created successfully.", embedder)


        #This retriever is not receivng and cypher prompts. It is only receiving the user input.
        """
        retriever = HybridRetriever(
            self.driver,
            vector_index_name="ifcModelEmbeddings",
            fulltext_index_name="ifcFulltext",
            embedder=embedder,
            return_properties=["name", "type", "properties", "globalid"],
        )
        """
        #query_text = Is the User's natural language prompt that is used for invoking.
        query_text = self.user_input
        if not self.user_input:
            raise ValueError("User input cannot be empty. Provide a query.")

        # Create a retriever
        vector_retriever = VectorRetriever(
            self.driver,
            index_name="ifcModelEmbeddings",
            embedder=embedder,
            )
        question = "Find all spaces with an area greater than 50 square meters."

        context = """Nodes:
                    - IfcSpace (GlobalId: "space1", Name: "Room 101", GrossFloorArea: 75.0)
                    - IfcWall (GlobalId: "wall1", Name: "Wall A", Material: "Concrete")
                    - IfcWall (GlobalId: "wall2", Name: "Wall B", Material: "Brick")

                    Relationships:
                    - IfcRelContainedInSpatialStructure: "wall1" isContainedIn "space1"
                    - IfcRelContainedInSpatialStructure: "wall2" isContainedIn "space1"

                    Properties:
                    - IfcSpace: {Name: "Room 101", GrossFloorArea: 75.0}
                    - IfcWall: {Name: "Wall A", Material: "Concrete"}
                    - IfcWall: {Name: "Wall B", Material: "Brick"}"""
        
        examples = """Example 1:
                    Question: "Find all spaces with an area greater than 50 square meters."
                    Nodes: [
                        {"GlobalId": "space1", "Name": "Room 101", "GrossFloorArea": 75.0}
                    ]
                    Relationships: []
                    Properties: [
                        {"node": "space1", "property": "GrossFloorArea", "value": 75.0}
                    ]

                    Example 2:
                    Question: "Find all walls made of concrete."
                    Nodes: [
                        {"GlobalId": "wall1", "Name": "Wall A", "Material": "Concrete"}
                    ]
                    Relationships: []
                    Properties: [
                        {"node": "wall1", "property": "Material", "value": "Concrete"}
                    ]"""
        
        structure =  """"Nodes: [
                    {"GlobalId": "space1", "Name": "Room 101", "GrossFloorArea": 75.0},
                    {"GlobalId": "wall1", "Name": "Wall A", "Material": "Concrete"},
                    {"GlobalId": "wall2", "Name": "Wall B", "Material": "Brick"}
                ]
                Relationships: [
                    {"type": "IfcRelContainedInSpatialStructure", "start": "wall1", "end": "space1"},
                    {"type": "IfcRelContainedInSpatialStructure", "start": "wall2", "end": "space1"}
                ]
                Properties: [
                    {"node": "space1", "property": "GrossFloorArea", "value": 75.0},
                    {"node": "wall1", "property": "Material", "value": "Concrete"},
                    {"node": "wall2", "property": "Material", "value": "Brick"}
                ]"""
        llm = self.llm()
        rag_template = RagTemplate(
            template="""
                 "Extract all relevant nodes, relationships, and properties from the IFC knowledge graph "
                "needed to answer the question. The IFC schema includes entities such as IfcWall, IfcSpace, "
                "IfcDoor, IfcWindow, and their attributes (e.g., Name, Dimensions, Area, Material). "
                "Relationships include spatial containment (e.g., IfcRelContainedInSpatialStructure), connections "
                "(e.g., IfcRelConnectsElements), and aggregations (e.g., IfcRelAggregates). "
                "Return the relevant nodes, relationships, and properties in structured format as shown below in structure. "
                "\n\n"
                "Context:\n"
                "{context}\n\n"
                "Examples:\n"
                "{examples}\n\n"

                

                Question:
                "Find all walls connected to spaces with an area greater than 50 square meters."

                Return the relevant nodes, relationships, and properties as structured data in this format:
                Nodes: [list of relevant nodes with properties]
                Relationships: [list of relevant relationships]
                Properties: [list of relevant properties with their values].
            """,
            expected_inputs=["context", "examples"]
)

        vector_rag  = GraphRAG(llm=llm, retriever=vector_retriever, prompt_template=rag_template)
  
        result = vector_rag.search(self.user_input, retriever_config={'top_k':5})
        answer = result.get('answer', 'No answer found')
        print("Vector RAG result: ", answer)


        return vector_rag

    def close(self):
        self.driver.close()

if __name__ == "__main__":
    rag = RunHybridRAG()
    rag.create_vector_index()
    rag.create_fulltext_index()
    rag.main()

"""        # Reload the vector store
        #try:
        #    vectorstore = self.create_vector_index()
        #except FileNotFoundError:
        #    print("Vector store not found...")
            
        


        hyCy_retriever = HybridCypherRetriever(
            driver = self.driver, 
            vector_index_name  = "ifcModelEmbeddings",
            fulltext_index_name = "ifcFulltext",
            retrieval_query = retrieval_query, 
            embedder = embedder,
        )

        hyCy_retrieverresult = hyCy_retriever.search(query_text=query_text, top_k=5)
        print("Cypher retriever: ", hyCy_retrieverresult)"""

