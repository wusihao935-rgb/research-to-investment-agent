from __future__ import annotations

import re
from collections.abc import Callable

import streamlit as st
from dotenv import load_dotenv

from llm_client import LLMClient
from memo_generator import generate_memo


load_dotenv()

st.set_page_config(
    page_title="MiMo Research-to-Investment Agent",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="collapsed",
)


DEFAULT_FORM_STATE = {
    "project_name": "",
    "sector": "",
    "source_text": "",
    "depth": "Standard",
}

EXAMPLE_PAYLOAD = {
    "project_name": "ForgeCode AI",
    "sector": "AI Coding Agent / Developer Tools",
    "source_text": """ForgeCode AI is building an AI-native coding agent for engineering teams that need reliable automation beyond autocomplete. The product accepts feature requests, codebase context, tickets, and technical docs, then produces implementation plans, pull request drafts, regression checks, and release summaries. The company positions itself as an execution layer for software teams rather than a chat interface for developers.

The platform integrates with GitHub, Jira, Slack, and internal documentation systems. Team leads can define review policies, coding standards, and deployment constraints, allowing the agent to follow team-specific workflows. ForgeCode says this configuration layer is critical because enterprises want AI assistance that respects existing engineering processes instead of bypassing them.

From a technical perspective, the system combines long-context retrieval, repository indexing, task decomposition, test-aware execution loops, and model routing across different foundation models. The team claims its main advantage is not proprietary pretraining, but a workflow engine that improves task success rates, traceability, and human-in-the-loop approval for high-risk actions.

The initial target customers are software teams at growth-stage SaaS companies and mid-market enterprises with 50 to 500 engineers. ForgeCode is currently running pilot programs where engineering managers measure reduced backlog time, faster bug triage, and improved documentation coverage. The company expects to monetize through per-seat subscriptions, usage-based compute charges, and enterprise contracts with audit and security features.

The main open questions are whether customers will trust the system for production code changes, whether implementation accuracy remains high in large legacy repositories, and whether the company can defend its workflow layer if foundation model vendors or Git platforms bundle similar capabilities directly into their products.""",
    "depth": "Deep",
}

SECTION_ICONS = {
    "1. Executive Summary": "🧭",
    "2. Project Overview": "🏗️",
    "3. Technology Analysis": "🧪",
    "4. Market & Business Analysis": "💼",
    "5. Risk Analysis": "⚠️",
    "6. Key Due Diligence Questions": "🔍",
    "7. Go / No-Go Recommendation": "🎯",
    "8. Confidence Score": "📈",
    "Token Usage Rationale": "🪙",
}


def _ensure_default_state() -> None:
    for key, value in DEFAULT_FORM_STATE.items():
        st.session_state.setdefault(key, value)
    st.session_state.setdefault("memo_result", None)


def _reset_form() -> None:
    for key, value in DEFAULT_FORM_STATE.items():
        st.session_state[key] = value
    st.session_state["memo_result"] = None


def _load_example() -> None:
    for key, value in EXAMPLE_PAYLOAD.items():
        st.session_state[key] = value
    st.session_state["memo_result"] = None


def _inject_styles() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --bg: #f5f1e8;
    --ink: #102a43;
    --muted: #5d6d7e;
    --card: rgba(255, 255, 255, 0.86);
    --card-strong: rgba(255, 255, 255, 0.96);
    --line: #d7e1ea;
    --accent: #0f766e;
    --accent-soft: #dff5f2;
    --deep: #0f172a;
    --gold: #b7791f;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', 'Segoe UI', sans-serif;
}

code, pre, kbd {
    font-family: 'IBM Plex Mono', monospace !important;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(15, 118, 110, 0.08), transparent 28%),
        radial-gradient(circle at top right, rgba(183, 121, 31, 0.08), transparent 20%),
        linear-gradient(180deg, #f6f3ec 0%, #f5efe6 100%);
    color: var(--ink);
}

.block-container {
    max-width: 1420px;
    padding-top: 2rem;
    padding-bottom: 2.4rem;
}

