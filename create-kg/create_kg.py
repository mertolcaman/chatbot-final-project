import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from collections import defaultdict
from tqdm import tqdm
from langchain.embeddings import OpenAIEmbeddings
from langchain.graphs import Neo4jGraph


load_dotenv()
api_key_google = os.getenv("GOOGLE_MAPS")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



load_dotenv()
api_key_google = os.getenv("GOOGLE_MAPS")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#finding all json files
folder_path = "data_preparation/kg_database_data"
file_names = os.listdir(folder_path)

file_names = [
    folder_path + "/" + f
    for f in file_names
    if os.path.isfile(folder_path + "/" + f) and f.endswith(".json")
]


#String Response to JSON file conversion
def stringjson2json(output_text: str):
    """
    Extracts and parses a JSON array from an OpenAI LLM string output,
    which may contain markdown formatting, extra text, or surrounding commentary.

    Returns:
        - A parsed Python list/dictionary if successful
        - None if parsing fails
    """
    try:
        # Try to find the first code block starting with ```json
        if "```json" in output_text:
            start = output_text.find("```json") + len("```json")
            end = output_text.find("```", start)
            json_str = output_text[start:end].strip()
        elif "```" in output_text:  # Fallback to any code block
            start = output_text.find("```") + len("```")
            end = output_text.find("```", start)
            json_str = output_text[start:end].strip()
        else:
            json_str = output_text.strip()

        # Parse the JSON string
        parsed = json.loads(json_str)

        return parsed

    except Exception as e:
        print("JSON Parse Error:", e)
        return None
    

#get json file and convert string into json
def file2json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()
        return stringjson2json(raw_text)
    

foods       = file2json(file_names[0]) #contains only foods
merged_places       = file2json(file_names[1]) #contains all places such as Town, Beach, Museum etc.
print("Files have been read.")

#CREATING KNOWLEDGE GRAPH
def normalize_name(name: str) -> str:
    translation_table = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    return name.translate(translation_table).lower().strip().title()


# Initialize embedding
embedding_provider = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model="text-embedding-ada-002"
)


# Get embedding function
def get_embedding(text: str):
    return embedding_provider.embed_query(text)

graph = Neo4jGraph(
    url=os.getenv('NEO4J_URI'),
    username=os.getenv('NEO4J_USERNAME'),
    password=os.getenv('NEO4J_PASSWORD')
)

def drop_all_indexes(graph):
    indexes = graph.query("SHOW INDEXES YIELD name AS idx_name RETURN idx_name")
    for row in indexes:
        index_name = row["idx_name"]
        try:
            graph.query(f"DROP INDEX `{index_name}` IF EXISTS")
            print(f"Dropped index: {index_name}")
        except Exception as e:
            print(f"Failed to drop index `{index_name}`: {e}")


#cleaning database
def reset_neo4j_database(graph):
    print("Deleting all nodes and relationships...")
    graph.query("MATCH (n) DETACH DELETE n")

    print("Dropping all indexes...")
    drop_all_indexes(graph)

    print("Dropping all constraints...")
    graph.query("""
    CALL db.constraints() YIELD name
    CALL db.dropConstraint(name, {ifExists: true})
    YIELD name RETURN name
    """)

    print("Neo4j database reset complete.")


#setup vector indexes
# def setup_all_vector_indexes(graph):
#     # --- MUSEUM ---
#     graph.query("""
#     CREATE VECTOR INDEX embeddingDescriptionMuseum
#     IF NOT EXISTS
#     FOR (m:Museum) ON (m.embedding_description_museum)
#     OPTIONS {
#         indexConfig: {
#             `vector.dimensions`: 1536,
#             `vector.similarity_function`: 'cosine'
#         }
#     }
#     """)

#     graph.query("""
#     CREATE VECTOR INDEX embeddingAudienceMuseum
#     IF NOT EXISTS
#     FOR (a:Audience) ON (a.embedding_audience_museum)
#     OPTIONS {
#         indexConfig: {
#             `vector.dimensions`: 1536,
#             `vector.similarity_function`: 'cosine'
#         }
#     }
#     """)

