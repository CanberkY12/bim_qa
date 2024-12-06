import os
import dotenv

# Package imports
import ollama
import subprocess
import ifcopenshell
from neo4j import GraphDatabase
#from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import SKLearnVectorStore
from neo4j_graphrag.retrievers import HybridCypherRetriever

# Local imports
import ifcChunker
# Import the client

os.environ["GROQ_API_KEY"] = dotenv.get_key(".env" ,"GROQ_API_KEY")

class RunHybridRAG:
    def __init__(self):
        self.url=dotenv.get_key(".env" ,"url")
        self.username=dotenv.get_key(".env" ,"username")
        self.password=dotenv.get_key(".env" ,"password")
        self.user_input = None
        self.cypher_query = None
        self.driver = self.connect()

    def connect(self):
        
        driver = GraphDatabase.driver(self.url, auth=(self.username, self.password))
        print("Connected to the Neo4j graph.")
        return driver

    # Create a vector index
    def create_vector_index(self):
        # This file is going to be received from the frontend as a file upload. For now, it is hardcoded.
        # However, the ifcChunker also needs to receive nodes from kg of neo4j and iterate over them to create the chunks.
        ifc_file = ifcopenshell.open("C:/Users/berky/Downloads/small (1).ifc")
        ifc_element = ifcChunker.IfcElement(ifc_file)
        #with self.driver.session() as session:
        #    try:
        #        nodes = session.run("MATCH (n) RETURN DISTINCT labels(n) AS node")
        #        print("Nodes received from kg for chunking...")
        #        relationships = session.run("MATCH ()-[r]->() RETURN DISTINCT type(r) AS relationship")
        #        print("Relationships received from kg for chunking...")
        #    except Exception as e:
        #        print("Error while querying the nodes and relationships from db: ", e)

        chunks = ifc_element.splitter()

        #persist_directory = "C:/Users/berky/oxide/src/app/llmGraphQL/vector_store"  # Directory to save the vector store

        ollama.pull("nomic-embed-text")

        vectorstore = SKLearnVectorStore.from_documents(
            documents=chunks,
            embedding=OllamaEmbeddings(model="nomic-embed-text"),
        )

        #vectorstore = Chroma.from_documents(
        #    documents= chunks,
        #    embedding = OllamaEmbeddings(model="nomic-embed-text"),
        #    collection_name= "ifcModelEmbeddings",
        #    persist_directory=persist_directory,
        #)

        #vectorstore.persist()  # Save the vector store to disk
        print(vectorstore)
        return vectorstore
        # Part below was meant to be used for creating the vector index in the Neo4j database but not going to be used.
        drop_index_query = """ DROP INDEX ifcModelEmbeddings IF EXISTS; """


        query = """
        CREATE VECTOR INDEX ifcModelEmbeddings IF NOT EXISTS
            FOR (m:Entity)
            ON m.embedding
            OPTIONS { indexConfig: { 
            `vector.dimensions`: 3072,

            `vector.similarity_function`: 'cosine'
            }
        }
        """
        #with self.driver.session() as session:
        #    try:
        #        session.run(drop_index_query)
        #        print("Vector index 'ifcModelEmbeddings' deleted successfully.")
        #    except Exception as e:
        #        print("Error deleting vector index:", e)

        #    try:
        #        session.run(query)
        #        print("Vector index 'ifcModelEmbeddings' created successfully.")
        #    except Exception as e:
        #        print("Error creating vector index:", e)
    
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

    def main(self):

        #model_name = "mxbai-embed-large"
        model_name = "llama3.2"

        try:
            # Use subprocess to call the Ollama CLI
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                encoding="utf-8",  # Explicitly use UTF-8,
                errors="replace",  # Replace invalid characters
                check=True,  # Raises an exception if the command fails
            )
            print(f"Model {model_name} pulled successfully:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to pull model {model_name}. Error:\n{e.stderr}")
        except FileNotFoundError:
            print("Ollama CLI not found. Ensure it is installed and in your PATH.")


        embedder = OllamaEmbeddings(model=model_name)
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
        #retriever_result = retriever.search(query_text=query_text, top_k=3)
        #print(retriever_result.stdout.decode('utf-8', errors='replace'))  # Decode manually with error handling
        #print("normal retriever: ",retriever_result)


        #Retrieval Query = Is the cypher query genereted from lchain2cypher text and send to  cypher hybrid retriever.
        retrieval_query = self.cypher_query
        #"""
        #                MATCH (n:Entity)
        #                WHERE n.type = $slab
        #                RETURN n.name, n.type, n.properties, n.GlobalId
        #                """

        #similar_docs = self.create_vector_index().similarity_search(query_text, k=5)
        #doc_ids = [doc.metadata["id"] for doc in similar_docs]
        # Directory where the vector store was saved
        persist_directory = "C:/Users/berky/oxide/src/app/llmGraphQL/vector_store"

        # Reload the vector store
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
        print("Cypher retriever: ", hyCy_retrieverresult)
        return hyCy_retrieverresult

    def close(self):
        self.driver.close()

#if __name__ == "__main__":
#rag = RunHybridRAG()
#persist_directory = "C:/Users/berky/oxide/src/app/llmGraphQL/vector_store"


#vectorstore = rag.create_vector_index()
#retriever =  vectorstore.as_retriever(k = 3)
#result = retriever.invoke("What are the names of all the walls in the model?")
#print(result)

#    rag.create_fulltext_index()
#    rag.user_input = generated_cypher
#    result = rag.main()
#    print(result)
#    rag.close()
#try:
#    vectorstore = Chroma(
#        embedding_function=OllamaEmbeddings(model="nomic-embed-text"),
#        collection_name="ifcModelEmbeddings",
#        persist_directory=persist_directory
#    )
#except FileNotFoundError:
#    print("Vector store not found. Generating a new vector index for hybrid RAG retrieval...")