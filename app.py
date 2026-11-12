# EquityLens AI
# Copyright © 2026 Keya Dhanani. All rights reserved.
# Independently designed and developed by Keya Dhanani.
# Unauthorized reproduction, redistribution, republication, or creation of a substantially
# similar copy of this original application code is not permitted except where allowed by law
# or applicable platform terms. Third-party libraries, public filings, factual source data,
# company names, and trademarks remain subject to their respective rights and terms.

import gzip
import json
import time
from urllib.parse import urlencode

import pandas as pd
import streamlit as st

from research_data import index_dataset_by_ticker as _index_dataset_by_ticker
from ui_components import section
from views.home import render_home
from research_experience import inject_readability_styles

st.set_page_config(
    page_title="EquityLens AI",
    page_icon="📊",
    layout="wide"
)

_app_run_started = time.perf_counter()

PERFORMANCE_BUDGET_MS = {
    "Home": 2000,
    "Company Research": 3000,
}
NAVIGATION_RERUN_BUDGET_MS = 1000


def _timed_render(page_name, render_callable):
    """Record server-side render duration for one top-level destination."""
    started = time.perf_counter()
    try:
        return render_callable()
    finally:
        elapsed_ms = (time.perf_counter() - started) * 1000
        timings = st.session_state.setdefault(
            "equitylens_page_timings",
            {},
        )
        history = list(timings.get(page_name, []))
        history.append(round(elapsed_ms, 1))
        timings[page_name] = history[-20:]
        st.session_state["equitylens_page_timings"] = timings
        st.session_state["equitylens_last_page_timing"] = {
            "page": page_name,
            "milliseconds": round(elapsed_ms, 1),
        }