.hero-card {
    padding: 1.8rem 2rem;
    border-radius: 24px;
    color: white;
    background:
        linear-gradient(140deg, rgba(15, 23, 42, 0.98) 0%, rgba(16, 42, 67, 0.97) 52%, rgba(15, 118, 110, 0.92) 100%);
    box-shadow: 0 24px 60px rgba(15, 23, 42, 0.18);
    margin-bottom: 1rem;
}

.hero-kicker {
    text-transform: uppercase;
    letter-spacing: 0.18em;
    font-size: 0.78rem;
    opacity: 0.82;
    margin-bottom: 0.75rem;
}

.hero-title {
    font-size: 2.15rem;
    font-weight: 700;
    margin-bottom: 0.4rem;
    line-height: 1.15;
}

.hero-subtitle {
    font-size: 1.02rem;
    color: rgba(255, 255, 255, 0.82);
    max-width: 760px;
    line-height: 1.7;
}

.hero-chips {
    margin-top: 1rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.65rem;
}

.hero-chip {
    display: inline-flex;
    align-items: center;
    padding: 0.45rem 0.8rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.15);
    font-size: 0.9rem;
}

.info-card {
    padding: 1rem 1.15rem;
    border-radius: 18px;
    border: 1px solid var(--line);
    background: var(--card);
    box-shadow: 0 10px 32px rgba(16, 42, 67, 0.06);
    margin-bottom: 1rem;
}

.section-kicker {
    text-transform: uppercase;
    letter-spacing: 0.18em;
    font-size: 0.74rem;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 0.35rem;
}

.section-heading {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--deep);
    margin-bottom: 0.25rem;
}

.section-copy {
    color: var(--muted);
    line-height: 1.65;
}

.status-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.5rem 0.85rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid var(--line);
    color: var(--deep);
    font-size: 0.9rem;
    margin-bottom: 0.65rem;
}

.mini-stat-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.75rem;
    margin-top: 0.75rem;
}

.mini-stat {
    background: var(--card-strong);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 0.9rem 0.95rem;
}

.mini-stat-label {
    font-size: 0.8rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.35rem;
}

.mini-stat-value {
    font-size: 1rem;
    font-weight: 700;
    color: var(--deep);
}

.output-placeholder {
    padding: 1.4rem;
    border-radius: 22px;
    border: 1px dashed var(--line);
    background: rgba(255, 255, 255, 0.72);
}

.memo-title-card {
    padding: 1.2rem 1.3rem;
    border-radius: 20px;
    border: 1px solid var(--line);
    background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(250,252,253,0.96) 100%);
    box-shadow: 0 12px 32px rgba(16, 42, 67, 0.06);
    margin-bottom: 1rem;
}

.memo-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--deep);
    margin-bottom: 0.35rem;
}

.memo-caption {
    color: var(--muted);
    line-height: 1.6;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: rgba(255, 255, 255, 0.78);
}

[data-testid="stMarkdownContainer"] ul {
    padding-left: 1.15rem;
}
</style>
""",
        unsafe_allow_html=True,
    )


def _render_hero() -> None:
    st.markdown(
        """
<div class="hero-card">
  <div class="hero-kicker">AI Investment Workflow</div>
  <div class="hero-title">MiMo Research-to-Investment Agent</div>
  <div class="hero-subtitle">
    AI-driven multi-agent system for investment research and decision support.
    Transform unstructured startup, research, and product materials into a structured
    investment memo that is ready for internal review, diligence planning, and demo presentation.
  </div>
  <div class="hero-chips">
    <div class="hero-chip">5 specialized agents</div>
    <div class="hero-chip">Long-context input digestion</div>
    <div class="hero-chip">Structured investment memo output</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="info-card">
  <div class="section-kicker">Product Overview</div>
  <div class="section-heading">Built for investment teams evaluating AI-native products</div>
  <div class="section-copy">
    This demo simulates how an analyst could review a company brief, research abstract, or product note,
    then delegate technical, commercial, and risk analysis to a coordinated multi-agent system.
    The final output is a reusable memo designed for fast decision support.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def _render_runtime_banner(client: LLMClient) -> None:
    runtime = client.get_runtime_config()
    mode = runtime["mode"]

    if mode == "live":
        message = (
            f"Live mode | Model: {runtime['model_name']} | "
            f"Base URL: {runtime['base_url']}"
        )
    elif mode == "fallback-mock":
        message = (
            "Fallback mock mode | Real API call failed, so the app switched to demo-safe output."
        )
    else:
        message = "Mock mode | No API key detected, demo-safe analysis output enabled."

    st.markdown(
        f'<div class="status-chip">{message}</div>',
        unsafe_allow_html=True,
    )

    if mode == "fallback-mock" and runtime.get("last_error"):
        st.caption(f"Last error: `{runtime['last_error']}`")


