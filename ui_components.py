from contextlib import contextmanager
import streamlit as st

from formatting import format_utc_timestamp


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
