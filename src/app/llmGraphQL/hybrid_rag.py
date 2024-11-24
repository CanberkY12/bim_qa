import os
import dotenv

from neo4j import GraphDatabase
import subprocess
from neo4j_graphrag.retrievers import HybridRetriever, HybridCypherRetriever
from langchain_ollama import OllamaEmbeddings
from neo4j_graphrag.types import (
    EmbedderModel,
    HybridCypherRetrieverModel,
    HybridCypherSearchModel,
    HybridRetrieverModel,
    HybridSearchModel,
    Neo4jDriverModel,
    RawSearchResult,
    RetrieverResultItem,
    SearchType,
)

# Import the client

os.environ["GROQ_API_KEY"] = dotenv.get_key(".env" ,"GROQ_API_KEY")

class RunHybridRAG:
    def __init__(self):
        self.url=dotenv.get_key(".env" ,"url")
        self.username=dotenv.get_key(".env" ,"username")
        self.password=dotenv.get_key(".env" ,"password")
        self.user_input = None
        self.driver = self.connect()

    def connect(self):
        
        driver = GraphDatabase.driver(self.url, auth=(self.username, self.password))
        print("Connected to the Neo4j graph.")
        return driver
    
    # Create a vector index
    def create_vector_index(self):
        drop_index_query = """ DROP INDEX ifcModelEmbeddings IF EXISTS; """
        with self.driver.session() as session:
            try:
                session.run(drop_index_query)
                print("Vector index 'ifcModelEmbeddings' deleted successfully.")
            except Exception as e:
                print("Vector index 'ifcModelEmbeddings' could not be deleted.", e)

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
        with self.driver.session() as session:
            try:
                session.run(drop_index_query)
                print("Vector index 'ifcModelEmbeddings' deleted successfully.")
            except Exception as e:
                print("Error deleting vector index:", e)

            try:
                session.run(query)
                print("Vector index 'ifcModelEmbeddings' created successfully.")
            except Exception as e:
                print("Error creating vector index:", e)
  

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
        import ollama
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
            
       
        #with self.driver.session() as session:
        #ollama.pull(model_name)
        embedder = OllamaEmbeddings(model=model_name)
        print("Embedder created successfully.", embedder)
        retriever = HybridRetriever(
            self.driver,
            vector_index_name="ifcModelEmbeddings",
            fulltext_index_name="ifcFulltext",
            embedder=embedder,
            return_properties=["name", "type", "properties", "globalid"],
        )
        query_text = self.user_input
        if not self.user_input:
            raise ValueError("User input cannot be empty. Provide a query.")
        retriever_result = retriever.search(query_text=query_text, top_k=3)
        #print(retriever_result.stdout.decode('utf-8', errors='replace'))  # Decode manually with error handling
        print("normal retriever: ",retriever_result)

        retrieval_query = self.user_input
        #"""
        #                MATCH (n:Entity)
        #                WHERE n.type = $slab
        #                RETURN n.name, n.type, n.properties, n.GlobalId
        #                """
        hyCy_retriever = HybridCypherRetriever(
            self.driver, "ifcModelEmbeddings", "ifcFulltext",retrieval_query, embedder
        )
        hyCy_retrieverresult = hyCy_retriever.search(query_text=query_text, top_k=5)
        print("Cypher retriever: ",hyCy_retrieverresult)
        return hyCy_retrieverresult

    def close(self):
        self.driver.close()

#if __name__ == "__main__":
#    rag = RunHybridRAG()
#    rag.create_vector_index()
#    rag.create_fulltext_index()
#    rag.user_input = generated_cypher
#    result = rag.main()
#    print(result)
#    rag.close()