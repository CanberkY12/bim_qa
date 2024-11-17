from neo4j import GraphDatabase
from dotenv import load_dotenv
import json
import os
from typing import Tuple
from llama_index.graph_stores.neo4j import Neo4jPGStore

# Part 3 - Python Driver
def execute_query(
  uri: str,
  username: str,
  password: str,
  query: str, 
  params: dict):
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
      records, summary, keys = driver.execute_query(query, params)
      driver.close()
      return summary


# Part 2 - Conversion
def convert_nodes(
    nodes: dict
  ) -> Tuple[str, dict]:

    query = ""

    for node_label, _ in nodes.items():
        query += f"""CALL apoc.create.nodes(["{node_label}"], ${node_label});"""
    return query, nodes


def convert_relationships(
    relationships: dict
    ) -> Tuple[str, dict]:
        
        rel_record_list = []
        params = {}

        for rel_type, rel_records in relationships.items():
            for record in rel_records:
                
                # Get the relationships _uid to distinguish it from other params
                record_key = record.get('_uid')
                params[record_key] = record

                # Get the source and target node _uids
                from_node_uid = record.get('_from__uid')
                to_node_uid = record.get('_to__uid')

                # Create a list of values and parameter keys which will be used to construct the relationship
                item = f"['{rel_type}', '{from_node_uid}', '{to_node_uid}', ${record_key}]"
                rel_record_list.append(item)

        # Combine all the lists into a master list
        composite_rel_records_list = ",".join(rel_record_list)

        # Create a single query to process all the Relationship records
        query = f"""WITH [{composite_rel_records_list}] AS rel_data
                    UNWIND rel_data AS relationship
                    MATCH (n {{`_uid`:relationship[1]}})
                    MATCH (n2 {{`_uid`:relationship[2]}})
                    CALL apoc.create.relationship(n, relationship[0], relationship[3], n2) YIELD rel
                    RETURN rel
        """

        return query, params   


# Part 1 - Upload
def upload(
  uri: str,
  username: str,
  password: str,
  data: str
  ):

    if isinstance(data, str) is True:
        try:
            data = json.loads(data)
        except Exception as e:
            raise Exception(f'Error converting data to json: {e}')

    # Convert the nodes and relationships into cypher queries and params
    query, params = convert_nodes(data['nodes'])
    rel_query, rel_params = convert_relationships(data['relationships'])

    # Aggregate them into a single query and params dictionary
    query += rel_query
    params.update(rel_params)

    # Upload
    execute_query(uri, username, password, query, params)
    
    


username=os.getenv("username")
password=os.getenv("password")
url=os.getenv("url")

graph_store = Neo4jPGStore(
    username=username,
    password=password,
    url=url,
)

import os

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
JSONpath = "C:/Users/berky/Downloads/properties.json"

# Load the JSON data from the file
with open(JSONpath, 'r') as file:
    json_data = file.read()

# Upload the JSON data to the Neo4j database
upload(url, username, password, json_data)
