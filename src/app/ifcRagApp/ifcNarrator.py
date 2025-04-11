#
# 
# 
#       This file uses saved kgPath.txt file to narrate a knowledge graph paths story 
# 
#       that is going to be used as semantically rich and highly knowledge graph state relevant vector store data.
# 
#       The second class in the file named 'ifcNarrator' is going to create and store the embeddings in chroma db.
# #

import os
import ast 
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

class CustomOllamaEmbeddingFunction:
    """
    Here just calling the Ollama API for crteating embeddings model.
    """
    def __init__(self, url="http://localhost:11434", model_name="nomic-embed-text:latest"):
        self.url = url
        self.model_name = model_name
        
    def __call__(self, input):
        """Generate embeddings for input - matching Chroma's expected interface
        
        Args:
            input: A string or list of strings to generate embeddings for
        """
        if isinstance(input, str):
            input = [input]
            
        return [self.safe_embed(text) for text in input]

    def safe_embed(self, doc):
        """
        Call the Ollama API for embeddings, also
        address JSON decode errors and empty documents.
        """
        if not doc or not doc.strip() or doc.strip() == "Empty record.":
            return [0.0] * 768 
        
        import httpx
        
        try:
            response = httpx.post(
                f"{self.url}/api/embeddings",
                json={"model": self.model_name, "prompt": doc},
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("embedding", [0.0] * 768)
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.0] * 768




