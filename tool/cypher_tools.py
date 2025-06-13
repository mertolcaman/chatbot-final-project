from configuration.cypher_chain import cypher_chain, full_schema
from langchain_core.tools import Tool
from langchain.prompts import PromptTemplate
from configuration.prompt import  CYPHER_GENERATION_TEMPLATE

cypher_tools=[]


cypher_nl_tool = Tool(
    name="cypher_nl_tool",
    func=lambda question: cypher_chain.invoke({
        "question": question,
        "schema": full_schema
    }).get("result", "No answer found."),
    description="""
    Use this tool when the user asks about structured knowledge, such as:
    - places, relationships, or attributes stored in the Neo4j knowledge graph
    - questions about museums, foods, towns, features, audience, or concepts
    This tool generates and runs Cypher queries based on the graph database schema.
    """
    
)

cypher_tools.append(cypher_nl_tool)