st.markdown(
    """
    <style>
/* Compact tool homepage and a stable navigation row. */
.el-tool-hero { padding: 1.7rem 1.8rem; margin: .7rem 0 1rem; }
.el-tool-hero .el-eyebrow { margin-bottom: .8rem; }
.el-tool-hero .el-product-title { font-size: clamp(2rem, 4vw, 3.2rem); line-height: 1.12; }
.el-tool-hero .el-product-subtitle { margin-top: .8rem; font-size: 1rem; max-width: 820px; }
.st-key-main_navigation [role="radiogroup"] {
    gap: .5rem; flex-wrap: wrap; padding: .6rem;
    border: 1px solid var(--el-border); border-radius: 9px; background: var(--el-surface);
}
.st-key-main_navigation label { padding: .3rem .45rem; }

.st-key-top_command_bar {
    position: sticky;
    top: 3.15rem;
    z-index: 950;
    margin: 0 0 1.05rem;
    padding: .72rem .8rem .66rem;
    border: 1px solid rgba(38,54,64,.9);
    border-radius: 10px;
    background: rgba(5,11,14,.94);
    box-shadow: 0 14px 34px rgba(0,0,0,.22);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
}

.st-key-top_command_bar .el-kicker {
    margin: 0 0 .42rem;
    font-size: .69rem;
}

.st-key-top_command_bar [data-testid="stSelectbox"] {
    margin-bottom: .2rem;
}

.st-key-top_command_bar [data-testid="stSelectbox"] > label {
    display: none;
}

.st-key-top_command_bar .st-key-main_navigation [role="radiogroup"] {
    margin-top: .15rem;
    padding: .35rem .4rem;
    background: rgba(9,18,23,.72);
}

@media (max-width: 640px) {
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    .el-tool-hero { padding: 1.3rem; }
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: .8rem !important; }
    [data-testid="stColumn"] { width: 100% !important; flex: 1 1 100% !important; min-width: 0 !important; }
    .st-key-main_navigation [role="radiogroup"] { gap: .2rem; }
    .st-key-top_command_bar {
        top: 2.8rem;
        padding: .58rem .62rem .52rem;
        border-radius: 8px;
    }
    .st-key-top_command_bar .el-kicker { display: none; }
    [data-testid="stDataFrame"] { max-width: 100%; overflow-x: auto; }
}

@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

:root {
    --el-font: "IBM Plex Sans", "Segoe UI", Arial, sans-serif;
    --el-mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
    --el-bg: #050B0E;
    --el-surface: #091217;
    --el-surface-2: #0D171D;
    --el-surface-3: #111C24;
    --el-border: #263640;
    --el-border-soft: rgba(130,154,166,.16);
    --el-text: #EEF3F5;
    --el-muted: #8F9CA6;
    --el-muted-2: #65737D;
    --el-teal: #16C7B2;
    --el-blue: #7DD3FC;
    --el-red: #FF6B72;
}

html, body, .stApp {
    font-family: var(--el-font) !important;
    background: var(--el-bg) !important;
    color: var(--el-text) !important;
}

.stApp {
    font-size: .98rem;
    line-height: 1.55;
    background:
        radial-gradient(circle at 82% 7%, rgba(22,199,178,.055), transparent 24%),
        var(--el-bg) !important;
}

.block-container {
    max-width: 1450px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 4rem !important;
}

[data-testid="stHeader"] {
    background: rgba(5,11,14,.92) !important;
    border-bottom: 1px solid rgba(38,54,64,.45);
}

.material-symbols-rounded,
[data-testid="stIconMaterial"] {
    font-family: "Material Symbols Rounded" !important;
    font-weight: normal !important;
    font-style: normal !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    white-space: nowrap !important;
    word-wrap: normal !important;
    direction: ltr !important;
    font-feature-settings: "liga" !important;
    -webkit-font-feature-settings: "liga" !important;
    -webkit-font-smoothing: antialiased !important;
}

h1,h2,h3,h4,h5,h6,
[data-testid="stHeadingWithActionElements"] {
    font-family: var(--el-font) !important;
    color: var(--el-text) !important;
    font-weight: 600 !important;
    letter-spacing: -.025em !important;
}

p,li,label,input,textarea,button,
[data-testid="stMarkdownContainer"],
[data-testid="stMetricLabel"],
[data-testid="stMetricValue"],
[data-baseweb="tab"] {
    font-family: var(--el-font) !important;
}

/* Original tab layout, refined to feel like the reference design. */
.stTabs [data-baseweb="tab-list"] {
    gap: .25rem !important;
    padding: .35rem .4rem .2rem !important;
    margin: 0 0 1.2rem 0 !important;
    border: 1px solid var(--el-border) !important;
    border-radius: 9px !important;
    background: rgba(9,18,23,.84) !important;
    overflow-x: auto !important;
}

.stTabs [data-baseweb="tab"] {
    min-height: 2.85rem !important;
    padding: 0 .95rem !important;
    border-radius: 6px !important;
    color: var(--el-muted) !important;
    font-size: .88rem !important;
    font-weight: 600 !important;
    letter-spacing: 0 !important;
    white-space: nowrap !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--el-text) !important;
    background: rgba(22,199,178,.045) !important;
}

.stTabs [aria-selected="true"] {
    color: var(--el-text) !important;
    background: rgba(22,199,178,.085) !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    background-color: var(--el-teal) !important;
    height: 2px !important;
}

/* Hero keeps the original placement but adopts the reference site's visual language. */
.el-product-hero {
    position: relative;
    overflow: hidden;
    padding: clamp(2.2rem, 5vw, 4.7rem);
    margin-bottom: 1rem;
    border: 1px solid var(--el-border);
    border-radius: 12px;
    background:
        linear-gradient(rgba(47,67,76,.20) 1px, transparent 1px),
        linear-gradient(90deg, rgba(47,67,76,.20) 1px, transparent 1px),
        radial-gradient(circle at 74% 42%, rgba(22,199,178,.08), transparent 31%),
        #061014;
    background-size: 62px 62px, 62px 62px, auto, auto;
    box-shadow: none;
    isolation: isolate;
}

.el-product-hero::after {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background: linear-gradient(90deg, rgba(5,11,14,0) 55%, rgba(5,11,14,.12) 100%);
}

.el-eyebrow {
    position: relative;
    z-index: 1;
    display: inline-flex;
    align-items: center;
    gap: .55rem;
    margin-bottom: 1.8rem;
    padding: 0;
    border: 0;
    background: transparent;
    color: var(--el-muted);
    font-size: .82rem;
    font-weight: 500;
    letter-spacing: .01em;
    text-transform: none;
}

.el-eyebrow::before {
    content: "";
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--el-teal);
    box-shadow: 0 0 0 4px rgba(22,199,178,.05);
}

.el-product-title {
    position: relative;
    z-index: 1;
    max-width: 1080px;
    margin: 0;
    color: var(--el-text);
    font-size: clamp(3.25rem, 6.3vw, 6.1rem);
    line-height: .99;
    letter-spacing: -.055em;
    font-weight: 600;
}

.el-product-title span {
    color: #7F8B94;
    background: none;
    -webkit-background-clip: initial;
    background-clip: initial;
}

.el-product-subtitle {
    position: relative;
    z-index: 1;
    max-width: 920px;
    margin: 2rem 0 0;
    color: var(--el-muted);
    font-size: clamp(1rem, 1.6vw, 1.2rem);
    line-height: 1.72;
}

.el-badges {
    position: relative;
    z-index: 1;
    display: flex;
    flex-wrap: wrap;
    gap: .55rem;
    margin-top: 1.75rem;
}

.el-badge {
    padding: .42rem .68rem;
    border: 1px solid var(--el-border);
    border-radius: 999px;
    background: rgba(9,18,23,.64);
    color: var(--el-muted);
    font-family: var(--el-mono);
    font-size: .72rem;
    font-weight: 500;
}

.el-availability-grid {
    display: grid;
    grid-template-columns: repeat(4,minmax(0,1fr));
    gap: .7rem;
    margin: -.35rem 0 .55rem;
}

.el-availability-card {
    min-height: 104px;
    padding: .95rem 1rem;
    border: 1px solid var(--el-border);
    border-radius: 9px;
    background: #071014;
}

.el-availability-label {
    color: var(--el-muted);
    font-family: var(--el-mono);
    font-size: .69rem;
    font-weight: 600;
    letter-spacing: .035em;
    text-transform: uppercase;
}

.el-availability-status {
    margin-top: .45rem;
    color: var(--el-text);
    font-size: .98rem;
    font-weight: 600;
}

.el-availability-detail {
    margin-top: .3rem;
    color: var(--el-muted-2);
    font-size: .76rem;
    line-height: 1.4;
}

.el-availability-card.available {
    border-top-color: rgba(22,199,178,.7);
}
.el-availability-card.available .el-availability-status {
    color: var(--el-teal);
}

.el-availability-card.partial {
    border-top-color: rgba(125,211,252,.58);
}
.el-availability-card.partial .el-availability-status {
    color: var(--el-blue);
}

.el-availability-card.missing {
    border-top-color: rgba(101,115,125,.65);
}
.el-availability-card.missing .el-availability-status {
    color: #A7B2B8;
}

.el-overview-grid {
    display: grid;
    grid-template-columns: repeat(2,minmax(0,1fr));
    gap: .75rem;
    margin: .7rem 0 .6rem;
}

.el-overview-card {
    min-height: 150px;
    padding: 1.15rem 1.2rem;
    border: 1px solid var(--el-border);
    border-radius: 9px;
    background: #091217;
}

.el-overview-question {
    color: var(--el-teal);
    font-family: var(--el-mono);
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: .035em;
    text-transform: uppercase;
}

.el-overview-answer {
    margin-top: .65rem;
    color: #D5DEE2;
    font-size: .92rem;
    line-height: 1.62;
}

.el-framework-grid {
    display: grid;
    grid-template-columns: repeat(2,minmax(0,1fr));
    gap: .75rem;
    margin: .8rem 0 1rem;
}

.el-framework-card {
    padding: 1.15rem 1.2rem;
    border: 1px solid var(--el-border);
    border-radius: 9px;
    background: #091217;
}

.el-framework-card.risk {
    border-top-color: rgba(255,107,114,.42);
}

.el-framework-label {
    color: var(--el-teal);
    font-family: var(--el-mono);
    font-size: .7rem;
    font-weight: 600;
    letter-spacing: .04em;
    text-transform: uppercase;
}

.el-framework-question {
    margin-top: .45rem;
    color: var(--el-text);
    font-size: 1rem;
    font-weight: 600;
}

.el-framework-answer {
    margin-top: .55rem;
    color: #D5DEE2;
    font-size: .9rem;
    line-height: 1.62;
}

.el-framework-why {
    margin-top: .75rem;
    padding-top: .7rem;
    border-top: 1px solid var(--el-border-soft);
    color: var(--el-muted);
    font-size: .78rem;
    line-height: 1.52;
}

@media (max-width: 760px) {
    .el-framework-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 700px) {
    .el-overview-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 900px) {
    .el-availability-grid {
        grid-template-columns: repeat(2,minmax(0,1fr));
    }
}

@media (max-width: 560px) {
    .el-availability-grid {
        grid-template-columns: 1fr;
    }
}

/* One bordered trust rail instead of floating cards. */
.el-trust-strip {
    display: grid;
    grid-template-columns: repeat(4,minmax(0,1fr));
    gap: 0;
    margin: .9rem 0 1.45rem;
    border: 1px solid var(--el-border);
    border-radius: 9px;
    overflow: hidden;
    background: #071014;
}

.el-trust-item {
    min-height: 68px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: .8rem 1rem;
    box-sizing: border-box;
    color: var(--el-muted) !important;
    background: transparent !important;
    border: 0 !important;
    border-right: 1px solid var(--el-border) !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    font-size: .84rem;
    font-weight: 500;
    text-align: center;
}

.el-trust-item:last-child { border-right: 0 !important; }

.el-trust-item::before {
    content: "✓";
    width: 16px;
    height: 16px;
    display: inline-grid;
    place-items: center;
    margin-right: .55rem;
    border: 1px solid var(--el-teal);
    border-radius: 50%;
    color: var(--el-teal);
    font-size: .62rem;
}

/* Section typography */
.el-section {
    margin-top: 2rem;
    margin-bottom: .75rem;
}

.el-section-label {
    margin-bottom: .4rem;
    color: var(--el-teal);
    font-family: var(--el-mono);
    text-transform: uppercase;
    letter-spacing: .045em;
    font-size: .73rem;
    font-weight: 600;
}

.el-section-title {
    margin: 0;
    color: var(--el-text);
    font-size: clamp(1.7rem, 3vw, 2.4rem);
    font-weight: 600;
    letter-spacing: -.03em;
}

/* Company/research cards */
.el-company-hero,
.el-summary-card,
.el-change-card,
.el-risk-card,
.el-feature-card,
.el-answer-card,
.el-ai-panel {
    border: 1px solid var(--el-border) !important;
    border-radius: 9px !important;
    background: #091217 !important;
    box-shadow: none !important;
}

.el-company-hero {
    padding: 1.7rem 1.8rem;
    margin: .8rem 0 1.25rem;
}

.el-kicker {
    color: var(--el-teal);
    font-family: var(--el-mono);
    font-size: .74rem;
    font-weight: 600;
    letter-spacing: .035em;
    text-transform: uppercase;
}

.el-company-title {
    margin-top: .45rem;
    color: var(--el-text);
    font-size: clamp(1.85rem,4vw,2.65rem);
    font-weight: 600;
    letter-spacing: -.035em;
}

.el-subtitle {
    max-width: 930px;
    margin: .65rem 0 0;
    color: var(--el-muted);
    font-size: .96rem;
    line-height: 1.7;
}

.el-summary-card {
    min-height: 122px;
    padding: 1.15rem 1.2rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.el-summary-label {
    color: var(--el-muted);
    font-family: var(--el-mono);
    font-size: .72rem;
    text-transform: uppercase;
    letter-spacing: .025em;
}

.el-summary-value {
    margin-top: .55rem;
    color: var(--el-text);
    font-family: var(--el-mono);
    font-size: 1.52rem;
    font-weight: 500;
}

.el-change-card,
.el-risk-card,
.el-feature-card,
.el-answer-card,
.el-ai-panel {
    padding: 1.2rem;
    margin: .65rem 0;
}

.el-change-title,.el-risk-title,.el-feature-title,.el-ai-title {
    color: var(--el-text);
    font-weight: 600;
}

.el-change-copy,.el-feature-copy,.el-ai-copy,.el-answer-copy {
    color: var(--el-muted);
    line-height: 1.65;
}

.el-risk-list { color: var(--el-muted); line-height: 1.55; }

.el-feature-grid {
    display: grid;
    grid-template-columns: repeat(3,minmax(0,1fr));
    gap: .85rem;
    margin: .8rem 0 1.2rem;
}

.el-feature-card { min-height: 170px; padding: 1.35rem; }

.el-feature-num,.el-ai-kicker,.el-answer-kicker {
    color: var(--el-teal);
    font-family: var(--el-mono);
    font-size: .72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .04em;
}

.el-feature-title,.el-ai-title {
    margin-top: .55rem;
    font-size: 1.08rem;
}

.el-feature-copy,.el-ai-copy {
    margin-top: .5rem;
    font-size: .9rem;
}

/* Screenshot-inspired 4-stage workflow, still in the original homepage flow. */
.el-workflow-shell {
    margin: 1rem 0 1.6rem;
    padding: 0;
    border: 1px solid var(--el-border);
    border-radius: 9px;
    overflow: hidden;
    background: #091217;
}

.el-workflow-shell::before { display: none; }

.el-workflow-kicker {
    padding: 1.35rem 1.4rem .3rem;
    color: var(--el-teal);
    font-family: var(--el-mono);
    font-size: .72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .045em;
}

.el-workflow-title {
    padding: 0 1.4rem 1.25rem;
    color: var(--el-text);
    font-size: 1.42rem;
    font-weight: 600;
    letter-spacing: -.025em;
}

.el-workflow-grid {
    display: grid;
    grid-template-columns: repeat(4,minmax(0,1fr));
    gap: 0;
    border-top: 1px solid var(--el-border);
}

.el-workflow-step {
    min-height: 184px;
    padding: 1.3rem;
    background: rgba(5,11,14,.14);
    border-right: 1px solid var(--el-border);
    border-radius: 0;
}

.el-workflow-step:last-child { border-right: 0; }
.el-workflow-step + .el-workflow-step::before { display:none; }

.el-workflow-num {
    color: var(--el-teal);
    font-family: var(--el-mono);
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: .035em;
    text-transform: uppercase;
}

.el-workflow-step-title {
    margin-top: 2rem;
    color: var(--el-text);
    font-size: 1.05rem;
    font-weight: 600;
}

.el-workflow-copy {
    margin-top: .65rem;
    color: var(--el-muted);
    font-size: .86rem;
    line-height: 1.6;
}

/* AI section */
.el-ai-panel {
    position: relative;
    overflow: hidden;
    padding: 1.6rem !important;
    background:
        radial-gradient(circle at 90% 10%,rgba(22,199,178,.07),transparent 28%),
        #091217 !important;
}

.el-ai-panel::after {
    content: "AI";
    position: absolute;
    right: 1.15rem;
    top: .5rem;
    color: rgba(143,156,166,.055);
    font-family: var(--el-mono);
    font-size: 4.2rem;
    font-weight: 600;
}

.el-ai-title { font-size: 1.4rem; max-width: 650px; }
.el-ai-copy { max-width: 820px; }

.el-ai-chips {
    display:flex;
    flex-wrap:wrap;
    gap:.45rem;
    margin-top:1rem;
}

.el-ai-chip {
    padding:.34rem .55rem;
    border:1px solid var(--el-border);
    border-radius:999px;
    color:var(--el-muted);
    font-family:var(--el-mono);
    font-size:.68rem;
}

/* EquityLens structured research workspace */
.el-research-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: .85rem;
    margin: .9rem 0 1.2rem;
}

.el-research-panel {
    min-height: 170px;
    padding: 1.25rem 1.3rem;
    border: 1px solid var(--el-border);
    border-radius: 9px;
    background: #091217;
}

.el-research-panel.wide {
    grid-column: 1 / -1;
    min-height: 0;
}

.el-research-panel-kicker {
    color: var(--el-teal);
    font-family: var(--el-mono);
    font-size: .7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .04em;
}

.el-research-panel-title {
    margin-top: .45rem;
    color: var(--el-text);
    font-size: 1.05rem;
    font-weight: 600;
}

.el-research-panel-copy {
    margin-top: .6rem;
    color: var(--el-muted);
    font-size: .88rem;
    line-height: 1.65;
}

.el-risk-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: .45rem;
    margin-top: .75rem;
}

.el-risk-chip {
    padding: .34rem .55rem;
    border: 1px solid var(--el-border);
    border-radius: 999px;
    color: var(--el-muted);
    font-family: var(--el-mono);
    font-size: .68rem;
}

/* Market Monitor */
.el-market-hero {
    margin: .9rem 0 1.25rem;
    padding: 1.45rem 1.55rem;
    border: 1px solid var(--el-border);
    border-radius: 9px;
    background:
        radial-gradient(circle at 92% 12%, rgba(22,199,178,.07), transparent 32%),
        #091217;
}

.el-market-hero-label {
    color: var(--el-teal);
    font-family: var(--el-mono);
    font-size: .72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .045em;
}

.el-market-hero-title {
    margin-top: .5rem;
    color: var(--el-text);
    font-size: 1.55rem;
    font-weight: 600;
    letter-spacing: -.028em;
}

.el-market-hero-copy {
    margin-top: .55rem;
    max-width: 900px;
    color: var(--el-muted);
    font-size: .9rem;
    line-height: 1.65;
}

.el-move-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: .75rem;
    margin: .85rem 0 1.25rem;
}

.el-move-card {
    padding: 1rem 1.05rem;
    border: 1px solid var(--el-border);
    border-radius: 9px;
    background: #091217;
}

.el-move-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: .75rem;
}

.el-move-ticker {
    color: var(--el-text);
    font-family: var(--el-mono);
    font-weight: 600;
}

.el-move-change {
    font-family: var(--el-mono);
    font-weight: 600;
}

.el-move-change.positive { color: var(--el-teal); }
.el-move-change.negative { color: var(--el-red); }

.el-move-name {
    margin-top: .45rem;
    color: var(--el-muted);
    font-size: .82rem;
}

.el-move-filing {
    margin-top: .75rem;
    padding-top: .7rem;
    border-top: 1px solid var(--el-border);
    color: var(--el-muted);
    font-size: .76rem;
    line-height: 1.5;
}

.el-market-source {
    margin-top: .65rem;
    color: var(--el-muted-2);
    font-family: var(--el-mono);
    font-size: .7rem;
}

/* Market ticker + heat map */
.el-exchange-tape {
    display: grid;
    grid-template-columns: 170px minmax(0, 1fr);
    gap: 0;
    align-items: stretch;
    margin: .95rem 0 .35rem;
    border: 1px solid var(--el-border);
    border-radius: 9px;
    overflow: hidden;
    background: #071014;
    box-shadow: 0 18px 45px rgba(0,0,0,.18);
}
.el-exchange-pill {
    min-height: 72px;
    padding: 0 1.15rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background:
        radial-gradient(circle at 15% 15%, rgba(22,199,178,.12), transparent 45%),
        #081216;
    color: var(--el-text);
    border-right: 1px solid var(--el-border);
    font-family: var(--el-mono);
    font-size: .9rem;
    font-weight: 600;
    letter-spacing: .08em;
}
.el-exchange-pill::before {
    content: "";
    width: 8px;
    height: 8px;
    margin-right: .7rem;
    flex: 0 0 auto;
    border-radius: 50%;
    background: var(--el-teal);
    box-shadow: 0 0 0 4px rgba(22,199,178,.08), 0 0 16px rgba(22,199,178,.32);
}
.el-exchange-pill > span:first-child {
    flex: 1;
}
.el-exchange-chevron {
    color: var(--el-muted);
    font-size: 1rem;
    font-weight: 400;
}
.el-ticker-shell {
    width: 100%;
    min-width: 0;
    min-height: 72px;
    overflow: hidden;
    position: relative;
    display: flex;
    align-items: stretch;
    background:
        linear-gradient(180deg, rgba(255,255,255,.018), rgba(255,255,255,0)),
        #071014;
}
.el-ticker-shell::before,
.el-ticker-shell::after {
    content: "";
    position: absolute;
    top: 0;
    bottom: 0;
    width: 38px;
    z-index: 2;
    pointer-events: none;
}
.el-ticker-shell::before {
    left: 0;
    background: linear-gradient(90deg, #071014 0%, rgba(7,16,20,0) 100%);
}
.el-ticker-shell::after {
    right: 0;
    background: linear-gradient(270deg, #071014 0%, rgba(7,16,20,0) 100%);
}
.el-ticker-track {
    display: flex;
    width: max-content;
    animation: elTickerScroll 52s linear infinite;
    will-change: transform;
}
.el-ticker-shell:hover .el-ticker-track {
    animation-play-state: paused;
}
.el-ticker-item {
    min-height: 72px;
    display: flex;
    align-items: center;
    gap: .8rem;
    padding: 0 1.3rem;
    border-right: 1px solid rgba(130,154,166,.17);
    white-space: nowrap;
    color: var(--el-text);
    font-family: var(--el-font);
    transition: background .18s ease;
}
.el-ticker-item:hover {
    background: rgba(22,199,178,.035);
}
.el-ticker-company {
    max-width: 190px;
    overflow: hidden;
    text-overflow: ellipsis;
    color: #B7C2C8;
    font-size: .75rem;
    font-weight: 500;
    letter-spacing: .01em;
    text-transform: uppercase;
}
.el-ticker-symbol {
    min-width: 50px;
    color: var(--el-text);
    font-family: var(--el-mono);
    font-size: .88rem;
    font-weight: 600;
    letter-spacing: .025em;
}
.el-ticker-price {
    min-width: 76px;
    color: #D9E1E5;
    font-family: var(--el-mono);
    font-size: .84rem;
    font-weight: 500;
}
.el-ticker-change {
    min-width: 86px;
    font-family: var(--el-mono);
    font-size: .82rem;
    font-weight: 600;
}
.el-ticker-arrow {
    display: inline-block;
    margin-right: .3rem;
    font-size: .72rem;
}
.el-ticker-change.positive {
    color: var(--el-teal);
}
.el-ticker-change.negative {
    color: var(--el-red);
}
.el-ticker-change.flat {
    color: var(--el-muted);
}
.el-market-delay {
    margin: .3rem 0 1.45rem;
    display: flex;
    justify-content: flex-end;
    color: var(--el-muted-2);
    font-family: var(--el-mono);
    font-size: .67rem;
}
.el-heatmap-head {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1rem;
    margin: .9rem 0 .55rem;
}
.el-heatmap-copy {
    max-width: 720px;
    color: var(--el-muted);
    font-size: .83rem;
}
.el-heatmap-legend {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: .55rem;
    color: var(--el-muted);
    font-family: var(--el-mono);
    font-size: .67rem;
}
.el-legend-item {
    display: inline-flex;
    align-items: center;
    gap: .3rem;
}
.el-legend-swatch {
    width: 10px;
    height: 10px;
    border-radius: 2px;
}
@keyframes elTickerScroll {
    from { transform: translateX(0); }
    to { transform: translateX(-50%); }
}
@media (max-width: 900px) {
    .el-exchange-tape {
        grid-template-columns: 1fr;
    }
    .el-exchange-pill {
        min-height: 46px;
        border-right: 0;
        border-bottom: 1px solid var(--el-border);
    }
    .el-ticker-shell,
    .el-ticker-item {
        min-height: 64px;
    }
    .el-ticker-company {
        max-width: 145px;
    }
}
@media (prefers-reduced-motion: reduce) {
    .el-ticker-track {
        animation: none;
    }
}


/* Market news */
.el-news-shell {
    margin: .9rem 0 1.4rem;
}
.el-news-topline {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: .7rem;
    color: var(--el-muted);
    font-family: var(--el-mono);
    font-size: .7rem;
}
.el-news-live {
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    color: var(--el-teal);
    font-weight: 600;
    letter-spacing: .03em;
    text-transform: uppercase;
}
.el-news-live::before {
    content: "";
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--el-teal);
    box-shadow: 0 0 0 4px rgba(22,199,178,.08);
}
.el-news-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: .8rem;
}
.el-news-card {
    min-height: 190px;
    padding: 1.05rem 1.1rem 1rem;
    display: flex;
    flex-direction: column;
    border: 1px solid var(--el-border);
    border-radius: 9px;
    background:
        linear-gradient(180deg, rgba(255,255,255,.015), transparent),
        #091217;
    text-decoration: none !important;
    transition: transform .14s ease, border-color .14s ease, background .14s ease;
}
.el-news-card:hover {
    transform: translateY(-2px);
    border-color: rgba(22,199,178,.5);
    background:
        radial-gradient(circle at 92% 8%, rgba(22,199,178,.06), transparent 34%),
        #0A151A;
}
.el-news-card.featured {
    grid-column: span 2;
    min-height: 225px;
    padding: 1.25rem 1.3rem 1.15rem;
}
.el-news-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: .6rem;
    margin-bottom: .8rem;
}
.el-news-source {
    color: var(--el-teal);
    font-family: var(--el-mono);
    font-size: .66rem;
    font-weight: 600;
    letter-spacing: .04em;
    text-transform: uppercase;
}
.el-news-topic {
    padding: .22rem .42rem;
    border: 1px solid var(--el-border);
    border-radius: 999px;
    color: var(--el-muted);
    font-family: var(--el-mono);
    font-size: .61rem;
    white-space: nowrap;
}
.el-news-headline {
    color: var(--el-text);
    font-size: 1rem;
    font-weight: 600;
    line-height: 1.45;
    letter-spacing: -.018em;
}
.el-news-card.featured .el-news-headline {
    max-width: 820px;
    font-size: 1.35rem;
    line-height: 1.35;
}
.el-news-visual {
    position: relative;
    overflow: hidden;
    min-height: 104px;
    margin: .95rem 0 .75rem;
    padding: .8rem .85rem;
    border: 1px solid var(--el-border-soft);
    border-radius: 8px;
    background:
        linear-gradient(rgba(125,211,252,.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(125,211,252,.035) 1px, transparent 1px),
        radial-gradient(circle at 88% 18%, rgba(22,199,178,.08), transparent 38%),
        #071014;
    background-size: 22px 22px, 22px 22px, auto, auto;
}
.el-news-card.featured .el-news-visual {
    min-height: 132px;
    margin-top: 1.05rem;
}
.el-news-visual-kicker {
    position: relative;
    z-index: 2;
    color: var(--el-muted-2);
    font-family: var(--el-mono);
    font-size: .59rem;
    letter-spacing: .04em;
    text-transform: uppercase;
}
.el-news-viz-stats {
    position: relative;
    z-index: 2;
    display: flex;
    flex-wrap: wrap;
    gap: .65rem;
    margin-top: .55rem;
}
.el-news-viz-stat {
    min-width: 66px;
}
.el-news-viz-label {
    color: var(--el-muted);
    font-family: var(--el-mono);
    font-size: .58rem;
}
.el-news-viz-value {
    margin-top: .12rem;
    color: var(--el-text);
    font-family: var(--el-mono);
    font-size: .76rem;
    font-weight: 600;
}
.el-news-viz-value.positive { color: var(--el-teal); }
.el-news-viz-value.negative { color: var(--el-red); }
.el-news-viz-bars {
    position: absolute;
    right: .8rem;
    bottom: .75rem;
    left: .8rem;
    height: 33px;
    display: flex;
    align-items: flex-end;
    gap: 5px;
    opacity: .62;
    pointer-events: none;
}
.el-news-viz-bar {
    flex: 1;
    min-width: 4px;
    border-radius: 2px 2px 0 0;
    background: linear-gradient(180deg, rgba(22,199,178,.95), rgba(22,199,178,.18));
}
.el-news-viz-line {
    position: absolute;
    inset: auto 0 0 0;
    width: 100%;
    height: 54px;
    opacity: .58;
    pointer-events: none;
}
.el-news-viz-line polyline {
    fill: none;
    stroke: #16C7B2;
    stroke-width: 2;
    vector-effect: non-scaling-stroke;
}
.el-news-viz-line .el-news-viz-area {
    fill: rgba(22,199,178,.06);
    stroke: none;
}
.el-news-spacer {
    flex: 1;
    min-height: .8rem;
}
.el-news-footer {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: .7rem;
    padding-top: .75rem;
    border-top: 1px solid var(--el-border-soft);
}
.el-news-time {
    color: var(--el-muted-2);
    font-family: var(--el-mono);
    font-size: .64rem;
}
.el-news-read {
    color: var(--el-blue);
    font-family: var(--el-mono);
    font-size: .67rem;
    font-weight: 600;
}
@media (max-width: 900px) {
    .el-news-grid {
        grid-template-columns: 1fr;
    }
    .el-news-card.featured {
        grid-column: span 1;
    }
}

/* Native Streamlit surfaces */
div[data-testid="stMetric"] {
    background:#091217 !important;
    border:1px solid var(--el-border) !important;
    border-radius:9px !important;
    padding:1rem 1.05rem !important;
    box-shadow:none !important;
}

div[data-testid="stMetricLabel"] {
    color:var(--el-muted) !important;
    font-family:var(--el-mono) !important;
    font-size:.76rem !important;
}

div[data-testid="stMetricValue"] {
    color:var(--el-text) !important;
    font-family:var(--el-mono) !important;
    font-weight:500 !important;
}

div[data-baseweb="select"] > div,
div[data-baseweb="base-input"],
textarea,input {
    background:#091217 !important;
    border-color:var(--el-border) !important;
    border-radius:7px !important;
    color:var(--el-text) !important;
}

.stSelectbox label,.stMultiSelect label,.stTextInput label {
    color:var(--el-muted) !important;
}

.stButton > button,
.stLinkButton > a,
.stDownloadButton > button {
    min-height:2.85rem !important;
    border:1px solid var(--el-border) !important;
    border-radius:7px !important;
    background:#081116 !important;
    color:var(--el-text) !important;
    box-shadow:none !important;
    font-weight:600 !important;
}

.stButton > button:hover,
.stLinkButton > a:hover,
.stDownloadButton > button:hover {
    border-color:rgba(22,199,178,.7) !important;
    color:var(--el-text) !important;
}

button:focus-visible,
a:focus-visible,
input:focus-visible,
textarea:focus-visible,
[role="radio"]:focus-visible,
[role="option"]:focus-visible {
    outline:2px solid var(--el-teal) !important;
    outline-offset:2px !important;
    box-shadow:0 0 0 3px rgba(22,199,178,.10) !important;
}

.stButton > button[kind="primary"] {
    background:var(--el-teal) !important;
    border-color:var(--el-teal) !important;
    color:#03110F !important;
}

div[data-testid="stDataFrame"] {
    border:1px solid var(--el-border) !important;
    border-radius:8px !important;
    overflow:hidden !important;
    background:#091217 !important;
}

div[data-testid="stExpander"] {
    border:1px solid var(--el-border) !important;
    border-radius:8px !important;
    background:#091217 !important;
}

div[data-testid="stAlert"] {
    border:1px solid var(--el-border) !important;
    border-radius:8px !important;
    background:#0B151B !important;
    color:var(--el-text) !important;
}

[data-testid="stChatMessage"] {
    border:1px solid var(--el-border) !important;
    border-radius:9px !important;
    background:#091217 !important;
    padding:.75rem !important;
}

.stCaption,small {
    color:var(--el-muted) !important;
    font-size:.76rem !important;
    line-height:1.45 !important;
}

div[data-baseweb="select"] > div,
div[data-baseweb="base-input"],
textarea,
input {
    min-height:2.75rem !important;
}

div[role="radiogroup"] {
    gap:.35rem !important;
}

@media (max-width: 700px) {
    .block-container {
        padding-left:.75rem !important;
        padding-right:.75rem !important;
    }

    .stButton > button,
    .stLinkButton > a,
    .stDownloadButton > button {
        min-height:2.95rem !important;
        padding:.6rem .8rem !important;
    }

    div[role="radiogroup"] {
        display:flex !important;
        flex-wrap:wrap !important;
        align-items:stretch !important;
    }

    div[role="radiogroup"] label {
        min-height:2.6rem !important;
        display:flex !important;
        align-items:center !important;
    }

    div[data-testid="stDataFrame"] {
        max-width:100% !important;
        overflow-x:auto !important;
    }

    .el-section-title {
        font-size:clamp(1.45rem,8vw,2rem) !important;
    }

    .el-company-title {
        font-size:clamp(1.7rem,9vw,2.3rem) !important;
    }
}

hr {
    border-color:var(--el-border) !important;
    margin:2rem 0 !important;
}

/* Footer-style principle card added without removing the original methodology/disclosure content. */
.el-evidence-strip {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:1.5rem;
    margin:2rem 0 1rem;
    padding:1.6rem 1.8rem;
    border:1px solid var(--el-border);
    border-radius:9px;
    background:#071014;
}

.el-evidence-title {
    color:var(--el-text);
    font-size:1.4rem;
    font-weight:600;
    letter-spacing:-.025em;
}

.el-evidence-copy {
    margin-top:.35rem;
    color:var(--el-muted);
    font-size:.88rem;
}

.el-evidence-note {
    color:var(--el-muted);
    font-size:.82rem;
    white-space:nowrap;
}

.el-evidence-note span { color:var(--el-teal); }

/* User-first entry points and interpretation layer */
.el-user-intro {
    margin: 1.25rem 0 1.1rem;
}

.el-user-intro-kicker {
    color: var(--el-teal);
    font-family: var(--el-mono);
    font-size: .72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .045em;
    margin-bottom: .45rem;
}

.el-user-intro-title {
    color: var(--el-text);
    font-size: 1.55rem;
    font-weight: 600;
    letter-spacing: -.028em;
}

.el-user-intro-copy {
    margin-top: .4rem;
    max-width: 850px;
    color: var(--el-muted);
    font-size: .92rem;
    line-height: 1.65;
}

.el-intent-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: .75rem;
    margin: 1rem 0 1.6rem;
}

.el-intent-card {
    min-height: 132px;
    padding: 1.15rem;
    border: 1px solid var(--el-border);
    border-radius: 9px;
    background: #091217;
    box-sizing: border-box;
}

.el-intent-card:hover {
    border-color: rgba(22,199,178,.55);
    background: rgba(22,199,178,.035);
}

.el-intent-label {
    color: var(--el-teal);
    font-family: var(--el-mono);
    font-size: .69rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .04em;
}

.el-intent-title {
    margin-top: .6rem;
    color: var(--el-text);
    font-size: .98rem;
    font-weight: 600;
}

.el-intent-copy {
    margin-top: .42rem;
    color: var(--el-muted);
    font-size: .82rem;
    line-height: 1.5;
}

.el-quick-read {
    margin: 1.1rem 0 1.4rem;
    padding: 1.25rem 1.35rem;
    border: 1px solid var(--el-border);
    border-left: 3px solid var(--el-teal);
    border-radius: 9px;
    background: #091217;
}

.el-quick-read-kicker {
    color: var(--el-teal);
    font-family: var(--el-mono);
    font-size: .7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .045em;
}

.el-quick-read-title {
    margin-top: .45rem;
    color: var(--el-text);
    font-size: 1.1rem;
    font-weight: 600;
}

.el-quick-read-copy {
    margin-top: .55rem;
    color: var(--el-muted);
    line-height: 1.7;
    font-size: .91rem;
}

.el-next-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: .75rem;
    margin: .9rem 0 1.4rem;
}

.el-next-card {
    padding: 1rem 1.05rem;
    border: 1px solid var(--el-border);
    border-radius: 9px;
    background: #091217;
}

.el-next-title {
    color: var(--el-text);
    font-size: .9rem;
    font-weight: 600;
}

.el-next-copy {
    margin-top: .35rem;
    color: var(--el-muted);
    font-size: .79rem;
    line-height: 1.5;
}

@media (max-width:900px) {
    .block-container { padding:1rem .9rem 3rem !important; }
    .el-product-hero { padding:1.6rem 1.2rem; }
    .el-product-title { font-size:clamp(2.55rem,13vw,4.1rem); }
    .el-product-subtitle { font-size:.95rem; }
    .el-trust-strip { grid-template-columns:1fr 1fr; }
    .el-trust-item:nth-child(2) { border-right:0 !important; }
    .el-trust-item:nth-child(1),.el-trust-item:nth-child(2) { border-bottom:1px solid var(--el-border) !important; }
    .el-workflow-grid { grid-template-columns:1fr 1fr; }
    .el-workflow-step:nth-child(2) { border-right:0; }
    .el-workflow-step:nth-child(1),.el-workflow-step:nth-child(2) { border-bottom:1px solid var(--el-border); }
    .el-feature-grid { grid-template-columns:1fr; }
    .el-intent-grid { grid-template-columns:1fr 1fr; }
    .el-next-grid { grid-template-columns:1fr; }
    .el-research-grid { grid-template-columns:1fr; }
    .el-research-panel.wide { grid-column:auto; }
    .el-move-grid { grid-template-columns:1fr; }
    .el-evidence-strip { flex-direction:column; align-items:flex-start; }
    .el-evidence-note { white-space:normal; }
}

.el-loading-panel {
    display: flex;
    align-items: center;
    gap: .85rem;
    min-height: 76px;
    margin: .55rem 0;
    padding: 1rem 1.05rem;
    border: 1px solid var(--el-border);
    border-radius: 9px;
    background: linear-gradient(90deg, rgba(9,18,23,.96), rgba(13,23,29,.88));
}
.el-loading-dot {
    width: 11px;
    height: 11px;
    flex: 0 0 auto;
    border-radius: 50%;
    background: var(--el-teal);
    box-shadow: 0 0 0 0 rgba(22,199,178,.34);
    animation: el-loading-pulse 1.35s ease-out infinite;
}
.el-loading-label {
    color: var(--el-text);
    font-size: .9rem;
    font-weight: 600;
}
.el-loading-detail {
    margin-top: .2rem;
    color: var(--el-muted);
    font-size: .76rem;
    line-height: 1.45;
}
@keyframes el-loading-pulse {
    0% { box-shadow: 0 0 0 0 rgba(22,199,178,.34); }
    70% { box-shadow: 0 0 0 9px rgba(22,199,178,0); }
    100% { box-shadow: 0 0 0 0 rgba(22,199,178,0); }
}
@media (prefers-reduced-motion: reduce) {
    .el-loading-dot { animation: none; }
}

.el-refresh-indicator {
    display: inline-flex;
    align-items: center;
    gap: .38rem;
    margin: .25rem 0 .65rem;
    padding: .38rem .58rem;
    border: 1px solid var(--el-border-soft);
    border-radius: 999px;
    background: rgba(9,18,23,.68);
    color: var(--el-muted);
    font-size: .72rem;
    line-height: 1.35;
}
.el-refresh-indicator strong {
    color: var(--el-text);
    font-weight: 600;
}
.el-refresh-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--el-teal);
    box-shadow: 0 0 0 2px rgba(22,199,178,.12);
}
</style>
    """,
    unsafe_allow_html=True
)



