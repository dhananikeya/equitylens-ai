# EquityLens AI
# Copyright © 2026 Keya Dhanani. All rights reserved.
# Independently designed and developed by Keya Dhanani.
# Unauthorized reproduction, redistribution, republication, or creation of a substantially
# similar copy of this original application code is not permitted except where allowed by law
# or applicable platform terms. Third-party libraries, public filings, factual source data,
# company names, and trademarks remain subject to their respective rights and terms.

import json
import io
import html
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import urljoin, urlencode

import requests
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st
from bs4 import BeautifulSoup
from market_tables import render_crisp_table
from sec_data import (
    get_sec_company_research,
    latest_filing_by_forms,
)
from market_data import (
    finviz_market_cap_dollars,
    finviz_numeric,
    get_company_analyst_data,
    get_company_financial_snapshot,
    get_company_ownership_data,
    get_finviz_screener_data,
    get_live_market_data,
    get_major_etf_exposure,
    get_market_history,
    normalize_finviz_screener,
)
from research_data import index_dataset_by_ticker as _index_dataset_by_ticker
from macro_data import (
    format_bls_display,
    get_bloomberg_market_news,
    get_bls_macro_snapshot,
    get_bls_release_calendar,
    get_fed_monetary_updates,
    get_fomc_calendar,
    get_rates_bundle,
    market_provider_error,
    render_market_news_cards,
    render_rates_ticker,
)
from ui_components import render_summary_cards, section
from financial_utils import (
    build_change_notes,
    calc_growth,
    calc_margin,
    choose_income_period,
    financial_period_label,
    format_market_price,
    format_market_volume,
    format_money,
    format_multiple,
    market_return,
    pct,
    quarterly_metrics,
    safe_float,
)
from views.home import render_home
from views.filings import render_filings
from views.learn import render_learn
from views.industry_comparison import render_industry_comparison
from views.market_monitor import render_market_monitor
from research_experience import (
    inject_readability_styles,
    render_home_discovery,
    render_watchlist,
    toggle_watchlist,
    render_company_evidence,
    render_quarterly_comparison,
    render_report_download,
)

st.set_page_config(
    page_title="EquityLens AI",
    page_icon="📊",
    layout="wide"
)

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
@media (max-width: 640px) {
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    .el-tool-hero { padding: 1.3rem; }
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: .8rem !important; }
    [data-testid="stColumn"] { width: 100% !important; flex: 1 1 100% !important; min-width: 0 !important; }
    .st-key-main_navigation [role="radiogroup"] { gap: .2rem; }
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

.stCaption,small { color:var(--el-muted) !important; }

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
    return load_json("data/sec_filings.json")


hand_company_data = load_json("data/company_metrics.json")
hand_company_analysis = load_json("data/company_analysis.json")
hand_company_quarterly = load_json("data/company_quarterly.json")
hand_company_s1 = load_json("data/company_s1.json")

generated_company_data = load_json("data/generated_company_metrics.json")
generated_company_analysis = load_json("data/generated_company_analysis.json")
generated_company_quarterly = load_json("data/generated_company_quarterly.json")
generated_company_s1 = load_json("data/generated_company_s1.json")

# Generated research expands coverage; hand-curated records remain authoritative.
company_data = {**generated_company_data, **hand_company_data}
company_analysis = {**generated_company_analysis, **hand_company_analysis}
company_quarterly = {
    **generated_company_quarterly,
    **hand_company_quarterly
}
company_s1 = {**generated_company_s1, **hand_company_s1}

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
    company_universe["Market Cap"] = company_universe["Market Cap"].apply(finviz_market_cap_dollars)
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

# Normalize research datasets by ticker so company-name capitalization or spelling
# differences never disconnect research from the matching universe record.
_analysis_by_ticker = _index_dataset_by_ticker(company_analysis)
_quarterly_by_ticker = _index_dataset_by_ticker(company_quarterly)
_s1_by_ticker = _index_dataset_by_ticker(company_s1)

# Make all 517 companies available throughout the app immediately.
# Generated SEC research fills these stubs over time.
_company_key_by_ticker = {
    str(record.get("ticker", "")).upper(): key
    for key, record in company_data.items()
    if record.get("ticker")
}
for _ticker, _key in list(_company_key_by_ticker.items()):
    if _ticker in _analysis_by_ticker:
        company_analysis[_key] = _analysis_by_ticker[_ticker]
    if _ticker in _quarterly_by_ticker:
        company_quarterly[_key] = _quarterly_by_ticker[_ticker]
    if _ticker in _s1_by_ticker:
        company_s1[_key] = _s1_by_ticker[_ticker]

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
    company_analysis[_key] = _analysis_by_ticker.get(_ticker, {})
    company_quarterly[_key] = _quarterly_by_ticker.get(_ticker, {})
    company_s1[_key] = _s1_by_ticker.get(_ticker, {})
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
        "finviz_min_relative_volume", "finviz_min_abs_change",
        "sec_tracker_company", "sec_tracker_forms", "sec_registration_company",
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
    get_sec_company_research.clear(ticker)
    get_live_market_data.clear([ticker])
    get_company_financial_snapshot.clear(ticker)
    get_market_history.clear()


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
    st.session_state["toolbar_destination"] = destination


def navigate_from_toolbar():
    selected = st.session_state.get("toolbar_destination")

    if selected in navigation_labels:
        navigate_to(selected)
        return

    company = global_company_lookup.get(selected, {})
    ticker = company.get("ticker")
    if ticker:
        open_company_research(ticker)


def sync_navigation_search():
    st.session_state["toolbar_destination"] = st.session_state["main_navigation"]


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
st.markdown('<div class="el-kicker">EquityLens AI · Free educational research</div>', unsafe_allow_html=True)
st.selectbox(
    "Search EquityLens",
    options=global_search_options,
    index=None,
    format_func=format_global_search_option,
    placeholder="Search companies, tickers, filings, markets, or sections…",
    key="toolbar_destination",
    on_change=navigate_from_toolbar,
)
active_destination = st.radio(
    "Explore EquityLens",
    options=list(navigation_labels),
    horizontal=True,
    key="main_navigation",
    label_visibility="collapsed",
    on_change=sync_navigation_search,
)
workspace_search = ""



sec_synced_companies = int(
    sec_summary.get("synced_companies", 0) or 0
)

deep_research_tickers = {
    str(company_data.get(_key, {}).get("ticker", "")).upper()
    for _key, _analysis in company_analysis.items()
    if _analysis and _analysis.get("business_model")
}
deep_research_tickers.discard("")

