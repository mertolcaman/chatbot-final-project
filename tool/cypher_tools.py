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
    description="Use this tool to answer any question based on the structured data in the Neo4j knowledge graph."
)

cypher_tools.append(cypher_nl_tool)