#     graph.query("""
#     CREATE VECTOR INDEX embeddingConceptMuseum
#     IF NOT EXISTS
#     FOR (c:Concept) ON (c.embedding_concept_museum)
#     OPTIONS {
#         indexConfig: {
#             `vector.dimensions`: 1536,
#             `vector.similarity_function`: 'cosine'
#         }
#     }
#     """)

#     graph.query("""
#     CREATE VECTOR INDEX embeddingFacilityMuseum
#     IF NOT EXISTS
#     FOR (f:Facility) ON (f.embedding_facility_museum)
#     OPTIONS {
#         indexConfig: {
#             `vector.dimensions`: 1536,
#             `vector.similarity_function`: 'cosine'
#         }
#     }
#     """)

#     # --- PLACES ---
#     graph.query("""
#     CREATE VECTOR INDEX embeddingDescriptionPlaces
#     IF NOT EXISTS
#     FOR (p:City) ON (p.embedding_description_places)
#     OPTIONS {
#         indexConfig: {
#             `vector.dimensions`: 1536,
#             `vector.similarity_function`: 'cosine'
#         }
#     }
#     """)

#     graph.query("""
#     CREATE VECTOR INDEX embeddingAudiencePlaces
#     IF NOT EXISTS
#     FOR (a:Audience) ON (a.embedding_audience_places)
#     OPTIONS {
#         indexConfig: {
#             `vector.dimensions`: 1536,
#             `vector.similarity_function`: 'cosine'
#         }
#     }
#     """)

#     graph.query("""
#     CREATE VECTOR INDEX embeddingConceptPlaces
#     IF NOT EXISTS
#     FOR (c:Concept) ON (c.embedding_concept_places)
#     OPTIONS {
#         indexConfig: {
#             `vector.dimensions`: 1536,
#             `vector.similarity_function`: 'cosine'
#         }
#     }
#     """)

#     # --- FOODS ---
#     graph.query("""
#     CREATE VECTOR INDEX embeddingDescriptionFoods
#     IF NOT EXISTS
#     FOR (f:Food) ON (f.embedding_description_foods)
#     OPTIONS {
#         indexConfig: {
#             `vector.dimensions`: 1536,
#             `vector.similarity_function`: 'cosine'
#         }
#     }
#     """)

#     graph.query("""
#     CREATE VECTOR INDEX embeddingFoodType
#     IF NOT EXISTS
#     FOR (ft:FoodType) ON (ft.embedding_foodtype)
#     OPTIONS {
#         indexConfig: {
#             `vector.dimensions`: 1536,
#             `vector.similarity_function`: 'cosine'
#         }
#     }
#     """)

#     graph.query("""
#     CREATE VECTOR INDEX embeddingIngredient
#     IF NOT EXISTS
#     FOR (i:Ingredient) ON (i.embedding_ingredient)
#     OPTIONS {
#         indexConfig: {
#             `vector.dimensions`: 1536,
#             `vector.similarity_function`: 'cosine'
#         }
#     }
#     """)


LABEL_EMBEDDING_INDEX_MAP = {
    "Museum": ("embedding_description_museum", "embeddingDescriptionMuseum"),
    "Audience": ("embedding_audience", "embeddingAudience"),
    "Concept": ("embedding_concept", "embeddingConcept"),
    "Facility": ("embedding_facility", "embeddingFacility"),
    "City": ("embedding_description_city", "embeddingDescriptionCity"),
    "Town": ("embedding_description_town", "embeddingDescriptionTown"),
    "Beach": ("embedding_description_beach", "embeddingDescriptionBeach"),
    "Bay": ("embedding_description_bay", "embeddingDescriptionBay"),
    "Island": ("embedding_description_island", "embeddingDescriptionIsland"),
    "Village": ("embedding_description_village", "embeddingDescriptionVillage"),
    "Castle": ("embedding_description_castle", "embeddingDescriptionCastle"),
    "Historicalsite": ("embedding_description_historicalsite", "embeddingDescriptionHistorical"),
    "Culturalsite": ("embedding_description_culturalsite", "embeddingDescriptionCultural"),
    "Ancientcity": ("embedding_description_ancientcity", "embeddingDescriptionAncient"),
    "Temple": ("embedding_description_temple", "embeddingDescriptionTemple"),
    "Monument": ("embedding_description_monument", "embeddingDescriptionMonument"),
    "Religiousplace": ("embedding_description_religiousplace", "embeddingDescriptionReligious"),
    "Naturalpark": ("embedding_description_naturalpark", "embeddingDescriptionNatural"),
    "Market": ("embedding_description_market", "embeddingDescriptionMarket"),
    "Tower": ("embedding_description_tower", "embeddingDescriptionTower"),
    "Landmark": ("embedding_description_landmark", "embeddingDescriptionLandmark"),
    "Food": ("embedding_description_food", "embeddingDescriptionFood"),
    "FoodType": ("embedding_foodtype", "embeddingFoodType"),
    "Ingredient": ("embedding_ingredient", "embeddingIngredient"),
}

