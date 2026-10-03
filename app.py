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
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

    :root {
        --el-font: "IBM Plex Sans", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
        /* Follow Streamlit's active System / Light / Dark theme automatically. */
        --el-bg: var(--background-color);
        --el-surface: var(--secondary-background-color);
        --el-surface-2: color-mix(
            in srgb,
            var(--secondary-background-color) 82%,
            var(--background-color)
        );
        --el-border: color-mix(in srgb, var(--text-color) 16%, transparent);
        --el-text: var(--text-color);
        --el-muted: color-mix(in srgb, var(--text-color) 62%, transparent);
        --el-teal: #14B8A6;
        --el-blue: #3B82F6;
        --el-gold: #D99A13;
        --el-green: #16A34A;
        --el-red: #DC2626;
    }

    html, body, .stApp {
        font-family: var(--el-font);
    }

    /* Preserve Streamlit's icon font. Applying the app font to every descendant
       turns Material Symbol ligatures into literal text such as "double_arrow_right". */
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

    .stApp {
        font-size: 0.98rem;
        line-height: 1.55;
        background:
            radial-gradient(
                circle at 10% 0%,
                color-mix(in srgb, var(--el-teal) 8%, transparent),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 10%,
                color-mix(in srgb, var(--el-blue) 8%, transparent),
                transparent 30%
            ),
            var(--el-bg);
        color: var(--el-text);
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.8rem;
        padding-bottom: 4rem;
    }

    .el-hero {
        padding: 2rem 2.2rem;
        border: 1px solid var(--el-border);
        border-radius: 10px;
        background: linear-gradient(135deg, var(--el-surface), var(--el-surface-2));
        box-shadow: 0 20px 60px rgba(0,0,0,0.22);
        margin-bottom: 1.4rem;
    }

    .el-company-hero {
        padding: 1.6rem 1.8rem;
        border: 1px solid var(--el-border);
        border-radius: 10px;
        background: linear-gradient(135deg, var(--el-surface-2), var(--el-surface));
        margin: 0.8rem 0 1.3rem 0;
    }

    .el-kicker {
        color: var(--el-teal);
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.10em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }

    .el-title {
        font-size: clamp(2.2rem, 5vw, 4.2rem);
        line-height: 0.98;
        font-weight: 700;
        letter-spacing: -0.025em;
        color: var(--el-text);
        margin: 0 0 0.8rem 0;
    }

    .el-title span { color: var(--el-teal); }

    .el-company-title {
        font-size: clamp(1.8rem, 4vw, 3rem);
        line-height: 1.05;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--el-text);
        margin-bottom: 0.5rem;
    }

    .el-subtitle {
        max-width: 900px;
        font-size: 1.02rem;
        line-height: 1.65;
        color: color-mix(in srgb, var(--el-text) 82%, transparent);
        margin: 0;
    }

    .el-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 1.1rem;
    }

    .el-badge {
        padding: 0.42rem 0.7rem;
        border-radius: 8px;
        border: 1px solid var(--el-border);
        background: color-mix(in srgb, var(--el-text) 5%, transparent);
        color: color-mix(in srgb, var(--el-text) 78%, transparent);
        font-size: 0.78rem;
        font-weight: 600;
    }

    .el-section {
        margin-top: 1.65rem;
        margin-bottom: 0.55rem;
    }

    .el-section-label {
        color: var(--el-teal);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.74rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .el-section-title {
        font-size: 1.65rem;
        font-weight: 700;
        color: var(--el-text);
        letter-spacing: -0.02em;
        margin: 0;
    }

    .el-summary-card, .el-change-card, .el-risk-card {
        border: 1px solid var(--el-border);
        border-radius: 12px;
        background: linear-gradient(180deg, var(--el-surface-2), var(--el-surface));
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
    }

    .el-summary-card {
        min-height: 145px;
        padding: 1.2rem 1.3rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .el-summary-label {
        color: var(--el-muted);
        font-size: 0.88rem;
        font-weight: 600;
        margin-bottom: 0.55rem;
    }

    .el-summary-value {
        color: var(--el-text);
        font-size: 1.7rem;
        line-height: 1.2;
        font-weight: 700;
        letter-spacing: -0.015em;
        overflow-wrap: anywhere;
    }

    .el-change-card, .el-risk-card {
        padding: 1rem 1.1rem;
        margin: 0.6rem 0;
    }

    .el-change-title, .el-risk-title {
        color: var(--el-text);
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }

    .el-change-copy {
        color: color-mix(in srgb, var(--el-text) 88%, transparent);
        line-height: 1.55;
        margin: 0;
    }

    .el-risk-list {
        margin: 0;
        padding-left: 1.1rem;
        color: color-mix(in srgb, var(--el-text) 88%, transparent);
        line-height: 1.5;
    }

    .el-risk-list li { margin: 0.25rem 0; }

    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, var(--el-surface-2), var(--el-surface));
        border: 1px solid var(--el-border);
        border-radius: 12px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.14);
    }

    div[data-testid="stMetricLabel"] { color: var(--el-muted); }
    div[data-testid="stMetricValue"] { color: var(--el-text); font-weight: 750; }

    .stButton > button {
        min-height: 3rem;
        border-radius: 8px;
        border: 1px solid rgba(45, 212, 191, 0.35);
        background: linear-gradient(135deg, #13B8A6, #2F7FEA);
        color: white;
        font-weight: 700;
        padding: 0.7rem 1.35rem;
        box-shadow: 0 10px 28px rgba(47,127,234,0.18);
    }

    .stButton > button:hover {
        border-color: rgba(45, 212, 191, 0.75);
        filter: brightness(1.05);
        color: white;
    }

    div[data-baseweb="select"] > div {
        background: var(--el-surface);
        border-color: var(--el-border);
        border-radius: 8px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--el-border);
        border-radius: 10px;
        overflow: hidden;
        background: color-mix(in srgb, var(--el-surface) 88%, transparent);
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--el-border);
        border-radius: 10px;
        background: color-mix(in srgb, var(--el-surface) 82%, transparent);
    }

    div[data-testid="stAlert"] { border-radius: 14px; }

    hr {
        border-color: color-mix(in srgb, var(--el-text) 12%, transparent) !important;
        margin: 1.8rem 0 !important;
    }

    .stCaption, small { color: var(--el-muted) !important; }

    h1, h2, h3, h4, h5, h6,
    [data-testid="stHeadingWithActionElements"] {
        font-family: var(--el-font) !important;
        font-weight: 700 !important;
        letter-spacing: -0.018em;
    }

    p, li, label, input, textarea, button,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-baseweb="tab"] {
        font-family: var(--el-font) !important;
    }

    [data-baseweb="tab"] {
        font-weight: 600 !important;
        letter-spacing: 0.005em;
    }

    .stButton > button,
    .stLinkButton > a {
        font-weight: 600 !important;
        letter-spacing: 0.005em;
    }


    .el-product-hero {
        position: relative;
        overflow: hidden;
        padding: clamp(2rem, 5vw, 4.3rem);
        border: 1px solid var(--el-border);
        border-radius: 18px;
        background:
            linear-gradient(135deg,
                color-mix(in srgb, var(--el-surface) 98%, transparent),
                color-mix(in srgb, var(--el-surface-2) 94%, transparent));
        box-shadow: 0 22px 65px rgba(0,0,0,0.15);
        margin-bottom: 1.2rem;
        isolation: isolate;
    }

    .el-product-hero::before {
        content: "";
        position: absolute;
        inset: 0;
        z-index: -2;
        pointer-events: none;
        background:
            linear-gradient(
                90deg,
                transparent 0%,
                transparent 58%,
                color-mix(in srgb, var(--el-teal) 4%, transparent) 58%,
                transparent 100%
            ),
            repeating-linear-gradient(
                0deg,
                transparent 0 27px,
                color-mix(in srgb, var(--el-text) 5%, transparent) 27px 28px
            );
        mask-image: linear-gradient(90deg, transparent 0%, transparent 48%, black 76%, black 100%);
        -webkit-mask-image: linear-gradient(90deg, transparent 0%, transparent 48%, black 76%, black 100%);
        opacity: .75;
    }

    .el-product-hero::after {
        content: "";
        position: absolute;
        right: -6%;
        top: -30%;
        width: 46%;
        height: 150%;
        z-index: -1;
        pointer-events: none;
        background:
            radial-gradient(
                circle at 42% 40%,
                color-mix(in srgb, var(--el-blue) 12%, transparent) 0%,
                transparent 48%
            ),
            radial-gradient(
                circle at 72% 66%,
                color-mix(in srgb, var(--el-teal) 10%, transparent) 0%,
                transparent 44%
            );
        filter: blur(8px);
        opacity: .85;
    }

    .el-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: .45rem;
        padding: .38rem .68rem;
        border-radius: 7px;
        border: 1px solid color-mix(in srgb, var(--el-teal) 38%, transparent);
        background: color-mix(in srgb, var(--el-teal) 9%, transparent);
        color: var(--el-teal);
        font-size: .76rem;
        font-weight: 600;
        letter-spacing: .07em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    .el-product-title {
        max-width: 980px;
        margin: 0;
        font-size: clamp(2.6rem, 6vw, 4.7rem);
        line-height: 1.0;
        letter-spacing: -.035em;
        font-weight: 700;
        color: var(--el-text);
    }

    .el-product-title span {
        background: linear-gradient(90deg, var(--el-teal), var(--el-blue));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    .el-product-subtitle {
        max-width: 800px;
        margin: 1.2rem 0 0 0;
        font-size: clamp(1rem, 2vw, 1.18rem);
        line-height: 1.65;
        color: color-mix(in srgb, var(--el-text) 76%, transparent);
    }

    .el-trust-strip {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: .85rem;
        margin: 1.05rem 0 1.5rem 0;
    }

    .el-trust-item {
        min-height: 72px;
        box-sizing: border-box;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem 1.1rem;
        text-align: center;
        font-size: .86rem;
        font-weight: 600;
        color: var(--el-text) !important;
        border: 1px solid rgba(71, 163, 155, .72) !important;
        border-radius: 12px !important;
        background: rgba(18, 27, 33, .72) !important;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.025),
            0 10px 28px rgba(0,0,0,.12) !important;
        transition: transform .18s ease, border-color .18s ease, background .18s ease;
    }

    .el-trust-item:hover {
        transform: translateY(-2px);
        border-color: rgba(45, 212, 191, .95) !important;
        background: rgba(20, 184, 166, .08) !important;
    }

    .el-feature-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: .9rem;
        margin: .8rem 0 1.2rem 0;
    }

    .el-feature-card {
        min-height: 188px;
        padding: 1.5rem;
        border: 1px solid rgba(148, 163, 184, .18);
        border-radius: 14px;
        background:
            linear-gradient(180deg,
                rgba(255,255,255,.025),
                rgba(255,255,255,.008));
        box-shadow: 0 16px 42px rgba(0,0,0,.08);
        transition: transform .2s ease, border-color .2s ease;
    }

    .el-feature-card:hover {
        transform: translateY(-3px);
        border-color: rgba(45, 212, 191, .48);
    }

    .el-feature-num {
        color: var(--el-teal);
        font-size: .76rem;
        font-weight: 600;
        letter-spacing: .08em;
        text-transform: uppercase;
    }

    .el-feature-title {
        margin-top: .5rem;
        color: var(--el-text);
        font-size: 1.12rem;
        font-weight: 700;
    }

    .el-feature-copy {
        margin-top: .45rem;
        color: color-mix(in srgb, var(--el-text) 72%, transparent);
        line-height: 1.55;
        font-size: .92rem;
    }

    .el-company-card {
        min-height: 150px;
        padding: 1.15rem;
        border: 1px solid var(--el-border);
        border-radius: 12px;
        background: color-mix(in srgb, var(--el-surface) 92%, transparent);
        box-shadow: 0 10px 30px rgba(0,0,0,.08);
    }

    .el-company-card-ticker {
        color: var(--el-teal);
        font-size: .78rem;
        font-weight: 600;
        letter-spacing: .08em;
    }

    .el-company-card-name {
        margin-top: .25rem;
        color: var(--el-text);
        font-size: 1.08rem;
        font-weight: 700;
    }

    .el-company-card-meta {
        margin-top: .55rem;
        color: var(--el-muted);
        font-size: .84rem;
        line-height: 1.45;
    }

    .el-answer-card {
        padding: 1.2rem 1.3rem;
        border: 1px solid color-mix(in srgb, var(--el-teal) 28%, var(--el-border));
        border-radius: 12px;
        background:
            linear-gradient(135deg,
                color-mix(in srgb, var(--el-teal) 7%, var(--el-surface)),
                color-mix(in srgb, var(--el-blue) 5%, var(--el-surface)));
        margin: .8rem 0;
    }

    .el-answer-kicker {
        color: var(--el-teal);
        font-size: .76rem;
        font-weight: 600;
        letter-spacing: .09em;
        text-transform: uppercase;
        margin-bottom: .4rem;
    }

    .el-answer-copy {
        color: color-mix(in srgb, var(--el-text) 88%, transparent);
        line-height: 1.65;
        margin: 0;
    }

    /* Editorial-style navigation, inspired by modern institutional research products. */
    .stTabs [data-baseweb="tab-list"] {
        gap: .35rem;
        border-bottom: 1px solid rgba(148, 163, 184, .14);
        padding-bottom: .15rem;
    }

    .stTabs [data-baseweb="tab"] {
        min-height: 2.9rem;
        padding: 0 1rem;
        border-radius: 9px 9px 0 0;
        color: var(--el-muted);
    }

    .stTabs [aria-selected="true"] {
        color: var(--el-text) !important;
        background: rgba(20, 184, 166, .055);
    }

    .el-workflow-shell {
        position: relative;
        overflow: hidden;
        margin: .9rem 0 1.8rem 0;
        padding: 1.65rem;
        border: 1px solid rgba(148, 163, 184, .16);
        border-radius: 16px;
        background:
            radial-gradient(circle at 86% 18%, rgba(59,130,246,.09), transparent 28%),
            linear-gradient(180deg, rgba(255,255,255,.018), rgba(255,255,255,.004));
    }

    .el-workflow-shell::before {
        content: "";
        position: absolute;
        inset: 0;
        pointer-events: none;
        background-image:
            linear-gradient(rgba(148,163,184,.045) 1px, transparent 1px),
            linear-gradient(90deg, rgba(148,163,184,.045) 1px, transparent 1px);
        background-size: 34px 34px;
        mask-image: linear-gradient(90deg, transparent 0%, black 45%, black 100%);
        -webkit-mask-image: linear-gradient(90deg, transparent 0%, black 45%, black 100%);
    }

    .el-workflow-kicker {
        position: relative;
        z-index: 1;
        color: var(--el-teal);
        text-transform: uppercase;
        letter-spacing: .11em;
        font-size: .72rem;
        font-weight: 700;
        margin-bottom: .45rem;
    }

    .el-workflow-title {
        position: relative;
        z-index: 1;
        color: var(--el-text);
        font-size: 1.45rem;
        font-weight: 700;
        letter-spacing: -.018em;
        margin-bottom: 1.15rem;
    }

    .el-workflow-grid {
        position: relative;
        z-index: 1;
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: .8rem;
    }

    .el-workflow-step {
        position: relative;
        min-height: 132px;
        padding: 1.1rem;
        border: 1px solid rgba(148, 163, 184, .17);
        border-radius: 12px;
        background: rgba(10, 15, 20, .34);
    }

    .el-workflow-step + .el-workflow-step::before {
        content: "→";
        position: absolute;
        left: -.72rem;
        top: 50%;
        transform: translateY(-50%);
        color: rgba(45,212,191,.8);
        font-size: 1.05rem;
        font-weight: 700;
    }

    .el-workflow-num {
        color: var(--el-teal);
        font-size: .7rem;
        font-weight: 700;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: .5rem;
    }

    .el-workflow-step-title {
        color: var(--el-text);
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: .35rem;
    }

    .el-workflow-copy {
        color: var(--el-muted);
        font-size: .84rem;
        line-height: 1.5;
    }

    @media (max-width: 900px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
            padding-bottom: 2.5rem;
        }

        .el-product-hero {
            padding: 1.4rem 1.15rem;
            border-radius: 12px;
        }
