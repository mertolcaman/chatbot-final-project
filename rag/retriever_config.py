from langchain_neo4j import Neo4jVector
from configuration.embedding import embedding_model
from configuration.graph import graph
from rag.indexes import INDEX_MAP

# A dictionary to store retrievers by key
RETRIEVERS = {}

# Loop through INDEX_MAP and create a retriever for each
for key, config in INDEX_MAP.items():
    RETRIEVERS[key] = Neo4jVector.from_existing_index(
        embedding=embedding_model,
        graph=graph,
        index_name=config["index"],
        embedding_node_property=config["property"],
        text_node_property="description",  # This assumes 'description' holds the retrievable content
        retrieval_query=f"""
        OPTIONAL MATCH (node)-[:LOCATED_IN|POPULAR_IN]->(loc)
        RETURN node.description AS text, score,
        {{
            name: node.name,
            location: loc.name
        }} AS metadata
        """
    )
# location: node.located_in