def setup_all_vector_indexes(graph):
    for label, (property_name, index_name) in LABEL_EMBEDDING_INDEX_MAP.items():
        graph.query(f"""
        CREATE VECTOR INDEX {index_name}
        IF NOT EXISTS
        FOR (n:{label}) ON (n.{property_name})
        OPTIONS {{
            indexConfig: {{
                `vector.dimensions`: 1536,
                `vector.similarity_function`: 'cosine'
            }}
        }}
        """)

def insert_places(graph, places):
    for place in tqdm(places):
        name = place["mention"].title()
        label = place["node_type"].title()
        description = place.get("description", "")
        embedding_description = get_embedding(description)

        coordinates = place.get("coordinates")
        try:
            lat, lon = (float(coordinates[0]), float(coordinates[1])) if coordinates else (None, None)
        except (TypeError, ValueError, IndexError):
            lat, lon = None, None

        located_in = place.get("located_in", "").strip().title()
        best_for = place.get("best_for", [])
        properties = place.get("properties", [])

        # Get correct embedding property
        embedding_property = LABEL_EMBEDDING_INDEX_MAP.get(label, ("embedding_description_generic",))[0]

        # Merge node and set vector
        graph.query(f"""
        MERGE (p:{label} {{name: $name}})
        SET p.description = $description,
            p.coordinates = point({{latitude: $lat, longitude: $lon}})
        WITH p
        CALL db.create.setNodeVectorProperty(p, '{embedding_property}', $embedding_description)
        """, {
            "name": name,
            "description": description,
            "lat": lat,
            "lon": lon,
            "embedding_description": embedding_description
        })

        # LOCATED_IN relationship
        if located_in:
            loc_label = "City" if located_in == "Izmir" else "Town"
            graph.query(f"""
            MERGE (p:{loc_label} {{name: $parent}})
            MERGE (m:{label} {{name: $name}})
            MERGE (m)-[:LOCATED_IN]->(p)
            """, {
                "name": name,
                "parent": located_in
            })

        # BEST_FOR → Audience
        for audience in best_for:
            embedding_audience = get_embedding(audience)
            graph.query(f"""
            MERGE (a:Audience {{name: $audience}})
            WITH a
            CALL db.create.setNodeVectorProperty(a, 'embedding_audience', $embedding_audience)
            MATCH (p:{label} {{name: $name}})
            MERGE (p)-[:BEST_FOR]->(a)
            """, {
                "audience": audience.lower().capitalize(),
                "name": name,
                "embedding_audience": embedding_audience
            })

        # HAS_CONCEPT → Concept (from properties)
        for concept in properties:
            embedding_concept = get_embedding(concept)
            graph.query(f"""
            MERGE (c:Concept {{name: $concept}})
            WITH c
            CALL db.create.setNodeVectorProperty(c, 'embedding_concept', $embedding_concept)
            MATCH (p:{label} {{name: $name}})
            MERGE (p)-[:HAS_CONCEPT]->(c)
            """, {
                "concept": concept.lower().capitalize(),
                "name": name,
                "embedding_concept": embedding_concept
            })


