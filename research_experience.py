"""Educational, no-login UX components for EquityLens.

These components only display existing research and public SEC evidence.
They do not generate investment recommendations or require user accounts.
"""

from __future__ import annotations

import csv
import html
import io
from datetime import datetime, timezone
from urllib.parse import urlparse

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import simpleSplit
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

SOURCE_UNAVAILABLE = "Structured research is still being added for this company."


def _clean(value, fallback="Not yet available"):
    text = str(value or "").strip()
    return text if text and text.lower() not in {"none", "nan", "n/a"} else fallback


def _safe_sec_url(value):
    """Only link to official SEC HTTPS resources in exported reports."""
    url = str(value or "").strip()
    parsed = urlparse(url)
    if parsed.scheme == "https" and parsed.hostname in {"sec.gov", "www.sec.gov"}:
        return url
    return ""


def inject_readability_styles(st):
    st.markdown(
        """
        <style>
        /* A refinement layer, not a redesign of the existing sections. */
        .el-readability-intro {
            padding: 1.05rem 1.3rem; margin: .8rem 0 1.2rem;
            border: 1px solid var(--el-border);
            border-left: 3px solid var(--el-teal);
            background: var(--el-surface); border-radius: 9px;
        }
        .el-readability-intro strong { color: var(--el-text); font-size: 1.05rem; }
        .el-readability-intro p { color: var(--el-muted); margin: .35rem 0 0; }
        .el-quicklabel { font-size: .76rem; color: var(--el-muted);
                         letter-spacing: .035em; text-transform: uppercase; }
        .el-evidence-card {
            border: 1px solid var(--el-border); background: var(--el-surface);
            padding: 1.15rem 1.25rem; border-radius: 9px;
            min-height: 100%; line-height: 1.6;
        }
        .el-evidence-card h4 { margin: 0 0 .55rem; font-size: 1.02rem; }
        .el-evidence-card p { color: var(--el-muted); margin: .3rem 0; }
        .el-topic-chip {
            display: inline-block; padding: .32rem .58rem;
            margin: .22rem .22rem .22rem 0;
            border: 1px solid var(--el-border); border-radius: 6px;
            color: var(--el-text); font-size: .79rem;
            background: var(--el-surface-2);
        }
        .el-positive { border-top: 2px solid #16C7B2; }
        .el-caution { border-top: 2px solid #E4B96D; }
        .el-readable-section { margin-top: 1.5rem; margin-bottom: .6rem; }
        .el-readable-section h3 { font-size: 1.18rem; margin: 0 0 .25rem; }
        .el-readable-section p { color: var(--el-muted); margin: 0; }
        .el-footnote { font-size: .82rem; color: var(--el-muted); }
        @media(max-width: 760px) {
            .el-readability-intro { padding: .9rem 1rem; }
            .el-evidence-card { min-height: 0; padding: 1rem; }
            .el-readable-section { margin-top: 1.1rem; }
            .el-readability-intro p { line-height: 1.55; }
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                min-width: 0 !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _filer_timeline(filings, maximum=6):
    usable = [
        row for row in (filings or [])
        if isinstance(row, dict) and row.get("filing_date")
    ]
    usable.sort(key=lambda row: (str(row.get("filing_date", "")),
                                 str(row.get("acceptance_datetime", ""))), reverse=True)
    return usable[:maximum]


def _analysis_sources(analysis, filings):
    sources = []
    candidate = _safe_sec_url((analysis or {}).get("source_filing"))
    if candidate:
        sources.append(("Source for structured research", candidate))
    for row in _filer_timeline(filings, 5):
        url = _safe_sec_url(row.get("url"))
        if url and url not in {item[1] for item in sources}:
            sources.append((
                "%s filed %s" % (_clean(row.get("form"), "SEC filing"),
                                 _clean(row.get("filing_date"), "date unknown")),
                url,
            ))
    return sources[:6]


def render_home_discovery(st, universe, open_company_research, sec_filings):
    """Guided first interaction without replacing the original landing page."""
    st.markdown(
        '<div class="el-readability-intro"><strong>Start with a question, not a spreadsheet.</strong>'
        '<p>Search a U.S. public company to see its business model, financial trends, '
        'SEC filings, and questions worth investigating. Open access, no account required.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.55, 1], gap="large")
    with left:
        search = st.text_input(
            "Find a company",
            placeholder="Try Apple, AAPL, Microsoft, or MSFT",
            key="home_company_lookup",
            help="Find a company in the covered market universe. All research is free.",
        ).strip()
        if search:
            tickers = universe["Ticker"].fillna("").astype(str)
            companies = universe["Company"].fillna("").astype(str)
            matching = universe[
                tickers.str.contains(search, case=False, regex=False)
                | companies.str.contains(search, case=False, regex=False)
            ].head(5)
            if matching.empty:
                st.caption("No matches in the current coverage list. Try a company name or ticker.")
            else:
                for _, row in matching.iterrows():
                    ticker = str(row.get("Ticker", "")).upper().strip()
                    company = str(row.get("Company", ticker))
                    if ticker:
                        st.button(
                            "%s · %s" % (ticker, company),
                            key="home_lookup_%s" % ticker,
                            on_click=open_company_research,
                            args=(ticker,),
                            use_container_width=True,
                        )
        else:
            st.caption("Examples to explore")
            examples = [
                (ticker, name) for ticker, name in [
                    ("AAPL", "Apple"), ("MSFT", "Microsoft"), ("NVDA", "NVIDIA"),
                ] if (universe["Ticker"].fillna("").astype(str).str.upper() == ticker).any()
            ]
            example_cols = st.columns(max(1, len(examples)))
            for col, (ticker, label) in zip(example_cols, examples):
                with col:
                    st.button(
                        label, key="home_example_%s" % ticker,
                        on_click=open_company_research, args=(ticker,),
                        use_container_width=True,
                    )
    with right:
        total = len(universe)
        synced = sum(
            bool(value.get("cik") and value.get("filings"))
            for value in sec_filings.values() if isinstance(value, dict)
        )
        st.markdown(
            '<div class="el-evidence-card">'
            '<div class="el-quicklabel">Research coverage</div>'
            '<h4>%s public companies</h4>'
            '<p>%s with available SEC filing records.</p>'
            '<p>Coverage does not imply that every company has a completed deep-dive.</p>'
            '</div>' % (f"{total:,}", f"{synced:,}"),
            unsafe_allow_html=True,
        )
    st.caption("Educational research only. No sign-in, subscription, paywall, or personalized investment recommendations.")


def _watchlist_store(st):
    return st.session_state.setdefault("education_watchlist", [])


def toggle_watchlist(st, ticker):
    items = _watchlist_store(st)
    if ticker in items:
        items.remove(ticker)
    else:
        items.append(ticker)


def render_watchlist(st, company_data, open_company_research):
    """Session-only watchlist. Download CSV to retain it across visits."""
    items = _watchlist_store(st)
    with st.expander("My research list · %d companies (this visit)" % len(items),
                     expanded=bool(items)):
        st.caption(
            "Save companies while exploring. This list is stored only for this visit; "
            "no account or personal data collection is required. Export a CSV to keep it."
        )
        if not items:
            st.caption("Open a company and select 'Save to my research list' to start.")
            return
        names = {}
        for key, value in company_data.items():
            ticker = str(value.get("ticker", "")).upper().strip()
            if ticker:
                names[ticker] = key.split(" (")[0]
        for ticker in list(items):
            st.button(
                "%s · %s" % (ticker, names.get(ticker, ticker)),
                key="watchlist_open_%s" % ticker,
                on_click=open_company_research,
                args=(ticker,),
                use_container_width=True,
            )
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Ticker", "Company"])
        for ticker in items:
            writer.writerow([ticker, names.get(ticker, ticker)])
        st.download_button(
            "Export research list as CSV",
            data=buffer.getvalue(),
            file_name="equitylens_research_list.csv",
            mime="text/csv",
            key="export_education_watchlist",
        )


def _compact_dollars(value):
    """Human-readable amount; preserve negatives and avoid fabricated zeros."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "Not available"
    if value != value or value in (float("inf"), float("-inf")):
        return "Not available"
    sign = "-" if value < 0 else ""
    magnitude = abs(value)
    if magnitude >= 1_000_000_000:
        return "%s$%.2fB" % (sign, magnitude / 1_000_000_000)
    if magnitude >= 1_000_000:
        return "%s$%.1fM" % (sign, magnitude / 1_000_000)
    return "%s$%s" % (sign, f"{magnitude:,.0f}")


def render_quarterly_comparison(st, quarterly):
    """Show actual reported current vs year-ago quarterly values when present.

    No metrics are synthesized for companies missing structured quarter data.
    """
    if not isinstance(quarterly, dict):
        return
    current = quarterly.get("latest_quarter") or {}
    year_ago = quarterly.get("prior_year_quarter") or {}
    if not current or not year_ago:
        return

    rows = [
        ("Revenue", "revenue"),
        ("Operating income", "operating_income"),
        ("Net income", "net_income"),
    ]
    available = [
        (label, key) for label, key in rows
        if current.get(key) is not None and year_ago.get(key) is not None
    ]
    if not available:
        return

    period = _clean(quarterly.get("quarter_label"), "latest reported quarter")
    st.markdown(
        '<div class="el-readable-section"><h3>What changed this quarter?</h3>'
        '<p>Reported figures from %s compared with the year-ago quarter. '
        'Review the financial statements for the full calculation and context.</p></div>'
        % html.escape(period),
        unsafe_allow_html=True,
    )
    cols = st.columns(len(available))
    for col, (label, key) in zip(cols, available):
        current_value = current[key]
        prior_value = year_ago[key]
        try:
            difference = float(current_value) - float(prior_value)
            delta = "%s YoY" % _compact_dollars(difference)
        except (TypeError, ValueError):
            delta = None
        with col:
            st.metric(
                label,
                _compact_dollars(current_value),
                delta=delta,
                delta_color="off",  # Profit/loss changes are not investment signals.
                help="Difference from the same quarter one year earlier.",
            )
    sec_url = _safe_sec_url(quarterly.get("source_filing"))
    if sec_url:
        st.markdown("[Verify these figures in the original filing](%s)" % sec_url)
    st.caption(
        "A year-over-year comparison is not a forecast, rating, or investment recommendation. "
        "Unavailable figures are not interpreted as zero."
    )


def render_company_evidence(st, ticker, analysis, filings, growth_label, period_label):
    """Balanced research prompts with named disclosure evidence, not model guesses."""
    analysis = analysis or {}
    filings = filings or []
    latest = _filer_timeline(filings, 1)
    st.markdown(
        '<div class="el-readable-section"><h3>Build a balanced research view</h3>'
        '<p>Potential strengths and risks to investigate, not buy or sell signals. '
        'Statements below come from existing research fields and source documents.</p></div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns(2, gap="medium")
    revenue_source = _clean(analysis.get("primary_revenue_source"), "")
    model = _clean(analysis.get("business_model"), "")
    risk = _clean(analysis.get("competitive_risk"), "")
    operational = _clean(analysis.get("operational_risk"), "")
    with left:
        st.markdown(
            '<div class="el-evidence-card el-positive"><h4>Growth lens · evidence to check</h4>'
            '<p>What drives sales, and could those drivers persist?</p></div>',
            unsafe_allow_html=True,
        )
        if revenue_source:
            st.markdown("**Revenue driver**")
            st.write(revenue_source)
        elif model:
            st.markdown("**Business model**")
            st.write(model)
        else:
            st.caption(SOURCE_UNAVAILABLE)
        st.caption("Reported growth: %s · Period: %s" % (
            _clean(growth_label), _clean(period_label)))
        st.caption("Check Financials for the calculation basis and reporting period.")
    with right:
        st.markdown(
            '<div class="el-evidence-card el-caution"><h4>Risk lens · evidence to check</h4>'
            '<p>What assumptions could fail or limit future performance?</p></div>',
            unsafe_allow_html=True,
        )
        if risk:
            st.markdown("**Competitive risk**")
            st.write(risk)
        if operational:
            st.markdown("**Operational risk**")
            st.write(operational)
        if not risk and not operational:
            st.caption("Detailed risk research is still being added. Verify the Risk Factors section of the 10-K.")
    themes = analysis.get("key_risk_themes", []) or []
    themes = [str(theme) for theme in themes if str(theme).strip()][:6]
    if themes:
        st.markdown("**Disclosed risk themes to investigate**")
        st.markdown(
            "".join('<span class="el-topic-chip">%s</span>' % html.escape(topic)
                    for topic in themes),
            unsafe_allow_html=True,
        )
    sources = _analysis_sources(analysis, filings)
    if sources:
        st.caption("Evidence and primary sources")
        for label, url in sources[:3]:
            st.markdown("[%s](%s)" % (label, url))
    if latest:
        last = latest[0]
        st.caption(
            "Newest filing in this source feed: %s · %s. "
            "Source dates and report completion dates can differ."
            % (_clean(last.get("form")), _clean(last.get("filing_date")))
        )


def build_research_pdf(company_name, ticker, industry, sector, analysis,
                       filings, metric_labels):
    """Produce a concise, source-linked educational brief from known data."""
    analysis = analysis or {}
    metrics = metric_labels or {}
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, leftMargin=44, rightMargin=44,
        topMargin=43, bottomMargin=45,
        title="EquityLens Research Brief - %s" % ticker,
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ELHeading", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=12, spaceBefore=14, spaceAfter=6, textColor=colors.HexColor("#143E48"),
    ))
    styles.add(ParagraphStyle(
        name="ELBody", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=9.5, leading=14, spaceAfter=6, alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="ELSmall", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=8, leading=11, textColor=colors.HexColor("#46555A"), spaceAfter=4,
    ))
    def safe(text):
        return html.escape(str(text or ""), quote=True)
    def add(label, value, style="ELBody"):
        story.append(Paragraph("<b>%s:</b> %s" % (safe(label), safe(value)), styles[style]))

    story = [
        Paragraph("EQUITYLENS | COMPANY RESEARCH", styles["ELSmall"]),
        Paragraph(safe(company_name), styles["Title"]),
        Paragraph(safe("%s · %s · %s" % (ticker, sector or "Sector unavailable",
                                      industry or "Industry unavailable")), styles["ELSmall"]),
        Spacer(1, 7), HRFlowable(width="100%", thickness=1, color=colors.HexColor("#D7E2E3")),
        Spacer(1, 10),
    ]
    for title, field in [("Company overview", "business_model"),
                         ("Primary revenue source", "primary_revenue_source")]:
        story.append(Paragraph(title, styles["ELHeading"]))
        story.append(Paragraph(safe(_clean(analysis.get(field), SOURCE_UNAVAILABLE)), styles["ELBody"]))
    story.append(Paragraph("Financial snapshot", styles["ELHeading"]))
    for label, value in metrics.items():
        add(label, value)
    story.append(Paragraph("Growth questions / bull lens", styles["ELHeading"]))
    story.append(Paragraph(
        "Investigate whether reported revenue trends and the business model are durable. "
        "This is an educational research prompt, not a positive investment rating.",
        styles["ELBody"],
    ))
    story.append(Paragraph("Counterarguments / bear lens", styles["ELHeading"]))
    for label, field in [("Competitive risk", "competitive_risk"),
                         ("Operational risk", "operational_risk")]:
        add(label, _clean(analysis.get(field), SOURCE_UNAVAILABLE))
    themes = analysis.get("key_risk_themes", []) or []
    if themes:
        add("Risk themes", ", ".join(str(item) for item in themes[:8]))
    story.append(Paragraph("Recent SEC filings and sources", styles["ELHeading"]))
    sources = _analysis_sources(analysis, filings)
    if sources:
        for label, url in sources:
            story.append(Paragraph(
                "%s — <link href=\"%s\" color=\"#126876\">Open source at SEC.gov</link>" %
                (safe(label), safe(url)), styles["ELBody"],
            ))
    else:
        story.append(Paragraph("No verified filing links available in this report.", styles["ELBody"]))
    story.extend([
        Spacer(1, 14), HRFlowable(width="100%", thickness=.6,
                                  color=colors.HexColor("#D7E2E3")),
        Spacer(1, 8),
        Paragraph(
            "Generated from available public data on %s UTC. Financial and market data may "
            "be delayed or incomplete. Verify every material claim using the original "
            "filing. Free educational research only; not investment advice." %
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
            styles["ELSmall"],
        ),
    ])
    doc.build(story)
    return buffer.getvalue()


def render_report_download(st, company_name, ticker, industry, sector,
                           analysis, filings, metrics):
    st.markdown(
        '<div class="el-readable-section"><h3>Keep researching</h3>'
        '<p>Export a brief with the available disclosures, analysis and original SEC links. '
        'The complete interactive workspace remains below.</p></div>',
        unsafe_allow_html=True,
    )
    pdf_bytes = build_research_pdf(
        company_name, ticker, industry, sector, analysis, filings, metrics,
    )
    st.download_button(
        "Download free research brief (PDF)",
        data=pdf_bytes,
        file_name="EquityLens_%s_research.pdf" % "".join(c for c in ticker if c.isalnum()),
        mime="application/pdf",
        key="research_pdf_%s" % ticker,
        use_container_width=True,
    )
    st.caption(
        "This summary exports currently available information, not every underlying "
        "financial statement. Use the full Company Research tabs for complete detail."
    )
