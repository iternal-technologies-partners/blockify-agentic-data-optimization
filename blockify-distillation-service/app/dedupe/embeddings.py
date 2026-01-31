"""OpenAI embeddings generation."""

import numpy as np
import requests
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.utils.logging import get_logger
from app.config import settings

logger = get_logger(__name__)

EMBEDDING_PARALLEL_THREADS = settings.embedding_parallel_threads


class OpenAIEmbeddingGenerator:
    """Handles text embedding generation using OpenAI embeddings API."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model_name
        self.api_key = settings.openai_api_key
        self.embedding_url = settings.openai_embedding_url
        self.max_batch_size = settings.openai_embedding_batch_size

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for embeddings")

        logger.info(
            "Initialized OpenAI embedding generator",
            model=self.model_name,
            url=self.embedding_url,
        )

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts using OpenAI API.

        Uses parallel batch processing for improved performance.

        Args:
            texts: List of text strings to embed

        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([])

        try:
            # Calculate batch ranges
            batch_ranges = []
            for start_idx in range(0, len(texts), self.max_batch_size):
                end_idx = min(start_idx + self.max_batch_size, len(texts))
                batch_ranges.append((start_idx, end_idx))

            num_batches = len(batch_ranges)
            logger.info(
                "Generating OpenAI embeddings (parallel)",
                count=len(texts),
                model=self.model_name,
                batch_size=self.max_batch_size,
                num_batches=num_batches,
                parallel_threads=EMBEDDING_PARALLEL_THREADS,
            )

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            def process_batch(batch_info: Tuple[int, int, int]) -> Tuple[int, List[List[float]]]:
                """Process a single batch of texts (thread worker function).

                Args:
                    batch_info: Tuple of (batch_index, start_idx, end_idx)

                Returns:
                    Tuple of (batch_index, embeddings_list)
                """
                batch_index, start_idx, end_idx = batch_info
                batch_texts = texts[start_idx:end_idx]

                logger.debug("Requesting embeddings batch", batch=batch_index, start=start_idx, end=end_idx)

                payload = {
                    "input": batch_texts,
                    "model": self.model_name,
                }

                response = requests.post(
                    self.embedding_url,
                    json=payload,
                    headers=headers,
                    timeout=60,
                )
                response.raise_for_status()

                response_data = response.json()
                batch_embeddings = [item["embedding"] for item in response_data["data"]]

                return (batch_index, batch_embeddings)

            # Process batches in parallel
            batch_infos = [
                (idx, start, end) for idx, (start, end) in enumerate(batch_ranges)
            ]

            # Store results indexed by batch order to maintain original ordering
            results_by_index: Dict[int, List[List[float]]] = {}

            with ThreadPoolExecutor(max_workers=EMBEDDING_PARALLEL_THREADS) as executor:
                futures = {
                    executor.submit(process_batch, info): info for info in batch_infos
                }

                for future in as_completed(futures):
                    batch_index, batch_embeddings = future.result()
                    results_by_index[batch_index] = batch_embeddings

            # Reassemble embeddings in correct order
            embeddings: List[List[float]] = []
            for idx in range(num_batches):
                embeddings.extend(results_by_index[idx])

            embeddings_array = np.array(embeddings, dtype=np.float32)
            logger.info(
                "OpenAI embeddings generated successfully (parallel)",
                shape=embeddings_array.shape,
            )
            return embeddings_array

        except Exception as e:
            logger.error("Failed to generate OpenAI embeddings", error=str(e), count=len(texts))
            raise

    def create_text_blob(self, block: Dict[str, Any]) -> str:
        """Create a text blob from a blockify result for embedding.

        Args:
            block: BlockifyResult dictionary

        Returns:
            Combined text string
        """
        result = block.get("blockifiedTextResult", {})
        name = result.get("name", "")
        question = result.get("criticalQuestion", "")
        answer = result.get("trustedAnswer", "")

        # Combine with spaces, filter empty strings
        parts = [part.strip() for part in [name, question, answer] if part.strip()]
        text = " ".join(parts)

        # Handle empty text
        if not text:
            text = f"block-{block.get('blockifyResultUUID', 'unknown')}"

        return text
