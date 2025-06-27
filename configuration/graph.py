from langchain_neo4j import Neo4jGraph
import os

try:
    import streamlit as st
    uri = st.secrets["NEO4J_URI"]
    username = st.secrets["NEO4J_USERNAME"]
    password = st.secrets["NEO4J_PASSWORD"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

graph = Neo4jGraph(
    url=uri,
    username=username,
    password=password,
)
