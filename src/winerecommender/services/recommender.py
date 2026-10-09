import psycopg


from src.winerecommender.adapters.db import PostgresAdapter
from src.winerecommender.adapters.embedding_model import EmbeddingModel
from src.winerecommender.configs.setting import DB_URL, EMBEDDING_MODEL
from src.winerecommender.models.attributes import WineAttribute


def recommend_wines(query, top_n):
    db = PostgresAdapter(DB_URL)
    embedding_model = EmbeddingModel(EMBEDDING_MODEL)
    query_embedding = embedding_model.encode_query(query)
    top_candidates = None
    with psycopg.connect(DB_URL) as conn:
        top_candidates = db.get_top_candidates(conn, query_embedding, top_n)
    
    if not top_candidates:
        return []
    return [WineAttribute.model_validate(row) for row in top_candidates]
    
def encode(query):
    embedding_model = EmbeddingModel(EMBEDDING_MODEL)
    query_embedding = embedding_model.encode_query(query)
    return query_embedding
