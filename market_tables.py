"""Crisp, accessible HTML tables for the EquityLens Market Monitor.

Unlike canvas-rendered dataframe grids, native text stays sharp on mobile
displays and table cells stack with labels rather than shrinking to fit.
All cell text and link attributes are escaped before HTML rendering.
"""
from __future__ import annotations

import html
import math
from urllib.parse import urlsplit


def _text(value):
    if value is None:
        return "—"
    try:
        if isinstance(value, float) and math.isnan(value):
            return "—"
    except (ValueError, TypeError):
        pass
    return str(value)


def _safe_link(value):
    url = str(value or "").strip()
    parsed = urlsplit(url)
    if parsed.scheme not in {"https", "http"} or not parsed.hostname:
        return ""
    return url


def table_markup(dataframe, *, link_columns=(), link_label="Open source"):
    """Render all rows without truncation. No vendor or data-source rewriting."""
    columns = [str(value) for value in dataframe.columns]
    safe_headers = "".join(
        "<th scope='col'>%s</th>" % html.escape(name)
        for name in columns
    )
    body = []
    link_cols = set(link_columns)
    for row in dataframe.itertuples(index=False, name=None):
        cells = []
        for label, value in zip(columns, row):
            display = _text(value)
            if label in link_cols and _safe_link(display):
                href = html.escape(display, quote=True)
                content = (
                    '<a href="%s" target="_blank" rel="noopener noreferrer">'
                    '%s ↗</a>' % (href, html.escape(link_label))
                )
            else:
                content = html.escape(display)
            cells.append(
                '<td data-label="%s">%s</td>' %
                (html.escape(label, quote=True), content)
            )
        body.append("<tr>%s</tr>" % "".join(cells))
    if not body:
        return '<div class="el-crisp-empty">No table entries available.</div>'
    return (
        '<div class="el-crisp-scroll" role="region" '
        'aria-label="Market research data table" tabindex="0">'
        '<table class="el-crisp-table"><thead><tr>%s</tr></thead>'
        '<tbody>%s</tbody></table></div>'
        % (safe_headers, "".join(body))
    )


def render_crisp_table(st, dataframe, *, link_columns=(), link_label="Open source"):
    """A text-native alternative to canvas-backed st.dataframe for compact data."""
    st.markdown(
        """
        <style>
        .el-crisp-scroll {
            width: 100%; max-width: 100%; overflow-x: auto;
            border: 1px solid var(--el-border, #263640);
            border-radius: 9px; background: var(--el-surface, #091217);
            -webkit-overflow-scrolling: touch;
        }
        .el-crisp-table {
            width: 100%; border-collapse: collapse; border-spacing: 0;
            text-align: left; font-size: .89rem; line-height: 1.55;
            font-family: var(--el-font, "IBM Plex Sans", sans-serif);
            color: var(--el-text, #eef3f5);
        }
        .el-crisp-table th {
            padding: .82rem .85rem; font-weight: 600; white-space: nowrap;
            color: var(--el-muted, #b7c6ce);
            background: var(--el-surface-3, #111c24);
            border-bottom: 1px solid var(--el-border, #263640);
        }
        .el-crisp-table td {
            padding: .8rem .85rem; vertical-align: top;
            border-bottom: 1px solid var(--el-border-soft, #213039);
            overflow-wrap: anywhere; min-width: 0;
        }
        .el-crisp-table tr:last-child td { border-bottom: none; }
        .el-crisp-table a { color: #7dd3fc; text-decoration: underline; }
        .el-crisp-table a:focus-visible {
            outline: 2px solid #7dd3fc; outline-offset: 2px;
        }
        .el-crisp-empty { color: var(--el-muted, #b7c6ce); padding: .75rem; }
        @media (max-width: 760px) {
            .el-crisp-scroll {
                border: 0; background: transparent; overflow-x: visible;
            }
            .el-crisp-table, .el-crisp-table tbody, .el-crisp-table tr,
            .el-crisp-table td { display: block; width: 100%; }
            .el-crisp-table thead { display: none; }
            .el-crisp-table tr {
                margin: 0 0 .7rem; padding: .45rem .8rem;
                border: 1px solid var(--el-border, #263640);
                border-radius: 9px; background: var(--el-surface, #091217);
            }
            .el-crisp-table td {
                display: grid; grid-template-columns: minmax(95px, 37%) minmax(0, 1fr);
                gap: .8rem; align-items: start; padding: .48rem 0;
                font-size: .88rem; white-space: normal;
                border-bottom: 1px solid var(--el-border-soft, #213039);
            }
            .el-crisp-table td::before {
                content: attr(data-label);
                display: block; color: var(--el-muted, #b7c6ce);
                font-size: .79rem; font-weight: 600; word-break: break-word;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        table_markup(dataframe, link_columns=link_columns, link_label=link_label),
        unsafe_allow_html=True,
    )
