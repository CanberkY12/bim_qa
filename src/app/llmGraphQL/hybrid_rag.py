import os
import dotenv

from neo4j import GraphDatabase
import subprocess
from neo4j_graphrag.retrievers import HybridRetriever
from langchain_ollama import OllamaEmbeddings

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

            `vector.similarity_function`: 'cosine'}}
        """
        with self.driver.session() as session:
            try:
                session.run(query)
                print("Vector index 'ifcModelEmbeddings' created successfully.")
            except:
                print("Vector index 'ifcModelEmbeddings' already exists.")
  

    # Create a full-text index
    def create_fulltext_index(self):
        query = """
        CREATE FULLTEXT INDEX ifcFulltext FOR (n:Entity) ON EACH [n.name, n.description, n.type, n.GlobalId]
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
                check=True  # Raises an exception if the command fails
            )
            print(f"Model {model_name} pulled successfully:\n{result.stdout}")
        except :
            print(f"Failed to pull model {model_name}")
            
       
        with self.driver.session() as session:
            #ollama.pull(model_name)
            embedder = OllamaEmbeddings(model=model_name)
            retriever = HybridRetriever(
                self.driver,
                vector_index_name="ifcModelEmbeddings",
                fulltext_index_name="ifcFulltext",
                embedder=embedder,
                return_properties=["name", "type", "properties", "globalid"],
            )
            query_text = self.user_input
            retriever_result = retriever.search(query_text=query_text, top_k=3)

            return retriever_result

    def close(self):
        self.driver.close()

if __name__ == "__main__":
    rag = RunHybridRAG()
    rag.create_vector_index()
    rag.create_fulltext_index()
    rag.user_input = "How many slabs are there in the model?"
    result = rag.main()
    print(result)
    rag.close()