def insert_museum(graph, places):
    for place in tqdm(places):
        label = place["node_type"].capitalize()
        if label == "Museum":
            name = place["mention"].title().strip()   
            located_in = place.get("located_in", "").strip().title()

            best_for = place.get("best_for", [])
            properties = place.get("properties", [])
            description = place.get("description", "")

            embedding_description = get_embedding(description)
            
            
            coords = place.get("coordinates")
            
            #some coordinates are not in a list
            if isinstance(coords, str):
                lat, lon = [float(x.strip()) for x in coords.split(",")]
            else:
                lat, lon = float(coords[0]), float(coords[1])
                
                
            rating = place.get("rating")
            facilities = place.get("facilities", [])

            # Extract individual properties from the 'information' dictionary
            address = place.get("address", "")
            email = place.get("email", "")
            phone = place.get("phone", "")


            # storing as separate properties for summer/winter.
            opening_hours_data = place.get("opening_hours", {}) # Default to an empty dictionary if not present

            opening_hours_summer = opening_hours_data.get("summer", "")
            opening_hours_winter = opening_hours_data.get("winter", "")

            images = place.get("images", []) # This is a list of strings, which is fine
            local_price = place.get("local_price", "")
            foreigner_price = place.get("foreigner_price", "")

            # Merge Museum node with flattened properties
            graph.query("""
            MERGE (m:Museum {name: $name})
            SET m.description = $description,
                m.coordinates = point({latitude: $lat, longitude: $lon}),
                m.rating = $rating,
                m.address = $address,
                m.email = $email,
                m.phone = $phone,
                m.opening_hours_summer = $opening_hours_summer,
                m.opening_hours_winter = $opening_hours_winter,
                m.images = $images,
                m.local_price = $local_price,
                m.foreigner_price = $foreigner_price
            WITH m
            CALL db.create.setNodeVectorProperty(m, 'embedding_description_museum', $embedding_description)
            """, {
                "name": name,
                "description": description,
                "lat": lat,
                "lon": lon,
                "rating": rating,
                "address": address,
                "email": email,
                "phone": phone,
                "opening_hours_summer": opening_hours_summer,
                "opening_hours_winter": opening_hours_winter,
                "images": images,
                "local_price": local_price,
                "foreigner_price": foreigner_price,
                "embedding_description": embedding_description
            })

            # The rest of the relationships (LOCATED_IN, BEST_FOR, HAS_CONCEPT, HAS_FACILITY)
            
            if located_in=="Izmir": loc_node="Izmir"
            else: loc_node = "Town"
            # LOCATED_IN relationship
            if located_in:
                graph.query(f"""
                MERGE (l:{loc_node} {{name: $parent}})
                MERGE (m:Museum {{name: $name}})
                MERGE (m)-[:LOCATED_IN]->(l)
                """, {"name": name, "parent": located_in})

            # BEST_FOR → Audience
            for audience in best_for:
                embedding_audience = get_embedding(audience)
                
                graph.query("""
                MERGE (a:Audience {name: $audience})
                WITH a
                CALL db.create.setNodeVectorProperty(a, 'embedding_audience_museum', $embedding_audience)
                MATCH (m:Museum {name: $name})
                MERGE (m)-[:BEST_FOR]->(a)
                """, {"audience": audience.lower().capitalize(), "name": name,"embedding_audience": embedding_audience})

            # HAS_CONCEPT → Concept (from properties)
            for concept in properties:
                embedding_concept = get_embedding(concept)
                
                graph.query("""
                MERGE (c:Concept {name: $concept})
                WITH c
                CALL db.create.setNodeVectorProperty(c, 'embedding_concept_museum', $embedding_concept)
                MATCH (m:Museum {name: $name})
                MERGE (m)-[:HAS_CONCEPT]->(c)
                """, {"concept": concept.lower().capitalize(), "name": name, "embedding_concept": embedding_concept})

            # HAS_FACILITY → Facility
            for facility in facilities:
                embedding_facility = get_embedding(facility)
                
                graph.query("""
                MERGE (f:Facility {name: $facility})
                WITH f
                CALL db.create.setNodeVectorProperty(f, 'embedding_facility_museum', $embedding_facility)
                MATCH (m:Museum {name: $name})
                MERGE (m)-[:HAS_FACILITY]->(f)
                """, {"facility": facility.lower().capitalize(), "name": name, "embedding_facility":embedding_facility})


# def insert_places(graph,places):
#     for place in tqdm(places):
#         name = place["mention"].title()
#         label = place["node_type"].title()
#         description = place.get("description", "")
#         embedding_description = get_embedding(description)

