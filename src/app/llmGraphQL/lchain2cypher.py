import sys
import os
import getpass
import ast
import json
import numpy as np
import pandas as pd

# Local imports
from hybrid_rag import RunHybridRAG

# Package imports
from typing import Set, Any, Union, Dict, List, Tuple, Hashable
from langchain_community.graphs import Neo4jGraph
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from neo4j import GraphDatabase
import seaborn as sns
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
# Output result as JSON or Simply print the user input 
try:
    #print(json.dumps(result))
    print(user_input)
except Exception as e:
    print("No data received")


# Initialize language model (e.g., LLaMA 3.2) for text generation and embeddings
# llm_pipeline = pipeline("text-generation", model="LLaMA-3.2")  # Specify correct model here
# llm = HuggingFacePipeline(pipeline=llm_pipeline)

# Connect to the neo4j graph

username=os.getenv("username")
password=os.getenv("password")
url=os.getenv("url")

# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"

graph = Neo4jGraph(url=url,username=username,password=password,sanitize=True)
driver = GraphDatabase.driver(url, auth=(username, password))
#print(graph.schema)

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
print("API key received")

llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0.0,
    max_tokens=100,
    timeout=None,
    max_retries=3,
    # other params...
)

cypher_template = """Based on the Neo4j graph schema below,
write a Cypher query that would answer the user's question.
User's questions are only relating to the BIM/IFC model that is uploaded to the Neo4j graph
as a knowledge graph.
Return only Cypher statement, no backticks, nothing else.
{schema}

Question: {question}
Cypher query:"""  # noqa: E501



print("llm created")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Given an input question, convert it to a Cypher query. No pre-amble and only return the cypher query.",
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
        #"What are the names of all the walls in the model?",
        
    }
)
print(response)

# Cypher query to send to Neo4j
cypher_query = response
#hybrid_result = RunHybridRAG(generated_cypher=cypher_query)

# Function to run a Cypher query on Neo4j and return results
try:
    driver.verify_connectivity()
    driver.get_server_info()
    neo4j_connection = driver
    session = driver.session()
    rag = RunHybridRAG()
    rag.create_vector_index()
    rag.create_fulltext_index()
    rag.user_input = cypher_query
    resultRag = rag.main()
    print("RAG result", resultRag)
    rag.close()
    session.run(cypher_query)
    result = session.run(cypher_query)
    print("db query result: ", result.data())

    #session.run("MATCH (p:Person {name: 'Alice'}) WITH p LIMIT 5 DELETE p")
finally:
    session.close()




