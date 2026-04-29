from __future__ import annotations

import math
import re
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field

from agents import (
    AnalysisContext,
    BusinessAnalysisAgent,
    InformationExtractionAgent,
    MemoGenerationAgent,
    RiskAnalysisAgent,
    TechnologyAnalysisAgent,
)
from llm_client import LLMClient


DEPTH_TO_MAX_CHUNKS = {
    "Basic": 2,
    "Standard": 4,
    "Deep": 6,
}

CHUNK_SIZE = 1800


class MemoResult(BaseModel):
    memo_markdown: str = Field(min_length=1)
    agent_outputs: dict[str, str]
    source_stats: dict[str, Any]
    runtime: dict[str, Any]


def generate_memo(
    project_name: str,
    sector: str,
    text: str,
    depth: str,
    client: LLMClient | None = None,
    on_step: Callable[[str, int, str], None] | None = None,
) -> MemoResult:
    normalized_text = _normalize_text(text)
    if not normalized_text:
        raise ValueError("Source text cannot be empty.")

    _notify_step(
        on_step,
        stage="Context Preparation",
        percent=8,
        detail="Chunking long-form material and selecting representative context slices.",
    )

    source_digest, source_stats = _prepare_source_digest(
        normalized_text,
        max_chunks=DEPTH_TO_MAX_CHUNKS.get(depth, 4),
    )

    context = AnalysisContext(
        project_name=project_name.strip(),
        sector=sector.strip(),
        raw_text=normalized_text,
        depth=depth,
        source_digest=source_digest,
        source_stats=source_stats,
    )

    llm_client = client or LLMClient()

    _notify_step(
        on_step,
        stage="Information Extraction Agent",
        percent=24,
        detail="Extracting company, product, user, and business-model facts.",
    )
    info_result = InformationExtractionAgent().run(context, llm_client)

    _notify_step(
        on_step,
        stage="Technology Analysis Agent",
        percent=42,
        detail="Assessing technical novelty, moat, feasibility, and model dependence.",
    )
    tech_result = TechnologyAnalysisAgent().run(
        context,
        llm_client,
        extracted_info=info_result.content,
    )

    _notify_step(
        on_step,
        stage="Business Analysis Agent",
        percent=58,
        detail="Reviewing demand, monetization path, and competitive positioning.",
    )
    business_result = BusinessAnalysisAgent().run(
        context,
        llm_client,
        extracted_info=info_result.content,
    )

    _notify_step(
        on_step,
        stage="Risk Analysis Agent",
        percent=74,
        detail="Scoring technical, market, compliance, and execution risks.",
    )
    risk_result = RiskAnalysisAgent().run(
        context,
        llm_client,
        extracted_info=info_result.content,
        technology_analysis=tech_result.content,
        business_analysis=business_result.content,
    )

    agent_outputs = {
        "Information Extraction Agent": info_result.content,
        "Technology Analysis Agent": tech_result.content,
        "Business Analysis Agent": business_result.content,
        "Risk Analysis Agent": risk_result.content,
    }

    _notify_step(
        on_step,
        stage="Memo Generation Agent",
        percent=92,
        detail="Synthesizing all agent outputs into a structured investment memo.",
    )
    memo_result = MemoGenerationAgent().run(
        context,
        llm_client,
        extracted_info=info_result.content,
        technology_analysis=tech_result.content,
        business_analysis=business_result.content,
        risk_analysis=risk_result.content,
        agent_outputs=agent_outputs,
    )

    return MemoResult(
        memo_markdown=memo_result.content,
        agent_outputs=agent_outputs,
        source_stats=source_stats,
        runtime=llm_client.get_runtime_config(),
    )


def _notify_step(
    callback: Callable[[str, int, str], None] | None,
    *,
    stage: str,
    percent: int,
    detail: str,
) -> None:
    if callback is not None:
        callback(stage, percent, detail)


def _normalize_text(text: str) -> str:
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned


def _prepare_source_digest(text: str, max_chunks: int) -> tuple[str, dict[str, Any]]:
    chunks = _chunk_text(text, chunk_size=CHUNK_SIZE)
    selected = _select_representative_chunks(chunks, max_chunks=max_chunks)

    digest_blocks = []
    for index, chunk_text in selected:
        digest_blocks.append(
            f"### Source Chunk {index + 1}/{len(chunks)}\n{chunk_text.strip()}"
        )

    source_stats = {
        "original_characters": len(text),
        "estimated_tokens": max(1, math.ceil(len(text) / 4)),
        "total_chunks": len(chunks),
        "included_chunks": len(selected),
        "truncated": len(selected) < len(chunks),
        "strategy": "deterministic head/middle/tail chunk selection",
    }

    return "\n\n".join(digest_blocks), source_stats


def _chunk_text(text: str, chunk_size: int) -> list[str]:
    paragraphs = [segment.strip() for segment in text.split("\n") if segment.strip()]
    if not paragraphs:
        return [text]

    chunks: list[str] = []
    current: list[str] = []
    current_length = 0

    for paragraph in paragraphs:
        paragraph_length = len(paragraph) + 1
        if current and current_length + paragraph_length > chunk_size:
            chunks.append("\n".join(current))
            current = [paragraph]
            current_length = paragraph_length
            continue

        if not current and paragraph_length > chunk_size:
            chunks.append(paragraph[:chunk_size])
            remaining = paragraph[chunk_size:]
            while len(remaining) > chunk_size:
                chunks.append(remaining[:chunk_size])
                remaining = remaining[chunk_size:]
            if remaining:
                current = [remaining]
                current_length = len(remaining)
            continue

        current.append(paragraph)
        current_length += paragraph_length

    if current:
        chunks.append("\n".join(current))

    return chunks or [text]


def _select_representative_chunks(chunks: list[str], max_chunks: int) -> list[tuple[int, str]]:
    if len(chunks) <= max_chunks:
        return list(enumerate(chunks))

    preferred_indexes = [0, 1, len(chunks) // 2, len(chunks) - 2, len(chunks) - 1]
    indexes: list[int] = []
    for index in preferred_indexes:
        if 0 <= index < len(chunks) and index not in indexes:
            indexes.append(index)
        if len(indexes) >= max_chunks:
            break

    if len(indexes) < max_chunks:
        for index in range(len(chunks)):
            if index not in indexes:
                indexes.append(index)
            if len(indexes) >= max_chunks:
                break

    indexes.sort()
    return [(index, chunks[index]) for index in indexes]
