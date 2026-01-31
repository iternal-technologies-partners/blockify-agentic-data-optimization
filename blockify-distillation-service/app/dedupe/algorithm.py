"""Core deduplication algorithm with per-iteration LLM merging.

This module implements the iterative deduplication pipeline that:
1. Generates embeddings for blocks
2. Uses LSH bucketing for large datasets
3. Finds similar pairs via cosine similarity
4. Creates clusters using Louvain (large) or BFS (small)
5. Merges clusters via LLM within each iteration
6. Re-embeds merged results for next iteration
7. Increases similarity threshold progressively
"""

import numpy as np
import uuid
import math
from typing import List, Dict, Any, Set, Tuple, Optional, Callable
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.dedupe.embeddings import OpenAIEmbeddingGenerator
from app.dedupe.similarity import find_similar_pairs_sparse, find_similar_pairs_dense
from app.dedupe.lsh import find_similar_pairs_with_lsh, MIN_ITEMS_TO_ENABLE_LSH
from app.utils.logging import get_logger
from app.config import settings

logger = get_logger(__name__)

# Configuration constants
MAX_BLOCKS_PER_CLUSTER = settings.max_blocks_per_cluster
SIMILARITY_INCREASE_PER_ITERATION = settings.similarity_increase_per_iteration
SIMILARITY_INCREASE_ITERATION_START = settings.similarity_increase_iteration_start
MAX_SIMILARITY_THRESHOLD = settings.max_similarity_threshold
LOUVAIN_NODE_THRESHOLD = settings.louvain_node_threshold
LLM_PARALLEL_THREADS = settings.llm_parallel_threads


class ProgressReporter:
    """Reports progress during deduplication."""

    def __init__(self, callback: Optional[Callable[[str, float, Dict], None]] = None):
        self.callback = callback

    def report(self, phase: str, progress: float, details: Dict[str, Any] = None):
        """Report progress update."""
        if self.callback:
            self.callback(phase, progress, details or {})
        logger.info(f"Progress: {phase}", progress=f"{progress:.1%}", **(details or {}))


