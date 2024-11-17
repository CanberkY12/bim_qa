import os

from neo4j import GraphDatabase
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j_graphrag.retrievers import HybridRetriever



class RunHybridRAG:
    def __init__(self):
        self.url="neo4j+s://be20d4fc.databases.neo4j.io"
        self.username="neo4j"
        self.password="sz7lL8-kJT9q5e7jN-j6VGoaEJ4XEXNRgHgJJugMp0U"
        self.user_input = None
        self.driver = self.connect()

    def connect(self):
        os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
        driver = GraphDatabase.driver(self.url, auth=(self.username, self.password))
        return driver
    
    # Create a full-text index
    def create_fulltext_index(self):
        query = """
        CREATE FULLTEXT INDEX ifcFulltext FOR (n:Entity) ON EACH [n.name, n.description, n.type, n.GlobalId]
        """
        with self.driver.session() as session:
            session.run(query)
            print("Full-text index 'ifcFulltext' created successfully.")
    
    def main(self):
        # Vector index search 
        with self.driver.session() as session:

            embedder = OpenAIEmbeddings(model="llama-3.2-3b-preview")
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

    