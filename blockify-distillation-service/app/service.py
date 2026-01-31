"""High-level service for orchestrating the deduplication workflow.

This service follows the frontend technical flow:
1. Per-iteration LLM merging (not deferred to end)
2. Hierarchical subclustering with sqrt(n)*2 formula
3. UUID-based deterministic ordering
4. Progress reporting
"""

import uuid
import math
import time
from typing import List, Dict, Any, Tuple, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.models import AutoDistillRequest, ProcessingStats
from app.dedupe.embeddings import OpenAIEmbeddingGenerator
from app.dedupe.algorithm import DedupeAlgorithm, ProgressReporter
from app.dedupe.similarity import find_similar_pairs_dense
from app.llm.blockify import BlockifyLLM
from app.llm.schemas import MergeRequest
from app.utils.logging import get_logger
from app.config import settings

logger = get_logger(__name__)

MAX_CLUSTER_SIZE_FOR_LLM = settings.max_cluster_size_for_llm
MAX_RECURSION_DEPTH = settings.max_recursion_depth
LLM_PARALLEL_THREADS = settings.llm_parallel_threads
LLM_MAX_RETRIES = settings.llm_max_retries
LLM_RETRY_DELAY = settings.llm_retry_delay


class DedupeService:
    """High-level service for orchestrating the deduplication workflow."""

    def __init__(self):
        # Initialize OpenAI embeddings
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.embedding_generator = OpenAIEmbeddingGenerator()
        logger.info("Using OpenAI embeddings")

        self.algorithm = DedupeAlgorithm(self.embedding_generator)

        # Initialize Blockify LLM
        self.llm = BlockifyLLM()
        logger.info(
            "LLM initialized for block merging",
            max_cluster_size=MAX_CLUSTER_SIZE_FOR_LLM,
            parallel_threads=LLM_PARALLEL_THREADS,
        )

    def process_dedupe_request(
        self,
        request: AutoDistillRequest,
        progress_callback: Optional[Callable[[str, float, Dict], None]] = None,
        save_intermediate_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """Process a deduplication request with per-iteration LLM merging.

        Args:
            request: The auto-distill request
            progress_callback: Optional callback for progress updates
            save_intermediate_callback: Optional callback for intermediate saves

        Returns:
            Dictionary with results and stats
        """
        logger.info(
            "Processing dedupe request",
            task_uuid=request.blockifyTaskUUID,
            similarity=request.similarity,
            iterations=request.iterations,
            input_blocks=len(request.results),
        )

        try:
            blocks_dict = [block.model_dump() for block in request.results]
            reporter = ProgressReporter(progress_callback)

            def llm_merge_func(
                cluster_blocks: List[Dict[str, Any]], similarity_threshold: float
            ) -> List[Dict[str, Any]]:
                return self._merge_cluster_with_llm(cluster_blocks, similarity_threshold)

            final_blocks, stats = self.algorithm.run_dedupe(
                blocks_dict,
                request.similarity,
                request.iterations,
                llm_merge_func=llm_merge_func,
                progress_reporter=reporter,
                save_intermediate_func=save_intermediate_callback,
            )

            # Build the final payload
            original_hidden_blocks = []
            for original in blocks_dict:
                hidden_block = original.copy()
                hidden_block["hidden"] = True
                if "_embedding" in hidden_block:
                    del hidden_block["_embedding"]
                original_hidden_blocks.append(hidden_block)

            new_output_blocks = []
            for block in final_blocks:
                if block.get("type") == "merged":
                    clean_block = block.copy()
                    for key in ["_embedding", "_cluster_blocks", "_iteration"]:
                        if key in clean_block:
                            del clean_block[key]
                    new_output_blocks.append(clean_block)

            response_results = original_hidden_blocks + new_output_blocks

            # Recalculate stats
            starting_count = stats["startingBlockCount"]
            final_count = len(new_output_blocks)
            stats = {
                "startingBlockCount": starting_count,
                "finalBlockCount": final_count,
                "blocksRemoved": starting_count,
                "blocksAdded": final_count,
                "blockReductionPercent": (
                    round(100 * (1 - final_count / starting_count), 2) if starting_count > 0 else 0
                ),
            }

            response = {
                "schemaVersion": 1,
                "status": "success",
                "stats": stats,
                "results": response_results,
            }

            logger.info(
                "Dedupe request completed successfully",
                task_uuid=request.blockifyTaskUUID,
                final_blocks=len(response_results),
                merged_blocks=len(new_output_blocks),
            )

            return response

        except KeyboardInterrupt:
            logger.info("Dedupe request interrupted", task_uuid=request.blockifyTaskUUID)
            raise

        except Exception as e:
            logger.error(
                "Error processing dedupe request",
                task_uuid=request.blockifyTaskUUID,
                error=str(e),
            )
            raise

    def _merge_cluster_with_llm(
        self, cluster_blocks: List[Dict[str, Any]], similarity_threshold: float
    ) -> List[Dict[str, Any]]:
        """Merge a cluster of blocks using LLM with hierarchical subclustering."""
        if len(cluster_blocks) <= MAX_CLUSTER_SIZE_FOR_LLM:
            return self._single_llm_merge_to_blocks(cluster_blocks)
        else:
            logger.info(
                "Large cluster detected, using hierarchical subclustering",
                cluster_size=len(cluster_blocks),
                max_size=MAX_CLUSTER_SIZE_FOR_LLM,
            )

            merged_contents = self._process_large_cluster_recursively(
                cluster_blocks, similarity_threshold, depth=0
            )

            return self._contents_to_blocks(merged_contents, cluster_blocks)

    def _process_large_cluster_recursively(
        self,
        cluster_blocks: List[Dict[str, Any]],
        similarity_threshold: float,
        depth: int = 0,
    ) -> List[Dict[str, str]]:
        """Process a large cluster recursively following frontend algorithm."""
        n = len(cluster_blocks)

        # Base cases
        if n < 2:
            if n == 1:
                result = cluster_blocks[0].get("blockifiedTextResult", {})
                return [
                    {
                        "name": result.get("name", ""),
                        "criticalQuestion": result.get("criticalQuestion", ""),
                        "trustedAnswer": result.get("trustedAnswer", ""),
                    }
                ]
            return []

        if depth >= MAX_RECURSION_DEPTH:
            logger.warning(
                "Max recursion depth reached, forcing direct merge",
                depth=depth,
                cluster_size=n,
            )
            return self._single_llm_merge(cluster_blocks[:MAX_CLUSTER_SIZE_FOR_LLM])

        if n <= MAX_CLUSTER_SIZE_FOR_LLM:
            return self._single_llm_merge(cluster_blocks)

        # Calculate target subcluster size (frontend formula)
        target_size = min(MAX_CLUSTER_SIZE_FOR_LLM, max(5, int(math.floor(math.sqrt(n) * 2))))
        num_subclusters = math.ceil(n / target_size)

        logger.info(
            "Hierarchical split",
            depth=depth,
            total_blocks=n,
            target_size=target_size,
            num_subclusters=num_subclusters,
        )

        # Sort by UUID for deterministic ordering
        sorted_blocks = sorted(cluster_blocks, key=lambda b: b.get("blockifyResultUUID", ""))

        # Create even subclusters
        subclusters = []
        for i in range(num_subclusters):
            start = int(math.floor((i / num_subclusters) * n))
            end = int(math.floor(((i + 1) / num_subclusters) * n))
            if start < end:
                subclusters.append(sorted_blocks[start:end])

        # Process subclusters in parallel
        all_results = []

        if LLM_PARALLEL_THREADS > 1 and len(subclusters) > 1:
            with ThreadPoolExecutor(max_workers=LLM_PARALLEL_THREADS) as executor:
                future_to_idx = {
                    executor.submit(
                        self._process_large_cluster_recursively,
                        subcluster,
                        similarity_threshold,
                        depth + 1,
                    ): i
                    for i, subcluster in enumerate(subclusters)
                }

                results_by_idx = {}
                for future in as_completed(future_to_idx):
                    idx = future_to_idx[future]
                    try:
                        result = future.result()
                        results_by_idx[idx] = result
                    except Exception as e:
                        logger.error(f"Subcluster {idx+1} failed", error=str(e))
                        results_by_idx[idx] = []

                for i in range(len(subclusters)):
                    all_results.extend(results_by_idx.get(i, []))
        else:
            for i, subcluster in enumerate(subclusters):
                subcluster_results = self._process_large_cluster_recursively(
                    subcluster, similarity_threshold, depth + 1
                )
                all_results.extend(subcluster_results)

        # Check if combined results are still too large
        if len(all_results) > MAX_CLUSTER_SIZE_FOR_LLM:
            synthetic_blocks = self._results_to_blocks(all_results)
            return self._process_large_cluster_recursively(
                synthetic_blocks, similarity_threshold, depth + 1
            )

        # Check for similar pairs that need further merging
        if len(all_results) > 1:
            synthetic_blocks = self._results_to_blocks(all_results)
            similar_clusters = self._find_similar_clusters(synthetic_blocks, similarity_threshold)

            if similar_clusters:
                return self._process_large_cluster_recursively(
                    synthetic_blocks, similarity_threshold, depth + 1
                )

        return all_results

    def _single_llm_merge(self, cluster_blocks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Merge a single cluster via LLM with retry logic."""
        last_error = None

        for attempt in range(1, LLM_MAX_RETRIES + 1):
            try:
                merge_request = MergeRequest(cluster_blocks=cluster_blocks, iteration=1)
                merge_response = self.llm.merge_cluster(merge_request)

                if merge_response.success and merge_response.merged_contents:
                    logger.info(
                        "LLM merge produced blocks",
                        input_count=len(cluster_blocks),
                        output_count=len(merge_response.merged_contents),
                        attempt=attempt,
                    )
                    return merge_response.merged_contents

                last_error = merge_response.error or "No merged content returned"
                logger.warning(
                    "LLM merge attempt failed",
                    attempt=attempt,
                    max_retries=LLM_MAX_RETRIES,
                    error=last_error,
                )

            except Exception as e:
                last_error = str(e)
                logger.warning(
                    "LLM merge attempt raised exception",
                    attempt=attempt,
                    max_retries=LLM_MAX_RETRIES,
                    error=last_error,
                )

            if attempt < LLM_MAX_RETRIES:
                delay = LLM_RETRY_DELAY * (2 ** (attempt - 1))
                time.sleep(delay)

        raise RuntimeError(
            f"LLM merge failed after {LLM_MAX_RETRIES} attempts. Last error: {last_error}"
        )

    def _single_llm_merge_to_blocks(
        self, cluster_blocks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge via LLM and return as full block objects."""
        merged_contents = self._single_llm_merge(cluster_blocks)
        return self._contents_to_blocks(merged_contents, cluster_blocks)

    def _contents_to_blocks(
        self, contents: List[Dict[str, str]], source_blocks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Convert merged content dicts to full block objects."""
        source_uuids = [b["blockifyResultUUID"] for b in source_blocks]
        doc_uuid = None
        for b in source_blocks:
            if "blockifyDocumentUUID" in b:
                doc_uuid = b["blockifyDocumentUUID"]
                break

        blocks = []
        for content in contents:
            block = {
                "type": "merged",
                "blockifyResultUUID": str(uuid.uuid4()),
                "blockifiedTextResult": {
                    "name": content.get("name", ""),
                    "criticalQuestion": content.get("criticalQuestion", ""),
                    "trustedAnswer": content.get("trustedAnswer", ""),
                },
                "hidden": False,
                "exported": False,
                "reviewed": False,
                "blockifyResultsUsed": source_uuids,
            }
            if doc_uuid:
                block["blockifyDocumentUUID"] = doc_uuid
            blocks.append(block)

        return blocks

    def _results_to_blocks(self, results: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Convert merged content results to synthetic block format."""
        synthetic_blocks = []
        for result in results:
            block = {
                "blockifyResultUUID": str(uuid.uuid4()),
                "blockifiedTextResult": {
                    "name": result.get("name", ""),
                    "criticalQuestion": result.get("criticalQuestion", ""),
                    "trustedAnswer": result.get("trustedAnswer", ""),
                },
                "type": "synthetic",
            }
            synthetic_blocks.append(block)

        return synthetic_blocks

    def _find_similar_clusters(
        self, blocks: List[Dict[str, Any]], threshold: float
    ) -> List[List[int]]:
        """Find clusters of similar blocks at the given threshold."""
        from collections import defaultdict

        if len(blocks) < 2:
            return []

        text_blobs = [self.embedding_generator.create_text_blob(block) for block in blocks]
        embeddings = self.embedding_generator.generate_embeddings(text_blobs)

        similar_pairs = find_similar_pairs_dense(embeddings, threshold)

        if not similar_pairs:
            return []

        adjacency = defaultdict(set)
        for i, j, _ in similar_pairs:
            adjacency[i].add(j)
            adjacency[j].add(i)

        visited = set()
        clusters = []

        for i in range(len(blocks)):
            if i not in visited:
                cluster = []
                stack = [i]
                while stack:
                    node = stack.pop()
                    if node not in visited:
                        visited.add(node)
                        cluster.append(node)
                        for neighbor in adjacency[node]:
                            if neighbor not in visited:
                                stack.append(neighbor)
                clusters.append(cluster)

        return [c for c in clusters if len(c) > 1]

    def get_health_status(self) -> Dict[str, str]:
        """Get service health status."""
        embedding_model = getattr(self.embedding_generator, "model_name", "unknown")
        llm_model = getattr(self.llm, "model", "none") if self.llm else "none"

        return {
            "status": "ok",
            "model": llm_model,
            "embedding_model": embedding_model,
            "max_cluster_size": str(MAX_CLUSTER_SIZE_FOR_LLM),
        }
