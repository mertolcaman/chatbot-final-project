from langchain.tools import Tool
from rag.indexes import INDEX_MAP
from rag.retrieval_chain import get_rag_chain, get_activity_chain

rag_tools = []

# Function to create a callable for RAG category chains
def make_tool_func(cat):
    return lambda query: get_rag_chain(cat).invoke({"input": query})["answer"]

# Generate RAG tools for each category in INDEX_MAP
for category in INDEX_MAP:
    readable_name = category.replace("_", " ").title()

    description = (
        f"Use this tool to answer descriptive or unstructured questions about {readable_name} in İzmir — such as what it is, "
        "what it's known for, or why it is recommended. This tool is ideal for answering questions about the place's description, "
        "special features, or unique experiences. "
        "Avoid using this tool to answer fact-based questions like exact locations, ingredients, facilities, or structured attributes — "
        "use a Cypher tool instead for those."
    )

    rag_tools.append(
        Tool(
            name=f"rag_{category}",
            description=description,
            func=make_tool_func(category),
            return_direct=True
        )
    )

# Special tool: Activity-based semantic search across multiple places
rag_tools.append(
    Tool(
        name="rag_activity_matcher",
        description=(
            "Use this tool to find towns, beaches, or other places in İzmir associated with specific activities based on their descriptions. "
            "Ideal for questions like 'Where can I do windsurfing?' or 'Where is good for hiking?'"
        ),
        func=lambda query: get_activity_chain().invoke({"input": query})["answer"],
        return_direct=True
    )
)
