import pandas as pd
import psycopg
from sentence_transformers import SentenceTransformer
import logging

from configs.setting import RAW_DATA_DIR, CLEAN_DATA_DIR, DB_URL, EMBEDDING_MODEL
from utils.data_util import make_embedding_text, make_region

logger = logging.getLogger(__name__)

def process():
    logger.info("====== Starting data processing ======")
    # Get final data (without embeddings)
    try:
        df = pd.read_json(RAW_DATA_DIR)
    except FileNotFoundError:
        logger.error(f"File not found in {RAW_DATA_DIR}")
        raise

    logger.info(f"Loaded {len(df)} rows")

    # Make new region column (concatenation of region_1 + province)
    df["region"] = df.apply(make_region)
    df = df[['title', 'description', 'region', 'country', 'designation', 'points', 'price', 'variety', 'winery']]
    
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
    logger.info(f"Loading embedding model {EMBEDDING_MODEL}")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL, device='cpu')
    embedding_model = embedding_model.to('cuda')
    
    # Batch generate embedding text
    embeddings = embedding_model.encode(
        df["embedding_text"].tolist(),
        batch_size=16,
        show_progress_bar=True,
        normalize_embeddings=True
    )
    
    # Write to database
    logger.info("Writing to database")
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            with cur.copy("""
                COPY wines (
                    title,
                    description,
                    region,
                    country,
                    designation,
                    points,
                    price,
                    variety,
                    winery,
                    embedding
                )
                FROM STDIN
            """) as copy:

                for row, embedding in zip(df.itertuples(index=False), embeddings):
                    copy.write_row((
                        row.title,
                        row.description,
                        row.region,
                        row.country,
                        row.designation,
                        row.points,
                        row.price,
                        row.variety,
                        row.winery,
                        embedding.tolist(),
                    ))
    logger.info("====== Data processing complete ======")

if __name__ == '__main__':
    process()