@st.cache_data(show_spinner=False)
def load_json(path):
    """Load repository-backed JSON once per app process.

    Git-backed data changes arrive through a Streamlit redeploy, so repeatedly
    re-reading large static files every 60 seconds only adds startup/rerun cost.
    """
    with open(path, "r") as file:
        return json.load(file)


@st.cache_data(show_spinner=False)
def load_sec_filings():
    """Load the full SEC filing archive only on pages that truly need it."""
    try:
        with gzip.open(
            "data/sec_filings.json.gz",
            "rt",
            encoding="utf-8",
        ) as archive_file:
            return json.load(archive_file)
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        # Transitional fallback until the next SEC refresh writes the compressed
        # archive and removes the legacy plain JSON file.
        return load_json("data/sec_filings.json")


@st.cache_data(show_spinner=False)
def load_sec_company(ticker, company_key=""):
    """Load one company's local SEC shard without opening the full archive.

    During the migration window, fall back to the legacy monolithic archive if
    the per-company shard has not been generated yet.
    """
    safe_ticker = re.sub(
        r"[^A-Z0-9.\-]",
        "",
        str(ticker or "").upper().strip(),
    )
    if safe_ticker:
        try:
            return load_json(f"data/sec_companies/{safe_ticker}.json")
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    if company_key:
        try:
            return load_sec_filings().get(company_key, {})
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    return {}