.el-product-title {
            font-size: clamp(2rem, 10vw, 3rem);
            line-height: 1.04;
            letter-spacing: -0.025em;
        }

        .el-product-subtitle {
            font-size: 0.96rem;
            line-height: 1.55;
        }

        .el-badges {
            gap: .4rem;
        }

        .el-badge {
            font-size: .72rem;
            padding: .34rem .5rem;
        }

        .el-trust-strip {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: .45rem;
            margin: .75rem 0 1rem 0;
        }

        .el-trust-item {
            padding: .65rem .55rem;
            font-size: .76rem;
            line-height: 1.35;
        }

        .el-feature-grid {
            grid-template-columns: 1fr;
            gap: .6rem;
        }

        .el-workflow-grid {
            grid-template-columns: 1fr;
        }

        .el-workflow-step + .el-workflow-step::before {
            content: "↓";
            left: 50%;
            top: -.75rem;
            transform: translateX(-50%);
        }

        .el-workflow-shell {
            padding: 1.15rem;
        }

        .el-feature-card {
            min-height: 0;
            padding: 1rem;
        }

        .el-summary-card {
            min-height: 88px;
            padding: .85rem 1rem;
        }

        .el-summary-label {
            margin-bottom: .25rem;
            font-size: .78rem;
        }

        .el-summary-value {
            font-size: 1.35rem;
        }

        .el-company-hero {
            padding: 1.15rem;
            margin: .6rem 0 1rem 0;
        }

        .el-company-title {
            font-size: 1.7rem;
        }

        .el-company-card {
            min-height: 0;
            padding: 1rem;
        }

        .el-section {
            margin-top: 1.2rem;
        }

        .el-section-title {
            font-size: 1.35rem;
        }

        div[data-testid="stExpander"] summary {
            min-height: 3rem;
        }

        div[data-testid="stMetric"] {
            padding: .8rem .9rem;
        }
    }

    footer { visibility: hidden; }
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
    ]
}

