import pandas as pd
import psycopg
import logging
from tqdm import tqdm

from src.winerecommender.configs.setting import RAW_DATA_DIR, CLEAN_DATA_DIR, DB_URL, EMBEDDING_MODEL, BATCH_SIZE, EMBEDDING_TEMPLATE_VERSION
from src.winerecommender.utils.data_util import make_embedding_df, make_final_df
from src.winerecommender.adapters.db import PostgresAdapter
from src.winerecommender.adapters.embedding_model import EmbeddingModel

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

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

    # Creating new columns and selecting relevant columns
    df = make_final_df(df)
    
    # Write to file
    try:
        df.to_json(CLEAN_DATA_DIR)
    except FileNotFoundError:
        logger.error(f"Directory not found in {CLEAN_DATA_DIR}")
        raise

    logger.info(f"Final dataset: {len(df)} rows")
    
    # Load embedding model and db adapter
    logger.info("Loading embedding model and db adapter")
    embedding_model = EmbeddingModel(EMBEDDING_MODEL)
    db = PostgresAdapter(DB_URL)
    
    # Batch encode -> write to db
    with psycopg.connect(DB_URL) as conn:
        db.create_staging_tables(conn)
        logger.info("Starting embedding generation")
        for start in tqdm(range(0, len(df), BATCH_SIZE), desc="Generating batch embeddings"):
            # logger.info(f"Encoding and writing batch: {start // BATCH_SIZE}")
            end = start + BATCH_SIZE
            batch_df = df.iloc[start:end]
            batch_embeddings = embedding_model.encode(batch_df)

            batch_embedding_df = make_embedding_df(batch_df, batch_embeddings, EMBEDDING_MODEL, EMBEDDING_TEMPLATE_VERSION)

            db.copy_into_wines_staging_table(conn, batch_df)
            db.copy_into_embeddings_staging_table(conn, batch_embedding_df)
            db.upsert_into_wines_table(conn)
            db.upsert_into_embeddings_table(conn)

            db.clear_staging_tables(conn)            
            conn.commit()
    
    logger.info("====== Data processing complete ======")

if __name__ == '__main__':
    process()
