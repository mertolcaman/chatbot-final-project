# from langchain_community.chat_message_histories import Neo4jChatMessageHistory
# from configuration.graph import graph  # Ensure this is your active Neo4jGraph instance

# def get_memory(session_id: str):
#     """
#     Returns a Neo4j-backed message history object for the given session.
#     Compatible with RunnableWithMessageHistory.
#     """
#     return Neo4jChatMessageHistory(session_id=session_id, graph=graph)


from langchain_neo4j import Neo4jChatMessageHistory
from configuration.graph import graph

def get_memory(session_id: str):
    return Neo4jChatMessageHistory(session_id=session_id, graph=graph)
