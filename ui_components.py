from contextlib import contextmanager
import pandas as pd
import streamlit as st


def section(label, title):
    st.markdown(
        f"""
        <div class="el-section">
            <div class="el-section-label">{label}</div>
            <div class="el-section-title">{title}</div>
        </div>
        """,
        unsafe_allow_html=True,
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
                unsafe_allow_html=True,
            )


def format_utc_timestamp(value, fallback="Unavailable"):
    if not value:
        return fallback
    parsed = pd.to_datetime(
        value,
        errors="coerce",
        utc=True,
    )
    if pd.isna(parsed):
        return str(value)
    return parsed.strftime(
        "%Y-%m-%d %H:%M UTC"
    )


@contextmanager
def loading_panel(label, detail=""):
    """Show a branded, descriptive loading placeholder during slow operations."""
    placeholder = st.empty()
    detail_html = (
        f'<div class="el-loading-detail">{detail}</div>'
        if detail else ""
    )
    placeholder.markdown(
        f"""
        <div class="el-loading-panel" role="status" aria-live="polite">
            <div class="el-loading-dot"></div>
            <div>
                <div class="el-loading-label">{label}</div>
                {detail_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    try:
        yield
    finally:
        placeholder.empty()


def render_refresh_indicator(label, timestamp, detail=""):
    """Render a compact source-freshness indicator without overstating recency."""
    formatted = format_utc_timestamp(
        timestamp,
        fallback="Unavailable",
    )
    detail_text = f" · {detail}" if detail else ""
    st.markdown(
        f"""
        <div class="el-refresh-indicator">
            <span class="el-refresh-dot"></span>
            <strong>{label}:</strong>
            <span>{formatted}{detail_text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