def _validate_inputs() -> str | None:
    if not st.session_state["project_name"].strip():
        return "Please enter a project or company name."
    if not st.session_state["sector"].strip():
        return "Please enter the technology sector."
    if not st.session_state["source_text"].strip():
        return "Please paste the source material."
    return None


def _build_progress_callback(
    *,
    progress_bar,
    status_box,
) -> Callable[[str, int, str], None]:
    def _callback(stage: str, percent: int, detail: str) -> None:
        progress_bar.progress(percent, text=f"{stage}: {detail}")
        status_box.write(f"**{stage}**  \n{detail}")

    return _callback


def _split_memo_sections(markdown_text: str) -> tuple[str, list[tuple[str, str]]]:
    cleaned = markdown_text.strip()
    if not cleaned:
        return "", []

    title_match = re.match(r"(?ms)^#\s+(.+?)\n", cleaned)
    title = title_match.group(1).strip() if title_match else "Investment Research Memo"
    sections: list[tuple[str, str]] = []

    for part in re.split(r"(?m)^##\s+", cleaned):
        part = part.strip()
        if not part or part == title:
            continue
        lines = part.splitlines()
        heading = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        sections.append((heading, body))

    return title, sections


def _section_icon(heading: str) -> str:
    for key, icon in SECTION_ICONS.items():
        if heading.startswith(key):
            return icon
    return "•"


