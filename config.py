import logging
from langchain.agents import AgentType
import os

# Logger level 
LOGGER_LEVEL = logging.INFO

# Remove unnecessary keys
KEYS = []

# Update models list
MODELS = ['custom_llm']

# Agents configuration
AGENTS = [eval('AgentType.'+a) for a in dir(AgentType) if a.isupper()]

# LLM temperature 
TEMPERATURE = 0

# Maximum thoughts iteration per query
MAX_ITERATIONS = 20

# Document embedding chunk size
CHUNK_SIZE = 500

# Similarity document search 
SIMILARITY_MAX_DOC = 5
