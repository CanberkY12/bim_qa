import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))  # Add parent directory to path

import json

# Local imports
import few_shot_examples
from ifcRagApp import rag4llm

# Package imports
import ollama
import ifcopenshell
import sys

import anthropic
from openai import OpenAI # Import the OpenAI package
from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
from langchain_community.graphs import Neo4jGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
#print("GROQ API key received...")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
#print("OpenAI API key received...")

#Reciveing user input from the web page and returning a response ( page.tsx -> promptreceiver.js -> runPython.js -> lchain2cypher.py )
#user_input = sys.argv[1]  # Read the argument passed by the Node.js script
user_input = "How many windows are there in the building?"

result = {"status": "success", "input_received": user_input}
# Output result as JSON or Simply print the user input 
try:
    print(user_input)
except Exception as e:
    print("No data received in cypher generator: ", e)

class RunCypher:
    def __init__(self, user_input):
        self.url="neo4j+s://be20d4fc.databases.neo4j.io"#os.getenv("url")
        self.username="neo4j"#os.getenv("username")
        self.password="sz7lL8-kJT9q5e7jN-j6VGoaEJ4XEXNRgHgJJugMp0U"#os.getenv("password")
        self.driver = self.connect()
        self.graph = Neo4jGraph(url=self.url,username=self.username,password=self.password)
        self.user_input = user_input
        self.fine_tuning_data = []

    def connect(self):
        driver = GraphDatabase.driver(self.url, auth=(self.username, self.password))
        print("Connected to the Neo4j graph.")
        return driver


    def few_shot_setter(self):

        # Create a PromptTemplate for formatting the examples
        example_template = PromptTemplate(
            input_variables=["question", "schema"],  # Define the input variables for the template
            template="User: {question}\nAI: {cypher_query}"  # Template structure for each example
        )

        #print("Few shot examples: ", few_shot_examples)
        prompt = FewShotPromptTemplate(
            examples=few_shot_examples.examples[:],
            example_prompt=example_template,
            prefix="Here are some examples of questions and answers:",
            suffix="User input: {question}\nAI: ",
            input_variables=["question", "schema"],
        )

        return prompt
    
    def openai_llm(self):
        model = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=None, timeout=None, max_retries=1)
        print("OpenAI model created...")
        return model
    
    def unthropic_llm(self, user_input, task_description):

        claude_key = os.environ.get("anthropic_api_key")
        client = anthropic.Anthropic(
        api_key = claude_key,
        )
        print("Anthropic model created...")
        Prompt = user_input

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system = task_description,
            temperature=0.0,
            messages=[
                {"role": "user", "content": Prompt}
            ]
        )
        result = message.content[0].text
        return result

    def local_llm(self):
        ollama.pull("hf.co/berky12/Qwen2.5-Coder-7B-Instruct-ifc2cypher:latest")
        print("Ollama model created...")
        #ollama.pull("llama3.2")
        llm = OllamaLLM(
            model="hf.co/berky12/Qwen2.5-Coder-7B-Instruct-ifc2cypher:latest",
            temperature=0.0,
            max_tokens=None,
            timeout=30,  # Add timeout
            max_retries=3,
            cuda=True,  # Enable CUDA
            model_kwargs={
                "gpu_layers": 32,  # Use GPU for more layers
                "cache_capacity": "2gb",  # Add cache
                "num_gpu": 1,
                "num_thread": 4
            }
        )
        return llm

    def ragCaller(self):
        rag = rag4llm.RunLocalRAG()
        result = rag.runChromaRAG(user_input)
        print("RAG result: ", result)
        return result

    def cypherQuery(self):

        self.graph.refresh_schema()
        schema = self.graph.schema
        ragResult = self.ragCaller()
        #print("Schema: ", schema)

        task_description = """Task: Based on the IFC/BIM graph rag result and Ifc schema provided,
            graph rag result: {ragResult} and the schema: {schema},
            generate a Cypher query to answer the user's question.
            Your query labels and relationships can only taken from the nodes and relationships received by the graph rag result and schema.
            Use the schema information only to complete the missing parts of the graph rag result.

            Instructions:
            - Only use node types and relationship types that appear in the provided schema.
            - Only use nodes and attributes explicitly listed in the schema.
            - Do not use the relationships, you can leave the relationships empty.
            - When returning the query results, return the global id of the queried node/s. Such as, w.GlobalId.
            - The query should be efficient and make use of nodes that start with 'Ifc...' and connected with 'IfcRel...'.
            - Return ONLY the Cypher query. No extra comments or explanation.
            - Do not use backticks around the query.
            """

        llm = self.local_llm()
        openai_llm = self.openai_llm()
        #anthropic_llm = self.unthropic_llm(user_input, task_description)

        #print("llm created")

        #chunks = self.chunker()
        prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template(
                        "You are an assistant specialized in generating Cypher queries based on IFC model knowledge graph derived schema and schema summary result you receive."
                    ),
                    HumanMessagePromptTemplate.from_template(
                        "Given the following IFC model knowledge graph related schema:\n\n{schema}\n\n and the user question related summary of the schema:\n\n{ragResult}\n\n,"
                        "Generate a Cypher query to answer the user's question based on the provided schema and the ragResults."
                        "Only use the node types and attributes that appear in the schema and the ragResult."
                        "In order to create the structure of the cypher query only write the node names and don't use any relationship names. Such as, (a)-[]->(b)."
                        "When you do not know the specific names of the nodes, you can use generic nodes."
                        "When returning the query results, return the global id of the queried node/s. Such as, w.GlobalId."
                        "Always produce only one Cypher query. "
                        "Do not include any explanations or apologies in your response.\n\n"
                        "User question: {question}"
                    ),
                ]
            )
        
