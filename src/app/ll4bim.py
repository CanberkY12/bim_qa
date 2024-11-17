from llama_index.graph_stores.neo4j import Neo4jPGStore
import nest_asyncio
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from typing import Literal
from llama_index.core.indices.property_graph import SchemaLLMPathExtractor
from llama_index.core import PropertyGraphIndex
from typing import Any, Optional
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import CustomPGRetriever
from llama_index.core.vector_stores.types import VectorStore


from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.retrievers import CustomPGRetriever, VectorContextRetriever
from llama_index.core.vector_stores.types import VectorStore
from llama_index.program.openai import OpenAIPydanticProgram
from pydantic import BaseModel
from typing import Optional, List

from langchain_openai import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph

nest_asyncio.apply()


#  Connect to the Neo4j graph database

from llama_index.graph_stores.neo4j import Neo4jPGStore

username="neo4j"
password="sz7lL8-kJT9q5e7jN-j6VGoaEJ4XEXNRgHgJJugMp0U"
url="neo4j+s://be20d4fc.databases.neo4j.io"

graph_store = Neo4jPGStore(
    username=username,
    password=password,
    url=url,
)

import os

os.environ["OPENAI_API_KEY"] = "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"


llm = OpenAI(model="gpt-4o", temperature=0.0)
embed_model = OpenAIEmbedding(model_name="text-embedding-3-small")


# best practice to use upper-case
entities = Literal["PERSON", "LOCATION", "ORGANIZATION", "PRODUCT", "EVENT"]
relations = Literal[
    "SUPPLIER_OF",
    "COMPETITOR",
    "PARTNERSHIP",
    "ACQUISITION",
    "WORKS_AT",
    "SUBSIDIARY",
    "BOARD_MEMBER",
    "CEO",
    "PROVIDES",
    "HAS_EVENT",
    "IN_LOCATION",
]

# define which entities can have which relations
validation_schema = {
    "Person": ["WORKS_AT", "BOARD_MEMBER", "CEO", "HAS_EVENT"],
    "Organization": [
        "SUPPLIER_OF",
        "COMPETITOR",
        "PARTNERSHIP",
        "ACQUISITION",
        "WORKS_AT",
        "SUBSIDIARY",
        "BOARD_MEMBER",
        "CEO",
        "PROVIDES",
        "HAS_EVENT",
        "IN_LOCATION",
    ],
    "Product": ["PROVIDES"],
    "Event": ["HAS_EVENT", "IN_LOCATION"],
    "Location": ["HAPPENED_AT", "IN_LOCATION"],
}



kg_extractor = SchemaLLMPathExtractor(
    llm=llm,
    possible_entities=entities,
    possible_relations=relations,
    kg_validation_schema=validation_schema,
    # if false, allows for values outside of the schema
    # useful for using the schema as a suggestion
    strict=True,
)

graph_store.structured_query("""
CREATE VECTOR INDEX entity IF NOT EXISTS
FOR (m:`__Entity__`)
ON m.embedding
OPTIONS {indexConfig: {
 `vector.dimensions`: 1536,
 `vector.similarity_function`: 'cosine'
}}
""")

# Just for inspection
similarity_threshold = 0.9
word_edit_distance = 5
data = graph_store.structured_query("""
MATCH (e:__Entity__)
CALL {
  WITH e
  CALL db.index.vector.queryNodes('entity', 10, e.embedding)
  YIELD node, score
  WITH node, score
  WHERE score > toFLoat($cutoff)
      AND (toLower(node.name) CONTAINS toLower(e.name) OR toLower(e.name) CONTAINS toLower(node.name)
           OR apoc.text.distance(toLower(node.name), toLower(e.name)) < $distance)
      AND labels(e) = labels(node)
  WITH node, score
  ORDER BY node.name
  RETURN collect(node) AS nodes
}
WITH distinct nodes
WHERE size(nodes) > 1
WITH collect([n in nodes | n.name]) AS results
UNWIND range(0, size(results)-1, 1) as index
WITH results, index, results[index] as result
WITH apoc.coll.sort(reduce(acc = result, index2 IN range(0, size(results)-1, 1) |
        CASE WHEN index <> index2 AND
            size(apoc.coll.intersection(acc, results[index2])) > 0
            THEN apoc.coll.union(acc, results[index2])
            ELSE acc
        END
)) as combinedResult
WITH distinct(combinedResult) as combinedResult
// extra filtering
WITH collect(combinedResult) as allCombinedResults
UNWIND range(0, size(allCombinedResults)-1, 1) as combinedResultIndex
WITH allCombinedResults[combinedResultIndex] as combinedResult, combinedResultIndex, allCombinedResults
WHERE NOT any(x IN range(0,size(allCombinedResults)-1,1)
    WHERE x <> combinedResultIndex
    AND apoc.coll.containsAll(allCombinedResults[x], combinedResult)
)
RETURN combinedResult
""", param_map={'cutoff': similarity_threshold, 'distance': word_edit_distance})
for row in data:
    print(row)



class Entities(BaseModel):
    """List of named entities in the text such as names of people, organizations, concepts, and locations"""
    names: Optional[List[str]]


prompt_template_entities = """
Extract all named entities such as names of people, organizations, concepts, and locations
from the following text:
{text}
"""

class MyCustomRetriever(CustomPGRetriever):
    """Custom retriever with cohere reranking."""

    def init(
        self,
        ## vector context retriever params
        embed_model: Optional[BaseEmbedding] = None,
        vector_store: Optional[VectorStore] = None,
        similarity_top_k: int = 4,
        path_depth: int = 1,
        include_text: bool = True,
        **kwargs: Any,
    ) -> None:
        """Uses any kwargs passed in from class constructor."""
        self.entity_extraction = OpenAIPydanticProgram.from_defaults(
            output_cls=Entities, prompt_template_str=prompt_template_entities
        )
        self.vector_retriever = VectorContextRetriever(
            self.graph_store,
            include_text=self.include_text,
            embed_model=embed_model,
            similarity_top_k=similarity_top_k,
            path_depth=path_depth,
        )

    def custom_retrieve(self, query_str: str) -> str:
        """Define custom retriever with reranking.

        Could return `str`, `TextNode`, `NodeWithScore`, or a list of those.
        """
        entities = self.entity_extraction(text=query_str).names
        result_nodes = []
        if entities:
            print(f"Detected entities: {entities}")
            for entity in entities:
                result_nodes.extend(self.vector_retriever.retrieve(entity))
        else:
            result_nodes.extend(self.vector_retriever.retrieve(query_str))
        ## TMP: please change
        final_text = "\n\n".join(
            [n.get_content(metadata_mode="llm") for n in result_nodes]
        )
        return final_text
    
index = PropertyGraphIndex(graph_store=graph_store, extractor=kg_extractor, nodes=[])

custom_sub_retriever = MyCustomRetriever(
    index.property_graph_store,
    include_text=True,
    vector_store=index.vector_store,
    embed_model=embed_model
)

query_engine = RetrieverQueryEngine.from_args(
    index.as_retriever(sub_retrievers=[custom_sub_retriever]), llm=llm
)

response = query_engine.query("What do you know about Maliek Collins or Darragh O’Brien?")
print(str(response))