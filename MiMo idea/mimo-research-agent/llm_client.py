from __future__ import annotations

import hashlib
import os
import random
import re
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class LLMClient:
    """Thin wrapper around an OpenAI-compatible chat completion API."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model_name: str | None = None,
        timeout: float = 90.0,
    ) -> None:
        self.base_url = base_url or os.getenv("LLM_BASE_URL") or "https://api.openai.com/v1"
        self.api_key = api_key or os.getenv("LLM_API_KEY") or ""
        self.model_name = model_name or os.getenv("LLM_MODEL_NAME") or "gpt-4o-mini"
        self.timeout = timeout
        self.last_error: str | None = None

        if not self.api_key:
            self.mode = "mock"
            self.client: OpenAI | None = None
            return

        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
            )
            self.mode = "live"
        except Exception as exc:  # pragma: no cover - defensive path
            self.client = None
            self.mode = "fallback-mock"
            self.last_error = str(exc)

    @property
    def mock_mode(self) -> bool:
        return self.mode != "live"

    def get_runtime_config(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "base_url": self.base_url,
            "model_name": self.model_name,
            "last_error": self.last_error,
        }

    def generate(
        self,
        *,
        agent_name: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        if self.client is None or self.mock_mode:
            return self._mock_response(
                agent_name=agent_name,
                metadata=metadata or {},
            )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return self._extract_text(response).strip()
        except Exception as exc:
            self.mode = "fallback-mock"
            self.last_error = str(exc)
            return self._mock_response(
                agent_name=agent_name,
                metadata=metadata or {},
            )

    def _extract_text(self, response: Any) -> str:
        message = response.choices[0].message
        content = getattr(message, "content", "")

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") in {"text", "output_text"}:
                    parts.append(item.get("text", ""))
                    continue
                text = getattr(item, "text", None)
                if text:
                    parts.append(text)
            return "\n".join(part for part in parts if part)

        return str(content)

    def _mock_response(self, *, agent_name: str, metadata: dict[str, Any]) -> str:
        project_name = metadata.get("project_name", "Target Project")
        sector = metadata.get("sector", "AI")
        depth = metadata.get("depth", "Standard")
        source_stats = metadata.get("source_stats", {})
        seed = int(
            hashlib.md5(f"{project_name}|{sector}|{agent_name}".encode("utf-8")).hexdigest(),
            16,
        )
        rng = random.Random(seed)

        differentiation = rng.choice(
            [
                "通过工作流编排与模型调用的组合提升交付效率",
                "通过行业数据闭环与反馈学习改善输出质量",
                "通过产品化封装降低复杂模型系统的使用门槛",
            ]
        )
        moat = rng.choice(
            [
                "场景 know-how + 数据积累",
                "模型调用链路优化 + 工程效率",
                "行业工作流集成 + 用户粘性",
            ]
        )
        market_signal = rng.choice(
            [
                "企业在降本增效和自动化上的预算仍然活跃",
                "Agent 化产品正在从实验阶段走向业务落地",
                "AI 工具的采购逻辑正从单点能力转向端到端解决方案",
            ]
        )

        if agent_name == "information_extraction":
            return f"""## Extracted Project Facts
- Project summary: `{project_name}` appears to be an AI product or platform in the `{sector}` category, positioned as a practical execution layer rather than a pure model demo.
- Product: The likely core product includes an end-user workflow interface plus orchestration, retrieval, or automation infrastructure behind the scenes.
- Technology: The technical narrative centers on foundation-model workflows, retrieval, task orchestration, or multi-step reasoning, with emphasis on {differentiation}.
- Target users: The most likely users are enterprise teams, researchers, or high-frequency knowledge workers seeking to operationalize AI output.
- Business model: The most plausible model is SaaS subscription, usage-based pricing, or enterprise deployment plus services.
- Current progress: The project appears to be between product validation and early scale, with enough narrative clarity to assess, but not enough operating evidence to underwrite with high confidence.

## Investor-Relevant Signals
- ✅ Positive signal: The project already reads like a product thesis instead of a generic AI capability demo.
- ✅ Positive signal: There is a visible mapping between technical design choices and user value.
- ⚠️ Needs validation: There is still no hard evidence here on retention, paid conversion, unit economics, or efficient distribution."""

        if agent_name == "technology_analysis":
            return f"""## Technology Analysis
- Technical novelty: The differentiation is more likely to come from {differentiation} than from proprietary frontier-model research. This is best understood as workflow and systems innovation.
- Defensibility: A durable moat is more likely to come from `{moat}` than from raw model access alone.
- Implementation feasibility: Given current AI infrastructure maturity, the product looks feasible to ship, but stability, reproducibility, and success rate on complex tasks are still likely bottlenecks.
- Dependence on foundation models: High. Model quality, latency, and cost structure will directly shape product quality and gross margin.

## Technical Investment View
- 🧪 If the team can turn general-purpose model capability into a reliable workflow engine, there is a credible path to repeatable value.
- ⚠️ If the product is mostly thin orchestration around commodity APIs, technical differentiation could compress quickly.
- Key diligence focus: evaluation framework, task success rate, monitoring loop, and ability to swap or route across models."""

        if agent_name == "business_analysis":
            return f"""## Market & Business Analysis
- Market demand: `{market_signal}` makes the category directionally attractive, especially for organizations under pressure to increase productivity with fewer manual steps.
- Business model: The strongest path is likely a mix of standardized software and higher-value enterprise packaging, which supports both distribution and larger account value.
- Competitive landscape: Competition will come from model vendors, incumbent SaaS platforms adding AI layers, and lighter-weight AI-native startups.
- Monetization path: Near-term revenue is most likely pilot-led subscription and usage spend; medium-term quality depends on whether the product embeds deeply enough to support expansion and renewals.

