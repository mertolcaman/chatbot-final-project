from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.runnables import RunnableWithMessageHistory
from memory.memory_store import get_memory 
from configuration.llm import llm
from configuration.tool_config import tools
from configuration.prompt import agent_prompt


# Agent with memory for conversational interactions
react_agent = create_react_agent(llm, tools, agent_prompt)
executor = AgentExecutor(agent=react_agent, tools=tools, verbose=True)

product_agent = RunnableWithMessageHistory(
    executor,
    get_memory, 
    input_messages_key="input",
    history_messages_key="chat_history",
)



