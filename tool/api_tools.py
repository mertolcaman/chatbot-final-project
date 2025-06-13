from langchain.agents import Tool
import requests
from ast import literal_eval
from configuration.graph import graph
from math import radians, sin, cos, sqrt, atan2
import pandas as pd
import streamlit as st
from datetime import datetime
api_tools=[]






def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius of Earth in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c   # in km



def get_pharmacy_api_url():
    now = datetime.now()
    day = now.strftime("%A")
    hour = now.hour
    weekend = ["Saturday", "Sunday"]
    if day in weekend or (hour < 9 or hour >= 19):
        return "https://openapi.izmir.bel.tr/api/ibb/nobetcieczaneler"  # night
    return "https://openapi.izmir.bel.tr/api/ibb/eczaneler"  # day



def find_closest_pharmacy(user_lat: float, user_lon: float) -> str:
    try:
        url = get_pharmacy_api_url()
        response = requests.get(url)
        data = response.json()
    except Exception as e:
        return f"Failed to fetch data: {e}"

    df = pd.DataFrame(data)
    df = df[df["LokasyonX"].notnull() & df["LokasyonY"].notnull()]
    df["LokasyonX"] = df["LokasyonX"].astype(float)
    df["LokasyonY"] = df["LokasyonY"].astype(float)
    df["Address"] = df["Adres"]
    df["Name"] = df["Adi"]

    min_distance = float("inf")
    closest = {}

    for _, row in df.iterrows():
        dist = haversine(user_lat, user_lon, row["LokasyonX"], row["LokasyonY"])
        if dist < min_distance:
            min_distance = dist
            closest = {"name": row["Name"], 
                       "address": row["Address"], 
                       "distance": dist,
                       'lat':row["LokasyonX"],
                       'lon':row["LokasyonY"]
                       }

    if closest:
        label = "night" if "nobetci" in url else "daytime"
        maps_link = f"https://www.google.com/maps?q={closest['lat']},{closest['lon']}"
        direction = f"https://www.google.com/maps/dir/?api=1&origin={user_lat},{user_lon}&destination={closest['lat']},{closest['lon']}"
        return (
            f"The closest **{label} pharmacy** is **{closest['name']}**.\n"
            f"Address: {closest['address']}\n"
            f"Distance: {round(closest['distance'], 2)} km.",
            f"[Open in Google Maps]({maps_link})",
            f"[Get direction]({direction})"
            
        )
    return "No valid pharmacies found nearby."



def find_pharmacy_from_browser_location(_: str = "") -> str:
    loc = st.session_state.get("user_location")
    if not loc:
        return "User location is not available. Please allow location access."
    return find_closest_pharmacy(user_lat=loc["lat"], user_lon=loc["lon"])

find_pharmacy_tool = Tool(
    name="find_closest_pharmacy_near_me",
    description="Find the closest pharmacy using user's current browser location (supports both day & night based on time).",
    func=find_pharmacy_from_browser_location
)

api_tools.append(find_pharmacy_tool)





def find_closest_wifi_spot(user_lat: float, user_lon: float) -> str:
    try:
        response = requests.get("https://openapi.izmir.bel.tr/api/ibb/cbs/wizmirnetnoktalari")
        data = response.json()["onemliyer"]
    except Exception as e:
        return f"Failed to fetch Wi-Fi hotspot data: {e}"

    df = pd.DataFrame(data)
    df = df[df["ENLEM"].notnull() & df["BOYLAM"].notnull()]
    
    min_dist = float("inf")
    closest = {}

    for _, row in df.iterrows():
        dist = haversine(user_lat, user_lon, row["ENLEM"], row["BOYLAM"])
        if dist < min_dist:
            min_dist = dist
            closest = {
                "name": row["ADI"],
                "district": row["ILCE"],
                "neighborhood": row["MAHALLE"],
                "road": row["YOL"],
                "lat": row["ENLEM"],
                "lon": row["BOYLAM"],
                "distance": dist
            }

    if closest:
        maps_link = f"https://www.google.com/maps?q={closest['lat']},{closest['lon']}"
        direction = f"https://www.google.com/maps/dir/?api=1&origin={user_lat},{user_lon}&destination={closest['lat']},{closest['lon']}"

        return (
            f"The closest **Wi-Fi hotspot** is **{closest['name']}** \n"
            f"District: {closest['district']}, Neighborhood: {closest['neighborhood']}, Road: {closest['road']}\n"
            f"Distance: {round(closest['distance'], 2)} km",
            f"[Open in Google Maps]({maps_link})",
            f"[Get direction]({direction})"
        )
    return "No valid Wi-Fi hotspot found nearby."

def find_wifi_by_browser_location(_: str = "") -> str:
    loc = st.session_state.get("user_location")
    if not loc:
        return "User location is not available. Please allow location access."
    return find_closest_wifi_spot(user_lat=loc["lat"], user_lon=loc["lon"])

find_wifi_by_location_tool = Tool(
    name="find_closest_wifi_near_me",
    description="Find the nearest free Wi-Fi hotspot in İzmir using the user's current browser location.",
    func=find_wifi_by_browser_location
)

api_tools.append(find_wifi_by_location_tool)