st.markdown(
    """
    <div class="el-product-hero">
        <div class="el-eyebrow">EquityLens AI · Public-company research</div>
        <h1 class="el-product-title">Understand public companies.<br><span>Without digging through hundreds of pages.</span></h1>
        <p class="el-product-subtitle">
            Explore financial performance, business models, risks, and SEC filings in one place.
            EquityLens turns dense company disclosures into structured research while keeping the
            underlying source visible. EquityLens informs. You decide.
        </p>
        <div class="el-badges">
            <span class="el-badge">SEC EDGAR sourced</span>
            <span class="el-badge">Calculations shown</span>
            <span class="el-badge">Direct filing links</span>
            <span class="el-badge">No investment recommendations</span>
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


render_summary_cards([
    ("Companies", str(len(company_data))),
    ("Industries", str(len(industries))),
    ("Primary Source", "SEC EDGAR"),
    ("Monitoring", "Automatic SEC checks")
])

home_tab, company_tab, peer_tab, ask_tab, sec_tracker_tab, learn_tab = st.tabs([
    "Home",
    "Explore Companies",
    "Industry Comparison",
    "Ask EquityLens",
    "Filings",
    "Learn"
])

with home_tab:
    st.info(
        "New to financial statements? Start in Learn. Want to understand a company at IPO? Open Explore Companies. "
        "Comparing competitors? Open Industry Comparison."
    )

    section("Start here", "Research a company in seconds")

    home_industry = st.selectbox(
        "Choose industry",
        industries,
        key="home_industry"
    )

    home_industry_companies = [
        name for name, company in company_data.items()
        if company.get("industry", "Unclassified") == home_industry
    ]

    st.caption(
        f"{len(home_industry_companies)} covered compan"
        f"{'y' if len(home_industry_companies) == 1 else 'ies'} in {home_industry}."
    )

    home_company = st.selectbox(
        "Choose company",
        home_industry_companies,
        format_func=lambda name: (
            f"{company_data[name].get('ticker', '')} · {name.split(' (')[0]}"
        ),
        key="home_company"
    )

    home_data = company_data[home_company]
    home_analysis = company_analysis.get(home_company, {})
    home_qdata = company_quarterly.get(home_company, {})
    home_qm = quarterly_metrics(home_qdata)
    home_latest = home_qdata.get("latest_quarter", {})
    home_ticker = home_data.get("ticker", "")
    home_name = home_company.split(" (")[0]

    st.markdown(
        f"""
        <div class="el-company-hero">
            <div class="el-kicker">{home_ticker} · {home_data.get('industry', 'Unclassified')}</div>
            <div class="el-company-title">{home_name}</div>
            <p class="el-subtitle">{home_analysis.get('business_model', 'Company research is being prepared.')}</p>
            <div class="el-badges">
                <span class="el-badge">{home_qdata.get('quarter_label', 'Latest quarter')}</span>
                <span class="el-badge">{home_data.get('source', 'SEC filing')} sourced</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    home_metrics = st.columns(4)
    home_metrics[0].metric("Quarter Revenue", format_money(home_latest.get("revenue")))
    home_metrics[1].metric("YoY Growth", pct(home_qm.get("yoy_growth")))
    home_metrics[2].metric("Operating Margin", pct(home_qm.get("operating_margin")))
    home_metrics[3].metric(
        "Cash + Investments",
        format_money(home_data.get("capital_structure", {}).get("cash_and_investments"))
    )

    source_url = home_qdata.get("source_filing") or home_data.get("filing_url")
    if source_url:
        st.link_button("Open latest supporting SEC filing", source_url)

    st.caption(
        "Continue in Explore Companies for an S-1-focused view of how the company described its business, "
        "strategy, market opportunity, and risks when it prepared to go public."
    )

    st.markdown(
        """
        <div class="el-workflow-shell">
            <div class="el-workflow-kicker">Research workflow</div>
            <div class="el-workflow-title">From filing to understanding</div>
            <div class="el-workflow-grid">
                <div class="el-workflow-step">
                    <div class="el-workflow-num">01 · Source</div>
                    <div class="el-workflow-step-title">Start with primary filings</div>
                    <div class="el-workflow-copy">EquityLens anchors company research to SEC EDGAR filings and direct source links.</div>
                </div>
                <div class="el-workflow-step">
                    <div class="el-workflow-num">02 · Structure</div>
                    <div class="el-workflow-step-title">Turn disclosure into usable research</div>
                    <div class="el-workflow-copy">Reported figures, calculated metrics, business-model context, and risk disclosures are organized consistently.</div>
                </div>
                <div class="el-workflow-step">
                    <div class="el-workflow-num">03 · Compare</div>
                    <div class="el-workflow-step-title">Understand the company in context</div>
                    <div class="el-workflow-copy">Review trends and peers without rankings, recommendations, or hidden scoring.</div>
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
    featured_companies = home_industry_companies[:6]
    featured_cols = st.columns(3)
    for idx, featured_company in enumerate(featured_companies):
        featured_data = company_data[featured_company]
        featured_q = company_quarterly.get(featured_company, {})
        featured_qm = quarterly_metrics(featured_q)
        with featured_cols[idx % 3]:
            st.markdown(
                f"""
                <div class="el-company-card">
                    <div class="el-company-card-ticker">{featured_data.get('ticker', '')}</div>
                    <div class="el-company-card-name">{featured_company.split(' (')[0]}</div>
                    <div class="el-company-card-meta">
                        {featured_data.get('industry', 'Unclassified')}<br>
                        Latest revenue growth: {pct(featured_qm.get('yoy_growth'))}<br>
                        Latest filing period: {featured_q.get('period_end', 'N/A')}
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


with ask_tab:
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


with learn_tab:
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

st.markdown("---")
section("Methodology", "Data Sources")
st.markdown(
    """
    **Source priority**

    1. SEC EDGAR filings, including Forms 10-K, 10-Q, 8-K, and S-1
    2. Company investor-relations materials and company-reported disclosures
    3. Market-data providers only where the relevant licensing and exchange permissions allow use

    EquityLens distinguishes company-reported figures from metrics calculated inside the app. Material figures should include a reporting period and a link to the original source whenever available.
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

