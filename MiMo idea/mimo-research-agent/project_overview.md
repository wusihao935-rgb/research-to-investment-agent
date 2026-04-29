# Project Overview

## 1. Background

MiMo Research-to-Investment Agent was created to demonstrate a practical, high-value use case for large language models in research-heavy workflows. Early-stage investment teams often review fragmented materials such as startup descriptions, product launch notes, research abstracts, technical blog posts, and internal diligence notes. These materials are dense, uneven in quality, and difficult to convert into a structured first-pass investment view under time pressure.

This project explores how a multi-agent AI system can reduce that friction by transforming long, unstructured material into a concise investment memo that is ready for internal review and follow-up diligence.

## 2. Problem Statement

Most AI research demos stop at summarization. That is not sufficient for investment decision support.

An investment workflow needs:

- extraction of core facts from noisy source material
- separate technical and commercial judgment
- clear articulation of risk
- structured follow-up questions
- an explicit recommendation that can guide next steps

The challenge is that all of this must happen over long-form context, often across multiple source styles, while remaining easy to explain and reproduce.

## 3. System Architecture

The system uses a coordinated five-agent pipeline:

1. Information Extraction Agent
   Converts raw material into an investable fact base.
2. Technology Analysis Agent
   Evaluates novelty, feasibility, moat, and model dependence.
3. Business Analysis Agent
   Evaluates demand, competition, monetization, and go-to-market logic.
4. Risk Analysis Agent
   Surfaces technical, market, compliance, and execution risks.
5. Memo Generation Agent
   Synthesizes all prior outputs into a final investment memo.

This architecture is intentionally modular. Each agent runs as an independent LLM call, which makes the workflow easier to inspect, debug, explain, and later adapt to MiMo API usage policies.

## 4. Technical Highlights

### Multi-agent workflow

The project demonstrates that decision support can be improved by splitting one large reasoning task into multiple specialized sub-tasks. Instead of relying on a single monolithic prompt, the system creates a chain of narrower analytical steps and a final synthesis step.

### Long-context analysis

The app accepts long-form source material and performs lightweight chunking before analysis. This keeps the implementation simple while making token usage explicit and realistic. It also mirrors how real AI products often need to manage heterogeneous input rather than clean prompt-sized text.

### Investment decision support

The output is not just a summary. It is a structured investment memo with a recommendation, confidence score, and due diligence questions. This makes the system easier to position as a product workflow rather than an isolated LLM demo.

## 5. Use Cases

This project is especially relevant for:

- AI startup screening
- technical diligence support
- internal investment memo drafting
- research commercialization review
- AI product demos that need a concrete business outcome

It can also serve as a template for other domains where long-context analysis and structured decision support matter, such as strategy, procurement, or enterprise transformation.

## 6. Token Usage Rationale

Token usage is a central design point in this project.

The system intentionally consumes non-trivial token budget for three reasons:

1. Long input material
   Source material may include startup positioning, product notes, research abstracts, or multi-paragraph launch content. Digesting this well requires meaningful context length.
2. Multiple agent passes
   Each agent runs separately and examines the context from a different analytical angle. This creates better decomposition and traceability, but also increases aggregate token usage.
3. Final synthesis
   The memo generation step must combine all intermediate outputs into a single decision-support artifact, which adds another token-heavy reasoning stage.

This pattern is precisely what makes the project a strong candidate for AI platform support programs: token usage is not decorative, it is directly tied to product value.

## 7. Demo Narrative

The demo experience is designed to be presentation-ready.

- The user opens a polished Streamlit interface.
- The user can load a prebuilt AI startup example with one click.
- The system shows a multi-agent analysis flow while processing.
- The final memo appears in structured report cards on the right side of the interface.
- Agent trace and raw markdown views are also available for transparency.

This makes the project suitable for:

- GitHub portfolio presentation
- application screenshots
- product walkthroughs
- technical interviews
- AI incentive or grant submissions

## 8. Why This Demo Is Strong for Applications

MiMo Research-to-Investment Agent presents a coherent story:

- it solves a real workflow problem
- it uses multiple LLM calls for a good reason
- it has a clear token narrative
- it looks like a product, not just a notebook
- it can run in mock mode for reliable review

That combination makes it a strong demonstration project for any application that values practical AI product thinking, structured token usage, and end-to-end developer execution.
