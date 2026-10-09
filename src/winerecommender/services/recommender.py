import psycopg
import logging

from winerecommender.adapters.db import PostgresAdapter
from winerecommender.adapters.embedding_model import EmbeddingModel
from winerecommender.configs.setting import DB_URL
from winerecommender.models.attributes import WineAttribute

logger = logging.getLogger(__name__)

class RecommenderService:
    def __init__(
        self,
        db_adapter: PostgresAdapter,
        embedding_model: EmbeddingModel,
        db_url: str,
    ):
        self.db_adapter = db_adapter
        self.embedding_model = embedding_model
        self.db_url = db_url

    def recommend_wines(self, query, top_n):
        query_embedding = self.embedding_model.encode_query(query)
        top_candidates = None
        with psycopg.connect(DB_URL) as conn:
            top_candidates = self.db_adapter.get_top_candidates(conn, query_embedding, top_n)
            logger.info(f"Retrieved: {top_candidates}")
        
        if not top_candidates:
            return []
        return [WineAttribute.model_validate(row) for row in top_candidates]
        
    def encode(self, query):
        query_embedding = self.embedding_model.encode_query(query)
        return query_embedding