class DedupeAlgorithm:
    """Core deduplication algorithm with per-iteration LLM merging."""

    def __init__(self, embedding_generator: OpenAIEmbeddingGenerator):
        self.embedding_generator = embedding_generator
        self.use_lsh = settings.use_lsh
        self.max_neighbors = settings.max_similarity_neighbors

    def run_dedupe(
        self,
        blocks: List[Dict[str, Any]],
        similarity_threshold: float,
        max_iterations: int,
        llm_merge_func: Optional[Callable] = None,
        progress_reporter: Optional[ProgressReporter] = None,
        save_intermediate_func: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Run the iterative deduplication process with per-iteration LLM merging.

        Args:
            blocks: List of blockify results
            similarity_threshold: Initial cosine similarity threshold
            max_iterations: Maximum number of iterations
            llm_merge_func: Function to merge a cluster via LLM
            progress_reporter: Optional progress reporter
            save_intermediate_func: Optional function to save intermediate results

        Returns:
            Tuple of (final_blocks, stats)
        """
        reporter = progress_reporter or ProgressReporter()

        reporter.report("initialization", 0.0, {"status": "Starting deduplication"})

        # Phase 1: Filter and prepare blocks
        active_blocks = [
            block
            for block in blocks
            if not block.get("hidden", False) and not block.get("exported", False)
        ]

        starting_count = len(active_blocks)
        current_threshold = similarity_threshold

        logger.info(
            "Starting deduplication",
            initial_count=starting_count,
            similarity_threshold=similarity_threshold,
            max_iterations=max_iterations,
            max_blocks_per_cluster=MAX_BLOCKS_PER_CLUSTER,
        )

        if starting_count < 2:
            return active_blocks, self._create_stats(starting_count, starting_count, 0)

        # Phase 2: Generate initial embeddings
        reporter.report("embeddings", 0.05, {"status": "Generating embeddings"})
        master_list = self._add_embeddings_to_blocks(active_blocks)
        reporter.report(
            "embeddings", 0.15, {"status": "Embeddings complete", "count": len(master_list)}
        )

        # Track all source blocks that get merged
        all_hidden_uuids: Set[str] = set()
        all_merged_blocks: List[Dict[str, Any]] = []

        # Phase 3: Iteration loop
        iteration_progress_start = 0.15
        iteration_progress_end = 0.95
        iteration_progress_range = iteration_progress_end - iteration_progress_start

        for iteration in range(1, max_iterations + 1):
            iteration_progress = (
                iteration_progress_start + (iteration / max_iterations) * iteration_progress_range
            )

            reporter.report(
                "iteration",
                iteration_progress,
                {
                    "iteration": iteration,
                    "block_count": len(master_list),
                    "threshold": current_threshold,
                },
            )

            logger.info(
                "Starting iteration",
                iteration=iteration,
                block_count=len(master_list),
                threshold=current_threshold,
            )

            if len(master_list) < 2:
                logger.info("Too few blocks to cluster, stopping", iteration=iteration)
                break

            # Step 3.1: Find similar pairs
            embeddings = self._extract_embeddings(master_list)
            similar_pairs = self._find_similar_pairs(embeddings, current_threshold)

            if not similar_pairs:
                logger.info("No similar pairs found, stopping iterations", iteration=iteration)
                break

            # Step 3.2: Create non-overlapping clusters
            clusters = self._create_clusters(similar_pairs, len(master_list))
            mergeable_clusters = [c for c in clusters if len(c) > 1]

            if not mergeable_clusters:
                logger.info("No mergeable clusters found, stopping", iteration=iteration)
                break

            logger.info(
                "Found mergeable clusters",
                iteration=iteration,
                cluster_count=len(mergeable_clusters),
                total_items=sum(len(c) for c in mergeable_clusters),
            )

            # Step 3.3: Process clusters via LLM merge (parallel)
            merged_results = []
            hidden_uuids_this_iteration: Set[str] = set()
            items_not_in_clusters = set(range(len(master_list)))
            failed_cluster_indices: Set[int] = set()

            successful_merges = 0
            failed_merges = 0

            def process_single_cluster(cluster_data):
                """Process a single cluster for merging (thread worker function)."""
                cluster_idx, cluster_indices = cluster_data
                cluster_blocks = [master_list[i] for i in cluster_indices]

                if llm_merge_func:
                    try:
                        merge_results = llm_merge_func(cluster_blocks, current_threshold)
                        if merge_results:
                            return {
                                "success": True,
                                "cluster_idx": cluster_idx,
                                "cluster_indices": cluster_indices,
                                "cluster_blocks": cluster_blocks,
                                "merge_results": merge_results,
                            }
                        else:
                            logger.warning(
                                "LLM merge returned empty results",
                                cluster_idx=cluster_idx,
                                cluster_size=len(cluster_blocks),
                            )
                            return {
                                "success": False,
                                "cluster_idx": cluster_idx,
                                "cluster_indices": cluster_indices,
                            }
                    except Exception as e:
                        logger.error(
                            "LLM merge failed for cluster",
                            error=str(e),
                            cluster_idx=cluster_idx,
                            cluster_size=len(cluster_blocks),
                        )
                        return {
                            "success": False,
                            "cluster_idx": cluster_idx,
                            "cluster_indices": cluster_indices,
                        }
                else:
                    merged_block = self._create_merged_block_placeholder(cluster_blocks, iteration)
                    return {
                        "success": True,
                        "cluster_idx": cluster_idx,
                        "cluster_indices": cluster_indices,
                        "cluster_blocks": cluster_blocks,
                        "merge_results": [merged_block],
                    }

            # Process clusters in parallel using ThreadPoolExecutor
            cluster_data_list = list(enumerate(mergeable_clusters))

            with ThreadPoolExecutor(max_workers=LLM_PARALLEL_THREADS) as executor:
                futures = {
                    executor.submit(process_single_cluster, data): data
                    for data in cluster_data_list
                }

                for future in as_completed(futures):
                    result = future.result()

                    if result["success"]:
                        merged_results.extend(result["merge_results"])
                        successful_merges += 1

                        for idx in result["cluster_indices"]:
                            items_not_in_clusters.discard(idx)
                        for block in result["cluster_blocks"]:
                            hidden_uuids_this_iteration.add(block["blockifyResultUUID"])
                    else:
                        failed_merges += 1
                        failed_cluster_indices.update(result["cluster_indices"])

            logger.info(
                "Cluster merge summary",
                iteration=iteration,
                successful=successful_merges,
                failed=failed_merges,
                merged_blocks=len(merged_results),
            )

            if not merged_results and failed_merges > 0:
                logger.warning(
                    "All cluster merges failed in iteration",
                    iteration=iteration,
                    failed_count=failed_merges,
                )

            all_hidden_uuids.update(hidden_uuids_this_iteration)
            all_merged_blocks.extend(merged_results)

            # Step 3.4: Generate embeddings for new merged results
            merged_with_embeddings = []
            if merged_results:
                merged_with_embeddings = self._add_embeddings_to_blocks(merged_results)

            # Step 3.5: Build new master list for next iteration
            items_to_keep = [master_list[i] for i in sorted(items_not_in_clusters)]
            master_list = items_to_keep + merged_with_embeddings

            if not merged_results and current_threshold >= MAX_SIMILARITY_THRESHOLD:
                logger.warning(
                    "No successful merges and threshold at maximum, stopping",
                    iteration=iteration,
                )
                break

            logger.info(
                "Iteration complete",
                iteration=iteration,
                items_merged=len(hidden_uuids_this_iteration),
                new_blocks=len(merged_results),
                next_iteration_count=len(master_list),
            )

            # Save intermediate progress
            if save_intermediate_func and all_merged_blocks:
                try:
                    intermediate_result = self._build_intermediate_result(
                        active_blocks, all_hidden_uuids, all_merged_blocks, starting_count
                    )
                    save_intermediate_func(intermediate_result)
                except Exception as e:
                    logger.warning("Failed to save intermediate progress", error=str(e))

            # Step 3.6: Increase threshold for next iteration
            if iteration >= SIMILARITY_INCREASE_ITERATION_START:
                current_threshold = min(
                    current_threshold + SIMILARITY_INCREASE_PER_ITERATION,
                    MAX_SIMILARITY_THRESHOLD,
                )

        # Phase 4: Build final results
        reporter.report("completion", 0.95, {"status": "Building results"})

        final_blocks = []

        for block in active_blocks:
            if block["blockifyResultUUID"] not in all_hidden_uuids:
                final_blocks.append(block)

        final_blocks.extend(all_merged_blocks)

        stats = self._create_stats(starting_count, len(final_blocks), len(all_merged_blocks))

        reporter.report("completion", 1.0, {"status": "Complete", **stats})

        logger.info("Deduplication completed", **stats)

        return final_blocks, stats

    def _add_embeddings_to_blocks(
        self, blocks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate embeddings for blocks and add as property."""
        if not blocks:
            return []

        text_blobs = [self.embedding_generator.create_text_blob(block) for block in blocks]
        embeddings = self.embedding_generator.generate_embeddings(text_blobs)

        result = []
        for block, embedding in zip(blocks, embeddings):
            block_with_embedding = block.copy()
            block_with_embedding["_embedding"] = embedding
            result.append(block_with_embedding)

        return result

    def _extract_embeddings(self, blocks: List[Dict[str, Any]]) -> np.ndarray:
        """Extract embeddings array from blocks."""
        embeddings = []
        for block in blocks:
            if "_embedding" in block:
                embeddings.append(block["_embedding"])
            else:
                text_blob = self.embedding_generator.create_text_blob(block)
                embedding = self.embedding_generator.generate_embeddings([text_blob])[0]
                embeddings.append(embedding)

        return np.array(embeddings)

    def _find_similar_pairs(
        self, embeddings: np.ndarray, threshold: float
    ) -> List[Tuple[int, int, float]]:
        """Find similar pairs using LSH for large datasets, dense for small."""
        n_samples = embeddings.shape[0]

        if self.use_lsh and n_samples >= MIN_ITEMS_TO_ENABLE_LSH:
            logger.info("Using LSH for similarity search", n_samples=n_samples)
            return find_similar_pairs_with_lsh(embeddings, threshold)
        else:
            logger.info("Using dense similarity search", n_samples=n_samples)
            return find_similar_pairs_dense(embeddings, threshold)

    def _create_clusters(
        self, similar_pairs: List[Tuple[int, int, float]], n_items: int
    ) -> List[List[int]]:
        """Create non-overlapping clusters from similar pairs."""
        if not similar_pairs:
            return [[i] for i in range(n_items)]

        adjacency = defaultdict(set)
        for i, j, _ in similar_pairs:
            adjacency[i].add(j)
            adjacency[j].add(i)

        n_nodes = len(adjacency)

        if n_nodes >= LOUVAIN_NODE_THRESHOLD:
            logger.info("Using Louvain community detection", n_nodes=n_nodes)
            return self._louvain_clustering(similar_pairs, n_items)
        else:
            logger.info("Using BFS connected components", n_nodes=n_nodes)
            return self._bfs_clustering(similar_pairs, n_items)

    def _bfs_clustering(
        self, similar_pairs: List[Tuple[int, int, float]], n_items: int
    ) -> List[List[int]]:
        """Build clusters using BFS connected components."""
        adjacency = defaultdict(set)
        for i, j, _ in similar_pairs:
            adjacency[i].add(j)
            adjacency[j].add(i)

        visited = set()
        clusters = []

        for i in range(n_items):
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

        return clusters

    def _louvain_clustering(
        self, similar_pairs: List[Tuple[int, int, float]], n_items: int
    ) -> List[List[int]]:
        """Build clusters using Louvain community detection."""
        try:
            import networkx as nx
            from networkx.algorithms.community import louvain_communities

            G = nx.Graph()
            G.add_nodes_from(range(n_items))

            for i, j, similarity in similar_pairs:
                G.add_edge(i, j, weight=similarity)

            communities = louvain_communities(G, weight="weight", resolution=1.0)

            clusters = [list(community) for community in communities]

            logger.info(
                "Louvain clustering complete",
                n_communities=len(clusters),
                largest_community=max(len(c) for c in clusters) if clusters else 0,
            )

            return clusters

        except ImportError:
            logger.warning("networkx not available, falling back to BFS")
            return self._bfs_clustering(similar_pairs, n_items)
        except Exception as e:
            logger.warning("Louvain failed, falling back to BFS", error=str(e))
            return self._bfs_clustering(similar_pairs, n_items)

    def _create_merged_block_placeholder(
        self, cluster_blocks: List[Dict[str, Any]], iteration: int
    ) -> Dict[str, Any]:
        """Create a merged block placeholder."""
        document_uuid = None
        for block in cluster_blocks:
            if "blockifyDocumentUUID" in block:
                document_uuid = block["blockifyDocumentUUID"]
                break

        merged_block = {
            "type": "merged",
            "blockifyResultUUID": str(uuid.uuid4()),
            "blockifiedTextResult": {
                "name": "",
                "criticalQuestion": "",
                "trustedAnswer": "",
            },
            "hidden": False,
            "exported": False,
            "reviewed": False,
            "blockifyResultsUsed": [block["blockifyResultUUID"] for block in cluster_blocks],
            "_cluster_blocks": cluster_blocks,
            "_iteration": iteration,
        }

        if document_uuid:
            merged_block["blockifyDocumentUUID"] = document_uuid

        return merged_block

    def _create_stats(
        self, starting_count: int, final_count: int, merged_count: int
    ) -> Dict[str, Any]:
        """Create statistics dictionary."""
        reduction_percent = (
            ((starting_count - final_count) / starting_count * 100) if starting_count > 0 else 0
        )

        return {
            "startingBlockCount": starting_count,
            "finalBlockCount": final_count,
            "blocksRemoved": starting_count - final_count + merged_count,
            "blocksAdded": merged_count,
            "blockReductionPercent": round(reduction_percent, 2),
        }

    def _build_intermediate_result(
        self,
        original_blocks: List[Dict[str, Any]],
        hidden_uuids: Set[str],
        merged_blocks: List[Dict[str, Any]],
        starting_count: int,
    ) -> Dict[str, Any]:
        """Build intermediate result structure for saving progress."""
        results = []

        for block in original_blocks:
            hidden_block = block.copy()
            hidden_block["hidden"] = True
            if "_embedding" in hidden_block:
                del hidden_block["_embedding"]
            results.append(hidden_block)

        for block in merged_blocks:
            clean_block = block.copy()
            for key in ["_embedding", "_cluster_blocks", "_iteration"]:
                if key in clean_block:
                    del clean_block[key]
            results.append(clean_block)

        final_count = len(merged_blocks)
        stats = self._create_stats(starting_count, final_count, len(merged_blocks))

        return {
            "schemaVersion": 1,
            "status": "partial",
            "stats": stats,
            "results": results,
        }