if active_destination == "Home":
    render_home(
        company_universe=company_universe,
        sec_synced_companies=sec_synced_companies,
        sec_summary=sec_summary,
        deep_research_tickers=deep_research_tickers,
        company_data=company_data,
        open_company_research=open_company_research,
        navigate_to=navigate_to,
    )


if active_destination == "Industry Comparison":
    render_industry_comparison(
        industries=industries,
        company_data=company_data,
        subgroups=SUBGROUPS,
        public_market_data_enabled=public_market_data_enabled,
        company_quarterly=company_quarterly,
        analysis_by_ticker=_analysis_by_ticker,
        company_analysis=company_analysis,
        remember_choice=remember_choice,
    )


if active_destination == "Company Research":
    section("Company Research", "Company Research Workspace")

    st.caption(
        "Find a company by name or ticker. Start with its summary, then explore the details below."
    )

    def reopen_recent_company(ticker):
        open_company_research(ticker)

    recent_companies = st.session_state.get("recent_companies", [])
    if recent_companies:
        with st.expander("Recently viewed"):
            for recent_ticker, recent_name in recent_companies:
                st.button(
                    f"{recent_name} ({recent_ticker})",
                    key=f"recent_company_{recent_ticker}",
                    on_click=reopen_recent_company,
                    args=(recent_ticker,),
                )
            st.caption("Recent companies are remembered during this visit.")

    workspace_search = st.text_input(
        "Search company or ticker",
        placeholder="e.g. Amazon, AMZN, MongoDB or MDB",
        key="workspace_company_search",
        on_change=reset_coverage_selection,
    )

    workspace_sectors = sorted(
        [
            value
            for value in workspace_universe["Sector"].dropna().unique().tolist()
            if str(value).strip()
        ]
    )

    workspace_filters = st.columns(2)

    with workspace_filters[0]:
        workspace_sector = st.selectbox(
            "Sector",
            ["All sectors"] + workspace_sectors,
            key="workspace_sector",
        )

    if workspace_sector == "All sectors":
        workspace_sector_df = workspace_universe.copy()
    else:
        workspace_sector_df = workspace_universe[
            workspace_universe["Sector"] == workspace_sector
        ].copy()

    workspace_industries = sorted(
        [
            value
            for value in workspace_sector_df["Industry"].dropna().unique().tolist()
            if str(value).strip()
        ]
    )

    if st.session_state.get("workspace_industry", "All industries") not in ["All industries"] + workspace_industries:
        remember_choice("workspace_industry", "All industries")

    with workspace_filters[1]:
        workspace_industry = st.selectbox(
            "Industry",
            ["All industries"] + workspace_industries,
            key="workspace_industry",
        )

    workspace_filtered = workspace_sector_df.copy()
    if workspace_industry != "All industries":
        workspace_filtered = workspace_filtered[
            workspace_filtered["Industry"] == workspace_industry
        ].copy()

    search_text = workspace_search.strip()
    search_pool = workspace_filtered.copy()
    st.caption("Company search uses the sector and industry filters above.")
    st.button("Reset filters", key="research_reset_filters", on_click=clear_company_filters)
    selected_workspace_row = None

    if search_text:
        search_lower = search_text.lower()
        ticker_lower = search_pool["Ticker"].fillna("").astype(str).str.lower()
        company_lower = search_pool["Company"].fillna("").astype(str).str.lower()

        exact_ticker = search_pool[ticker_lower == search_lower]
        exact_company = search_pool[company_lower == search_lower]
        starts_with = search_pool[
            company_lower.str.startswith(search_lower, na=False)
            | ticker_lower.str.startswith(search_lower, na=False)
        ]
        contains = search_pool[
            company_lower.str.contains(search_lower, regex=False, na=False)
            | ticker_lower.str.contains(search_lower, regex=False, na=False)
        ]

        if not exact_ticker.empty:
            search_matches = exact_ticker
        elif not exact_company.empty:
            search_matches = exact_company
        elif not starts_with.empty:
            search_matches = starts_with
        else:
            search_matches = contains

        if not search_matches.empty:
            selected_workspace_row = search_matches.iloc[0]
            if len(search_matches) > 1:
                st.caption(
                    f"{len(search_matches)} matches found. Showing "
                    f"{selected_workspace_row['Company']} "
                    f"({selected_workspace_row['Ticker']}). Keep typing to narrow the result."
                )
        else:
            st.info(f'No company or ticker matched "{search_text}" within the current filters.')
            st.caption("Check the spelling, try a ticker, or reset the filters to search all companies.")
            save_rendered_choices()
            st.stop()

    coverage_pool = search_matches if search_text else workspace_filtered
    coverage_display = coverage_pool[
        [
            column
            for column in [
                "Ticker", "Company", "Sector", "Industry", "Country",
                "Market Cap", "P/E", "Price", "Change",
            ]
            if column in workspace_filtered.columns
        ]
    ].copy().reset_index(drop=True)

    with st.expander(
        f"Matching companies · {len(coverage_pool):,} results",
        expanded=False,
    ):
        st.caption("Select a row to open that company directly in the research workspace.")
        coverage_event = None
        try:
            coverage_event = st.dataframe(
                coverage_display,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                key="workspace_coverage_table",
            )
        except TypeError:
            st.dataframe(
                coverage_display,
                use_container_width=True,
                hide_index=True,
            )

    if coverage_event is not None:
        try:
            selected_rows = list(coverage_event.selection.rows)
        except Exception:
            selected_rows = []
        if selected_rows:
            selected_index = selected_rows[0]
            if 0 <= selected_index < len(coverage_display):
                selected_ticker_from_table = str(
                    coverage_display.iloc[selected_index].get("Ticker", "")
                ).upper()
                table_match = workspace_universe[
                    workspace_universe["Ticker"].astype(str).str.upper()
                    == selected_ticker_from_table
                ]
                if not table_match.empty:
                    selected_workspace_row = table_match.iloc[0]

    if selected_workspace_row is None and not search_text:
        previous_ticker = st.session_state.get("last_research_ticker")
        previous_match = workspace_filtered[
            workspace_filtered["Ticker"].astype(str).str.upper() == previous_ticker
        ]
        if not previous_match.empty:
            selected_workspace_row = previous_match.iloc[0]

    if selected_workspace_row is None:
        if not workspace_filtered.empty:
            selected_workspace_row = workspace_filtered.iloc[0]
        else:
            st.info("No companies match these filters. Reset filters to see the full list.")
            save_rendered_choices()
            st.stop()

    selected_ticker = str(selected_workspace_row.get("Ticker", "")).upper().strip()
    st.session_state["last_research_ticker"] = selected_ticker
    selected_name = str(selected_workspace_row.get("Company", "")).strip()
    st.session_state["recent_companies"] = [
        (selected_ticker, selected_name)
    ] + [
        item for item in st.session_state.get("recent_companies", [])
        if item[0] != selected_ticker
    ][:4]
    selected_sector_name = str(selected_workspace_row.get("Sector", "")).strip()
    selected_industry_name = str(selected_workspace_row.get("Industry", "")).strip()
    selected_country = str(selected_workspace_row.get("Country", "")).strip()

    selected_company_key = next(
        (
            company_name
            for company_name, company in company_data.items()
            if str(company.get("ticker", "")).upper() == selected_ticker
        ),
        str(selected_workspace_row.get("Coverage Key", "")).strip(),
    )

    selected_data = company_data.get(selected_company_key, {})
    selected_analysis = _analysis_by_ticker.get(
        selected_ticker,
        company_analysis.get(selected_company_key, {}),
    )
    selected_qdata = _quarterly_by_ticker.get(
        selected_ticker,
        company_quarterly.get(selected_company_key, {}),
    )
    selected_qm = quarterly_metrics(selected_qdata)
    selected_s1 = _s1_by_ticker.get(
        selected_ticker,
        company_s1.get(selected_company_key, {}),
    )
    selected_latest = selected_qdata.get("latest_quarter", {})

    try:
        with st.spinner("Loading financial statements from Yahoo Finance…"):
            selected_financial_fallback = get_company_financial_snapshot(
                selected_ticker
            )
    except Exception:
        selected_financial_fallback = {}

    selected_fallback_latest = selected_financial_fallback.get(
        "latest", {}
    )
    selected_fallback_history = selected_financial_fallback.get(
        "history", []
    )
    selected_fallback_quarters = selected_financial_fallback.get(
        "quarterly_history", []
    )

    try:
        with st.spinner("Loading company filings from SEC EDGAR…"):
            selected_sec = get_sec_company_research(selected_ticker)
        selected_sec_error = None
    except Exception:
        selected_sec = {}
        selected_sec_error = (
            "SEC EDGAR is temporarily unavailable for this company. "
            "The rest of the workspace will continue to load."
        )

    # The full local SEC archive is intentionally lazy-loaded. Most company
    # sessions use the live per-company SEC request and never touch the large file.
    selected_local_sec = {}
    if not selected_sec.get("filings"):
        try:
            selected_local_sec = load_sec_filings().get(
                selected_company_key,
                {},
            )
        except (FileNotFoundError, json.JSONDecodeError):
            selected_local_sec = {}

    selected_filings = (
        selected_sec.get("filings")
        or selected_local_sec.get("filings")
        or []
    )
    selected_registrations = (
        selected_sec.get("registration_filings")
        or selected_local_sec.get("registration_filings")
        or []
    )

    latest_annual = latest_filing_by_forms(
        selected_filings,
        {"10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"},
    )
    latest_quarter = latest_filing_by_forms(
        selected_filings,
        {"10-Q", "10-Q/A"},
    )
    latest_current = latest_filing_by_forms(
        selected_filings,
        {"8-K", "8-K/A", "6-K", "6-K/A"},
    )
    primary_registration = selected_registrations[0] if selected_registrations else {}

    try:
        with st.spinner("Loading the latest available Yahoo Finance price…"):
            selected_quote = get_live_market_data([selected_ticker]).get(selected_ticker, {})
    except Exception:
        selected_quote = {}

    selected_price = selected_quote.get("close")
    selected_change = selected_quote.get("percent_change")

    selected_market_cap = finviz_numeric(
        selected_workspace_row.get("Market Cap")
    )
    selected_pe = finviz_numeric(selected_workspace_row.get("P/E"))

    filing_badge = "SEC filings available" if selected_filings else "SEC filings unavailable"

    business_summary = selected_analysis.get(
        "business_model",
        "Structured company research is being expanded for this company. "
        "SEC filings and market data remain available in the workspace.",
    )

    st.markdown(
        f"""
        <div class="el-company-hero">
            <div class="el-kicker">
                {html.escape(selected_ticker)} · {html.escape(selected_sector_name)} · {html.escape(selected_industry_name)}
            </div>
            <div class="el-company-title">{html.escape(selected_name)}</div>
            <p class="el-subtitle">{html.escape(str(business_summary))}</p>
            <div class="el-badges">
                <span class="el-badge">{html.escape(selected_country or "Global")}</span>
                <span class="el-badge">{html.escape(filing_badge)}</span>
                <span class="el-badge">Research only</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    research_actions = st.columns(3)
    with research_actions[0]:
        if selected_company_key in company_data and company_data[selected_company_key].get("industry", "Unclassified") in industries:
            st.button(
                "Compare this company",
                key="research_compare_company",
                on_click=compare_company,
                args=(selected_company_key,),
                use_container_width=True,
            )
        else:
            st.caption("Peer comparison is not available for this company's industry yet.")
    with research_actions[1]:
        with st.expander("Share this research"):
            st.caption("Copy this link to open the same company. Data may change as sources update.")
            st.code(research_link(selected_ticker), language=None)

    with research_actions[2]:
        already_saved = selected_ticker in st.session_state.get(
            "education_watchlist", []
        )
        st.button(
            "Remove from research list" if already_saved else "Save to my research list",
            key="company_watchlist_toggle_%s" % selected_ticker,
            on_click=toggle_watchlist,
            args=(st, selected_ticker),
            use_container_width=True,
        )

    if selected_sec_error or selected_price is None or not selected_financial_fallback:
        st.caption("Some source data is unavailable. You can retry without losing your selected company.")
        st.button(
            "Retry company data",
            key="retry_company_data",
            on_click=retry_company_data,
            args=(selected_ticker,),
        )

    header_metrics = st.columns(5)
    header_metrics[0].metric(
        "Price",
        ("$" + f"{selected_price:,.2f}") if selected_price is not None else "N/A",
        f"{selected_change:+.2f}%" if selected_change is not None else None,
    )
    header_metrics[1].metric("Market Cap", format_money(selected_market_cap), help="Share price multiplied by shares outstanding. Market value differs from revenue or cash.")
    header_metrics[2].metric(
        "P/E",
        f"{selected_pe:.1f}x" if selected_pe is not None else "N/A",
        help="Price-to-earnings ratio: share price relative to earnings per share. An unavailable value does not mean zero.",
    )

    income_selection = choose_income_period(selected_data, selected_qdata, selected_financial_fallback)
    workspace_revenue = income_selection["record"].get("revenue")
    workspace_growth = income_selection["growth"]
    revenue_source_label = income_selection["source"]

    header_metrics[3].metric("Revenue", format_money(workspace_revenue), help="Sales before expenses. Check the period shown below before comparing companies.")
    header_metrics[4].metric("Revenue Growth", pct(workspace_growth), help=income_selection["growth_basis"])

    quote_session = selected_quote.get("quote_session")
    quote_retrieved_at = selected_quote.get("retrieved_at")
    st.caption(
        "Price source: Yahoo Finance daily price data · "
        f"Trading session: {quote_session or 'Unavailable'} · "
        f"Retrieved (UTC): {quote_retrieved_at or 'Unavailable'}. Quotes may be delayed."
    )
    st.caption(
        f"Revenue source: {revenue_source_label}. "
        "Market cap and P/E: coverage screener dataset; may have a different update time."
    )

    latest_available_filing = max(
        selected_filings,
        key=lambda filing: str(filing.get("filing_date") or ""),
        default={},
    )
    filing_date = latest_available_filing.get("filing_date") or "Date unavailable"
    filing_form = latest_available_filing.get("form") or "Form unavailable"
    financial_period = income_selection["period"]
    st.caption(
        f"Financial period: {financial_period or 'See Financials for source periods'} · "
        "Market quotes may be delayed. Unavailable figures are not zero."
    )

    section("At a glance", "Research summary")
    summary_columns = st.columns(2)
    with summary_columns[0]:
        st.markdown("**Key risks to explore**")
        summary_risks = selected_analysis.get("key_risk_themes", [])
        if summary_risks:
            for risk in summary_risks[:3]:
                st.write(f"• {risk}")
        else:
            st.caption("Risk summary is still being added. Review Risk Factors in the original filings.")
    with summary_columns[1]:
        st.markdown("**Latest filing available**")
        if latest_available_filing:
            st.write(f"{filing_form} · Filed {filing_date}")
            if latest_available_filing.get("url"):
                st.link_button("Read the original filing", latest_available_filing["url"])
        else:
            st.caption("No filing is available in this feed yet.")
        st.caption("This is the latest filing returned by the source feed.")

    with st.expander("Need help reading these numbers?"):
        st.markdown(
            "**Revenue:** sales before expenses.\n\n"
            "**Operating margin:** operating profit as a percentage of revenue.\n\n"
            "**LTM:** the most recent twelve months of results.\n\n"
            "**YoY:** comparison with the same period one year earlier.\n\n"
            "**10-K / 10-Q:** annual / quarterly SEC reports."
        )
        st.button("Open Learn", key="summary_open_learn", on_click=navigate_to, args=("Learn",))

    render_quarterly_comparison(st, selected_qdata)
    render_company_evidence(
        st, selected_ticker, selected_analysis, selected_filings,
        pct(workspace_growth), financial_period,
    )
    render_report_download(
        st, selected_name, selected_ticker, selected_industry_name,
        selected_sector_name, selected_analysis, selected_filings,
        {
            "Price (Yahoo Finance, may be delayed)": (
                "$" + f"{selected_price:,.2f}"
                if selected_price is not None else "Not available"
            ),
            "Revenue": format_money(workspace_revenue),
            "Revenue growth": pct(workspace_growth),
            "Reporting period": financial_period or "See Financials",
            "Data source": revenue_source_label,
            "Most recent filing": f"{filing_form} · {filing_date}",
        },
    )

    st.markdown("### Explore the complete research workspace")
    st.caption(
        "The detailed data, filings, sources, ownership and peer research below "
        "remain available in their original sections."
    )
    company_section = st.radio(
        "Company sections",
        ["Snapshot", "Financials", "Filings", "Ownership", "Analyst Research", "Peers & ETFs"],
        horizontal=True,
        key=f"workspace_section_{selected_ticker}",
        label_visibility="collapsed",
    )

    if company_section == "Snapshot":
        snapshot_chart_col, snapshot_context_col = st.columns([1.65, 1])

        with snapshot_chart_col:
            st.markdown("**Price Performance**")
            chart_range = st.radio(
                "Range",
                ["1M", "3M", "1Y", "2Y"],
                index=2,
                horizontal=True,
                key=f"workspace_chart_range_{selected_ticker}",
                label_visibility="collapsed",
            )
            try:
                selected_history = get_market_history(
                    selected_ticker,
                    interval="1day",
                    outputsize=None,
                    calendar_range=chart_range,
                )
            except Exception:
                selected_history = pd.DataFrame()

            if not selected_history.empty:
                price_fig = go.Figure(
                    go.Scatter(
                        x=selected_history["datetime"],
                        y=selected_history["close"],
                        mode="lines",
                        name=selected_ticker,
                        line={"color": "#16C7B2", "width": 2},
                    )
                )
                price_fig.update_layout(
                    height=390,
                    margin={"l": 8, "r": 8, "t": 22, "b": 8},
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": "#8F9CA6", "family": "IBM Plex Sans"},
                    hovermode="x unified",
                    showlegend=False,
                    xaxis={"showgrid": False, "zeroline": False, "title": None},
                    yaxis={
                        "gridcolor": "rgba(143,156,166,.12)",
                        "zeroline": False,
                        "title": None,
                        "tickprefix": "$",
                    },
                )
                st.plotly_chart(
                    price_fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
            else:
                st.info("Price history is temporarily unavailable.")

        with snapshot_context_col:
            st.markdown("**Company Snapshot**")
            snapshot_items = [
                ("Primary revenue source", selected_analysis.get("primary_revenue_source", "Research in progress.")),
                ("Customer type", selected_analysis.get("customer_type", "Research in progress.")),
                ("Platform / operating dependency", selected_analysis.get("platform_dependency", "Research in progress.")),
            ]
            for label, value in snapshot_items:
                st.markdown(f"**{label}**")
                st.write(value)

        st.markdown("---")
        snapshot_left, snapshot_right = st.columns(2)

        with snapshot_left:
            st.markdown("**What changed recently**")
            change_notes = build_change_notes(selected_qdata)
            if not change_notes:
                annual_history = selected_data.get("history", []) or selected_fallback_history
                if len(annual_history) >= 2:
                    latest_year = annual_history[-1]
                    prior_year = annual_history[-2]
                    annual_growth = calc_growth(
                        latest_year.get("revenue"),
                        prior_year.get("revenue"),
                    )
                    if annual_growth is not None:
                        change_notes = [(
                            "Annual revenue",
                            f"Revenue changed {annual_growth:+.1f}% from "
                            f"FY{prior_year.get('fiscal_year')} to FY{latest_year.get('fiscal_year')}.",
                        )]

            if change_notes:
                for label, copy in change_notes[:4]:
                    st.markdown(f"**{label}**")
                    st.write(copy)
            else:
                st.caption("Recent standardized period-over-period changes are still being prepared.")

        with snapshot_right:
            st.markdown("**Key disclosed risk themes**")
            risk_themes = selected_analysis.get("key_risk_themes", [])
            if risk_themes:
                for risk in risk_themes[:8]:
                    st.markdown(f"- {risk}")
            else:
                st.caption("Structured risk themes are being added as deep research coverage expands.")

        st.markdown("**Recent SEC activity**")
        if selected_filings:
            snapshot_filing_rows = [
                {
                    "Filed": filing.get("filing_date", ""),
                    "Form": filing.get("form", ""),
                    "Description": filing.get("description", "") or filing.get("primary_document", ""),
                    "SEC Filing": filing.get("url", ""),
                }
                for filing in selected_filings[:6]
            ]
            st.dataframe(
                pd.DataFrame(snapshot_filing_rows),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SEC Filing": st.column_config.LinkColumn("SEC Filing", display_text="Open")
                },
            )
        elif selected_sec_error:
            st.warning(selected_sec_error)
        else:
            st.caption("Recent filing metadata is not available yet.")

    if company_section == "Financials":
        section("Financials", "Income Statement & Balance Sheet")

        latest_financial_period = income_selection["record"]
        st.caption(
            f"Income statement: {income_selection['period']} · {income_selection['source']}. "
            "Unavailable fields stay unavailable rather than being filled from another period."
        )

        financial_metric_cols = st.columns(4)
        financial_metric_cols[0].metric("Revenue", format_money(latest_financial_period.get("revenue")))
        financial_metric_cols[1].metric("Gross Profit", format_money(latest_financial_period.get("gross_profit")))
        financial_metric_cols[2].metric("Operating Income", format_money(latest_financial_period.get("operating_income")))
        financial_metric_cols[3].metric("Net Income", format_money(latest_financial_period.get("net_income")))

        annual_history = income_selection["annual_history"]
        st.caption(f"Annual trend source: {income_selection['annual_source']}")
        financial_chart_cols = st.columns(2)

        with financial_chart_cols[0]:
            st.markdown("**Annual Revenue Trend**")
            annual_rows = [
                row for row in annual_history
                if row.get("fiscal_year") is not None and row.get("revenue") is not None
            ]
            if annual_rows:
                annual_df = pd.DataFrame(annual_rows)
                annual_fig = go.Figure(
                    go.Bar(
                        x=annual_df["fiscal_year"].astype(str),
                        y=annual_df["revenue"],
                        name="Revenue",
                        marker={"color": "#16C7B2"},
                    )
                )
                annual_fig.update_layout(
                    height=330,
                    margin={"l": 8, "r": 8, "t": 20, "b": 8},
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": "#8F9CA6", "family": "IBM Plex Sans"},
                    showlegend=False,
                    xaxis={"showgrid": False, "title": None},
                    yaxis={"gridcolor": "rgba(143,156,166,.12)", "title": None},
                )
                st.plotly_chart(annual_fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Annual revenue history is still being standardized.")

        with financial_chart_cols[1]:
            st.markdown("**Latest P&L Structure**")
            pnl_labels = ["Revenue", "Gross Profit", "Operating Income", "Net Income"]
            pnl_values = [
                latest_financial_period.get("revenue"),
                latest_financial_period.get("gross_profit"),
                latest_financial_period.get("operating_income"),
                latest_financial_period.get("net_income"),
            ]
            if any(value is not None for value in pnl_values):
                pnl_fig = go.Figure(
                    go.Bar(
                        x=pnl_labels,
                        y=pnl_values,
                        marker={"color": "#7DD3FC"},
                    )
                )
                pnl_fig.update_layout(
                    height=330,
                    margin={"l": 8, "r": 8, "t": 20, "b": 8},
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": "#8F9CA6", "family": "IBM Plex Sans"},
                    showlegend=False,
                    xaxis={"showgrid": False, "title": None},
                    yaxis={"gridcolor": "rgba(143,156,166,.12)", "title": None},
                )
                st.plotly_chart(pnl_fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("P&L data is still being standardized.")

        latest_q = selected_qdata.get("latest_quarter", {})
        prior_q = selected_qdata.get("prior_quarter", {})
        prior_y_q = selected_qdata.get("prior_year_quarter", {})

        if not latest_q and selected_fallback_quarters:
            latest_q = selected_fallback_quarters[-1]
            prior_q = (
                selected_fallback_quarters[-2]
                if len(selected_fallback_quarters) >= 2
                else {}
            )
            prior_y_q = (
                selected_fallback_quarters[-5]
                if len(selected_fallback_quarters) >= 5
                else {}
            )

        if latest_q and (prior_q or prior_y_q):
            st.markdown("**Quarterly Financial Comparison**")
            quarter_series = []
            for label, payload in [
                ("Prior Year Quarter", prior_y_q),
                ("Prior Quarter", prior_q),
                ("Latest Quarter", latest_q),
            ]:
                if payload:
                    quarter_series.append({
                        "Period": label,
                        "Revenue": payload.get("revenue"),
                        "Gross Profit": payload.get("gross_profit"),
                        "Operating Income": payload.get("operating_income"),
                        "Net Income": payload.get("net_income"),
                    })

            quarter_df = pd.DataFrame(quarter_series)
            quarter_fig = go.Figure()
            for metric in ["Revenue", "Gross Profit", "Operating Income", "Net Income"]:
                quarter_fig.add_trace(go.Bar(name=metric, x=quarter_df["Period"], y=quarter_df[metric]))
            quarter_fig.update_layout(
                barmode="group",
                height=380,
                margin={"l": 8, "r": 8, "t": 30, "b": 8},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"color": "#8F9CA6", "family": "IBM Plex Sans"},
                legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0},
                xaxis={"showgrid": False, "title": None},
                yaxis={"gridcolor": "rgba(143,156,166,.12)", "title": None},
            )
            st.plotly_chart(quarter_fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown("**Balance Sheet Snapshot**")
        capital_structure = selected_data.get("capital_structure", {})
        fallback_capital = selected_financial_fallback.get("capital_structure", {})

        balance_fields = ["cash_and_investments", "total_debt", "total_assets", "cash"]
        use_structured_balance = any(capital_structure.get(field) is not None for field in balance_fields)
        balance_record = capital_structure if use_structured_balance else fallback_capital
        balance_source = "Structured company balance sheet" if use_structured_balance else "Yahoo Finance balance sheet"
        cash_value = balance_record.get("cash")
        cash_investments_value = balance_record.get("cash_and_investments")
        debt_value = balance_record.get("total_debt")
        assets_value = balance_record.get("total_assets")
        st.caption(
            f"Balance sheet: {balance_record.get('balance_sheet_as_of') or 'Date unavailable'} · {balance_source}. "
            "Its reporting date may differ from the income statement."
        )

        balance_cols = st.columns(4)
        balance_cols[0].metric("Cash", format_money(cash_value))
        balance_cols[1].metric("Cash + Investments", format_money(cash_investments_value))
        balance_cols[2].metric("Total Debt", format_money(debt_value))
        balance_cols[3].metric("Total Assets", format_money(assets_value))

        financial_source = income_selection.get("source_url")
        if financial_source:
            st.link_button(
                "Open source financial filing",
                financial_source,
                key=f"workspace_financial_source_{selected_ticker}",
            )

        st.caption(
            "EquityLens uses standardized SEC-reported figures when available. "
             "Income statements and balance sheets each use a single source record; "
            "missing fields remain unavailable. Annual trends can use labeled Yahoo Finance fallback history. "
            "Market values and financial statement periods update on different schedules."
        )

    if company_section == "Filings":
        section("Filings", "SEC Filing History & Deep Filing Research")

        filing_metric_cols = st.columns(4)
        filing_metric_cols[0].metric("Annual", latest_annual.get("form", "N/A"), latest_annual.get("filing_date") or None)
        filing_metric_cols[1].metric("Quarterly", latest_quarter.get("form", "N/A"), latest_quarter.get("filing_date") or None)
        filing_metric_cols[2].metric("Current Report", latest_current.get("form", "N/A"), latest_current.get("filing_date") or None)
        filing_metric_cols[3].metric("Registration", primary_registration.get("form", "Not found"), primary_registration.get("filing_date") or None)

        if selected_sec_error:
            st.warning(selected_sec_error)

        if selected_filings:
            st.markdown("**Recent SEC filings**")
            filing_table = pd.DataFrame([
                {
                    "Filed": filing.get("filing_date", ""),
                    "Form": filing.get("form", ""),
                    "Report Period": filing.get("report_date", ""),
                    "Description": filing.get("description", "") or filing.get("primary_document", ""),
                    "SEC Filing": filing.get("url", ""),
                }
                for filing in selected_filings[:25]
            ])
            st.dataframe(
                filing_table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SEC Filing": st.column_config.LinkColumn("SEC Filing", display_text="Open filing")
                },
            )

        st.markdown("**IPO / Registration history**")
        if selected_registrations:
            registration_table = pd.DataFrame([
                {
                    "Filed": filing.get("filing_date", ""),
                    "Form": filing.get("form", ""),
                    "Description": filing.get("description", "") or filing.get("primary_document", ""),
                    "SEC Filing": filing.get("url", ""),
                }
                for filing in selected_registrations
            ])
            st.dataframe(
                registration_table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SEC Filing": st.column_config.LinkColumn("SEC Filing", display_text="Open filing")
                },
            )
        else:
            st.caption("No S-1, F-1, S-11 or related amendment was found in the available SEC submission history.")

        if selected_s1:
            st.markdown("**Structured registration-file research**")
            st.write(selected_s1.get("historical_context", "Historical registration context is available."))
            st.markdown("**What to learn from the filing**")
            st.write(
                selected_s1.get(
                    "what_to_learn",
                    "Review the original filing for business, risk, ownership and financial context.",
                )
            )

            detail_map = selected_s1.get("filing_details", {})
            detail_sections = [
                ("Business & Revenue Model", "business_revenue_model"),
                ("Customers & Go-to-Market", "customers_go_to_market"),
                ("Growth & Market Opportunity", "growth_market_opportunity"),
                ("Competition & Differentiation", "competition_differentiation"),
                ("Risk Factors", "risk_factors"),
                ("Financial History", "financial_history"),
                ("Capitalization & Dilution", "ipo_capitalization_dilution"),
                ("Proceeds, Management & Ownership", "proceeds_management_ownership"),
            ]
            detail_cols = st.columns(2)
            for idx, (label, field) in enumerate(detail_sections):
                with detail_cols[idx % 2]:
                    with st.expander(label, expanded=(idx < 2)):
                        points = detail_map.get(field, [])
                        if points:
                            for point in points:
                                st.markdown(f"- {point}")
                        else:
                            st.caption("Structured detail is not available yet.")

            if selected_s1.get("source_url"):
                st.link_button(
                    "Open EquityLens registration source",
                    selected_s1.get("source_url"),
                    key=f"workspace_s1_source_{selected_ticker}",
                )

        if selected_sec.get("sec_company_url"):
            st.link_button(
                "Open complete SEC company history",
                selected_sec.get("sec_company_url"),
                key=f"workspace_sec_history_{selected_ticker}",
            )

    if company_section == "Ownership":
        section("Ownership", "Ownership & Major Holders")
        st.caption(
            "Ownership combines SEC beneficial-ownership filings with supplemental institutional and fund-holder data. "
            "Percentages and holder tables can update on a different schedule from company filings."
        )

        try:
            ownership_data = get_company_ownership_data(selected_ticker)
        except Exception:
            ownership_data = {
                "major": pd.DataFrame(),
                "institutional": pd.DataFrame(),
                "mutual_fund": pd.DataFrame(),
            }

        major_table = ownership_data.get("major", pd.DataFrame())
        major_lookup = {}
        if isinstance(major_table, pd.DataFrame) and not major_table.empty:
            major_copy = major_table.copy()
            key_column = next(
                (
                    column
                    for column in ["index", "Breakdown", "Metric"]
                    if column in major_copy.columns
                ),
                major_copy.columns[0],
            )
            value_column = next(
                (
                    column
                    for column in ["Value", "value"]
                    if column in major_copy.columns
                ),
                major_copy.columns[-1],
            )
            for _, row in major_copy.iterrows():
                major_lookup[str(row.get(key_column, ""))] = row.get(value_column)

        def _ownership_pct(value):
            number = safe_float(value)
            if number is None:
                return "N/A"
            if abs(number) <= 1:
                number *= 100
            return f"{number:.1f}%"

        def _ownership_count(value):
            number = safe_float(value)
            return f"{int(number):,}" if number is not None else "N/A"

        ownership_summary_cols = st.columns(4)
        ownership_summary_cols[0].metric(
            "Insider ownership",
            _ownership_pct(
                major_lookup.get(
                    "insidersPercentHeld",
                    major_lookup.get("% of Shares Held by All Insider", None),
                )
            ),
        )
        ownership_summary_cols[1].metric(
            "Institutional ownership",
            _ownership_pct(
                major_lookup.get(
                    "institutionsPercentHeld",
                    major_lookup.get("% of Shares Held by Institutions", None),
                )
            ),
        )
        ownership_summary_cols[2].metric(
            "Institutional float",
            _ownership_pct(
                major_lookup.get(
                    "institutionsFloatPercentHeld",
                    major_lookup.get("% of Float Held by Institutions", None),
                )
            ),
        )
        ownership_summary_cols[3].metric(
            "Institutional holders",
            _ownership_count(
                major_lookup.get(
                    "institutionsCount",
                    major_lookup.get("Number of Institutions Holding Shares", None),
                )
            ),
        )

        st.markdown("**SEC beneficial-ownership filings**")
        ownership_forms = {
            "DEF 14A",
            "DEFA14A",
            "SC 13D",
            "SC 13D/A",
            "SC 13G",
            "SC 13G/A",
        }
        sec_ownership_rows = [
            {
                "Filed": filing.get("filing_date", ""),
                "Form": filing.get("form", ""),
                "Description": (
                    filing.get("description", "")
                    or filing.get("primary_document", "")
                ),
                "SEC Filing": filing.get("url", ""),
            }
            for filing in selected_filings
            if filing.get("form") in ownership_forms
        ][:20]

        if sec_ownership_rows:
            st.dataframe(
                pd.DataFrame(sec_ownership_rows),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SEC Filing": st.column_config.LinkColumn(
                        "SEC Filing",
                        display_text="Open",
                    )
                },
            )
        else:
            st.caption(
                "No proxy or Schedule 13D/13G filing appeared in the currently loaded SEC history."
            )

        def _clean_holder_table(table):
            if not isinstance(table, pd.DataFrame) or table.empty:
                return pd.DataFrame()

            cleaned = table.copy()
            cleaned = cleaned.drop(
                columns=[column for column in ["index"] if column in cleaned.columns],
                errors="ignore",
            )
            cleaned = cleaned.rename(
                columns={
                    "Date Reported": "Reported",
                    "pctHeld": "% Held",
                    "pctChange": "% Change",
                    "Value": "Position Value",
                }
            )

            if "Reported" in cleaned.columns:
                cleaned["Reported"] = pd.to_datetime(
                    cleaned["Reported"],
                    errors="coerce",
                ).dt.date.astype(str)

            if "% Held" in cleaned.columns:
                cleaned["% Held"] = cleaned["% Held"].apply(
                    lambda value: _ownership_pct(value)
                )

            if "% Change" in cleaned.columns:
                cleaned["% Change"] = cleaned["% Change"].apply(
                    lambda value: _ownership_pct(value)
                )

            if "Shares" in cleaned.columns:
                cleaned["Shares"] = cleaned["Shares"].apply(
                    lambda value: (
                        f"{int(safe_float(value)):,}"
                        if safe_float(value) is not None
                        else "N/A"
                    )
                )

            if "Position Value" in cleaned.columns:
                cleaned["Position Value"] = cleaned["Position Value"].apply(
                    lambda value: format_money(safe_float(value))
                )

            preferred = [
                column
                for column in [
                    "Holder",
                    "Reported",
                    "% Held",
                    "Shares",
                    "Position Value",
                    "% Change",
                ]
                if column in cleaned.columns
            ]
            remaining = [
                column for column in cleaned.columns
                if column not in preferred
            ]
            return cleaned[preferred + remaining]

        st.markdown("**Largest institutional holders**")
        institutional_table = _clean_holder_table(
            ownership_data.get("institutional", pd.DataFrame())
        )
        if not institutional_table.empty:
            st.dataframe(
                institutional_table.head(15),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption(
                "Institutional-holder detail is unavailable from the supplemental feed."
            )

        st.markdown("**Largest mutual-fund holders**")
        mutual_table = _clean_holder_table(
            ownership_data.get("mutual_fund", pd.DataFrame())
        )
        if not mutual_table.empty:
            st.dataframe(
                mutual_table.head(15),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption(
                "Mutual-fund holder detail is unavailable from the supplemental feed."
            )

        st.caption(
            "SEC filings are the primary ownership source. Institutional and fund-holder tables are supplemental Yahoo Finance data via yfinance."
        )

    if company_section == "Analyst Research":
        section("Analyst Research", "Consensus, Price Targets & Rating Changes")
        st.caption(
            "These are third-party analyst opinions and market-data aggregates. "
            "They are not EquityLens ratings, recommendations, or price forecasts."
        )

        try:
            analyst_data = get_company_analyst_data(selected_ticker)
        except Exception:
            analyst_data = {
                "targets": {},
                "recommendations": pd.DataFrame(),
                "upgrades": pd.DataFrame(),
            }

        targets = analyst_data.get("targets", {}) or {}

        def target_value(*keys):
            for key in keys:
                if key in targets and targets.get(key) is not None:
                    return safe_float(targets.get(key))
            return None

        current_target_price = target_value("current", "currentPrice", "Current")
        mean_target = target_value("mean", "meanPriceTarget", "targetMeanPrice")
        median_target = target_value("median", "medianPriceTarget", "targetMedianPrice")
        low_target = target_value("low", "lowPriceTarget", "targetLowPrice")
        high_target = target_value("high", "highPriceTarget", "targetHighPrice")

        analyst_metric_cols = st.columns(5)
        analyst_metric_cols[0].metric(
            "Current Price",
            ("$" + f"{(current_target_price or selected_price):,.2f}")
            if (current_target_price or selected_price) is not None
            else "N/A",
        )
        analyst_metric_cols[1].metric(
            "Mean Target",
            ("$" + f"{mean_target:,.2f}") if mean_target is not None else "N/A",
        )
        analyst_metric_cols[2].metric(
            "Median Target",
            ("$" + f"{median_target:,.2f}") if median_target is not None else "N/A",
        )
        analyst_metric_cols[3].metric(
            "Low Target",
            ("$" + f"{low_target:,.2f}") if low_target is not None else "N/A",
        )
        analyst_metric_cols[4].metric(
            "High Target",
            ("$" + f"{high_target:,.2f}") if high_target is not None else "N/A",
        )

        recommendations_table = analyst_data.get("recommendations", pd.DataFrame())
        st.markdown("**Recommendation summary**")
        if isinstance(recommendations_table, pd.DataFrame) and not recommendations_table.empty:
            st.dataframe(recommendations_table, use_container_width=True, hide_index=True)
        else:
            st.caption("Consensus recommendation data is unavailable from the supplemental feed.")

        upgrades_table = analyst_data.get("upgrades", pd.DataFrame())
        st.markdown("**Recent upgrades / downgrades**")
        if isinstance(upgrades_table, pd.DataFrame) and not upgrades_table.empty:
            st.dataframe(
                upgrades_table.tail(25).iloc[::-1],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("Recent analyst rating-change data is unavailable from the supplemental feed.")

        st.caption(
            "Supplemental analyst data: Yahoo Finance via yfinance. "
            "EquityLens does not convert third-party opinions into its own buy, sell, or hold rating."
        )

    if company_section == "Peers & ETFs":
        section("Peers", "Related Companies & Major ETF Exposure")

        peer_rows = workspace_universe[
            (workspace_universe["Industry"] == selected_industry_name)
            & (workspace_universe["Ticker"].astype(str).str.upper() != selected_ticker)
        ].copy()

        if "Market Cap" in peer_rows.columns:
            peer_rows["_market_cap_sort"] = peer_rows["Market Cap"].apply(finviz_numeric)
            peer_rows = peer_rows.sort_values("_market_cap_sort", ascending=False)

        peer_columns = [
            column
            for column in [
                "Ticker", "Company", "Sector", "Industry",
                "Market Cap", "P/E", "Price", "Change",
            ]
            if column in peer_rows.columns
        ]

        st.markdown("**Industry peers**")
        if not peer_rows.empty:
            st.dataframe(
                peer_rows[peer_columns].head(20),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No additional companies share this exact industry label in the current universe.")

        st.markdown("**Major ETF exposure**")
        st.caption(
            "This scanner checks the published top-holdings lists for a curated set of major broad-market, growth, sector, semiconductor, communication-services, and software ETFs. "
            "It is useful context, not an exhaustive ETF-ownership database."
        )

        etf_state_key = f"workspace_etf_scan_{selected_ticker}"
        if st.button("Scan major ETFs", key=f"workspace_etf_button_{selected_ticker}"):
            st.session_state[etf_state_key] = True

        if st.session_state.get(etf_state_key, False):
            try:
                etf_matches = get_major_etf_exposure(selected_ticker)
            except Exception:
                etf_matches = []

            if etf_matches:
                etf_df = pd.DataFrame(etf_matches)
                if "Holding" in etf_df.columns:
                    etf_df["Holding"] = etf_df["Holding"].apply(
                        lambda value: (
                            f"{safe_float(value) * 100:.2f}%"
                            if safe_float(value) is not None and abs(safe_float(value)) <= 1
                            else (
                                f"{safe_float(value):.2f}%"
                                if safe_float(value) is not None
                                else "N/A"
                            )
                        )
                    )
                st.dataframe(etf_df, use_container_width=True, hide_index=True)
            else:
                st.info(
                    "No match was found in the published top-holdings sample for the ETFs scanned. "
                    "This does not mean no ETF owns the stock; free fund feeds do not expose every holding for every ETF."
                )

        st.caption(
            "Peer groups use the EquityLens industry classification. "
            "ETF holdings are supplemental market data and may be delayed."
        )


if active_destination == "Market Monitor":
    render_market_monitor(
        public_finviz_data_enabled=public_finviz_data_enabled,
        industries=industries,
        company_data=company_data,
        sec_summary=sec_summary,
        workspace_known_tickers=workspace_known_tickers,
        research_link=research_link,
    )


if active_destination == "Filings":
    render_filings(
        company_universe=company_universe,
        load_sec_filings=load_sec_filings,
        get_sec_company_research=get_sec_company_research,
    )


if active_destination == "Learn":
    render_learn()


save_rendered_choices()

st.markdown(
    """
    <div class="el-evidence-strip">
        <div>
            <div class="el-evidence-title">Evidence first. Judgment stays with you.</div>
            <div class="el-evidence-copy">Source it. Show the math. Show the date. Show the uncertainty.</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")
section("Methodology", "Data Sources")
st.markdown(
    """
    **Source priority**

    1. SEC EDGAR filings, including Forms 10-K, 10-Q, 8-K, and S-1
    2. U.S. Bureau of Labor Statistics for CPI, PPI, employment, earnings, ECI, and release schedules
    3. U.S. Department of the Treasury for the official daily Treasury par yield curve
    4. Federal Reserve and Federal Reserve Bank of New York for FOMC information, SOFR, and reference rates
    5. Company investor-relations materials and company-reported disclosures
    6. Licensed or permitted market-data/news providers where the relevant redistribution rights allow use

    EquityLens distinguishes reported figures from metrics calculated inside the app. Bloomberg headline metadata is displayed only as an outbound news gateway when retrievable; article text is not republished. Material figures should include a reporting period and a link to the original source whenever available.
    """
)

section("Disclosure", "Important Disclosures")
st.caption(
    """
    EquityLens AI is an educational and research tool that analyzes publicly
    available financial information. It does not provide personalized investment
    advice, investment recommendations, rankings, or guarantees of future performance.

    EquityLens AI is an independent personal research project and is not affiliated
    with, sponsored by, or endorsed by any similarly named company, product, service,
    financial institution, broker, exchange, or data provider.

    Financial information may be delayed, incomplete, or affected by later filings
    and restatements. Users should verify material information against the original
    SEC filings and company disclosures before making financial decisions.
    """
)

st.markdown("---")
st.markdown(
    """
    **© 2026 Keya Dhanani. All rights reserved.**

    EquityLens AI was independently designed and developed by Keya Dhanani. Original
    application code, user-interface design, written explanations, project-specific
    research structure, and documentation are proprietary unless otherwise stated.

    Public SEC filings, company disclosures, trademarks, company names, and third-party
    source materials remain the property of their respective owners. EquityLens cites
    or links to original sources where applicable and does not claim ownership of those
    underlying materials.

    Unauthorized reproduction, redistribution, republishing, or creation of a
    substantially similar copy of the original EquityLens AI application or its
    original written content is not permitted except where allowed by applicable law
    or platform terms.
    """
)

