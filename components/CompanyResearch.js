"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

const TABS = [
  "Overview",
  "Financials",
  "Business & Risks",
  "SEC Filings",
  "IPO / Registration",
  "Ownership",
];

function money(value) {
  if (value === null || value === undefined || value === "") return "N/A";
  const number = Number(value);
  if (!Number.isFinite(number)) return "N/A";
  const abs = Math.abs(number);
  if (abs >= 1e12) return "$" + (number / 1e12).toFixed(2) + "T";
  if (abs >= 1e9) return "$" + (number / 1e9).toFixed(2) + "B";
  if (abs >= 1e6) return "$" + (number / 1e6).toFixed(1) + "M";
  return "$" + number.toLocaleString();
}

function numberFormat(value) {
  if (value === null || value === undefined || value === "") return "N/A";
  const number = Number(value);
  return Number.isFinite(number) ? number.toLocaleString() : "N/A";
}

function pct(value) {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) {
    return "N/A";
  }
  return (Number(value) * 100).toFixed(1) + "%";
}

function growth(current, prior) {
  const c = Number(current);
  const p = Number(prior);
  if (!Number.isFinite(c) || !Number.isFinite(p) || p === 0) return null;
  return c / p - 1;
}

function margin(profit, revenue) {
  const p = Number(profit);
  const r = Number(revenue);
  if (!Number.isFinite(p) || !Number.isFinite(r) || r === 0) return null;
  return p / r;
}

function filingLink(filing) {
  return filing?.url || filing?.filing_url || "";
}

function DetailList({ items }) {
  if (!items?.length) return <p className="muted">Not available in the structured research yet.</p>;
  return (
    <ul className="research-list">
      {items.map((item, index) => <li key={index}>{item}</li>)}
    </ul>
  );
}

function DataStatus({ label, available, detail }) {
  return (
    <div className={"status-chip " + (available ? "available" : "pending")}>
      <span className="status-dot" />
      <span>
        <strong>{label}</strong>
        <small>{detail}</small>
      </span>
    </div>
  );
}

