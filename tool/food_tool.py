from langchain.tools import Tool
from configuration.graph import graph

def check_allergen_foods(allergen: str) -> str:
    query = """
    MATCH (f:Food)-[:HAS_INGREDIENT]->(i:Ingredient)
    WHERE toLower(i.name) CONTAINS toLower($allergen)
    RETURN f.name AS name, collect(i.name) AS matched_ingredients
    """
    results = graph.query(query, {"allergen": allergen})

    if not results:
        return f"No foods found containing '{allergen}'. You may be safe — but always ask locally!"

    response = f"The following foods in İzmir contain ingredients related to '{allergen}':\n"
    for record in results:
        response += f"- {record['name']} (Ingredients: {', '.join(record['matched_ingredients'])})\n"

    return response.strip()

food_tools = []


allergen_tool = Tool(
    name="allergen_checker",
    description="Use this tool to check which İzmir foods contain a specific allergen (like tomato, nuts, dairy).",
    func=check_allergen_foods,
    return_direct=True
)

food_tools.append(allergen_tool)