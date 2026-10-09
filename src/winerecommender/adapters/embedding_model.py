from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class EmbeddingModel:
    def __init__(self, embedding_model, device='cuda'):
        logger.info(f"Loading embedding model {embedding_model}")
        self.device = device
        self.embedding_model = SentenceTransformer(embedding_model, device='cpu')
        self.embedding_model = self.embedding_model.to(device)

    def encode(self, df):
        embeddings = self.embedding_model.encode(
            df["embedding_text"].tolist(),
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embeddings
    
    def encode_query(self, query):
        embedding = self.embedding_model.encode(
            query,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embedding