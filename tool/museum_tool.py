from langchain.tools import tool
import re
from configuration.llm import llm
from configuration.prompt import CYPHER_GENERATION_TEMPLATE
from configuration.graph import graph
from configuration.cypher_chain import cypher_chain
from configuration.embedding import embedding_model
from typing import Union

import os
from dotenv import load_dotenv
load_dotenv()


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
    query_embedding = embedding_model.embed_query(user_query)
    best_score = -1
    best_match = None
    for facility in facility_list:
        facility_embedding = embedding_model.embed_query(facility)
        similarity = sum(q * f for q, f in zip(query_embedding, facility_embedding))
        if similarity > best_score:
            best_score = similarity
            best_match = facility
    return best_match, best_score

@tool
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


museum_tools.append(smart_facility_lookup)

@tool
def get_museum_info(museum_name: str) -> str:
    """
    Returns structured summary for a museum, including hours, rating, etc.
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
    summary = f""" **{data.get('name', 'Unknown Museum')}**"""
    if data.get("rating"):
        summary += f" ( {data['rating']})"
    if data.get("address"):
        summary += f"\n Address: {data['address']}"
    if data.get("summer") or data.get("winter"):
        summary += "\n Opening Hours:"
        if data.get("summer"):
            summary += f"\n  - Summer: {data['summer']}"
        if data.get("winter"):
            summary += f"\n  - Winter: {data['winter']}"
    if data.get("phone"):
        summary += f"\n Phone: {data['phone']}"
    if data.get("description"):
        summary += f"\n\nℹ Description: {data['description']}"
    if data.get("images"):
        if isinstance(data["images"], list):
            summary += f"\n\n Images:\n" + "\n".join(data["images"])
        else:
            summary += f"\n\n Image: {data['images']}"
    return summary


museum_tools.append(get_museum_info)



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

@tool
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

museum_tools.append(bestfor_sorted_by_rating)


@tool
def smart_bestfor_lookup(user_request: str) -> list:
    """
    Match user's interest (e.g. 'architecture lovers') with best matching audience node,
    and return museums connected to it.
    """
    # Step 1: Get all Audience names
    results = graph.query("MATCH (a:Audience) RETURN DISTINCT toLower(a.name) AS name")
    all_audiences = [r["name"] for r in results]

    # Step 2: Find best semantic match
    query_embedding = embedding_model.embed_query(user_request)
    best_score = -1
    best_match = None
    for audience in all_audiences:
        audience_embedding = embedding_model.embed_query(audience)
        similarity = sum(q * a for q, a in zip(query_embedding, audience_embedding))
        if similarity > best_score:
            best_score = similarity
            best_match = audience

    if not best_match or best_score < 0.5:
        return [f"No good match found for '{user_request}'"]

    # Step 3: Find museums connected to that audience
    cypher = """
    MATCH (m:Museum)-[:BEST_FOR]->(a:Audience)
    WHERE toLower(a.name) = $name
    RETURN m.name AS museum
    """
    match_results = graph.query(cypher, {"name": best_match})
    return [f"{row['museum']} (best for: {best_match})" for row in match_results]

museum_tools.append(smart_bestfor_lookup)