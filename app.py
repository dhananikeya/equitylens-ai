# EquityLens AI
# Copyright © 2026 Keya Dhanani. All rights reserved.
# Independently designed and developed by Keya Dhanani.
# Unauthorized reproduction, redistribution, republication, or creation of a substantially
# similar copy of this original application code is not permitted except where allowed by law
# or applicable platform terms. Third-party libraries, public filings, factual source data,
# company names, and trademarks remain subject to their respective rights and terms.

import json
import requests
import pandas as pd
import streamlit as st
from supabase import create_client
from openai import OpenAI

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
        --el-bg: #050b0e;
        --el-panel: #0a1318;
        --el-panel-2: #0d171d;
        --el-panel-3: #111c24;
        --el-border: #263640;
        --el-border-soft: rgba(130, 154, 166, .18);
        --el-text: #eef3f5;
        --el-muted: #8f9ca6;
        --el-muted-2: #63727d;
        --el-teal: #16c7b2;
        --el-teal-soft: rgba(22, 199, 178, .12);
        --el-blue: #7dd3fc;
        --el-red: #ff6b72;
        --el-font: "IBM Plex Sans", "Segoe UI", Arial, sans-serif;
        --el-mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
    }

    html, body, .stApp {
        font-family: var(--el-font) !important;
        background: var(--el-bg) !important;
        color: var(--el-text) !important;
    }

    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    footer,
    #MainMenu {
        display: none !important;
        visibility: hidden !important;
    }

    .block-container {
        max-width: 100% !important;
        padding: 88px 0 0 0 !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 76% 19%, rgba(22,199,178,.035), transparent 25%),
            var(--el-bg) !important;
    }

    h1, h2, h3, h4, h5, h6,
    p, li, label, input, textarea, button,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-baseweb="tab"] {
        font-family: var(--el-font) !important;
    }

    .material-symbols-rounded,
    [data-testid="stIconMaterial"] {
        font-family: "Material Symbols Rounded" !important;
        font-weight: normal !important;
        font-style: normal !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        font-feature-settings: "liga" !important;
        -webkit-font-feature-settings: "liga" !important;
    }

    /* ---------- fixed product header ---------- */
    .el-topbar {
        position: fixed;
        z-index: 9999;
        top: 0;
        left: 0;
        right: 0;
        height: 88px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 26px;
        box-sizing: border-box;
        background: rgba(5, 11, 14, .97);
        border-bottom: 1px solid var(--el-border);
        backdrop-filter: blur(12px);
    }

    .el-brand {
        display: inline-flex;
        align-items: center;
        gap: 15px;
        color: var(--el-text) !important;
        text-decoration: none !important;
        font-weight: 700;
        font-size: 1.28rem;
        letter-spacing: -.02em;
    }

    .el-brand strong { color: var(--el-teal); font-weight: 700; }

    .el-logo-mark {
        width: 35px;
        height: 35px;
        border: 1px solid var(--el-border);
        border-radius: 6px;
        background: #0c151a;
        display: flex;
        align-items: flex-end;
        justify-content: center;
        gap: 4px;
        padding: 7px 7px 8px;
        box-sizing: border-box;
    }

    .el-logo-mark i {
        display: block;
        width: 4px;
        border-radius: 1px;
        background: var(--el-teal);
    }
    .el-logo-mark i:nth-child(1) { height: 8px; opacity: .55; }
    .el-logo-mark i:nth-child(2) { height: 15px; opacity: .8; }
    .el-logo-mark i:nth-child(3) { height: 22px; }

    .el-top-actions {
        display: flex;
        align-items: center;
        gap: 20px;
    }

    .el-search-link,
    .el-workspace-link {
        color: var(--el-text) !important;
        text-decoration: none !important;
    }

    .el-search-link {
        width: 34px;
        height: 34px;
        display: grid;
        place-items: center;
    }

    .el-search-link svg {
        width: 21px;
        height: 21px;
        stroke: var(--el-text);
    }

    .el-workspace-link {
        border: 1px solid var(--el-border);
        border-radius: 8px;
        padding: 12px 18px;
        font-weight: 600;
        background: rgba(255,255,255,.01);
    }

    .el-workspace-link:hover {
        border-color: rgba(22,199,178,.55);
        background: rgba(22,199,178,.045);
    }

    .el-menu {
        position: relative;
    }

    .el-menu summary {
        list-style: none;
        cursor: pointer;
        width: 34px;
        height: 34px;
        display: grid;
        place-items: center;
        color: var(--el-text);
        font-size: 1.6rem;
        line-height: 1;
        user-select: none;
    }

    .el-menu summary::-webkit-details-marker { display: none; }

    .el-menu-panel {
        position: absolute;
        top: 48px;
        right: 0;
        width: 250px;
        padding: 8px;
        border: 1px solid var(--el-border);
        border-radius: 10px;
        background: #091116;
        box-shadow: 0 24px 70px rgba(0,0,0,.45);
    }

    .el-menu-panel a {
        display: block;
        padding: 11px 12px;
        color: var(--el-muted) !important;
        text-decoration: none !important;
        border-radius: 6px;
        font-size: .92rem;
    }

    .el-menu-panel a:hover {
        color: var(--el-text) !important;
        background: rgba(22,199,178,.07);
    }

    /* ---------- full-bleed sections ---------- */
    .el-page-section {
        padding: 96px max(24px, calc((100vw - 1390px) / 2));
        box-sizing: border-box;
        border-bottom: 1px solid var(--el-border);
    }

    .el-grid-bg {
        background-color: var(--el-bg);
        background-image:
            linear-gradient(rgba(52, 73, 83, .26) 1px, transparent 1px),
            linear-gradient(90deg, rgba(52, 73, 83, .26) 1px, transparent 1px),
            radial-gradient(circle at 71% 37%, rgba(22,199,178,.07), transparent 29%);
        background-size: 73px 73px, 73px 73px, auto;
    }

    .el-hero {
        min-height: 775px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding-top: 86px;
        padding-bottom: 76px;
    }

    .el-hero-kicker {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 46px;
        color: var(--el-muted);
        font-size: 1.02rem;
    }

    .el-hero-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background: var(--el-teal);
        box-shadow: 0 0 0 4px rgba(22,199,178,.05);
    }

    .el-hero-title {
        max-width: 980px;
        margin: 0;
        font-size: clamp(4.3rem, 7.25vw, 7rem);
        line-height: .98;
        letter-spacing: -.055em;
        font-weight: 600;
        color: var(--el-text);
    }

    .el-hero-title .muted-line {
        color: #7f8b94;
    }

    .el-hero-copy {
        max-width: 930px;
        margin: 42px 0 0 0;
        color: #8f9ca6;
        font-size: clamp(1.05rem, 1.65vw, 1.38rem);
        line-height: 1.75;
    }

    .el-hero-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin-top: 44px;
    }

    .el-hero-btn {
        min-width: 250px;
        padding: 15px 21px;
        border-radius: 7px;
        border: 1px solid var(--el-border);
        text-decoration: none !important;
        color: var(--el-text) !important;
        font-weight: 600;
        text-align: center;
        box-sizing: border-box;
    }

    .el-hero-btn.primary {
        color: #03110f !important;
        border-color: var(--el-teal);
        background: var(--el-teal);
    }

    .el-hero-btn:hover { border-color: var(--el-teal); }

    .el-motto {
        margin-top: 44px;
        font-family: var(--el-mono);
        color: var(--el-teal);
        font-size: 1rem;
        letter-spacing: .01em;
    }

    .el-trust-row {
        min-height: 105px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 56px;
        padding: 0 24px;
        border-bottom: 1px solid var(--el-border);
        background: #071014;
        box-sizing: border-box;
    }

    .el-trust-point {
        display: inline-flex;
        align-items: center;
        gap: 11px;
        color: var(--el-muted);
        font-size: .93rem;
        white-space: nowrap;
    }

    .el-trust-check {
        width: 16px;
        height: 16px;
        border: 1px solid var(--el-teal);
        border-radius: 50%;
        display: grid;
        place-items: center;
        color: var(--el-teal);
        font-size: .65rem;
        line-height: 1;
    }

    .el-eyebrow {
        font-family: var(--el-mono);
        color: var(--el-teal);
        text-transform: uppercase;
        font-size: .82rem;
        font-weight: 600;
        letter-spacing: .035em;
        margin-bottom: 22px;
    }

    .el-section-heading {
        margin: 0;
        max-width: 1050px;
        color: var(--el-text);
        font-size: clamp(2.35rem, 4vw, 3.55rem);
        line-height: 1.08;
        letter-spacing: -.035em;
        font-weight: 600;
    }

    .el-section-copy {
        margin-top: 24px;
        max-width: 920px;
        color: var(--el-muted);
        font-size: 1.15rem;
        line-height: 1.7;
    }

    /* ---------- research record ---------- */
    .el-record-wrap { padding-top: 78px; padding-bottom: 78px; }

    .el-research-record {
        border: 1px solid var(--el-border);
        border-radius: 11px;
        overflow: hidden;
        background: rgba(10, 19, 24, .95);
    }

    .el-record-head {
        min-height: 80px;
        padding: 0 28px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid var(--el-border);
        color: var(--el-text);
        font-weight: 600;
    }

    .el-source-pill {
        display: inline-flex;
        align-items: center;
        gap: 9px;
        padding: 8px 14px;
        border: 1px solid var(--el-border);
        border-radius: 999px;
        color: var(--el-muted);
        font-family: var(--el-mono);
        font-size: .77rem;
        font-weight: 500;
    }

    .el-source-pill::before {
        content: "";
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--el-teal);
    }

    .el-record-body { padding: 38px 34px 30px; }

    .el-record-title-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 24px;
        margin-bottom: 32px;
    }

    .el-record-title {
        margin: 0;
        font-size: 2rem;
        font-weight: 600;
        letter-spacing: -.025em;
    }

    .el-record-subtitle {
        margin-top: 8px;
        color: var(--el-muted);
        font-size: 1rem;
    }

    .el-period-badge {
        padding: 7px 12px;
        border-radius: 6px;
        color: var(--el-teal);
        background: rgba(22,199,178,.10);
        font-family: var(--el-mono);
        font-size: .86rem;
    }

    .el-metric-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        border: 1px solid var(--el-border);
        border-radius: 8px;
        overflow: hidden;
    }

    .el-metric-cell {
        min-height: 126px;
        padding: 27px 25px;
        box-sizing: border-box;
        background: rgba(6,14,18,.20);
    }

    .el-metric-cell:nth-child(1),
    .el-metric-cell:nth-child(3) { border-right: 1px solid var(--el-border); }
    .el-metric-cell:nth-child(1),
    .el-metric-cell:nth-child(2) { border-bottom: 1px solid var(--el-border); }

    .el-metric-label {
        font-family: var(--el-mono);
        color: var(--el-muted);
        text-transform: uppercase;
        font-size: .76rem;
        font-weight: 600;
        letter-spacing: .02em;
    }

    .el-metric-value {
        margin-top: 13px;
        color: var(--el-text);
        font-family: var(--el-mono);
        font-size: 1.82rem;
        line-height: 1.1;
        font-weight: 500;
    }

    .el-metric-value.teal { color: var(--el-teal); }

    .el-record-source {
        margin-top: 34px;
        padding-top: 24px;
        border-top: 1px solid var(--el-border);
    }

    .el-record-source-row {
        display: flex;
        justify-content: space-between;
        gap: 24px;
        color: var(--el-muted);
        font-size: .9rem;
    }

    .el-record-source-row .reported { color: #82d7ff; }

    .el-validation-line {
        height: 3px;
        margin: 14px 0 11px;
        border-radius: 2px;
        background: linear-gradient(90deg, var(--el-teal) 0 82%, #162129 82% 100%);
    }

    .el-validation-note {
        color: var(--el-muted);
        font-size: .82rem;
    }

    .el-record-link {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 24px;
        padding-top: 22px;
        border-top: 1px solid var(--el-border);
        color: var(--el-teal) !important;
        text-decoration: none !important;
        font-size: .95rem;
    }

    /* ---------- workflow ---------- */
    .el-workflow-grid {
        margin-top: 68px;
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        border: 1px solid var(--el-border);
        border-radius: 9px;
        overflow: hidden;
    }

    .el-workflow-card {
        min-height: 264px;
        padding: 36px 32px;
        border-right: 1px solid var(--el-border);
        background: rgba(10, 19, 24, .64);
        box-sizing: border-box;
    }
    .el-workflow-card:last-child { border-right: none; }

    .el-workflow-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-family: var(--el-mono);
        color: var(--el-teal);
        font-size: .82rem;
    }

    .el-workflow-icon {
        color: var(--el-muted);
        font-family: var(--el-mono);
        font-size: 1rem;
    }

    .el-workflow-title {
        margin-top: 58px;
        color: var(--el-text);
        font-size: 1.32rem;
        font-weight: 600;
    }

    .el-workflow-copy {
        margin-top: 20px;
        color: var(--el-muted);
        font-size: .98rem;
        line-height: 1.75;
    }

    /* ---------- AI showcase ---------- */
    .el-ai-intro {
        max-width: 730px;
    }

    .el-ai-question-card {
        margin-top: 66px;
        border: 1px solid var(--el-border);
        border-radius: 10px;
        padding: 36px 38px;
        background: rgba(10, 19, 24, .82);
    }

    .el-ai-q-head {
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .el-mini-logo {
        width: 34px;
        height: 34px;
        border: 1px solid var(--el-border);
        border-radius: 6px;
        display: grid;
        place-items: center;
        color: var(--el-teal);
        font-family: var(--el-mono);
        font-size: .75rem;
        background: #0c151a;
    }

    .el-ai-q-title {
        font-size: 1rem;
        color: var(--el-text);
        font-weight: 600;
    }

    .el-ai-q-meta {
        margin-top: 5px;
        color: var(--el-muted);
        font-size: .82rem;
    }

    .el-ai-answer {
        margin: 34px 0 0 0;
        padding: 7px 0 7px 30px;
        border-left: 2px solid var(--el-teal);
        color: var(--el-text);
        font-size: 1.05rem;
        line-height: 1.85;
    }

    .el-source-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 22px;
    }

    .el-source-tag {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 12px;
        border: 1px solid var(--el-border);
        border-radius: 999px;
        color: var(--el-muted);
        font-family: var(--el-mono);
        font-size: .76rem;
    }

    .el-source-tag::before {
        content: "";
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--el-teal);
    }

    .el-ai-trust-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-top: 36px;
    }

    .el-ai-trust {
        padding: 13px 15px;
        text-align: center;
        border-radius: 6px;
        background: #111c24;
        color: var(--el-muted);
        font-size: .86rem;
    }

    /* ---------- Streamlit controls ---------- */
    .el-control-shell {
        margin-top: 50px;
        margin-bottom: 20px;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"],
    textarea,
    input {
        background: #091217 !important;
        border-color: var(--el-border) !important;
        color: var(--el-text) !important;
        border-radius: 7px !important;
    }

    .stSelectbox label,
    .stMultiSelect label,
    .stTextInput label {
        color: var(--el-muted) !important;
        font-size: .82rem !important;
    }

    .stButton > button,
    .stLinkButton > a,
    .stDownloadButton > button {
        min-height: 46px !important;
        border-radius: 7px !important;
        border: 1px solid var(--el-border) !important;
        background: #081116 !important;
        color: var(--el-text) !important;
        font-weight: 600 !important;
        box-shadow: none !important;
    }

    .stButton > button:hover,
    .stLinkButton > a:hover,
    .stDownloadButton > button:hover {
        border-color: rgba(22,199,178,.65) !important;
        color: var(--el-text) !important;
    }

    .stButton > button[kind="primary"] {
        border-color: var(--el-teal) !important;
        background: var(--el-teal) !important;
        color: #03110f !important;
    }

    div[data-testid="stMetric"] {
        padding: 22px !important;
        border: 1px solid var(--el-border) !important;
        border-radius: 8px !important;
        background: #091217 !important;
        box-shadow: none !important;
    }

    div[data-testid="stMetricLabel"] { color: var(--el-muted) !important; }
    div[data-testid="stMetricValue"] {
        color: var(--el-text) !important;
        font-family: var(--el-mono) !important;
        font-weight: 500 !important;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--el-border) !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        background: #091217 !important;
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--el-border) !important;
        border-radius: 8px !important;
        background: #091217 !important;
    }

    div[data-testid="stAlert"] {
        border-radius: 8px !important;
        border-color: var(--el-border) !important;
        background: #0b151b !important;
        color: var(--el-text) !important;
    }

    [data-testid="stChatMessage"] {
        background: #091217 !important;
        border: 1px solid var(--el-border) !important;
        border-radius: 9px !important;
        padding: 14px !important;
        margin-bottom: 12px !important;
    }

    /* ---------- existing research pages ---------- */
    .el-section {
        max-width: 1390px;
        margin: 0 auto;
        padding: 38px 24px 12px;
        box-sizing: border-box;
    }

    .el-section-label {
        color: var(--el-teal);
        text-transform: uppercase;
        letter-spacing: .045em;
        font-family: var(--el-mono);
        font-size: .78rem;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .el-section-title {
        color: var(--el-text);
        font-size: clamp(2rem, 3.4vw, 3.05rem);
        line-height: 1.1;
        letter-spacing: -.035em;
        font-weight: 600;
        margin: 0;
    }

    .el-company-hero,
    .el-summary-card,
    .el-change-card,
    .el-risk-card,
    .el-feature-card,
    .el-ai-panel,
    .el-answer-card {
        border: 1px solid var(--el-border) !important;
        border-radius: 9px !important;
        background: #091217 !important;
        box-shadow: none !important;
    }

    .el-company-hero { padding: 28px 30px; margin: 18px 0 28px; }
    .el-kicker { color: var(--el-teal); font-family: var(--el-mono); font-size: .78rem; text-transform: uppercase; }
    .el-company-title { margin-top: 8px; color: var(--el-text); font-size: 2rem; font-weight: 600; }
    .el-subtitle { color: var(--el-muted); line-height: 1.7; }
    .el-badges { display:flex; gap:8px; flex-wrap:wrap; margin-top:16px; }
    .el-badge { border:1px solid var(--el-border); border-radius:999px; padding:6px 10px; color:var(--el-muted); font-size:.75rem; }

    .el-summary-card { min-height: 124px; padding: 22px; }
    .el-summary-label { color: var(--el-muted); font-size: .8rem; text-transform: uppercase; font-family: var(--el-mono); }
    .el-summary-value { margin-top: 12px; color: var(--el-text); font-family: var(--el-mono); font-size: 1.55rem; }

    .el-change-card, .el-risk-card, .el-feature-card, .el-ai-panel, .el-answer-card { padding: 22px; margin: 12px 0; }
    .el-change-title, .el-risk-title, .el-feature-title, .el-ai-title { color: var(--el-text); font-weight: 600; }
    .el-change-copy, .el-feature-copy, .el-ai-copy, .el-answer-copy { color: var(--el-muted); line-height: 1.65; }
    .el-feature-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }
    .el-feature-num, .el-ai-kicker, .el-answer-kicker { color:var(--el-teal); font-family:var(--el-mono); font-size:.74rem; text-transform:uppercase; }
    .el-risk-list { color: var(--el-muted); }

    /* keep all non-home page widgets centered */
    .stSelectbox, .stMultiSelect, .stButton, .stDownloadButton, .stLinkButton,
    [data-testid="stDataFrame"], [data-testid="stAlert"], [data-testid="stChatMessage"],
    .stCaption, div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stMetric"]) {
        max-width: 1390px;
    }

    /* ---------- footer ---------- */
    .el-evidence {
        min-height: 225px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 36px;
        padding-top: 60px;
        padding-bottom: 60px;
    }

    .el-evidence-title {
        color: var(--el-text);
        font-size: 1.9rem;
        font-weight: 600;
        letter-spacing: -.025em;
    }

    .el-evidence-copy {
        margin-top: 10px;
        color: var(--el-muted);
        font-size: 1rem;
    }

    .el-evidence-note {
        display: flex;
        align-items: center;
        gap: 12px;
        color: var(--el-muted);
        font-size: .9rem;
    }

    .el-evidence-shield {
        color: var(--el-teal);
        font-size: 1.15rem;
    }

    .el-footer {
        padding-top: 54px;
        padding-bottom: 48px;
        background: #071014;
    }

    .el-footer-grid {
        display: grid;
        grid-template-columns: .8fr 1.2fr;
        gap: 88px;
    }

    .el-footer-brandline {
        display: flex;
        align-items: center;
        gap: 12px;
        color: var(--el-text);
        font-size: 1.18rem;
        font-weight: 700;
    }

    .el-footer-brandline strong { color: var(--el-teal); }
    .el-footer-motto { margin-top: 22px; color: var(--el-muted); }
    .el-footer-copy { color: var(--el-muted); line-height: 1.8; font-size: .9rem; }

    .el-footer-links {
        display: flex;
        gap: 28px;
        margin-top: 26px;
    }

    .el-footer-links a {
        color: var(--el-muted) !important;
        text-decoration: none !important;
        font-size: .86rem;
    }

    .el-footer-bottom {
        margin-top: 42px;
        padding-top: 28px;
        border-top: 1px solid var(--el-border);
        color: var(--el-muted);
        font-size: .84rem;
    }

    .el-footer-details {
        margin-top: 26px;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }

    .el-footer-details details {
        border: 1px solid var(--el-border);
        border-radius: 7px;
        padding: 13px 15px;
        color: var(--el-muted);
        font-size: .84rem;
        line-height: 1.6;
    }

    .el-footer-details summary {
        cursor: pointer;
        color: var(--el-text);
        font-weight: 600;
    }

    /* ---------- responsive ---------- */
    @media (max-width: 900px) {
        .block-container { padding-top: 74px !important; }
        .el-topbar { height: 74px; padding: 0 15px; }
        .el-workspace-link { display: none; }
        .el-brand { font-size: 1.05rem; gap: 10px; }
        .el-logo-mark { width: 31px; height: 31px; }
        .el-page-section { padding: 66px 18px; }
        .el-hero { min-height: 680px; padding-top: 70px; }
        .el-hero-kicker { margin-bottom: 32px; font-size: .92rem; }
        .el-hero-title { font-size: clamp(3rem, 15vw, 4.7rem); }
        .el-hero-copy { margin-top: 30px; font-size: 1rem; }
        .el-hero-btn { width: 100%; min-width: 0; }
        .el-trust-row { align-items:flex-start; flex-direction:column; gap:14px; padding:24px 18px; }
        .el-metric-grid { grid-template-columns: 1fr; }
        .el-metric-cell { border-right: none !important; border-bottom: 1px solid var(--el-border) !important; }
        .el-metric-cell:last-child { border-bottom: none !important; }
        .el-record-title-row { flex-direction: column; }
        .el-workflow-grid { grid-template-columns:1fr; }
        .el-workflow-card { border-right:none; border-bottom:1px solid var(--el-border); min-height:210px; }
        .el-workflow-card:last-child { border-bottom:none; }
        .el-workflow-title { margin-top:32px; }
        .el-ai-trust-grid { grid-template-columns:1fr 1fr; }
        .el-feature-grid { grid-template-columns:1fr; }
        .el-evidence { align-items:flex-start; flex-direction:column; }
        .el-footer-grid { grid-template-columns:1fr; gap:34px; }
        .el-footer-details { grid-template-columns:1fr; }
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



def get_openai_client():
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def build_equitylens_ai_context(company_name):
    data = company_data.get(company_name, {})
    analysis = company_analysis.get(company_name, {})
    quarterly = company_quarterly.get(company_name, {})
    s1 = company_s1.get(company_name, {})
    filings = sec_filings.get(company_name, {}).get("filings", [])[:8]

    context = {
        "company": company_name,
        "ticker": data.get("ticker"),
        "industry": data.get("industry"),
        "annual_financials": {
            "fiscal_year": data.get("fiscal_year"),
            "fiscal_year_end": data.get("fiscal_year_end"),
            "revenue": data.get("revenue"),
            "gross_profit": data.get("gross_profit"),
            "operating_income": data.get("operating_income"),
            "net_income": data.get("net_income"),
            "cash": data.get("cash"),
            "assets": data.get("assets"),
            "history": data.get("history", []),
            "source_filing": data.get("filing_url")
        },
        "capital_structure": data.get("capital_structure", {}),
        "quarterly_and_ltm": quarterly,
        "business_and_risk_research": analysis,
        "historical_s1_context": s1,
        "recent_sec_filings": filings
    }
    return json.dumps(context, indent=2)


def equitylens_ai_answer(company_name, messages):
    client = get_openai_client()
    if client is None:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    context = build_equitylens_ai_context(company_name)
    recent_messages = messages[-8:]

    instructions = """
You are EquityLens AI, a source-grounded public-company research assistant.

Your job is to help users understand the company using ONLY the EquityLens context supplied
with the request. Do not use outside knowledge, memory, web search, or unsupported assumptions.

Rules:
1. Never invent financial figures, filing details, management commentary, dates, or causes.
2. If the supplied context does not support an answer, say that the current EquityLens dataset
   does not contain enough information and identify what additional filing or data would be needed.
3. Clearly distinguish:
   - Reported: figures or disclosures from company/SEC sources.
   - Calculated by EquityLens: metrics derived from reported figures.
   - Research summary: plain-language interpretation of supplied disclosures.
4. Do not give personalized investment advice, buy/sell/hold recommendations, price targets,
   rankings, or say one security is the best investment.
5. You may neutrally compare growth, profitability, capital structure, business models, and risks.
6. Be concise but substantive. Explain finance terminology when useful.
7. When discussing a number, include its relevant reporting period when the context provides one.
8. End with a short 'Source basis' line naming the relevant filing type or structured EquityLens
   dataset used. Do not fabricate citations or URLs.
"""

    input_items = [
        {
            "role": "user",
            "content": (
                "EQUITYLENS VERIFIED CONTEXT FOR THIS COMPANY:\n"
                f"{context}\n\n"
                "Use this context as the sole factual basis for the conversation."
            )
        }
    ]

    for message in recent_messages:
        input_items.append({
            "role": message["role"],
            "content": message["content"]
        })

    response = client.responses.create(
        model="gpt-6-luna",
        instructions=instructions,
        input=input_items
    )
    return response.output_text


def equitylens_s1_ai_brief(company_name):
    client = get_openai_client()
    if client is None:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    s1_context = company_s1.get(company_name, {})
    company = company_name.split(" (")[0]

    instructions = """
You are EquityLens AI, a source-grounded public-company research assistant.

Create a concise S-1 research brief using ONLY the S-1 context supplied with the request.
Do not use outside knowledge, memory, web search, or unsupported assumptions.

Structure the brief with these headings:
- Business model
- Customers and go-to-market
- Growth strategy
- Competition and differentiation
- Key disclosed risks
- Financial and operating history
- IPO structure and ownership
- What matters most to understand

Rules:
1. Treat the filing as historical IPO-era context, not current company information.
2. Never invent figures or claims.
3. If a section is not supported by the supplied context, say so briefly.
4. Do not rank the company, recommend the security, or use buy/sell/hold language.
5. Keep the tone analytical, neutral, and accessible.
6. End with: "Source basis: company S-1 / registration filing context in EquityLens."
"""

    response = client.responses.create(
        model="gpt-6-luna",
        instructions=instructions,
        input=[
            {
                "role": "user",
                "content": (
                    f"COMPANY: {company}\n\n"
                    "EQUITYLENS S-1 CONTEXT:\n"
                    f"{json.dumps(s1_context, indent=2)}"
                )
            }
        ]
    )
    return response.output_text


def equitylens_source_links(company_name):
    data = company_data.get(company_name, {})
    analysis = company_analysis.get(company_name, {})
    quarterly = company_quarterly.get(company_name, {})
    links = []

    annual = data.get("filing_url")
    if annual:
        links.append(("Annual filing", annual))

    quarter = quarterly.get("source_filing")
    if quarter and quarter != annual:
        links.append(("Latest quarterly filing", quarter))

    analysis_source = analysis.get("source_filing")
    if analysis_source and analysis_source not in [url for _, url in links]:
        links.append(("Risk / business source", analysis_source))

    for filing in sec_filings.get(company_name, {}).get("filings", [])[:3]:
        url = filing.get("url")
        form = filing.get("form", "SEC filing")
        filed = filing.get("filing_date", "")
        label = f"{form} filed {filed}" if filed else form
        if url and url not in [existing_url for _, existing_url in links]:
            links.append((label, url))

    return links[:5]





@st.cache_data(ttl=60)
def load_json(path):
    with open(path, "r") as file:
        return json.load(file)


@st.cache_data(ttl=300)
def get_live_market_data(symbols):
    api_key = st.secrets.get(
        "TWELVE_DATA_API_KEY",
        st.secrets.get("FINIMPULSE_API_KEY")
    )

    if not api_key:
        raise ValueError("Missing Twelve Data API key in Streamlit Secrets.")

    response = requests.get(
        "https://api.twelvedata.com/quote",
        params={"symbol": ",".join(symbols), "apikey": api_key},
        timeout=20
    )
    response.raise_for_status()
    body = response.json()

    if isinstance(body, dict) and body.get("status") == "error":
        raise ValueError(body.get("message", "Twelve Data API error"))

    if len(symbols) == 1 and isinstance(body, dict) and body.get("symbol"):
        body = {symbols[0]: body}

    return {
        symbol: body.get(symbol, {})
        for symbol in symbols
        if isinstance(body, dict)
    }


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


company_data = load_json("data/company_metrics.json")
company_analysis = load_json("data/company_analysis.json")
company_quarterly = load_json("data/company_quarterly.json")
company_s1 = load_json("data/company_s1.json")
sec_filings = load_json("data/sec_filings.json")

public_market_data_enabled = bool(
    st.secrets.get("PUBLIC_MARKET_DATA_ENABLED", False)
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

current_view = st.query_params.get("view", "home")
if current_view not in {"home", "explore", "compare", "ai", "filings", "learn"}:
    current_view = "home"

st.markdown(
    """
    <div class="el-topbar">
        <a class="el-brand" href="?view=home" target="_self">
            <span class="el-logo-mark"><i></i><i></i><i></i></span>
            <span>EquityLens <strong>AI</strong></span>
        </a>
        <div class="el-top-actions">
            <a class="el-search-link" href="?view=explore" target="_self" aria-label="Explore companies">
                <svg viewBox="0 0 24 24" fill="none" stroke-width="2">
                    <circle cx="11" cy="11" r="7"></circle>
                    <path d="M20 20l-4-4"></path>
                </svg>
            </a>
            <a class="el-workspace-link" href="?view=explore" target="_self">Research workspace</a>
            <details class="el-menu">
                <summary aria-label="Open navigation">☰</summary>
                <div class="el-menu-panel">
                    <a href="?view=home" target="_self">Home</a>
                    <a href="?view=explore" target="_self">Explore Companies</a>
                    <a href="?view=compare" target="_self">Industry Comparison</a>
                    <a href="?view=ai" target="_self">EquityLens AI</a>
                    <a href="?view=filings" target="_self">SEC Filings</a>
                    <a href="?view=learn" target="_self">Learn</a>
                </div>
            </details>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if current_view == "home":
    featured_key = "Snowflake (SNOW)" if "Snowflake (SNOW)" in company_data else next(iter(company_data))
    featured_data = company_data[featured_key]
    featured_name = featured_key.split(" (")[0]
    featured_ticker = featured_data.get("ticker", "")
    featured_history = featured_data.get("history", [])
    featured_prior_revenue = (
        featured_history[-2].get("revenue")
        if len(featured_history) >= 2
        else None
    )
    featured_growth = calc_growth(featured_data.get("revenue"), featured_prior_revenue)
    featured_margin = calc_margin(
        featured_data.get("operating_income"),
        featured_data.get("revenue")
    )
    featured_cash = featured_data.get("capital_structure", {}).get("cash_and_investments")
    featured_source = featured_data.get("filing_url", "")
    featured_form = featured_data.get("source", "SEC filing")
    featured_fy = featured_data.get("fiscal_year", "")
    featured_analysis = company_analysis.get(featured_key, {})
    featured_industry_label = (
        "Cloud data platform"
        if featured_ticker == "SNOW"
        else featured_data.get("industry", "Public company")
    )

    st.markdown(
        """
        <section class="el-page-section el-grid-bg el-hero">
            <div class="el-hero-kicker"><span class="el-hero-dot"></span>Public-markets research, made legible</div>
            <h1 class="el-hero-title">
                Understand public<br>companies.<br>
                <span class="muted-line">Without digging<br>through hundreds of<br>pages.</span>
            </h1>
            <p class="el-hero-copy">
                EquityLens organizes financial performance, company strategy, risk disclosures,
                business models, and SEC filings into structured research while keeping the
                original sources visible.
            </p>
            <div class="el-hero-actions">
                <a class="el-hero-btn primary" href="?view=explore" target="_self">Explore companies &nbsp; →</a>
                <a class="el-hero-btn" href="?view=compare" target="_self">Compare an industry</a>
            </div>
            <div class="el-motto">EquityLens informs. You decide.</div>
        </section>
        <div class="el-trust-row">
            <div class="el-trust-point"><span class="el-trust-check">✓</span>SEC EDGAR sourced</div>
            <div class="el-trust-point"><span class="el-trust-check">✓</span>Calculations shown</div>
            <div class="el-trust-point"><span class="el-trust-check">✓</span>Direct filing links</div>
            <div class="el-trust-point"><span class="el-trust-check">✓</span>No investment recommendations</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <section class="el-page-section el-grid-bg el-record-wrap" id="research-record">
            <div class="el-research-record">
                <div class="el-record-head">
                    <span>Research record · {featured_ticker}</span>
                    <span class="el-source-pill">SEC EDGAR</span>
                </div>
                <div class="el-record-body">
                    <div class="el-record-title-row">
                        <div>
                            <h2 class="el-record-title">{featured_name} Inc.</h2>
                            <div class="el-record-subtitle">{featured_industry_label}</div>
                        </div>
                        <span class="el-period-badge">FY{featured_fy}</span>
                    </div>
                    <div class="el-metric-grid">
                        <div class="el-metric-cell">
                            <div class="el-metric-label">Revenue</div>
                            <div class="el-metric-value">{format_money(featured_data.get("revenue"))}</div>
                        </div>
                        <div class="el-metric-cell">
                            <div class="el-metric-label">YoY Growth</div>
                            <div class="el-metric-value teal">{pct(featured_growth)}</div>
                        </div>
                        <div class="el-metric-cell">
                            <div class="el-metric-label">Operating Margin</div>
                            <div class="el-metric-value">{pct(featured_margin)}</div>
                        </div>
                        <div class="el-metric-cell">
                            <div class="el-metric-label">Cash + Investments</div>
                            <div class="el-metric-value">{format_money(featured_cash)}</div>
                        </div>
                    </div>
                    <div class="el-record-source">
                        <div class="el-record-source-row">
                            <span class="reported">Reported information</span>
                            <span>Company {featured_form}</span>
                        </div>
                        <div class="el-validation-line"></div>
                        <div class="el-validation-note">Validated against the structured EquityLens filing record · reporting period FY{featured_fy}</div>
                        <a class="el-record-link" href="{featured_source}" target="_blank">
                            <span>Latest supporting SEC filing · {featured_form}</span><span>→</span>
                        </a>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <section class="el-page-section">
            <div class="el-eyebrow">The research workflow</div>
            <h2 class="el-section-heading">From primary source to useful context.</h2>
            <p class="el-section-copy">A structured path through company disclosures, not a black-box investment score.</p>
            <div class="el-workflow-grid">
                <div class="el-workflow-card">
                    <div class="el-workflow-top"><span>01</span><span class="el-workflow-icon">▧</span></div>
                    <div class="el-workflow-title">Source</div>
                    <div class="el-workflow-copy">Original SEC filings and company disclosures.</div>
                </div>
                <div class="el-workflow-card">
                    <div class="el-workflow-top"><span>02</span><span class="el-workflow-icon">▱</span></div>
                    <div class="el-workflow-title">Structure</div>
                    <div class="el-workflow-copy">Reported facts organized into consistent research categories.</div>
                </div>
                <div class="el-workflow-card">
                    <div class="el-workflow-top"><span>03</span><span class="el-workflow-icon">◉</span></div>
                    <div class="el-workflow-title">Understand</div>
                    <div class="el-workflow-copy">Trends, economics, risks, and business context.</div>
                </div>
                <div class="el-workflow-card">
                    <div class="el-workflow-top"><span>04</span><span class="el-workflow-icon">⚖</span></div>
                    <div class="el-workflow-title">Compare</div>
                    <div class="el-workflow-copy">Period-aware views across relevant peers.</div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )

    prior_margin = None
    if len(featured_history) >= 2:
        prior_margin = calc_margin(
            featured_history[-2].get("operating_income"),
            featured_history[-2].get("revenue")
        )

    if featured_growth is not None and featured_margin is not None and prior_margin is not None:
        margin_direction = "improved" if featured_margin > prior_margin else "declined"
        ai_example_answer = (
            f"Revenue changed {featured_growth:+.1f}% from the prior fiscal year, while the "
            f"GAAP operating margin {margin_direction} from {prior_margin:.1f}% to "
            f"{featured_margin:.1f}%. The company remained "
            + ("unprofitable" if featured_margin < 0 else "profitable")
            + " on a GAAP operating basis for the period."
        )
    else:
        ai_example_answer = (
            "EquityLens can explain changes in reported performance using the structured "
            "financial and filing context available for the selected company."
        )

    st.markdown(
        f"""
        <section class="el-page-section">
            <div class="el-ai-intro">
                <div class="el-eyebrow">EquityLens AI</div>
                <h2 class="el-section-heading">Ask the filing,<br>not the internet.</h2>
                <p class="el-section-copy">
                    Ask questions against structured company and filing research. Explore performance,
                    disclosed risks, business models, and changes across reporting periods with the
                    sources close at hand.
                </p>
                <div class="el-hero-actions">
                    <a class="el-hero-btn" href="?view=ai" target="_self">Open research assistant &nbsp; →</a>
                </div>
            </div>
            <div class="el-ai-question-card">
                <div class="el-ai-q-head">
                    <div class="el-mini-logo">EL</div>
                    <div>
                        <div class="el-ai-q-title">Why did operating margin change?</div>
                        <div class="el-ai-q-meta">{featured_name} · FY{featured_fy}</div>
                    </div>
                </div>
                <div class="el-ai-answer">{ai_example_answer}</div>
                <div class="el-source-tags">
                    <span class="el-source-tag">{featured_form}</span>
                    <span class="el-source-tag">Income statements</span>
                </div>
                <div class="el-ai-trust-grid">
                    <div class="el-ai-trust">Filing-grounded</div>
                    <div class="el-ai-trust">Source-linked</div>
                    <div class="el-ai-trust">Follow-up questions</div>
                    <div class="el-ai-trust">No stock rankings</div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <section class="el-page-section">
            <div class="el-eyebrow">Interactive preview</div>
            <h2 class="el-section-heading">See the research, not just the promise.</h2>
            <p class="el-section-copy">Choose a covered company to preview its latest standardized snapshot.</p>
        </section>
        """,
        unsafe_allow_html=True
    )

    preview_control = st.container()
    with preview_control:
        control_cols = st.columns(2)
        with control_cols[0]:
            home_industry = st.selectbox(
                "Industry",
                industries,
                index=(industries.index("Cloud & Data Infrastructure Software")
                       if "Cloud & Data Infrastructure Software" in industries else 0),
                key="home_industry"
            )

        home_industry_companies = [
            name for name, company in company_data.items()
            if company.get("industry", "Unclassified") == home_industry
        ]

        default_company_index = (
            home_industry_companies.index("Snowflake (SNOW)")
            if "Snowflake (SNOW)" in home_industry_companies
            else 0
        )

        with control_cols[1]:
            home_company = st.selectbox(
                "Company",
                home_industry_companies,
                index=default_company_index,
                format_func=lambda name: f"{company_data[name].get('ticker', '')} · {name.split(' (')[0]}",
                key="home_company"
            )

    home_data = company_data[home_company]
    home_qdata = company_quarterly.get(home_company, {})
    home_qm = quarterly_metrics(home_qdata)
    home_latest = home_qdata.get("latest_quarter", {})
    home_ticker = home_data.get("ticker", "")
    home_name = home_company.split(" (")[0]
    home_history = home_data.get("history", [])
    home_prior_revenue = home_history[-2].get("revenue") if len(home_history) >= 2 else None
    home_growth = (
        home_qm.get("yoy_growth")
        if home_latest.get("revenue") is not None
        else calc_growth(home_data.get("revenue"), home_prior_revenue)
    )
    home_revenue = (
        home_latest.get("revenue")
        if home_latest.get("revenue") is not None
        else home_data.get("revenue")
    )
    home_margin = (
        home_qm.get("operating_margin")
        if home_latest.get("revenue") is not None
        else calc_margin(home_data.get("operating_income"), home_data.get("revenue"))
    )
    home_cash = home_data.get("capital_structure", {}).get("cash_and_investments")
    home_source = home_qdata.get("source_filing") or home_data.get("filing_url", "")
    home_period = (
        home_qdata.get("quarter_label")
        if home_latest.get("revenue") is not None
        else f"FY{home_data.get('fiscal_year', '')}"
    )
    home_form = home_data.get("source", "SEC filing")

    st.markdown(
        f"""
        <section class="el-page-section" style="padding-top:28px;">
            <div class="el-research-record">
                <div class="el-record-head">
                    <span>Research record · {home_ticker}</span>
                    <span class="el-source-pill">SEC EDGAR</span>
                </div>
                <div class="el-record-body">
                    <div class="el-record-title-row">
                        <div>
                            <h2 class="el-record-title">{home_name}</h2>
                            <div class="el-record-subtitle">{home_data.get('industry', '')}</div>
                        </div>
                        <span class="el-period-badge">{home_period}</span>
                    </div>
                    <div class="el-metric-grid">
                        <div class="el-metric-cell"><div class="el-metric-label">Revenue</div><div class="el-metric-value">{format_money(home_revenue)}</div></div>
                        <div class="el-metric-cell"><div class="el-metric-label">YoY Growth</div><div class="el-metric-value teal">{pct(home_growth)}</div></div>
                        <div class="el-metric-cell"><div class="el-metric-label">Operating Margin</div><div class="el-metric-value">{pct(home_margin)}</div></div>
                        <div class="el-metric-cell"><div class="el-metric-label">Cash + Investments</div><div class="el-metric-value">{format_money(home_cash)}</div></div>
                    </div>
                    <a class="el-record-link" href="{home_source}" target="_blank">
                        <span>Latest supporting SEC filing · {home_form}</span><span>→</span>
                    </a>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )

if current_view == "compare":
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

if current_view == "explore":
    section("Explore Companies", "Read the Company Through Its S-1")

    st.caption(
        "This view is intentionally focused on the company's S-1 or IPO registration materials. "
        "It does not mix in later 10-K or 10-Q results, so the historical IPO story stays separate from current performance."
    )

    explore_industry = st.selectbox(
        "Industry",
        industries,
        key="explore_s1_industry"
    )

    explore_companies = [
        name for name, company in company_data.items()
        if company.get("industry", "Unclassified") == explore_industry
    ]

    explore_company = st.selectbox(
        "Company",
        explore_companies,
        format_func=lambda name: (
            f"{company_data[name].get('ticker', '')} · {name.split(' (')[0]}"
        ),
        key="explore_s1_company"
    )

    explore_data = company_data.get(explore_company, {})
    explore_s1 = company_s1.get(explore_company, {})
    explore_ticker = explore_data.get("ticker", "")
    explore_name = explore_company.split(" (")[0]

    st.markdown(
        f"""
        <div class="el-company-hero">
            <div class="el-kicker">{explore_ticker} · {explore_data.get('industry', '')}</div>
            <div class="el-company-title">{explore_name}</div>
            <p class="el-subtitle">
                Historical IPO research based on the company's S-1 registration materials.
            </p>
            <div class="el-badges">
                <span class="el-badge">{explore_s1.get('form', 'S-1')}</span>
                <span class="el-badge">SEC EDGAR source</span>
                <span class="el-badge">Historical filing context</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if explore_s1:
        meta_left, meta_right = st.columns(2)
        with meta_left:
            st.markdown("**Registration form**")
            st.write(explore_s1.get("form", "S-1"))
        with meta_right:
            st.markdown("**Filed**")
            st.write(explore_s1.get("filed_date", "N/A"))

        section("Company Story", "How the Company Described Itself")
        st.write(explore_s1.get("historical_context", "No S-1 summary is available yet."))

        section("Research Guide", "What to Look for in the S-1")
        st.write(explore_s1.get("what_to_learn", "No research guide is available yet."))

        section("S-1 Detail Map", "What the Filing Covers")
        detail_cols = st.columns(2)

        with detail_cols[0]:
            with st.expander("Business & Revenue Model", expanded=True):
                st.markdown("Focus on how the company describes its products or services, who pays for them, how revenue is generated, whether revenue is recurring or usage-based, and which products or customer relationships management considered most important at the time.")
                filing_points = explore_s1.get("filing_details", {}).get("business_revenue_model", [])
                if filing_points:
                    st.markdown("**From this company's S-1**")
                    for point in filing_points:
                        st.markdown(f"- {point}")

            with st.expander("Customers & Go-to-Market"):
                st.markdown("Review the customer base, target market, sales motion, distribution channels, customer concentration, expansion strategy, retention language, and any reliance on partners or resellers described in the filing.")
                filing_points = explore_s1.get("filing_details", {}).get("customers_go_to_market", [])
                if filing_points:
                    st.markdown("**From this company's S-1**")
                    for point in filing_points:
                        st.markdown(f"- {point}")

            with st.expander("Growth Strategy & Market Opportunity"):
                st.markdown("Look for management's stated growth priorities, new-product plans, geographic expansion, market-size discussion, customer expansion strategy, and the assumptions behind the opportunity the company presented to public investors.")
                filing_points = explore_s1.get("filing_details", {}).get("growth_market_opportunity", [])
                if filing_points:
                    st.markdown("**From this company's S-1**")
                    for point in filing_points:
                        st.markdown(f"- {point}")

            with st.expander("Competition & Differentiation"):
                st.markdown("The S-1 usually explains the competitive landscape, alternative products or technologies, larger incumbent competitors, and the capabilities management believed differentiated the company at the time of the offering.")
                filing_points = explore_s1.get("filing_details", {}).get("competition_differentiation", [])
                if filing_points:
                    st.markdown("**From this company's S-1**")
                    for point in filing_points:
                        st.markdown(f"- {point}")

        with detail_cols[1]:
            with st.expander("Risk Factors", expanded=True):
                st.markdown("Risk Factors can include dependence on growth, customer retention, large customers, suppliers or cloud providers, cybersecurity, regulation, international operations, competition, losses, stock-based compensation, and other company-specific exposures. EquityLens treats these as disclosed risks, not predictions.")
                filing_points = explore_s1.get("filing_details", {}).get("risk_factors", [])
                if filing_points:
                    st.markdown("**From this company's S-1**")
                    for point in filing_points:
                        st.markdown(f"- {point}")

            with st.expander("Financial Condition & Operating History"):
                st.markdown("Review historical revenue, gross profit, operating expenses, net income or loss, cash flow, accumulated deficit, and management's discussion of the factors that affected results before the IPO.")
                filing_points = explore_s1.get("filing_details", {}).get("financial_history", [])
                if filing_points:
                    st.markdown("**From this company's S-1**")
                    for point in filing_points:
                        st.markdown(f"- {point}")

            with st.expander("IPO Structure, Capitalization & Dilution"):
                st.markdown("Registration filings can describe the shares being offered, existing capitalization, preferred-stock conversion, dilution, voting rights, and how ownership changes when the company becomes public. Final pricing may appear in later amendments rather than the first S-1.")
                filing_points = explore_s1.get("filing_details", {}).get("ipo_capitalization_dilution", [])
                if filing_points:
                    st.markdown("**From this company's S-1**")
                    for point in filing_points:
                        st.markdown(f"- {point}")

            with st.expander("Use of Proceeds, Management & Ownership"):
                st.markdown("Look for how the company expected to use offering proceeds, executive and director information, compensation disclosures, related-party matters, and principal stockholders. These sections help explain governance and ownership around the IPO.")
                filing_points = explore_s1.get("filing_details", {}).get("proceeds_management_ownership", [])
                if filing_points:
                    st.markdown("**From this company's S-1**")
                    for point in filing_points:
                        st.markdown(f"- {point}")

        st.caption(
            "The exact level of detail varies by company and filing amendment. EquityLens uses the original SEC filing as the primary source."
        )

        section("How to Read It", "Questions to Keep in Mind")
        st.markdown(
            """
            - **Business model:** What product or service did the company say it sells, and how does it make money?
            - **Growth strategy:** How did management describe the path to adding customers, products, or markets?
            - **Market opportunity:** What market did the company believe it was addressing at the time of the IPO?
            - **Competitive position:** Which alternatives, technologies, or competitors did the filing identify?
            - **Risk factors:** What could materially affect the business, operations, or ability to grow?
            - **Economics:** What did the filing reveal about revenue mix, costs, profitability, and capital needs?
            """
        )

        section("EquityLens AI", "Generate an S-1 Research Brief")
        st.caption(
            "This AI brief is grounded only in the S-1 research currently stored for this company. "
            "It is historical filing analysis, not an investment recommendation."
        )

        if get_openai_client() is None:
            st.info(
                "The AI feature is built into EquityLens but is not active until OPENAI_API_KEY is added to Streamlit Secrets."
            )
        else:
            if st.button(
                "Generate AI S-1 brief",
                key=f"generate_s1_ai_{explore_ticker}",
                use_container_width=True
            ):
                with st.spinner("Reviewing the S-1 research context..."):
                    try:
                        st.session_state[f"s1_ai_brief_{explore_ticker}"] = equitylens_s1_ai_brief(explore_company)
                    except Exception as exc:
                        st.error("EquityLens AI could not generate the S-1 brief.")
                        st.caption(str(exc))

            generated_brief = st.session_state.get(f"s1_ai_brief_{explore_ticker}")
            if generated_brief:
                st.markdown(
                    '<div class="el-ai-panel"><div class="el-ai-kicker">Generated research brief</div></div>',
                    unsafe_allow_html=True
                )
                st.markdown(generated_brief)

        if explore_s1.get("source_url"):
            st.link_button(
                "Open original S-1 on SEC EDGAR",
                explore_s1.get("source_url"),
                key=f"explore_s1_source_{explore_ticker}"
            )

        st.info(
            "S-1 filings are historical documents. This tab explains the company's IPO-era story rather than its current financial condition. "
            "Use the original SEC filing for full detail, and use Industry Comparison and Filings for later-period research."
        )
    else:
        st.info("S-1 research has not been added for this company yet.")


if current_view == "ai":
    section("Grounded AI research assistant", "Ask EquityLens AI")

    st.write(
        "Ask questions in plain English about a covered company. The assistant is grounded in "
        "EquityLens structured financial data, filing-based research, and SEC source links."
    )
    st.caption(
        "It can explain results, compare periods, summarize risks, and answer follow-up questions. "
        "It does not provide buy, sell, hold, ranking, or personalized investment recommendations."
    )

    ask_industry = st.selectbox(
        "Industry",
        industries,
        key="ai_chat_industry"
    )

    ask_industry_companies = [
        name for name, company in company_data.items()
        if company.get("industry", "Unclassified") == ask_industry
    ]

    ask_company = st.selectbox(
        "Research company",
        ask_industry_companies,
        format_func=lambda name: (
            f"{company_data[name].get('ticker', '')} · {name.split(' (')[0]}"
        ),
        key="ai_chat_company"
    )

    st.caption(
        f"Researching {company_data[ask_company].get('ticker', '')} in {ask_industry}."
    )

    openai_client_available = get_openai_client() is not None
    if not openai_client_available:
        st.warning(
            "AI chat is ready but not yet connected. Add OPENAI_API_KEY to Streamlit Secrets "
            "to activate the grounded assistant."
        )

    if "equitylens_chat_history" not in st.session_state:
        st.session_state.equitylens_chat_history = {}

    if ask_company not in st.session_state.equitylens_chat_history:
        st.session_state.equitylens_chat_history[ask_company] = []

    chat_history = st.session_state.equitylens_chat_history[ask_company]

    starter_cols = st.columns(3)
    starter_questions = [
        "What changed in the latest quarter?",
        "What are the main disclosed risks?",
        "Explain the profitability trend."
    ]

    for col, starter in zip(starter_cols, starter_questions):
        with col:
            if st.button(starter, key=f"starter_{ask_company}_{starter}", use_container_width=True):
                st.session_state.ai_starter_question = starter

    for message in chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                sources = equitylens_source_links(ask_company)
                if sources:
                    with st.expander("Source links"):
                        for idx, (label, url) in enumerate(sources):
                            st.link_button(
                                label,
                                url,
                                key=f"history_source_{ask_company}_{len(chat_history)}_{idx}_{message.get('id', idx)}"
                            )

    prompt = st.chat_input(
        "Ask about financial performance, filings, risks, business model, or trends..."
    )

    starter_prompt = st.session_state.pop("ai_starter_question", None)
    user_prompt = prompt or starter_prompt

    if user_prompt:
        chat_history.append({
            "role": "user",
            "content": user_prompt
        })

        with st.chat_message("user"):
            st.markdown(user_prompt)

        if not openai_client_available:
            with st.chat_message("assistant"):
                st.info(
                    "The AI connection is not configured yet. Once OPENAI_API_KEY is added to "
                    "Streamlit Secrets, this question can be answered from EquityLens data."
                )
        else:
            with st.chat_message("assistant"):
                with st.spinner("Reviewing EquityLens data and filing context..."):
                    try:
                        answer = equitylens_ai_answer(ask_company, chat_history)
                        st.markdown(answer)

                        assistant_message = {
                            "role": "assistant",
                            "content": answer,
                            "id": len(chat_history)
                        }
                        chat_history.append(assistant_message)

                        sources = equitylens_source_links(ask_company)
                        if sources:
                            with st.expander("Source links"):
                                for idx, (label, url) in enumerate(sources):
                                    st.link_button(
                                        label,
                                        url,
                                        key=f"new_source_{ask_company}_{len(chat_history)}_{idx}"
                                    )
                    except Exception as exc:
                        st.error(
                            "EquityLens AI could not complete the request. The underlying research "
                            "data is still available elsewhere in the app."
                        )
                        st.caption(str(exc))

    control_cols = st.columns([1, 4])
    with control_cols[0]:
        if st.button("Clear chat", key=f"clear_chat_{ask_company}", use_container_width=True):
            st.session_state.equitylens_chat_history[ask_company] = []
            st.rerun()

    st.caption(
        "AI responses are generated from the structured EquityLens context supplied to the model. "
        "Users should verify material information using the linked SEC filings."
    )

if current_view == "filings":
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


if current_view == "learn":
    section("Learning", "Understand the Numbers")
    st.write(
        "EquityLens is designed for users who are still learning how to read public-company information. "
        "The goal is to explain what a metric measures, show the reported or calculated value, and make the original source easy to inspect."
    )

    learning_items = [
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
        "view expressed in a video, and the videos should not be treated as personalized investment advice."
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
    <section class="el-page-section el-evidence">
        <div>
            <div class="el-evidence-title">Evidence first. Judgment stays with you.</div>
            <div class="el-evidence-copy">Source it. Show the math. Show the date. Show the uncertainty.</div>
        </div>
        <div class="el-evidence-note"><span class="el-evidence-shield">♢</span>Research assistance, never investment advice</div>
    </section>
    <footer class="el-page-section el-footer">
        <div class="el-footer-grid">
            <div>
                <div class="el-footer-brandline">
                    <span class="el-logo-mark"><i></i><i></i><i></i></span>
                    <span>EquityLens <strong>AI</strong></span>
                </div>
                <div class="el-footer-motto">EquityLens informs. You decide.</div>
                <div class="el-footer-links">
                    <a href="?view=learn" target="_self">Methodology</a>
                    <a href="#equitylens-disclosures">Disclosures</a>
                </div>
            </div>
            <div class="el-footer-copy" id="equitylens-disclosures">
                EquityLens AI is an educational and research tool that analyzes publicly available
                financial information. It does not provide personalized investment advice,
                investment recommendations, rankings, or guarantees of future performance.
                EquityLens is an independent project and is not affiliated with or endorsed by
                covered public companies, exchanges, brokers, or similarly named organizations.
                Financial information may be delayed, incomplete, or affected by later SEC filings
                or restatements. Verify material information using the original linked disclosures.
            </div>
        </div>
        <div class="el-footer-details">
            <details>
                <summary>Methodology</summary>
                <p>Source priority: SEC EDGAR filings first, company investor-relations disclosures second,
                and appropriately licensed market-data providers where needed. EquityLens distinguishes
                reported figures from calculations and keeps reporting periods visible.</p>
            </details>
            <details>
                <summary>Source labels</summary>
                <p><strong>Reported</strong> means taken from a filing or company disclosure.
                <strong>Calculated by EquityLens</strong> means derived from reported figures.
                <strong>Research summary</strong> is explanatory context and is not an investment recommendation.</p>
            </details>
        </div>
        <div class="el-footer-bottom">© 2026 Keya Dhanani. All rights reserved.</div>
    </footer>
    """,
    unsafe_allow_html=True
)