hand_company_data = load_json("data/company_metrics.json")
generated_company_data = load_json("data/generated_company_metrics.json")

# Keep startup lightweight. Narrative, quarterly, and registration research
# load only when a destination actually needs them.
company_data = {**generated_company_data, **hand_company_data}

@st.cache_data(show_spinner=False)
def load_research_datasets():
    hand_analysis = load_json("data/company_analysis.json")
    hand_quarterly = load_json("data/company_quarterly.json")
    hand_s1 = load_json("data/company_s1.json")
    generated_analysis = load_json("data/generated_company_analysis.json")
    generated_quarterly = load_json("data/generated_company_quarterly.json")
    generated_s1 = load_json("data/generated_company_s1.json")

    analysis = {**generated_analysis, **hand_analysis}
    quarterly = {**generated_quarterly, **hand_quarterly}
    s1 = {**generated_s1, **hand_s1}
    return {
        "analysis": analysis,
        "quarterly": quarterly,
        "s1": s1,
        "analysis_by_ticker": _index_dataset_by_ticker(analysis),
        "quarterly_by_ticker": _index_dataset_by_ticker(quarterly),
        "s1_by_ticker": _index_dataset_by_ticker(s1),
    }

try:
    research_index = load_json("data/research_index.json")
except (FileNotFoundError, json.JSONDecodeError):
    research_index = {"deep_research_tickers": []}

