from langchain.tools import tool, Tool
import re
from configuration.graph import graph
from configuration.cypher_chain import cypher_chain
from configuration.embedding import embedding_model
from typing import Union


from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

museum_tools = []


# to get a standartized name
def sanitize_name(name: str) -> str:
    """Removes surrounding quotes and extra whitespace from the museum name."""
    return re.sub(r"^[\"']+|[\"']+$", "", name.strip())

def normalize_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text.strip().lower())

def get_all_facilities():
    results = graph.query("MATCH (f:Facility) RETURN DISTINCT toLower(f.name) AS facility")
    return [r["facility"] for r in results]



def get_best_matching_facility(user_query, facility_list):
    # Embed the user query
    query_embedding = embedding_model.embed_query(user_query)

    # Embed all facilities at once
    facility_embeddings = [embedding_model.embed_query(facility) for facility in facility_list]

    # Compute cosine similarities
    similarities = cosine_similarity([query_embedding], facility_embeddings)[0]  # shape: (N,)

    # Find the best match
    best_index = np.argmax(similarities)
    best_match = facility_list[best_index]
    best_score = similarities[best_index]

    return best_match, best_score


def smart_facility_lookup(user_request: str) -> list:
    """
    Understand the user's facility request (e.g. 'internet', 'parking'), find the closest facility name in the database,
    and return all museums that offer it.
    """

    facility_list = get_all_facilities()
    best_match, score = get_best_matching_facility(user_request, facility_list)

    if not best_match or score < 0.5:
        return [f"No matching facility found for: {user_request}"]

    cypher = """
    MATCH (m:Museum)-[:HAS_FACILITY]->(f:Facility)
    WHERE toLower(f.name) = toLower($facility_name)
    RETURN m.name AS museum
    """
    results = graph.query(cypher, {"facility_name": best_match})
    return [f"{row['museum']} (facility matched: {best_match})" for row in results]


smart_facility_lookup_tool = Tool(
    name="smart_facility_lookup",
    func=smart_facility_lookup,
    description=(
        """
    Understand the user's facility request (e.g. 'internet', 'parking'), find the closest facility name in the database,
    and return all museums that offer it.
    """
    )
)
museum_tools.append(smart_facility_lookup_tool)


def get_museum_info(museum_name: str) -> str:
    """
    Returns structured summary for a museum, 
    including opening hours, rating, address, 
    phone, description, images etc.
    """
    query = """
    MATCH (m:Museum)
    WHERE toLower(m.name) CONTAINS toLower($name)
    RETURN m.name AS name, m.description AS description,
           m.rating AS rating, m.address AS address,
           m.opening_hours_summer AS summer,
           m.opening_hours_winter AS winter,
           m.phone AS phone, m.images AS images
    LIMIT 1
    """
    results = graph.query(query, {"name": museum_name})
    if not results:
        return f"No information found for '{museum_name}'."
    
    data = results[0]
    summary = f"""**{data.get('name', 'Unknown Museum')}**"""
    
    if data.get("rating"):
        summary += f" ({data['rating']})"
    if data.get("address"):
        summary += f"\nAddress: {data['address']}"
    
    if data.get("summer") or data.get("winter"):
        summary += "\nOpening Hours:"
        if data.get("summer"):
            summary += f"\n  - Summer: {data['summer']}"
        if data.get("winter"):
            summary += f"\n  - Winter: {data['winter']}"
    
    if data.get("phone"):
        summary += f"\nPhone: {data['phone']}"
    if data.get("description"):
        summary += f"\n\nℹ Description: {data['description']}"
    if data.get("images"):
        if isinstance(data["images"], list):
            summary += "\n\nImages:\n" + "\n".join(data["images"])
        else:
            summary += f"\n\nImage: {data['images']}"
    
    return summary

get_museum_info_tool = Tool(
    name="get_museum_info",
    func=get_museum_info,
    description=(
        "Use this tool to get detailed information about a museum in İzmir. "
        "It returns the museum's name, rating, address, opening hours (summer/winter), "
        "phone number, description, and images if available. "
        "Input should be the museum's name or a keyword in the name."
    )
)