#         coordinates = place.get("coordinates")
# #         lat, lon = coordinates if coordinates else (None, None)
#         try:
#             lat, lon = (float(coordinates[0]), float(coordinates[1])) if coordinates else (None, None)
#         except (TypeError, ValueError, IndexError):
#             lat, lon = None, None
            
#         located_in = place.get("located_in", "").title()
#         best_for = place.get("best_for", [])
#         properties = place.get("properties", [])

#         if label == "City": #which means Izmir node
            
#             # Merge City node with flattened properties
#             graph.query("""
#             MERGE (p:City {name: $name})
#             SET p.description = $description,
#                 p.coordinates = point({latitude: $lat, longitude: $lon})
#             WITH p
#             CALL db.create.setNodeVectorProperty(p, 'embedding_description_places', $embedding_description)
#             """, {
#                 "name": name,
#                 "description": description,
#                 "lat": lat,
#                 "lon": lon,
#                 "embedding_description": embedding_description
#             })
            
#         else:
#             # Merge the node with flattened properties
#             # Use f-string to inject the label dynamically, keep property map with single braces as Langchain might handle
#             graph.query(f"""
#             MERGE (p:{label} {{name: $name}})
#             SET p.description = $description,
#                 p.coordinates = point({{latitude: $lat, longitude: $lon}})
#             WITH p
#             CALL db.create.setNodeVectorProperty(p, 'embedding_description_places', $embedding_description)
#             """, {
#                 "name": name,
#                 "description": description,
#                 "lat": lat,
#                 "lon": lon,
#                 "embedding_description": embedding_description
#             })
            
#             if located_in=="Izmir": #only city is Izmir
#                 loc_label = "City"
#             else: loc_label="Town"
            
#             # LOCATED_IN relationship
#             if located_in:
#                 graph.query(f"""
#                 MERGE (p:{loc_label} {{name: $parent}})
#                 MERGE (m:{label} {{name: $name}})
#                 MERGE (m)-[:LOCATED_IN]->(p)
#                 """, {
#                     "name": name,
#                     "parent": located_in
#                 })
                
                

#         # Relationships (handled outside if-else so they work for all nodes)
#         if label != "Museum":
#             # BEST_FOR → Audience
#             for audience in best_for:
#                 embedding_audience = get_embedding(audience)
                
#                 graph.query(f"""
#                 MERGE (a:Audience {{name: $audience}})
#                 WITH a
#                 CALL db.create.setNodeVectorProperty(a, 'embedding_audience_places', $embedding_audience)
#                 MATCH (p:{label} {{name: $name}})
#                 MERGE (p)-[:BEST_FOR]->(a)
#                 """, {
#                     "audience": audience.lower().capitalize(),
#                     "name": name,
#                     "embedding_audience": embedding_audience
#                 })

#             # HAS_CONCEPT → Concept (from properties)
#             for concept in properties:
#                 embedding_concept = get_embedding(concept)
                
#                 graph.query(f"""
#                 MERGE (c:Concept {{name: $concept}})
#                 WITH c
#                 CALL db.create.setNodeVectorProperty(c, 'embedding_concept_places', $embedding_concept)
#                 MATCH (p:{label} {{name: $name}})
#                 MERGE (p)-[:HAS_CONCEPT]->(c)
#                 """, {
#                     "concept": concept.lower().capitalize(),
#                     "name": name,
#                     "embedding_concept": embedding_concept
#                 })