try:
    sec_summary = load_json("data/sec_summary.json")
    sec_summary["_ready"] = True
except (FileNotFoundError, json.JSONDecodeError):
    # The summary is produced by the SEC refresh workflow. Do not fall back to
    # the giant filing archive during startup; keeping the homepage lightweight
    # is more important than a temporary coverage counter during deployment.
    sec_summary = {
        "_ready": False,
        "company_count": 0,
        "synced_companies": 0,
        "companies": {},
        "recent_filings": [],
    }

def _market_cap_dollars(value):
    """Normalize screener market-cap values without importing market_data/yfinance."""
    if value is None or pd.isna(value):
        return None

    text = str(value).strip().replace(",", "").replace("%", "")
    if not text or text in {"-", "N/A", "nan"}:
        return None

    multiplier = 1.0
    suffix = text[-1:].upper()
    if suffix == "K":
        multiplier = 1_000.0
        text = text[:-1]
    elif suffix == "M":
        multiplier = 1_000_000.0
        text = text[:-1]
    elif suffix == "B":
        multiplier = 1_000_000_000.0
        text = text[:-1]
    elif suffix == "T":
        multiplier = 1_000_000_000_000.0
        text = text[:-1]

    try:
        parsed = float(text) * multiplier
    except ValueError:
        return None

    return parsed if suffix in {"K", "M", "B", "T"} else parsed * 1_000_000


