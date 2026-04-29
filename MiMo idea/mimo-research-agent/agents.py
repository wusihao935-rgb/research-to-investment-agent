from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from llm_client import LLMClient
from prompts import (
    build_business_analysis_prompts,
    build_information_extraction_prompts,
    build_memo_generation_prompts,
    build_risk_analysis_prompts,
    build_technology_analysis_prompts,
)


class AnalysisContext(BaseModel):
    project_name: str = Field(min_length=1)
    sector: str = Field(min_length=1)
    raw_text: str = Field(min_length=1)
    depth: Literal["Basic", "Standard", "Deep"]
    source_digest: str = Field(min_length=1)
    source_stats: dict[str, Any]


class AgentResult(BaseModel):
    agent_name: str
    content: str


class BaseAgent:
    agent_name: str = "base_agent"
    temperature: float = 0.2

    def build_prompts(self, context: AnalysisContext, **kwargs: Any) -> tuple[str, str]:
        raise NotImplementedError

    def run(self, context: AnalysisContext, llm_client: LLMClient, **kwargs: Any) -> AgentResult:
        system_prompt, user_prompt = self.build_prompts(context, **kwargs)
        content = llm_client.generate(
            agent_name=self.agent_name,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=self.temperature,
            metadata={
                "project_name": context.project_name,
                "sector": context.sector,
                "depth": context.depth,
                "source_stats": context.source_stats,
                **kwargs,
            },
        )
        return AgentResult(agent_name=self.agent_name, content=content.strip())


class InformationExtractionAgent(BaseAgent):
    agent_name = "information_extraction"

    def build_prompts(self, context: AnalysisContext, **kwargs: Any) -> tuple[str, str]:
        return build_information_extraction_prompts(context)


class TechnologyAnalysisAgent(BaseAgent):
    agent_name = "technology_analysis"

    def build_prompts(self, context: AnalysisContext, **kwargs: Any) -> tuple[str, str]:
        return build_technology_analysis_prompts(
            context,
            extracted_info=kwargs["extracted_info"],
        )


class BusinessAnalysisAgent(BaseAgent):
    agent_name = "business_analysis"

    def build_prompts(self, context: AnalysisContext, **kwargs: Any) -> tuple[str, str]:
        return build_business_analysis_prompts(
            context,
            extracted_info=kwargs["extracted_info"],
        )


class RiskAnalysisAgent(BaseAgent):
    agent_name = "risk_analysis"

    def build_prompts(self, context: AnalysisContext, **kwargs: Any) -> tuple[str, str]:
        return build_risk_analysis_prompts(
            context,
            extracted_info=kwargs["extracted_info"],
            technology_analysis=kwargs["technology_analysis"],
            business_analysis=kwargs["business_analysis"],
        )


class MemoGenerationAgent(BaseAgent):
    agent_name = "memo_generation"
    temperature = 0.15

    def build_prompts(self, context: AnalysisContext, **kwargs: Any) -> tuple[str, str]:
        return build_memo_generation_prompts(
            context,
            extracted_info=kwargs["extracted_info"],
            technology_analysis=kwargs["technology_analysis"],
            business_analysis=kwargs["business_analysis"],
            risk_analysis=kwargs["risk_analysis"],
        )
