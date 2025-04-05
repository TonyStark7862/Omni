import streamlit as st
from langchain.prompts import MessagesPlaceholder
from langchain.agents import AgentType, initialize_agent
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from storage.logger_config import logger
from config import MAX_ITERATIONS, TEMPERATURE
from ui.callbacks_ui import Custom_chat_callback, ToolCallback
from custom_llm import abc_response  # You'll provide this

class CustomLLM:
    def __init__(self):
        self.temperature = TEMPERATURE
    
    def predict(self, prompt: str) -> str:
        return abc_response(prompt)
    
    def get_num_tokens(self, text: str) -> int:
        # Implement token counting if needed
        return len(text.split())

class AgentConfig:
    def __init__(self, model, agent_type, tools, chat_history, memory):
        self.llm = CustomLLM()
        self.agent_type = agent_type
        self.tools = tools
        self.chat_history = chat_history
        self.memory = memory

        if st.session_state.plan_execute:
            self.planner = load_chat_planner(self.llm)
            self.executor = load_agent_executor(self.llm, tools, include_task_in_prompt=True)

    def _handle_error(self, error):
        return f'Error in agent execution: \n {error}'

    def initialize_agent(self):
        input_variables = ["input", "agent_scratchpad", "chat_history"]
        if self.agent_type in [AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, 
                             AgentType.ZERO_SHOT_REACT_DESCRIPTION]:
            input_variables = ["input", "agent_scratchpad"]

        agent_kwargs = {
            "extra_prompt_messages": [self.chat_history],
            "memory_prompts": [self.chat_history],
            "input_variables": input_variables,
        }

        if st.session_state.plan_execute:
            return PlanAndExecute(
                planner=self.planner,
                executor=self.executor,
                memory=self.memory,
                agent_kwargs=agent_kwargs,
                verbose=True,
                handle_parsing_errors=True
            )
        else:
            return initialize_agent(
                self.tools,
                self.llm,
                agent=self.agent_type,
                verbose=True,
                memory=self.memory,
                agent_kwargs=agent_kwargs,
                max_iterations=MAX_ITERATIONS,
                streaming=True,
                handle_parsing_errors=self._handle_error,
            )