try:
    company_universe = pd.read_csv("data/finviz_universe.csv")
except pd.errors.ParserError:
    company_universe = pd.read_csv(
        "data/finviz_universe.csv",
        engine="python",
        on_bad_lines="skip"
    )

required_universe_columns = {
    "Ticker", "Company", "Sector", "Industry", "Country"
}
if not required_universe_columns.issubset(company_universe.columns):
    missing_columns = sorted(
        required_universe_columns - set(company_universe.columns)
    )
    st.error(
        "The expanded company-universe file is missing required columns: "
        + ", ".join(missing_columns)
    )
    st.stop()

for _column in ["Ticker", "Company", "Sector", "Industry", "Country"]:
    company_universe[_column] = (
        company_universe[_column].fillna("").astype(str).str.strip()
    )
if "Market Cap" in company_universe.columns:
    company_universe["Market Cap"] = company_universe["Market Cap"].apply(_market_cap_dollars)
company_universe["Ticker"] = company_universe["Ticker"].str.upper()
company_universe["Coverage Key"] = (
    company_universe["Company"]
    + " ("
    + company_universe["Ticker"]
    + ")"
)
coverage_sectors = sorted(
    [value for value in company_universe["Sector"].dropna().unique().tolist() if value]
)

# Make all 517 companies available throughout the app immediately.
# Generated SEC research fills these stubs over time.
_company_key_by_ticker = {
    str(record.get("ticker", "")).upper(): key
    for key, record in company_data.items()
    if record.get("ticker")
}
for _, _row in company_universe.iterrows():
    _ticker = str(_row.get("Ticker", "")).upper().strip()
    if not _ticker or _ticker in _company_key_by_ticker:
        continue

    _key = str(_row.get("Coverage Key", "")).strip()
    company_data[_key] = {
        "ticker": _ticker,
        "industry": str(_row.get("Industry", "Unclassified")),
        "sector": str(_row.get("Sector", "")),
        "country": str(_row.get("Country", "")),
        "fiscal_year": None,
        "fiscal_year_end": None,
        "source": "SEC research pending",
        "filing_url": "",
        "revenue": None,
        "gross_profit": None,
        "operating_income": None,
        "net_income": None,
        "cash": None,
        "assets": None,
        "history": [],
        "capital_structure": {
            "shares_outstanding": None,
            "shares_as_of": None,
            "total_debt": None,
            "cash_and_investments": None,
            "balance_sheet_as_of": None,
            "source_filing": ""
        }
    }
    _company_key_by_ticker[_ticker] = _key

public_market_data_enabled = True

public_finviz_data_enabled = bool(
    st.secrets.get("PUBLIC_FINVIZ_DATA_ENABLED", False)
    or st.secrets.get("FINVIZ_API_KEY")
    or st.secrets.get("FINVIZ_EXPORT_URL")
)

industries = sorted({
    item.get("industry", "Unclassified")
    for item in company_data.values()
})