museum_tools.append(get_museum_info_tool)



@tool
def search_by_rating(min_rating: Union[str, float]) -> str:
    """Returns museums with a rating greater than or equal to the given value."""
    try:
        threshold = float(min_rating)
        query = f"""
        MATCH (m:Museum)
        WHERE toFloat(m.rating) >= {threshold}
        RETURN m.name AS name, m.rating AS rating
        ORDER BY toFloat(m.rating) DESC
        """
        result = cypher_chain.graph.query(query)
        if not result:
            return f"No museums found with rating ≥ {threshold}."
        return "\n".join([f"{row['name']} (⭐ {row['rating']})" for row in result])
    except Exception as e:
        return f"Invalid rating value: {min_rating}. Please provide a number like 4.5."

museum_tools.append(search_by_rating)


def bestfor_sorted_by_rating(bestfor_topic: str) -> str:
    """
    Finds museums best for a specific topic (like 'architecture lovers') and sorts them by rating.
    """
    try:
        # Remove surrounding quotes and normalize the text
        # topic_clean = normalize_text(re.sub(r"^[\"']+|[\"']+$", "", bestfor_topic.strip()))
        topic_clean = sanitize_name(bestfor_topic)
        cypher = """
        MATCH (m:Museum)-[:BEST_FOR]->(a:Audience)
        WHERE toLower(a.name) = $topic AND m.rating IS NOT NULL
        RETURN m.name AS name, m.rating AS rating
        ORDER BY toFloat(m.rating) DESC
        """
        result = graph.query(cypher, {"topic": topic_clean})
        if not result:
            return f"No museums found for topic: '{bestfor_topic}'"
        return "\n".join([f"{row['name']} (⭐ {row['rating']})" for row in result])
    except Exception as e:
        return f"Error processing topic '{bestfor_topic}': {e}" 


bestfor_sorted_by_rating_tool = Tool(
    name="bestfor_sorted_by_rating",
    func=bestfor_sorted_by_rating,
    description=(
        "Finds museums best for a specific topic (like 'architecture lovers') and sorts them by rating."
    )
)

museum_tools.append(bestfor_sorted_by_rating_tool)



def smart_bestfor_lookup(user_request: str) -> list:
    """
    Match user's interest (e.g. 'architecture lovers') with best matching audience node,
    and return museums connected to it.
    """
    # Step 1: Get all Audience names
    results = graph.query("MATCH (a:Audience) RETURN DISTINCT toLower(a.name) AS name")
    all_audiences = [r["name"] for r in results]

    # Step 2: Find best semantic match
    query_embedding = np.array(embedding_model.embed_query(user_request)).reshape(1, -1)

    best_score = -1
    best_match = None

    # Step 3: Compare with each audience embedding using cosine similarity
    for audience in all_audiences:
        audience_embedding = np.array(embedding_model.embed_query(audience)).reshape(1, -1)
        similarity = cosine_similarity(query_embedding, audience_embedding)[0][0]
        if similarity > best_score:
            best_score = similarity
            best_match = audience

    if not best_match or best_score < 0.5:
        return [f"No good match found for '{user_request}'"]

    # Step 4: Find museums connected to that audience
    cypher = """
    MATCH (m:Museum)-[:BEST_FOR]->(a:Audience)
    WHERE toLower(a.name) = $name
    RETURN m.name AS museum
    """
    match_results = graph.query(cypher, {"name": best_match})
    return [f"{row['museum']} (best for: {best_match})" for row in match_results]


smart_bestfor_lookup_tool = Tool(
    name="smart_bestfor_lookup",
    func=smart_bestfor_lookup,
    description=(
        """
    Match user's interest (e.g. 'architecture lovers','history lover') with best matching audience node,
    and return museums connected to it.
    """
    )
)

museum_tools.append(smart_bestfor_lookup_tool)