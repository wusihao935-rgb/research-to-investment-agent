# MiMo Research-to-Investment Agent

AI-driven multi-agent system for investment research and decision support.

This project turns unstructured startup, research, and product materials into a structured investment memo. It is designed as a lightweight but presentation-ready demo that showcases long-context reasoning, coordinated agent workflows, and a clear token usage rationale for future MiMo API integration.

## What this project does

MiMo Research-to-Investment Agent helps an analyst answer a practical question:

> If I paste in a company brief, research abstract, product launch note, or internal memo, can an AI system turn that into an investable first-pass read?

The app processes long-form text, routes it through specialized analysis agents, and generates a structured investment memo covering:

- executive summary
- project overview
- technology analysis
- market and business analysis
- risk analysis
- key diligence questions
- a clear go / no-go recommendation
- token usage rationale

## Why this project matters

Most AI demos stop at summarization. Investment workflows need more than that.

This project matters because it demonstrates how an AI system can:

- break down a complex research task into specialized sub-analyses
- reason over long, mixed-quality source material
- produce a decision-support artifact rather than a generic chat answer
- make token consumption legible and defensible for an AI product workflow

That makes it a useful demo for AI tooling, research systems, internal copilot workflows, and developer incentive applications focused on meaningful LLM usage.

## Demo positioning

This repository is intentionally built to be:

- easy to run locally
- clean enough to publish on GitHub
- visual enough to capture in screenshots
- structured enough to explain as an AI product demo

## Demo screenshot placeholders

Use these file paths as placeholders in your application materials after you capture screenshots:

- `docs/screenshots/dashboard-overview.png`
- `docs/screenshots/generated-memo.png`
- `docs/screenshots/agent-trace.png`

Suggested captions:

- `dashboard-overview.png`: input form plus product header
- `generated-memo.png`: investment memo cards shown in the right panel
- `agent-trace.png`: intermediate multi-agent outputs and traceability

## Architecture overview

The app uses a five-agent pipeline. Each agent makes its own LLM call so the workflow is explicit, inspectable, and easy to explain.

1. Information Extraction Agent
   Extracts project facts, product shape, users, business model, and stage signals.
2. Technology Analysis Agent
   Evaluates novelty, moat, feasibility, and dependence on large models.
3. Business Analysis Agent
   Evaluates demand, monetization, GTM logic, and competitive pressure.
4. Risk Analysis Agent
   Surfaces technical, market, compliance, and execution risks.
5. Memo Generation Agent
   Synthesizes all prior outputs into a structured investment memo.

Long-form input is chunked before analysis so the workflow visibly reflects long-context processing rather than pretending all source material fits into a trivial prompt.

## Architecture diagram description

The logical flow is:

`Source Material -> Long-Context Chunking -> Information Extraction -> Technology Analysis -> Business Analysis -> Risk Analysis -> Memo Generation -> Investment Memo`

This architecture is intentionally simple enough to understand in one glance, while still showing real multi-step orchestration.

## UI highlights

The Streamlit interface is optimized for product-style demos:

- left panel for input and analysis configuration
- right panel for memo output, agent trace, and raw markdown
- top-level product header and overview card
- demo-safe mock mode when no API key is configured
- one-click example loader for screenshot capture

## Project structure

```text
mimo-research-agent/
  app.py
  llm_client.py
  agents.py
  prompts.py
  memo_generator.py
  project_overview.md
  requirements.txt
  .env.example
  README.md
```

## How to run

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app supports two runtime modes:

- `Live mode`: used when `LLM_API_KEY` is available
- `Mock mode`: used when no API key is configured, or if a live call fails and the app falls back safely

## Environment variables

Create a `.env` file from `.env.example`:

```env
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your_api_key_here
LLM_MODEL_NAME=gpt-4o-mini
```

Fields:

- `LLM_BASE_URL`: OpenAI-compatible base URL
- `LLM_API_KEY`: API key for the target model service
- `LLM_MODEL_NAME`: model name used for chat completion

## How to connect MiMo API

If MiMo exposes an OpenAI-compatible endpoint, no structural code change is required. Update only the environment variables:

```env
LLM_BASE_URL=https://your-mimo-endpoint/v1
LLM_API_KEY=your_mimo_key
LLM_MODEL_NAME=your_mimo_model_name
```

If MiMo later requires custom auth headers or a different payload shape, the only file that should need modification is `llm_client.py`.

## Example demo input

Use the built-in `Load Example` button or paste a similar scenario:

- Project / Company Name: `ForgeCode AI`
- Technology Sector: `AI Coding Agent / Developer Tools`
- Analysis Depth: `Deep`
- Source Material: startup/product description covering product thesis, workflow integration, technical approach, customer segment, and open risks

## Example output

```markdown
# Investment Research Memo

## 1. Executive Summary
ForgeCode AI looks more like a workflow product than a feature demo, but the investment case still depends on repeatable deployment quality and customer trust.

## 7. Go / No-Go Recommendation
Conditional Go

Gating logic:
- confirm recurring usage in real engineering workflows
- confirm production-grade task quality in complex repositories
- confirm that pricing and deployment effort support software-scale economics
```

## Token usage rationale

Token usage is a core part of the product story, not an implementation accident.

This workflow uses meaningful token budget because:

- startup and research materials are often long and multi-source
- the app intentionally runs five specialized agent calls instead of a single flat summary
- the final memo requires synthesis across technical, business, and risk perspectives

That makes this project useful for explaining why an advanced AI workflow deserves non-trivial token allocation.

## How to take demo screenshots

Use this sequence when preparing application materials:

1. Run `streamlit run app.py`
2. Click `Load Example`
3. Keep `Analysis Depth` on `Deep`
4. Click `Generate Investment Memo`
5. Capture the page once the memo cards appear on the right
6. Capture the `Agent Trace` tab as a second screenshot to show multi-agent transparency

Recommended screenshots:

- Screenshot 1: full dashboard with header, left-side inputs, and right-side memo output
- Screenshot 2: right-side memo panel focused on the recommendation and token rationale
- Screenshot 3: agent trace panel showing the five-step workflow

## Demo assets for applications

For application material, also review:

- `project_overview.md` for a professional project summary that can be exported to PDF
- this README for the GitHub-facing explanation

## Notes on mock mode

Mock mode is intentional. It keeps the demo usable when no real API key is present, while preserving the same UI flow and multi-agent architecture.

That makes the repository easier to review, fork, and test.
