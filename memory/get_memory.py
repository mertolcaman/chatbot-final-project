from langchain.memory import ConversationBufferMemory
from langchain_neo4j import Neo4jChatMessageHistory
from configuration.graph import graph  # Your Neo4jGraph instance

def get_memory(session_id: str):
    history = Neo4jChatMessageHistory(session_id=session_id, graph=graph)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=history,
        return_messages=True
    )

    return memory
