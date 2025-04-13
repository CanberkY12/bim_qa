# IFC/BIM Query Web API

This repository contains a small RESTFULL web api that is allowing users to upload their Ifc based BIM and query information using the llm chatbox.

This project is a voluntary based study poject and it is not for any commercial purposes. The only motivation is to develop skills in BIM software development and IFC/BIM information management.

# Overview

In this project, the feasability of improving a small and local Large Language Model's (LLM) Knowledge Graph (KG) querying accuracy up to benchmark llm's is investigated by utilizing Industry Foundation Classes (IFC) standards and buildingSmart Data Dictionary (bSDD) definitions. The challange is addressed by combining RAG retrieval with fine tuned llm. Several common problems such as hallucination, incorrect cypher query structure generation and partially correct node names are targeted by the mentioned fine tuning and RAG applications.

# Contents

data/: Contains the ifcnarrative text files and the vector store that is contained in Chroma db.

pages\api/: Created for a JavaScript based GET/POST logic implemented several files that simply send the Ifc file and the user input to the backend and to the databases.

src/app/: The implementation is located here. Refer to the User Interface (UI) side of the application which contains the React based web page dev (page.tsx) and the backend part which is written with Python. The backend parts can be specifically found under ifcRagApp and llm4Cypher folders.

# Installation and Setup

The installation requires several open source repos, node.js and python packages to work together which is both hard to setup cleanly and also requires a lot of space. Therefore the docker container is much easier to run if the purpose is to just test the api.

### Acknowledgements:
  This project makes use of the following open-source libraries and tools:

### 1. UI Components
- **[ThatOpen/engine_ui-components](https://github.com/ThatOpen/engine_ui-components)**
  - License: MIT
  - Description: Provides reusable and modern UI components.

### 2. IFC to LPG Conversion
- **[marwiss/IFC-graph](https://github.com/marwiss/IFC-graph)**
  - License: GNU General Public License v3.0 (GPL-3.0)
  - Description: Converts Industry Foundation Classes (IFC) to Linked Property Graphs (LPG).
  - This code is not modified or distributed. Only used from app by calling with childprocess.spawn, therefore this repository is nout bound to be licensed under GPL-3.0.

### 3. Alternative Parser
- **[seb-esser/ConMan](https://github.com/seb-esser/ConMan)**
  - License: MIT
  - Description: A modular IFC-to-LPG converter with alternative logic.

Each project retains its respective license and intellectual property rights. See their individual repositories for more details.

## Packages:
  1- packages.txt file has the Anaconda env packages
  2- pnpm-lock.yaml is the lock file for pnpm package manager
  3- package.json for dependencies and scripts


Additionally, the fundamental part is the locally run llm. The project uses Ollama models and the specifically fine tuned model is: berky12/Qwen2.5-Coder-7B-Instruct-ifc2cypher and berky12/Phi-3-medium-4k-instruct-text2cypher which should be converted to gguf,  It can be found in this **[link](https://huggingface.co/berky12)**.

The Phi-3-medium-4k-instruct-text2cypher model is suggested for space, speed and for it is fine tuned with better quality.

# Usage

The model should run on installed Ollama software, the ollama is installed from: **[ollama website](https://ollama.com/)** and the model can be downloaded by using the terminal/command prompt: "ollama run berky12/Phi-3-medium-4k-instruct-text2cypher"

Neo4j aura cloud database can be created for free and the instance credentials should be written to .env file.

As for the IFC to kg parser, forking and compiling the requirements.txt (pip install -r path/to/conman/requirements.txt) of **[seb-esser/ConMan](https://github.com/seb-esser/ConMan)** is the better choice. The IFC-graph by "marwiss" is included and tested in the project because the code's logic is explained very well.

Using not-local LLM: simply save the API key to the .env file that is created, and change the "local_llm" in src/llm4Cypher/lchain2cypher.py to the selected model's method. In the script there are small calling methods for OpenAI, Groq and Anthropic.

After cloning and compiling, navigating to /src directory and running "pnpm run dev" in the terminal initiates the Web API in the localhost:3000

# License

MIT License

# Related Literature

1. Zhu, J., Wu, P., & Lei, X. (2023). IFC-graph for facilitating building information access and query. Automation in Construction, 148, 104778. https://doi.org/10.1016/j.autcon.2023.104778