export default function CompanyResearch({ company, research, companies }) {
  const router = useRouter();
  const [tab, setTab] = useState("Overview");
  const [query, setQuery] = useState("");

  const { metrics, quarterly, analysis, registration, sec, provenance } = research;
  const filings = sec?.filings || [];
  const registrationFilings = sec?.registration_filings || [];

  const latestRevenue =
    quarterly?.latest_quarter?.revenue ?? metrics?.revenue ?? null;
  const priorYearRevenue =
    quarterly?.prior_year_quarter?.revenue ??
    (metrics?.history?.length >= 2
      ? metrics.history[metrics.history.length - 2]?.revenue
      : null);

  const revenueGrowth = growth(latestRevenue, priorYearRevenue);
  const operatingMargin = margin(
    quarterly?.latest_quarter?.operating_income ?? metrics?.operating_income,
    latestRevenue
  );

  const searchResults = useMemo(() => {
    const normalized = query.toLowerCase().trim();
    if (!normalized) return [];
    return companies
      .filter((item) =>
        item.ticker.toLowerCase().includes(normalized) ||
        item.company.toLowerCase().includes(normalized) ||
        item.industry.toLowerCase().includes(normalized)
      )
      .slice(0, 8);
  }, [query, companies]);

  const availability = {
    financials: Boolean(metrics || quarterly),
    analysis: Boolean(analysis?.business_model),
    sec: Boolean(sec?.filings?.length),
    registration: Boolean(registration || registrationFilings.length),
  };

  const annualForm = filings.find((item) =>
    ["10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"].includes(item.form)
  );
  const quarterlyForm = filings.find((item) =>
    ["10-Q", "10-Q/A"].includes(item.form)
  );
  const currentForm = filings.find((item) =>
    ["8-K", "8-K/A", "6-K", "6-K/A"].includes(item.form)
  );

  const capital = metrics?.capital_structure || {};
  const filingDetails = registration?.filing_details || {};

  return (
    <main className="app-shell company-page">
      <a className="brand-link" href="/">EquityLens AI</a>

      <div className="company-search-wrap">
        <input
          className="global-search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Jump to another company or ticker…"
          aria-label="Search companies"
        />
        {query && searchResults.length > 0 && (
          <div className="search-results">
            {searchResults.map((item) => (
              <button
                key={item.ticker}
                className="search-result"
                onClick={() => router.push("/company/" + item.ticker)}
              >
                <span>{item.ticker} · {item.company}</span>
                <small>{item.industry}</small>
              </button>
            ))}
          </div>
        )}
      </div>

      <nav className="top-nav compact-nav">
        <a className="nav-item" href="/">Home</a>
        <span className="nav-item active">Company Research</span>
        <a className="nav-item" href="/#comparison">Industry Comparison</a>
        <a className="nav-item" href="/#markets">Market Monitor</a>
        <a className="nav-item" href="/#filings">Filings</a>
        <a className="nav-item" href="/#learn">Learn</a>
      </nav>

      <section className="company-hero-full">
        <div>
          <div className="section-label">{company.ticker} · {company.industry}</div>
          <h1>{company.company}</h1>
          <p>
            {company.sector}{company.country ? " · " + company.country : ""}
          </p>
        </div>
        <div className="market-snapshot">
          <span>
            <small>Market snapshot</small>
            <strong>{company.price ? "$" + company.price : "N/A"}</strong>
          </span>
          <span>
            <small>Change</small>
            <strong className={String(company.change).startsWith("-") ? "negative-text" : "positive-text"}>
              {company.change || "N/A"}
            </strong>
          </span>
          <span>
            <small>P/E</small>
            <strong>{company.pe || "N/A"}</strong>
          </span>
        </div>
      </section>

      <section className="status-grid">
        <DataStatus
          label="Financials"
          available={availability.financials}
          detail={availability.financials ? "Structured SEC metrics" : "Research pending"}
        />
        <DataStatus
          label="Business research"
          available={availability.analysis}
          detail={availability.analysis ? "Structured analysis available" : "Research pending"}
        />
        <DataStatus
          label="SEC filings"
          available={availability.sec}
          detail={availability.sec ? filings.length + " filings indexed" : "No indexed filing feed"}
        />
        <DataStatus
          label="IPO / registration"
          available={availability.registration}
          detail={availability.registration ? "Registration history available" : "No filing found / pending"}
        />
      </section>

      <section className="headline-metrics">
        <article>
          <small>{quarterly?.latest_quarter?.revenue ? "Quarter revenue" : "Fiscal-year revenue"}</small>
          <strong>{money(latestRevenue)}</strong>
          <span>{quarterly?.period_end || metrics?.fiscal_year_end || "Latest available period"}</span>
        </article>
        <article>
          <small>Revenue growth</small>
          <strong>{pct(revenueGrowth)}</strong>
          <span>Comparable prior period</span>
        </article>
        <article>
          <small>Operating margin</small>
          <strong>{pct(operatingMargin)}</strong>
          <span>Reported operating income ÷ revenue</span>
        </article>
        <article>
          <small>Cash + investments</small>
          <strong>{money(capital.cash_and_investments ?? metrics?.cash)}</strong>
          <span>{capital.balance_sheet_as_of || "Latest balance-sheet date"}</span>
        </article>
      </section>

      <div className="research-tabs">
        {TABS.map((item) => (
          <button
            key={item}
            className={tab === item ? "research-tab active" : "research-tab"}
            onClick={() => setTab(item)}
          >
            {item}
          </button>
        ))}
      </div>

      {tab === "Overview" && (
        <section className="research-panel">
          <div className="panel-grid two-col">
            <article className="research-card featured-card">
              <div className="section-label">BUSINESS MODEL</div>
              <h2>How the company makes money</h2>
              <p>{analysis?.business_model || "Structured business-model research has not been generated for this company yet."}</p>
            </article>
            <article className="research-card">
              <div className="section-label">REVENUE ENGINE</div>
              <h3>Primary revenue source</h3>
              <p>{analysis?.primary_revenue_source || "Not yet structured."}</p>
            </article>
            <article className="research-card">
              <div className="section-label">CUSTOMERS</div>
              <h3>Who buys</h3>
              <p>{analysis?.customer_type || "Not yet structured."}</p>
            </article>
            <article className="research-card">
              <div className="section-label">RECENT CONTEXT</div>
              <h3>Performance summary</h3>
              <p>{analysis?.recent_performance_summary || "Use the Financials and SEC Filings tabs for the latest reported evidence."}</p>
            </article>
          </div>

          <div className="source-note">
            Structured research source: <strong>{provenance.analysis}</strong>. Financial figures remain tied to SEC-derived records where available.
          </div>
        </section>
      )}

      {tab === "Financials" && (
        <section className="research-panel">
          <div className="section-label">FINANCIALS</div>
          <h2>Reported financial performance</h2>

          <div className="financial-table-wrap">
            <table className="financial-table">
              <thead>
                <tr>
                  <th>Period</th>
                  <th>Revenue</th>
                  <th>Gross profit</th>
                  <th>Operating income</th>
                  <th>Net income</th>
                </tr>
              </thead>
              <tbody>
                {quarterly?.latest_quarter && (
                  <tr>
                    <td>{quarterly.quarter_label || "Latest quarter"}</td>
                    <td>{money(quarterly.latest_quarter.revenue)}</td>
                    <td>{money(quarterly.latest_quarter.gross_profit)}</td>
                    <td>{money(quarterly.latest_quarter.operating_income)}</td>
                    <td>{money(quarterly.latest_quarter.net_income)}</td>
                  </tr>
                )}
                {quarterly?.ltm && (
                  <tr>
                    <td>LTM</td>
                    <td>{money(quarterly.ltm.revenue)}</td>
                    <td>{money(quarterly.ltm.gross_profit)}</td>
                    <td>{money(quarterly.ltm.operating_income)}</td>
                    <td>{money(quarterly.ltm.net_income)}</td>
                  </tr>
                )}
                {metrics && (
                  <tr>
                    <td>FY {metrics.fiscal_year || ""}</td>
                    <td>{money(metrics.revenue)}</td>
                    <td>{money(metrics.gross_profit)}</td>
                    <td>{money(metrics.operating_income)}</td>
                    <td>{money(metrics.net_income)}</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {metrics?.history?.length > 0 && (
            <>
              <div className="section-label section-spacer">ANNUAL HISTORY</div>
              <div className="history-grid">
                {metrics.history.map((year) => (
                  <article className="research-card" key={year.fiscal_year}>
                    <small>FY {year.fiscal_year}</small>
                    <strong>{money(year.revenue)}</strong>
                    <span>Revenue</span>
                    <div className="mini-separator" />
                    <span>Operating income: {money(year.operating_income)}</span>
                  </article>
                ))}
              </div>
            </>
          )}

          {(metrics?.filing_url || quarterly?.source_filing) && (
            <a
              className="source-button"
              href={quarterly?.source_filing || metrics?.filing_url}
              target="_blank"
              rel="noreferrer"
            >
              Open source SEC financial filing ↗
            </a>
          )}
        </section>
      )}

      {tab === "Business & Risks" && (
        <section className="research-panel">
          <div className="panel-grid two-col">
            {[
              ["Platform dependency", analysis?.platform_dependency],
              ["Competitive risk", analysis?.competitive_risk],
              ["Operational risk", analysis?.operational_risk],
              ["Profitability history", analysis?.profitability_history],
              ["Customer concentration", analysis?.customer_concentration],
              ["International exposure", analysis?.international_exposure],
            ].map(([label, value]) => (
              <article className="research-card" key={label}>
                <div className="section-label">{label}</div>
                <p>{value || "Not yet structured."}</p>
              </article>
            ))}
          </div>

          <article className="research-card risk-card">
            <div className="section-label">KEY RISK THEMES</div>
            <h2>What the filings tell you to watch</h2>
            <DetailList items={analysis?.key_risk_themes} />
          </article>

          {analysis?.source_filing && (
            <a className="source-button" href={analysis.source_filing} target="_blank" rel="noreferrer">
              Open source filing ↗
            </a>
          )}
        </section>
      )}

      {tab === "SEC Filings" && (
        <section className="research-panel">
          <div className="filing-summary-grid">
            {[
              ["Latest annual", annualForm],
              ["Latest quarterly", quarterlyForm],
              ["Latest current report", currentForm],
              ["Registration filings", registrationFilings.length ? { form: registrationFilings[0].form, filing_date: registrationFilings[0].filing_date } : null],
            ].map(([label, filing]) => (
              <article className="research-card" key={label}>
                <small>{label}</small>
                <strong>{filing?.form || "N/A"}</strong>
                <span>{filing?.filing_date || "Not indexed"}</span>
              </article>
            ))}
          </div>

          {filings.length > 0 ? (
            <div className="financial-table-wrap">
              <table className="financial-table">
                <thead>
                  <tr>
                    <th>Filed</th>
                    <th>Form</th>
                    <th>Report period</th>
                    <th>Description</th>
                    <th>Source</th>
                  </tr>
                </thead>
                <tbody>
                  {filings.slice(0, 25).map((filing, index) => (
                    <tr key={(filing.accession_number || filing.filing_date || "filing") + index}>
                      <td>{filing.filing_date || ""}</td>
                      <td><strong>{filing.form || ""}</strong></td>
                      <td>{filing.report_date || ""}</td>
                      <td>{filing.description || filing.primary_document || ""}</td>
                      <td>
                        {filingLink(filing) ? (
                          <a href={filingLink(filing)} target="_blank" rel="noreferrer">Open ↗</a>
                        ) : "N/A"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">No SEC filing feed is currently indexed for this ticker.</div>
          )}

          {sec?.sec_company_url && (
            <a className="source-button" href={sec.sec_company_url} target="_blank" rel="noreferrer">
              Open complete SEC company history ↗
            </a>
          )}
        </section>
      )}

      {tab === "IPO / Registration" && (
        <section className="research-panel">
          <div className="section-label">IPO / REGISTRATION RESEARCH</div>
          <h2>
            {registration?.form
              ? registration.form + " filed " + (registration.filed_date || "")
              : registrationFilings[0]?.form
                ? registrationFilings[0].form + " registration history"
                : "No structured registration filing found"}
          </h2>

          {registration ? (
            <>
              <article className="research-card featured-card">
                <h3>Historical context</h3>
                <p>{registration.historical_context || "Not yet structured."}</p>
                <div className="mini-separator" />
                <h3>What to learn from the filing</h3>
                <p>{registration.what_to_learn || "Review the original registration filing for IPO-era context."}</p>
              </article>

              <div className="panel-grid two-col">
                {[
                  ["Business & revenue model", filingDetails.business_revenue_model],
                  ["Customers & go-to-market", filingDetails.customers_go_to_market],
                  ["Growth & market opportunity", filingDetails.growth_market_opportunity],
                  ["Competition & differentiation", filingDetails.competition_differentiation],
                  ["Risk factors", filingDetails.risk_factors],
                  ["Financial history", filingDetails.financial_history],
                  ["Capitalization & dilution", filingDetails.ipo_capitalization_dilution],
                  ["Proceeds, management & ownership", filingDetails.proceeds_management_ownership],
                ].map(([label, items]) => (
                  <article className="research-card" key={label}>
                    <div className="section-label">{label}</div>
                    <DetailList items={items} />
                  </article>
                ))}
              </div>

              {registration.source_url && (
                <a className="source-button" href={registration.source_url} target="_blank" rel="noreferrer">
                  Open original {registration.form || "registration filing"} on SEC EDGAR ↗
                </a>
              )}
            </>
          ) : registrationFilings.length > 0 ? (
            <>
              <div className="empty-state">
                EquityLens has indexed the registration filing, but the structured deep-analysis record has not been generated yet.
              </div>
              <a className="source-button" href={filingLink(registrationFilings[0])} target="_blank" rel="noreferrer">
                Open {registrationFilings[0].form} on SEC EDGAR ↗
              </a>
            </>
          ) : (
            <div className="empty-state">
              No S-1, F-1, or S-11 registration statement is currently available in the indexed SEC history for this issuer.
            </div>
          )}
        </section>
      )}

      {tab === "Ownership" && (
        <section className="research-panel">
          <div className="headline-metrics ownership-metrics">
            <article>
              <small>Shares outstanding</small>
              <strong>{numberFormat(capital.shares_outstanding)}</strong>
              <span>{capital.shares_as_of || "Latest available date"}</span>
            </article>
            <article>
              <small>Total debt</small>
              <strong>{money(capital.total_debt)}</strong>
              <span>SEC-derived balance-sheet context</span>
            </article>
            <article>
              <small>Cash + investments</small>
              <strong>{money(capital.cash_and_investments)}</strong>
              <span>{capital.balance_sheet_as_of || "Latest available date"}</span>
            </article>
            <article>
              <small>SEC CIK</small>
              <strong>{sec?.cik || "N/A"}</strong>
              <span>Issuer identifier</span>
            </article>
          </div>

          <article className="research-card featured-card">
            <div className="section-label">IPO OWNERSHIP CONTEXT</div>
            <h2>Capitalization, dilution, management & ownership</h2>
            <DetailList items={filingDetails.ipo_capitalization_dilution} />
            <div className="mini-separator" />
            <DetailList items={filingDetails.proceeds_management_ownership} />
          </article>
        </section>
      )}

      <footer className="research-footer">
        EquityLens presents educational research and primary-source filing context. It is not investment advice.
      </footer>
    </main>
  );
}