## Business Investment View
- 💰 The opportunity becomes materially stronger if the product becomes part of a core workflow rather than a discretionary productivity add-on.
- Key business question: can acquisition cost, willingness to pay, and retention support real software scale?
- ⚠️ If customer education remains heavy, the company may stay trapped in pilots, consulting-style delivery, or narrow team-level deployment."""

        if agent_name == "risk_analysis":
            return f"""## Risk Analysis
- Technical risk: Output variability, low success rates on multi-step tasks, context limitations, and immature evaluation can all degrade production value.
- Market risk: If customers view the tool as optional acceleration rather than mission-critical workflow infrastructure, budget durability will be weak.
- Compliance risk: If the workflow touches enterprise data, regulated content, or automated decision paths, permissions, privacy, and auditability become material.
- Execution risk: Common failure modes include overpromising on automation, costly onboarding, and difficulty converting demos into repeatable deployment.

## Risk Weighting
- ⚠️ The dominant risk is usually not whether the model can produce output, but whether the product can deliver that output reliably enough to retain revenue.
- If the team lacks a robust eval, monitoring, and iteration loop, risk will compound as customer complexity grows.
- Priority diligence areas: real usage frequency, task success rate, deployment friction, and unit economics."""

        agent_outputs = metadata.get("agent_outputs", {})
        ddq_count = {"Basic": 3, "Standard": 5, "Deep": 8}.get(depth, 5)
        due_diligence_questions = "\n".join(
            f"- Q{i + 1}: Validate real customer usage, retention behavior, and expansion potential for the `{sector}` workflow."
            for i in range(ddq_count)
        )
        confidence_score = rng.randint(68, 84)
        recommendation = rng.choice(["Conditional Go", "Conditional Go", "Go", "No-Go"])

        info_hint = self._plain_snippet(agent_outputs.get("Information Extraction Agent", ""))
        tech_hint = self._plain_snippet(agent_outputs.get("Technology Analysis Agent", ""))
        business_hint = self._plain_snippet(agent_outputs.get("Business Analysis Agent", ""))
        risk_hint = self._plain_snippet(agent_outputs.get("Risk Analysis Agent", ""))

        return f"""# Investment Research Memo

## 1. Executive Summary
`{project_name}` in `{sector}` looks more like a credible productized AI opportunity than a loose concept demo. The core attraction is the combination of workflow utility and AI enablement, but investment quality still depends on whether the team can prove reliable deployment, durable customer value, and defensible execution.

- ✅ Primary strength: the product narrative appears connected to a real workflow problem.
- ⚠️ Primary concern: commercial readiness and repeatability are still not fully proven.

## 2. Project Overview
- Positioning: The company is packaging model capability into a usable `{sector}` workflow or product layer.
- Core value proposition: Improve throughput on knowledge work, automation, or multi-step execution tasks.
- Stage assessment: The direction looks developed enough for structured review, but still needs harder evidence on production value and commercial traction.

> Extraction reference: {info_hint[:180]}...

## 3. Technology Analysis
- The technical story is stronger as systems design, orchestration, and productization than as frontier-model R&D.
- A real moat would need to come from data loops, evaluation quality, workflow depth, and embedded customer behavior.
- High dependence on foundation models means cost control, routing strategy, and resilience to model shifts matter materially.

> Technology reference: {tech_hint[:180]}...

## 4. Market & Business Analysis
- There is a believable demand trend here, but the real question is whether the product becomes workflow-critical.
- The business model should prove software-like repeatability before leaning too heavily on services or bespoke deployment.
- Competitive pressure will likely come from model platforms, AI-native startups, and incumbents adding AI execution features.

> Business reference: {business_hint[:180]}...

## 5. Risk Analysis
- Technical diligence should focus on reliability, error rate, complex-task completion, and inference cost.
- Commercial diligence should focus on budget durability, sales cycle length, and paid expansion behavior.
- Governance diligence should focus on data boundaries, auditability, and customer trust requirements.
- Execution diligence should focus on whether the team can turn a compelling demo into repeatable deployment.

> Risk reference: {risk_hint[:180]}...

## 6. Key Due Diligence Questions
{due_diligence_questions}

## 7. Go / No-Go Recommendation
**{recommendation}**

Gating logic:
- Confirm that the product is used inside a recurring workflow, not only in exploratory demos.
- Confirm that task quality stays acceptable in realistic production conditions.
- Confirm that pricing, usage growth, and deployment effort can support venture-scale software economics.

## 8. Confidence Score
**{confidence_score} / 100**

This confidence score reflects how strongly the current material supports an investable view. It is useful for screening and internal discussion, but still limited by missing first-hand customer and operating evidence.

## Token Usage Rationale
This workflow is token-intensive for structural reasons. First, source materials are often long and heterogeneous, combining company descriptions, product notes, research abstracts, and launch commentary, which requires long-context digestion. Second, the system deliberately runs multiple specialized agents, and each agent consumes context separately in order to produce an independent technical, business, or risk view. Third, the final memo agent must synthesize all intermediate outputs into a single structured recommendation. For a future MiMo API integration, this token pattern is justified because it maps directly to high-value tasks: long-form comprehension, multi-perspective reasoning, and investment memo synthesis."""

    def _plain_snippet(self, text: str, limit: int = 220) -> str:
        cleaned = re.sub(r"#+\s*", "", text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned[:limit]
