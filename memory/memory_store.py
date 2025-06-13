from langchain_neo4j import Neo4jChatMessageHistory
from configuration.graph import graph

def get_memory(session_id: str):
    return Neo4jChatMessageHistory(session_id=session_id, graph=graph)