def insert_foods(graph, foods):
    for food in tqdm(foods):
        name = food["mention"].lower().capitalize()
        food_type = food["type"].lower().capitalize()
        description = food.get("description", "")
        coordinates = food.get("coordinates")
        lat, lon = (coordinates[0], coordinates[1]) if coordinates else (None, None)
        ingredients = food.get("ingredients", [])
        where_to_eat = food.get("where_to_eat", [])

        embedding_description = get_embedding(description)
        
        # Create/Merge the Food node
        graph.query(f"""
            MERGE (f:Food {{name: $name}})
            SET f.description = $description,
                f.coordinates = point({{latitude: $lat, longitude: $lon}})
            WITH f
            CALL db.create.setNodeVectorProperty(f, 'embedding_description_foods', $embedding_description)
        """, {
            "name": name,
            "description": description,
            "lat": lat,
            "lon": lon,
            "embedding_description": embedding_description
        })

        # Create/Merge the FoodType node and link it
        if food_type:
            embedding_foodtype = get_embedding(food_type)
            
            graph.query(f"""
                MERGE (ft:FoodType {{name: $food_type}})
                WITH ft
                CALL db.create.setNodeVectorProperty(ft, 'embedding_foodtype', $embedding_foodtype)
                MATCH (f:Food {{name: $name}})
                MERGE (f)-[:TYPE_OF]->(ft)
            """, {
                "food_type": food_type,
                "name": name,
                "embedding_foodtype": embedding_foodtype
            })

        # Create/Merge Ingredient nodes and link them
        for ingredient in ingredients:
            ingredient_name = ingredient.lower().capitalize()
            
            embedding_ingredient = get_embedding(ingredient)
            
            graph.query(f"""
                MERGE (i:Ingredient {{name: $ingredient_name}})
                WITH i
                CALL db.create.setNodeVectorProperty(i, 'embedding_ingredient', $embedding_ingredient)
                MATCH (f:Food {{name: $name}})
                MERGE (f)-[:HAS_INGREDIENT]->(i)
            """, {
                "ingredient_name": ingredient_name,
                "name": name,
                "embedding_ingredient": embedding_ingredient
            })
        
        # Create/Merge Location nodes (where_to_eat) and link them
        for location in where_to_eat:
            location_name = location.strip().title()
            if location_name=="Izmir": loc_node="City"
            else: loc_node = "Town"
            # Assuming 'where_to_eat' typically refers to a Location, e.g., a district or specific place
            graph.query(f"""
                MERGE (l:{loc_node} {{name: $location_name}})
                WITH l
                MATCH (f:Food {{name: $name}})
                MERGE (f)-[:POPULAR_IN]->(l)
            """, {
                "location_name": location_name,
                "name": name
            })








# Connecting all town nodes not connected to another town, connect to Izmir (city) node
def connect_unlocated_places_to_izmir(graph):
    """
    Connects Town (and optionally other specific Place types like Bay, Beach)
    nodes that do not have an outgoing LOCATED_IN relationship to the
    'Izmir' City node.

    Args:
        graph: The Neo4jGraph object connected to your Neo4j database.
    """
    print("Connecting unlocated places to Izmir City node...")

    cypher_query = """
    // 1. Ensure the 'Izmir' City node exists (idempotent)
    MERGE (izmir:City {name: 'Izmir'})

    // 2. Find all Town (or other relevant labels) nodes that do NOT have an outgoing LOCATED_IN relationship
    WITH izmir
    MATCH (p)
    WHERE (p:Town OR p:Bay OR p:Beach) // Adjust labels as needed for your schema
      AND NOT (p)-[:LOCATED_IN]->()

    // 3. MERGE the LOCATED_IN relationship from these places to Izmir
    MERGE (p)-[:LOCATED_IN]->(izmir)

    RETURN count(p) AS PlacesConnectedToIzmir
    """

    try:
        # The graph.query method typically returns a list of records.
        # We expect one record with the count.
        result = graph.query(cypher_query)
        
        # Access the count from the result
        if result and isinstance(result, list) and len(result) > 0 and 'PlacesConnectedToIzmir' in result[0]:
            connected_count = result[0]['PlacesConnectedToIzmir']
            print(f"Successfully connected {connected_count} places to Izmir City node.")
        else:
            print("Query executed, but no count returned or result format unexpected.")
            print(f"Raw query result: {result}")

    except Exception as e:
        print(f"An error occurred while connecting unlocated places: {e}")            


print("Vector indexes are being created...")
setup_all_vector_indexes(graph)
print("Vector indexes have been created.")


print("Museum nodes and relationships with embeddings are being created...")
insert_museum(graph, merged_places)
print("Museum nodes and relationships have been added.")

print("Food nodes and relationships with embeddings are being created...")
insert_foods(graph,foods)
print("Food nodes and relationships have been added.")

print("Place nodes and relationships with embeddings are being created...")
insert_places(graph, merged_places)
print("Place nodes and relationships have been added.")


connect_unlocated_places_to_izmir(graph)
print("not connected towns have been connected to Izmir.")