SUBGROUPS = {
    "Data Platforms": [
        "Snowflake (SNOW)",
        "MongoDB (MDB)",
        "Datadog (DDOG)",
        "Elastic (ESTC)",
        "Dynatrace (DT)"
    ],
    "Cloud / Network Infrastructure": [
        "Cloudflare (NET)",
        "Akamai (AKAM)"
    ],
    "Cybersecurity": [
        "Rubrik (RBRK)",
        "Palo Alto Networks (PANW)",
        "Zscaler (ZS)"
    ],
    "Enterprise / AI Platforms": [],
    "AI / Compute Infrastructure": [],
    "Endpoint / XDR": [
        "CrowdStrike (CRWD)",
        "SentinelOne (S)"
    ],
    "Identity Security": [
        "Okta (OKTA)"
    ],
    "Network Security": [
        "Palo Alto Networks (PANW)",
        "Fortinet (FTNT)",
        "Zscaler (ZS)"
    ],
    "Exposure Management": [
        "Tenable (TENB)"
    ],
    "Consumer Financial Platforms": [
        "Coinbase (COIN)",
        "Robinhood (HOOD)",
        "Affirm (AFRM)"
    ],
    "Payments / Commerce Infrastructure": [
        "Block (XYZ)",
        "Toast (TOST)",
        "BILL Holdings (BILL)",
        "Marqeta (MQ)"
    ]
}

# Build a unified searchable universe from the 517-company market universe plus
# curated legacy research profiles that are not present in that CSV.
workspace_universe = company_universe.copy()
workspace_known_tickers = set(
    workspace_universe["Ticker"].astype(str).str.upper().tolist()
)
workspace_extra_rows = []

for workspace_key, workspace_record in company_data.items():
    extra_ticker = str(workspace_record.get("ticker", "")).upper().strip()
    if not extra_ticker or extra_ticker in workspace_known_tickers:
        continue

    extra_industry = str(
        workspace_record.get("industry", "Other")
    ).strip() or "Other"
    extra_sector = str(workspace_record.get("sector", "")).strip()

    if not extra_sector:
        if extra_industry in {
            "Cloud & Data Infrastructure Software",
            "Cybersecurity",
        }:
            extra_sector = "Technology"
        elif extra_industry == "Fintech & Digital Finance":
            extra_sector = "Financial"
        else:
            extra_sector = "Other"

    workspace_extra_rows.append({
        "Ticker": extra_ticker,
        "Company": workspace_key.rsplit(" (", 1)[0],
        "Sector": extra_sector,
        "Industry": extra_industry,
        "Country": str(workspace_record.get("country", "")).strip(),
        "Coverage Key": workspace_key,
    })
    workspace_known_tickers.add(extra_ticker)

if workspace_extra_rows:
    workspace_universe = pd.concat(
        [workspace_universe, pd.DataFrame(workspace_extra_rows)],
        ignore_index=True,
        sort=False,
    )


def reset_coverage_selection():
    # A new top-level search takes precedence over a previously selected table row.
    st.session_state.pop("workspace_coverage_table", None)


# One toolbar searches destinations across the website.
navigation_labels = {
    "Home": "Home",
    "Company Research": "Company Research — companies, tickers & SEC analysis",
    "Industry Comparison": "Industry Comparison — industries & peers",
    "Market Monitor": "Market Monitor — company monitor, markets, ticker & heat map",
    "Filings": "Filings — SEC tracker, S-1, 10-K & 10-Q",
    "Learn": "Learn — learn the basics, lessons & financial terms",
}
# Durable copies keep widget choices when their section is not rendered.
saved_choices = st.session_state.setdefault("saved_choices", {})
for choice_key, choice_value in saved_choices.items():
    st.session_state.setdefault(choice_key, choice_value)


def remember_choice(key, value):
    st.session_state[key] = value
    st.session_state["saved_choices"][key] = value


def save_rendered_choices():
    choice_keys = {
        "workspace_company_search", "workspace_sector", "workspace_industry",
        "peer_industry", "peer_subgroup", "peer_companies",
        "nyse_heatmap_sector", "nyse_heatmap_limit", "nyse_heatmap_search",
        "market_monitor_industry", "market_movement_threshold",
        "market_monitor_section", "finviz_min_relative_volume", "finviz_min_abs_change",
        "peer_comparison_focus", "learning_path",
        "sec_tracker_company", "sec_tracker_forms", "sec_registration_company",
        "sec_tracker_search", "sec_tracker_category", "sec_tracker_display_limit",
        "sec_tracker_start_date", "sec_tracker_end_date",
    }
    for key, value in list(st.session_state.items()):
        if key in choice_keys or key.startswith(("workspace_chart_range_", "workspace_section_")):
            st.session_state["saved_choices"][key] = value


def clear_company_filters():
    remember_choice("workspace_sector", "All sectors")
    remember_choice("workspace_industry", "All industries")
    reset_coverage_selection()


def open_company_research(ticker):
    clear_company_filters()
    remember_choice("workspace_company_search", ticker)
    st.session_state["last_research_ticker"] = ticker
    reset_coverage_selection()
    navigate_to("Company Research")


def compare_company(company_key):
    comparison_industry = company_data[company_key].get("industry", "Unclassified")
    peers = [
        name for name, data in company_data.items()
        if data.get("industry", "Unclassified") == comparison_industry
        and name != company_key
    ]
    remember_choice("peer_industry", comparison_industry)
    remember_choice("peer_subgroup", "All current peers")
    remember_choice("peer_companies", [company_key] + peers[:2])
    navigate_to("Industry Comparison")


def retry_company_data(ticker):
    # Import network-heavy modules only when the user explicitly requests a refresh.
    from sec_data import get_sec_company_research
    from market_data import (
        get_company_analyst_data,
        get_company_financial_snapshot,
        get_company_ownership_data,
        get_live_market_data,
        get_major_etf_exposure,
        get_market_history,
    )

    normalized_ticker = str(ticker).upper().strip()
    get_sec_company_research.clear(ticker)
    get_live_market_data.clear([ticker])
    get_company_financial_snapshot.clear(ticker)
    get_company_ownership_data.clear(ticker)
    get_company_analyst_data.clear(ticker)
    get_major_etf_exposure.clear(ticker)
    get_market_history.clear()

    snapshot_prefixes = (
        f"company_core_snapshot::{normalized_ticker}",
        f"company_ownership::{normalized_ticker}",
        f"company_analyst::{normalized_ticker}",
        f"company_etf_exposure::{normalized_ticker}",
        f"company_history::{normalized_ticker}::",
    )
    for key in list(st.session_state):
        if any(
            key == prefix or key.startswith(prefix)
            for prefix in snapshot_prefixes
        ):
            st.session_state.pop(key, None)


def research_link(ticker=None, destination="Company Research"):
    params = {"section": destination}
    if ticker:
        params["ticker"] = ticker
    return "https://equitylens-ai-2h7rd8qluv3bc8sdqf5cu3.streamlit.app/?" + urlencode(params)


global_company_lookup = {}
for _, _search_row in company_universe.iterrows():
    _search_ticker = str(_search_row.get("Ticker", "")).upper().strip()
    _search_company = str(_search_row.get("Company", "")).strip()
    _search_industry = str(_search_row.get("Industry", "")).strip()
    if not _search_ticker:
        continue
    global_company_lookup[f"ticker::{_search_ticker}"] = {
        "ticker": _search_ticker,
        "company": _search_company,
        "industry": _search_industry,
    }

global_search_options = (
    list(navigation_labels)
    + sorted(
        global_company_lookup,
        key=lambda option: (
            global_company_lookup[option]["company"].lower(),
            global_company_lookup[option]["ticker"].lower(),
        ),
    )
)


def format_global_search_option(option):
    if option in navigation_labels:
        return navigation_labels[option]

    company = global_company_lookup.get(option, {})
    ticker = company.get("ticker", "")
    name = company.get("company", ticker)
    industry = company.get("industry", "")
    suffix = f" · {industry}" if industry else ""
    return f"{ticker} · {name}{suffix}"


def navigate_to(destination):
    st.session_state["main_navigation"] = destination


def navigate_from_global_search():
    selected = st.session_state.get("global_search_choice")

    if selected in navigation_labels:
        navigate_to(selected)
        return

    company = global_company_lookup.get(selected, {})
    ticker = company.get("ticker")
    if ticker:
        open_company_research(ticker)


if not st.session_state.get("shared_link_loaded"):
    shared_destination = st.query_params.get("section")
    shared_ticker = str(st.query_params.get("ticker", "")).upper().strip()
    if shared_destination in navigation_labels:
        navigate_to(shared_destination)
    if shared_ticker and shared_ticker in workspace_known_tickers:
        open_company_research(shared_ticker)
    st.session_state["shared_link_loaded"] = True

st.session_state.setdefault("main_navigation", "Home")
inject_readability_styles(st)

