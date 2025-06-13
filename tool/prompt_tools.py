from langchain.tools import tool
from configuration.llm import llm


prompt_tools = []


@tool
def itinerary_formatter(input: str) -> str:
    """
    Format a raw itinerary for a specific audience. 
    Input must be in the format: raw_itinerary|||audience
    Example: "3-day plan in İzmir|||family"
    """
    try:
        raw_itinerary, audience = input.split("|||")
    except Exception:
        return "Input must be in the format: raw_itinerary|||audience"

    prompt = f"""
    Format this is an İzmir travel itinerary for a {audience} traveler.
    Adjust the tone, recommended activities, and language style accordingly.
    
    - Highlight the most relevant locations with the features what makes those places unique.
    - Use clear, friendly, human-style language.
 
    Raw Itinerary:
    {raw_itinerary}
    """
    return llm.invoke(prompt)


prompt_tools.append(itinerary_formatter)