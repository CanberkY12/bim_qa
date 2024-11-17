import sys
import os
import getpass
import ast
import json
import numpy as np
import pandas as pd


import os
import pandas as pd
from typing import Set, Any, Union, Dict, List, Tuple, Hashable
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from neo4j import GraphDatabase
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

import torch


#print(transformers.__version__)

#import numpy as np
#from flask import Flask, request

#Reciveing user input from the web page and returning a response ( page.tsx -> promptreceiver.js -> runPython.js -> lchain2cypher.py )
user_input = sys.argv[1]  # Read the argument passed by the Node.js script
# Process data (add your logic here)
result = {"status": "success", "input_received": user_input}
# Output result as JSON
try:
    #print(json.dumps(result))
    print(user_input)
except Exception as e:
    print("No data received")


# Initialize language model (e.g., LLaMA 3.2) for text generation and embeddings
#llm_pipeline = pipeline("text-generation", model="LLaMA-3.2")  # Specify correct model here
#llm = HuggingFacePipeline(pipeline=llm_pipeline)

# Connect to the neo4j graph

username="neo4j"
password="sz7lL8-kJT9q5e7jN-j6VGoaEJ4XEXNRgHgJJugMp0U"
url="neo4j+s://be20d4fc.databases.neo4j.io"

# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"

graph = Neo4jGraph(url=url,username=username,password=password,sanitize=True)
driver = GraphDatabase.driver(url, auth=(username, password))
print(graph.schema)

os.environ["GROQ_API_KEY"] = "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"
print("API key received")
llm = ChatGroq(
    model="llama-3.2-3b-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

cypher_template = """Based on the Neo4j graph schema below,
write a Cypher query that would answer the user's question.
Return only Cypher statement, no backticks, nothing else.
{schema}

Question: {question}
Cypher query:"""  # noqa: E501



print("llm created")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Given an input question, convert it to a Cypher query. No pre-amble.",
        ),
        ("human", cypher_template),
    ]
)

#chain = prompt | llm
cypher_chain = (
    RunnablePassthrough.assign(
        schema=lambda _: graph.get_schema,
    )
    | prompt
    | llm.bind(stop=["\nCypherResult:"])
    | StrOutputParser()
)

response = cypher_chain.invoke(
    {
        "question": user_input
    }
)
print(response)

# Example Cypher query to send to Neo4j
cypher_query = response

# Function to run a Cypher query on Neo4j and return results
try:
    driver.verify_connectivity()
    driver.get_server_info()
    neo4j_connection = driver
    session = driver.session()
    session.run(cypher_query)
    result = session.run(cypher_query)
    print("db query result: ", result.data())

    #session.run("MATCH (p:Person {name: 'Alice'}) WITH p LIMIT 5 DELETE p")
finally:
    session.close()






"""
os.environ["OPENAI_API_KEY"] = "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"


llm_openai = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
# Generate Cypher statement based on natural language input
cypher_template = """"""Based on the Neo4j graph schema below,
write a Cypher query that would answer the user's question.
Return only Cypher statement, no backticks, nothing else.
{schema}

Question: {question}
Cypher query:""""""  # noqa: E501


cypher_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Given an input question, convert it to a Cypher query. No pre-amble.",
        ),
        ("human", cypher_template),
    ]
)

cypher_chain = (
    RunnablePassthrough.assign(
        schema=lambda _: graph.get_schema,
    )
    | cypher_prompt
    | llm_openai.bind(stop=["\nCypherResult:"])
    | StrOutputParser()
)

response = cypher_chain.invoke(
    {
        "question": "How many nodes are there in the dataset?"
    }
)
print(response)

#graph_store = Neo4jGraphStore(
#    username=username,
#    password=password,
#    url=url,
#)
#print(graph_store.schema)

#driver = GraphDatabase.driver(url, auth=(username, password))
#model_openai = ChatOpenAI(model_name="gpt-3.5-turbo", api_key="sk-3j0SIWqlte7Uj8UgebyPWGdyb3FYfy33XWIjn4EK0WaSWaMnHlQg")

#chain = GraphCypherQAChain.from_llm(graph=graph, 
#                                    llm=model_openai, 
#                                    verbose=True)


#prompt = "Write any cypher query?"
#try:
    #result = chain.invoke(prompt)['result']
#except:
#    pass 


#print(result)

""""""

#llama_3_cypher.Llama3Cypher(graph=graph, prompt="How many windows in the building?")
#----------------------------------------------------------
#   OPENAI API KEY
#----------------------------------------------------
""""""
# Load a text embedding model for vector search
embedding_model = pipeline("feature-extraction", model="sentence-transformers/all-mpnet-base-v2")

# Example documents with embeddings
documents = ["Document about employee policies.", "Document detailing management hierarchy.", "General HR guidelines."]
document_embeddings = []

# Precompute embeddings for documents
for doc in documents:
    embedding = np.array(embedding_model(doc)).mean(axis=1)  # Convert to single embedding vector
    document_embeddings.append(embedding)
document_embeddings = np.array(document_embeddings)  # Convert list to array for matrix operations

# Define prompt template for generating Cypher queries
prompt_template = """
"""
Convert the following natural language query to a Cypher query:

Natural language query: "{question}"

Cypher query:
"""
"""

template = PromptTemplate(input_variables=["question"], template=prompt_template)
#llm_chain = LLMChain(llm=llm, prompt=template)

def generate_cypher_query(question):
    """"""Generate Cypher query from a natural language question.""""""
    response = llm_chain.run(question)
    cypher_query = response.strip()
    return cypher_query

def query_neo4j(cypher_query):
    """"""Run a Cypher query on Neo4j and return results.""""""
    with driver.session() as session:
        result = session.run(cypher_query)
        return [record.data() for record in result]

def vector_search(question, top_k=3):
    """"""Perform vector search to find relevant documents for the question.""""""
    question_embedding = np.array(embedding_model(question)).mean(axis=1)  # Single vector for question
    question_embedding = np.expand_dims(question_embedding, axis=0)  # Reshape for FAISS
    distances, indices = pd.search(question_embedding, top_k)
    
    # Retrieve top-k documents based on indices
    relevant_docs = [(documents[idx], distances[0][i]) for i, idx in enumerate(indices[0])]
    return relevant_docs

def answer_question_hybrid(question):
    """"""Hybrid approach combining Cypher and vector search results.""""""
    # Step 1: Generate and execute Cypher query
    cypher_query = generate_cypher_query(question)
    print(f"Generated Cypher Query: {cypher_query}")
    structured_results = query_neo4j(cypher_query)
    
    # Step 2: Perform vector-based similarity search for unstructured data
    unstructured_results = vector_search(question)
    
    # Combine structured and unstructured results
    combined_results = {
        "structured_data": structured_results,
        "unstructured_data": unstructured_results
    }
    return combined_results

# Example usage
question = "How many windows in the building?"
results = answer_question_hybrid(question)

print("Structured Data (Graph Results):")
for result in results["structured_data"]:
    print(result)

print("\nUnstructured Data (Document Search Results):")
for doc, distance in results["unstructured_data"]:
    print(f"Document: {doc}, Similarity Score: {distance}")


    """