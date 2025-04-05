import langchain 
langchain.debug = False

import os
from datetime import datetime
import streamlit as st
st.set_option('deprecation.showPyplotGlobalUse', False)
from streamlit_option_menu import option_menu
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder

from tools.tool_manager import ToolManager
from storage.storage import PersistentStorage
from storage.document import DocumentManager
from storage.feedback import FeedbackTracker
from storage.logger_config import logger
from ui.sidebar_ui import sidebar
from ui.chat_ui import chat_page
from ui.settings_ui import settings_page
from ui.tools_ui import tools_page
from ui.info_ui import info_page
from ui.settings_ui import list_custom_Agent_names
import config
from PIL import Image

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
logger.debug('BASE_DIR :'+BASE_DIR)

im = Image.open(BASE_DIR+'/assets/appicon.ico')
st.set_page_config(
    page_title="OmniTool",
    page_icon=im,
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/americium-241/Omnitool_UI/tree/master',
        'Report a bug': "https://github.com/americium-241/Omnitool_UI/tree/master",
        'About': "Prototype for highly interactive and customizable chatbot "
    }
)

def ensure_session_state():
    logger.debug('Ensure sessions states')
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    if "model" not in st.session_state:
        st.session_state.model = "custom_llm"
    if "agent" not in st.session_state:
        st.session_state.agent = AgentType.OPENAI_FUNCTIONS
    if 'tool_manager' not in st.session_state:
        st.session_state.tool_manager = ToolManager()
        st.session_state.tool_list = st.session_state.tool_manager.structured_tools
    if "initial_tools" not in st.session_state:
        st.session_state.initial_tools=['Testtool']
    if "selected_tools" not in st.session_state:
        st.session_state.selected_tools = st.session_state.initial_tools
    if "tools" not in st.session_state:
        st.session_state.tools = st.session_state.tool_manager.get_selected_tools(st.session_state.initial_tools)
    if "clicked_cards" not in st.session_state:
        st.session_state.clicked_cards = {tool_name: True for tool_name in st.session_state.initial_tools}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = MessagesPlaceholder(variable_name="chat_history")
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    if "doc_manager" not in st.session_state:
        st.session_state.doc_manager = DocumentManager()
    if "documents" not in st.session_state:
        st.session_state.documents = st.session_state.doc_manager.list_documents()
    if "database" not in st.session_state:
        st.session_state.database = st.session_state.doc_manager.database
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "Settings"
    if "autorun_state" not in st.session_state:
        st.session_state.autorun_state = False
    if "all_tokens" not in st.session_state:
        st.session_state.all_tokens = ''
    if "prefix" not in st.session_state:
        st.session_state.prefix = ''
    if "suffix" not in st.session_state:
        st.session_state.suffix = ''
    if "session_name" not in st.session_state:
        st.session_state.session_name = {}
    if "token_count" not in st.session_state:
        st.session_state.token_count = 0
    if "executed_code" not in st.session_state:
        st.session_state.executed_code = []
    if "plan_execute" not in st.session_state:
        st.session_state.plan_execute = False
    if "customAgentList" not in st.session_state:
        st.session_state.customAgentList = list_custom_Agent_names
    if "feedback_tracker" not in st.session_state:
        st.session_state.feedback_tracker = FeedbackTracker(os.path.join(BASE_DIR, 'storage', 'feedback.csv'))

def option_menu_cb(cb):
    st.session_state.selected_page = st.session_state.menu_opt

def init_storage(base_path=os.path.join(BASE_DIR, 'storage')):
    logger.info('Building storage and doc_manager')
    storage = PersistentStorage(base_path)
    doc_manager = DocumentManager()
    return storage, doc_manager

def menusetup():
    list_menu = ["Chat", "Tools", "Settings", "Info"]
    list_pages = [chat_page, tools_page, settings_page, info_page]
    st.session_state.dictpages = dict(zip(list_menu, list_pages))
    list_icons = ['cloud', 'cloud-upload', 'gear', 'info-circle']
    st.session_state.selected_page = option_menu(
        "", list_menu,
        icons=list_icons,
        menu_icon="",
        orientation="horizontal",
        on_change=option_menu_cb,
        key='menu_opt',
        default_index=list_menu.index(st.session_state.selected_page)
    )

def pageselection():
    st.session_state.dictpages[st.session_state.selected_page]()

def main():
    ensure_session_state()
    menusetup()
    st.session_state.storage, st.session_state.doc_manager = init_storage()
    sidebar()
    pageselection()

if __name__ == "__main__":
    main()
