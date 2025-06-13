# # from rag.retrieval_chain import get_rag_chain
# # from configuration.graph import graph
# # query = "I would like to eat something sweet."
# # category = "food"  # or "castle", "city", etc.

# # rag_chain = get_rag_chain(category)
# # result = rag_chain.invoke({"input": query})
# # print(result["answer"])


# # full_schema = graph.get_schema
# # print(full_schema)



# import pandas as pd
# # from IPython.display import display

# # Define the node types and their properties
# node_data = [
#     ("Museum", ["embedding_description_museum", "name", "description", "coordinates", "address", "email", "phone", "opening_hours_summer", "opening_hours_winter", "images", "local_price", "foreigner_price", "rating"]),
#     ("Audience", ["embedding_audience", "name", "embedding_audience_museum"]),
#     ("Concept", ["embedding_concept", "name", "embedding_concept_museum"]),
#     ("Facility", ["name", "embedding_facility_museum"]),
#     ("City", ["embedding_description_city", "name", "description", "coordinates"]),
#     ("Town", ["embedding_description_town", "name", "description", "coordinates"]),
#     ("Beach", ["embedding_description_beach", "name", "description", "coordinates"]),
#     ("Bay", ["embedding_description_bay", "name", "description", "coordinates"]),
#     ("Island", ["embedding_description_island", "name", "description", "coordinates"]),
#     ("Village", ["embedding_description_village", "name", "description", "coordinates"]),
#     ("Castle", ["embedding_description_castle", "name", "description", "coordinates"]),
#     ("Historicalsite", ["embedding_description_historicalsite", "name", "description", "coordinates"]),
#     ("Culturalsite", ["embedding_description_culturalsite", "name", "description", "coordinates"]),
#     ("Ancientcity", ["embedding_description_ancientcity", "name", "description", "coordinates"]),
#     ("Temple", ["embedding_description_temple", "name", "description", "coordinates"]),
#     ("Monument", ["embedding_description_monument", "name", "description", "coordinates"]),
#     ("Religiousplace", ["embedding_description_religiousplace", "name", "description", "coordinates"]),
#     ("Naturalpark", ["embedding_description_naturalpark", "name", "description", "coordinates"]),
#     ("Market", ["embedding_description_market", "name", "description", "coordinates"]),
#     ("Tower", ["embedding_description_tower", "name", "description", "coordinates"]),
#     ("Landmark", ["embedding_description_landmark", "name", "description", "coordinates"]),
#     ("Food", ["name", "description", "coordinates", "embedding_description_foods"]),
#     ("FoodType", ["embedding_foodtype", "name"]),
#     ("Ingredient", ["embedding_ingredient", "name"]),
# ]

# # Convert to DataFrame for tabular display
# df_nodes = pd.DataFrame([
#     {"Node Type": label, "Properties": ", ".join(props)}
#     for label, props in node_data
# ])

# print(pd.DataFrame(df_nodes))
# # import ace_tools as tools; tools.display_dataframe_to_user(name="Node Properties Table", dataframe=df_nodes)


# import pandas as pd
# import requests
# from geopy.distance import geodesic
# from math import radians, sin, cos, sqrt, atan2

# response = requests.get("https://openapi.izmir.bel.tr/api/ibb/nobetcieczaneler")
# data = response.json()

# df = pd.DataFrame(data)

# # Filter out those with valid coordinates
# df = df[df["LokasyonX"].notnull() & df["LokasyonY"].notnull()]

# # Convert coordinates to float
# df["LokasyonX"] = df["LokasyonX"].astype(float)
# df["LokasyonY"] = df["LokasyonY"].astype(float)
# df["Address"] = df["Adres"]
# df["Name"] = df["Adi"]




# def haversine(lat1, lon1, lat2, lon2):
#     R = 6371.0  # Earth radius in kilometers

#     dlat = radians(lat2 - lat1)
#     dlon = radians(lon2 - lon1)

#     a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
#     c = 2 * atan2(sqrt(a), sqrt(1 - a))

#     return R * c * 1000


# loc_x, loc_y = df["LokasyonX"][0], df["LokasyonY"][0]
# user_x,user_y= 38.299245, 26.374194

# def find_the_closest_location(user_x,user_y, loc_x, loc_y, loc_address, loc_name):
#     min_name = ""
#     min_address = ""
#     min_distance= 9999999999999999
#     for lat, lon, address, name in zip(loc_x, loc_y, loc_address, loc_name):
#         distance = haversine(lat,lon, user_x,user_y)
#         if distance < min_distance:
#             min_address = address
#             min_distance = distance 
#             min_name = name
#     return {
#         "name": min_name,
#         "adress": min_address,
#         "distance_m": min_distance
#     }



# pharmacy_info= find_the_closest_location(user_x,user_y,df["LokasyonX"],df["LokasyonY"], df["Address"], df["Name"])
# print(pharmacy_info)
# print(f"The closes pharmacy is {pharmacy_info["name"]}. It is located in {round(pharmacy_info["distance_m"],2)}m away. The address is {pharmacy_info["adress"]}")


from datetime import datetime, timedelta

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

now = datetime.now()
week_day= now.strftime("%A")
hour = now.hour
weekend = ["Saturday", "Sunday"]
# if now.strftime("%A") in weekend or (now.hour<9 and now. :
#     print("True")
print(now.strftime("%A"))
print(now.minute)
