import os
import dotenv
import getpass

import ollama
import ifcopenshell
from neo4j import GraphDatabase
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import SKLearnVectorStore
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter

import ifcChunker

class RunLocalRAG:
    def __init__(self):
        self.url=dotenv.get_key(".env" ,"url")
        self.username=dotenv.get_key(".env" ,"username")
        self.password=dotenv.get_key(".env" ,"password")
        self.user_input = None
        self.driver = self.connect()
        self.graph = Neo4jGraph(url=self.url,username=self.username,password=self.password,sanitize=True)


    def connect(self):
        driver = GraphDatabase.driver(self.url, auth=(self.username, self.password))
        print("Connected to the Neo4j graph.")
        return driver
    
    def create_vector_store(self):
        # This file is going to be received from the frontend as a file upload. For now, it is hardcoded.
        # However, the ifcChunker also needs to receive nodes from kg of neo4j and iterate over them to create the chunks.
        ifc_file = ifcopenshell.open("C:/Users/berky/Downloads/small (1).ifc")
        ifc_element = ifcChunker.IfcElement(ifc_file)

        chunks = ifc_element.splitter()

        #persist_directory = "C:/Users/berky/oxide/src/app/llmGraphQL/vector_store"  # Directory to save the vector store

        ollama.pull("nomic-embed-text")

        vectorstore = SKLearnVectorStore.from_documents(
            documents=chunks,
            embedding=OllamaEmbeddings(model="nomic-embed-text"),
        )

        retriever = vectorstore.as_retriever(k = 3)
        print("Vector store and retriever are created and saved.")
        return retriever
    
    def create_rag(self):
        #graph = Neo4jGraph(url=self.url,username=self.username,password=self.password,sanitize=True)
        schema = self.graph.schema
        retriever = self.create_vector_store()
        llm = ChatOllama(
            model="llama3-8b-8192",
            temperature=0.0,
            max_tokens=500,
            timeout=None,
            max_retries=3,
            retriever=retriever,
        )
        print("RAG is created.")
        return llm
    
    def query_receiver(self):
        user_input = input("How many IfcWindow are in the building?")
        return user_input
    
    def run_rag(self):
        llm = self.create_rag()

        instructions = """You are a Neo4j expert. 

        The vectorstore contains nodes and relationships that are generated from a BIM/IFC model.

        Use the vectorstore to answer the user's questions and always include GlobalId of the returned item/s in your answer.

        Here is the schema information 
        {schema}.

        """


        prompt = llm.invoke(
            [SystemMessage(content = instructions)]
            + [
                HumanMessage(
                    content= self.query_receiver(),
                )
            ]
        )

        print(prompt)
        print("RAG is closed.")


if __name__ == "__main__":
    run = RunLocalRAG()
    run.run_rag()

    
    

    
