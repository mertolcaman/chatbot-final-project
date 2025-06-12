from langchain.agents import initialize_agent, AgentType
from configuration.llm import llm
from configuration.tool_config import tools

from configuration.prompt import agent_prompt



# Stateless agent (no memory)
test_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    agent_kwargs={
        "prompt": agent_prompt 
    }
)