with st.container(key="top_command_bar"):
    st.markdown(
        '<div class="el-kicker">EquityLens AI · Search and navigate</div>',
        unsafe_allow_html=True,
    )
    st.selectbox(
        "Search EquityLens",
        options=global_search_options,
        index=None,
        format_func=format_global_search_option,
        placeholder="Search a company, ticker, filing area, market view, or section…",
        key="global_search_choice",
        on_change=navigate_from_global_search,
        label_visibility="collapsed",
    )
    active_destination = st.radio(
        "Explore EquityLens",
        options=list(navigation_labels),
        horizontal=True,
        key="main_navigation",
        label_visibility="collapsed",
    )

workspace_search = ""



sec_synced_companies = int(
    sec_summary.get("synced_companies", 0) or 0
)

deep_research_tickers = {
    str(ticker).upper().strip()
    for ticker in research_index.get(
        "deep_research_tickers",
        [],
    )
    if str(ticker).strip()
}

if active_destination == "Home":
    _timed_render(
        "Home",
        lambda: render_home(
        company_universe=company_universe,
        sec_synced_companies=sec_synced_companies,
        sec_summary=sec_summary,
        deep_research_tickers=deep_research_tickers,
        company_data=company_data,
        open_company_research=open_company_research,
        navigate_to=navigate_to,
        research_link=research_link,
        ),
    )


if active_destination == "Industry Comparison":
    from views.industry_comparison import render_industry_comparison

    _research = load_research_datasets()
    company_analysis = _research["analysis"]
    company_quarterly = _research["quarterly"]
    _analysis_by_ticker = _research["analysis_by_ticker"]

    _timed_render(
        "Industry Comparison",
        lambda: render_industry_comparison(
        industries=industries,
        company_data=company_data,
        subgroups=SUBGROUPS,
        public_market_data_enabled=public_market_data_enabled,
        company_quarterly=company_quarterly,
        analysis_by_ticker=_analysis_by_ticker,
        company_analysis=company_analysis,
        remember_choice=remember_choice,
        company_universe=company_universe,
        research_link=research_link,
        ),
    )


if active_destination == "Company Research":
    from views.company_research import render_company_research

    _research = load_research_datasets()
    company_analysis = _research["analysis"]
    company_quarterly = _research["quarterly"]
    company_s1 = _research["s1"]
    _analysis_by_ticker = _research["analysis_by_ticker"]
    _quarterly_by_ticker = _research["quarterly_by_ticker"]
    _s1_by_ticker = _research["s1_by_ticker"]

    # Fill lightweight universe stubs with the matching lazy-loaded records.
    for _key, _record in company_data.items():
        _ticker = str(_record.get("ticker", "")).upper()
        if _ticker in _analysis_by_ticker:
            company_analysis[_key] = _analysis_by_ticker[_ticker]
        if _ticker in _quarterly_by_ticker:
            company_quarterly[_key] = _quarterly_by_ticker[_ticker]
        if _ticker in _s1_by_ticker:
            company_s1[_key] = _s1_by_ticker[_ticker]

    _timed_render(
        "Company Research",
        lambda: render_company_research(
        workspace_universe=workspace_universe,
        company_data=company_data,
        company_analysis=company_analysis,
        company_quarterly=company_quarterly,
        company_s1=company_s1,
        _analysis_by_ticker=_analysis_by_ticker,
        _quarterly_by_ticker=_quarterly_by_ticker,
        _s1_by_ticker=_s1_by_ticker,
        industries=industries,
        load_sec_company=load_sec_company,
        open_company_research=open_company_research,
        reset_coverage_selection=reset_coverage_selection,
        remember_choice=remember_choice,
        clear_company_filters=clear_company_filters,
        compare_company=compare_company,
        retry_company_data=retry_company_data,
        research_link=research_link,
        save_rendered_choices=save_rendered_choices,
        navigate_to=navigate_to,
        ),
    )


if active_destination == "Market Monitor":
    from views.market_monitor import render_market_monitor

    _timed_render(
        "Market Monitor",
        lambda: render_market_monitor(
        public_finviz_data_enabled=public_finviz_data_enabled,
        industries=industries,
        company_data=company_data,
        sec_summary=sec_summary,
        workspace_known_tickers=workspace_known_tickers,
        research_link=research_link,
        ),
    )


if active_destination == "Filings":
    from sec_data import get_sec_company_research
    from views.filings import render_filings

    _timed_render(
        "Filings",
        lambda: render_filings(
        company_universe=company_universe,
        load_sec_filings=load_sec_filings,
        get_sec_company_research=get_sec_company_research,
        ),
    )


if active_destination == "Learn":
    from views.learn import render_learn

    render_learn()


save_rendered_choices()

_app_run_elapsed_ms = round(
    (time.perf_counter() - _app_run_started) * 1000,
    1,
)
st.session_state["equitylens_last_rerun_ms"] = _app_run_elapsed_ms

_debug_flag = str(
    st.query_params.get("debug", "")
).strip().lower()
if _debug_flag in {"1", "true", "yes"}:
    with st.expander("Developer performance diagnostics"):
        timings = st.session_state.get(
            "equitylens_page_timings",
            {},
        )
        rows = []
        for page_name, samples in sorted(timings.items()):
            if not samples:
                continue
            budget = PERFORMANCE_BUDGET_MS.get(
                page_name
            )
            average_ms = round(
                sum(samples) / len(samples),
                1,
            )
            rows.append({
                "Page": page_name,
                "Last render (ms)": samples[-1],
                "Average (ms)": average_ms,
                "Budget (ms)": budget or "—",
                "Budget status": (
                    "Within budget"
                    if budget and samples[-1] <= budget
                    else (
                        "Over budget"
                        if budget
                        else "Monitor"
                    )
                ),
                "Fastest (ms)": min(samples),
                "Slowest (ms)": max(samples),
                "Samples": len(samples),
            })
        if rows:
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption(
                "Navigate to a page to collect timing samples."
            )
        navigation_status = (
            "within target"
            if _app_run_elapsed_ms <= NAVIGATION_RERUN_BUDGET_MS
            else "over target"
        )
        st.caption(
            f"Current full Streamlit rerun: {_app_run_elapsed_ms:,.1f} ms "
            f"({navigation_status}; target < {NAVIGATION_RERUN_BUDGET_MS:,} ms) · "
            "Server-side timing only; browser/network paint time is not included."
        )


st.markdown(
    """
    <div class="el-evidence-strip">
        <div>
            <div class="el-evidence-title">Evidence first. Judgment stays with you.</div>
            <div class="el-evidence-copy">Source it · show the math · show the date · show the uncertainty.</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

trust_cols = st.columns(5)
trust_items = [
    (
        "Primary Source",
        "Original SEC, government, or company disclosure.",
    ),
    (
        "Reported",
        "Value taken from a disclosed source record.",
    ),
    (
        "Calculated",
        "EquityLens formula using reported source values.",
    ),
    (
        "Research Summary",
        "Structured context based on available disclosures.",
    ),
    (
        "Supplemental Data",
        "Market or third-party context with its own update schedule.",
    ),
]
for col, (label, description) in zip(trust_cols, trust_items):
    with col:
        st.markdown(f"**{label}**")
        st.caption(description)

with st.expander("Sources & methodology"):
    st.markdown(
        """
        **Source priority**

        1. SEC EDGAR filings, including 10-K, 10-Q, 8-K, S-1, F-1, 20-F, 6-K, and related amendments
        2. U.S. Bureau of Labor Statistics for inflation, employment, earnings, ECI, and release schedules
        3. U.S. Department of the Treasury for the official daily Treasury par yield curve
        4. Federal Reserve and Federal Reserve Bank of New York for FOMC information, SOFR, and reference rates
        5. Company investor-relations materials and company-reported disclosures
        6. Supplemental market-data/news providers where permitted

        EquityLens keeps reported figures separate from metrics calculated inside the app.
        Material figures should show a reporting period and original-source link when one is available.
        Local-LLM research summaries are qualitative context; reported financial facts are not generated by the model.
        """
    )

with st.expander("Educational disclosure"):
    st.caption(
        """
        EquityLens AI is an educational and research tool built from publicly available
        financial information. It does not provide personalized investment advice,
        investment recommendations, security rankings, or guarantees of future performance.

        Financial and market information can be delayed, incomplete, revised, or affected
        by later filings and restatements. Verify material information against the original
        SEC filing, government release, or company disclosure.

        EquityLens AI is an independent personal research project and is not affiliated with,
        sponsored by, or endorsed by a broker, exchange, issuer, financial institution, or
        similarly named product or service.
        """
    )

st.caption(
    "© 2026 Keya Dhanani · EquityLens AI · Independent educational research project. "
    "Public filings, company names, trademarks, and third-party source materials remain the property of their respective owners."
)
