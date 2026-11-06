import re

import streamlit as st

from ui_components import section


def render_learn():
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

    path_terms = {
        "Start Here": {
            "Revenue",
            "Year-over-Year (YoY) Growth",
            "Operating Margin",
            "Net Income",
            "10-K",
            "10-Q",
        },
        "Financial Statements": {
            "Revenue",
            "Year-over-Year (YoY) Growth",
            "Gross Margin",
            "Operating Margin",
            "Net Income",
            "LTM / Trailing Twelve Months",
            "Cash + Investments",
            "Debt",
        },
        "SEC Filings": {
            "S-1 Registration Statement",
            "8-K Current Report",
            "10-K",
            "10-Q",
        },
        "Research a Business": {
            "S-1 Registration Statement",
            "10-K",
            "10-Q",
            "Revenue",
            "Operating Margin",
            "Cash + Investments",
            "Debt",
        },
        "Markets & Rates": {
            "Consumer Price Index (CPI)",
            "Producer Price Index (PPI)",
            "Employment Situation",
            "JOLTS",
            "Employment Cost Index (ECI)",
            "10-Year Treasury Yield",
            "SOFR",
            "Interest-Rate Swap",
        },
        "All Concepts": None,
    }

    path_descriptions = {
        "Start Here": (
            "Build the minimum vocabulary needed to open a company page and understand "
            "the basic financial and filing context."
        ),
        "Financial Statements": (
            "Learn how revenue, margins, profitability, liquidity, and debt fit together."
        ),
        "SEC Filings": (
            "Learn what the major SEC forms are and where each one fits in a research process."
        ),
        "Research a Business": (
            "Use filings and financial statements together to understand the business model, "
            "growth, profitability, balance sheet, and risks."
        ),
        "Markets & Rates": (
            "Understand the macro and rates indicators shown in Market Monitor without treating "
            "a single release as a market forecast."
        ),
        "All Concepts": (
            "Browse every concept currently included in the EquityLens learning library."
        ),
    }

    path_steps = {
        "Start Here": [
            "Understand what revenue measures.",
            "Learn the difference between growth and profitability.",
            "Know what a 10-K and 10-Q are.",
            "Open a Company Research page and verify one number in the original filing.",
        ],
        "Financial Statements": [
            "Start with revenue and comparable-period growth.",
            "Read gross margin and operating margin together.",
            "Check whether net income is positive or negative.",
            "Review cash, investments, and debt before judging financial flexibility.",
        ],
        "SEC Filings": [
            "Use the 10-K for the annual business, risk, and audited financial picture.",
            "Use the 10-Q for the latest quarterly financial and risk updates.",
            "Use 8-K for specified material events between periodic reports.",
            "Use S-1/F-1/S-11 for registration-era business, ownership, and offering context.",
        ],
        "Research a Business": [
            "Understand what the company sells and who pays.",
            "Identify the primary revenue engine.",
            "Measure growth and operating profitability.",
            "Review liquidity, debt, and major disclosed risks.",
            "Compare peers, then verify conclusions in primary filings.",
        ],
        "Markets & Rates": [
            "Separate inflation, labor, and interest-rate indicators.",
            "Read the observation period before comparing releases.",
            "Distinguish Treasury yields, SOFR, and swap rates.",
            "Use macro data as context, not as an automatic explanation for every market move.",
        ],
        "All Concepts": [
            "Choose any concept below and use the source link when one is available.",
        ],
    }

    learning_path = st.radio(
        "Learning path",
        list(path_terms),
        horizontal=True,
        key="learning_path",
    )
    st.markdown(f"### {learning_path}")
    st.write(path_descriptions[learning_path])

    step_cols = st.columns(
        min(len(path_steps[learning_path]), 4)
    )
    for index, step in enumerate(
        path_steps[learning_path],
        start=1,
    ):
        with step_cols[(index - 1) % len(step_cols)]:
            st.markdown(f"**{index}**")
            st.caption(step)

    selected_terms = path_terms[learning_path]
    display_items = (
        learning_items
        if selected_terms is None
        else [
            item
            for item in learning_items
            if item["term"] in selected_terms
        ]
    )

    st.markdown("### Concepts in this path")

    for item in display_items:
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

