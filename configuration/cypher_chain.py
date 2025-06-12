from langchain_neo4j import GraphCypherQAChain
from configuration.llm import llm
from configuration.graph import graph
from configuration.prompt import cypher_generation_prompt

cypher_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    cypher_prompt=cypher_generation_prompt,
    verbose=True,
    enhanced_schema=True,
    input_key="question",
    allow_dangerous_requests=True
)

full_schema = graph.get_schema



#cypher_chain is called in cypher_tools.py
