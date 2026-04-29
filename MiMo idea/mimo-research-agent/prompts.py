from __future__ import annotations


DEPTH_GUIDANCE = {
    "Basic": "Keep the output concise and decision-oriented. Limit diligence questions to roughly 3.",
    "Standard": "Provide balanced analysis across product, technology, business, and risk. Limit diligence questions to roughly 5.",
    "Deep": "Provide a fuller investment readout with explicit assumptions, sharper judgment, and roughly 8 diligence questions.",
}


STYLE_GUIDE = """
You are a professional venture investor and AI diligence analyst evaluating emerging AI products,
research initiatives, and infrastructure startups.

Follow these rules:
1. Output in professional English Markdown.
2. Keep the tone investment-oriented, analytical, and concise.
3. Distinguish observed facts from inference when evidence is incomplete.
4. Do not fabricate revenue, user numbers, traction data, financing details, or regulatory conclusions.
5. Use compact bullets, clear section logic, and decisive language.
6. You may use very light visual cues such as `✅`, `⚠️`, `🧪`, or `💰` inside bullets, but do not overuse them.
""".strip()


def _shared_context(context) -> str:
    return f"""
Project name: {context.project_name}
Technology sector: {context.sector}
Analysis depth: {context.depth}
Long-context handling note: the source material contains {context.source_stats['original_characters']} characters
and an estimated {context.source_stats['estimated_tokens']} tokens. It was split into
{context.source_stats['total_chunks']} chunks, and {context.source_stats['included_chunks']} representative chunks
were included in this analysis pass.

Source digest:
{context.source_digest}

Depth requirement: {DEPTH_GUIDANCE[context.depth]}
""".strip()


def build_information_extraction_prompts(context) -> tuple[str, str]:
    system_prompt = STYLE_GUIDE
    user_prompt = f"""
{_shared_context(context)}

Task:
Extract the most investment-relevant baseline facts from the source material. Cover:
- project summary
- product
- technology
- target users
- business model
- current stage of progress

Output requirements:
1. Output Markdown only.
2. Use two level-2 headers: `## Extracted Project Facts` and `## Investor-Relevant Signals`.
3. Be concrete. If the material does not directly support a claim, mark it as `Needs validation` or `Inferred`.
4. Avoid vague statements such as "high potential" without evidence.
""".strip()
    return system_prompt, user_prompt


def build_technology_analysis_prompts(context, *, extracted_info: str) -> tuple[str, str]:
    system_prompt = STYLE_GUIDE
    user_prompt = f"""
{_shared_context(context)}

Known extracted facts:
{extracted_info}

Task:
Analyze the opportunity from a technical investment perspective. Cover:
- technical novelty
- defensibility / moat
- implementation feasibility
- dependence on foundation models

Output requirements:
1. Output Markdown only.
2. Use two level-2 headers: `## Technology Analysis` and `## Technical Investment View`.
3. For each judgment, explain the likely basis, assumption, or open validation point.
4. If the moat appears weak or mostly distribution-driven, state that clearly.
""".strip()
    return system_prompt, user_prompt


def build_business_analysis_prompts(context, *, extracted_info: str) -> tuple[str, str]:
    system_prompt = STYLE_GUIDE
    user_prompt = f"""
{_shared_context(context)}

Known extracted facts:
{extracted_info}

Task:
Analyze the opportunity from a business investment perspective. Cover:
- market demand
- business model
- competitive landscape
- monetization path

Output requirements:
1. Output Markdown only.
2. Use two level-2 headers: `## Market & Business Analysis` and `## Business Investment View`.
3. Focus on scalability, buying behavior, and GTM quality rather than generic market enthusiasm.
4. Explicitly identify the most important business assumption that still needs proof.
""".strip()
    return system_prompt, user_prompt


def build_risk_analysis_prompts(
    context,
    *,
    extracted_info: str,
    technology_analysis: str,
    business_analysis: str,
) -> tuple[str, str]:
    system_prompt = STYLE_GUIDE
    user_prompt = f"""
{_shared_context(context)}

Known extracted facts:
{extracted_info}

Technology analysis:
{technology_analysis}

Business analysis:
{business_analysis}

Task:
Analyze the investment risk profile. Cover:
- technical risk
- market risk
- compliance / policy risk
- execution risk

Output requirements:
1. Output Markdown only.
2. Use two level-2 headers: `## Risk Analysis` and `## Risk Weighting`.
3. Do not stay generic. Make clear which 1-2 risks are most material to the investment case.
4. If evidence is thin, explicitly mark the issue as `Needs validation`.
""".strip()
    return system_prompt, user_prompt


def build_memo_generation_prompts(
    context,
    *,
    extracted_info: str,
    technology_analysis: str,
    business_analysis: str,
    risk_analysis: str,
) -> tuple[str, str]:
    system_prompt = STYLE_GUIDE
    user_prompt = f"""
{_shared_context(context)}

Below are the intermediate outputs from the analysis agents.

### Information Extraction Agent
{extracted_info}

### Technology Analysis Agent
{technology_analysis}

### Business Analysis Agent
{business_analysis}

### Risk Analysis Agent
{risk_analysis}

Task:
Synthesize the above analysis into a polished investment memo for an AI-focused investment team.

You must use this exact heading structure:
# Investment Research Memo
## 1. Executive Summary
## 2. Project Overview
## 3. Technology Analysis
## 4. Market & Business Analysis
## 5. Risk Analysis
## 6. Key Due Diligence Questions
## 7. Go / No-Go Recommendation
## 8. Confidence Score
## Token Usage Rationale

Writing requirements:
1. Keep the memo compact, readable, and presentation-ready.
2. Use sharper investment language than a neutral summary would.
3. In `Go / No-Go Recommendation`, give a clear decision: `Go`, `Conditional Go`, or `No-Go`.
4. If the recommendation is `Conditional Go`, explicitly state the gating conditions.
5. In `Confidence Score`, provide a score from 0-100 and explain what is driving confidence or uncertainty.
6. In `Key Due Diligence Questions`, match the current depth requirement: {DEPTH_GUIDANCE[context.depth]}
7. In `Token Usage Rationale`, explain why this workflow naturally consumes meaningful token budget because of long-context digestion, multi-agent analysis, and final synthesis.
8. Keep headings exact, but feel free to use light visual cues inside bullets.
9. Do not add any extra sections or meta commentary.
""".strip()
    return system_prompt, user_prompt