class ifcNarrator:
    """
    The main class for narrating the knowledge graph paths.
    In a simple explanation: Takes already stored chunks text file -> narratess the paths -> stores the embeddings in chroma db.

    """
    def __init__(self):
        self.kgPath = "C:/Users/berky/oxide/data/chunks.txt"
        self.kgPathList = []
        self.kgPathDict = {}
        self.narratedChunks = []
        self.persist_directory = "C:/Users/berky/oxide/data/chroma"
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        self.ollama_url = "http://localhost:11434"
        
        self.embedding_function = CustomOllamaEmbeddingFunction(
            url=self.ollama_url,
            model_name="nomic-embed-text:latest"
        )
    
      
        self.collection = self.client.get_or_create_collection(
            "ifc_narratives", 
            embedding_function=self.embedding_function
        )

    def generate_narrative_from_record(self, record):
    # The structure of each record is complex: 
    # record:  [{'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcFurnishingElement', 'ObjectType': 'M_Chair-Breuer:M_Chair-Breuer', '__step_file_id': 19219, 'Tag': '165779', 'Name': 'M_Chair-Breuer:M_Chair-Breuer:165779', 'GlobalId': '2idC0G3ezCdhA9WVjWe$3v'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 19213}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 19211, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}, 'ContextOfItems', {'__instance_of': 'IfcGeometricRepresentationSubContext', 'ContextType': 'Model', '__step_file_id': 116, 'ContextIdentifier': 'Body', 'TargetView': 'MODEL_VIEW'}, 'RepresentationsInContext', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 24993, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'SweptSolid'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcWindow', 'OverallWidth': 1.0, 'ObjectType': 'Ventana simple:100 x 100 cm', '__step_file_id': 6627, 'Tag': '164180', 'Name': 'Ventana simple:100 x 100 cm:164180', 'GlobalId': '2idC0G3ezCdhA9WVjWe$O_', 'OverallHeight': 2.3}, 'FillsVoids', {'__instance_of': 'IfcRelFillsElement', '__step_file_id': 24954, 'GlobalId': '11_r20HAvCyvt6z8UU63xQ'}, 'RelatingOpeningElement', {'__instance_of': 'IfcOpeningElement', 'ObjectType': 'Opening', '__step_file_id': 24949, 'Tag': '164180', 'Name': 'Ventana simple:100 x 100 cm:164180:1', 'GlobalId': '2idC0G3ezCdhA9WUXWe$O_'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 24943}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 24941, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'SweptSolid'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 
    # 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcWindow', 'OverallWidth': 1.0, 'ObjectType': 'Ventana simple:100 x 100 cm', '__step_file_id': 6595, 'Tag': '164156', 'Name': 'Ventana simple:100 x 100 cm:164156', 'GlobalId': '2idC0G3ezCdhA9WVjWe$PM', 'OverallHeight': 2.3}, 'FillsVoids', {'__instance_of': 'IfcRelFillsElement', '__step_file_id': 24928, 'GlobalId': '1uDNy6B9vBtuiXn7ELLfec'}, 'RelatingOpeningElement', {'__instance_of': 'IfcOpeningElement', 'ObjectType': 'Opening', '__step_file_id': 24923, 'Tag': '164156', 'Name': 'Ventana simple:100 x 100 cm:164156:1', 'GlobalId': '2idC0G3ezCdhA9WUXWe$PM'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 24917}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 24915, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'SweptSolid'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcFurnishingElement', 'ObjectType': 'M_Chair-Breuer:M_Chair-Breuer', '__step_file_id': 19219, 'Tag': '165779', 'Name': 'M_Chair-Breuer:M_Chair-Breuer:165779', 'GlobalId': '2idC0G3ezCdhA9WVjWe$3v'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 19213}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 19211, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}, 'ContextOfItems', {'__instance_of': 'IfcGeometricRepresentationSubContext', 'ContextType': 'Model', '__step_file_id': 116, 'ContextIdentifier': 'Body', 'TargetView': 'MODEL_VIEW'}, 'RepresentationsInContext', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 23743, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'SweptSolid'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', '__step_file_id': 23875, 'GlobalId': '1s5utE$rDDfRKgyV6jUJ1G'}, 'RelatedObjects', {'__instance_of': 'IfcMember', 'ObjectType': 'Montante rectangular:Montante rectangular - 5 x 10 cm', '__step_file_id': 23704, 'Tag': '167103', 'Name': 'Montante rectangular:Montante rectangular - 5 x 10 cm:167103', 'GlobalId': '1s5utE$rDDfRKgzV6jUJSH'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 23694}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 23692, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcFurnishingElement', 'ObjectType': 'M_Chair-Breuer:M_Chair-Breuer', '__step_file_id': 19219, 'Tag': '165779', 'Name': 'M_Chair-Breuer:M_Chair-Breuer:165779', 'GlobalId': '2idC0G3ezCdhA9WVjWe$3v'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 19213}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 19211, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}, 'ContextOfItems', {'__instance_of': 'IfcGeometricRepresentationSubContext', 'ContextType': 'Model', '__step_file_id': 116, 'ContextIdentifier': 'Body', 'TargetView': 'MODEL_VIEW'}, 'RepresentationsInContext', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 23684, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'SweptSolid'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf',
    #  {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcFurnishingElement', 'ObjectType': 'M_Chair-Breuer:M_Chair-Breuer', '__step_file_id': 19219, 'Tag': '165779', 'Name': 'M_Chair-Breuer:M_Chair-Breuer:165779', 'GlobalId': '2idC0G3ezCdhA9WVjWe$3v'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 19213}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 19211, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}, 'ContextOfItems', {'__instance_of': 'IfcGeometricRepresentationSubContext', 'ContextType': 'Model', '__step_file_id': 116, 'ContextIdentifier': 'Body', 'TargetView': 'MODEL_VIEW'}, 'RepresentationsInContext', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 23598, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'SweptSolid'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', '__step_file_id': 23875, 'GlobalId': '1s5utE$rDDfRKgyV6jUJ1G'}, 'RelatedObjects', {'__instance_of': 'IfcMember', 'ObjectType': 'Montante rectangular:Montante rectangular - 5 x 10 cm', '__step_file_id': 23566, 'Tag': '167017', 'Name': 'Montante rectangular:Montante rectangular - 5 x 10 cm:167017', 'GlobalId': '1s5utE$rDDfRKgzV6jUJV7'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 23556}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 23554, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', '__step_file_id': 23875, 'GlobalId': '1s5utE$rDDfRKgyV6jUJ1G'}, 'RelatedObjects', {'__instance_of': 'IfcMember', 'ObjectType': 'Montante rectangular:Montante rectangular - 5 x 10 cm', '__step_file_id': 23534, 'Tag': '167015', 'Name': 'Montante rectangular:Montante rectangular - 5 x 10 cm:167015', 'GlobalId': '1s5utE$rDDfRKgzV6jUJV9'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 23524}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 23522, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', '__step_file_id': 23875, 'GlobalId': '1s5utE$rDDfRKgyV6jUJ1G'}, 'RelatedObjects', {'__instance_of': 'IfcMember', 'ObjectType': 'Montante rectangular:Montante rectangular - 5 x 10 cm', '__step_file_id': 23502, 'Tag': '167013', 'Name': 'Montante rectangular:Montante rectangular - 5 x 10 cm:167013', 'GlobalId': '1s5utE$rDDfRKgzV6jUJVB'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 23492}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 23490, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', '__step_file_id': 23875, 'GlobalId': '1s5utE$rDDfRKgyV6jUJ1G'}, 'RelatedObjects', {'__instance_of': 'IfcMember', 'ObjectType': 'Montante rectangular:Montante rectangular - 5 x 10 cm', '__step_file_id': 23436, 'Tag': '167011', 'Name': 'Montante rectangular:Montante rectangular - 5 x 10 cm:167011', 'GlobalId': '1s5utE$rDDfRKgzV6jUJVD'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 23426}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 23424, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', '__step_file_id': 23875, 'GlobalId': '1s5utE$rDDfRKgyV6jUJ1G'}, 'RelatedObjects', {'__instance_of': 'IfcMember', 'ObjectType': 'Montante rectangular:Montante rectangular - 5 x 10 cm', '__step_file_id': 23384, 'Tag': '167009', 'Name': 'Montante rectangular:Montante rectangular - 5 x 10 cm:167009', 'GlobalId': '1s5utE$rDDfRKgzV6jUJVF'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 23374}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 23372, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcFurnishingElement', 'ObjectType': 'M_Chair-Breuer:M_Chair-Breuer', '__step_file_id': 19219, 'Tag': '165779', 'Name': 'M_Chair-Breuer:M_Chair-Breuer:165779', 'GlobalId': '2idC0G3ezCdhA9WVjWe$3v'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 19213}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 19211, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}, 'ContextOfItems', {'__instance_of': 'IfcGeometricRepresentationSubContext', 'ContextType': 'Model', '__step_file_id': 116, 'ContextIdentifier': 'Body', 'TargetView': 'MODEL_VIEW'}, 'RepresentationsInContext', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 25045, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'SweptSolid'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', '__step_file_id': 23875, 'GlobalId': '1s5utE$rDDfRKgyV6jUJ1G'}, 'RelatedObjects', {'__instance_of': 'IfcMember',
    #  'ObjectType': 'Montante rectangular:Montante rectangular - 5 x 10 cm', '__step_file_id': 23329, 'Tag': '167006', 'Name': 'Montante rectangular:Montante rectangular - 5 x 10 cm:167006', 'GlobalId': '1s5utE$rDDfRKgzV6jUJVm'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 23319}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 23317, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcFurnishingElement', 'ObjectType': 'M_Chair-Breuer:M_Chair-Breuer', '__step_file_id': 19219, 'Tag': '165779', 'Name': 'M_Chair-Breuer:M_Chair-Breuer:165779', 'GlobalId': '2idC0G3ezCdhA9WVjWe$3v'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 19213}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 19211, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}, 'ContextOfItems', {'__instance_of': 'IfcGeometricRepresentationSubContext', 'ContextType': 'Model', '__step_file_id': 116, 'ContextIdentifier': 'Body', 'TargetView': 'MODEL_VIEW'}, 'RepresentationsInContext', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 23309, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'SweptSolid'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', '__step_file_id': 23875, 'GlobalId': '1s5utE$rDDfRKgyV6jUJ1G'}, 'RelatedObjects', {'__instance_of': 'IfcMember', 'ObjectType': 'Montante rectangular:Montante rectangular - 5 x 10 cm', '__step_file_id': 23286, 'Tag': '167005', 'Name': 'Montante rectangular:Montante rectangular - 5 x 10 cm:167005', 'GlobalId': '1s5utE$rDDfRKgzV6jUJVp'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 23276}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 23274, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcFurnishingElement', 'ObjectType': 'M_Chair-Breuer:M_Chair-Breuer', '__step_file_id': 19219, 'Tag': '165779', 'Name': 'M_Chair-Breuer:M_Chair-Breuer:165779', 'GlobalId': '2idC0G3ezCdhA9WVjWe$3v'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 19213}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 19211, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}, 'ContextOfItems', {'__instance_of': 'IfcGeometricRepresentationSubContext', 'ContextType': 'Model', '__step_file_id': 116, 'ContextIdentifier': 'Body', 'TargetView': 'MODEL_VIEW'}, 'RepresentationsInContext', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 23223, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'SweptSolid'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcFurnishingElement', 'ObjectType': 'M_Chair-Breuer:M_Chair-Breuer', '__step_file_id': 19219, 'Tag': '165779', 'Name': 'M_Chair-Breuer:M_Chair-Breuer:165779', 'GlobalId': '2idC0G3ezCdhA9WVjWe$3v'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 19213}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 19211, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}, 'ContextOfItems', {'__instance_of': 'IfcGeometricRepresentationSubContext', 'ContextType': 'Model', '__step_file_id': 116, 'ContextIdentifier': 'Body', 'TargetView': 'MODEL_VIEW'}, 'RepresentationsInContext', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 23137, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'SweptSolid'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', '__step_file_id': 23875, 'GlobalId': '1s5utE$rDDfRKgyV6jUJ1G'}, 'RelatedObjects', {'__instance_of': 'IfcMember', 'ObjectType': 'Montante rectangular:Montante rectangular - 5 x 10 cm', '__step_file_id': 23039, 'Tag': '166955', 'Name': 'Montante rectangular:Montante rectangular - 5 x 10 cm:166955', 'GlobalId': '1s5utE$rDDfRKgzV6jUJU5'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 23029}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 23027, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcFurnishingElement', 'ObjectType': 'M_Chair-Breuer:M_Chair-Breuer', '__step_file_id': 19219, 'Tag': '165779', 'Name': 'M_Chair-Breuer:M_Chair-Breuer:165779', 'GlobalId': '2idC0G3ezCdhA9WVjWe$3v'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 19213}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 19211, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}, 'ContextOfItems', {'__instance_of': 'IfcGeometricRepresentationSubContext', 'ContextType': 'Model', '__step_file_id': 116, 'ContextIdentifier': 'Body', 'TargetView': 'MODEL_VIEW'}, 'RepresentationsInContext', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 23019, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'SweptSolid'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 
    # 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', '__step_file_id': 23875, 'GlobalId': '1s5utE$rDDfRKgyV6jUJ1G'}, 'RelatedObjects', {'__instance_of': 'IfcMember', 'ObjectType': 'Montante rectangular:Montante rectangular - 5 x 10 cm', '__step_file_id': 22996, 'Tag': '166944', 'Name': 'Montante rectangular:Montante rectangular - 5 x 10 cm:166944', 'GlobalId': '1s5utE$rDDfRKgzV6jUJUE'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 22986}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 22984, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', '__step_file_id': 23875, 'GlobalId': '1s5utE$rDDfRKgyV6jUJ1G'}, 'RelatedObjects', {'__instance_of': 'IfcMember', 'ObjectType': 'Montante rectangular:Montante rectangular - 5 x 10 cm', '__step_file_id': 22952, 'Tag': '166943', 'Name': 'Montante rectangular:Montante rectangular - 5 x 10 cm:166943', 'GlobalId': '1s5utE$rDDfRKgzV6jUJUn'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 22942}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 22940, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', '__step_file_id': 23875, 'GlobalId': '1s5utE$rDDfRKgyV6jUJ1G'}, 'RelatedObjects', {'__instance_of': 'IfcPlate', 'ObjectType': 'Panel de sistema:Acristalado', '__step_file_id': 22916, 'Tag': '166992', 'Name': 'Panel de sistema:Acristalado:166992', 'GlobalId': '1s5utE$rDDfRKgzV6jUJV_'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 22906}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 22904, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', '__step_file_id': 23875, 'GlobalId': '1s5utE$rDDfRKgyV6jUJ1G'}, 'RelatedObjects', {'__instance_of': 'IfcPlate', 'ObjectType': 'Panel de sistema:Acristalado', '__step_file_id': 22900, 'Tag': '166991', 'Name': 'Panel de sistema:Acristalado:166991', 'GlobalId': '1s5utE$rDDfRKgzV6jUJVX'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 22890}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 22888, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', '__step_file_id': 23875, 'GlobalId': '1s5utE$rDDfRKgyV6jUJ1G'}, 'RelatedObjects', {'__instance_of': 'IfcPlate', 'ObjectType': 'Panel de sistema:Acristalado', '__step_file_id': 22836, 'Tag': '166986', 'Name': 'Panel de sistema:Acristalado:166986', 'GlobalId': '1s5utE$rDDfRKgzV6jUJVa'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 22826}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 22824, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', '__step_file_id': 23875, 'GlobalId': '1s5utE$rDDfRKgyV6jUJ1G'}, 'RelatedObjects', {'__instance_of': 'IfcPlate', 'ObjectType': 'Panel de sistema:Acristalado', '__step_file_id': 22804, 'Tag': '166984', 'Name': 'Panel de sistema:Acristalado:166984', 'GlobalId': '1s5utE$rDDfRKgzV6jUJVc'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 22794}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 22792, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', '__step_file_id': 23875, 'GlobalId': '1s5utE$rDDfRKgyV6jUJ1G'}, 'RelatedObjects', {'__instance_of': 'IfcPlate', 'ObjectType': 'Panel de sistema:Acristalado', '__step_file_id': 22748, 'Tag': '166946', 'Name': 'Panel de sistema:Acristalado:166946', 'GlobalId': '1s5utE$rDDfRKgzV6jUJUC'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 22738}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 22736, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcFurnishingElement', 'ObjectType': 'M_Chair-Breuer:M_Chair-Breuer', '__step_file_id': 19219, 'Tag': '165779', 'Name': 'M_Chair-Breuer:M_Chair-Breuer:165779', 'GlobalId': '2idC0G3ezCdhA9WVjWe$3v'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 19213}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 19211, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}, 'ContextOfItems', {'__instance_of': 'IfcGeometricRepresentationSubContext', 'ContextType': 'Model', '__step_file_id': 116, 'ContextIdentifier': 'Body', 'TargetView': 'MODEL_VIEW'}, 'RepresentationsInContext', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 22728, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'SweptSolid'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 
    # 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', '__step_file_id': 23875, 'GlobalId': '1s5utE$rDDfRKgyV6jUJ1G'}, 'RelatedObjects', {'__instance_of': 'IfcPlate', 'ObjectType': 'Panel de sistema:Acristalado', '__step_file_id': 22705, 'Tag': '166941', 'Name': 'Panel de sistema:Acristalado:166941', 'GlobalId': '1s5utE$rDDfRKgzV6jUJUp'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 22694}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 22692, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcSlab', 'ObjectType': 'Suelo:Por defecto - 30 cm', '__step_file_id': 22551, 'Tag': '166729', 'PredefinedType': 'FLOOR', 'Name': 'Suelo:Por defecto - 30 cm:166729', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ3d'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 22549}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 22547, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'SweptSolid'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcFurnishingElement', 'ObjectType': 'M_Chair-Breuer:M_Chair-Breuer', '__step_file_id': 19219, 'Tag': '165779', 'Name': 'M_Chair-Breuer:M_Chair-Breuer:165779', 'GlobalId': '2idC0G3ezCdhA9WVjWe$3v'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 19213}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 19211, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}, 'ContextOfItems', {'__instance_of': 'IfcGeometricRepresentationSubContext', 'ContextType': 'Model', '__step_file_id': 116, 'ContextIdentifier': 'Body', 'TargetView': 'MODEL_VIEW'}, 'RepresentationsInContext', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 22468, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'Brep'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcFurnishingElement', 'ObjectType': 'M_Chair-Breuer:M_Chair-Breuer', '__step_file_id': 19419, 'Tag': '165865', 'Name': 'M_Chair-Breuer:M_Chair-Breuer:165865', 'GlobalId': '2idC0G3ezCdhA9WVjWe$23'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 19413}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 19411, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcFurnishingElement', 'ObjectType': 'M_Chair-Breuer:M_Chair-Breuer', '__step_file_id': 19379, 'Tag': '165863', 'Name': 'M_Chair-Breuer:M_Chair-Breuer:165863', 'GlobalId': '2idC0G3ezCdhA9WVjWe$2D'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 19373}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 19371, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcFurnishingElement', 'ObjectType': 'M_Table-Dining Round w Chairs:0915mm Diameter', '__step_file_id': 19359, 'Tag': '165862', 'Name': 'M_Table-Dining Round w Chairs:0915mm Diameter:165862', 'GlobalId': '2idC0G3ezCdhA9WVjWe$2C'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 19353}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 19351, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcFurnishingElement', 'ObjectType': 'M_Chair-Breuer:M_Chair-Breuer', '__step_file_id': 19339, 'Tag': '165825', 'Name': 'M_Chair-Breuer:M_Chair-Breuer:165825', 'GlobalId': '2idC0G3ezCdhA9WVjWe$2h'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 19333}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 19331, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, {'p': [{'__instance_of': 'IfcCurtainWallType', '__step_file_id': 23921, 'Tag': '16282', 'PredefinedType': 'NOTDEFINED', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm', 'GlobalId': '0wQknZQiXEOBcv2M5Gzx_W'}, 'ObjectTypeOf', {'__instance_of': 'IfcRelDefinesByType', '__step_file_id': 24832, 'GlobalId': '0K2f6vH057y85pGQ0ljFn9'}, 'RelatedObjects', {'__instance_of': 'IfcCurtainWall', 'ObjectType': 'Muro cortina:Muro cortina - 300 x 200 cm', '__step_file_id': 22655, 'Tag': '166910', 'Name': 'Muro cortina:Muro cortina - 300 x 200 cm:166910', 'GlobalId': '1s5utE$rDDfRKgzV6jUJ1G'}, 'ContainedInStructure', {'__instance_of': 'IfcRelContainedInSpatialStructure', '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcFurnishingElement', 'ObjectType': 'M_Chair-Breuer:M_Chair-Breuer', '__step_file_id': 19319, 'Tag': '165824', 'Name': 'M_Chair-Breuer:M_Chair-Breuer:165824', 'GlobalId': '2idC0G3ezCdhA9WVjWe$2g'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 19313}, 'Representations', {'__instance_of': 'IfcShapeRepresentation', '__step_file_id': 19311, 'RepresentationIdentifier': 'Body', 'RepresentationType': 'MappedRepresentation'}]}, 

        """
        [{'p': [{'__instance_of': 'IfcBuilding', '__step_file_id': 129, 'LongName': '', 
        'CompositionType': 'ELEMENT', 'Name': '', 'GlobalId': '0w984V0GL6yR4z75XVLWOr'}, 'IsDecomposedBy', {'__instance_of': 'IfcRelAggregates', 
        '__step_file_id': 24537, 'GlobalId': '29TFpHBYXAnw12nit37b74'}, 'RelatedObjects', {'__instance_of': 'IfcBuildingStorey', 
        'ObjectType': 'Nivel:Nivel 1', 'Elevation': 0.0, '__step_file_id': 138, 'LongName': 'Nivel 1', 'CompositionType': 'ELEMENT', 
        'Name': 'Nivel 1', 'GlobalId': '0w984V0GL6yR4z75YWgVfX'}, 'ContainsElements', {'__instance_of': 'IfcRelContainedInSpatialStructure', 
        '__step_file_id': 24466, 'GlobalId': '29TFpHBYXAnw12ni$37b4C'}, 'RelatedElements', {'__instance_of': 'IfcFurnishingElement', 
        'ObjectType': 'M_Chair-Breuer:M_Chair-Breuer', '__step_file_id': 19439, 'description': '{code: IfcFurnishingElement, 
        name: Furnishing Element, definition: A furnishing element is a generalization of all furniture related objects. 
        Furnishing objects are characterized as being}', 'Tag': '165866', 'Name': 'M_Chair-Breuer:M_Chair-Breuer:165866', 
        'GlobalId': '2idC0G3ezCdhA9WVjWe$20'}, 'Representation', {'__instance_of': 'IfcProductDefinitionShape', '__step_file_id': 19433}, 
        'Representations', {'__instance_of': 'IfcShapeRepresentation', 
        """
        print("Narrator is running...")
        print("record: ", record)
        record = record.strip()
        
        
        if record.lower().startswith("p"):
            try:
                record = record.split("p", 1)[1].strip()
                print("record in .lower(): ", record)
            except Exception as e:
                return e
    
        
        try:
            import json
            
            parsed_record = ast.literal_eval(record.strip())
            print("parsed_record: ", parsed_record)
        except Exception as e:
            return f"Error parsing record: {e}"

        narrative_parts = []
       # there are many print statements in the code, which are used for debugging and tracking the process.
        for element in parsed_record:
            if isinstance(element, dict) and 'p' in element:
                #print("Element: ",element)
                parts = element['p']
                #print("parts: ", parts)
                i = 0
                # The part here is süper crucial as it directly tailors the narrations language.
                # It always up to improvement and in fact should be improved.
                while i < len(parts):
                    item = parts[i]
                    if isinstance(item, dict):
                        attr_str = ", ".join(f"{k}: '{v}'" for k, v in item.items() if k != '__instance_of')
                        narrative_parts.append(
                            f"{item.get('__instance_of', 'Unknown')} has attributes ({attr_str})."
                        )
                        i += 1
                    elif isinstance(item, str):
                        relationship = item
                        
                        if i + 1 < len(parts) and isinstance(parts[i + 1], dict):
                            next_node = parts[i + 1]
                            attr_str = ", ".join(f"{k}: '{v}'" for k, v in next_node.items() if k != '__instance_of')
                            narrative_parts.append(
                                f"It is connected via the relationship '{relationship}' to {next_node.get('__instance_of', 'Unknown')}, which has attributes ({attr_str})."
                            )
                            i += 2 
                        else:
                            narrative_parts.append(
                                f"It is connected via the relationship '{relationship}', but no node info is provided."
                            )
                            i += 1
                    else:
                        narrative_parts.append("Unrecognized element encountered.")
                        i += 1
            else:
                narrative_parts.append("Record element is unrecognized.")
        
        return " ".join(narrative_parts)



       
    def narrate(self):
        with open(self.kgPath, 'r', encoding='utf-8') as f:
            print("f", f)
            for line in f:
                try:
                    record = line
                    print(record)
                    
                except Exception as e:
                    print("Error processing line:",e)
                    continue
                narrative = self.generate_narrative_from_record(record)
                if narrative and narrative != "" or "Empty record." and not narrative.startswith("Error parsing record: invalid syntax"):
                    self.narratedChunks.append(narrative)
                
        print(f"Narratives generated", self.narratedChunks)
        # Print the narratives, in a one per record way
        """for idx, narrative in enumerate(self.narratedChunks, start=1):
            print(f"Record {idx}: {narrative}")"""


    def save_narratives_to_file(self):
        output_path = "C:/Users/berky/oxide/data/narratives.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            for idx, narrative in enumerate(self.narratedChunks, start=1):
                f.write(f"Record {idx}: {narrative}\n")
        print(f"Saved {len(self.narratedChunks)} narratives to {output_path}.")



    
    def store_file_to_chroma_chunked(self, file_path="C:/Users/berky/oxide/data/narratives.txt", batch_size=100):
        """
        Reads narratives from a text file, splits them into smaller chunks,
        and stores them in the Chroma vector store for RAG application.
        Uses batched processing to avoid memory issues.
        """
        try:
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            os.makedirs(self.persist_directory, exist_ok=True)
            
            print(f"Loading text from {file_path}...")
            
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                
            if not text.strip():
                print(f"No content found in {file_path}.")
                return
                
            # RecursiveCharacterTextSplitter which handles long texts better
            # Overlap size and so on are all debatable and wouldn't defend this configuration at all.
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1500,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            # Whole text split into chunks here.
            chunks = text_splitter.split_text(text)
            print(f"Split text into {len(chunks)} chunks.")
            
            print("Recreating collection...")
            try:
                self.client.delete_collection("ifc_narratives")
                print("Deleted existing collection")
            except:
                print("No existing collection to delete")
            
            # Create a fresh collection
            self.collection = self.client.create_collection(
                "ifc_narratives", 
                embedding_function=self.embedding_function
            )
            # Processing in smaller batches better for computing
            #total_chunks = len(chunks)
            total_chunks = 100
            for i in range(0, total_chunks, batch_size):
                batch_end = min(i + batch_size, total_chunks)
                batch_chunks = chunks[i:batch_end]
                
                print(f"Processing batch {i//batch_size + 1}/{(total_chunks + batch_size - 1)//batch_size}: chunks {i} to {batch_end-1}")
                
                # Prepare document IDs and metadata for this batch
                batch_ids = [f"chunk_{i+j}" for j in range(len(batch_chunks))]
                batch_metadatas = [{"chunk_num": i+j, "source": file_path} for j in range(len(batch_chunks))]
                
                # Add this batch to the collection
                self.collection.add(
                    ids=batch_ids,
                    documents=batch_chunks,
                    metadatas=batch_metadatas
                )
                
                
            # A small verification test
            collections = self.client.list_collections()
            collection_names = [col.name for col in collections]
            print(f"Available collections: {collection_names}")
            
            if "ifc_narratives" in collection_names:
                count = self.collection.count()
                print(f"Successfully stored {count} documents in collection 'ifc_narratives' at '{self.persist_directory}'.")
                
                # Verify it's queryable with a simple query
                try:
                    results = self.collection.query(
                        query_texts=["test query"],
                        n_results=1
                    )
                    print(f"Collection is queryable - received {len(results['documents'])} results for test query")
                except Exception as query_error:
                    print(f"Warning: Collection exists but query failed: {query_error}")
            else:
                print("ERROR: Collection was not successfully created!")
            
                print(f"Successfully stored {total_chunks} text chunks to Chroma DB at '{self.persist_directory}'.")
                
        except ImportError:
            # I had package management issues for some reason. So implemented this try except block to call the package
            # Sometimes it doesn't import :S.
            print("LangChain not installed. Please install with: pip install langchain")
        

if __name__ == "__main__":
    narrator = ifcNarrator()
    #narrator.narrate()
    #narrator.save_narratives_to_file()
    narrator.store_file_to_chroma_chunked()





