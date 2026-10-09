import os
from dotenv import load_dotenv
load_dotenv()

def require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value

# --- Environment-derived config ---
RAW_DATA_DIR = require_env("RAW_DATA_DIR")
CLEAN_DATA_DIR = require_env("CLEAN_DATA_DIR")
DB_URL = require_env("DB_URL")
EMBEDDING_MODEL = require_env("EMBEDDING_MODEL")
EMBEDDING_TEMPLATE_VERSION = require_env("EMBEDDING_TEMPLATE_VERSION")
BATCH_SIZE = int(require_env("BATCH_SIZE"))
TOP_N = int(require_env("TOP_N"))