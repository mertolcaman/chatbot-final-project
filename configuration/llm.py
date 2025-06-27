from langchain_openai import ChatOpenAI
import os

try:
    import streamlit as st
    openai_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    openai_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    openai_api_key=openai_key,
    temperature=0
)
