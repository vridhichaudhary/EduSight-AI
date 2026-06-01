"""
EduSight AI — FAISS RAG System

Core components:
    FAISSVectorStore  → Manages FAISS index (build/save/load/search)
    ResourceRetriever → High-level search interface
    RAGPipeline       → Orchestrates retrieval for recommendations

Usage:
    # Build index (run once)
    store = FAISSVectorStore()
    store.build()

    # Search
    retriever = ResourceRetriever()
    results   = retriever.search('algebra equations help', k=5)

    # Full RAG pipeline
    pipeline = RAGPipeline()
    context  = pipeline.get_context_for_weak_area('Mathematics', 75.0)
"""

import os
import logging
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger('apps.recommendations')

# ── Paths ──
VECTORSTORE_DIR  = (
    Path(__file__).resolve().parent.parent.parent / 'vectorstores'
)
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

INDEX_PATH    = VECTORSTORE_DIR / 'edusight_resources.index'
METADATA_PATH = VECTORSTORE_DIR / 'edusight_metadata.pkl'
CONFIG_PATH   = VECTORSTORE_DIR / 'edusight_config.json'


# ─────────────────────────────────────────────
# FAISS VECTOR STORE
# ─────────────────────────────────────────────
class FAISSVectorStore:
    """
    Manages a FAISS Flat Index for educational resources.

    Index type: IndexFlatIP (Inner Product = cosine similarity
    when vectors are L2-normalized).

    Files saved to disk:
        edusight_resources.index  → FAISS binary index
        edusight_metadata.pkl     → Resource metadata list
        edusight_config.json      → Index configuration
    """

    def __init__(self):
        self.index     = None
        self.metadata  = []   # List of resource dicts in index order
        self.embedder  = None
        self.dimension = None

    def _get_embedder(self):
        """Lazy-load embedder."""
        if self.embedder is None:
            from .embedder import EmbedderFactory
            self.embedder = EmbedderFactory.create()
        return self.embedder

    def build(self, force_rebuild: bool = False) -> bool:
        """
        Build FAISS index from educational resources.

        Args:
            force_rebuild: If True, rebuild even if index exists.

        Returns:
            True if built successfully, False otherwise.
        """
        if not force_rebuild and self.index_exists():
            logger.info("FAISS index already exists. Use force_rebuild=True.")
            return True

        try:
            import faiss
        except ImportError:
            logger.error("FAISS not installed. Run: pip install faiss-cpu")
            return False

        from .resource_loader import get_all_resources, get_resource_text

        logger.info("Building FAISS index from educational resources...")

        resources = get_all_resources()
        logger.info(f"Embedding {len(resources)} resources...")

        # ── Generate text for embedding ──
        texts = [get_resource_text(r) for r in resources]

        # ── Create embeddings ──
        embedder   = self._get_embedder()
        embeddings = embedder.embed_batch(texts)
        dimension  = embeddings.shape[1]

        logger.info(
            f"Embeddings shape: {embeddings.shape}, dim={dimension}"
        )

        # ── L2 normalize for cosine similarity ──
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        embeddings = embeddings / norms

        # ── Build FAISS index ──
        # IndexFlatIP = exact search with inner product
        self.index    = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)
        self.metadata  = resources
        self.dimension = dimension

        logger.info(
            f"FAISS index built: {self.index.ntotal} vectors, "
            f"dim={dimension}"
        )

        # ── Save to disk ──
        self._save()

        return True

    def _save(self):
        """Save index and metadata to disk."""
        try:
            import faiss

            # Save FAISS binary index
            faiss.write_index(self.index, str(INDEX_PATH))

            # Save resource metadata
            with open(METADATA_PATH, 'wb') as f:
                pickle.dump(self.metadata, f)

            # Save config
            config = {
                'dimension':       self.dimension,
                'num_vectors':     self.index.ntotal,
                'embedder_type':   type(self.embedder).__name__,
                'resource_count':  len(self.metadata),
            }
            with open(CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info(
                f"Index saved: {INDEX_PATH} "
                f"({self.index.ntotal} vectors)"
            )
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise

    def index_exists(self) -> bool:
        """Check if all required index files exist on disk."""
        return (
            INDEX_PATH.exists() and
            METADATA_PATH.exists() and
            CONFIG_PATH.exists()
        )

    def load(self) -> bool:
        """
        Load FAISS index from disk.

        Returns:
            True if loaded successfully, False otherwise.
        """
        if not self.index_exists():
            logger.warning("No FAISS index found. Run build() first.")
            return False

        try:
            import faiss

            self.index = faiss.read_index(str(INDEX_PATH))

            with open(METADATA_PATH, 'rb') as f:
                self.metadata = pickle.load(f)

            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                self.dimension = config.get('dimension')

            logger.info(
                f"FAISS index loaded: {self.index.ntotal} vectors, "
                f"dim={self.dimension}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False

    def get_stats(self) -> Dict:
        """Get statistics about the index."""
        if not self.index_exists():
            return {'exists': False}
            
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
            
            size_bytes = INDEX_PATH.stat().st_size if INDEX_PATH.exists() else 0
            config['exists'] = True
            config['index_size_kb'] = round(size_bytes / 1024, 2)
            config['index_path'] = str(INDEX_PATH)
            return config
        except Exception:
            return {'exists': False}

    def search(
        self,
        query:  str,
        k:      int = 5,
        filter_subject: Optional[str] = None,
    ) -> List[Tuple[Dict, float]]:
        """
        Search for most relevant resources.

        Args:
            query:          Natural language search query
            k:              Number of results to return
            filter_subject: Optional subject filter

        Returns:
            List of (resource_dict, similarity_score) tuples,
            sorted by relevance (highest first).
        """
        if self.index is None:
            if not self.load():
                logger.warning("FAISS index not loaded. Returning empty.")
                return []

        try:
            import faiss

            embedder = self._get_embedder()
            vec      = embedder.embed_text(query)

            # L2 normalize
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm

            # Reshape for FAISS: (1, dim)
            vec = vec.reshape(1, -1).astype(np.float32)

            # Search (return more if filtering)
            search_k = k * 3 if filter_subject else k
            search_k = min(search_k, self.index.ntotal)

            if search_k == 0:
                return []

            scores, indices = self.index.search(vec, search_k)

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:
                    continue

                resource = self.metadata[idx]

                # Apply subject filter if specified
                if filter_subject:
                    subj_match = (
                        resource['subject'].lower() ==
                        filter_subject.lower()
                    )
                    tag_match = (
                        filter_subject.lower() in
                        [t.lower() for t in resource['tags']]
                    )
                    if not (subj_match or tag_match):
                        continue

                results.append((resource, float(score)))
                if len(results) == k:
                    break

            return results

        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            return []


# ─────────────────────────────────────────────
# RESOURCE RETRIEVER
# ─────────────────────────────────────────────
class ResourceRetriever:
    """
    High-level interface for semantic search of educational resources.
    """

    def __init__(self):
        self.store = FAISSVectorStore()

    def search(self, query: str, k: int = 3, subject: Optional[str] = None) -> List[Dict]:
        """
        Search for top K resources.
        Returns list of resource dicts (without scores).
        """
        results = self.store.search(query, k=k, filter_subject=subject)
        return [res[0] for res in results]

    def format_resources_for_prompt(self, resources: List[Dict]) -> str:
        """Format resources nicely for LLM injection."""
        if not resources:
            return "No specific resources available. Please provide general guidance."

        lines = ["AVAILABLE EDUCATIONAL RESOURCES:"]
        for i, r in enumerate(resources, 1):
            lines.append(
                f"\n[Resource {i}]"
                f"\nTitle: {r.get('title')}"
                f"\nType:  {r.get('type', 'article').title()}"
                f"\nURL:   {r.get('url', 'URL not available')}"
                f"\nDesc:  {r.get('description', '')}"
            )
        return "\n".join(lines)


# ─────────────────────────────────────────────
# RAG PIPELINE
# ─────────────────────────────────────────────
class RAGPipeline:
    """
    Orchestrates the Retrieval-Augmented Generation process.
    Used by the Recommender Agent to get context.
    """

    def __init__(self):
        self.retriever = ResourceRetriever()

    def get_context_for_weak_area(self, subject: str, percentage: float, severity: str = "moderate", k: int = 3) -> Dict:
        """
        Generate search query and retrieve formatted resources context.
        """
        # Formulate search query based on weak area insights
        query = f"{subject} fundamentals and practice for struggling students"

        logger.info(f"RAG query: '{query}'")

        # Retrieve resources
        resources = self.retriever.search(query, k=k, subject=subject)

        logger.info(f"RAG retrieved {len(resources)} resources for {subject}")

        # Format context string
        context_string = self.retriever.format_resources_for_prompt(resources)
        
        return {
            'subject': subject,
            'percentage': percentage,
            'severity': severity,
            'resource_count': len(resources),
            'resources': resources,
            'context_string': context_string,
            'query_used': query
        }

