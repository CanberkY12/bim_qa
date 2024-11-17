from langchain_community.graphs import Neo4jGraph

from langchain_openai import ChatOpenAI
from langchain.chains.graph_qa.cypher import GraphCypherQAChain

#from unsloth import FastLanguageModel
#from transformers import AutoTokenizer
#import transformers


class Llama3Cypher:
    def __init__(self, graph, prompt):
        self.graph
        self.prompt

    def run(self):

        model_openai = ChatOpenAI(model_name="gpt-3.5-turbo", api_key="sk-3j0SIWqlte7Uj8UgebyPWGdyb3FYfy33XWIjn4EK0WaSWaMnHlQg")

        #model = ChatGroq(temperature = 0.3, 
        #                 model_name="llama3-8b-8192", 
        #                 groq_api_key = "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"
        #                 )
        chain = GraphCypherQAChain.from_llm(graph=self.graph, 
                                            llm=model_openai, 
                                            verbose=True)

        try:
            result = chain.invoke(self.prompt)['result']
        except:
            pass
        return result


