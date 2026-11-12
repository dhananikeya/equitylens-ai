import Link from "next/link";
import { notFound } from "next/navigation";
import { getCompanyResearch } from "@/lib/research-data";

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
  const latest = quarterly?.latest_quarter || {};
  const priorYear = quarterly?.prior_year_quarter || {};
  const ltm = quarterly?.ltm || {};
  const revenueGrowth = pctChange(latest.revenue, priorYear.revenue);
  const cap = metrics?.capital_structure || {};
  const risks: string[] = Array.isArray(analysis?.key_risk_themes)
    ? analysis.key_risk_themes
    : [];

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
        <section className="research-panel wide">
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

        <section className="research-panel">
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

        <section className="research-panel">
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

        <section className="research-panel wide">
          <div className="panel-heading">
            <div><p className="eyebrow">SEC EVIDENCE</p><h2>Latest filing record</h2></div>
            {sourceLink(sec?.latest_filing?.url, "Open latest SEC filing")}
          </div>
          <div className="filing-row">
            <div><span>Form</span><strong>{sec?.latest_filing?.form || "Not available"}</strong></div>
            <div><span>Filed</span><strong>{sec?.latest_filing?.filing_date || "Not available"}</strong></div>
            <div><span>Report period</span><strong>{sec?.latest_filing?.report_date || "Not specified"}</strong></div>
            <div><span>SEC status</span><strong>{sec?.sec_status || "Unknown"}</strong></div>
          </div>
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
