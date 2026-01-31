"""Blockify LLM integration for block merging.

This module handles calling the Blockify distill API to merge similar IdeaBlocks.
"""

import json
import time
import re
import requests
from typing import List, Dict, Any, Optional

from app.llm.schemas import MergeRequest, MergeResponse
from app.utils.logging import get_logger
from app.config import settings

logger = get_logger(__name__)


class BlockifyLLM:
    """Blockify LLM integration for merging IdeaBlocks."""

    def __init__(self):
        self.api_key = settings.blockify_api_key
        self.api_url = f"{settings.blockify_base_url.rstrip('/')}/chat/completions"
        self.model = "distill"  # Blockify uses "distill" model for merging
        self.max_completion_tokens = settings.llm_max_completion_tokens
        self.request_timeout = settings.llm_request_timeout
        self.debug_mode = settings.llm_debug

        if not self.api_key:
            raise ValueError("BLOCKIFY_API_KEY environment variable is required")

        if self.debug_mode:
            logger.info(
                "BlockifyLLM initialized",
                api_url=self.api_url,
                model=self.model,
                max_tokens=self.max_completion_tokens,
                timeout=self.request_timeout,
            )

    def merge_cluster(self, request: MergeRequest) -> MergeResponse:
        """Merge a cluster of blocks using Blockify distill API.

        Args:
            request: MergeRequest containing blocks to merge

        Returns:
            MergeResponse with merged content(s) or error
        """
        try:
            prompt = self._create_merge_prompt(request.cluster_blocks)

            if self.debug_mode:
                logger.info(
                    "Sending merge request to Blockify",
                    cluster_size=len(request.cluster_blocks),
                    prompt_preview=prompt[:200],
                )

            raw_content = self._call_blockify_api(prompt)

            if raw_content:
                # Try to parse ALL ideablocks from the response
                all_blocks = self._parse_all_xml_ideablocks(raw_content)

                if all_blocks:
                    logger.info(
                        "Successfully merged cluster",
                        cluster_size=len(request.cluster_blocks),
                        result_blocks=len(all_blocks),
                    )
                    return MergeResponse(
                        success=True,
                        merged_content=all_blocks[0],
                        merged_contents=all_blocks,
                    )

                # Fallback: try single-block parsing
                single_block = self._parse_llm_response(raw_content)
                if single_block:
                    logger.info(
                        "Successfully merged cluster (single block)",
                        cluster_size=len(request.cluster_blocks),
                    )
                    return MergeResponse(
                        success=True,
                        merged_content=single_block,
                        merged_contents=[single_block],
                    )

            logger.error("Failed to get valid response from Blockify")
            return MergeResponse(success=False, error="Invalid response from Blockify")

        except Exception as e:
            logger.error("Error during LLM merge", error=str(e))
            return MergeResponse(success=False, error=str(e))

    def _create_merge_prompt(self, cluster_blocks: List[Dict[str, Any]]) -> str:
        """Create the prompt for merging blocks."""
        xml_content = ""
        for i, block in enumerate(cluster_blocks):
            result = block.get("blockifiedTextResult", {})
            name = result.get("name", f"Block {i+1}")
            question = result.get("criticalQuestion", "")
            answer = result.get("trustedAnswer", "")

            xml_content += (
                f"<ideablock>"
                f"<name>{name}</name>"
                f"<critical_question>{question}</critical_question>"
                f"<trusted_answer>{answer}</trusted_answer>"
                f"</ideablock>"
            )

        return xml_content.strip()

    def _call_blockify_api(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Call Blockify API and return raw content string."""
        for attempt in range(max_retries):
            try:
                payload = {
                    "model": self.model,
                    "messages": [{"role": "system", "content": prompt}],
                    "response_format": {"type": "text"},
                    "temperature": 0.5,
                    "max_completion_tokens": self.max_completion_tokens,
                    "top_p": 1,
                    "frequency_penalty": 0,
                    "presence_penalty": 0,
                }

                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }

                if self.debug_mode:
                    logger.debug(
                        "Blockify API request",
                        attempt=attempt + 1,
                        payload_size=len(json.dumps(payload)),
                    )

                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=self.request_timeout,
                )
                response.raise_for_status()

                response_data = response.json()

                if "choices" in response_data and len(response_data["choices"]) > 0:
                    choice = response_data["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        content = choice["message"]["content"].strip()
                        if self.debug_mode:
                            logger.debug(
                                "Blockify API response",
                                content_length=len(content),
                                tokens_used=response_data.get("usage", {}).get("total_tokens"),
                            )
                        return content

                logger.warning("Unknown response format from Blockify")
                return None

            except KeyboardInterrupt:
                logger.info("Blockify API call interrupted")
                raise

            except Exception as e:
                logger.warning(
                    "Blockify API call failed",
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    error=str(e),
                )
                if attempt == max_retries - 1:
                    raise

                sleep_time = 2 ** attempt
                time.sleep(sleep_time)

        return None

    def _parse_all_xml_ideablocks(self, content: str) -> List[Dict[str, str]]:
        """Parse ALL ideablocks from an XML-like LLM response."""
        ideablocks = []

        try:
            # Find all complete <ideablock>...</ideablock> sections
            ideablock_pattern = r"<ideablock[^>]*>(.*?)</ideablock>"
            matches = re.findall(ideablock_pattern, content, re.DOTALL | re.IGNORECASE)

            for block_content in matches:
                parsed = self._extract_ideablock_fields(block_content)
                if parsed:
                    ideablocks.append(parsed)

            if ideablocks:
                return ideablocks

            # Handle truncated response
            truncated_pattern = r"<ideablock[^>]*>(.*?)(?:</ideablock>|$)"
            truncated_matches = re.findall(truncated_pattern, content, re.DOTALL | re.IGNORECASE)

            for block_content in truncated_matches:
                parsed = self._extract_ideablock_fields(block_content)
                if parsed:
                    ideablocks.append(parsed)
                    logger.warning("Parsed truncated ideablock")

        except Exception as e:
            logger.warning("Error parsing XML ideablocks", error=str(e))

        return ideablocks

    def _extract_ideablock_fields(self, block_content: str) -> Optional[Dict[str, str]]:
        """Extract fields from a single ideablock content."""
        name_match = re.search(
            r"<(?:name|n)>(.*?)</(?:name|n)>", block_content, re.DOTALL | re.IGNORECASE
        )
        question_match = re.search(
            r"<(?:critical_question|criticalQuestion|question)>(.*?)</(?:critical_question|criticalQuestion|question)>",
            block_content,
            re.DOTALL | re.IGNORECASE,
        )
        answer_match = re.search(
            r"<(?:trusted_answer|trustedAnswer|answer)>(.*?)</(?:trusted_answer|trustedAnswer|answer)>",
            block_content,
            re.DOTALL | re.IGNORECASE,
        )

        if name_match and question_match and answer_match:
            parsed = {
                "name": name_match.group(1).strip(),
                "criticalQuestion": question_match.group(1).strip(),
                "trustedAnswer": answer_match.group(1).strip(),
            }
            if self._validate_response_fields(parsed):
                return parsed

        return None

    def _parse_llm_response(self, content: str) -> Optional[Dict[str, str]]:
        """Robustly parse LLM response, handling both JSON and malformed responses."""
        if not content:
            return None

        # Strategy 1: Try direct JSON parsing
        try:
            parsed = json.loads(content)
            if self._validate_response_fields(parsed):
                return parsed
        except json.JSONDecodeError:
            pass

        # Strategy 2: Extract JSON from markdown code blocks
        json_match = re.search(
            r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL | re.IGNORECASE
        )
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                if self._validate_response_fields(parsed):
                    return parsed
            except json.JSONDecodeError:
                pass

        # Strategy 3: Parse XML-like response
        xml_parsed = self._parse_xml_response(content)
        if xml_parsed:
            return xml_parsed

        return None

    def _parse_xml_response(self, content: str) -> Optional[Dict[str, str]]:
        """Parse XML-like response."""
        try:
            name_match = re.search(
                r"<(?:name|n)>(.*?)</(?:name|n)>", content, re.DOTALL | re.IGNORECASE
            )
            question_match = re.search(
                r"<(?:critical_question|criticalQuestion|question)>(.*?)</(?:critical_question|criticalQuestion|question)>",
                content,
                re.DOTALL | re.IGNORECASE,
            )
            answer_match = re.search(
                r"<(?:trusted_answer|trustedAnswer|answer)>(.*?)</(?:trusted_answer|trustedAnswer|answer)>",
                content,
                re.DOTALL | re.IGNORECASE,
            )

            if name_match and question_match and answer_match:
                parsed = {
                    "name": name_match.group(1).strip(),
                    "criticalQuestion": question_match.group(1).strip(),
                    "trustedAnswer": answer_match.group(1).strip(),
                }
                if self._validate_response_fields(parsed):
                    return parsed

        except Exception as e:
            logger.warning("Error parsing XML response", error=str(e))

        return None

    def _validate_response_fields(self, parsed: Dict[str, Any]) -> bool:
        """Validate that response has required fields."""
        required_fields = ["name", "criticalQuestion", "trustedAnswer"]
        return all(
            key in parsed and isinstance(parsed[key], str) and parsed[key].strip()
            for key in required_fields
        )
