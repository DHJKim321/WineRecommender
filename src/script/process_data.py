import pandas as pd
import psycopg
import logging

from src.configs.setting import RAW_DATA_DIR, CLEAN_DATA_DIR, DB_URL, EMBEDDING_MODEL
from src.utils.data_util import make_embedding_text, make_region
from src.adapter.db import PostgresAdapter
from src.adapter.embedding_model import EmbeddingModel

logger = logging.getLogger(__name__)

def process():
    logger.info("====== Starting data processing ======")
    # Get final data (without embeddings)
    try:
        df = pd.read_json(RAW_DATA_DIR)
        df["source_id"] = df.index
    except FileNotFoundError:
        logger.error(f"File not found in {RAW_DATA_DIR}")
        raise

    logger.info(f"Loaded {len(df)} rows")

    # Make new region column (concatenation of region_1 + province)
    df["region"] = df.apply(make_region, axis=1)
    df = df[['source_id', 'title', 'description', 'region', 'country', 'designation', 'points', 'price', 'variety', 'winery']]
    
    # Write to file
    try:
        df.to_json(CLEAN_DATA_DIR)
    except FileNotFoundError:
        logger.error(f"Directory not found in {CLEAN_DATA_DIR}")
        raise

    logger.info(f"Final dataset: {len(df)} rows")
    
    # Format data into input text
    df["embedding_text"] = df.apply(make_embedding_text, axis=1)
    
    # Load embedding model
    logger.info("Loading embedding model")
    embedding_model = EmbeddingModel(EMBEDDING_MODEL)
    embeddings = embedding_model.encode(df)
    
    # Write to database
    logger.info("Writing to database")
    db = PostgresAdapter(DB_URL)
    with psycopg.connect(DB_URL) as conn:
        db.create_staging_table(conn)
        db.copy_into_staging_table(conn, df, embeddings)
        db.upsert_into_table(conn)
    
    logger.info("====== Data processing complete ======")

if __name__ == '__main__':
    process()
