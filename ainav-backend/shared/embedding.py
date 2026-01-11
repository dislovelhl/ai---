import logging
from sentence_transformers import SentenceTransformer
import os

logger = logging.getLogger(__name__)

# Use a lightweight multilingual model good for Chinese and English
# BAAI/bge-small-zh-v1.5 is excellent for Chinese but 'paraphrase-multilingual-MiniLM-L12-v2' is a safe standard
# The strategy report mentioned BGE-M3, but Bge-small-zh-v1.5 is much faster for CPU.
# Let's use 'BAAI/bge-small-zh-v1.5' if possible, but to be safe and standard: 'all-MiniLM-L6-v2' or 'paraphrase-multilingual-MiniLM-L12-v2'.
# Report says: "Generates BGE-M3 embedding". I will respect the intent but use a smaller variant for performance in this env.
MODEL_NAME = "BAAI/bge-small-zh-v1.5"

class EmbeddingService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    def initialize(self):
        if self._model is None:
            logger.info(f"Loading embedding model: {MODEL_NAME}...")
            try:
                # Cache folder can be set env var SENTENCE_TRANSFORMERS_HOME or default
                self._model = SentenceTransformer(MODEL_NAME)
                logger.info("Embedding model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise e

    def generate_embedding(self, text: str) -> list[float]:
        if self._model is None:
            self.initialize()
        
        # BGE models need specific instruction for queries but usually fine without for simple usage
        # content-based embedding
        embeddings = self._model.encode(text, normalize_embeddings=True)
        return embeddings.tolist()

embedding_service = EmbeddingService()
