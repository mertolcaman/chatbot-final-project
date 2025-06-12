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
    Format this 3-day İzmir travel itinerary for a {audience} traveler.
    Adjust the tone, recommended activities, and language style accordingly.

    Raw Itinerary:
    {raw_itinerary}
    """
    return llm.invoke(prompt)


prompt_tools.append(itinerary_formatter)

# @tool
# def romantic_itinerary_formatter(raw_itinerary: str) -> str:
#     """
#     Beautifies a raw itinerary into a romantic and scenic 3-day trip plan for couples who prefer hidden gems and non-crowded places.
#     """
#     prompt = f"""
#     Transform the following raw itinerary into a personalized, romantic 3-day trip plan in İzmir for a couple around 29 years old.
#     Prioritize peaceful, scenic, and less-explored locations. Use vivid, engaging descriptions. Avoid generic budget advice.

#     Raw Itinerary:
#     {raw_itinerary}

#     Romantic 3-Day Trip Plan:
#     """
#     return llm.invoke(prompt)

# prompt_tools.append(romantic_itinerary_formatter)


# @tool
# def family_itinerary_formatter(raw_itinerary: str) -> str:
#     """
#     Transforms a raw itinerary into a 3-day family-friendly trip plan in İzmir.
#     Focuses on educational, interactive, and fun activities for all ages.
#     """
#     prompt = f"""
#     Convert the following raw itinerary into a 3-day İzmir trip plan designed for a family with children.
#     Emphasize educational museums, hands-on activities, safe locations, and kid-friendly dining options.

#     Raw Itinerary:
#     {raw_itinerary}

#     Family-Friendly Trip Plan:
#     """
#     return llm.invoke(prompt)

# prompt_tools.append(family_itinerary_formatter)