from langchain.prompts import PromptTemplate

CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
Generate a Cypher statement to query a Neo4j graph database for an İzmir travel assistant.

Instructions:
- Use only the provided node labels, relationship types, and properties mentioned in the schema below.
- DO NOT invent or assume new labels, relationship types (e.g., OPENING_HOURS), or node types (e.g., OpeningHours).
- Museums store their opening hours as **node properties**: `opening_hours_summer` and `opening_hours_winter`.
- Use case-insensitive string comparisons for all user-supplied values.
- Museums have time ranges in their properties: `opening_hours_summer`, `opening_hours_winter`, e.g., "08:30-19:00(Monday : Close)" or "09:00-21:00"
- To check current opening status:
    1. Remove text like "(Monday : Close)"
    2. Split by '-' to get opening and closing times
    3. Convert them using `apoc.temporal.toTime(...)`
    4. Compare using `WITH time() AS now` then `WHERE now >= open_time AND now <= close_time`
---------------------------------------
Examples of valid queries:
----------------------------------------
-- Find museums best for families, sorted by rating:
MATCH (m:Museum)-[:BEST_FOR]->(a:Audience)
WHERE toLower(a.name) = 'families' AND m.rating IS NOT NULL
RETURN m.name AS name, m.rating AS rating
ORDER BY toFloat(m.rating) DESC

-- Find museums with a specific facility (like 'parking'):
MATCH (m:Museum)-[:HAS_FACILITY]->(f:Facility)
WHERE toLower(f.name) = 'car parking'
RETURN m.name AS name

-- Get museum information (description, opening hours, rating, coordinates etc.): 
MATCH (m:Museum)
WHERE toLower(m.name) CONTAINS toLower("Louvre Museum")
RETURN m.name AS name, m.description AS description,
       m.rating AS rating, m.address AS address,
       m.opening_hours_summer AS summer,
       m.opening_hours_winter AS winter,
       m.phone AS phone, m.images AS images
LIMIT 1


----------------------------------------



Schema:
{schema}

The question is:
{question}"""

cypher_generation_prompt = PromptTemplate(
    template=CYPHER_GENERATION_TEMPLATE,
    input_variables=["schema", "question"]
)


from rag.indexes import INDEX_MAP
available_categories = ", ".join(f"'{k}'" for k in INDEX_MAP.keys())





agent_prompt = PromptTemplate.from_template("""
You are an intelligent travel assistant for İzmir.
You can answer questions about places, food, landmarks, events, activities, culture etc.

IMPORTANT RULES:
- NEVER invent names of places, museums, foods, or facilities.
- ONLY mention places that exist in the knowledge graph or have been retrieved using a tool.
- If unsure about a place, always call the relevant RAG tool or Cypher query tool to verify.

If the user's query is related to locations, museums, foods, or descriptions,
use the `general_rag_search` tool with the appropriate category.

Available categories: {available_categories}
Call the tool with input like: {{'query': 'user question', 'category': 'category name'}}

TOOL USAGE:
-----------
Use tools strategically depending on the query. Some key behaviors include:
{tools}

To use a tool, follow this format:

Thought: Do I need to use a tool? Yes  
Action: the action to take, should be one of [{tool_names}]  
Action Input: the input to the action  
Observation: the result of the action

If you do not need a tool, or you're ready to answer the user, respond like this:

Thought: Do I need to use a tool? No  
Final Answer: [your response here]

                                            
REMINDER:
---------
In your Final Answer, aim to:
- Highlight the most relevant locations.
- Include YouTube video link for the top places.
- Include a Google Maps location if available.
- Use clear, friendly, human-style language.

Start your reasoning now.

Previous conversation history:  
{chat_history}

New input: {input}  
{agent_scratchpad}
""").partial(available_categories=available_categories)

