import streamlit as st
from langchain.callbacks import StreamlitCallbackHandler
from agents.agent import AgentConfig
from storage.logger_config import logger
from .callbacks_ui import Custom_chat_callback, ToolCallback
from .settings_ui import list_custom_Agent
from config import SIMILARITY_MAX_DOC
from tools.utils import executecode

class StreamlitUI:
    def display_message(self, role, message):
        st.chat_message(role).write(message)

    def get_prompt(self):
        return st.chat_input()

    def make_callback(self):
        self.st_callbacks = [StreamlitCallbackHandler(st.container()), 
                           Custom_chat_callback(), 
                           ToolCallback()]

def initialize_chat_memory(session_id):
    st.session_state.memory.clear()
    if "session_id" in st.session_state:
        st.session_state.messages = st.session_state.storage.get_chat_history(st.session_state.session_id)
        for msg in st.session_state.messages:
            if msg["role"] == 'user':
                st.session_state.memory.chat_memory.add_user_message(msg["content"])
            else:
                st.session_state.memory.chat_memory.add_ai_message(msg["content"])

def configure_agent(_model, _agent, _tools, _chat_history, _memory, session_id, selected_tools_names):
    logger.info(f'Agent config for session {session_id} with model : {_model}, agent : {_agent}, tools : {_tools}')
    logger.debug(f'Agent config for session {session_id} with memory : {_memory}')
    if _agent in st.session_state.customAgentList:
        agt = list(filter(lambda x: x[0] == _agent, list_custom_Agent))[0]
        agent_config = agt[1]()
    else:
        agent_config = AgentConfig(_model, _agent, _tools, _chat_history, _memory)
    st.session_state.agent_instance = agent_config.initialize_agent()

def chat_page():
    st.session_state.chat_ui = StreamlitUI()
    s = ', '.join(st.session_state.selected_tools)
    st.info('Selected tools : ' + s)
    st.markdown("---")
    st.markdown("### 💭 Chat")
    st.markdown("---")

    initialize_chat_memory(st.session_state.session_id)
    configure_agent(
        st.session_state.model,
        st.session_state.agent,
        st.session_state.tools,
        st.session_state.chat_history,
        st.session_state.memory,
        st.session_state.session_id,
        st.session_state.selected_tools
    )

    if "session_id" in st.session_state:
        st.session_state.messages = st.session_state.storage.get_chat_history(st.session_state.session_id)
        for msg in st.session_state.messages:
            st.session_state.chat_ui.display_message(msg["role"], msg["content"])

    if prompt := st.session_state.chat_ui.get_prompt():
        original_prompt = prompt
        
        if st.session_state.database:
            similar_docs = st.session_state.database.similarity_search(prompt, k=SIMILARITY_MAX_DOC)
            if similar_docs:
                logger.info("Documents found : \n" + str(similar_docs))
                prompt = '\n Relevant documentation : \n' + similar_docs[0].page_content + '\n' + 'User prompt : \n ' + prompt
                for p in similar_docs:
                    logger.info(p.page_content)

        prompt = st.session_state.prefix + prompt + st.session_state.suffix
        st.session_state.chat_ui.display_message("user", original_prompt)
        logger.info('Input prompt : ' + prompt)

        with st.chat_message("assistant"):
            st.session_state.chat_ui.make_callback()
            response = st.session_state.agent_instance.run(
                input=prompt,
                callbacks=st.session_state.chat_ui.st_callbacks
            )

        logger.info('Chat response : ' + response)
        st.session_state.chat_ui.display_message("assistant", response)
        
        # Log to feedback tracker
        st.session_state.feedback_tracker.log_interaction(
            st.session_state.session_id,
            original_prompt,
            response,
            st.session_state.token_count
        )

        session_name = st.session_state.session_name.get(
            st.session_state.session_id,
            st.session_state.session_id
        )

        st.session_state.storage.save_chat_message(
            st.session_state.session_id,
            "user",
            original_prompt,
            session_name
        )
        st.session_state.storage.save_chat_message(
            st.session_state.session_id,
            "assistant",
            response,
            session_name
        )
        st.session_state.storage.save_session_name(
            st.session_state.session_id,
            session_name
        )

    if 'Code_sender' in st.session_state.selected_tools:
        try:
            with st.empty().container():
                with st.expander('Code'):
                    st.markdown('''```python \n ''' + st.session_state.executed_code[-1] + '''```''')
        except Exception as e:
            pass

    if st.session_state.autorun_state:
        try:
            executecode(st.session_state.executed_code[-1])
        except Exception as e:
            pass
