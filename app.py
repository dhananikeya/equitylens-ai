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
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st
from bs4 import BeautifulSoup
from supabase import create_client

st.set_page_config(
    page_title="EquityLens AI",
    page_icon="📊",
    layout="wide"
)

st.markdown(
    """
    <style>
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


def get_supabase_client():
    url = st.secrets.get("SUPABASE_URL")
    anon_key = st.secrets.get("SUPABASE_ANON_KEY")
    if not url or not anon_key:
        return None
    return create_client(url, anon_key)


def get_public_app_url():
    """Return the public URL users should land on after confirming their email."""
    configured_url = st.secrets.get(
        "PUBLIC_APP_URL",
        "https://equitylens-ai-2h7rd8qluv3bc8sdqf5cu3.streamlit.app/"
    )
    return str(configured_url).rstrip("/") + "/"



@st.cache_data(ttl=60)
def load_json(path):
    with open(path, "r") as file:
        return json.load(file)


SEC_REQUEST_HEADERS = {
    "User-Agent": "EquityLens AI research app dhananikeya@gmail.com",
    "From": "dhananikeya@gmail.com",
    "Accept": "application/json",
}


@st.cache_data(ttl=86400)
def get_sec_ticker_directory():
    response = requests.get(
        "https://www.sec.gov/files/company_tickers.json",
        headers=SEC_REQUEST_HEADERS,
        timeout=30
    )
    response.raise_for_status()
    payload = response.json()

    directory = {}
    for row in payload.values():
        ticker = str(row.get("ticker", "")).upper().strip()
        if ticker:
            directory[ticker] = {
                "cik": str(row.get("cik_str", "")).zfill(10),
                "title": row.get("title", "")
            }
    return directory


def sec_filing_url(cik, accession, primary_document):
    if not cik or not accession or not primary_document:
        return ""
    return (
        "https://www.sec.gov/Archives/edgar/data/"
        + str(int(cik))
        + "/"
        + str(accession).replace("-", "")
        + "/"
        + str(primary_document)
    )


def sec_rows_from_recent(recent, cik):
    forms = recent.get("form", []) if isinstance(recent, dict) else []
    rows = []

    def value(field, index, default=""):
        values = recent.get(field, []) if isinstance(recent, dict) else []
        return values[index] if index < len(values) else default

    for index, form in enumerate(forms):
        accession = value("accessionNumber", index)
        primary_document = value("primaryDocument", index)
        rows.append({
            "form": form,
            "filing_date": value("filingDate", index),
            "report_date": value("reportDate", index),
            "accession_number": accession,
            "primary_document": primary_document,
            "description": value("primaryDocDescription", index),
            "items": value("items", index),
            "url": sec_filing_url(cik, accession, primary_document)
        })

    return rows


@st.cache_data(ttl=900)
def get_sec_company_research(ticker):
    ticker = str(ticker).upper().strip()
    directory = get_sec_ticker_directory()
    ticker_record = directory.get(ticker)

    if not ticker_record:
        return {
            "ticker": ticker,
            "cik": "",
            "entity_name": "",
            "filings": [],
            "registration_filings": [],
            "sec_company_url": "",
            "status": "Ticker not resolved in SEC directory"
        }

    cik = ticker_record["cik"]
    response = requests.get(
        f"https://data.sec.gov/submissions/CIK{cik}.json",
        headers=SEC_REQUEST_HEADERS,
        timeout=30
    )
    response.raise_for_status()
    submissions = response.json()

    recent = submissions.get("filings", {}).get("recent", {})
    recent_rows = sec_rows_from_recent(recent, cik)

    registration_forms = {
        "S-1", "S-1/A",
        "F-1", "F-1/A",
        "S-11", "S-11/A"
    }
    registration_rows = [
        row for row in recent_rows
        if row.get("form") in registration_forms
    ]

    if not registration_rows:
        history_files = submissions.get("filings", {}).get("files", []) or []
        for history_file in history_files:
            history_name = history_file.get("name")
            if not history_name:
                continue
            history_response = requests.get(
                "https://data.sec.gov/submissions/" + history_name,
                headers=SEC_REQUEST_HEADERS,
                timeout=30
            )
            history_response.raise_for_status()
            historical_rows = sec_rows_from_recent(
                history_response.json(),
                cik
            )
            registration_rows.extend(
                row for row in historical_rows
                if row.get("form") in registration_forms
            )
            if registration_rows:
                break

    seen_accessions = set()
    registration_unique = []
    for row in registration_rows:
        accession = row.get("accession_number")
        if accession and accession in seen_accessions:
            continue
        if accession:
            seen_accessions.add(accession)
        registration_unique.append(row)

    return {
        "ticker": ticker,
        "cik": cik,
        "entity_name": submissions.get(
            "name",
            ticker_record.get("title", "")
        ),
        "filings": recent_rows[:40],
        "registration_filings": registration_unique,
        "sec_company_url": (
            "https://www.sec.gov/edgar/browse/"
            + f"?CIK={int(cik)}&owner=exclude&action=getcompany"
        ),
        "status": "available"
    }


def latest_filing_by_forms(filings, forms):
    wanted_forms = set(forms)
    for filing in filings:
        if filing.get("form") in wanted_forms:
            return filing
    return {}


@st.cache_data(ttl=300)
def get_live_market_data(symbols):
    """Fetch current-ish quote data from Yahoo Finance via yfinance."""
    symbols = [str(symbol).strip().upper() for symbol in symbols if symbol]
    if not symbols:
        return {}

    quotes = {}
    for symbol in symbols:
        try:
            history = yf.Ticker(symbol).history(
                period="5d",
                interval="1d",
                auto_adjust=False
            )
        except Exception:
            continue

        if history is None or history.empty:
            continue

        history = history.dropna(subset=["Close"])
        if history.empty:
            continue

        latest = history.iloc[-1]
        previous_close = (
            float(history.iloc[-2]["Close"])
            if len(history) >= 2 and pd.notna(history.iloc[-2]["Close"])
            else None
        )
        close = float(latest["Close"]) if pd.notna(latest.get("Close")) else None
        open_price = float(latest["Open"]) if pd.notna(latest.get("Open")) else None
        volume = float(latest["Volume"]) if pd.notna(latest.get("Volume")) else None

        percent_change = None
        if close is not None and previous_close not in (None, 0):
            percent_change = ((close - previous_close) / previous_close) * 100

        quotes[symbol] = {
            "symbol": symbol,
            "close": close,
            "open": open_price,
            "previous_close": previous_close,
            "percent_change": percent_change,
            "volume": volume
        }

    return quotes


@st.cache_data(ttl=120)
def get_finviz_screener_data(symbols=None, filters=None):
    export_url = st.secrets.get("FINVIZ_EXPORT_URL")
    api_key = st.secrets.get("FINVIZ_API_KEY")
    configured_api_url = str(
        st.secrets.get("FINVIZ_API_URL", "")
    ).strip()
    api_url = (
        configured_api_url
        if configured_api_url.startswith(("https://", "http://"))
        else "https://elite.finviz.com/export.ashx"
    )

    headers = {"User-Agent": "EquityLens/1.0"}

    if api_key:
        params = {
            "v": "152",
            "auth": str(api_key),
            "ft": "4"
        }

        if symbols:
            params["t"] = ",".join(symbols)

        if filters:
            params["f"] = str(filters)

        response = requests.get(
            str(api_url),
            params=params,
            headers=headers,
            timeout=30
        )
    elif export_url:
        response = requests.get(
            str(export_url),
            headers=headers,
            timeout=30
        )
    else:
        raise ValueError(
            "Configure FINVIZ_API_KEY or FINVIZ_EXPORT_URL in Streamlit Secrets."
        )

    response.raise_for_status()

    payload = response.text.strip()
    if not payload:
        raise ValueError("Finviz returned an empty response.")

    payload_start = payload[:200].lower()
    if "<html" in payload_start or "<!doctype" in payload_start:
        raise ValueError(
            "Finviz did not return CSV data. Check the Elite API token/export configuration."
        )

    data = pd.read_csv(io.StringIO(payload))
    if data.empty:
        raise ValueError("Finviz returned no screener rows.")

    return data


def find_finviz_column(dataframe, candidates):
    lookup = {
        str(column).strip().lower(): column
        for column in dataframe.columns
    }
    for candidate in candidates:
        match = lookup.get(candidate.strip().lower())
        if match is not None:
            return match
    return None


def normalize_finviz_screener(dataframe):
    if dataframe is None or dataframe.empty:
        return pd.DataFrame()

    field_map = {
        "Ticker": ["Ticker", "Symbol"],
        "Company": ["Company", "Company Name"],
        "Sector": ["Sector"],
        "Industry": ["Industry"],
        "Market Cap": ["Market Cap", "Market Cap."],
        "P/E": ["P/E", "PE"],
        "Price": ["Price"],
        "Change": ["Change", "Change %"],
        "Volume": ["Volume", "Current Volume"],
        "Relative Volume": ["Relative Volume", "Rel Volume", "Rel Volume 20D"],
        "Perf Week": ["Perf Week", "Performance Week", "Performance 1 Week"],
        "Perf Month": ["Perf Month", "Performance Month", "Performance 1 Month"],
        "Earnings": ["Earnings", "Earnings Date"]
    }

    normalized = pd.DataFrame(index=dataframe.index)

    for target, candidates in field_map.items():
        source = find_finviz_column(dataframe, candidates)
        if source is not None:
            normalized[target] = dataframe[source]

    if "Ticker" not in normalized.columns:
        raise ValueError(
            "The Finviz export does not include a Ticker/Symbol column."
        )

    normalized["Ticker"] = normalized["Ticker"].astype(str).str.upper().str.strip()
    return normalized


def finviz_numeric(value):
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
        return float(text) * multiplier
    except ValueError:
        return None


@st.cache_data(ttl=900)
def get_market_history(symbol, interval="1day", outputsize=60):
    """Fetch chart history from Yahoo Finance via yfinance."""
    interval_map = {
        "15min": "15m",
        "1h": "1h",
        "1day": "1d"
    }
    yf_interval = interval_map.get(interval, "1d")

    if yf_interval == "15m":
        period = "5d"
    elif yf_interval == "1h":
        period = "1mo"
    elif outputsize <= 35:
        period = "3mo"
    elif outputsize <= 140:
        period = "1y"
    else:
        period = "2y"

    history = yf.Ticker(symbol).history(
        period=period,
        interval=yf_interval,
        auto_adjust=False
    )

    if history is None or history.empty:
        return pd.DataFrame()

    history = history.reset_index()
    datetime_column = "Datetime" if "Datetime" in history.columns else "Date"
    history = history.rename(columns={
        datetime_column: "datetime",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    })

    wanted = [
        column for column in
        ["datetime", "open", "high", "low", "close", "volume"]
        if column in history.columns
    ]
    history = history[wanted].copy()

    if "datetime" in history.columns:
        history["datetime"] = pd.to_datetime(history["datetime"], errors="coerce")

    for column in ["open", "high", "low", "close", "volume"]:
        if column in history.columns:
            history[column] = pd.to_numeric(history[column], errors="coerce")

    history = history.dropna(subset=["datetime", "close"]).sort_values("datetime")
    if outputsize and len(history) > outputsize:
        history = history.tail(outputsize)

    return history


def market_provider_error(provider, exc):
    """Return a safe, user-facing provider error without exposing credentials."""
    status_code = getattr(getattr(exc, "response", None), "status_code", None)

    if status_code == 429:
        return (
            f"{provider} rate limit reached. EquityLens will keep the last cached data "
            "and try again after the provider quota resets."
        )

    return (
        f"{provider} is temporarily unavailable. Check the provider configuration "
        "or try again shortly."
    )



PUBLIC_DATA_HEADERS = {
    "User-Agent": "EquityLensAI/1.0 (+https://github.com/dhananikeya/equitylens-ai)"
}


def _numeric_text(value):
    if value is None:
        return None
    text = str(value).strip().replace(",", "").replace("%", "")
    text = text.replace("−", "-").replace("–", "-")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


@st.cache_data(ttl=1800)
def get_treasury_yield_curve():
    """Load the latest official U.S. Treasury par yield curve observation."""
    year = datetime.now(timezone.utc).year
    source_url = (
        "https://home.treasury.gov/resource-center/data-chart-center/"
        "interest-rates/pages/xml"
        f"?data=daily_treasury_yield_curve&field_tdr_date_value={year}"
    )
    response = requests.get(
        source_url,
        headers=PUBLIC_DATA_HEADERS,
        timeout=25
    )
    response.raise_for_status()

    root = ET.fromstring(response.content)
    records = []
    for element in root.iter():
        if element.tag.split("}")[-1].lower() != "properties":
            continue
        record = {}
        for child in list(element):
            key = child.tag.split("}")[-1]
            record[key] = (child.text or "").strip()
        if record:
            records.append(record)

    if not records:
        raise ValueError("Treasury returned no yield-curve observations.")

    def record_date(record):
        raw = record.get("NEW_DATE") or record.get("Date") or ""
        parsed = pd.to_datetime(raw, errors="coerce")
        return parsed if pd.notna(parsed) else pd.Timestamp.min

    latest = max(records, key=record_date)
    latest_date = record_date(latest)

    field_map = {
        "1M": "BC_1MONTH",
        "3M": "BC_3MONTH",
        "6M": "BC_6MONTH",
        "1Y": "BC_1YEAR",
        "2Y": "BC_2YEAR",
        "3Y": "BC_3YEAR",
        "5Y": "BC_5YEAR",
        "7Y": "BC_7YEAR",
        "10Y": "BC_10YEAR",
        "20Y": "BC_20YEAR",
        "30Y": "BC_30YEAR",
    }
    rates = {
        tenor: _numeric_text(latest.get(field))
        for tenor, field in field_map.items()
    }

    return {
        "date": (
            latest_date.strftime("%Y-%m-%d")
            if latest_date != pd.Timestamp.min else ""
        ),
        "rates": rates,
        "source_url": source_url,
    }


def _find_html_data_row(url, required_header_terms):
    response = requests.get(
        url,
        headers={
            **PUBLIC_DATA_HEADERS,
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 Safari/537.36 EquityLensAI/1.0"
            ),
        },
        timeout=25,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    for table in soup.find_all("table"):
        header_text = " ".join(
            cell.get_text(" ", strip=True)
            for cell in table.find_all("th")
        ).upper()
        if not all(term.upper() in header_text for term in required_header_terms):
            continue

        for row in table.find_all("tr"):
            cells = [
                cell.get_text(" ", strip=True)
                for cell in row.find_all("td")
            ]
            if cells:
                return cells
    return []


def _walk_dicts(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_dicts(child)


def _normalized_dict(record):
    return {
        re.sub(r"[^a-z0-9]", "", str(key).lower()): value
        for key, value in record.items()
    }


@st.cache_data(ttl=900)
def get_sofr_reference_rates():
    """Load SOFR and published SOFR averages from the New York Fed."""
    sofr_url = "https://www.newyorkfed.org/markets/reference-rates/sofr"
    averages_url = (
        "https://www.newyorkfed.org/markets/reference-rates/"
        "sofr-averages-and-index"
    )

    result = {
        "date": "",
        "SOFR": None,
        "30D": None,
        "90D": None,
        "180D": None,
        "source_url": averages_url,
    }

    # Prefer the New York Fed's Markets Data API when available.
    try:
        response = requests.get(
            "https://markets.newyorkfed.org/api/rates/secured/sofr/last/1.json",
            headers=PUBLIC_DATA_HEADERS,
            timeout=20,
        )
        if response.ok:
            for record in _walk_dicts(response.json()):
                normalized = _normalized_dict(record)
                rate = (
                    normalized.get("percentrate")
                    or normalized.get("rate")
                    or normalized.get("percent")
                )
                rate_type = str(
                    normalized.get("type")
                    or normalized.get("ratetype")
                    or ""
                ).upper()
                if rate is not None and ("SOFR" in rate_type or not rate_type):
                    result["SOFR"] = _numeric_text(rate)
                    result["date"] = str(
                        normalized.get("effectivedate")
                        or normalized.get("date")
                        or result["date"]
                    )
                    break
    except Exception:
        pass

    try:
        response = requests.get(
            "https://markets.newyorkfed.org/api/rates/secured/"
            "sofr-avg-ind/last/1.json",
            headers=PUBLIC_DATA_HEADERS,
            timeout=20,
        )
        if response.ok:
            for record in _walk_dicts(response.json()):
                normalized = _normalized_dict(record)
                aliases = {
                    "30D": [
                        "average30day", "avg30day", "sofr30dayavg",
                        "thirtydayaverage", "30dayaverage"
                    ],
                    "90D": [
                        "average90day", "avg90day", "sofr90dayavg",
                        "ninetydayaverage", "90dayaverage"
                    ],
                    "180D": [
                        "average180day", "avg180day", "sofr180dayavg",
                        "onehundredeightydayaverage", "180dayaverage"
                    ],
                }
                found_any = False
                for label, keys in aliases.items():
                    for key in keys:
                        if key in normalized:
                            result[label] = _numeric_text(normalized[key])
                            found_any = True
                            break
                if found_any:
                    result["date"] = str(
                        normalized.get("effectivedate")
                        or normalized.get("date")
                        or result["date"]
                    )
                    break
    except Exception:
        pass

    # Fallback to the official public HTML tables.
    if result["SOFR"] is None:
        try:
            cells = _find_html_data_row(
                sofr_url,
                ["DATE", "RATE", "VOLUME"]
            )
            if len(cells) >= 2:
                result["date"] = cells[0]
                result["SOFR"] = _numeric_text(cells[1])
        except Exception:
            pass

    if any(result[key] is None for key in ["30D", "90D", "180D"]):
        try:
            cells = _find_html_data_row(
                averages_url,
                ["DATE", "30-DAY", "90-DAY", "180-DAY"]
            )
            if len(cells) >= 4:
                if not result["date"]:
                    result["date"] = cells[0]
                result["30D"] = (
                    result["30D"]
                    if result["30D"] is not None
                    else _numeric_text(cells[1])
                )
                result["90D"] = (
                    result["90D"]
                    if result["90D"] is not None
                    else _numeric_text(cells[2])
                )
                result["180D"] = (
                    result["180D"]
                    if result["180D"] is not None
                    else _numeric_text(cells[3])
                )
        except Exception:
            pass

    return result


def render_rates_ticker(treasury_curve, sofr_rates):
    """Render official Treasury and New York Fed reference rates as a tape."""
    treasury_rates = treasury_curve.get("rates", {}) if treasury_curve else {}
    tape_data = [
        ("U.S. Treasury", "2Y", treasury_rates.get("2Y"), "%"),
        ("U.S. Treasury", "5Y", treasury_rates.get("5Y"), "%"),
        ("U.S. Treasury", "10Y", treasury_rates.get("10Y"), "%"),
        ("U.S. Treasury", "30Y", treasury_rates.get("30Y"), "%"),
    ]

    two_year = treasury_rates.get("2Y")
    ten_year = treasury_rates.get("10Y")
    spread = None
    if two_year is not None and ten_year is not None:
        spread = (ten_year - two_year) * 100
    tape_data.append(("Yield Curve", "2s10s", spread, " bp"))

    if sofr_rates:
        tape_data.extend([
            ("New York Fed", "SOFR", sofr_rates.get("SOFR"), "%"),
            ("New York Fed", "30D SOFR", sofr_rates.get("30D"), "%"),
            ("New York Fed", "90D SOFR", sofr_rates.get("90D"), "%"),
            ("New York Fed", "180D SOFR", sofr_rates.get("180D"), "%"),
        ])

    items = []
    for provider, label, value, suffix in tape_data:
        if value is None:
            value_text = "N/A"
        elif suffix == " bp":
            value_text = f"{value:+.1f} bp"
        else:
            value_text = f"{value:.3f}%"

        items.append(
            '<div class="el-ticker-item">'
            f'<span class="el-ticker-company">{html.escape(provider)}</span>'
            f'<span class="el-ticker-symbol">{html.escape(label)}</span>'
            f'<span class="el-ticker-price">{html.escape(value_text)}</span>'
            '<span class="el-ticker-change flat">Official</span>'
            '</div>'
        )

    if not items:
        st.caption("Official rates are temporarily unavailable.")
        return

    st.markdown(
        f"""
        <div class="el-exchange-tape">
            <div class="el-exchange-pill">
                <span>RATES</span>
                <span class="el-exchange-chevron">⌄</span>
            </div>
            <div class="el-ticker-shell">
                <div class="el-ticker-track">{"".join(items + items)}</div>
            </div>
        </div>
        <div class="el-market-delay">
            U.S. Treasury + Federal Reserve Bank of New York · official public data
        </div>
        """,
        unsafe_allow_html=True,
    )


BLS_SERIES_META = {
    "CPI": {
        "series_id": "CUUR0000SA0",
        "label": "CPI YoY",
        "mode": "yoy",
        "lag": 12,
        "source": "Consumer Price Index",
    },
    "Core CPI": {
        "series_id": "CUUR0000SA0L1E",
        "label": "Core CPI YoY",
        "mode": "yoy",
        "lag": 12,
        "source": "Consumer Price Index",
    },
    "PPI": {
        "series_id": "WPUFD4",
        "label": "PPI Final Demand YoY",
        "mode": "yoy",
        "lag": 12,
        "source": "Producer Price Index",
    },
    "Unemployment": {
        "series_id": "LNS14000000",
        "label": "Unemployment Rate",
        "mode": "percent",
        "lag": 1,
        "source": "Employment Situation",
    },
    "Payrolls": {
        "series_id": "CES0000000001",
        "label": "Nonfarm Payrolls MoM",
        "mode": "delta",
        "lag": 1,
        "source": "Employment Situation",
    },
    "Hourly Earnings": {
        "series_id": "CES0500000003",
        "label": "Avg. Hourly Earnings YoY",
        "mode": "yoy",
        "lag": 12,
        "source": "Employment Situation",
    },
    "ECI": {
        "series_id": "CIU1010000000000A",
        "label": "Employment Cost Index YoY",
        "mode": "yoy",
        "lag": 4,
        "source": "Employment Cost Index",
    },
}


@st.cache_data(ttl=3600)
def get_bls_macro_snapshot():
    """Retrieve selected material U.S. labor/inflation series from BLS."""
    now = datetime.now(timezone.utc)
    payload = {
        "seriesid": [
            metadata["series_id"]
            for metadata in BLS_SERIES_META.values()
        ],
        "startyear": str(now.year - 2),
        "endyear": str(now.year),
    }
    response = requests.post(
        "https://api.bls.gov/publicAPI/v2/timeseries/data/",
        json=payload,
        headers=PUBLIC_DATA_HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    if data.get("status") != "REQUEST_SUCCEEDED":
        raise ValueError("BLS API request did not succeed.")

    meta_by_id = {
        metadata["series_id"]: (name, metadata)
        for name, metadata in BLS_SERIES_META.items()
    }
    results = {}

    for series in data.get("Results", {}).get("series", []):
        series_id = series.get("seriesID")
        if series_id not in meta_by_id:
            continue

        name, metadata = meta_by_id[series_id]
        observations = []
        for row in series.get("data", []):
            period = str(row.get("period", ""))
            if not (
                period.startswith("M")
                or period.startswith("Q")
            ):
                continue
            if period == "M13":
                continue
            value = _numeric_text(row.get("value"))
            if value is None:
                continue
            try:
                period_number = int(re.sub(r"\D", "", period))
                year = int(row.get("year"))
            except (TypeError, ValueError):
                continue
            observations.append({
                "year": year,
                "period": period,
                "period_number": period_number,
                "period_name": row.get("periodName", period),
                "value": value,
            })

        observations.sort(
            key=lambda row: (row["year"], row["period_number"])
        )
        if not observations:
            continue

        latest = observations[-1]
        previous = observations[-2] if len(observations) >= 2 else None
        lag = int(metadata.get("lag", 1))
        lagged = observations[-(lag + 1)] if len(observations) > lag else None

        metric_value = latest["value"]
        if metadata["mode"] == "yoy":
            if lagged and lagged["value"] not in (None, 0):
                metric_value = (
                    (latest["value"] - lagged["value"])
                    / lagged["value"]
                ) * 100
            else:
                metric_value = None
        elif metadata["mode"] == "delta":
            metric_value = (
                latest["value"] - previous["value"]
                if previous else None
            )

        results[name] = {
            **metadata,
            "latest_level": latest["value"],
            "previous_level": previous["value"] if previous else None,
            "display_value": metric_value,
            "period": f"{latest['period_name']} {latest['year']}",
        }

    return results


def format_bls_display(item):
    value = item.get("display_value")
    if value is None:
        return "N/A"
    mode = item.get("mode")
    if mode in {"yoy", "percent"}:
        return f"{value:.1f}%"
    if mode == "delta":
        return f"{value:+,.0f}K"
    return f"{value:,.2f}"


@st.cache_data(ttl=3600)
def get_bls_release_calendar(limit=16):
    """Read the automatically updated BLS release calendar."""
    calendar_url = "https://www.bls.gov/schedule/news_release/bls.ics"
    response = requests.get(
        calendar_url,
        headers=PUBLIC_DATA_HEADERS,
        timeout=25,
    )
    response.raise_for_status()

    ics = (
        response.text
        .replace("\r\n ", "")
        .replace("\n ", "")
    )
    blocks = re.findall(
        r"BEGIN:VEVENT(.*?)END:VEVENT",
        ics,
        flags=re.DOTALL,
    )

    material_terms = [
        "consumer price index",
        "producer price index",
        "employment situation",
        "job openings",
        "employment cost index",
        "productivity and costs",
    ]
    source_links = {
        "consumer price index": "https://www.bls.gov/news.release/cpi.htm",
        "producer price index": "https://www.bls.gov/news.release/ppi.htm",
        "employment situation": "https://www.bls.gov/news.release/empsit.htm",
        "job openings": "https://www.bls.gov/news.release/jolts.htm",
        "employment cost index": "https://www.bls.gov/news.release/eci.htm",
        "productivity and costs": "https://www.bls.gov/news.release/prod2.htm",
    }

    events = []
    today = datetime.now(timezone.utc).date()

    for block in blocks:
        summary_match = re.search(
            r"SUMMARY(?:;[^:]*)?:(.*)",
            block,
        )
        date_match = re.search(
            r"DTSTART(?:;[^:]*)?:(\d{8})(?:T(\d{6}))?",
            block,
        )
        if not summary_match or not date_match:
            continue

        summary = (
            summary_match.group(1)
            .strip()
            .replace("\\,", ",")
            .replace("\\;", ";")
        )
        lowered = summary.lower()
        matched_term = next(
            (term for term in material_terms if term in lowered),
            None,
        )
        if not matched_term:
            continue

        date_value = datetime.strptime(
            date_match.group(1),
            "%Y%m%d",
        ).date()
        if date_value < today:
            continue

        time_value = ""
        if date_match.group(2):
            raw_time = date_match.group(2)
            time_value = (
                f"{raw_time[:2]}:{raw_time[2:4]}"
            )

        events.append({
            "Date": date_value.isoformat(),
            "Time": time_value,
            "Event": summary,
            "Agency": "BLS",
            "Source": source_links[matched_term],
        })

    events.sort(key=lambda row: (row["Date"], row["Time"]))
    return events[:limit]


@st.cache_data(ttl=21600)
def get_fomc_calendar(limit=12):
    """Parse the official Federal Reserve FOMC meeting calendar."""
    source_url = (
        "https://www.federalreserve.gov/monetarypolicy/"
        "fomccalendars.htm"
    )
    response = requests.get(
        source_url,
        headers=PUBLIC_DATA_HEADERS,
        timeout=25,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    text_lines = [
        line.strip()
        for line in soup.stripped_strings
        if line.strip()
    ]

    months = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
    }
    today = datetime.now(timezone.utc).date()
    current_year = today.year
    events = []

    for year in [current_year, current_year + 1]:
        heading = f"{year} FOMC Meetings"
        try:
            start = text_lines.index(heading) + 1
        except ValueError:
            continue

        end = len(text_lines)
        for idx in range(start, len(text_lines)):
            if re.fullmatch(r"\d{4} FOMC Meetings", text_lines[idx]):
                end = idx
                break

        block = text_lines[start:end]
        for idx, line in enumerate(block):
            if line not in months:
                continue

            date_text = None
            for candidate in block[idx + 1: idx + 7]:
                if re.fullmatch(r"\d{1,2}(?:-\d{1,2})?\*?", candidate):
                    date_text = candidate
                    break
            if not date_text:
                continue

            clean_date = date_text.rstrip("*")
            parts = clean_date.split("-")
            start_day = int(parts[0])
            end_day = int(parts[-1])
            meeting_end = datetime(
                year,
                months[line],
                end_day,
            ).date()
            if meeting_end < today:
                continue

            events.append({
                "Date": (
                    f"{year}-{months[line]:02d}-{start_day:02d}"
                    + (
                        f" to {year}-{months[line]:02d}-{end_day:02d}"
                        if end_day != start_day else ""
                    )
                ),
                "Time": "",
                "Event": (
                    f"FOMC Meeting{' · SEP' if date_text.endswith('*') else ''}"
                ),
                "Agency": "Federal Reserve",
                "Source": source_url,
            })

    if not events:
        joined = " ".join(text_lines)
        for year in [current_year, current_year + 1]:
            year_match = re.search(
                rf"{year} FOMC Meetings(.*?)(?=\\d{{4}} FOMC Meetings|$)",
                joined,
                flags=re.DOTALL,
            )
            if not year_match:
                continue
            for month_name, date_text in re.findall(
                r"(January|February|March|April|May|June|July|August|"
                r"September|October|November|December)\\s+"
                r"(\\d{1,2}(?:-\\d{1,2})?\\*?)",
                year_match.group(1),
            ):
                clean_date = date_text.rstrip("*")
                parts = clean_date.split("-")
                start_day = int(parts[0])
                end_day = int(parts[-1])
                meeting_end = datetime(
                    year,
                    months[month_name],
                    end_day,
                ).date()
                if meeting_end < today:
                    continue
                events.append({
                    "Date": (
                        f"{year}-{months[month_name]:02d}-{start_day:02d}"
                        + (
                            f" to {year}-{months[month_name]:02d}-{end_day:02d}"
                            if end_day != start_day else ""
                        )
                    ),
                    "Time": "",
                    "Event": (
                        f"FOMC Meeting{' · SEP' if date_text.endswith('*') else ''}"
                    ),
                    "Agency": "Federal Reserve",
                    "Source": source_url,
                })

    events.sort(key=lambda row: row["Date"])
    return events[:limit]


@st.cache_data(ttl=3600)
def get_fed_monetary_updates(limit=6):
    """Read official Federal Reserve monetary-policy press releases."""
    feed_url = "https://www.federalreserve.gov/feeds/press_monetary.xml"
    response = requests.get(
        feed_url,
        headers=PUBLIC_DATA_HEADERS,
        timeout=25,
    )
    response.raise_for_status()
    root = ET.fromstring(response.content)

    rows = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        published = (
            item.findtext("pubDate")
            or item.findtext("date")
            or ""
        ).strip()
        if not title or not link:
            continue
        rows.append({
            "Published": published,
            "Federal Reserve update": title,
            "Source": link,
        })
        if len(rows) >= limit:
            break

    if not rows:
        atom = "{http://www.w3.org/2005/Atom}"
        for entry in root.findall(f".//{atom}entry"):
            title = (
                entry.findtext(f"{atom}title")
                or ""
            ).strip()
            link_element = entry.find(f"{atom}link")
            link = (
                link_element.attrib.get("href", "")
                if link_element is not None else ""
            )
            published = (
                entry.findtext(f"{atom}updated")
                or entry.findtext(f"{atom}published")
                or ""
            ).strip()
            if not title or not link:
                continue
            rows.append({
                "Published": published,
                "Federal Reserve update": title,
                "Source": link,
            })
            if len(rows) >= limit:
                break
    return rows


@st.cache_data(ttl=900)
def get_bloomberg_market_news(limit=10):
    """Return Bloomberg market headlines and outbound links only."""
    feed_candidates = [
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://feeds.bloomberg.com/economics/news.rss",
    ]
    stories = []
    seen = set()

    for feed_url in feed_candidates:
        try:
            response = requests.get(
                feed_url,
                headers=PUBLIC_DATA_HEADERS,
                timeout=20,
            )
            if not response.ok:
                continue
            root = ET.fromstring(response.content)
            for item in root.findall(".//item"):
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                published = (item.findtext("pubDate") or "").strip()
                if not title or not link or title in seen:
                    continue
                seen.add(title)
                stories.append({
                    "Published": published,
                    "Headline": title,
                    "Bloomberg": link,
                })
                if len(stories) >= limit:
                    return stories
        except Exception:
            continue

    # Fallback: capture headline links from Bloomberg Markets without
    # reproducing article text.
    try:
        response = requests.get(
            "https://www.bloomberg.com/markets",
            headers={
                **PUBLIC_DATA_HEADERS,
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 Safari/537.36"
                ),
            },
            timeout=25,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for anchor in soup.find_all("a", href=True):
            title = " ".join(anchor.stripped_strings).strip()
            href = urljoin(
                "https://www.bloomberg.com",
                anchor.get("href", ""),
            )
            if (
                len(title) < 20
                or len(title) > 180
                or "bloomberg.com" not in href
                or "/news/" not in href
                or title in seen
            ):
                continue
            seen.add(title)
            stories.append({
                "Published": "",
                "Headline": title,
                "Bloomberg": href,
            })
            if len(stories) >= limit:
                break
    except Exception:
        pass

    return stories


def _market_news_topic(headline):
    text = str(headline or "").lower()
    if any(term in text for term in [
        "fed", "federal reserve", "rate", "yield", "treasury", "bond"
    ]):
        return "Rates"
    if any(term in text for term in [
        "inflation", "cpi", "ppi", "jobs", "payroll", "gdp", "economy"
    ]):
        return "Economy"
    if any(term in text for term in [
        "oil", "gold", "copper", "commodity", "natural gas"
    ]):
        return "Commodities"
    if any(term in text for term in [
        "stock", "shares", "earnings", "equity", "nasdaq", "s&p"
    ]):
        return "Equities"
    if any(term in text for term in [
        "dollar", "yen", "euro", "currency", "fx"
    ]):
        return "FX"
    return "Markets"


def _market_news_time(value):
    if not value:
        return "Latest"
    parsed = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(parsed):
        return str(value)[:42]
    try:
        eastern = parsed.tz_convert("America/New_York")
        return eastern.strftime("%b %d · %I:%M %p ET")
    except Exception:
        return parsed.strftime("%b %d · %H:%M UTC")


def _news_context_value(value, suffix="", signed=False):
    number = safe_float(value)
    if number is None:
        return "N/A", "flat"
    css_class = "positive" if number > 0 else "negative" if number < 0 else "flat"
    sign = "+" if signed and number > 0 else ""
    return f"{sign}{number:.2f}{suffix}", css_class


def _news_visual_html(topic, context, featured=False):
    """Create an original market-context visual for a news card."""
    topic = str(topic or "Markets")
    context = context or {}
    stats = []
    bars = []
    line_values = []

    if topic == "Rates":
        treasury = context.get("treasury", {})
        stats = [
            ("2Y", treasury.get("2Y"), "%", False),
            ("10Y", treasury.get("10Y"), "%", False),
            ("SOFR", context.get("SOFR"), "%", False),
        ]
        line_values = [
            treasury.get(tenor)
            for tenor in ["1M", "3M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"]
            if safe_float(treasury.get(tenor)) is not None
        ]
    elif topic == "Economy":
        stats = [
            ("CPI YoY", context.get("CPI"), "%", True),
            ("PPI YoY", context.get("PPI"), "%", True),
            ("Unemp.", context.get("Unemployment"), "%", False),
        ]
        bars = [
            context.get("CPI"),
            context.get("Core CPI"),
            context.get("PPI"),
            context.get("Unemployment"),
        ]
    elif topic == "Commodities":
        stats = [
            ("Gold · GLD", context.get("GLD"), "%", True),
            ("Oil · USO", context.get("USO"), "%", True),
        ]
        bars = [context.get("GLD"), context.get("USO"), 0.4, -0.25, 0.6]
    elif topic == "FX":
        stats = [
            ("USD · UUP", context.get("UUP"), "%", True),
            ("10Y", context.get("treasury", {}).get("10Y"), "%", False),
        ]
        bars = [context.get("UUP"), 0.25, -0.15, 0.4, -0.1]
    else:
        stats = [
            ("S&P · SPY", context.get("SPY"), "%", True),
            ("Nasdaq · QQQ", context.get("QQQ"), "%", True),
            ("10Y", context.get("treasury", {}).get("10Y"), "%", False),
        ]
        bars = [
            context.get("SPY"),
            context.get("QQQ"),
            context.get("GLD"),
            context.get("USO"),
        ]

    stat_html = []
    for label, value, suffix, signed in stats:
        value_text, css_class = _news_context_value(
            value,
            suffix=suffix,
            signed=signed,
        )
        stat_html.append(
            '<div class="el-news-viz-stat">'
            f'<div class="el-news-viz-label">{html.escape(label)}</div>'
            f'<div class="el-news-viz-value {css_class}">{html.escape(value_text)}</div>'
            '</div>'
        )

    visual_layer = ""
    clean_line = [
        safe_float(value)
        for value in line_values
        if safe_float(value) is not None
    ]
    if len(clean_line) >= 2:
        minimum = min(clean_line)
        maximum = max(clean_line)
        span = maximum - minimum or 1.0
        x_step = 100 / max(1, len(clean_line) - 1)
        points = []
        area_points = ["0,54"]
        for index, value in enumerate(clean_line):
            x = index * x_step
            y = 45 - ((value - minimum) / span) * 30
            points.append(f"{x:.1f},{y:.1f}")
            area_points.append(f"{x:.1f},{y:.1f}")
        area_points.append("100,54")
        visual_layer = (
            '<svg class="el-news-viz-line" viewBox="0 0 100 54" '
            'preserveAspectRatio="none" aria-hidden="true">'
            f'<polygon class="el-news-viz-area" points="{" ".join(area_points)}"></polygon>'
            f'<polyline points="{" ".join(points)}"></polyline>'
            '</svg>'
        )
    else:
        clean_bars = [
            safe_float(value)
            for value in bars
            if safe_float(value) is not None
        ]
        if not clean_bars:
            clean_bars = [0.2, 0.7, 0.45, 0.85, 0.58]
        magnitude = max(max(abs(value) for value in clean_bars), 0.01)
        bar_html = []
        for value in clean_bars:
            height = 9 + (abs(value) / magnitude) * 24
            opacity = 0.45 if value < 0 else 0.88
            bar_html.append(
                f'<span class="el-news-viz-bar" style="height:{height:.1f}px;opacity:{opacity:.2f};"></span>'
            )
        visual_layer = (
            '<div class="el-news-viz-bars">'
            + "".join(bar_html)
            + '</div>'
        )

    visual_label = "Live market context" if featured else "Market context"
    return (
        '<div class="el-news-visual">'
        f'<div class="el-news-visual-kicker">{visual_label}</div>'
        '<div class="el-news-viz-stats">'
        + "".join(stat_html)
        + '</div>'
        + visual_layer
        + '</div>'
    )


def render_market_news_cards(stories, market_context=None):
    """Render Bloomberg headlines with original EquityLens market visuals."""
    if not stories:
        return

    cards = []
    for index, story in enumerate(stories[:9]):
        raw_headline = str(story.get("Headline", "")).strip()
        headline = html.escape(raw_headline)
        link = html.escape(str(story.get("Bloomberg", "")).strip(), quote=True)
        published = html.escape(
            _market_news_time(story.get("Published", ""))
        )
        topic_raw = _market_news_topic(raw_headline)
        topic = html.escape(topic_raw)

        if not headline or not link:
            continue

        featured = index == 0
        featured_class = " featured" if featured else ""
        visual_html = _news_visual_html(
            topic_raw,
            market_context or {},
            featured=featured,
        )

        cards.append(
            f'<a class="el-news-card{featured_class}" '
            f'href="{link}" target="_blank" rel="noopener noreferrer">'
            '<div class="el-news-card-top">'
            '<span class="el-news-source">Bloomberg</span>'
            f'<span class="el-news-topic">{topic}</span>'
            '</div>'
            f'<div class="el-news-headline">{headline}</div>'
            f'{visual_html}'
            '<div class="el-news-spacer"></div>'
            '<div class="el-news-footer">'
            f'<span class="el-news-time">{published}</span>'
            '<span class="el-news-read">Read story ↗</span>'
            '</div>'
            '</a>'
        )

    if not cards:
        return

    st.markdown(
        """
        <div class="el-news-shell">
            <div class="el-news-topline">
                <span class="el-news-live">Latest market headlines</span>
                <span>Bloomberg headlines · EquityLens market context visuals</span>
            </div>
            <div class="el-news-grid">
        """
        + "".join(cards)
        + """
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=900)
def get_optional_swap_rates():
    """
    Load USD SOFR OIS curve data.

    Priority:
      1. A user-configured JSON endpoint in Streamlit Secrets.
      2. CheckMySwap's free public USD SOFR OIS curve endpoint.

    CheckMySwap publishes indicative OIS curves derived from public DTCC
    swap transaction reports. These are dated curve estimates, not executable
    dealer quotes.
    """
    configured_endpoint = str(
        st.secrets.get("SWAP_RATES_JSON_URL", "")
    ).strip()
    endpoint = (
        configured_endpoint
        if configured_endpoint
        else "https://checkmyswap.com/api/curves/USD"
    )

    response = requests.get(
        endpoint,
        headers=PUBLIC_DATA_HEADERS,
        timeout=25,
    )
    response.raise_for_status()
    payload = response.json()

    rows = []
    curve_date = ""

    if isinstance(payload, dict) and isinstance(payload.get("curve"), list):
        curve_date = str(payload.get("date", "")).strip()
        for record in payload.get("curve", []):
            if not isinstance(record, dict):
                continue
            tenor = record.get("tenor")
            rate = _numeric_text(record.get("rate"))
            if tenor and rate is not None:
                rows.append({
                    "Tenor": str(tenor),
                    "Swap Rate": rate,
                    "Curve Date": curve_date or str(record.get("date", "")),
                    "Source": str(
                        record.get("source", "CheckMySwap / DTCC public data")
                    ),
                    "Method": str(record.get("method", "")),
                })
    elif isinstance(payload, dict):
        for tenor, rate in payload.items():
            numeric = _numeric_text(rate)
            if numeric is not None:
                rows.append({
                    "Tenor": str(tenor),
                    "Swap Rate": numeric,
                    "Curve Date": "",
                    "Source": "Configured provider",
                    "Method": "",
                })
    elif isinstance(payload, list):
        for record in payload:
            if not isinstance(record, dict):
                continue
            tenor = (
                record.get("tenor")
                or record.get("Tenor")
                or record.get("maturity")
            )
            rate = (
                record.get("rate")
                or record.get("Rate")
                or record.get("swap_rate")
            )
            numeric = _numeric_text(rate)
            if tenor and numeric is not None:
                rows.append({
                    "Tenor": str(tenor),
                    "Swap Rate": numeric,
                    "Curve Date": str(record.get("date", "")),
                    "Source": str(record.get("source", "Configured provider")),
                    "Method": str(record.get("method", "")),
                })

    return rows



