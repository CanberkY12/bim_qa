# IFC/BIM Query Web API

This repository contains a small RESTFULL web api that is allowing users to upload their Ifc based BIM and query information using the llm chatbox.

This project is a voluntary based study poject and it is not for any commercial purposes. The only motivation is to develop skills in AEC industry focused fullstack software development and Ifc/BIM information management.

# Overview

In this project, a case study of improving a small and local Large Language Model's (LLM) Knowledge Graph (KG) querying accuracy up to benchmark llm's is investigated by utilizing Industry Foundation Classes (IFC) standards and buildingSmart Data Dictionary (bSDD) definitions. The challange is addressed by combining RAG retrieval with fine tuned llm. Several common problems such as hallucination, incorrect cypher query structure generation and partially correct node names are targeted by the mentioned fine tuning and RAG applications.

# Contents

data/: Contains the ifcnarrative text files and the vector store that is contained in Chroma db.

pages\api/: Created for a JavaScript based GET/POST logic implemented several files that simply send the Ifc file and the user input to the backend and to the databases.

src/app/: The implementation is located here. Refer to the User Interface (UI) side of the application which contains the React based web page dev (page.tsx) and the backend part which is written with Python. The backend parts can be specifically found under ifcRagApp and llmGraphQL folders.

# Installation and Setup

The installation requires several open source repos, node.js and python packages to work together which is both hard to setup cleanly and also requires a lot of space. Therefore the docker image is much easier to run if the purpose is to just test the api.

Additionally, the most fundamental part is the locally run llm. The project uses Ollama models and the specifically fine tuned model is:... It can be found in this link:...

Neo4j database credentials ...


# Usage
# License
# Related Literature
