import streamlit as st
from streamlit_elements import elements, mui, html
import os
from tools.base_tools import Ui_Tool
from storage.logger_config import logger
from tools.utils import evaluate_function_string
import autogen
from langchain.tools import WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import pandas as pd

Local_dir = os.path.dirname(os.path.realpath(__file__))

class Code_sender(Ui_Tool):
    name = 'Code_sender'
    icon = '💻'
    title = 'Code Sender'
    description = "Allow you to send python script code to complete the task and get the result of the code"

    def _run(self, code):
        try:
            logger.info("CODE executed : %s", code)
            st.session_state.executed_code.append(code)
            return 'Success, returns : ' + str(exec(code, globals(), locals()))
        except Exception as e:
            return f"An error occurred while executing the code: {e}"

    def _ui(self):
        def checkstate(value):
            st.session_state.autorun_state = value['target']['checked']

        with mui.Accordion():
            with mui.AccordionSummary(expandIcon=mui.icon.ExpandMore):
                mui.Typography("Options")
            with mui.AccordionDetails():
                mui.FormControlLabel(
                    control=mui.Checkbox(onChange=checkstate, checked=st.session_state.autorun_state),
                    label="Auto run"
                )

class SnowflakeQuery(Ui_Tool):
    name = 'snowflake_query'
    icon = '❄️'
    title = 'Snowflake Query'
    description = 'Execute queries on Snowflake database'

    def _run(self, query: str):
        try:
            # Import and connection handling should be implemented here
            # This is a placeholder - actual implementation needed
            return f"Query executed: {query}"
        except Exception as e:
            return f"Error executing query: {str(e)}"
    
    def _ui(self):
        with mui.Accordion():
            with mui.AccordionSummary(expandIcon=mui.icon.ExpandMore):
                mui.Typography("Options")
            with mui.AccordionDetails():
                if "snowflake_config" not in st.session_state:
                    st.session_state.snowflake_config = {
                        'warehouse': '',
                        'database': '',
                        'schema': ''
                    }

                def handle_config_change(key, value):
                    st.session_state.snowflake_config[key] = value['target']['value']

                for key in st.session_state.snowflake_config:
                    with elements(f"snowflake_{key}_input"):
                        mui.Typography(f"Enter {key}")
                        mui.TextField(
                            label="",
                            variant="outlined",
                            fullWidth=True,
                            defaultValue=st.session_state.snowflake_config[key],
                            onChange=lambda k=key: lambda v: handle_config_change(k, v)
                        )

def wiki_search(query):
    """Allow you to query the wikipedia api to get information about your query"""
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    return wikipedia.run(query)

def dataframe_query(query):
    """Allow you to query the available dataframe in the workspace"""
    workspace = Local_dir + '\\..\\..\\workspace'
    df_list = []
    for file in os.listdir(workspace):
        if file.endswith(".csv"):
            df_list.append(pd.read_csv(os.path.join(workspace, file)))
        elif file.endswith(".xlsx"):
            df_list.append(pd.read_excel(os.path.join(workspace, file)))
    
    if not df_list:
        return "No dataframes found in workspace"

    try:
        result = pd.concat(df_list)
        query_result = result.query(query) if query else result
        return query_result.to_string()
    except Exception as e:
        return f"Error querying dataframes: {str(e)}"

def make_tool(toolcode):
    """Send your toolcode to create a new tool"""
    runs_without_error, has_doc, tool_name = evaluate_function_string(toolcode)

    if not runs_without_error:
        return f"Error: {runs_without_error}"

    if not has_doc:
        return "Error: Function must have a docstring."

    if not tool_name:
        return "Error: Could not extract tool name."

    tools_path = os.path.join(Local_dir, f"{tool_name}.py")
    
    with open(tools_path, "w") as f:
        f.write('\n' + toolcode)

    st.session_state.tool_manager = ToolManager()
    st.session_state.tool_list = st.session_state.tool_manager.structured_tools
    return 'Success'