def _render_analysis_summary() -> None:
    st.markdown(
        """
<div class="info-card">
  <div class="section-kicker">Analysis</div>
  <div class="section-heading">Multi-agent memo generation flow</div>
  <div class="section-copy">
    The pipeline chunks long-form material, extracts investment-relevant facts, evaluates
    technical moat and market potential, scores key risks, and then consolidates those outputs
    into a final investment memo.
  </div>
  <div class="mini-stat-grid">
    <div class="mini-stat">
      <div class="mini-stat-label">Coverage</div>
      <div class="mini-stat-value">Technical, business, risk</div>
    </div>
    <div class="mini-stat">
      <div class="mini-stat-label">LLM Calls</div>
      <div class="mini-stat-value">5 per full memo</div>
    </div>
    <div class="mini-stat">
      <div class="mini-stat-label">Token Logic</div>
      <div class="mini-stat-value">Long context + synthesis</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def _render_empty_output() -> None:
    st.markdown(
        """
<div class="output-placeholder">
  <div class="section-kicker">Output</div>
  <div class="section-heading">Ready for a screenshot-friendly demo run</div>
  <div class="section-copy">
    Click <strong>Load Example</strong> to preload a developer-tools startup scenario, then run the analysis.
    The generated memo will appear here as a polished, sectioned report suitable for GitHub and application materials.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
**Suggested screenshot flow**

1. Load the example scenario.
2. Run the analysis in `Deep` mode.
3. Capture the page with the input panel on the left and the memo cards on the right.
"""
    )


def _render_memo_sections(memo_markdown: str) -> None:
    title, sections = _split_memo_sections(memo_markdown)

    st.markdown(
        f"""
<div class="memo-title-card">
  <div class="section-kicker">Output</div>
  <div class="memo-title">{title}</div>
  <div class="memo-caption">
    Structured memo generated by a coordinated research pipeline. Each section is rendered as its own card
    so the report is easier to review, present, and capture in a screenshot.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    for heading, body in sections:
        icon = _section_icon(heading)
        with st.container(border=True):
            st.markdown(f"### {icon} {heading}")
            if body:
                st.markdown(body)


def _render_run_metrics(memo_result: dict) -> None:
    source_stats = memo_result["source_stats"]
    runtime = memo_result["runtime"]
    mode_label = runtime["mode"].replace("-", " ").title()

    metric_cols = st.columns(4)
    metric_cols[0].metric("Runtime", mode_label)
    metric_cols[1].metric("Estimated Tokens", f"{source_stats['estimated_tokens']:,}")
    metric_cols[2].metric("Context Chunks", f"{source_stats['included_chunks']}/{source_stats['total_chunks']}")
    metric_cols[3].metric("Agent Calls", "5")


def _render_agent_trace(agent_outputs: dict[str, str]) -> None:
    for agent_name, content in agent_outputs.items():
        with st.container(border=True):
            st.markdown(f"#### {agent_name}")
            st.markdown(content)


def _render_output_panel(memo_result: dict) -> None:
    output_actions_left, output_actions_right = st.columns([0.62, 0.38])
    output_actions_left.markdown("### Output")
    output_actions_right.download_button(
        label="Download memo.md",
        data=memo_result["memo_markdown"],
        file_name="memo.md",
        mime="text/markdown",
        use_container_width=True,
    )

    if memo_result["runtime"]["mode"] == "fallback-mock":
        st.warning(
            "This run was completed in fallback mock mode after the live API call failed."
        )

    _render_run_metrics(memo_result)

    memo_tab, trace_tab, raw_tab = st.tabs(
        ["Investment Memo", "Agent Trace", "Raw Markdown"]
    )

    with memo_tab:
        _render_memo_sections(memo_result["memo_markdown"])

    with trace_tab:
        _render_agent_trace(memo_result["agent_outputs"])

    with raw_tab:
        st.code(memo_result["memo_markdown"], language="markdown")


_ensure_default_state()
_inject_styles()
_render_hero()

client = LLMClient()
_render_runtime_banner(client)

left_col, right_col = st.columns([0.92, 1.08], gap="large")

with left_col:
    st.markdown("### Input")
    with st.container(border=True):
        st.text_input(
            "Project / Company Name",
            key="project_name",
            placeholder="e.g. ForgeCode AI, OpenHands, a new multi-agent coding startup",
        )
        st.text_input(
            "Technology Sector",
            key="sector",
            placeholder="e.g. AI Coding Agent, Multimodal AI, Enterprise AI Infra",
        )
        st.text_area(
            "Source Material",
            key="source_text",
            height=360,
            placeholder=(
                "Paste company descriptions, product notes, research abstracts, launch posts, "
                "or investor-facing materials here."
            ),
        )
        st.selectbox(
            "Analysis Depth",
            options=["Basic", "Standard", "Deep"],
            key="depth",
            help="Basic for fast triage, Standard for core diligence, Deep for richer investment questions.",
        )

    st.divider()
    _render_analysis_summary()

    button_col_1, button_col_2, button_col_3 = st.columns(3)
    generate_clicked = button_col_1.button(
        "Generate Investment Memo",
        type="primary",
        use_container_width=True,
    )
    example_clicked = button_col_2.button(
        "Load Example",
        use_container_width=True,
    )
    clear_clicked = button_col_3.button(
        "Clear",
        use_container_width=True,
    )

if example_clicked:
    _load_example()
    st.rerun()

if clear_clicked:
    _reset_form()
    st.rerun()

with right_col:
    memo_result = st.session_state.get("memo_result")

    if generate_clicked:
        validation_error = _validate_inputs()
        if validation_error:
            st.error(validation_error)
        else:
            progress_bar = st.progress(0, text="Preparing long-form material...")
            status_box = st.status("Analysis in progress...", expanded=True)
            callback = _build_progress_callback(
                progress_bar=progress_bar,
                status_box=status_box,
            )

            result = generate_memo(
                project_name=st.session_state["project_name"],
                sector=st.session_state["sector"],
                text=st.session_state["source_text"],
                depth=st.session_state["depth"],
                client=client,
                on_step=callback,
            )
            st.session_state["memo_result"] = result.model_dump()
            memo_result = st.session_state["memo_result"]

            progress_bar.progress(100, text="Investment memo ready.")
            status_box.update(
                label="Analysis complete",
                state="complete",
                expanded=False,
            )

    if memo_result:
        _render_output_panel(memo_result)
    else:
        _render_empty_output()
