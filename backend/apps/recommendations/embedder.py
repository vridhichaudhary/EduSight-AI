"""
EduSight AI — Embedding Factory

Creates vector embeddings for FAISS index.

Supported embedders:
    OpenAIEmbedder  → text-embedding-ada-002 (1536 dims)
                      requires OPENAI_API_KEY
    GoogleEmbedder  → text-embedding-004
                      requires GOOGLE_API_KEY
    MockEmbedder    → random vectors (128 dims)
                      for development without API key

Both produce numpy float32 arrays compatible with FAISS.
The FAISS index dimension must match the embedder dimension.
"""

import os
import logging
import numpy as np
from typing import List

logger = logging.getLogger('apps.recommendations')

# Dimensions for each embedder
OPENAI_DIM = 1536
GOOGLE_DIM = 768
MOCK_DIM   = 128


class MockEmbedder:
    """
    Development embedder using deterministic random vectors.
    Seeds on text hash so same text → same vector.
    Allows FAISS to work without OpenAI API key.
    Similarity search returns plausible but not semantic results.
    """

    dim = MOCK_DIM

    def embed_text(self, text: str) -> np.ndarray:
        """Embed single text → deterministic random vector."""
        seed = hash(text) % (2**31)
        rng  = np.random.default_rng(seed)
        vec  = rng.random(self.dim).astype(np.float32)
        # L2 normalize for cosine similarity
        norm = np.linalg.norm(vec)
        return (vec / norm) if norm > 0 else vec

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Embed list of texts → 2D array (N, dim)."""
        return np.array(
            [self.embed_text(t) for t in texts],
            dtype=np.float32
        )

    def __repr__(self):
        return f"MockEmbedder(dim={self.dim})"


class OpenAIEmbedder:
    """
    Production embedder using OpenAI text-embedding-ada-002.
    Produces semantically meaningful 1536-dim vectors.
    Requires OPENAI_API_KEY in environment.
    """

    dim = OPENAI_DIM

    def __init__(self, api_key: str):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model  = 'text-embedding-ada-002'
            logger.info("OpenAIEmbedder initialized")
        except ImportError:
            raise ImportError("pip install openai")

    def embed_text(self, text: str) -> np.ndarray:
        """Embed single text using OpenAI API."""
        # Truncate to 8000 chars (API limit)
        text = text[:8000].replace('\n', ' ')
        response = self.client.embeddings.create(
            input=text,
            model=self.model,
        )
        vec = np.array(
            response.data[0].embedding,
            dtype=np.float32
        )
        return vec

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 20,
    ) -> np.ndarray:
        """
        Embed list of texts in batches.
        Batching reduces API calls and improves throughput.
        """
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch = [t[:8000].replace('\n', ' ') for t in batch]

            response = self.client.embeddings.create(
                input=batch,
                model=self.model,
            )
            batch_embeddings = [
                np.array(item.embedding, dtype=np.float32)
                for item in response.data
            ]
            all_embeddings.extend(batch_embeddings)

            logger.info(
                f"Embedded batch {i//batch_size + 1}"
                f"/{(len(texts)-1)//batch_size + 1}"
            )

        return np.array(all_embeddings, dtype=np.float32)

    def __repr__(self):
        return f"OpenAIEmbedder(model={self.model}, dim={self.dim})"


class GoogleEmbedder:
    """
    Production embedder using Google text-embedding-004.
    Produces semantically meaningful 768-dim vectors.
    Requires GOOGLE_API_KEY in environment.
    """

    dim = GOOGLE_DIM

    def __init__(self, api_key: str):
        try:
            from google import genai
            self.client = genai.Client(api_key=api_key)
            self.model  = 'gemini-embedding-2'
            logger.info("GoogleEmbedder initialized")
        except ImportError:
            raise ImportError("pip install google-genai")

    def embed_text(self, text: str) -> np.ndarray:
        """Embed single text using Google API."""
        text = text[:8000].replace('\n', ' ')
        response = self.client.models.embed_content(
            model=self.model,
            contents=text,
        )
        vec = np.array(
            response.embeddings[0].values,
            dtype=np.float32
        )
        return vec

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 20,
    ) -> np.ndarray:
        """
        Embed list of texts sequentially to avoid API batching shape issues.
        """
        all_embeddings = []

        for i, text in enumerate(texts):
            vec = self.embed_text(text)
            all_embeddings.append(vec)

            if (i + 1) % batch_size == 0 or (i + 1) == len(texts):
                logger.info(
                    f"Embedded {i + 1}/{len(texts)} resources"
                )

        return np.array(all_embeddings, dtype=np.float32)

    def __repr__(self):
        return f"GoogleEmbedder(model={self.model}, dim={self.dim})"


class EmbedderFactory:
    """
    Factory that creates the appropriate embedder.
    Checks API keys and returns accordingly.
    """

    @staticmethod
    def create() -> 'MockEmbedder | OpenAIEmbedder | GoogleEmbedder':
        """
        Create and return embedder instance.
        """
        google_api_key = os.getenv('GOOGLE_API_KEY', '')
        openai_api_key = os.getenv('OPENAI_API_KEY', '')

        if google_api_key and not google_api_key.startswith('your-'):
            try:
                embedder = GoogleEmbedder(api_key=google_api_key)
                logger.info("Using GoogleEmbedder (production mode)")
                return embedder
            except Exception as e:
                logger.error(f"GoogleEmbedder failed: {e}. Falling back.")
        
        if openai_api_key and not openai_api_key.startswith('your-'):
            try:
                embedder = OpenAIEmbedder(api_key=openai_api_key)
                logger.info("Using OpenAIEmbedder (production mode)")
                return embedder
            except Exception as e:
                logger.error(f"OpenAIEmbedder failed: {e}. Falling back.")

        logger.warning(
            "No valid API KEY found or initialization failed. "
            "Using MockEmbedder for development. "
            "Semantic search will return approximate results. "
        )
        return MockEmbedder()
