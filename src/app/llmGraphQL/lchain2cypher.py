import sys
import os
import requests

# Local imports
import few_shot_examples
from hybrid_rag import RunHybridRAG

# Package imports
import ollama
import torch
import subprocess
import threading
import time
import ifcopenshell
import ifcChunker
from neo4j import GraphDatabase
from langchain_ollama import OllamaLLM
from langchain_community.graphs import Neo4jGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from transformers import AutoModelForCausalLM, AutoTokenizer
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
print("GROQ API key received...")

#Reciveing user input from the web page and returning a response ( page.tsx -> promptreceiver.js -> runPython.js -> lchain2cypher.py )
user_input = sys.argv[1]  # Read the argument passed by the Node.js script
# Process data (add your logic here)
result = {"status": "success", "input_received": user_input}
# Output result as JSON or Simply print the user input 
try:
    print(user_input)
except Exception as e:
    print("No data received in cypher generator: ", e)

class RunCypher:
    def __init__(self, user_input):
        self.url=os.getenv("url")
        self.username=os.getenv("username")
        self.password=os.getenv("password")
        self.driver = self.connect()
        self.graph = Neo4jGraph(url=self.url,username=self.username,password=self.password,sanitize=True)
        self.user_input = user_input

    def connect(self):
        driver = GraphDatabase.driver(self.url, auth=(self.username, self.password))
        print("Connected to the Neo4j graph.")
        return driver
    
    def get_system_message(self):
        schema = self.graph.schema
        return f"""
        Task: Generate Cypher queries to query a Neo4j graph database based on the provided schema definition.
        Instructions:
        Use only the provided relationship types and properties.
        Do not use any other relationship types or properties that are not provided.
        If you cannot generate a Cypher statement based on the provided schema, explain the reason to the user.
        Schema:
        {schema}

    Note: Do not include any explanations or apologies in your responses.
    """

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
    
    def local_llm(self):
        ollama.pull("qwen2.5-coder:7b-instruct-q8_0")
        llm = OllamaLLM(
            model="qwen2.5-coder:7b-instruct-q8_0",
            temperature=0.3,
            max_tokens=None,
            timeout=None,
            max_retries=3,
        )
        return llm
    
    def chunker(self):
        ifc_file = ifcopenshell.open("C:/Users/berky/Downloads/small (1).ifc")
        ifc_element = ifcChunker.IfcElement(ifc_file)
        chunks = ifc_element.splitter()
        #print("Chunks received from the IFC file: ", chunks)
        return chunks
    
    def qwen(self):
        # Format the prompt
        prompt = f"""
        You are a helpful assistant specialized in generating Cypher queries for graph databases.
        Respond with only the Cypher query unless additional explanation is requested.
        Use the below provided ifc model schema to generate the Cypher query.
        schema: {self.graph.schema}

        User Query: {self.user_input}
        """

        # Call Ollama CLI
        result = subprocess.run(
            ["ollama", "run", "qwen2.5-coder:7b-instruct-q8_0"],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Check for errors
        if result.returncode != 0:
            raise Exception(f"Error from Ollama CLI: {result.stderr.decode()}")

        # Return the output
        return result
        """
        # Define Ollama server details
        OLLAMA_URL = "http://localhost:11434"  # Default Ollama server address
        MODEL_NAME = "qwen2.5-coder:7b-instruct-q8_0"

        model_name = "qwen2.5-coder:7b-instruct-q8_0"
        model = self.local_llm()

        tokenizer = AutoTokenizer.from_pretrained(model)

        prompt = "Generate a ifc knowledge graph related cypher query to answer user natural language questions.\n\nIn the response do not write any extra comments or explanation.\n\n While producing cypher query only use Ifc types of queried subjects.\n\nUser: What is the name of the wall with the longest length?\nAI: MATCH (w:IfcWall) RETURN w.name ORDER BY w.length DESC LIMIT 1"
        messages = [
            {"role": "system", "content": "You are neo4j knowledge graph related cypher query generator expert, created by Alibaba Cloud. Your task is to write cypher queries to answer user natural language questions."},
            {"role": "user", "content": "How many walls are in the model?"},
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        print("Response: ", response)
        return response"""



    def cypherQuery(self):

        self.graph.refresh_schema()
        schema = self.graph.schema

        #print("Schema: ", schema)

        task_description = """Task: Based on the IFC/BIM graph schema provided,
            write an accurate and efficient Cypher query to answer the user's question. 
            Your query labels and relationships can only taken from the nodes and relationships defined in the graph schema.

            Instructions:
            - Only use node types and relationship types that appear in the provided schema.
            - Only include properties and relationships explicitly listed in the schema.
            - The query should be efficient and make use of direct relationships.
            - Return ONLY the Cypher query. No extra comments or explanation.
            - Do not use backticks around the query.
            """

        llm = self.local_llm()
        print("llm created")

        chunks = self.chunker()
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    SystemMessagePromptTemplate.from_template(
                        "You are a Cypher query generation assistant. I will provide you with a description of a task and you need to generate the Cypher query based on the schema and ifc file's chunks provided."
                    )
                ),
                (
                    HumanMessagePromptTemplate.from_template(
                        "Here is the schema of the IFC/BIM graph: {schema}\n\n{task_description}\n\nGenerate the corresponding Cypher query based on the schema and chunks."
                    )
                ),
            ])
        
        def format_few_shot_prompt(schema, examples, user_input):
            few_shot_section = "\n".join(
                f"question: {example['question']}\ncypher query: {example['cypher query']}"
                for example in examples
            )
            user_section = f"question: {user_input}"
            formatted_prompt = f"""
            Schema:
            {schema}

            Examples:
            {few_shot_section}

            Now, based on the schema, generate the Cypher query for the following:
            {user_section}
            """
            print("Formatted Prompt:", formatted_prompt)  # Debugging to inspect the formatted prompt
            return formatted_prompt
        

        


        # Construct the prompt for the LLM
        #formatted_prompt = format_few_shot_prompt(schema, examples, user_input)

        # Generate the query using the LLM
        #response = llm(formatted_prompt)

        cypher_chain = (
            RunnablePassthrough.assign(
                schema=lambda _: self.graph.schema,
            )
            | prompt
            | llm  #.bind(stop=["\nCypherResult:"])
            | StrOutputParser()
        )
        """

        

        cypher_chain = (
            RunnablePassthrough.assign(
                schema=lambda _: self.graph.schema,
            )
            | RunnablePassthrough.assign(
                # Use a function to construct the prompt with examples
                prompt=lambda _: self.few_shot_setter()
            )
            | llm  # If needed, bind with stop condition
            | StrOutputParser()
        )
        """
        response = cypher_chain.invoke(
            {
                "question": user_input,
                "task_description": task_description,
            }
        )
        
        
        """
        response = cypher_chain.invoke(
            {
                "question": user_input, 
                "schema": self.graph.schema
            }
        )
        """
        if "`" in response:
            response = response.replace("`", "")
            if "MATCH" in response:
                response = response.split("MATCH", 1)[1]
                response = "MATCH" + response

        print("Cypher query: ", response)
        return response

    def main(self):
        try:
            self.driver.verify_connectivity()
            self.driver.get_server_info()
            session = self.driver.session()
            result = session.run(self.cypherQuery())
            print("Cypher query result: ", result.data())
            session.close()
            self.driver.close()
            return result.data()

        except Exception as e:
            print("Error in running the cypher query: ", e)

if user_input:
    cypher = RunCypher(user_input)
    #cypher.chunker()
    cypher.main()
    #cypher_query = cypher.qwen()
    #cypher.cypherQuery()
    #cypher.close