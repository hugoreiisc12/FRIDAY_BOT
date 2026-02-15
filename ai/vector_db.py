# Vector DB manager with FAISS and Pinecone optional support
from typing import List, Tuple, Optional, Dict
import numpy as np
import os

# Optional imports
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except Exception:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except Exception:
    faiss = None
    FAISS_AVAILABLE = False


class EmbeddingService:
    """Embeddings using Sentence-Transformers (or a simple fallback)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        if SENTENCE_TRANSFORMERS_AVAILABLE and SentenceTransformer is not None:
            self.model = SentenceTransformer(model_name)
            self.dim = self.model.get_sentence_embedding_dimension()
        else:
            self.model = None
            self.dim = 384  # default

    def encode(self, texts: List[str]) -> np.ndarray:
        if self.model:
            emb = self.model.encode(texts, convert_to_numpy=True)
            return emb
        # fallback: random but deterministic-ish
        return np.array([[hash(t) % 1000 / 1000.0 for _ in range(self.dim)] for t in texts], dtype=np.float32)

    def encode_single(self, text: str) -> np.ndarray:
        return self.encode([text])[0]


class FAISSVectorDB:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = None
        self.metadata: List[Dict] = []

    def _ensure_index(self):
        if self.index is None:
            if FAISS_AVAILABLE:
                self.index = faiss.IndexFlatL2(self.dimension)
            else:
                # Fallback to a simple in-memory index (brute-force) when faiss isn't available.
                # Stored as a list of numpy arrays.
                self.index = []

    def add_products(self, produtos: List[Dict], embedding_service: EmbeddingService):
        embeddings = embedding_service.encode([p.get("nome", "") for p in produtos])
        embeddings = np.array(embeddings).astype('float32')
        self._ensure_index()
        if FAISS_AVAILABLE:
            self.index.add(embeddings)
        else:
            # append rows to in-memory index
            for row in embeddings:
                self.index.append(row)
        # store metadata
        self.metadata.extend(produtos)

    def search(self, query: str, embedding_service: EmbeddingService, k: int = 10) -> List[Tuple[Dict, float]]:
        if self.index is None or (FAISS_AVAILABLE and getattr(self.index, 'ntotal', 0) == 0) or (not FAISS_AVAILABLE and len(self.index) == 0):
            return []
        q_emb = embedding_service.encode_single(query).astype('float32')
        if FAISS_AVAILABLE:
            D, I = self.index.search(np.expand_dims(q_emb, axis=0), k)
            results = []
            for dist, idx in zip(D[0], I[0]):
                if idx < 0 or idx >= len(self.metadata):
                    continue
                results.append((self.metadata[idx], float(dist)))
            return results
        else:
            # brute-force L2 distances
            arr = np.stack(self.index, axis=0)
            diffs = arr - q_emb
            dists = np.sum(diffs * diffs, axis=1)
            idxs = np.argsort(dists)[:k]
            results = []
            for idx in idxs:
                results.append((self.metadata[idx], float(dists[idx])))
            return results


class PineconeVectorDB:
    def __init__(self, index_name: str = None):
        # Lightweight stub - integration requires pinecone-client and env vars
        self.index_name = index_name

    def add_products(self, produtos: List[Dict], embedding_service: EmbeddingService):
        raise NotImplementedError("Pinecone integration not implemented in this scaffold.")

    def search(self, query: str, embedding_service: EmbeddingService, k: int = 10):
        raise NotImplementedError("Pinecone integration not implemented in this scaffold.")


class VectorDBManager:
    def __init__(self, embedding_service: EmbeddingService, vector_db: Optional[object] = None):
        self.embedding_service = embedding_service
        self.vector_db = vector_db or FAISSVectorDB(dimension=self.embedding_service.dim)

    def index_products(self, produtos: List[Dict]):
        self.vector_db.add_products(produtos, self.embedding_service)

    def search_semantic(self, query: str, k: int = 10, min_score: float = 0.3):
        res = self.vector_db.search(query, self.embedding_service, k=k)
        # Convert L2 distances to similarity-like scores (simple)
        results = []
        for meta, dist in res:
            # similarity proxy: 1 / (1 + dist)
            score = 1.0 / (1.0 + dist)
            if score >= min_score:
                results.append({"produto": meta, "score": score})
        return results