def render_nyse_market_monitor(nyse_finviz):
    """Render the Finviz-powered NYSE ticker and heat map."""
    section("NYSE", "NYSE Market Ticker")

    if nyse_finviz is None or nyse_finviz.empty:
        st.info(
            "NYSE market data is not available right now. "
            "Check the Finviz Elite connection and refresh the page."
        )
        return

    ticker_source = nyse_finviz.copy()

    if "Volume" in ticker_source.columns:
        ticker_source["_volume_num"] = ticker_source["Volume"].apply(finviz_numeric)
        ticker_source = ticker_source.sort_values(
            "_volume_num",
            ascending=False,
            na_position="last"
        )

    ticker_source = ticker_source.head(20)

    tape_items = []
    for _, ticker_row in ticker_source.iterrows():
        ticker_symbol = str(ticker_row.get("Ticker", "")).strip()
        company_name = str(ticker_row.get("Company", "")).strip()
        ticker_price = finviz_numeric(ticker_row.get("Price"))
        ticker_change = finviz_numeric(ticker_row.get("Change"))

        if not ticker_symbol:
            continue

        if not company_name or company_name.lower() == "nan":
            company_name = ticker_symbol

        if ticker_change is None:
            change_class = "flat"
            change_text = "N/A"
            arrow = "•"
        elif ticker_change > 0:
            change_class = "positive"
            change_text = f"{ticker_change:.2f}%"
            arrow = "▲"
        elif ticker_change < 0:
            change_class = "negative"
            change_text = f"{abs(ticker_change):.2f}%"
            arrow = "▼"
        else:
            change_class = "flat"
            change_text = "0.00%"
            arrow = "•"

        price_text = (
            "$" + f"{ticker_price:,.2f}"
            if ticker_price is not None
            else "N/A"
        )

        tape_items.append(
            '<div class="el-ticker-item">'
            f'<span class="el-ticker-company">{html.escape(company_name)}</span>'
            f'<span class="el-ticker-symbol">{html.escape(ticker_symbol)}</span>'
            f'<span class="el-ticker-price">{price_text}</span>'
            f'<span class="el-ticker-change {change_class}">'
            f'<span class="el-ticker-arrow">{arrow}</span>{change_text}'
            '</span></div>'
        )

    if tape_items:
        tape_html = "".join(tape_items + tape_items)
        st.markdown(
            f"""
            <div class="el-exchange-tape">
                <div class="el-exchange-pill">
                    <span>NYSE</span>
                    <span class="el-exchange-chevron">⌄</span>
                </div>
                <div class="el-ticker-shell">
                    <div class="el-ticker-track">{tape_html}</div>
                </div>
            </div>
            <div class="el-market-delay">
                Finviz Elite · market timing follows your data entitlement · hover to pause
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.caption("NYSE ticker data is not available in the current Finviz response.")

    section("Market Map", "NYSE Heat Map")

    st.markdown(
        """
        <div class="el-heatmap-head">
            <div class="el-heatmap-copy">
                Larger tiles represent larger market capitalization. Color represents today's price move.
            </div>
            <div class="el-heatmap-legend">
                <span class="el-legend-item"><span class="el-legend-swatch" style="background:#7F1D1D;"></span>Lower</span>
                <span class="el-legend-item"><span class="el-legend-swatch" style="background:#B94A50;"></span>Down</span>
                <span class="el-legend-item"><span class="el-legend-swatch" style="background:#24333A;"></span>Flat</span>
                <span class="el-legend-item"><span class="el-legend-swatch" style="background:#137F72;"></span>Up</span>
                <span class="el-legend-item"><span class="el-legend-swatch" style="background:#16C7B2;"></span>Higher</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    heatmap_required = {"Ticker", "Sector", "Market Cap", "Change"}
    if not heatmap_required.issubset(set(nyse_finviz.columns)):
        st.caption(
            "The current Finviz response is missing one or more fields needed for the NYSE heat map."
        )
        return

    heatmap_df = nyse_finviz.copy()
    heatmap_df["_market_cap_num"] = heatmap_df["Market Cap"].apply(finviz_numeric)
    heatmap_df["_change_num"] = heatmap_df["Change"].apply(finviz_numeric)
    heatmap_df = heatmap_df.dropna(
        subset=["_market_cap_num", "_change_num", "Sector"]
    )
    heatmap_df = heatmap_df[heatmap_df["_market_cap_num"] > 0]

    available_sectors = sorted(
        [
            str(sector)
            for sector in heatmap_df["Sector"].dropna().unique().tolist()
            if str(sector).strip()
        ]
    )

    heat_controls = st.columns([1.35, 1, 1.15])
    with heat_controls[0]:
        selected_heat_sector = st.selectbox(
            "Heat map sector",
            ["All sectors"] + available_sectors,
            key="nyse_heatmap_sector"
        )
    with heat_controls[1]:
        heatmap_limit = st.select_slider(
            "Companies shown",
            options=[40, 60, 80, 100, 120],
            value=120,
            key="nyse_heatmap_limit"
        )
    with heat_controls[2]:
        heatmap_search = st.text_input(
            "Find ticker",
            placeholder="e.g. JPM",
            key="nyse_heatmap_search"
        ).strip().upper()

    if selected_heat_sector != "All sectors":
        heatmap_df = heatmap_df[
            heatmap_df["Sector"].astype(str) == selected_heat_sector
        ]

    heatmap_df = heatmap_df.sort_values(
        "_market_cap_num",
        ascending=False
    ).head(heatmap_limit)

    if heatmap_df.empty:
        st.caption("No NYSE companies match the current heat-map filters.")
        return

    matching_tickers = set()
    if heatmap_search:
        matching_tickers = set(
            heatmap_df.loc[
                heatmap_df["Ticker"].astype(str).str.upper().str.contains(
                    heatmap_search,
                    regex=False,
                    na=False
                ),
                "Ticker"
            ].astype(str).tolist()
        )

    sector_rows = (
        heatmap_df.groupby("Sector", dropna=False)
        .apply(
            lambda group: pd.Series({
                "_sector_cap": group["_market_cap_num"].sum(),
                "_sector_change": (
                    (group["_change_num"] * group["_market_cap_num"]).sum()
                    / group["_market_cap_num"].sum()
                )
            })
        )
        .reset_index()
    )

    heat_ids = []
    heat_labels = []
    heat_parents = []
    heat_values = []
    heat_colors = []
    heat_custom = []

    for _, sector_row in sector_rows.iterrows():
        sector_name = str(sector_row["Sector"])
        heat_ids.append(f"sector::{sector_name}")
        heat_labels.append(sector_name)
        heat_parents.append("")
        heat_values.append(float(sector_row["_sector_cap"]))
        heat_colors.append(float(sector_row["_sector_change"]))
        heat_custom.append([
            sector_name,
            "",
            "",
            float(sector_row["_sector_change"]),
            float(sector_row["_sector_cap"]),
            ""
        ])

    for _, stock_row in heatmap_df.iterrows():
        ticker_symbol = str(stock_row.get("Ticker", ""))
        company_name = str(stock_row.get("Company", ""))
        sector_name = str(stock_row.get("Sector", ""))
        price_value = finviz_numeric(stock_row.get("Price"))
        change_value = float(stock_row["_change_num"])

        heat_ids.append(f"stock::{ticker_symbol}")
        heat_labels.append(ticker_symbol)
        heat_parents.append(f"sector::{sector_name}")
        heat_values.append(float(stock_row["_market_cap_num"]))
        heat_colors.append(change_value)
        heat_custom.append([
            company_name,
            sector_name,
            ("$" + f"{price_value:,.2f}") if price_value is not None else "N/A",
            change_value,
            float(stock_row["_market_cap_num"]),
            "Match" if ticker_symbol in matching_tickers else ""
        ])

    heat_fig = go.Figure(
        go.Treemap(
            ids=heat_ids,
            labels=heat_labels,
            parents=heat_parents,
            values=heat_values,
            branchvalues="total",
            maxdepth=2,
            pathbar={
                "visible": True,
                "textfont": {
                    "family": "IBM Plex Mono",
                    "size": 12,
                    "color": "#C6D0D5"
                },
                "thickness": 28
            },
            tiling={
                "packing": "squarify",
                "pad": 2
            },
            marker={
                "colors": heat_colors,
                "colorscale": [
                    [0.0, "#7F1D1D"],
                    [0.35, "#B94A50"],
                    [0.5, "#24333A"],
                    [0.65, "#137F72"],
                    [1.0, "#16C7B2"]
                ],
                "cmid": 0,
                "line": {"color": "#050B0E", "width": 1.4}
            },
            customdata=heat_custom,
            hovertemplate=(
                "<b>%{label}</b><br>"
                "%{customdata[0]}<br>"
                "Sector: %{customdata[1]}<br>"
                "Price: %{customdata[2]}<br>"
                "Daily change: %{customdata[3]:+.2f}%<br>"
                "Market cap: $%{customdata[4]:,.0f}<br>"
                "%{customdata[5]}"
                "<extra></extra>"
            ),
            texttemplate="<b>%{label}</b><br>%{customdata[3]:+.1f}%",
            textfont={"family": "IBM Plex Mono", "size": 13},
            hoverlabel={
                "bgcolor": "#091217",
                "bordercolor": "#263640",
                "font": {
                    "family": "IBM Plex Sans",
                    "color": "#EEF3F5"
                }
            },
            root={"color": "#071014"}
        )
    )
    heat_fig.update_layout(
        height=680,
        margin={"l": 0, "r": 0, "t": 8, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#050B0E",
        font={"color": "#EEF3F5", "family": "IBM Plex Sans"}
    )

    st.plotly_chart(
        heat_fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )
    st.caption(
        "Click a sector to drill into it, then use the breadcrumb above the map to return. "
        "Tile size represents market capitalization and color represents daily price change."
    )

    if heatmap_search:
        if matching_tickers:
            st.caption(
                "Ticker search match: " + ", ".join(sorted(matching_tickers))
            )
        else:
            st.caption(
                f'No displayed ticker matches "{heatmap_search}". Try a broader search or show more companies.'
            )


def safe_float(value):
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def market_return(history, sessions):
    if history is None or history.empty or len(history) <= sessions:
        return None

    latest = safe_float(history.iloc[-1].get("close"))
    prior = safe_float(history.iloc[-(sessions + 1)].get("close"))

    if latest is None or prior in (None, 0):
        return None

    return ((latest - prior) / prior) * 100


def format_market_price(value):
    number = safe_float(value)
    return "$" + f"{number:,.2f}" if number is not None else "N/A"


def format_market_volume(value):
    number = safe_float(value)
    if number is None:
        return "N/A"
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.2f}B"
    if number >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"
    if number >= 1_000:
        return f"{number / 1_000:.1f}K"
    return f"{number:,.0f}"


def format_money(value):
    if value is None:
        return "N/A"
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000_000:
        return f"{sign}${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"{sign}${value / 1_000_000:.1f}M"
    return f"{sign}${value:,.0f}"


def pct(value):
    return f"{value:.1f}%" if value is not None else "N/A"


def format_multiple(value):
    return f"{value:.2f}x" if value is not None else "N/A"


def calc_growth(current, prior):
    if current is None or prior in (None, 0):
        return None
    return ((current - prior) / prior) * 100


def calc_margin(profit, revenue):
    if profit is None or revenue in (None, 0):
        return None
    return (profit / revenue) * 100


def section(label, title):
    st.markdown(
        f"""
        <div class="el-section">
            <div class="el-section-label">{label}</div>
            <div class="el-section-title">{title}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_summary_cards(cards):
    cols = st.columns(len(cards))
    for col, (label, value) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="el-summary-card">
                    <div class="el-summary-label">{label}</div>
                    <div class="el-summary-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


def quarterly_metrics(qdata):
    latest = qdata.get("latest_quarter", {})
    prior_q = qdata.get("prior_quarter", {})
    prior_y = qdata.get("prior_year_quarter", {})

    revenue = latest.get("revenue")
    prior_q_revenue = prior_q.get("revenue")
    prior_y_revenue = prior_y.get("revenue")

    return {
        "revenue": revenue,
        "yoy_growth": calc_growth(revenue, prior_y_revenue),
        "qoq_growth": calc_growth(revenue, prior_q_revenue),
        "gross_margin": calc_margin(latest.get("gross_profit"), revenue),
        "operating_margin": calc_margin(latest.get("operating_income"), revenue),
        "net_margin": calc_margin(latest.get("net_income"), revenue),
        "prior_q_operating_margin": calc_margin(
            prior_q.get("operating_income"), prior_q_revenue
        ),
        "prior_y_operating_margin": calc_margin(
            prior_y.get("operating_income"), prior_y_revenue
        )
    }


def build_change_notes(qdata):
    latest = qdata.get("latest_quarter", {})
    prior_q = qdata.get("prior_quarter", {})
    prior_y = qdata.get("prior_year_quarter", {})
    m = quarterly_metrics(qdata)

    notes = []

    if m["qoq_growth"] is not None:
        notes.append((
            "Sequential revenue",
            f"Revenue changed {m['qoq_growth']:+.1f}% from the prior quarter, "
            f"from {format_money(prior_q.get('revenue'))} to {format_money(latest.get('revenue'))}."
        ))

    if m["yoy_growth"] is not None:
        notes.append((
            "Year-over-year revenue",
            f"Revenue changed {m['yoy_growth']:+.1f}% from the same quarter a year earlier, "
            f"from {format_money(prior_y.get('revenue'))} to {format_money(latest.get('revenue'))}."
        ))

    if m["operating_margin"] is not None and m["prior_q_operating_margin"] is not None:
        delta = m["operating_margin"] - m["prior_q_operating_margin"]
        notes.append((
            "Operating margin",
            f"Operating margin changed {delta:+.1f} percentage points sequentially, "
            f"from {m['prior_q_operating_margin']:.1f}% to {m['operating_margin']:.1f}%."
        ))

    current_net = latest.get("net_income")
    prior_net = prior_q.get("net_income")
    if current_net is not None and prior_net is not None:
        if prior_net < 0 <= current_net:
            copy = (
                f"Net income moved from a loss of {format_money(prior_net)} "
                f"to profit of {format_money(current_net)}."
            )
        elif prior_net >= 0 > current_net:
            copy = (
                f"Net income moved from profit of {format_money(prior_net)} "
                f"to a loss of {format_money(current_net)}."
            )
        else:
            copy = (
                f"Net income changed from {format_money(prior_net)} "
                f"to {format_money(current_net)}."
            )
        notes.append(("Net income", copy))

    return notes


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
sec_filings = load_json("data/sec_filings.json")

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
    company_analysis.setdefault(_key, {})
    company_quarterly.setdefault(_key, {})
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

st.markdown(
    """
    <div class="el-product-hero">
        <div class="el-eyebrow">Public-markets research, made legible</div>
        <h1 class="el-product-title">Understand public companies.<br><span>Without digging through hundreds of pages.</span></h1>
        <p class="el-product-subtitle">
            EquityLens organizes financial performance, company strategy, risk disclosures,
            business models, and SEC filings into structured research while keeping the
            original sources visible. <strong style="color:#16C7B2;">EquityLens informs. You decide.</strong>
        </p>
        <div class="el-badges">
            <span class="el-badge">SEC EDGAR sourced</span>
            <span class="el-badge">Calculations shown</span>
            <span class="el-badge">Direct filing links</span>
            <span class="el-badge">Period-aware research</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="el-trust-strip">
        <div class="el-trust-item">Primary SEC sources</div>
        <div class="el-trust-item">Reported vs. calculated</div>
        <div class="el-trust-item">Plain-language explanations</div>
        <div class="el-trust-item">Source-linked research</div>
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("Methodology & source standards"):
    st.markdown(
        """
        **Reported** — taken from a company filing or company-reported disclosure.

        **Calculated by EquityLens** — derived from reported figures, such as growth rates,
        margins, and trailing-twelve-month metrics.

        **Research summary** — plain-language context built from structured company information
        and filing disclosures. It is not a recommendation.

        **Source priority:** SEC EDGAR first, company investor-relations disclosures second,
        and appropriately licensed market-data providers where needed.
        """
    )


sec_synced_companies = sum(
    1
    for _company_feed in sec_filings.values()
    if _company_feed.get("cik")
    and _company_feed.get("filings")
)

deep_research_tickers = {
    str(company_data.get(_key, {}).get("ticker", "")).upper()
    for _key, _analysis in company_analysis.items()
    if _analysis and _analysis.get("business_model")
}
deep_research_tickers.discard("")

render_summary_cards([
    ("Companies", f"{len(company_universe):,}"),
    ("Industries", f"{company_universe['Industry'].nunique():,}"),
    ("SEC Synced", f"{sec_synced_companies:,} / {len(company_universe):,}"),
    ("Deep Research", f"{len(deep_research_tickers):,} / {len(company_universe):,}"),
    ("Primary Source", "SEC EDGAR")
])

home_tab, company_tab, peer_tab, research_tab, market_tab, sec_tracker_tab, learn_tab = st.tabs([
    "Home",
    "Explore Companies",
    "Industry Comparison",
    "EquityLens",
    "Market Monitor",
    "Filings",
    "Learn"
])

with home_tab:
    st.markdown(
        """
        <div class="el-user-intro">
            <div class="el-user-intro-kicker">Start with what you want to know</div>
            <div class="el-user-intro-title">What are you trying to understand?</div>
            <div class="el-user-intro-copy">
                EquityLens is organized around research questions, not a pile of financial data.
                Pick the path that matches what you are actually trying to figure out.
            </div>
        </div>
        <div class="el-intent-grid">
            <div class="el-intent-card">
                <div class="el-intent-label">Explore Companies</div>
                <div class="el-intent-title">How does this company work?</div>
                <div class="el-intent-copy">Understand the business model, customers, strategy, risks, and IPO-era story from its S-1.</div>
            </div>
            <div class="el-intent-card">
                <div class="el-intent-label">Industry Comparison</div>
                <div class="el-intent-title">How does it compare with peers?</div>
                <div class="el-intent-copy">Compare growth, margins, capital structure, business models, and risk themes on the same page.</div>
            </div>
            <div class="el-intent-card">
                <div class="el-intent-label">EquityLens</div>
                <div class="el-intent-title">What should I understand first?</div>
                <div class="el-intent-copy">Get a structured company brief covering performance, business model, risk themes, recent changes, and source links without using a chatbot.</div>
            </div>
            <div class="el-intent-card">
                <div class="el-intent-label">Market Monitor</div>
                <div class="el-intent-title">What is moving now?</div>
                <div class="el-intent-copy">See prices, daily changes, volume, notable movement, and recent SEC filing context for covered companies.</div>
            </div>
            <div class="el-intent-card">
                <div class="el-intent-label">Learn</div>
                <div class="el-intent-title">What does this metric mean?</div>
                <div class="el-intent-copy">Learn the financial concepts first, then return to the company with enough context to interpret the numbers.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    section("Coverage Universe", "Broader public-company coverage")

    coverage_metrics = st.columns(3)
    coverage_metrics[0].metric("Companies", f"{len(company_universe):,}")
    coverage_metrics[1].metric("Sectors", f"{company_universe['Sector'].nunique():,}")
    coverage_metrics[2].metric("Industries", f"{company_universe['Industry'].nunique():,}")

    st.write(
        "EquityLens now maintains a broader market-coverage universe sourced from the "
        "Finviz list you provided. These companies can be explored in Market Monitor "
        "with market context and SEC filing access, while the original deep-research "
        "set retains the most detailed structured financial analysis."
    )

    home_coverage_cols = st.columns(2)
    with home_coverage_cols[0]:
        home_coverage_sector = st.selectbox(
            "Browse sector",
            coverage_sectors,
            key="home_coverage_sector"
        )

    home_sector_df = company_universe[
        company_universe["Sector"] == home_coverage_sector
    ]
    home_sector_industries = sorted(
        [
            value for value in home_sector_df["Industry"].dropna().unique().tolist()
            if value
        ]
    )

    with home_coverage_cols[1]:
        home_coverage_industry = st.selectbox(
            "Browse industry",
            ["All industries"] + home_sector_industries,
            key="home_coverage_industry"
        )

    home_coverage_df = home_sector_df.copy()
    if home_coverage_industry != "All industries":
        home_coverage_df = home_coverage_df[
            home_coverage_df["Industry"] == home_coverage_industry
        ]

    st.caption(
        f"{len(home_coverage_df):,} companies in the current coverage view."
    )

    st.dataframe(
        home_coverage_df[
            [
                column for column in
                ["Ticker", "Company", "Industry", "Country"]
                if column in home_coverage_df.columns
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    section("Interactive preview", "See the research, not just the promise.")

    preview_industries = sorted(
        [
            value for value in company_universe["Industry"].dropna().unique().tolist()
            if value
        ]
    )

    home_industry = st.selectbox(
        "Choose industry",
        preview_industries,
        key="home_industry"
    )

    home_company_df = company_universe[
        company_universe["Industry"] == home_industry
    ].copy()

    st.caption(
        f"{len(home_company_df):,} companies in {home_industry} · "
        f"{len(company_universe):,} companies available across EquityLens."
    )

    home_company = st.selectbox(
        "Choose company",
        home_company_df["Coverage Key"].tolist(),
        format_func=lambda key: (
            key.split(" (")[-1].rstrip(")")
            + " · "
            + key.rsplit(" (", 1)[0]
        ),
        key="home_company"
    )

    home_row = home_company_df[
        home_company_df["Coverage Key"] == home_company
    ].iloc[0]

    home_ticker = str(home_row.get("Ticker", ""))
    home_name = str(home_row.get("Company", ""))
    home_sector = str(home_row.get("Sector", ""))
    home_country = str(home_row.get("Country", ""))

    deep_company = next(
        (
            company_name
            for company_name, company in company_data.items()
            if str(company.get("ticker", "")).upper() == home_ticker
        ),
        None
    )

    deep_data = company_data.get(deep_company, {}) if deep_company else {}
    deep_analysis = company_analysis.get(deep_company, {}) if deep_company else {}
    deep_qdata = company_quarterly.get(deep_company, {}) if deep_company else {}
    deep_qm = quarterly_metrics(deep_qdata) if deep_company else {}
    deep_latest = deep_qdata.get("latest_quarter", {}) if deep_company else {}

    if deep_company:
        preview_description = deep_analysis.get(
            "business_model",
            "Structured company research is available from EquityLens."
        )
        coverage_badge = "Deep research + SEC"
    else:
        preview_description = (
            f"{home_name} is covered in the {home_industry} industry within "
            f"{home_sector}. EquityLens combines market context with primary-source "
            "SEC filing access for this broader coverage universe."
        )
        coverage_badge = "Market + SEC coverage"

    st.markdown(
        f"""
        <div class="el-company-hero">
            <div class="el-kicker">{home_ticker} · {home_industry}</div>
            <div class="el-company-title">{home_name}</div>
            <p class="el-subtitle">{preview_description}</p>
            <div class="el-badges">
                <span class="el-badge">{home_sector}</span>
                <span class="el-badge">{home_country}</span>
                <span class="el-badge">{coverage_badge}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if deep_company:
        home_metrics = st.columns(4)
        if deep_latest.get("revenue") is not None:
            home_metrics[0].metric(
                "Quarter Revenue",
                format_money(deep_latest.get("revenue"))
            )
            home_metrics[1].metric(
                "YoY Growth",
                pct(deep_qm.get("yoy_growth"))
            )
            home_metrics[2].metric(
                "Operating Margin",
                pct(deep_qm.get("operating_margin"))
            )
        else:
            home_metrics[0].metric(
                "Fiscal Year Revenue",
                format_money(deep_data.get("revenue"))
            )
            deep_history = deep_data.get("history", [])
            deep_prior_revenue = (
                deep_history[-2].get("revenue")
                if len(deep_history) >= 2 else None
            )
            home_metrics[1].metric(
                "Revenue Growth",
                pct(
                    calc_growth(
                        deep_data.get("revenue"),
                        deep_prior_revenue
                    )
                )
            )
            home_metrics[2].metric(
                "Operating Margin",
                pct(
                    calc_margin(
                        deep_data.get("operating_income"),
                        deep_data.get("revenue")
                    )
                )
            )
        home_metrics[3].metric(
            "Cash + Investments",
            format_money(
                deep_data.get(
                    "capital_structure",
                    {}
                ).get("cash_and_investments")
            )
        )
    else:
        preview_metrics = st.columns(4)
        csv_price = finviz_numeric(home_row.get("Price"))
        csv_change = finviz_numeric(home_row.get("Change"))
        csv_pe = finviz_numeric(home_row.get("P/E"))
        csv_market_cap = finviz_numeric(home_row.get("Market Cap"))

        preview_metrics[0].metric(
            "Market Price",
            ("$" + f"{csv_price:,.2f}") if csv_price is not None else "N/A",
            f"{csv_change:+.2f}%" if csv_change is not None else None
        )
        preview_metrics[1].metric(
            "P/E",
            f"{csv_pe:.1f}x" if csv_pe is not None else "N/A"
        )
        preview_metrics[2].metric(
            "Market Cap",
            (
                "$" + f"{csv_market_cap / 1_000_000:.2f}T"
                if csv_market_cap is not None and csv_market_cap >= 1_000_000
                else (
                    "$" + f"{csv_market_cap / 1_000:.1f}B"
                    if csv_market_cap is not None
                    else "N/A"
                )
            )
        )
        preview_metrics[3].metric("Coverage", "SEC + Market")

    section("Primary Research", f"{home_ticker} SEC Filing Research")

    sec_research = {}
    sec_error = None
    try:
        sec_research = get_sec_company_research(home_ticker)
    except Exception:
        sec_error = (
            "SEC data is temporarily unavailable for this company. "
            "The market-coverage record is still available."
        )

    if sec_error:
        st.warning(sec_error)
    else:
        sec_filings_live = sec_research.get("filings", [])
        annual_filing = latest_filing_by_forms(
            sec_filings_live,
            {"10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"}
        )
        quarter_filing = latest_filing_by_forms(
            sec_filings_live,
            {"10-Q", "10-Q/A"}
        )
        current_filing = latest_filing_by_forms(
            sec_filings_live,
            {"8-K", "8-K/A", "6-K", "6-K/A"}
        )
        registration_filings = sec_research.get(
            "registration_filings",
            []
        )
        registration_filing = (
            registration_filings[0]
            if registration_filings
            else {}
        )

        filing_metrics = st.columns(4)
        filing_metrics[0].metric(
            "Latest Annual",
            annual_filing.get("form", "N/A"),
            annual_filing.get("filing_date") or None
        )
        filing_metrics[1].metric(
            "Latest Quarterly",
            quarter_filing.get("form", "N/A"),
            quarter_filing.get("filing_date") or None
        )
        filing_metrics[2].metric(
            "Latest Current Report",
            current_filing.get("form", "N/A"),
            current_filing.get("filing_date") or None
        )
        filing_metrics[3].metric(
            "IPO / Registration",
            registration_filing.get("form", "Not found"),
            registration_filing.get("filing_date") or None
        )

        if registration_filing:
            st.markdown(
                f"""
                <div class="el-quick-read">
                    <div class="el-quick-read-kicker">IPO-era source · {registration_filing.get('form', '')}</div>
                    <div class="el-quick-read-title">Registration filing available</div>
                    <div class="el-quick-read-copy">
                        EquityLens found a registration filing for {home_name}. This primary source
                        is where users can inspect the company's IPO-era business description,
                        risk factors, financial history, ownership structure, use of proceeds,
                        competition, and market opportunity as disclosed at the time.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if registration_filing.get("url"):
                st.link_button(
                    f"Open {registration_filing.get('form')} on SEC EDGAR",
                    registration_filing.get("url"),
                    key="home_registration_link"
                )
        else:
            st.caption(
                "No S-1, F-1, or S-11 registration statement was found in the "
                "SEC history scanned for this issuer. Older issuers may predate modern "
                "EDGAR coverage or may have used a different registration path."
            )

        recent_research_rows = []
        for filing in sec_filings_live[:12]:
            recent_research_rows.append({
                "Filed": filing.get("filing_date", ""),
                "Form": filing.get("form", ""),
                "Period": filing.get("report_date", ""),
                "Description": (
                    filing.get("description", "")
                    or filing.get("primary_document", "")
                ),
                "SEC Filing": filing.get("url", "")
            })

        if recent_research_rows:
            st.dataframe(
                pd.DataFrame(recent_research_rows),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SEC Filing": st.column_config.LinkColumn(
                        "SEC Filing",
                        display_text="Open filing"
                    )
                }
            )

        sec_company_url = sec_research.get("sec_company_url", "")
        if sec_company_url:
            st.link_button(
                "Open complete SEC company filing history",
                sec_company_url,
                key="home_sec_company_history"
            )

    if deep_company:
        static_s1 = company_s1.get(deep_company, {})
        if static_s1:
            st.markdown(
                f"""
                <div class="el-quick-read">
                    <div class="el-quick-read-kicker">EquityLens deep research</div>
                    <div class="el-quick-read-title">What the IPO filing helps explain</div>
                    <div class="el-quick-read-copy">
                        {static_s1.get('what_to_learn', static_s1.get('historical_context', ''))}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.caption(
        "The selector above uses the full 517-company coverage universe. SEC filing "
        "research is resolved on demand from EDGAR, while the original deep-research "
        "companies retain additional structured financial and narrative analysis."
    )

    st.markdown(
        """
        <div class="el-next-grid">
            <div class="el-next-card">
                <div class="el-next-title">Want the company story?</div>
                <div class="el-next-copy">Use the SEC filing research above for primary-source documents. Deep-research companies also include structured business-model, market-opportunity, competition, and risk analysis.</div>
            </div>
            <div class="el-next-card">
                <div class="el-next-title">Want context?</div>
                <div class="el-next-copy">Open Industry Comparison to see whether the company's growth, margins, and capital structure differ from selected peers.</div>
            </div>
            <div class="el-next-card">
                <div class="el-next-title">Want the full research brief?</div>
                <div class="el-next-copy">Open EquityLens for a structured view of the company's latest performance, business model, risk themes, and supporting filings.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="el-workflow-shell">
            <div class="el-workflow-kicker">The research workflow</div>
            <div class="el-workflow-title">From primary source to useful context.</div>
            <div class="el-workflow-grid">
                <div class="el-workflow-step">
                    <div class="el-workflow-num">01 · Source</div>
                    <div class="el-workflow-step-title">Primary disclosure</div>
                    <div class="el-workflow-copy">Original SEC filings and company disclosures stay connected to the research.</div>
                </div>
                <div class="el-workflow-step">
                    <div class="el-workflow-num">02 · Structure</div>
                    <div class="el-workflow-step-title">Organize the facts</div>
                    <div class="el-workflow-copy">Reported figures, business context, and risk disclosures are organized consistently.</div>
                </div>
                <div class="el-workflow-step">
                    <div class="el-workflow-num">03 · Understand</div>
                    <div class="el-workflow-step-title">Build useful context</div>
                    <div class="el-workflow-copy">Review trends, economics, risks, and what changed across reporting periods.</div>
                </div>
                <div class="el-workflow-step">
                    <div class="el-workflow-num">04 · Compare</div>
                    <div class="el-workflow-step-title">Put peers in context</div>
                    <div class="el-workflow-copy">Compare relevant companies without rankings, recommendations, or hidden scoring.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    section("Why EquityLens", "Research built to be understandable and verifiable")
    st.markdown(
        """
        <div class="el-feature-grid">
            <div class="el-feature-card">
                <div class="el-feature-num">01 · Understand</div>
                <div class="el-feature-title">Make finance easier to read</div>
                <div class="el-feature-copy">Plain-language explanations sit beside reported numbers so users can understand what a metric means before interpreting it.</div>
            </div>
            <div class="el-feature-card">
                <div class="el-feature-num">02 · Compare</div>
                <div class="el-feature-title">Put peers on the same page</div>
                <div class="el-feature-copy">Standardized growth, margins, LTM results, capital structure, business models, and risks make peer research easier to follow.</div>
            </div>
            <div class="el-feature-card">
                <div class="el-feature-num">03 · Verify</div>
                <div class="el-feature-title">Show the source</div>
                <div class="el-feature-copy">Material figures and filing-based research stay connected to original SEC sources so users can inspect the underlying disclosure themselves.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    section("Recently updated", "Latest SEC filings detected")
    recent_filing_rows = []
    for company_name, feed in sec_filings.items():
        ticker = company_data.get(company_name, {}).get("ticker", feed.get("ticker", ""))
        for filing in feed.get("filings", [])[:3]:
            filing_date = filing.get("filing_date", "")
            if filing_date:
                recent_filing_rows.append({
                    "Company": f"{ticker} · {company_name.split(' (')[0]}",
                    "Filed": filing_date,
                    "Form": filing.get("form", ""),
                    "Description": filing.get("description", "") or filing.get("primary_document", ""),
                    "SEC Filing": filing.get("url", "")
                })

    if recent_filing_rows:
        recent_filing_rows = sorted(
            recent_filing_rows,
            key=lambda row: row["Filed"],
            reverse=True
        )[:5]
        st.dataframe(
            pd.DataFrame(recent_filing_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open filing"
                )
            }
        )
        st.caption(
            "The filing monitor checks covered companies automatically. Newly detected filings may appear "
            "before EquityLens has standardized every financial or qualitative field from that filing."
        )
    else:
        st.caption("Recent SEC filing activity will appear here as the automated filing monitor populates.")

    section("Coverage", f"{home_industry} companies")

    featured_rows = home_company_df.head(6)
    featured_cols = st.columns(3)

    for idx, (_, featured_row) in enumerate(featured_rows.iterrows()):
        featured_ticker = str(featured_row.get("Ticker", ""))
        featured_name = str(featured_row.get("Company", ""))
        featured_sector = str(featured_row.get("Sector", ""))
        featured_country = str(featured_row.get("Country", ""))

        deep_match = next(
            (
                company_name
                for company_name, company in company_data.items()
                if str(company.get("ticker", "")).upper() == featured_ticker
            ),
            None
        )

        if deep_match:
            featured_q = company_quarterly.get(deep_match, {})
            featured_qm = quarterly_metrics(featured_q)
            featured_detail = (
                "Latest revenue growth: "
                + pct(featured_qm.get("yoy_growth"))
                + "<br>Latest filing period: "
                + str(featured_q.get("period_end", "N/A"))
            )
        else:
            featured_detail = (
                "SEC + market coverage"
                + "<br>"
                + featured_sector
                + (" · " + featured_country if featured_country else "")
            )

        with featured_cols[idx % 3]:
            st.markdown(
                f"""
                <div class="el-company-card">
                    <div class="el-company-card-ticker">{featured_ticker}</div>
                    <div class="el-company-card-name">{featured_name}</div>
                    <div class="el-company-card-meta">
                        {home_industry}<br>
                        {featured_detail}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    section("What makes it different", "Research that shows its work")
    st.info(
        "EquityLens separates company-reported figures from calculations and summaries, "
        "links material claims back to SEC filings, and keeps interpretation separate from the source data."
    )


with peer_tab:
    section("Peer Research", "Industry Comparison")

    selected_industry = st.selectbox(
        "Industry",
        industries,
        index=0
    )

    industry_companies = [
        name for name, data in company_data.items()
        if data.get("industry", "Unclassified") == selected_industry
    ]

    subgroup_options = ["All current peers"] + [
        name for name, members in SUBGROUPS.items()
        if any(member in industry_companies for member in members)
    ]

    selected_subgroup = st.selectbox(
        "Sub-group",
        subgroup_options,
        index=0
    )

    if selected_subgroup == "All current peers":
        available_companies = industry_companies
    else:
        available_companies = [
            company for company in SUBGROUPS[selected_subgroup]
            if company in industry_companies
        ]

    defaults = available_companies[:3]
    selected_companies = st.multiselect(
        "Select companies to compare",
        available_companies,
        default=defaults
    )

    if selected_subgroup != "All current peers":
        st.caption(
            f"Showing the {selected_subgroup} sub-group. "
            "More companies can be added without changing the comparison workflow."
        )

    if selected_companies:
        section("Balance Sheet", "Capital Structure Snapshot")

        capital_rows = []
        for company in selected_companies:
            capital = company_data[company].get("capital_structure", {})
            capital_rows.append({
                "Company": company,
                "Shares Outstanding": (
                    f"{capital.get('shares_outstanding'):,}"
                    if capital.get("shares_outstanding") is not None
                    else "N/A"
                ),
                "Debt": format_money(capital.get("total_debt")),
                "Cash + Investments": format_money(
                    capital.get("cash_and_investments")
                ),
                "Balance Sheet Date": capital.get(
                    "balance_sheet_as_of", "N/A"
                ),
                "Source": capital.get("source_filing", "")
            })

        st.dataframe(
            pd.DataFrame(capital_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Source": st.column_config.LinkColumn(
                    "Source",
                    display_text="Open filing"
                )
            }
        )

    if st.button("Run Peer Comparison", type="primary"):
        if len(selected_companies) < 2:
            st.warning("Select at least two companies to compare.")
        else:
            live_market = {}

            if public_market_data_enabled:
                symbols = [
                    company_data[company]["ticker"]
                    for company in selected_companies
                ]
                try:
                    live_market = get_live_market_data(symbols)
                except Exception as exc:
                    st.warning(
                        "Live market data is temporarily unavailable. "
                        "Filing-based research is still available."
                    )
                    st.caption(str(exc))

                section("Market", "Live Market Snapshot")
                price_cols = st.columns(len(selected_companies))
                for idx, company in enumerate(selected_companies):
                    ticker = company_data[company]["ticker"]
                    market = live_market.get(ticker, {})
                    close = market.get("close")
                    change = market.get("percent_change")

                    price = (
                        f"${float(close):,.2f}"
                        if close not in (None, "")
                        else "N/A"
                    )
                    delta = (
                        f"{float(change):.2f}%"
                        if change not in (None, "")
                        else None
                    )

                    price_cols[idx].metric(
                        ticker,
                        price,
                        delta=delta,
                        delta_color="normal"
                    )
            else:
                st.info(
                    "Public market-price data is disabled in this demo. "
                    "SEC filing analysis remains available."
                )

            section("Fundamentals", "Annual Financial Comparison")
            annual_rows = []
            for company in selected_companies:
                data = company_data[company]
                revenue = data.get("revenue")
                history = data.get("history", [])
                growth = None
                if len(history) >= 2:
                    growth = calc_growth(
                        history[-1].get("revenue"),
                        history[-2].get("revenue")
                    )

                annual_rows.append({
                    "Company": company,
                    "FY": data.get("fiscal_year"),
                    "Revenue": format_money(revenue),
                    "YoY Revenue Growth": pct(growth),
                    "Gross Margin": pct(
                        calc_margin(data.get("gross_profit"), revenue)
                    ),
                    "Operating Margin": pct(
                        calc_margin(data.get("operating_income"), revenue)
                    ),
                    "Net Margin": pct(
                        calc_margin(data.get("net_income"), revenue)
                    ),
                    "Cash": format_money(data.get("cash")),
                    "Assets": format_money(data.get("assets")),
                    "SEC Filing": data.get("filing_url", "")
                })

            st.dataframe(
                pd.DataFrame(annual_rows),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SEC Filing": st.column_config.LinkColumn(
                        "SEC Filing",
                        display_text="Open 10-K"
                    )
                }
            )

            section("Earnings", "Quarterly & LTM Analysis")
            quarter_rows = []
            ltm_rows = []

            for company in selected_companies:
                qdata = company_quarterly.get(company, {})
                latest = qdata.get("latest_quarter", {})
                ltm = qdata.get("ltm", {})
                qm = quarterly_metrics(qdata)

                quarter_rows.append({
                    "Company": company,
                    "Quarter": qdata.get("quarter_label", "N/A"),
                    "Revenue": format_money(qm["revenue"]),
                    "YoY Growth": pct(qm["yoy_growth"]),
                    "QoQ Growth": pct(qm["qoq_growth"]),
                    "Gross Margin": pct(qm["gross_margin"]),
                    "Operating Margin": pct(qm["operating_margin"]),
                    "Net Income": format_money(latest.get("net_income")),
                    "SEC Filing": qdata.get("source_filing", "")
                })

                ltm_revenue = ltm.get("revenue")
                ltm_rows.append({
                    "Company": company,
                    "LTM Revenue": format_money(ltm_revenue),
                    "LTM Gross Margin": pct(
                        calc_margin(ltm.get("gross_profit"), ltm_revenue)
                    ),
                    "LTM Operating Margin": pct(
                        calc_margin(ltm.get("operating_income"), ltm_revenue)
                    ),
                    "LTM Net Income": format_money(ltm.get("net_income")),
                    "LTM Net Margin": pct(
                        calc_margin(ltm.get("net_income"), ltm_revenue)
                    )
                })

            st.markdown("**Latest Quarter**")
            st.dataframe(
                pd.DataFrame(quarter_rows),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SEC Filing": st.column_config.LinkColumn(
                        "SEC Filing",
                        display_text="Open 10-Q"
                    )
                }
            )

            st.markdown("**Trailing Twelve Months**")
            st.dataframe(
                pd.DataFrame(ltm_rows),
                use_container_width=True,
                hide_index=True
            )

            section("Trend", "Three-Year Revenue")
            st.caption(
                "Use this view to compare the direction and pace of reported revenue growth. "
                "Fiscal years may end on different dates, so the chart is best read as a company-reported annual trend rather than a same-calendar-period comparison."
            )

            revenue_rows = []
            for company in selected_companies:
                for item in company_data[company].get("history", []):
                    revenue_rows.append({
                        "Company": company,
                        "Fiscal Year": str(item.get("fiscal_year")),
                        "Revenue": item.get("revenue")
                    })
            revenue_df = pd.DataFrame(revenue_rows)
            if not revenue_df.empty:
                st.line_chart(
                    revenue_df.pivot(
                        index="Fiscal Year",
                        columns="Company",
                        values="Revenue"
                    )
                )

                st.markdown("**Trend context**")
                trend_rows = []
                for company in selected_companies:
                    history = company_data[company].get("history", [])
                    if not history:
                        continue

                    first = history[0]
                    latest_hist = history[-1]
                    prior_hist = history[-2] if len(history) >= 2 else None

                    start_revenue = first.get("revenue")
                    latest_revenue = latest_hist.get("revenue")
                    latest_growth = (
                        calc_growth(latest_revenue, prior_hist.get("revenue"))
                        if prior_hist else None
                    )
                    total_change = calc_growth(latest_revenue, start_revenue)

                    periods = max(len(history) - 1, 0)
                    cagr = None
                    if (
                        periods > 0
                        and start_revenue not in (None, 0)
                        and latest_revenue is not None
                        and start_revenue > 0
                        and latest_revenue > 0
                    ):
                        cagr = (
                            (latest_revenue / start_revenue) ** (1 / periods) - 1
                        ) * 100

                    start_margin = calc_margin(
                        first.get("operating_income"),
                        start_revenue
                    )
                    latest_margin = calc_margin(
                        latest_hist.get("operating_income"),
                        latest_revenue
                    )
                    margin_change = (
                        latest_margin - start_margin
                        if latest_margin is not None and start_margin is not None
                        else None
                    )

                    trend_rows.append({
                        "Company": company,
                        "Latest FY": latest_hist.get("fiscal_year"),
                        "Latest Revenue": format_money(latest_revenue),
                        "Latest YoY Growth": pct(latest_growth),
                        "Multi-Year Revenue Change": pct(total_change),
                        "Annualized Growth": pct(cagr),
                        "Operating Margin Change": (
                            f"{margin_change:+.1f} pts"
                            if margin_change is not None else "N/A"
                        )
                    })

                st.dataframe(
                    pd.DataFrame(trend_rows),
                    use_container_width=True,
                    hide_index=True
                )

                st.markdown("**How to read this**")
                st.write(
                    "The chart shows absolute revenue over time, while the table separates growth rate from company size. "
                    "Latest YoY Growth measures the change from the prior reported fiscal year. "
                    "Multi-Year Revenue Change measures the total change from the first year shown to the latest year. "
                    "Annualized Growth converts that multi-year change into an average annual rate. "
                    "Operating Margin Change shows how many percentage points reported operating margin moved over the same period."
                )

            section("Qualitative Research", "Risk & Business Model")
            st.caption(
                "Choose any company in EquityLens to explore how it makes money, "
                "who it serves, what its platform depends on, and the risks disclosed in its filings."
            )

            risk_company = st.selectbox(
                "Choose a company to explore",
                list(company_data.keys()),
                index=(
                    list(company_data.keys()).index(selected_companies[0])
                    if selected_companies and selected_companies[0] in company_data
                    else 0
                ),
                format_func=lambda name: (
                    f"{company_data[name].get('ticker', '')} · {name.split(' (')[0]} "
                    f"— {company_data[name].get('industry', 'Unclassified')}"
                ),
                key="peer_risk_company"
            )

            risk_analysis = company_analysis.get(risk_company, {})
            risk_themes = risk_analysis.get("key_risk_themes", [])
            risk_source = risk_analysis.get(
                "source_filing",
                company_data.get(risk_company, {}).get("filing_url", "")
            )
            risk_name = risk_company.split(" (")[0]
            risk_ticker = company_data.get(risk_company, {}).get("ticker", "")
            risk_industry = company_data.get(risk_company, {}).get(
                "industry", "Unclassified"
            )

            st.markdown(
                f"""
                <div class="el-company-hero">
                    <div class="el-kicker">{risk_ticker} · {risk_industry}</div>
                    <div class="el-company-title">{risk_name}</div>
                    <p class="el-subtitle">{risk_analysis.get('business_model', 'Business model information is not available.')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            risk_left, risk_right = st.columns(2)

            with risk_left:
                st.markdown(
                    f"""
                    <div class="el-risk-card">
                        <div class="el-risk-title">How the company makes money</div>
                        <p class="el-change-copy">{risk_analysis.get('primary_revenue_source', 'N/A')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"""
                    <div class="el-risk-card">
                        <div class="el-risk-title">Who it serves</div>
                        <p class="el-change-copy">{risk_analysis.get('customer_type', 'N/A')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"""
                    <div class="el-risk-card">
                        <div class="el-risk-title">Platform dependency</div>
                        <p class="el-change-copy">{risk_analysis.get('platform_dependency', 'N/A')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with risk_right:
                st.markdown(
                    f"""
                    <div class="el-risk-card">
                        <div class="el-risk-title">Competitive risk</div>
                        <p class="el-change-copy">{risk_analysis.get('competitive_risk', 'N/A')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"""
                    <div class="el-risk-card">
                        <div class="el-risk-title">Operational risk</div>
                        <p class="el-change-copy">{risk_analysis.get('operational_risk', 'N/A')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"""
                    <div class="el-risk-card">
                        <div class="el-risk-title">Profitability history</div>
                        <p class="el-change-copy">{risk_analysis.get('profitability_history', 'N/A')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            if risk_themes:
                st.markdown("**Key risk themes disclosed or summarized from company filings**")
                theme_cols = st.columns(min(3, len(risk_themes)))
                for idx, theme in enumerate(risk_themes):
                    with theme_cols[idx % len(theme_cols)]:
                        st.markdown(
                            f"""
                            <div class="el-risk-card">
                                <div class="el-risk-title">{theme}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            extra_left, extra_right = st.columns(2)
            with extra_left:
                st.markdown("**Customer concentration**")
                st.write(risk_analysis.get("customer_concentration", "N/A"))
            with extra_right:
                st.markdown("**International exposure**")
                st.write(risk_analysis.get("international_exposure", "N/A"))

            if risk_source:
                st.caption("Source: company SEC filing")
                st.link_button(
                    "Open source filing",
                    risk_source,
                    key=f"risk_source_selected_{risk_ticker}"
                )

            st.caption(
                "This section summarizes publicly disclosed company information for educational research. "
                "It does not rate the company or recommend buying, selling, or holding its securities."
            )

with company_tab:
    section("Explore Companies", "Research the Company Through SEC Filings")

    st.caption(
        "Explore all companies in the EquityLens coverage universe. The app resolves current "
        "SEC filing history on demand and searches historical registration filings for S-1, "
        "F-1, S-11, and related amendments when they are available."
    )

    explore_filters = st.columns(3)

    with explore_filters[0]:
        explore_sector = st.selectbox(
            "Sector",
            ["All sectors"] + coverage_sectors,
            key="explore_sector"
        )

    if explore_sector == "All sectors":
        explore_sector_df = company_universe.copy()
    else:
        explore_sector_df = company_universe[
            company_universe["Sector"] == explore_sector
        ].copy()

    explore_industries = sorted(
        [
            value
            for value in explore_sector_df["Industry"].dropna().unique().tolist()
            if value
        ]
    )

    # "All sectors" is a true global-search mode. Do not let a stale
    # industry selection silently hide companies from the Company picker.
    if explore_sector == "All sectors":
        explore_industry = "All industries"
        with explore_filters[1]:
            st.selectbox(
                "Industry",
                ["All industries"],
                index=0,
                disabled=True,
                key="explore_all_sectors_industry"
            )
        explore_df = company_universe.copy()
    else:
        with explore_filters[1]:
            explore_industry = st.selectbox(
                "Industry",
                ["All industries"] + explore_industries,
                key="explore_s1_industry"
            )

        explore_df = explore_sector_df.copy()
        if explore_industry != "All industries":
            explore_df = explore_df[
                explore_df["Industry"] == explore_industry
            ]

    with explore_filters[2]:
        explore_search = st.text_input(
            "Search company or ticker",
            placeholder=(
                "e.g. MongoDB, MDB, Amazon, AAPL"
                if explore_sector == "All sectors"
                else "Search within this sector"
            ),
            key="explore_company_search"
        )

    # Resolve the search directly to a company so there is only one search control.
    # Ranking: exact ticker -> exact company -> starts-with -> contains.
    explore_options_df = explore_df.copy()
    search_text = explore_search.strip()

    if search_text:
        search_lower = search_text.lower()
        ticker_lower = explore_options_df["Ticker"].str.lower()
        company_lower = explore_options_df["Company"].str.lower()

        exact_ticker = explore_options_df[ticker_lower == search_lower]
        exact_company = explore_options_df[company_lower == search_lower]
        starts_with = explore_options_df[
            company_lower.str.startswith(search_lower, na=False)
            | ticker_lower.str.startswith(search_lower, na=False)
        ]
        contains = explore_options_df[
            company_lower.str.contains(search_lower, regex=False, na=False)
            | ticker_lower.str.contains(search_lower, regex=False, na=False)
        ]

        if not exact_ticker.empty:
            explore_matches = exact_ticker
        elif not exact_company.empty:
            explore_matches = exact_company
        elif not starts_with.empty:
            explore_matches = starts_with
        else:
            explore_matches = contains

        if explore_matches.empty:
            st.warning(
                f'No company or ticker matched "{search_text}" in the current filters.'
            )
            explore_row = explore_options_df.iloc[0]
        else:
            explore_row = explore_matches.iloc[0]
            if len(explore_matches) > 1:
                st.caption(
                    f"{len(explore_matches)} matches found. Showing "
                    f"{explore_row['Company']} ({explore_row['Ticker']}). "
                    "Keep typing to narrow the result."
                )
    else:
        explore_row = explore_options_df.iloc[0]

    explore_ticker = str(explore_row.get("Ticker", ""))
    explore_name = str(explore_row.get("Company", ""))
    explore_industry_name = str(explore_row.get("Industry", ""))
    explore_country = str(explore_row.get("Country", ""))

    deep_explore_company = next(
        (
            company_name
            for company_name, company in company_data.items()
            if str(company.get("ticker", "")).upper() == explore_ticker
        ),
        None
    )
    deep_explore_s1 = (
        company_s1.get(deep_explore_company, {})
        if deep_explore_company
        else {}
    )

    try:
        explore_sec = get_sec_company_research(explore_ticker)
        explore_sec_error = None
    except Exception:
        explore_sec = {}
        explore_sec_error = (
            "SEC EDGAR is temporarily unavailable for this company. "
            "Try again shortly."
        )

    explore_filings = explore_sec.get("filings", [])
    explore_registrations = explore_sec.get("registration_filings", [])

    latest_annual = latest_filing_by_forms(
        explore_filings,
        {"10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"}
    )
    latest_quarter = latest_filing_by_forms(
        explore_filings,
        {"10-Q", "10-Q/A"}
    )
    latest_current = latest_filing_by_forms(
        explore_filings,
        {"8-K", "8-K/A", "6-K", "6-K/A"}
    )
    primary_registration = (
        explore_registrations[0]
        if explore_registrations
        else {}
    )

    registration_label = (
        primary_registration.get("form", "")
        if primary_registration
        else "No registration filing found"
    )

    st.markdown(
        f"""
        <div class="el-company-hero">
            <div class="el-kicker">{explore_ticker} · {explore_industry_name}</div>
            <div class="el-company-title">{explore_name}</div>
            <p class="el-subtitle">
                Primary-source research from SEC EDGAR, including current public-company
                filings and IPO-era registration materials when available.
            </p>
            <div class="el-badges">
                <span class="el-badge">{explore_sector}</span>
                <span class="el-badge">{explore_country}</span>
                <span class="el-badge">{registration_label}</span>
                <span class="el-badge">SEC EDGAR</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if explore_sec_error:
        st.warning(explore_sec_error)
    else:
        source_metrics = st.columns(4)
        source_metrics[0].metric(
            "Annual filing",
            latest_annual.get("form", "N/A"),
            latest_annual.get("filing_date") or None
        )
        source_metrics[1].metric(
            "Quarterly filing",
            latest_quarter.get("form", "N/A"),
            latest_quarter.get("filing_date") or None
        )
        source_metrics[2].metric(
            "Current report",
            latest_current.get("form", "N/A"),
            latest_current.get("filing_date") or None
        )
        source_metrics[3].metric(
            "Registration",
            primary_registration.get("form", "Not found"),
            primary_registration.get("filing_date") or None
        )

        section("Registration", "IPO / Registration Filing History")

        if explore_registrations:
            registration_table = pd.DataFrame(
                [
                    {
                        "Filed": filing.get("filing_date", ""),
                        "Form": filing.get("form", ""),
                        "Description": (
                            filing.get("description", "")
                            or filing.get("primary_document", "")
                        ),
                        "SEC Filing": filing.get("url", "")
                    }
                    for filing in explore_registrations
                ]
            )

            st.dataframe(
                registration_table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SEC Filing": st.column_config.LinkColumn(
                        "SEC Filing",
                        display_text="Open filing"
                    )
                }
            )

            if primary_registration.get("url"):
                st.link_button(
                    "Open primary registration filing on SEC EDGAR",
                    primary_registration.get("url"),
                    key="explore_primary_registration"
                )
        else:
            st.info(
                "No S-1, S-1/A, F-1, F-1/A, S-11, or S-11/A was found in the "
                "issuer's available SEC submission history. That does not mean the company "
                "never registered securities: older issuers may predate modern EDGAR coverage, "
                "and some companies used a different registration path."
            )

        if deep_explore_s1:
            section("EquityLens Deep Research", "Structured IPO Filing Analysis")

            st.write(
                deep_explore_s1.get(
                    "historical_context",
                    "Historical IPO context is available for this company."
                )
            )

            st.markdown("**What to learn from the filing**")
            st.write(
                deep_explore_s1.get(
                    "what_to_learn",
                    "Review the original registration filing for business-model, risk, "
                    "ownership, and financial-history context."
                )
            )

            detail_cols = st.columns(2)
            detail_map = deep_explore_s1.get("filing_details", {})

            detail_sections = [
                (
                    "Business & Revenue Model",
                    "business_revenue_model",
                    "How the company described what it sells, who pays, and how revenue is generated."
                ),
                (
                    "Customers & Go-to-Market",
                    "customers_go_to_market",
                    "Customer mix, sales motion, distribution, retention, and expansion strategy."
                ),
                (
                    "Growth Strategy & Market Opportunity",
                    "growth_market_opportunity",
                    "Management's growth priorities, market opportunity, products, and expansion plans."
                ),
                (
                    "Competition & Differentiation",
                    "competition_differentiation",
                    "Competitors, alternatives, and the capabilities management said differentiated the business."
                ),
                (
                    "Risk Factors",
                    "risk_factors",
                    "Company-disclosed risks and operating dependencies."
                ),
                (
                    "Financial Condition & Operating History",
                    "financial_history",
                    "Historical revenue, profitability, cash flow, and capital needs around the IPO."
                ),
                (
                    "IPO Structure, Capitalization & Dilution",
                    "ipo_capitalization_dilution",
                    "Share structure, voting rights, capitalization, dilution, and offering mechanics."
                ),
                (
                    "Use of Proceeds, Management & Ownership",
                    "proceeds_management_ownership",
                    "Use of proceeds, governance, executives, principal stockholders, and ownership."
                )
            ]

            for idx, (label, field, explainer) in enumerate(detail_sections):
                with detail_cols[idx % 2]:
                    with st.expander(label, expanded=(idx < 2)):
                        st.write(explainer)
                        filing_points = detail_map.get(field, [])
                        for point in filing_points:
                            st.markdown(f"- {point}")

            if deep_explore_s1.get("source_url"):
                st.link_button(
                    "Open EquityLens source registration filing",
                    deep_explore_s1.get("source_url"),
                    key="explore_deep_s1_source"
                )
        else:
            section("Research Guide", "How to Read the Registration Filing")
            st.markdown(
                """
                Use the original registration filing to examine:

                - **Business model:** what the company sold and how it generated revenue.
                - **Customers and go-to-market:** who bought the product and how the company reached them.
                - **Growth strategy:** the opportunities management presented to prospective public investors.
                - **Competition:** alternatives, competitors, and stated differentiation.
                - **Risk factors:** material risks disclosed before or around the public listing.
                - **Financial history:** revenue, costs, profitability, cash flow, and capital requirements.
                - **Capitalization and dilution:** share classes, voting rights, preferred-stock conversion, and offering mechanics.
                - **Use of proceeds and ownership:** how proceeds were expected to be used and who controlled the company.
                """
            )

        section("Recent SEC Activity", "Current Company Filings")

        if explore_filings:
            recent_table = pd.DataFrame(
                [
                    {
                        "Filed": filing.get("filing_date", ""),
                        "Form": filing.get("form", ""),
                        "Report Period": filing.get("report_date", ""),
                        "Description": (
                            filing.get("description", "")
                            or filing.get("primary_document", "")
                        ),
                        "SEC Filing": filing.get("url", "")
                    }
                    for filing in explore_filings[:20]
                ]
            )

            st.dataframe(
                recent_table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SEC Filing": st.column_config.LinkColumn(
                        "SEC Filing",
                        display_text="Open filing"
                    )
                }
            )

        if explore_sec.get("sec_company_url"):
            st.link_button(
                "Open complete SEC company filing history",
                explore_sec.get("sec_company_url"),
                key="explore_complete_sec_history"
            )

        st.caption(
            "SEC filing metadata is resolved on demand and cached briefly for performance. "
            "Registration filings are searched through both the current SEC submission feed "
            "and the issuer's historical submission files."
        )


with research_tab:
    section("EquityLens", "Company Research Brief")

    st.write(
        "A structured company view for users who want the important context in one place without using a chatbot. "
        "This page combines reported financials, calculated metrics, business-model context, disclosed risk themes, "
        "and direct SEC source links."
    )

    research_industry = st.selectbox(
        "Industry",
        industries,
        key="equitylens_research_industry"
    )

    research_companies = [
        name for name, company in company_data.items()
        if company.get("industry", "Unclassified") == research_industry
    ]

    research_company = st.selectbox(
        "Company",
        research_companies,
        format_func=lambda name: (
            f"{company_data[name].get('ticker', '')} · {name.split(' (')[0]}"
        ),
        key="equitylens_research_company"
    )

    research_data = company_data.get(research_company, {})
    research_analysis = company_analysis.get(research_company, {})
    research_qdata = company_quarterly.get(research_company, {})
    research_qm = quarterly_metrics(research_qdata)
    research_latest = research_qdata.get("latest_quarter", {})
    research_ticker = research_data.get("ticker", "")
    research_name = research_company.split(" (")[0]

    st.markdown(
        f"""
        <div class="el-company-hero">
            <div class="el-kicker">{research_ticker} · {research_data.get('industry', 'Unclassified')}</div>
            <div class="el-company-title">{research_name}</div>
            <p class="el-subtitle">{research_analysis.get('business_model', 'Company research is being prepared.')}</p>
            <div class="el-badges">
                <span class="el-badge">{research_qdata.get('quarter_label', f"FY{research_data.get('fiscal_year', '')}")}</span>
                <span class="el-badge">SEC filing sourced</span>
                <span class="el-badge">No chatbot</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    research_metrics = st.columns(4)

    if research_latest.get("revenue") is not None:
        research_revenue = research_latest.get("revenue")
        research_growth = research_qm.get("yoy_growth")
        research_margin = research_qm.get("operating_margin")
        research_period = research_qdata.get("quarter_label", "Latest quarter")
    else:
        research_history = research_data.get("history", [])
        prior_revenue = (
            research_history[-2].get("revenue")
            if len(research_history) >= 2 else None
        )
        research_revenue = research_data.get("revenue")
        research_growth = calc_growth(research_data.get("revenue"), prior_revenue)
        research_margin = calc_margin(
            research_data.get("operating_income"),
            research_data.get("revenue")
        )
        research_period = f"FY{research_data.get('fiscal_year', '')}"

    research_metrics[0].metric("Revenue", format_money(research_revenue))
    research_metrics[1].metric("YoY Growth", pct(research_growth))
    research_metrics[2].metric("Operating Margin", pct(research_margin))
    research_metrics[3].metric(
        "Cash + Investments",
        format_money(
            research_data.get("capital_structure", {}).get("cash_and_investments")
        )
    )

    section("Research Summary", "What to Understand First")

    change_notes = build_change_notes(research_qdata)
    if not change_notes:
        annual_history = research_data.get("history", [])
        if len(annual_history) >= 2:
            latest_year = annual_history[-1]
            prior_year = annual_history[-2]
            annual_growth = calc_growth(
                latest_year.get("revenue"),
                prior_year.get("revenue")
            )
            if annual_growth is not None:
                change_notes = [(
                    "Annual revenue",
                    f"Revenue changed {annual_growth:+.1f}% from FY{prior_year.get('fiscal_year')} "
                    f"to FY{latest_year.get('fiscal_year')}."
                )]

    risk_themes = research_analysis.get("key_risk_themes", [])
    risk_chips = "".join(
        f'<span class="el-risk-chip">{risk}</span>'
        for risk in risk_themes[:8]
    )

    change_copy = (
        " ".join(note[1] for note in change_notes[:3])
        if change_notes
        else "Recent period-over-period changes are not yet fully standardized for this company."
    )

    st.markdown(
        f"""
        <div class="el-research-grid">
            <div class="el-research-panel">
                <div class="el-research-panel-kicker">Business model</div>
                <div class="el-research-panel-title">How the company makes money</div>
                <div class="el-research-panel-copy">
                    {research_analysis.get('business_model', 'Business-model context is being prepared.')}
                    <br><br>
                    <strong style="color:#EEF3F5;">Primary revenue source:</strong>
                    {research_analysis.get('primary_revenue_source', 'Not yet standardized.')}
                </div>
            </div>
            <div class="el-research-panel">
                <div class="el-research-panel-kicker">Customers</div>
                <div class="el-research-panel-title">Who the business serves</div>
                <div class="el-research-panel-copy">
                    {research_analysis.get('customer_type', 'Customer context is being prepared.')}
                </div>
            </div>
            <div class="el-research-panel">
                <div class="el-research-panel-kicker">Recent performance</div>
                <div class="el-research-panel-title">What changed in {research_period}</div>
                <div class="el-research-panel-copy">{change_copy}</div>
            </div>
            <div class="el-research-panel">
                <div class="el-research-panel-kicker">Operating context</div>
                <div class="el-research-panel-title">What the business depends on</div>
                <div class="el-research-panel-copy">
                    {research_analysis.get('platform_dependency', 'Platform and operating dependencies are being prepared.')}
                </div>
            </div>
            <div class="el-research-panel wide">
                <div class="el-research-panel-kicker">Disclosed risk themes</div>
                <div class="el-research-panel-title">What can materially affect the business</div>
                <div class="el-research-panel-copy">
                    {research_analysis.get('competitive_risk', '')}
                    {(' ' + research_analysis.get('operational_risk', '')) if research_analysis.get('operational_risk') else ''}
                </div>
                <div class="el-risk-chip-row">{risk_chips}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    section("Context", "Profitability, Concentration & Exposure")
    context_cols = st.columns(3)
    with context_cols[0]:
        st.markdown("**Profitability history**")
        st.write(
            research_analysis.get(
                "profitability_history",
                "Profitability history is being prepared."
            )
        )
    with context_cols[1]:
        st.markdown("**Customer concentration**")
        st.write(
            research_analysis.get(
                "customer_concentration",
                "Customer-concentration context is being prepared."
            )
        )
    with context_cols[2]:
        st.markdown("**International exposure**")
        st.write(
            research_analysis.get(
                "international_exposure",
                "International exposure context is being prepared."
            )
        )

    section("Sources", "Verify the Research")
    source_rows = []

    annual_source = research_data.get("filing_url")
    if annual_source:
        source_rows.append({
            "Source": research_data.get("source", "Annual filing"),
            "Period": research_data.get("fiscal_year_end", "N/A"),
            "SEC Filing": annual_source
        })

    quarterly_source = research_qdata.get("source_filing")
    if quarterly_source and quarterly_source != annual_source:
        source_rows.append({
            "Source": research_qdata.get("quarter_label", "Latest quarterly filing"),
            "Period": research_qdata.get("period_end", "N/A"),
            "SEC Filing": quarterly_source
        })

    analysis_source = research_analysis.get("source_filing")
    if analysis_source and analysis_source not in [row["SEC Filing"] for row in source_rows]:
        source_rows.append({
            "Source": "Business & risk source",
            "Period": "See filing",
            "SEC Filing": analysis_source
        })

    if source_rows:
        st.dataframe(
            pd.DataFrame(source_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open filing"
                )
            }
        )

    st.caption(
        "EquityLens separates reported figures from calculated metrics and research summaries, "
        "with direct links back to the underlying SEC sources."
    )


with market_tab:
    section("Market", "Market Monitor")

    st.markdown(
        """
        <div class="el-market-hero">
            <div class="el-market-hero-label">Covered-company market context</div>
            <div class="el-market-hero-title">See what is moving, then inspect the company behind it.</div>
            <div class="el-market-hero-copy">
                Monitor price changes and volume for EquityLens-covered companies, then place that movement
                beside company fundamentals and recent SEC filings. Market movement and filing activity are
                displayed together without assuming one caused the other.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    refresh_col, source_col = st.columns([1, 3])
    with refresh_col:
        if st.button(
            "Refresh market data",
            key="refresh_market_monitor",
            type="primary",
            use_container_width=True
        ):
            get_live_market_data.clear()
            get_market_history.clear()
            get_finviz_screener_data.clear()
            get_treasury_yield_curve.clear()
            get_sofr_reference_rates.clear()
            get_bls_macro_snapshot.clear()
            get_bls_release_calendar.clear()
            get_fomc_calendar.clear()
            get_fed_monetary_updates.clear()
            get_bloomberg_market_news.clear()
            get_optional_swap_rates.clear()
            st.rerun()

    with source_col:
        st.caption(
            "NYSE ticker + heat map: Finviz Elite · quotes + charts: Yahoo Finance via yfinance"
        )

    nyse_finviz = pd.DataFrame()
    if public_finviz_data_enabled:
        try:
            nyse_finviz = normalize_finviz_screener(
                get_finviz_screener_data(filters="exch_nyse")
            )
        except Exception as exc:
            st.warning(market_provider_error("NYSE Finviz data", exc))
    else:
        st.warning(
            "Finviz is not configured. Add FINVIZ_API_KEY to Streamlit Secrets "
            "to display the NYSE ticker and heat map."
        )

    render_nyse_market_monitor(nyse_finviz)

    section("Rates", "Treasury, SOFR & Swap Monitor")

    treasury_curve = {}
    sofr_reference = {}
    try:
        treasury_curve = get_treasury_yield_curve()
    except Exception:
        st.warning(
            "U.S. Treasury yield-curve data is temporarily unavailable."
        )

    try:
        sofr_reference = get_sofr_reference_rates()
    except Exception:
        st.warning(
            "New York Fed SOFR reference-rate data is temporarily unavailable."
        )

    render_rates_ticker(treasury_curve, sofr_reference)

    treasury_rates = treasury_curve.get("rates", {}) if treasury_curve else {}
    curve_rows = [
        {"Tenor": tenor, "Yield (%)": rate}
        for tenor, rate in treasury_rates.items()
        if rate is not None
    ]
    if curve_rows:
        curve_df = pd.DataFrame(curve_rows)
        curve_fig = go.Figure()
        curve_fig.add_trace(
            go.Scatter(
                x=curve_df["Tenor"],
                y=curve_df["Yield (%)"],
                mode="lines+markers",
                name="Treasury",
                line={"color": "#16C7B2", "width": 2},
                marker={"size": 7},
            )
        )
        curve_fig.update_layout(
            height=330,
            margin={"l": 8, "r": 8, "t": 24, "b": 8},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#8F9CA6", "family": "IBM Plex Sans"},
            showlegend=False,
            xaxis={"showgrid": False, "title": "Maturity"},
            yaxis={
                "gridcolor": "rgba(143,156,166,.12)",
                "title": "Yield (%)",
                "ticksuffix": "%",
            },
        )
        st.plotly_chart(
            curve_fig,
            use_container_width=True,
            config={"displayModeBar": False},
        )
        st.caption(
            "Daily Treasury par yield curve · U.S. Department of the Treasury"
            + (
                f" · as of {treasury_curve.get('date')}"
                if treasury_curve.get("date") else ""
            )
        )

    swap_rates = []
    try:
        swap_rates = get_optional_swap_rates()
    except Exception:
        swap_rates = []

    if swap_rates:
        swap_df = pd.DataFrame(swap_rates)
        swap_df["Swap Rate"] = swap_df["Swap Rate"].map(
            lambda value: f"{value:.3f}%"
        )
        st.markdown("**USD SOFR OIS Curve**")
        visible_swap_columns = [
            column for column in [
                "Tenor", "Swap Rate", "Curve Date", "Source", "Method"
            ]
            if column in swap_df.columns
        ]
        st.dataframe(
            swap_df[visible_swap_columns],
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "Free public curve data: CheckMySwap, derived from DTCC public swap "
            "transaction reports. These are dated indicative OIS curve estimates, "
            "not live executable dealer quotes."
        )
        st.link_button(
            "Open CheckMySwap methodology & curve archive",
            "https://checkmyswap.com/rates?ccy=USD",
            use_container_width=True,
        )
    else:
        st.info(
            "USD SOFR OIS curve data is temporarily unavailable. EquityLens will "
            "continue to show official Treasury and New York Fed reference rates."
        )

    section("Macro", "Material U.S. Economic Reports")

    try:
        bls_snapshot = get_bls_macro_snapshot()
    except Exception:
        bls_snapshot = {}
        st.warning(
            "BLS macro data is temporarily unavailable. The section will update "
            "automatically when the BLS public API is reachable."
        )

    macro_order = [
        "CPI",
        "Core CPI",
        "PPI",
        "Unemployment",
        "Payrolls",
        "Hourly Earnings",
        "ECI",
    ]
    available_macro = [
        key for key in macro_order if key in bls_snapshot
    ]

    for row_start in range(0, len(available_macro), 4):
        row_keys = available_macro[row_start:row_start + 4]
        cols = st.columns(len(row_keys))
        for col, key in zip(cols, row_keys):
            item = bls_snapshot[key]
            col.metric(
                item.get("label", key),
                format_bls_display(item),
            )
            col.caption(
                f"{item.get('period', '')} · BLS"
            )

    if available_macro:
        macro_source_rows = [
            {
                "Indicator": bls_snapshot[key].get("label", key),
                "BLS Series": bls_snapshot[key].get("series_id", ""),
                "Latest period": bls_snapshot[key].get("period", ""),
                "Primary report": bls_snapshot[key].get("source", ""),
            }
            for key in available_macro
        ]
        with st.expander("BLS source details"):
            st.dataframe(
                pd.DataFrame(macro_source_rows),
                use_container_width=True,
                hide_index=True,
            )
            st.link_button(
                "Open BLS Public Data API documentation",
                "https://www.bls.gov/developers/",
                use_container_width=True,
            )

    section("Calendar", "Economic & Federal Reserve Calendar")

    bls_calendar = []
    fomc_calendar = []
    try:
        bls_calendar = get_bls_release_calendar()
    except Exception:
        st.caption(
            "The BLS release calendar is temporarily unavailable."
        )
    try:
        fomc_calendar = get_fomc_calendar()
    except Exception:
        st.caption(
            "The Federal Reserve meeting calendar is temporarily unavailable."
        )

    calendar_rows = bls_calendar + fomc_calendar
    if calendar_rows:
        calendar_df = pd.DataFrame(calendar_rows)
        calendar_df = calendar_df.sort_values(
            ["Date", "Agency"],
            ascending=True,
        ).head(16)
        st.dataframe(
            calendar_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Source": st.column_config.LinkColumn(
                    "Primary source",
                    display_text="Open"
                )
            },
        )
        st.caption(
            "BLS dates come from its automatically updated online calendar. "
            "FOMC dates are read from the Federal Reserve's official meeting calendar."
        )

    st.markdown("**Latest Federal Reserve monetary-policy updates**")
    try:
        fed_updates = get_fed_monetary_updates()
    except Exception:
        fed_updates = []

    if fed_updates:
        st.dataframe(
            pd.DataFrame(fed_updates),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Source": st.column_config.LinkColumn(
                    "Federal Reserve",
                    display_text="Open"
                )
            },
        )
    else:
        st.link_button(
            "Open Federal Reserve monetary-policy updates",
            "https://www.federalreserve.gov/monetarypolicy.htm",
            use_container_width=True,
        )

    section("News", "Bloomberg Market News")

    try:
        bloomberg_news = get_bloomberg_market_news()
    except Exception:
        bloomberg_news = []

    news_quotes = {}
    try:
        news_quotes = get_live_market_data(
            ["SPY", "QQQ", "GLD", "USO", "UUP"]
        )
    except Exception:
        news_quotes = {}

    news_market_context = {
        "SPY": safe_float(news_quotes.get("SPY", {}).get("percent_change")),
        "QQQ": safe_float(news_quotes.get("QQQ", {}).get("percent_change")),
        "GLD": safe_float(news_quotes.get("GLD", {}).get("percent_change")),
        "USO": safe_float(news_quotes.get("USO", {}).get("percent_change")),
        "UUP": safe_float(news_quotes.get("UUP", {}).get("percent_change")),
        "treasury": (
            treasury_curve.get("rates", {})
            if treasury_curve else {}
        ),
        "SOFR": safe_float(
            sofr_reference.get("SOFR")
            if sofr_reference else None
        ),
        "CPI": safe_float(
            bls_snapshot.get("CPI", {}).get("display_value")
            if bls_snapshot else None
        ),
        "Core CPI": safe_float(
            bls_snapshot.get("Core CPI", {}).get("display_value")
            if bls_snapshot else None
        ),
        "PPI": safe_float(
            bls_snapshot.get("PPI", {}).get("display_value")
            if bls_snapshot else None
        ),
        "Unemployment": safe_float(
            bls_snapshot.get("Unemployment", {}).get("display_value")
            if bls_snapshot else None
        ),
    }

    if bloomberg_news:
        render_market_news_cards(
            bloomberg_news,
            market_context=news_market_context,
        )
        st.caption(
            "Bloomberg supplies the linked headlines. The charts and market-context panels shown on each card "
            "are original EquityLens visuals built from market, Treasury, New York Fed, and BLS data; they are "
            "not images copied from Bloomberg articles. Selecting a story opens the original article."
        )
    else:
        st.markdown(
            """
            <div class="el-news-shell">
                <div class="el-news-topline">
                    <span class="el-news-live">Market news</span>
                    <span>Bloomberg feed temporarily unavailable</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.link_button(
            "Open Bloomberg Markets",
            "https://www.bloomberg.com/markets",
            use_container_width=True,
        )

    section("Expanded Coverage", "EquityLens Company Universe")

    coverage_filter_cols = st.columns(3)
    with coverage_filter_cols[0]:
        coverage_sector = st.selectbox(
            "Sector",
            coverage_sectors,
            key="coverage_sector"
        )

    sector_universe = company_universe[
        company_universe["Sector"] == coverage_sector
    ].copy()

    sector_industries = sorted(
        [
            value for value in sector_universe["Industry"].dropna().unique().tolist()
            if value
        ]
    )

    with coverage_filter_cols[1]:
        coverage_industry = st.selectbox(
            "Industry",
            ["All industries"] + sector_industries,
            key="coverage_industry"
        )

    filtered_universe = sector_universe.copy()
    if coverage_industry != "All industries":
        filtered_universe = filtered_universe[
            filtered_universe["Industry"] == coverage_industry
        ]

    coverage_keys = filtered_universe["Coverage Key"].tolist()

    with coverage_filter_cols[2]:
        selected_coverage_company = st.selectbox(
            "Company",
            coverage_keys,
            key="coverage_company"
        )

    st.caption(
        f"{len(filtered_universe):,} companies shown · "
        f"{len(company_universe):,} total companies · "
        f"{len(coverage_sectors):,} sectors in the expanded EquityLens universe."
    )

    coverage_columns = [
        column for column in [
            "Ticker", "Company", "Industry", "Country",
            "Market Cap", "P/E", "Price", "Change", "Volume"
        ]
        if column in filtered_universe.columns
    ]
    st.dataframe(
        filtered_universe[coverage_columns],
        use_container_width=True,
        hide_index=True
    )

    selected_coverage_row = filtered_universe[
        filtered_universe["Coverage Key"] == selected_coverage_company
    ].iloc[0]
    selected_coverage_ticker = selected_coverage_row["Ticker"]

    section("SEC", f"{selected_coverage_ticker} Filing Access")

    selected_sec_feed = sec_filings.get(selected_coverage_company, {})
    selected_recent_filings = selected_sec_feed.get("filings", [])
    selected_registration_filings = selected_sec_feed.get(
        "registration_filings", []
    )

    sec_summary_cols = st.columns(3)
    sec_summary_cols[0].metric(
        "Recent filings loaded",
        len(selected_recent_filings)
    )
    sec_summary_cols[1].metric(
        "Registration filings found",
        len(selected_registration_filings)
    )
    sec_summary_cols[2].metric(
        "SEC CIK",
        selected_sec_feed.get("cik") or "Pending"
    )

    if selected_recent_filings:
        recent_rows = []
        for filing in selected_recent_filings[:10]:
            recent_rows.append({
                "Filed": filing.get("filing_date", ""),
                "Form": filing.get("form", ""),
                "Description": (
                    filing.get("description", "")
                    or filing.get("primary_document", "")
                ),
                "SEC Filing": filing.get("url", "")
            })

        st.dataframe(
            pd.DataFrame(recent_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open filing"
                )
            }
        )
    else:
        st.caption(
            "The SEC monitor has not populated recent filings for this company yet."
        )

    st.markdown("**IPO / registration filings**")
    if selected_registration_filings:
        registration_rows = []
        for filing in selected_registration_filings:
            registration_rows.append({
                "Filed": filing.get("filing_date", ""),
                "Form": filing.get("form", ""),
                "Description": (
                    filing.get("description", "")
                    or filing.get("primary_document", "")
                ),
                "SEC Filing": filing.get("url", "")
            })

        st.dataframe(
            pd.DataFrame(registration_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open filing"
                )
            }
        )
    else:
        st.caption(
            "No S-1, S-1/A, F-1, F-1/A, S-11, or S-11/A has been found "
            "in the scanned SEC submission history for this company yet."
        )

    sec_company_url = selected_sec_feed.get("sec_company_url", "")
    if sec_company_url:
        st.link_button(
            "Open complete SEC company filing history",
            sec_company_url,
            use_container_width=True
        )

    section("Deep Research", "Structured EquityLens Coverage")

    market_industry = st.selectbox(
        "Industry",
        industries,
        key="market_monitor_industry"
    )

    movement_threshold = st.slider(
        "Notable movement threshold",
        min_value=1.0,
        max_value=10.0,
        value=3.0,
        step=0.5,
        key="market_movement_threshold"
    )

    market_companies = [
        name for name, data in company_data.items()
        if data.get("industry", "Unclassified") == market_industry
    ]

    industry_symbols = [
        company_data[company].get("ticker")
        for company in market_companies
        if company_data[company].get("ticker")
    ]

    industry_market = {}
    benchmark_market = {}
    finviz_market = pd.DataFrame()

    if public_market_data_enabled:
        try:
            industry_market = get_live_market_data(industry_symbols)
        except Exception as exc:
            st.warning(market_provider_error("Yahoo Finance", exc))

        try:
            benchmark_market = get_live_market_data(["SPY", "QQQ"])
        except Exception:
            benchmark_market = {}

    if public_finviz_data_enabled:
        try:
            finviz_market = normalize_finviz_screener(
                get_finviz_screener_data(industry_symbols)
            )
        except Exception as exc:
            st.warning(market_provider_error("Finviz screener data", exc))

    section("Pulse", "Market Snapshot")

    pulse_cols = st.columns(4)

    spy = benchmark_market.get("SPY", {})
    qqq = benchmark_market.get("QQQ", {})

    spy_change = safe_float(spy.get("percent_change"))
    qqq_change = safe_float(qqq.get("percent_change"))

    pulse_cols[0].metric(
        "S&P 500 proxy · SPY",
        format_market_price(spy.get("close")),
        f"{spy_change:+.2f}%" if spy_change is not None else None
    )
    pulse_cols[1].metric(
        "Nasdaq-100 proxy · QQQ",
        format_market_price(qqq.get("close")),
        f"{qqq_change:+.2f}%" if qqq_change is not None else None
    )

    industry_changes = [
        safe_float(industry_market.get(symbol, {}).get("percent_change"))
        for symbol in industry_symbols
    ]
    industry_changes = [value for value in industry_changes if value is not None]

    positive_count = sum(1 for value in industry_changes if value > 0)
    median_change = (
        float(pd.Series(industry_changes).median())
        if industry_changes else None
    )

    pulse_cols[2].metric(
        "Covered names positive",
        f"{positive_count} / {len(industry_changes)}" if industry_changes else "N/A"
    )
    pulse_cols[3].metric(
        "Industry median move",
        f"{median_change:+.2f}%" if median_change is not None else "N/A"
    )

    st.caption(
        "SPY and QQQ are shown as broad-market proxies. Quote and chart data are provided through Yahoo Finance; NYSE ticker and heat-map data come from Finviz Elite."
    )

    section("Coverage", f"{market_industry} Market Board")

    market_rows = []
    for company in market_companies:
        data = company_data[company]
        ticker = data.get("ticker", "")
        quote = industry_market.get(ticker, {})
        price = safe_float(quote.get("close"))
        change = safe_float(quote.get("percent_change"))
        volume = safe_float(quote.get("volume"))
        open_price = safe_float(quote.get("open"))
        previous_close = safe_float(quote.get("previous_close"))

        market_rows.append({
            "Ticker": ticker,
            "Company": company.split(" (")[0],
            "Price": "$" + f"{price:,.2f}" if price is not None else "N/A",
            "Today": f"{change:+.2f}%" if change is not None else "N/A",
            "Volume": format_market_volume(volume),
            "Open": "$" + f"{open_price:,.2f}" if open_price is not None else "N/A",
            "Previous Close": (
                "$" + f"{previous_close:,.2f}"
                if previous_close is not None else "N/A"
            ),
            "_change": change
        })

    board_df = pd.DataFrame(market_rows)
    if not board_df.empty:
        st.dataframe(
            board_df.drop(columns=["_change"]),
            use_container_width=True,
            hide_index=True
        )

    if public_finviz_data_enabled:
        section("Screener", "Finviz Market Intelligence")

        if not finviz_market.empty:
            covered_finviz = finviz_market[
                finviz_market["Ticker"].isin(industry_symbols)
            ].copy()

            finviz_controls = st.columns(2)
            with finviz_controls[0]:
                min_relative_volume = st.number_input(
                    "Minimum relative volume",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    key="finviz_min_relative_volume"
                )
            with finviz_controls[1]:
                min_abs_change = st.number_input(
                    "Minimum absolute daily move (%)",
                    min_value=0.0,
                    value=0.0,
                    step=0.5,
                    key="finviz_min_abs_change"
                )

            if "Relative Volume" in covered_finviz.columns and min_relative_volume > 0:
                rel_values = covered_finviz["Relative Volume"].apply(finviz_numeric)
                covered_finviz = covered_finviz[
                    rel_values.fillna(-1) >= min_relative_volume
                ]

            if "Change" in covered_finviz.columns and min_abs_change > 0:
                change_values = covered_finviz["Change"].apply(finviz_numeric)
                covered_finviz = covered_finviz[
                    change_values.abs().fillna(-1) >= min_abs_change
                ]

            preferred_columns = [
                "Ticker",
                "Company",
                "Price",
                "Change",
                "Volume",
                "Relative Volume",
                "Market Cap",
                "P/E",
                "Perf Week",
                "Perf Month",
                "Earnings"
            ]
            visible_columns = [
                column for column in preferred_columns
                if column in covered_finviz.columns
            ]

            if not covered_finviz.empty:
                st.dataframe(
                    covered_finviz[visible_columns],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.caption(
                    "No covered companies match the current Finviz screener filters."
                )

            st.caption(
                "Finviz supplies the screener snapshot. EquityLens keeps SEC-reported fundamentals "
                "and filing research separate from market-screening fields."
            )
        else:
            st.caption(
                "Finviz is enabled, but the current export did not return usable screener rows."
            )

    notable_rows = [
        row for row in market_rows
        if row["_change"] is not None
        and abs(row["_change"]) >= movement_threshold
    ]
    notable_rows = sorted(
        notable_rows,
        key=lambda row: abs(row["_change"]),
        reverse=True
    )[:6]

    section("Movement", f"Moves Beyond ±{movement_threshold:.1f}%")

    if notable_rows:
        movement_cards = []
        for row in notable_rows:
            company_key = next(
                (
                    company for company in market_companies
                    if company_data[company].get("ticker") == row["Ticker"]
                ),
                None
            )

            latest_filing = {}
            if company_key:
                filings = sec_filings.get(company_key, {}).get("filings", [])
                if filings:
                    latest_filing = filings[0]

            filing_label = "No recent filing loaded"
            if latest_filing:
                filing_label = (
                    f"{latest_filing.get('form', 'SEC filing')} · "
                    f"{latest_filing.get('filing_date', 'date unavailable')}"
                )

            direction_class = "positive" if row["_change"] >= 0 else "negative"

            movement_cards.append(
                f"""
                <div class="el-move-card">
                    <div class="el-move-top">
                        <div class="el-move-ticker">{row['Ticker']}</div>
                        <div class="el-move-change {direction_class}">{row['_change']:+.2f}%</div>
                    </div>
                    <div class="el-move-name">{row['Company']}</div>
                    <div class="el-move-filing">
                        Recent SEC context: {filing_label}<br>
                        Market movement shown without attributing a cause.
                    </div>
                </div>
                """
            )

        st.markdown(
            '<div class="el-move-grid">' + "".join(movement_cards) + "</div>",
            unsafe_allow_html=True
        )
    else:
        st.caption(
            f"No covered {market_industry} company currently exceeds the selected "
            f"±{movement_threshold:.1f}% movement threshold in the loaded snapshot."
        )

    section("Company View", "Market Context + Fundamentals")

    selected_market_company = st.selectbox(
        "Company",
        market_companies,
        format_func=lambda name: (
            f"{company_data[name].get('ticker', '')} · {name.split(' (')[0]}"
        ),
        key="market_monitor_company"
    )

    selected_data = company_data[selected_market_company]
    selected_qdata = company_quarterly.get(selected_market_company, {})
    selected_qm = quarterly_metrics(selected_qdata)
    selected_quote = industry_market.get(selected_data.get("ticker", ""), {})
    selected_analysis = company_analysis.get(selected_market_company, {})
    selected_ticker = selected_data.get("ticker", "")
    selected_name = selected_market_company.split(" (")[0]

    selected_price = safe_float(selected_quote.get("close"))
    selected_change = safe_float(selected_quote.get("percent_change"))
    selected_volume = safe_float(selected_quote.get("volume"))
    selected_52 = selected_quote.get("fifty_two_week", {})
    if not isinstance(selected_52, dict):
        selected_52 = {}

    selected_52_low = safe_float(selected_52.get("low"))
    selected_52_high = safe_float(selected_52.get("high"))

    market_detail_cols = st.columns(4)
    market_detail_cols[0].metric(
        f"{selected_ticker} Price",
        "$" + f"{selected_price:,.2f}" if selected_price is not None else "N/A",
        f"{selected_change:+.2f}%" if selected_change is not None else None
    )
    market_detail_cols[1].metric(
        "Volume",
        format_market_volume(selected_volume)
    )
    market_detail_cols[2].metric(
        "52-week low",
        "$" + f"{selected_52_low:,.2f}" if selected_52_low is not None else "N/A"
    )
    market_detail_cols[3].metric(
        "52-week high",
        "$" + f"{selected_52_high:,.2f}" if selected_52_high is not None else "N/A"
    )

    range_label = st.radio(
        "Chart range",
        ["1D", "5D", "1M", "6M", "1Y"],
        index=2,
        horizontal=True,
        key="market_chart_range"
    )

    range_config = {
        "1D": ("15min", 32),
        "5D": ("1h", 40),
        "1M": ("1day", 30),
        "6M": ("1day", 126),
        "1Y": ("1day", 252)
    }
    interval, outputsize = range_config[range_label]

    selected_history = pd.DataFrame()
    try:
        selected_history = get_market_history(
            selected_ticker,
            interval=interval,
            outputsize=outputsize
        )
    except Exception as exc:
        st.caption("Historical price series is temporarily unavailable for this range.")

    if not selected_history.empty:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=selected_history["datetime"],
                y=selected_history["close"],
                mode="lines",
                name=selected_ticker,
                line={"color": "#16C7B2", "width": 2}
            )
        )
        fig.update_layout(
            height=390,
            margin={"l": 8, "r": 8, "t": 22, "b": 8},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#8F9CA6", "family": "IBM Plex Sans"},
            hovermode="x unified",
            showlegend=False,
            xaxis={
                "showgrid": False,
                "zeroline": False,
                "title": None
            },
            yaxis={
                "gridcolor": "rgba(143,156,166,.12)",
                "zeroline": False,
                "title": None,
                "tickprefix": "$"
            }
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    five_day_return = None
    one_month_return = None
    try:
        daily_history = get_market_history(
            selected_ticker,
            interval="1day",
            outputsize=35
        )
        five_day_return = market_return(daily_history, 5)
        one_month_return = market_return(daily_history, 21)
    except Exception:
        daily_history = pd.DataFrame()

    period_cols = st.columns(2)
    period_cols[0].metric(
        "5-session change",
        f"{five_day_return:+.2f}%" if five_day_return is not None else "N/A"
    )
    period_cols[1].metric(
        "Approx. 1-month change",
        f"{one_month_return:+.2f}%" if one_month_return is not None else "N/A"
    )

    section("Fundamentals", "What Sits Behind the Price")

    selected_latest = selected_qdata.get("latest_quarter", {})
    if selected_latest.get("revenue") is not None:
        fundamental_revenue = selected_latest.get("revenue")
        fundamental_growth = selected_qm.get("yoy_growth")
        fundamental_margin = selected_qm.get("operating_margin")
        fundamental_period = selected_qdata.get("quarter_label", "Latest quarter")
    else:
        selected_history_fin = selected_data.get("history", [])
        selected_prior_revenue = (
            selected_history_fin[-2].get("revenue")
            if len(selected_history_fin) >= 2 else None
        )
        fundamental_revenue = selected_data.get("revenue")
        fundamental_growth = calc_growth(
            selected_data.get("revenue"),
            selected_prior_revenue
        )
        fundamental_margin = calc_margin(
            selected_data.get("operating_income"),
            selected_data.get("revenue")
        )
        fundamental_period = f"FY{selected_data.get('fiscal_year', '')}"

    fundamentals_cols = st.columns(4)
    fundamentals_cols[0].metric("Reported Revenue", format_money(fundamental_revenue))
    fundamentals_cols[1].metric("Revenue Growth", pct(fundamental_growth))
    fundamentals_cols[2].metric("Operating Margin", pct(fundamental_margin))
    fundamentals_cols[3].metric("Reporting Period", fundamental_period)

    st.markdown(
        f"""
        <div class="el-quick-read">
            <div class="el-quick-read-kicker">Company context</div>
            <div class="el-quick-read-title">{selected_name}</div>
            <div class="el-quick-read-copy">
                {selected_analysis.get('business_model', 'Business-model context is being prepared.')}
                Market data above reflects a different clock from company financial reporting, so the
                reporting period remains visible beside the fundamentals.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    section("Events", "Recent SEC Filing Context")

    filing_rows = []
    for filing in sec_filings.get(selected_market_company, {}).get("filings", [])[:6]:
        filing_rows.append({
            "Filed": filing.get("filing_date", ""),
            "Form": filing.get("form", ""),
            "Description": filing.get("description", "") or filing.get("primary_document", ""),
            "SEC Filing": filing.get("url", "")
        })

    if filing_rows:
        st.dataframe(
            pd.DataFrame(filing_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open filing"
                )
            }
        )
    else:
        st.caption("Recent SEC filing context is not available for this company yet.")

    st.markdown(
        '<div class="el-market-source">Quotes and charts: Yahoo Finance via yfinance · '
        'NYSE ticker, heat map, and screener: Finviz Elite · Company disclosures: SEC EDGAR · '
        'Prices, screener fields, historical charts, and filings may update on different schedules.</div>',
        unsafe_allow_html=True
    )


with sec_tracker_tab:
    section("SEC Monitor", "Filing Tracker")

    st.write(
        "This tracker combines the recent SEC filings collected for every company covered by EquityLens. "
        "It records the issuer, ticker, form, SEC filing date, SEC acceptance timestamp when available, "
        "the period the filing covers, when EquityLens first detected it, and a direct link to the original filing."
    )

    st.caption(
        "The SEC does not publish an exact future posting time before a filing is submitted. "
        "EquityLens can track actual filings immediately after they appear and can separately add announced "
        "earnings dates or estimated filing windows later."
    )

    tracker_rows = []
    for tracked_company, feed in sec_filings.items():
        entity_name = feed.get("entity_name", tracked_company.split(" (")[0])
        tracked_ticker = feed.get("ticker", "")
        for filing in feed.get("filings", []):
            tracker_rows.append({
                "Company": entity_name,
                "Ticker": tracked_ticker,
                "Form": filing.get("form", ""),
                "SEC Filed Date": filing.get("filing_date", ""),
                "SEC Accepted": filing.get("acceptance_datetime", ""),
                "Report Period": filing.get("report_date", ""),
                "Description": filing.get("description", "") or filing.get("primary_document", ""),
                "Items": filing.get("items", ""),
                "First Seen by EquityLens (UTC)": filing.get("first_seen_utc", ""),
                "Accession Number": filing.get("accession_number", ""),
                "SEC Filing": filing.get("url", "")
            })

    tracker_df = pd.DataFrame(tracker_rows)

    if tracker_df.empty:
        st.info("The filing tracker is waiting for the SEC monitor to populate data.")
    else:
        accepted_dt = pd.to_datetime(
            tracker_df["SEC Accepted"],
            errors="coerce",
            utc=True
        )
        first_seen_dt = pd.to_datetime(
            tracker_df["First Seen by EquityLens (UTC)"],
            errors="coerce",
            utc=True
        )

        tracker_df["SEC Accepted (ET)"] = (
            accepted_dt.dt.tz_convert("America/New_York")
            .dt.strftime("%Y-%m-%d %I:%M:%S %p %Z")
        )
        tracker_df["First Seen by EquityLens (ET)"] = (
            first_seen_dt.dt.tz_convert("America/New_York")
            .dt.strftime("%Y-%m-%d %I:%M:%S %p %Z")
        )

        tracker_df = tracker_df.drop(
            columns=["SEC Accepted", "First Seen by EquityLens (UTC)"]
        )

        tracker_df = tracker_df.sort_values(
            by=["SEC Filed Date", "SEC Accepted (ET)"],
            ascending=False,
            na_position="last"
        )

        filter_cols = st.columns(2)
        with filter_cols[0]:
            tracker_company = st.selectbox(
                "Company",
                ["All companies"] + sorted(tracker_df["Company"].dropna().unique().tolist()),
                key="sec_tracker_company"
            )
        with filter_cols[1]:
            form_options = sorted(
                [form for form in tracker_df["Form"].dropna().unique().tolist() if form]
            )
            tracker_forms = st.multiselect(
                "Filing type",
                form_options,
                default=[],
                key="sec_tracker_forms"
            )

        filtered_tracker = tracker_df.copy()
        if tracker_company != "All companies":
            filtered_tracker = filtered_tracker[
                filtered_tracker["Company"] == tracker_company
            ]
        if tracker_forms:
            filtered_tracker = filtered_tracker[
                filtered_tracker["Form"].isin(tracker_forms)
            ]

        st.dataframe(
            filtered_tracker,
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEC Filing": st.column_config.LinkColumn(
                    "SEC Filing",
                    display_text="Open filing"
                )
            }
        )

        st.download_button(
            "Download filing tracker as CSV",
            data=filtered_tracker.to_csv(index=False).encode("utf-8"),
            file_name="equitylens_sec_filing_tracker.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.caption(
            f"Showing {len(filtered_tracker):,} filing records from the current monitored set. "
            "The monitor checks for new SEC submissions every 15 minutes."
        )

    section("Registration Filings", "S-1 / F-1 / S-11 History")

    registration_company = st.selectbox(
        "Company registration history",
        company_universe["Coverage Key"].tolist(),
        format_func=lambda key: (
            key.split(" (")[-1].rstrip(")")
            + " · "
            + key.rsplit(" (", 1)[0]
        ),
        key="sec_registration_company"
    )

    registration_row = company_universe[
        company_universe["Coverage Key"] == registration_company
    ].iloc[0]
    registration_ticker = str(registration_row.get("Ticker", ""))

    try:
        registration_feed = get_sec_company_research(registration_ticker)
        registration_error = None
    except Exception:
        registration_feed = {}
        registration_error = "SEC EDGAR is temporarily unavailable for this company."

    if registration_error:
        st.warning(registration_error)
    else:
        registration_rows = registration_feed.get(
            "registration_filings",
            []
        )

        if registration_rows:
            registration_table = pd.DataFrame(
                [
                    {
                        "Filed": filing.get("filing_date", ""),
                        "Form": filing.get("form", ""),
                        "Description": (
                            filing.get("description", "")
                            or filing.get("primary_document", "")
                        ),
                        "SEC Filing": filing.get("url", "")
                    }
                    for filing in registration_rows
                ]
            )

            st.dataframe(
                registration_table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "SEC Filing": st.column_config.LinkColumn(
                        "SEC Filing",
                        display_text="Open filing"
                    )
                }
            )
        else:
            st.caption(
                "No S-1, S-1/A, F-1, F-1/A, S-11, or S-11/A was found in "
                "the SEC history available for this issuer."
            )

        registration_sec_url = registration_feed.get("sec_company_url", "")
        if registration_sec_url:
            st.link_button(
                "Open complete SEC filing history",
                registration_sec_url,
                key="registration_sec_history",
                use_container_width=True
            )


with learn_tab:
    section("Learning", "Understand the Numbers")
    st.write(
        "EquityLens is designed for users who are still learning how to read public-company information. "
        "The goal is to explain what a metric measures, show the reported or calculated value, and make the original source easy to inspect."
    )

    learning_items = [
        {
            "term": "S-1 Registration Statement",
            "definition": "Form S-1 is the SEC registration statement used by many U.S. companies when registering securities under the Securities Act of 1933. It is commonly associated with an initial public offering.",
            "why": "An S-1 can provide the first detailed public view of a company's business model, historical financial statements, ownership, risks, proposed use of proceeds, management, and offering structure.",
            "how": "Start with the Prospectus Summary, Risk Factors, Use of Proceeds, MD&A, Business, Financial Statements, and Principal Stockholders. Amendments filed as S-1/A can update pricing, share counts, financial information, or other disclosures before an offering.",
            "watch": "An S-1 describes an offering before or during the registration process. Terms can change through amendments, and filing a registration statement does not by itself guarantee that an IPO will be completed.",
            "source_url": "https://www.sec.gov/submit-filings/forms-index"
        },
        {
            "term": "8-K Current Report",
            "definition": "Form 8-K is the SEC current report public companies use to disclose specified significant corporate events between periodic 10-Q and 10-K reports.",
            "why": "An 8-K can surface information that matters before the next quarterly report, including certain acquisitions, financing events, leadership changes, material agreements, earnings-related disclosures, and other reportable events.",
            "how": "Read the item number, event date, filing date, exhibits, and any attached press release or agreement. The item number tells you what category of event triggered the filing.",
            "watch": "Not every company announcement is an 8-K, and some information in an 8-K may be furnished rather than filed. Read the filing language and exhibits instead of relying only on a headline.",
            "source_url": "https://www.sec.gov/submit-filings/forms-index"
        },
        {
            "term": "Consumer Price Index (CPI)",
            "definition": "The Consumer Price Index measures the average change over time in prices paid by urban consumers for a market basket of consumer goods and services.",
            "why": "CPI is one of the most closely watched U.S. inflation measures and can affect expectations for Federal Reserve policy, Treasury yields, financing conditions, and valuation assumptions.",
            "how": "EquityLens can compare the latest CPI index level with the level twelve months earlier to calculate a year-over-year inflation rate. Core CPI excludes food and energy.",
            "watch": "Monthly and year-over-year changes answer different questions. Also distinguish headline CPI from core CPI and from the PCE price index used prominently by the Federal Reserve.",
            "source_url": "https://www.bls.gov/cpi/"
        },
        {
            "term": "Producer Price Index (PPI)",
            "definition": "The Producer Price Index measures average changes in selling prices received by domestic producers for their output.",
            "why": "PPI helps investors track price pressure earlier in the production chain and can provide context for company input costs, margins, and broader inflation trends.",
            "how": "EquityLens tracks the BLS Final Demand series and can calculate year-over-year change from the official index levels.",
            "watch": "PPI covers many goods and services and can be volatile. A single monthly reading should be interpreted alongside prior trends and component details.",
            "source_url": "https://www.bls.gov/ppi/"
        },
        {
            "term": "Employment Situation",
            "definition": "The BLS Employment Situation combines major labor-market measures including payroll employment, unemployment, labor-force participation, and earnings.",
            "why": "Labor-market strength influences household income, demand, inflation pressure, and expectations for monetary policy.",
            "how": "Common market focal points include the unemployment rate, monthly change in nonfarm payrolls, and average hourly earnings.",
            "watch": "Payroll estimates can be revised. The payroll and household surveys are separate surveys and can tell somewhat different stories in a given month.",
            "source_url": "https://www.bls.gov/news.release/empsit.htm"
        },
        {
            "term": "JOLTS",
            "definition": "The Job Openings and Labor Turnover Survey reports job openings, hires, quits, layoffs and discharges, and other labor-turnover measures.",
            "why": "JOLTS can help show labor demand and worker confidence beyond the monthly payroll count.",
            "how": "Job openings are often compared with the number of unemployed workers, while the quits rate can provide context on workers' willingness to leave jobs voluntarily.",
            "watch": "JOLTS is released with a lag and can be revised, so it is best used as part of a broader labor-market picture.",
            "source_url": "https://www.bls.gov/jlt/"
        },
        {
            "term": "Employment Cost Index (ECI)",
            "definition": "The Employment Cost Index measures changes in employer costs for employee wages, salaries, and benefits.",
            "why": "ECI is useful for tracking compensation pressure while controlling for shifts in the mix of occupations and industries.",
            "how": "EquityLens can compare quarterly ECI index levels with the same quarter a year earlier to show the annual rate of compensation-cost change.",
            "watch": "ECI is quarterly, so it updates less frequently than payroll and hourly-earnings data.",
            "source_url": "https://www.bls.gov/eci/"
        },
        {
            "term": "10-Year Treasury Yield",
            "definition": "The 10-year Treasury yield is the market yield associated with U.S. Treasury securities around the 10-year maturity point on the Treasury par yield curve.",
            "why": "It is a widely watched benchmark for long-term interest rates and can influence borrowing costs, discount rates, mortgages, and equity valuation assumptions.",
            "how": "EquityLens reads the official daily Treasury par yield curve and displays the 10-year rate alongside shorter and longer maturities.",
            "watch": "Treasury yields move with inflation expectations, real-rate expectations, monetary policy, growth expectations, supply and demand, and risk sentiment.",
            "source_url": "https://home.treasury.gov/resource-center/data-chart-center/interest-rates"
        },
        {
            "term": "SOFR",
            "definition": "The Secured Overnight Financing Rate is a broad measure of the cost of borrowing cash overnight collateralized by U.S. Treasury securities.",
            "why": "SOFR is a central reference rate for U.S. dollar floating-rate financing and derivatives after the transition away from LIBOR.",
            "how": "The New York Fed publishes SOFR each business day as well as compounded 30-, 90-, and 180-day SOFR averages and a SOFR Index.",
            "watch": "SOFR itself is an overnight secured rate. A term or swap rate is a different market measure and should not be inferred simply by adding a spread to SOFR.",
            "source_url": "https://www.newyorkfed.org/markets/reference-rates/sofr"
        },
        {
            "term": "Interest-Rate Swap",
            "definition": "An interest-rate swap is a derivative contract in which counterparties exchange interest-payment streams, commonly a fixed rate for a floating rate tied to a benchmark such as SOFR.",
            "why": "Swap rates reflect market pricing for future interest-rate cash flows and are widely used in corporate finance, hedging, fixed-income markets, and valuation.",
            "how": "A quoted par swap rate is the fixed rate that makes the present value of the fixed and floating legs equal at inception for the specified maturity.",
            "watch": "OTC swap quotes depend on tenor, conventions, collateral, clearing, and market data. EquityLens does not manufacture swap quotes from Treasury yields; live swap rates should come from an authorized market-data source.",
            "source_url": "https://www.cmegroup.com/articles/2025/price-and-hedging-usd-sofr-interest-swaps-with-sofr-futures.html"
        },
        {
            "term": "Revenue",
            "definition": "Revenue is the money a company earns from selling its products or services before expenses are deducted.",
            "why": "Revenue helps show the size of the business and whether customer demand is expanding, slowing, or shrinking over time.",
            "how": "For example, if a company reports $1.0B of revenue this year and $800M last year, sales increased by $200M. Revenue by itself does not tell you whether the company was profitable.",
            "watch": "Look at revenue together with growth rates, margins, customer trends, and whether growth is coming from recurring business or one-time activity."
        },
        {
            "term": "Year-over-Year (YoY) Growth",
            "definition": "YoY growth measures how much a financial metric changed compared with the same period one year earlier.",
            "why": "Comparing the same quarter across years helps reduce seasonal distortions. A retailer's fourth quarter, for example, may naturally be stronger than its third quarter.",
            "how": "Formula: (current-period value - prior-year value) ÷ prior-year value × 100. If quarterly revenue rises from $100M to $120M, YoY growth is 20%.",
            "watch": "A high growth rate can look impressive, but check whether it is accelerating or slowing and whether profitability is improving alongside it."
        },
        {
            "term": "Gross Margin",
            "definition": "Gross margin is the percentage of revenue left after subtracting the direct costs required to deliver a product or service.",
            "why": "It gives a basic view of the economics of what a company sells. Higher gross margins generally mean more revenue remains to pay operating expenses such as research, sales, and administration.",
            "how": "Formula: gross profit ÷ revenue × 100. If revenue is $100M and gross profit is $75M, gross margin is 75%.",
            "watch": "Compare margins with the company's own history and similar businesses. Different industries naturally have very different gross-margin structures."
        },
        {
            "term": "Operating Margin",
            "definition": "Operating margin shows how much operating profit or loss a company produces after core operating expenses such as research and development, sales and marketing, and administration.",
            "why": "It helps show whether the core business is becoming more or less efficient as it grows.",
            "how": "Formula: operating income ÷ revenue × 100. If revenue is $100M and operating income is $10M, operating margin is 10%. If operating income is -$10M, the margin is -10%.",
            "watch": "An improving operating margin may indicate better cost discipline or operating leverage, but one quarter should not be treated as a long-term trend."
        },
        {
            "term": "Net Income",
            "definition": "Net income is the company's final reported profit or loss after operating expenses, interest, taxes, and other reported gains or losses.",
            "why": "It is commonly called the bottom line because it shows what remains after the major expenses and non-operating items recognized during the period.",
            "how": "A company can have positive operating results but lower net income because of interest or taxes, or it can report positive net income because of a one-time gain.",
            "watch": "Read net income alongside operating income and cash flow. Large one-time tax benefits, investment gains, restructuring charges, or other unusual items can make a single period less representative."
        },
        {
            "term": "LTM / Trailing Twelve Months",
            "definition": "LTM combines the most recent twelve months of financial results, usually using the latest four reported quarters.",
            "why": "It gives a more current full-year view than an older annual report when one or more newer quarters have already been released.",
            "how": "If a company's latest 10-K ended six months ago, LTM can combine the newer quarterly results with the remaining quarters needed to create a rolling twelve-month total.",
            "watch": "LTM is calculated rather than a separate SEC reporting period. Always check which quarters are included, especially when comparing companies with different fiscal year-ends."
        },
        {
            "term": "10-K",
            "definition": "A 10-K is the detailed annual report that most U.S. public companies file with the SEC.",
            "why": "It is one of the most important primary sources for understanding a company because it includes audited annual financial statements, the business description, risk factors, management discussion, and other disclosures.",
            "how": "Useful sections include Business, Risk Factors, MD&A, Financial Statements and Notes, and information about debt, stock-based compensation, customers, and accounting policies.",
            "watch": "A 10-K is comprehensive but backward-looking. Pair it with newer 10-Q and 8-K filings so you are not relying on an outdated picture."
        },
        {
            "term": "10-Q",
            "definition": "A 10-Q is the quarterly report that most U.S. public companies file with the SEC for the first three fiscal quarters of the year.",
            "why": "It provides more recent financial statements and management commentary between annual 10-K filings.",
            "how": "A 10-Q can help you compare the newest quarter with the prior quarter and the same quarter a year earlier, while also showing changes in the balance sheet and cash flow.",
            "watch": "Quarterly figures can be seasonal or volatile. Compare them with prior periods and read the accompanying notes rather than judging a company from one number."
        },
        {
            "term": "Cash + Investments",
            "definition": "Cash and investments represent liquid financial resources reported on the balance sheet, although the exact categories included can vary by company.",
            "why": "These resources can help fund operations, acquisitions, debt repayment, share repurchases, or investment during periods when cash generation is weak.",
            "how": "EquityLens combines selected reported cash and investment balances when the underlying filing provides enough information to do so consistently.",
            "watch": "Do not treat every investment as identical to cash. Some securities may have different maturities, restrictions, or liquidity characteristics."
        },
        {
            "term": "Debt",
            "definition": "Debt is borrowed capital that the company is obligated to repay under specified terms.",
            "why": "Debt can finance growth or acquisitions, but it also creates repayment obligations and often interest expense.",
            "how": "When reviewing debt, compare it with cash, operating cash generation, maturity dates, interest rates, and the company's ability to refinance or repay it.",
            "watch": "Debt is not automatically negative, and zero debt is not automatically superior. Its significance depends on the company's business model, cash flow, cost of capital, and financial flexibility."
        }
    ]

    for item in learning_items:
        with st.expander(item["term"]):
            st.markdown("**What it means**")
            st.write(item["definition"])
            st.markdown("**Why it matters**")
            st.write(item["why"])
            st.markdown("**How to think about it**")
            st.write(item["how"])
            st.markdown("**What to watch for**")
            st.write(item["watch"])
            if item.get("source_url"):
                st.link_button(
                    "Open primary source",
                    item["source_url"],
                    key="learning_source_" + re.sub(
                        r"[^a-z0-9]+",
                        "_",
                        item["term"].lower()
                    ).strip("_")
                )

    section("Source Guide", "How EquityLens Labels Information")
    st.markdown(
        """
        **Reported** — a figure taken from a company filing or company-reported disclosure.

        **Calculated by EquityLens** — a metric computed from reported figures, such as revenue growth or operating margin.

        **Educational explanation** — plain-language context explaining what a financial term means. It is not a buy, sell, or hold recommendation.

        **Source** — the original filing or disclosure used for the underlying information. When available, EquityLens links directly to the filing so users can verify the data themselves.
        """
    )

    st.info(
        "EquityLens does not rate companies, predict returns, or tell users what securities to buy or sell. "
        "It is designed to help users understand public information and perform their own research."
    )

    section("Learning Resources", "Curated Video Lessons")
    st.write(
        "These external videos are included as supplemental education from established investors, "
        "finance educators, and primary creators. EquityLens links to the original uploader and does "
        "not reproduce or claim ownership of their content. Inclusion is not an endorsement of every "
        "view expressed in a video; they are included as supplemental educational resources."
    )

    video_resources = [
        {
            "title": "Valuation: A Preview",
            "creator": "Aswath Damodaran",
            "credit": "Professor of Finance, NYU Stern; original YouTube uploader",
            "url": "https://www.youtube.com/watch?v=LYGYvN5LUbA",
            "why": (
                "A useful introduction to how valuation combines financial numbers with a business story, "
                "and why value and market price are not the same thing."
            ),
            "topics": "Valuation, business fundamentals, price vs. value"
        },
        {
            "title": "Introduction to Valuation Class",
            "creator": "Aswath Damodaran",
            "credit": "Professor of Finance, NYU Stern; original YouTube uploader",
            "url": "https://www.youtube.com/watch?v=oi6M5KBWydg",
            "why": (
                "Introduces the basic logic behind valuing companies and the role of assumptions, "
                "financial statements, and judgment."
            ),
            "topics": "Valuation foundations, financial analysis"
        },
        {
            "title": "Passing Along My Investment and Economic Principles",
            "creator": "Ray Dalio",
            "credit": "Principles by Ray Dalio; original YouTube uploader",
            "url": "https://www.youtube.com/watch?v=y5LyVSQq3Wc",
            "why": (
                "A high-level perspective on how an experienced institutional investor thinks about "
                "investment principles, economics, diversification, and decision-making."
            ),
            "topics": "Investment principles, economics, portfolio thinking"
        },
        {
            "title": "How To Read An Annual Report (10-K)",
            "creator": "Hamish Hodder",
            "credit": "Hamish Hodder; original YouTube uploader",
            "url": "https://www.youtube.com/watch?v=Q0o9S0q0Rr4",
            "why": (
                "Walks through how a long-term investor approaches a 10-K and which sections can help "
                "a reader understand a company's business and financial condition."
            ),
            "topics": "10-Ks, annual reports, fundamental research"
        }
    ]

    for resource in video_resources:
        with st.expander(f"▶ {resource['title']} — {resource['creator']}"):
            st.write(resource["why"])
            st.caption(f"Topics: {resource['topics']}")
            st.caption(f"Credit: {resource['credit']}")
            st.link_button(
                "Watch on the original YouTube channel",
                resource["url"],
                key=f"learning_video_{resource['title']}"
            )

    st.caption(
        "External learning resources remain the property of their respective creators and platforms. "
        "EquityLens provides outbound links and attribution only. Video availability, titles, and content "
        "may change at the creator's discretion."
    )

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

