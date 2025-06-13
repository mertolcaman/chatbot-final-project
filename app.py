import streamlit as st
import uuid
import requests
from datetime import datetime
from urllib.parse import parse_qs
from chat import product_agent  
from langchain_core.messages import HumanMessage, AIMessage
from memory.memory_store import get_memory
from utils.streamlit_callbacks import StreamlitActionTracker

st.set_page_config(page_title="İzmir Travel Assistant", layout="wide")
st.title("🧳 İzmir Smart Travel Assistant")

# --- Inject JS for user geolocation ---
st.markdown("""
<script>
navigator.geolocation.getCurrentPosition(
    function(position) {
        const coords = position.coords.latitude + "," + position.coords.longitude;
        if (!window.location.search.includes("coords=")) {
            window.location.search = "?coords=" + coords;
        }
    }
);
</script>
""", unsafe_allow_html=True)

# --- Parse geolocation from URL ---
params = st.query_params
if "lat" in params and "lon" in params:
    try:
        st.session_state["user_location"] = {
            "lat": float(params["lat"]),
            "lon": float(params["lon"])
        }
        st.success(f"📍 Location set to {params['lat']}, {params['lon']}")
    except:
        st.warning("Invalid location coordinates in query params.")


# --- Session ID ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Optional: Let user override session ID
st.text_input("Session ID:", key="session_id")

# --- Message history ---
if "messages" not in st.session_state:
    history = get_memory(st.session_state.session_id)
    st.session_state.messages = []

    for msg in history.messages:
        if isinstance(msg, HumanMessage):
            st.session_state.messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            st.session_state.messages.append({"role": "assistant", "content": msg.content})

    if not st.session_state.messages:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am smart assistant for Izmir. How can I help you?"}]

# --- Display chat history ---
def render_message(role, content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with st.chat_message(role):
        st.markdown(f"**{role.capitalize()}** ({timestamp})")
        st.markdown(content)

for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])

# --- Chat input ---
if prompt := st.chat_input("Ask something about İzmir"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_message("user", prompt)

    tool_placeholder = st.empty()
    tracker = StreamlitActionTracker(tool_placeholder)

    with st.spinner("Thinking..."):
        response = product_agent.invoke(
            {"input": prompt},
            config={
                "configurable": {"session_id": st.session_state.session_id},
                "callbacks": [tracker],
            }
        )

    output = response.get("output", "")
    tool_used = tracker.last_tool_used or "Unknown Agent"
    agent_display = f"🧠 Response generated using: `{tool_used}`"

    st.session_state.messages.append({"role": "assistant", "content": f"{output}\n\n{agent_display}"})
    render_message("assistant", f"{output}\n\n{agent_display}")

# --- Reset chat ---
if st.button("Clear Conversation"):
    st.session_state.messages = []

st.markdown("""
You can manually set your location by adding `?lat=38.29&lon=26.37` to the URL.
Or pass it directly: [Set location to Alacati](?lat=38.29&lon=26.37)
""")