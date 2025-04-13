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

#import anthropic
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

"""
 Reciveing user input from the web page and returning a response ( page.tsx -> promptreceiver.js -> runPython.js -> lchain2cypher.py )
 the user_input = sys.argv[1] line is original web api connection. However for testing purposes, it can be hashed and question can be hardcoded.
"""

user_input = sys.argv[1]  # Read the argument passed by the Node.js script
#user_input = "Any question here..."

result = {"status": "success", "input_received": user_input}
# Output result as JSON or Simply print the user input 
try:
    print(user_input)
except Exception as e:
    print("No data received in cypher generator: ", e)

class RunCypher:
    """
    lchain2cypher is the main class that is receiving the user input and generating the final cypher query.
    The fine tuned model is called in local_llm method.
    There are several methods that are calling other ai models such as OpenAI, Anthropic, Groq and Ollama.
    The implementation is certainly not convenient. There should be a much better file/folder allocation and class structure.
    However, the class and its methods are straitformward and self explanatory.
    
    """
    def __init__(self, user_input):
        self.url=os.getenv("url")
        self.username=os.getenv("username")
        self.password=os.getenv("password")
        self.driver = self.connect()
        self.graph = Neo4jGraph(url=self.url,username=self.username,password=self.password)
        self.user_input = user_input
        self.fine_tuning_data = []

    def connect(self):
        driver = GraphDatabase.driver(self.url, auth=(self.username, self.password))
        #print("Connected to the Neo4j graph.")
        return driver


    def few_shot_setter(self):
        """
        In case few shot examples wanted to be passed, this method can be tailored.
        But currently unused.
        """
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
        #print("OpenAI model created...")
        return model
    
    def unthropic_llm(self, user_input, task_description):
        import anthropic
        claude_key = os.environ.get("anthropic_api_key")
        client = anthropic.Anthropic(
        api_key = claude_key,
        )
        #print("Anthropic model created...")
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
    
    def groq_llm(self):
        from groq import Groq

        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        
        # No need to pass schema and rag_result explicitly since they'll be passed 
        # in the content through the RunnablePassthrough in cypherQuery method
        def generate_query(prompt):
            chat_completion = client.chat.completions.create(
            messages=[
                {
                "role": "system",
                "content": "You are an assistant specialized in generating Cypher queries for Neo4j based on IFC/BIM knowledge graphs. Only return the Cypher query without explanations."
                },
                {
                "role": "user",
                "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1
            )
            return chat_completion.choices[0].message.content
        
        # Return the function that will be called by RunnablePassthrough
        return generate_query


    def local_llm(self):
        """
        This generative model solely depends on the local hardware and it is crucial to make sure 
        the hardware is up to it. 
        model_kwargs better be understood and editted accordingly. 
        In the current setting NVidia GTX 3050Ti 4Gb gpu is used with cuda support. 4gb is a bit low for this model (a bottleneck) but runs just fine?.
        """
        ollama.pull("hf.co/berky12/Qwen2.5-Coder-7B-Instruct-ifc2cypher:latest")
        #print("Ollama model created...")
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
        """
        Just returns the rag results depending on the user input.
        """
        rag = rag4llm.RunLocalRAG()
        result = rag.runChromaRAG(user_input)
        #print("RAG result: ", result)
        return result

    def cypherQuery(self):
        """
            The so called collective method where pieces come together.
            main method calls this method and runs the produced cypher query in the neo4j session.
            The prompts are written here with name prompt. task_description is not the prompt.
        """
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
        #openai_llm = self.openai_llm()
        #anthropic_llm = self.unthropic_llm(user_input, task_description)
        #groq_llm = self.groq_llm()

        #print("llm created")

        #chunks = self.chunker()
        prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template(
                        "You are an assistant specialized in generating Cypher queries based on IFC model knowledge graph derived schema and schema-summary result you receive."
                    ),
                    HumanMessagePromptTemplate.from_template(
                        "Given the following IFC model knowledge graph related schema:\n\n{schema}\n\n and the user question related summary of the schema:\n\n{ragResult}\n\n,"
                        "Generate a Cypher query to answer the user's question based on the provided schema and the ragResults."
                        "Only use the node types and attributes that appear in the schema and the ragResult."
                        "In order to create the structure of the cypher query only write the node names and don't use any relationships."
                        "When you do not know the specific names of the nodes, you can use generic nodes."
                        "When returning the query results, return the global id of the queried node/s. Such as, w.GlobalId."
                        "Always produce only one Cypher query. "
                        "Do not include any explanations or apologies in your response.\n\n"
                        "User question: {question}"
                    ),
                ]
            )
        
        
        
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
        """
        This method is meant to correct the invalid cypher query, however it is not used due to very long generation time.
        """
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
