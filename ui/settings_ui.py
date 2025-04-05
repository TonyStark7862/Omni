import streamlit as st
import os
from langchain.document_loaders import PyMuPDFLoader
from langchain.document_loaders import TextLoader
import autogen
from tools.utils import get_class_func_from_module, monitorFolder
from config import MODELS, AGENTS

Local_DIR = os.path.dirname(os.path.realpath(__file__))

monitored_files = monitorFolder(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'agents', 'agents_list'))

list_custom_Agent = []
for f in monitored_files:
    class_agent, _ = get_class_func_from_module(f)
    list_custom_Agent.extend(class_agent)

list_custom_Agent_names = [a[0] for a in list_custom_Agent]
AGENTS.extend(list_custom_Agent_names)

def llm_menu_cb():
    st.session_state.model = st.session_state.menu_model

def agent_menu_cb():
    st.session_state.agent = st.session_state.menu_agent

def prefixprompt_menu_cb():
    st.session_state.prefix = st.session_state.menu_prefixprompt

def suffixprompt_menu_cb():
    st.session_state.suffix = st.session_state.menu_suffixprompt

def planexec_menu_cb():
    st.session_state.plan_execute = st.session_state.menu_plan_exec

def empty_vdb():
    keys = list(st.session_state.doc_manager.documents.keys())
    for i, doc in enumerate(keys):
        st.session_state.doc_manager.remove_document(doc)
        if st.session_state.doc_manager.database:
            st.session_state.doc_manager.database.delete([st.session_state.doc_manager.database.index_to_docstore_id[i]])

def file_upload():
    with st.expander(label='Load documents', expanded=False):
        col1, col2 = st.columns([100, 92])
        
        uploaded_files = col1.file_uploader(
            "Embeddings Files",
            type=['txt', 'pdf'],
            accept_multiple_files=True
        )
        uploaded_files_workspace = col2.file_uploader(
            "Workspace Files",
            type=['txt', 'pdf', 'csv', 'png', 'jpg'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            load_files(uploaded_files)
        if uploaded_files_workspace:
            load_files_workspace(uploaded_files_workspace)
        
        col1.button('Empty document db', on_click=empty_vdb)
        if len(list(st.session_state.doc_manager.documents.keys())) > 0:
            col1.write('Documents loaded : \n' + str(list(st.session_state.doc_manager.documents.keys()))[1:-1])

@st.cache_data()
def load_file_workspace(file, workspace_dir):
    file_value = file.getvalue()
    with open(workspace_dir + str(file.name), 'wb') as f:
        f.write(file_value)

@st.cache_data()
def load_files(uploaded_files):
    for uploaded_file in uploaded_files:
        load_file(uploaded_file)
    
    st.session_state.doc_manager.create_embeddings_and_database()
    st.session_state.documents = st.session_state.doc_manager.list_documents()
    st.session_state.database = st.session_state.doc_manager.database
    st.success("Documents loaded and embeddings created.")

@st.cache_data()
def load_file(uploaded_file):
    if uploaded_file.type == 'application/pdf':
        temp_file_path = f"./temp_{uploaded_file.name}"
        with open(temp_file_path, mode='wb') as w:
            w.write(uploaded_file.getvalue())
        loader = PyMuPDFLoader(temp_file_path)
        doc_content = loader.load()
        st.session_state.doc_manager.add_document(uploaded_file.name, doc_content)
        os.remove(temp_file_path)

    if uploaded_file.type == 'text/plain':
        temp_file_path = f"./temp_{uploaded_file.name}"
        with open(temp_file_path, 'w') as f:
            f.write(uploaded_file.read().decode('utf-8'))
        loader = TextLoader(temp_file_path)
        doc_content = loader.load()
        st.session_state.doc_manager.add_document(uploaded_file.name, doc_content)
        os.remove(temp_file_path)

def settings_page():
    with st.expander(label='Settings', expanded=True):
        col1, col2 = st.columns(2)
        st.session_state.agent = col1.selectbox(
            "Select agent",
            options=AGENTS,
            key='menu_agent',
            on_change=agent_menu_cb,
            index=AGENTS.index(st.session_state.agent),
            help=Agent_Description[str(st.session_state.agent)]
        )
        st.session_state.model = col2.selectbox(
            "Select a model",
            options=MODELS,
            key='menu_model',
            on_change=llm_menu_cb,
            index=MODELS.index(st.session_state.model)
        )
        st.session_state.prefix = col1.text_area(
            'Prefix',
            key='menu_prefixprompt',
            on_change=prefixprompt_menu_cb,
            value=st.session_state.prefix,
            placeholder='First input for initial prompt'
        )
        st.session_state.suffix = col2.text_area(
            'Suffix',
            key='menu_suffixprompt',
            on_change=suffixprompt_menu_cb,
            value=st.session_state.suffix,
            placeholder='Last input for initial prompt'
        )

    file_upload()

    with st.expander(label='Experimental', expanded=False):
        col1, col2 = st.columns(2)
        st.session_state.plan_execute = col1.checkbox(
            'Plan and execute',
            key='menu_plan_exec',
            on_change=planexec_menu_cb,
            value=st.session_state.plan_execute
        )

    make_autogen_config()

def make_autogen_config():
    config_list = [{
        "model": st.session_state.model,
        "api_key": "not_needed"
    }]
    
    llm_config = {
        "config_list": config_list,
        "temperature": 0,
    }
    st.session_state.autogen_llm_config = llm_config

Agent_Description = {
    'AgentType.OPENAI_FUNCTIONS': "Uses function calling to determine which tool to use.",
    'AgentType.ZERO_SHOT_REACT_DESCRIPTION': "Uses ReAct framework based on tool description.",
    'AgentType.CONVERSATIONAL_REACT_DESCRIPTION': "Designed for conversational settings with memory.",
    'AgentType.SELF_ASK_WITH_SEARCH': "Uses single Intermediate Answer tool for factual lookups.",
    'AgentType.REACT_DOCSTORE': "Interacts with docstore using Search and Lookup tools.",
    'AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION': "Capable of using multi-input tools.",
}

# Add descriptions for custom agents
for ag in AGENTS:
    if str(ag) not in Agent_Description.keys():
        Agent_Description.update({str(ag): 'Custom agent'})
