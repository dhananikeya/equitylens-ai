import Link from "next/link";
import { notFound } from "next/navigation";
import { getCompanyResearch } from "@/lib/research-data";
import { getMarketSnapshot } from "@/lib/market-data-next";
import { getSecResearchFilings } from "@/lib/sec-live";

function money(value: unknown) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "Not available";
  const abs = Math.abs(number);
  if (abs >= 1_000_000_000) return `${number < 0 ? "-" : ""}$${(abs / 1_000_000_000).toFixed(2)}B`;
  if (abs >= 1_000_000) return `${number < 0 ? "-" : ""}$${(abs / 1_000_000).toFixed(1)}M`;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0
  }).format(number);
}

function price(value: unknown) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "Not available";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(number);
}

function pctChange(current: unknown, previous: unknown) {
  const a = Number(current);
  const b = Number(previous);
  if (!Number.isFinite(a) || !Number.isFinite(b) || b === 0) return null;
  return ((a - b) / Math.abs(b)) * 100;
}

function sourceLink(url: unknown, label = "Open original source") {
  if (!url || typeof url !== "string") return null;
  return <a className="source-link" href={url} target="_blank" rel="noreferrer">{label} ↗</a>;
}

export default async function CompanyResearchPage({
  params
}: {
  params: Promise<{ ticker: string }>
}) {
  const { ticker: tickerParam } = await params;
  const research = getCompanyResearch(tickerParam);
  if (!research) notFound();

  const { company, metrics, analysis, quarterly, s1, sec, secGeneratedAt } = research;
  const ticker = String(company.Ticker).toUpperCase();
  const [market, researchFilings] = await Promise.all([
    getMarketSnapshot(ticker),
    getSecResearchFilings(sec?.cik)
  ]);
  const latest = quarterly?.latest_quarter || {};
  const priorYear = quarterly?.prior_year_quarter || {};
  const ltm = quarterly?.ltm || {};
  const revenueGrowth = pctChange(latest.revenue, priorYear.revenue);
  const cap = metrics?.capital_structure || {};
  const risks: string[] = Array.isArray(analysis?.key_risk_themes)
    ? analysis.key_risk_themes
    : [];
  const annualHistory = Array.isArray(metrics?.history) ? metrics.history : [];
  const completenessChecks = [
    Boolean(metrics?.revenue),
    Boolean(quarterly?.latest_quarter),
    Boolean(analysis?.business_model),
    risks.length > 0,
    Boolean(sec?.has_filings),
    Boolean(cap?.shares_outstanding || cap?.total_debt || cap?.cash_and_investments)
  ];
  const completeness = Math.round(
    (completenessChecks.filter(Boolean).length / completenessChecks.length) * 100
  );
  const revenueMax = Math.max(
    1,
    ...annualHistory.map((item: any) => Math.abs(Number(item?.revenue) || 0))
  );
  const operatingMax = Math.max(
    1,
    ...annualHistory.map((item: any) => Math.abs(Number(item?.operating_income) || 0))
  );
  const companyExtra = company as Record<string, unknown>;
  const screenerMarketCap = Number(companyExtra["Market Cap"]);
  const screenerPE = String(companyExtra["P/E"] || "").trim();
  const marketHistory = market?.history || [];
  const chartWidth = 760;
  const chartHeight = 190;
  const marketMin = marketHistory.length
    ? Math.min(...marketHistory.map((point) => point.close))
    : 0;
  const marketMax = marketHistory.length
    ? Math.max(...marketHistory.map((point) => point.close))
    : 0;
  const marketRange = Math.max(1, marketMax - marketMin);
  const chartPoints = marketHistory
    .map((point, index) => {
      const x = marketHistory.length > 1
        ? (index / (marketHistory.length - 1)) * chartWidth
        : chartWidth / 2;
      const y = chartHeight - ((point.close - marketMin) / marketRange) * chartHeight;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  return (
    <main className="shell research-page">
      <div className="research-breadcrumb">
        <Link href="/company">Company Research</Link>
        <span>/</span>
        <strong>{ticker}</strong>
      </div>

      <section className="company-hero">
        <div>
          <p className="eyebrow">COMPANY RESEARCH</p>
          <h1 className="company-title">{company.Company}</h1>
          <p className="company-meta">
            {ticker} · {company.Sector || "Sector unavailable"} · {company.Industry || "Industry unavailable"} · {company.Country || "Country unavailable"}
          </p>
        </div>
        <div className="source-status">
          <span className={sec?.has_filings ? "status-dot available" : "status-dot"} />
          <div>
            <strong>{sec?.has_filings ? "SEC source available" : "SEC source pending"}</strong>
            <small>{secGeneratedAt ? `Feed generated ${new Date(secGeneratedAt).toLocaleString("en-US", { timeZone: "America/New_York" })} ET` : "Source timestamp unavailable"}</small>
          </div>
        </div>
      </section>

      <section className="market-snapshot">
        <div className="market-snapshot-main">
          <span>Market snapshot</span>
          <div className="market-price-line">
            <strong>{market?.price !== null && market?.price !== undefined ? price(market.price) : "Unavailable"}</strong>
            {market?.changePercent !== null && market?.changePercent !== undefined && (
              <b className={market.changePercent >= 0 ? "market-up" : "market-down"}>
                {market.changePercent >= 0 ? "+" : ""}{market.changePercent.toFixed(2)}%
              </b>
            )}
          </div>
          <small>
            {market?.exchange || "Exchange unavailable"}
            {market?.sessionDate ? ` · Session ${market.sessionDate}` : ""}
            {" · "}Supplemental market data, may be delayed
          </small>
        </div>
        <div className="market-snapshot-meta">
          <div><span>Previous close</span><strong>{market?.previousClose !== null && market?.previousClose !== undefined ? price(market.previousClose) : "N/A"}</strong></div>
          <div><span>Universe market cap</span><strong>{company["Market Cap"] ? `${(Number(company["Market Cap"]) / 1000).toFixed(1)}B` : "N/A"}</strong></div>
          <div><span>P/E</span><strong>{company["P/E"] || "N/A"}</strong></div>
        </div>
      </section>

      {marketHistory.length > 1 && (
        <section className="market-chart-panel" aria-label="Six month closing price history">
          <div className="market-chart-head">
            <div>
              <span>PRICE HISTORY</span>
              <strong>6 month closing price</strong>
            </div>
            <small>{price(marketMin)} – {price(marketMax)}</small>
          </div>
          <div className="market-chart-wrap">
            <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} role="img" aria-label={`${ticker} six month closing price chart`}>
              <polyline points={chartPoints} fill="none" stroke="currentColor" strokeWidth="3" vectorEffect="non-scaling-stroke" />
            </svg>
          </div>
          <p>Source: Yahoo Finance chart feed. Supplemental market context only. Verify time-sensitive prices with your brokerage or exchange source.</p>
        </section>
      )}

      <nav className="research-jumps" aria-label="Company research sections">
        <a href="#overview">Overview</a>
        <a href="#business">Business</a>
        <a href="#financials">Financials</a>
        <a href="#risks">Risks</a>
        <a href="#filings">SEC evidence</a>
      </nav>

      <section className="coverage-strip" id="overview">
        <div>
          <span>Research completeness</span>
          <strong>{completeness}%</strong>
        </div>
        <div className="coverage-meter" aria-label={`${completeness}% research completeness`}>
          <span style={{ width: `${completeness}%` }} />
        </div>
        <p>
          Completeness reflects currently available structured financials, business context,
          risks, SEC evidence, and capital-structure coverage. Missing data is shown explicitly.
        </p>
      </section>

      <section className="metric-grid">
        <article className="metric-card">
          <span>Annual revenue</span>
          <strong>{money(metrics?.revenue)}</strong>
          <small>{metrics?.fiscal_year ? `FY ${metrics.fiscal_year}` : "Period unavailable"}</small>
        </article>
        <article className="metric-card">
          <span>Latest quarter revenue</span>
          <strong>{money(latest?.revenue)}</strong>
          <small>{quarterly?.quarter_label || quarterly?.period_end || "Period unavailable"}</small>
        </article>
        <article className="metric-card">
          <span>Quarterly revenue growth</span>
          <strong>{revenueGrowth === null ? "Not available" : `${revenueGrowth.toFixed(1)}%`}</strong>
          <small>Year over year</small>
        </article>
        <article className="metric-card">
          <span>LTM revenue</span>
          <strong>{money(ltm?.revenue)}</strong>
          <small>Calculated from reported periods</small>
        </article>
      </section>

      <div className="research-grid">
        <section className="research-panel wide" id="business">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">BUSINESS</p>
              <h2>How the company works</h2>
            </div>
            {sourceLink(analysis?.source_filing || metrics?.filing_url)}
          </div>
          <div className="narrative-grid">
            <article><h3>Business model</h3><p>{analysis?.business_model || "Structured business-model research is not available yet."}</p></article>
            <article><h3>Primary revenue source</h3><p>{analysis?.primary_revenue_source || "Revenue-model research is not available yet."}</p></article>
            <article><h3>Customers</h3><p>{analysis?.customer_type || "Customer research is not available yet."}</p></article>
            <article><h3>Platform dependencies</h3><p>{analysis?.platform_dependency || "Dependency research is not available yet."}</p></article>
          </div>
        </section>

        <section className="research-panel" id="financials">
          <div className="panel-heading">
            <div><p className="eyebrow">FINANCIALS</p><h2>Reported performance</h2></div>
            {sourceLink(quarterly?.source_filing || metrics?.filing_url)}
          </div>
          <dl className="financial-list">
            <div><dt>Gross profit</dt><dd>{money(latest?.gross_profit ?? metrics?.gross_profit)}</dd></div>
            <div><dt>Operating income</dt><dd>{money(latest?.operating_income ?? metrics?.operating_income)}</dd></div>
            <div><dt>Net income</dt><dd>{money(latest?.net_income ?? metrics?.net_income)}</dd></div>
            <div><dt>Cash & investments</dt><dd>{money(cap?.cash_and_investments ?? metrics?.cash)}</dd></div>
            <div><dt>Total debt</dt><dd>{money(cap?.total_debt)}</dd></div>
            <div><dt>Shares outstanding</dt><dd>{cap?.shares_outstanding ? Number(cap.shares_outstanding).toLocaleString("en-US") : "Not available"}</dd></div>
          </dl>
        </section>

        <section className="research-panel" id="risks">
          <div className="panel-heading">
            <div><p className="eyebrow">RISK</p><h2>Key filing themes</h2></div>
            {sourceLink(analysis?.source_filing)}
          </div>
          {risks.length ? (
            <ul className="risk-list">{risks.map((risk) => <li key={risk}>{risk}</li>)}</ul>
          ) : (
            <p className="empty-state">Structured risk research is not available for this company yet.</p>
          )}
          {analysis?.competitive_risk && <div className="research-note"><strong>Competition</strong><p>{analysis.competitive_risk}</p></div>}
          {analysis?.operational_risk && <div className="research-note"><strong>Operations</strong><p>{analysis.operational_risk}</p></div>}
        </section>

        {annualHistory.length > 1 && (
          <section className="research-panel wide">
            <div className="panel-heading">
              <div><p className="eyebrow">TREND</p><h2>Annual operating history</h2></div>
              {sourceLink(metrics?.filing_url)}
            </div>
            <div className="trend-grid">
              <div>
                <h3>Revenue</h3>
                <div className="trend-bars">
                  {annualHistory.map((item: any) => (
                    <div className="trend-row" key={`revenue-${item.fiscal_year}`}>
                      <span>FY {item.fiscal_year}</span>
                      <div><i style={{ width: `${Math.max(3, Math.abs(Number(item.revenue) || 0) / revenueMax * 100)}%` }} /></div>
                      <strong>{money(item.revenue)}</strong>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h3>Operating income</h3>
                <div className="trend-bars">
                  {annualHistory.map((item: any) => (
                    <div className="trend-row" key={`operating-${item.fiscal_year}`}>
                      <span>FY {item.fiscal_year}</span>
                      <div><i className={Number(item.operating_income) < 0 ? "negative" : ""} style={{ width: `${Math.max(3, Math.abs(Number(item.operating_income) || 0) / operatingMax * 100)}%` }} /></div>
                      <strong>{money(item.operating_income)}</strong>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>
        )}

        <section className="research-panel wide" id="filings">
          <div className="panel-heading">
            <div><p className="eyebrow">SEC EVIDENCE</p><h2>Research filing history</h2></div>
            {sourceLink(sec?.latest_filing?.url, "Open latest SEC filing")}
          </div>
          {researchFilings.length ? (
            <div className="filing-table" role="table" aria-label={`${ticker} research filings`}>
              <div className="filing-table-head" role="row">
                <span>Form</span><span>Filed</span><span>Report period</span><span>Description</span><span>Source</span>
              </div>
              {researchFilings.map((filing) => (
                <div className="filing-table-row" role="row" key={filing.accessionNumber || `${filing.form}-${filing.filingDate}`}>
                  <strong>{filing.form}</strong>
                  <span>{filing.filingDate || "N/A"}</span>
                  <span>{filing.reportDate || "N/A"}</span>
                  <span>{filing.description || filing.items || "SEC filing"}</span>
                  <a href={filing.url} target="_blank" rel="noreferrer">Open ↗</a>
                </div>
              ))}
            </div>
          ) : (
            <>
              <div className="filing-row">
                <div><span>Form</span><strong>{sec?.latest_filing?.form || "Not available"}</strong></div>
                <div><span>Filed</span><strong>{sec?.latest_filing?.filing_date || "Not available"}</strong></div>
                <div><span>Report period</span><strong>{sec?.latest_filing?.report_date || "Not specified"}</strong></div>
                <div><span>SEC status</span><strong>{sec?.sec_status || "Unknown"}</strong></div>
              </div>
              <p className="empty-state">Live research-focused SEC filing history is temporarily unavailable. The latest indexed filing is shown above.</p>
            </>
          )}
        </section>

        {s1?.source_url && (
          <section className="research-panel wide">
            <div className="panel-heading">
              <div><p className="eyebrow">IPO HISTORY</p><h2>{s1.form || "Registration filing"} context</h2></div>
              {sourceLink(s1.source_url, `Open original ${s1.form || "filing"}`)}
            </div>
            <p className="large-copy">{s1.historical_context || s1.what_to_learn}</p>
            {s1.what_to_learn && <div className="research-note"><strong>Why it matters</strong><p>{s1.what_to_learn}</p></div>}
          </section>
        )}
      </div>

      <section className="methodology-note">
        <strong>Evidence first.</strong>
        <p>Reported financial figures come from structured source data. Calculated metrics are labeled separately. Research summaries are context, not investment recommendations. Verify material information against the linked SEC filing.</p>
      </section>
    </main>
  );
}
