import os
from dotenv import dotenv_values

secrets_file="/run/secrets/api_keys"
conf = dotenv_values(secrets_file)

TELEGRAM_BOT_TOKEN = conf.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = conf.get("OPENAI_API_KEY")
RAG_DOCS_PATH = os.path.join(os.path.dirname(__file__), "docs")
VECTOR_STORE_PATH = os.path.join(os.path.dirname(__file__), "vector_db")