#Here is the schema of the ifc model's knowledge graph graph: {schema}\n\n based on the nodes and relationships in the ifc model's knowledge graph
#                        "For returning the values, such as global id, height, width, directly use .-notation. Corresponsingly, w.GlobalId, w.OverallHeight, w.OverallWidth. "
        

        
        cypher_chain = (
            RunnablePassthrough.assign(
                schema=lambda _: self.graph.schema,
                ragResult=lambda _: ragResult,
            )
            | prompt
            | llm  #.bind(stop=["\nCypherResult:"])
            | StrOutputParser()
        )
 
        response = cypher_chain.invoke(
            {
                "question": user_input,
                "ragResult": ragResult,
                "schema": schema,
            }
        )
        
        if "`" in response:
            response = response.replace("`", "")
            if "MATCH" in response:
                response = response.split("MATCH", 1)[1]
                response = "MATCH" + response


        print("Cypher query: ", response)
        return response


    def validate_cypher_query(self, query):
            explain_query = f"EXPLAIN {query}"
            with self.driver.session() as session:
                result = session.run(explain_query)
                print("Validation result: ", result.data())

    def invalidCyHandler(self, query, error):
        llm = self.local_llm()
        schema = self.graph.schema
        prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template(
                        "You are an assistant specialized in correcting Cypher queries based on IFC model knowledge graph derived schema and the incorrect cypher query you receive."
                    ),
                    HumanMessagePromptTemplate.from_template(
                        "Given the following IFC model knowledge graph related node name:\n\n{schema}\n\n and the incorrect Cypher query:\n\n{query}\n\n and the error message:\n\n{error}\n\n"
                        "Generate a Cypher query to answer the user's question based on the provided schema."
                        "Only use the node types and relationship types that appear in the schema."
                        "When returning the query results, return the global id of the queried node/s. Such as, w.GlobalId."
                        "Always produce only one Cypher query. "
                        "Always make sure the generated Cypher query is different than the provided Cypher query."
                        "Do not include any explanations or apologies in your response.\n\n"
                        "User question: {question}"
                    ),
                ]
            )


        cypher_chain = (
            RunnablePassthrough.assign(
                schema=lambda _: self.graph.schema,
                query=lambda _: query,
                error=lambda _: error
            )
            | prompt
            | llm  #.bind(stop=["\nCypherResult:"])
            | StrOutputParser()
        )

        response = cypher_chain.invoke(
            {
                "question": user_input,
                "schema": schema,
                "query": query
            }
        )
        
        if "`" in response:
            response = response.replace("`", "")
            if "MATCH" in response:
                response = response.split("MATCH", 1)[1]
                response = "MATCH" + response


        print("Corrected Cypher query: ", response)
        return response
    
    def recurse(self, method):
        for i in range(3):
            try:
                return method()
            except Exception as e:
                print("Error in running the method:", e)
                continue


    def store_user_input(self, user_input, generated_query):
        data = {
            "input": user_input,
            "output": generated_query
        }
        self.fine_tuning_data.append(data)

    def save_fine_tuning_data(self, file_path="C:/Users/berky/workspace/projects/fine_tuning_data.jsonl"):
        with open(file_path, "w") as f:
            for entry in self.fine_tuning_data:
                f.write(json.dumps(entry) + "\n")



    def main(self):
        
        print("User input: ", self.user_input)
        #self.driver.verify_connectivity()
        session = self.driver.session()
        query = self.cypherQuery()
        result = session.run(query)
        print("Cypher query result: ", result.data())
        session.close()
        self.driver.close()
        return result.data()



if user_input:
    cypher = RunCypher(user_input)
    # Either use main() which does everything including cypherQuery()
    result = cypher.main()  
    print("Final result:", result)
