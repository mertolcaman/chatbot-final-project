from configuration.llm import llm
from rag.retriever_config import RETRIEVERS
from rag.indexes import INDEX_MAP
from configuration.graph import graph
from configuration.embedding import embedding_model

from langchain_neo4j import Neo4jVector
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.prompts import ChatPromptTemplate
from langchain.retrievers import EnsembleRetriever

# Flexible system prompt
INSTRUCTIONS_TEMPLATE = (
    "You are a helpful travel assistant for İzmir.\n"
    "Use the following context to answer the user's question.\n"
    "Context: {context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", INSTRUCTIONS_TEMPLATE),
    ("human", "{input}")
])

# Shared document combination logic
document_chain = create_stuff_documents_chain(llm, prompt)

# Place-related categories to use for activity matching
PLACE_CATEGORIES = [
    "ancient_city", "bay", "beach", "castle", "city", "cultural_site", "historical_site",
    "island", "landmark", "market", "monument", "natural_park", "religious_place",
    "temple", "tower", "town", "village"
]

# Utility: Build a Neo4j retriever from a single category config
def build_single_retriever(category: str):
    config = INDEX_MAP.get(category)
    if not config:
        raise ValueError(f"No config found for category: '{category}'.")

    text_property = "description" if "description" in config["property"] else "name"

    return Neo4jVector.from_existing_index(
        embedding=embedding_model,
        graph=graph,
        index_name=config["index"],
        embedding_node_property=config["property"],
        text_node_property=text_property,
        retrieval_query=f"""
        OPTIONAL MATCH (node)-[:LOCATED_IN|POPULAR_IN]->(loc)
        RETURN node.{text_property} AS text, score,
        {{
            name: node.name,
            location: loc.name
        }} AS metadata
        """
    )

# Main: Get a RAG chain for a single category
def get_rag_chain(category: str):
    retriever = build_single_retriever(category).as_retriever()

    return create_retrieval_chain(
        retriever=retriever,
        combine_docs_chain=document_chain
    )

# Composite: Get a merged activity chain for all place types
def get_activity_chain(categories: list[str] = PLACE_CATEGORIES):
    sub_retrievers = [
        build_single_retriever(cat).as_retriever()
        for cat in categories if cat in INDEX_MAP
    ]

    ensemble = EnsembleRetriever(retrievers=sub_retrievers, weights=[1] * len(sub_retrievers))

    return create_retrieval_chain(
        retriever=ensemble,
        combine_docs_chain=document_chain
    )
