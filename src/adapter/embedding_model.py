from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class EmbeddingModel:
    def __init__(self, embedding_model, batch_size=16, device='cuda'):
        logger.info(f"Loading embedding model {embedding_model}")
        self.device = device
        self.batch_size = batch_size
        self.embedding_model = SentenceTransformer(embedding_model, device='cpu')
        self.embedding_model = self.embedding_model.to(device)

    def encode(self, df):
        logger.info("Generating embeddings")
        embeddings = self.embedding_model.encode(
            df["embedding_text"].tolist(),
            batch_size=self.batch_size,
            show_progress_bar=True,
            normalize_embeddings=True
        )
        return embeddings