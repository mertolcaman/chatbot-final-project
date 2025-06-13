from langchain.callbacks.base import BaseCallbackHandler

class StreamlitActionTracker(BaseCallbackHandler):
    def __init__(self, placeholder):
        self.placeholder = placeholder
        self.last_tool_used = None

    def on_agent_action(self, action, **kwargs):
        tool_name = action.tool  
        tool_input = action.tool_input
        self.last_tool_used = tool_name  
        self.placeholder.markdown(
            f"🤖 Agent decided to use: `{tool_name}`\n\n**Input:** {tool_input}"
        )
