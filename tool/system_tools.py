from datetime import datetime, timedelta
from langchain.tools import tool
import pytz
from langchain.tools import Tool
from configuration.graph import graph
import re
from langchain.tools import YouTubeSearchTool
import ast


yt_tool = YouTubeSearchTool()



system_tools=[]





@tool
def get_current_datetime(input: str = "") -> dict:
    """
    Returns the current date/time, the day of the week, and the season.
    If input is 'tomorrow', returns tomorrow's date and day.
    Useful for timestamp logic like opening hours, checking current time/day, and seasonal checks.
    """
    now = datetime.now()

    if input.strip().lower() == "tomorrow":
        target = now + timedelta(days=1)
    else:
        target = now

    # Determine the season
    month = target.month
    day = target.day

    if (month == 12 and day >= 21) or (1 <= month <= 2) or (month == 3 and day < 20):
        season = "Winter"
    elif (month == 3 and day >= 20) or (4 <= month <= 5) or (month == 6 and day < 21):
        season = "Spring"
    elif (month == 6 and day >= 21) or (7 <= month <= 8) or (month == 9 and day < 22):
        season = "Summer"
    else:
        season = "Autumn"

    return {
        "iso": target.isoformat(),
        "day_of_week": target.strftime("%A"),  # e.g., Monday, Tuesday
        "season": season
    }


system_tools.append(get_current_datetime)


def get_hour_from_offset(offset: str = "now") -> dict:
   


    tz = pytz.timezone("Europe/Istanbul")
    now = datetime.now(tz)

    # Clean and normalize input
    offset = offset.strip().lower().replace('"', '').replace("'", "")
    
    if "hour" in offset:
        match = re.search(r"\d+", offset)
        hours = int(match.group()) if match else 0
        target = now + timedelta(hours=hours)
    elif "minute" in offset:
        match = re.search(r"\d+", offset)
        minutes = int(match.group()) if match else 0
        target = now + timedelta(minutes=minutes)
    else:
        target = now  # default fallback

    return {
        "hour": target.hour,
        "minute": target.minute,
        "iso": target.isoformat(),
        "pretty": target.strftime("%H:%M %p"),
    }


time_calc_tool = Tool(
    name="get_hour_from_offset",
    func=get_hour_from_offset,
    description="Returns the hour for a given time offset like 'now', 'in 2 hours', or 'in 30 minutes'"
)
system_tools.append(time_calc_tool)



def get_google_maps_link(place_name: str) -> str:
    query = """
    MATCH (n)
    WHERE toLower(n.name) CONTAINS toLower($name) AND n.coordinates IS NOT NULL
    RETURN n.coordinates AS coord, n.name AS name
    LIMIT 1
    """
    result = graph.query(query, params={"name": place_name})
    
    if not result:
        return f"Could not find coordinates for '{place_name}'."
    
    coord = result[0]['coord']
    longitude = coord.x
    latitude = coord.y

    maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"
    return f"**{place_name}** is located here: {maps_url}"





get_coordinates_tool = Tool.from_function(
    name="get_coordinates_google_maps",
    description="Get the Google Maps link for a location by its name (e.g., museum, beach, town).",
    func=get_google_maps_link
)

system_tools.append(get_coordinates_tool)



def search_top_video(item):
    query = f"{item} İzmir travel vlog site:youtube.com"
    return yt_tool.run(query)


def create_youtube_script(trip_plan: list):
    script = []
    for i, item in enumerate(trip_plan):
        intro = "Highlight:" if i == 0 else "Stop:"
        video_link = search_top_video(item)
        script.append(f"{intro} **{item}**\n Video: {video_link}")
    return "\n\n".join(script)


def safe_list_parser(input_str: str) -> list:
    try:
        result = ast.literal_eval(input_str)
        if isinstance(result, list):
            return result
        else:
            return [str(result)]
    except (ValueError, SyntaxError):
        return []


youtube_script_tool = Tool(
    name="generate_youtube_script",
    description="Given a list of İzmir travel items (places, activities, or landmarks), returns a vlog-style script with YouTube links for each.",
    func=lambda input_str: create_youtube_script(safe_list_parser(input_str)) 
)

system_tools.append(youtube_script_tool)

