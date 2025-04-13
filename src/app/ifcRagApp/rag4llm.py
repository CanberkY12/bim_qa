import os
import chromadb

chroma_path = "C:/Users/berky/oxide/data/chroma"
if os.path.exists(chroma_path):
    print(os.listdir(chroma_path))
else:
    print("Directory doesn't exist!")

class RunLocalRAG:
    """
    Obviously, the final .py file in ifcRagApp.
    Receives the user input -> generates the embedding for the query text
    -> queries the ChromaDB collection -> retrieves the documents -> generates the response using LLM.

    The final LLM response is making the result better, but takes longer time (around avg. 13 seconds).
    It can be cancelled.
    
    """

    def runChromaRAG(self, query_text):
        # This is the path to the ChromaDB directory where the database is stored.
        # Obviously everything is local, hence the vector store.
        persist_directory = "C:/Users/berky/oxide/data/chroma"
        
        #print("Initializing ChromaDB client...")
        client = chromadb.PersistentClient(path=persist_directory)
        
        # Check the available collection/s
        collections = client.list_collections()
        #print(f"Available collections ({len(collections)}):")
        for coll in collections:
            print(f"- {coll.name}")


        # Decided to use direct ChromaDB querying instead of langchain for faster retrieval
        # My pc's bottleneck issues limits the applicaiton a little bit
        collection_name = "ifc_narratives"
        try:
            collection = client.get_collection(collection_name)
            #print(f"Collection found: {collection_name} with {collection.count()} documents")
            
  
            import time
            start = time.time()
            

            import httpx
            

            print("Generating embedding for query...")
            try:

                response = httpx.post(
                    "http://localhost:11434/api/embeddings",
                    json={"model": "nomic-embed-text:latest", "prompt": query_text},
                    timeout=10.0
                )
                query_embedding = response.json().get("embedding", [])
                print(f"Embedding generated in {time.time() - start:.2f} seconds")
            except Exception as e:
                print(f"Error generating query embedding: {e}")
                return {"error": f"Failed to generate embedding: {str(e)}"}
            
            # Adding the time counter in order to measeure the performance of the RAG ret.
            print("Querying collection...")
            query_start = time.time()
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=1,
                include=["documents", "metadatas", "distances"]
            )
            print(f"Query completed in {time.time() - query_start:.2f} seconds")
            
            # Check if we got results
            if not results["documents"] or not results["documents"][0]:
                return {
                    "query": query_text,
                    "response": "No relevant documents found in the database.",
                    "retrieved_docs": []
                }
            
            retrieved_docs = results["documents"][0]
            distances = results["distances"][0] if "distances" in results else []
            
            #print(f"Retrieved {len(retrieved_docs)} documents")
            for i, (doc, dist) in enumerate(zip(retrieved_docs, distances)):
                print(f"Doc {i+1}: Distance {dist:.4f}, Preview: {doc[:50]}...")
                if i == 0:
                    print(f"\nComplete text of first document:\n{doc}\n")
            
        except Exception as e:
            print(f"Error during collection query: {e}")
            return {"error": str(e)}
        
        print("Creating LLM and generating response...")
        
        context = "\n\n".join([doc[:300] for doc in retrieved_docs]) 

        prompt = f"""
        Based on the following context, write the summary distinctly about the Ifc types, their attributes and connectedness that will be used for cypher query generation.
        Do not write the cypher query itself.
        
        Context:
        {context}
        
        Query: {query_text}
        
        Answer:"""
        
        # This is the final LLM part.
        # Receives the rag retrivals and summarizes them in a way that can be used for cypher query generation.
        # As mentioned before, not necessary.
        # An alternative is also using ollama.pull() method to call the model.
        try:
            llm_start = time.time()
            response = httpx.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3.2", "prompt": prompt, "stream": False},
                timeout=30.0
            )
            result = response.json().get("response", "No response generated")
            print(f"LLM response generated in {time.time() - llm_start:.2f} seconds")
        except Exception as e:
            print(f"Error generating response: {e}")
            result = f"Error generating response: {str(e)}"
        

        print(f"LLM Response: {result}")
        
        return {
            "query": query_text,
            "response": result,
            "retrieved_docs": [doc[:100] + "..." for doc in retrieved_docs]
        }

#if __name__ == "__main__":
#    run = RunLocalRAG()
#    run.runChromaRAG("Which wall the windows are in?")